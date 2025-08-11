# Quick Emoji Scanner - Agent Exo-Suit V3.0
# Fast emoji detection for immediate use

param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$Purge,
    [switch]$Report
)

Write-Host "Agent Exo-Suit V3.0 - Quick Emoji Scanner" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

if ($Quick -or $Full -or $Purge -or $Report) {
    # Use the full emoji sentinel
    & .\ops\emoji-sentinel.ps1 @PSBoundParameters
} else {
    # Quick scan by default
    Write-Host "Running quick emoji scan..." -ForegroundColor Yellow
    & .\ops\emoji-sentinel.ps1 -Scan
}

Write-Host "`nQuick Emoji Scanner complete!" -ForegroundColor Green
Write-Host "For full functionality, use: .\ops\emoji-sentinel.ps1" -ForegroundColor Yellow
