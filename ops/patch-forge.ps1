# Patch Forge Script for Agent Exo-Suit V2.0
# Manages AI branches and generates patches for review

<#
  Creates a feature branch, commits AI diff, saves patch file
#>
param([string]$featureName = "ai-$(Get-Date -UFormat %Y%m%d-%H%M%S)")

git switch -c $featureName 2>$null
git add -A
git commit -m "AI: $featureName" --allow-empty
git diff main...HEAD | Out-File "restore/AI_PATCH.diff" -Encoding utf8
