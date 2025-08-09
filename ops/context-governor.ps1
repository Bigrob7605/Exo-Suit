<#
.SYNOPSIS
  Trims context to a token budget by embedding score.

.PARAMETER MaxTokens
  Maximum number of tokens to keep.  Defaults to 128 000.
#>
[CmdletBinding()]
param(
    [int]$MaxTokens = 128000
)

# ------------------------------------------------------------------
# 0.  Early-exit if there's nothing to do
# ------------------------------------------------------------------
$sourceFile = Join-Path (Split-Path $PSScriptRoot -Parent) 'rag' 'context_topk.jsonl'
if (-not (Test-Path $sourceFile)) {
    Write-Verbose "No context file found – skipping trim."
    return
}

# ------------------------------------------------------------------
# 1.  Read & sort by score (descending)
# ------------------------------------------------------------------
$items = Get-Content $sourceFile -ErrorAction Stop |
         ConvertFrom-Json |
         Sort-Object -Property score -Descending

# ------------------------------------------------------------------
# 2.  Token estimator
#     (Tweak 5 chars ≈ 1 token for your own tokenizer if you like)
#     For current data structure: estimate based on path length + chunk info
# ------------------------------------------------------------------
function Get-TokenEstimate {
    param($obj)
    # Current format has path and chunk, estimate tokens conservatively
    $chars = $obj.path.Length + 50  # Path + chunk metadata overhead
    return [math]::Ceiling($chars / 5)
}

# ------------------------------------------------------------------
# 3.  Greedy selection until budget exhausted
# ------------------------------------------------------------------
$budget   = $MaxTokens
$selected = @()

foreach ($item in $items) {
    $tok = Get-TokenEstimate $item
    if ($tok -gt $budget) { break }
    $selected += $item
    $budget   -= $tok
}

# ------------------------------------------------------------------
# 4.  Persist the trimmed list
# ------------------------------------------------------------------
$outDir = Join-Path (Split-Path $PSScriptRoot -Parent) 'context' '_latest'
if (-not (Test-Path $outDir)) { $null = New-Item $outDir -ItemType Directory }
$outFile = Join-Path $outDir 'TRIMMED.json'

$selected | ConvertTo-Json -Depth 5 | Set-Content -Path $outFile -Encoding UTF8

Write-Verbose "Kept $($selected.Count) items, ~$($MaxTokens - $budget) tokens."
Write-Verbose "Top score: $($selected[0].score), Bottom score: $($selected[-1].score)"
