[CmdletBinding()]
param(
    [string]$name = "ai-sbx-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    [switch]$Force,
    [string]$CommitMessage = "AI sandbox patch"
)

$ErrorActionPreference = 'Stop'
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

# Safety check for uncommitted changes in the parent repo
if (git status --porcelain) {
    Write-Host "Parent repo has uncommitted changes; commit or stash first." -ForegroundColor Red
    exit 1
}

# Default branch detection (don't assume 'main')
$defaultBranch = git symbolic-ref refs/remotes/origin/HEAD 2>$null | Split-Path -Leaf
if (-not $defaultBranch) { $defaultBranch = "main" }

$sand = Join-Path $root ".sandboxes\$name"

# Idempotency & cleanup - check if worktree already exists
$worktreeExists = git worktree list --porcelain 2>$null | Select-String "worktree\s+$([regex]::Escape($sand))"

if ($worktreeExists -and -not $Force) {
    Write-Host "Worktree already exists. Use -Force to recreate." -ForegroundColor Yellow
    exit 1
}

if ($worktreeExists) {
    Write-Host "Removing existing worktree..." -ForegroundColor Yellow
    git worktree remove --force $sand
}

New-Item -ItemType Directory -Force $sand | Out-Null

git worktree add "$sand" -b $name
Write-Host "Sandbox ready: $sand" -ForegroundColor Green
Write-Host "Open this folder in Cursor, make changes, then run the finalize command below:" -ForegroundColor Cyan

# Auto-commit message templates
Write-Host "  git commit -m `"$CommitMessage`"" -ForegroundColor White

# Full-path finalizer script generation
$finalize = @"
# Auto-generated finalizer script
# Run this when you're done with your sandbox changes

cd `"$root`"
git diff $defaultBranch...$name > restore/AI_PATCH.diff
git merge --no-ff --no-commit $name

Write-Host "Sandbox changes merged! Check restore/AI_PATCH.diff for the diff." -ForegroundColor Green
"@

$finalize | Out-File -Encoding utf8 (Join-Path $sand "finalize.ps1") -Force
Write-Host "When you're done, just run: $sand\finalize.ps1" -ForegroundColor Green
