param([string]$name = "ai-sbx-$([DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss'))")

$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

# Check if we're in a git repo, if not initialize one
if (-not (Test-Path ".git")) {
  Write-Host "Initializing git repository..." -ForegroundColor Yellow
  git init
  git add -A
  git commit -m "Initial commit" --allow-empty
}

git rev-parse --is-inside-work-tree 2>$null | Out-Null
$root = (git rev-parse --show-toplevel).Trim()
$sand = Join-Path $root ".sandboxes\$name"
New-Item -ItemType Directory -Force $sand | Out-Null

git worktree add "$sand" -b $name
Write-Host "Sandbox ready: $sand" -ForegroundColor Green
Write-Host "Open this folder in Cursor, make changes, then run the finalize command below:" -ForegroundColor Cyan
Write-Host "  cd `"$sand`"" -ForegroundColor White
Write-Host "  git add -A" -ForegroundColor White
Write-Host "  git commit -m `"AI sandbox patch`"" -ForegroundColor White
Write-Host "  cd `"$root`"" -ForegroundColor White
Write-Host "  git diff main...$name > restore\AI_PATCH.diff" -ForegroundColor White
Write-Host "  git merge --no-ff --no-commit $name" -ForegroundColor White
