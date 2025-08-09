<#
  Trims context to token budget by embeddings score
#>
param([int]$maxTokens = 128000)
if (-not (Test-Path 'rag/context_topk.jsonl')) { return }
$budget = $maxTokens
$sel = Get-Content 'rag/context_topk.jsonl' | ConvertFrom-Json | ? {
  # Estimate tokens based on path length and chunk number
  # Each file path + chunk info is roughly 100-200 tokens
  $tok = 150  # Conservative estimate
  if ($tok -le $budget) { $budget -= $tok; $_ }
}
$sel | ConvertTo-Json -Depth 5 | Out-File 'context/_latest/TRIMMED.json'
