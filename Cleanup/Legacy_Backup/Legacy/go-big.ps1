# Agent Exo-Suit V3.0 "Monster-Mode" - Full System Activation
# This is the single command to rule them all

param(
    [switch]$NoEmojiScan,
    [switch]$ForceEmojiScan,
    [switch]$EmojiPurge
)

Write-Host "Agent Exo-Suit V3.0 'Monster-Mode' - Full System Activation" -ForegroundColor Green
Write-Host "Target: ASUS TUF i7-13620H + RTX 4070" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Emoji Sentinel Activation (NEW!)
if (-not $NoEmojiScan) {
    Write-Host "`nStep 1: Activating Emoji Sentinel..." -ForegroundColor Cyan
    
    if ($ForceEmojiScan -or $EmojiPurge) {
        Write-Host "Running comprehensive emoji scan..." -ForegroundColor Yellow
        & .\ops\emoji-sentinel.ps1 -Scan -Verbose
    } else {
        # Quick emoji check
        Write-Host "Running quick emoji scan..." -ForegroundColor Yellow
        & .\ops\emoji-sentinel.ps1 -Scan
    }
    
    if ($EmojiPurge) {
        Write-Host "`nInitiating emoji purge protocol..." -ForegroundColor Red
        & .\ops\emoji-sentinel.ps1 -Purge -Verbose
    }
    
    Write-Host "Emoji Sentinel: ACTIVE" -ForegroundColor Green
}

# Step 2: System Refresh
Write-Host "`nStep 2: System Refresh..." -ForegroundColor Cyan
& .\refresh.ps1 -Force
Write-Host "System Refresh: COMPLETE" -ForegroundColor Green

# Step 3: Performance Mode Activation
Write-Host "`nStep 3: Activating Ultimate Performance Mode..." -ForegroundColor Cyan
& .\AgentExoSuitV3.ps1
Write-Host "Performance Mode: ACTIVE" -ForegroundColor Green

# Step 4: Drift Detection
Write-Host "`nStep 4: Drift Detection..." -ForegroundColor Cyan
& .\ops\drift-gate.ps1
Write-Host "Drift Detection: COMPLETE" -ForegroundColor Green

# Step 5: Health Scan
Write-Host "`nStep 5: Project Health Scan..." -ForegroundColor Cyan
& .\ops\Project-Health-Scanner.ps1
Write-Host "Health Scan: COMPLETE" -ForegroundColor Green

# Step 6: GPU Acceleration
Write-Host "`nStep 6: GPU Acceleration..." -ForegroundColor Cyan
& .\ops\gpu-accelerator.ps1
Write-Host "GPU Acceleration: ACTIVE" -ForegroundColor Green

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Agent Exo-Suit V3.0 'Monster-Mode' - FULLY OPERATIONAL" -ForegroundColor Green
Write-Host "All systems: ONLINE" -ForegroundColor Green
Write-Host "Emoji Sentinel: DEPLOYED" -ForegroundColor Green
Write-Host "Performance: MAXIMUM" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`nSystem ready for high-performance development!" -ForegroundColor Cyan
Write-Host "Use '.\ops\emoji-sentinel.ps1 -Report' to view emoji scan results" -ForegroundColor Yellow
Write-Host "Use '.\ops\emoji-sentinel.ps1 -Purge' to remove all detected emojis" -ForegroundColor Yellow
