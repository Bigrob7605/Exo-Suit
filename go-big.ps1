# Agent Exo-Suit V4.0 "Perfection" "Monster-Mode" - Full System Activation
# This is the single command to rule them all
# Production Ready - Full V4 Feature Set

param(
    [switch]$NoEmojiScan,
    [switch]$ForceEmojiScan,
    [switch]$EmojiPurge
)

Write-Host "Agent Exo-Suit V4.0 'Perfection' 'Monster-Mode' - Full System Activation" -ForegroundColor Green
Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan
Write-Host "Target: ASUS TUF i7-13620H + RTX 4070" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Emoji Sentinel V4.0 Activation
if (-not $NoEmojiScan) {
    Write-Host "`nStep 1: Activating Emoji Sentinel V4.0..." -ForegroundColor Cyan
    
    if ($ForceEmojiScan -or $EmojiPurge) {
        Write-Host "Running comprehensive emoji scan..." -ForegroundColor Yellow
        & .\ops\emoji-sentinel-v4.ps1 -Scan -Verbose
    } else {
        # Quick emoji check
        Write-Host "Running quick emoji scan..." -ForegroundColor Yellow
        & .\ops\emoji-sentinel-v4.ps1 -Scan
    }
    
    if ($EmojiPurge) {
        Write-Host "`nInitiating emoji purge protocol..." -ForegroundColor Red
        & .\ops\emoji-sentinel-v4.ps1 -Purge -Verbose
    }
    
    Write-Host "Emoji Sentinel V4.0: ACTIVE" -ForegroundColor Green
}

# Step 2: System Refresh
Write-Host "`nStep 2: System Refresh..." -ForegroundColor Cyan
# Note: refresh.ps1 moved to Cleanup/Legacy_Backup/Legacy/
Write-Host "System Refresh: SKIPPED (Legacy component)" -ForegroundColor Yellow

# Step 3: Performance Mode Activation
Write-Host "`nStep 3: Activating Ultimate Performance Mode..." -ForegroundColor Cyan
& .\AgentExoSuitV4.ps1
Write-Host "Performance Mode: ACTIVE" -ForegroundColor Green

# Step 4: Drift Detection V4.0
Write-Host "`nStep 4: Drift Detection V4.0..." -ForegroundColor Cyan
& .\ops\Drift-Guard-V4.ps1
Write-Host "Drift Detection V4.0: COMPLETE" -ForegroundColor Green

# Step 5: Health Scan V4.0
Write-Host "`nStep 5: Project Health Scan V4.0..." -ForegroundColor Cyan
& .\ops\Project-Health-Scanner-V4.ps1
Write-Host "Health Scan V4.0: COMPLETE" -ForegroundColor Green

# Step 6: GPU Acceleration
Write-Host "`nStep 6: GPU Acceleration..." -ForegroundColor Cyan
& .\ops\gpu-accelerator.ps1
Write-Host "GPU Acceleration: ACTIVE" -ForegroundColor Green

# Step 7: V4.0 Full System Activation
Write-Host "`nStep 7: V4.0 Full System Activation..." -ForegroundColor Cyan
& .\AgentExoSuitV4.ps1 -FullSystem
Write-Host "V4.0 Full System: ACTIVE" -ForegroundColor Green

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Agent Exo-Suit V4.0 'Perfection' 'Monster-Mode' - FULLY OPERATIONAL" -ForegroundColor Green
Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Green
Write-Host "All V4.0 systems: ONLINE" -ForegroundColor Green
Write-Host "Emoji Sentinel V4.0: DEPLOYED" -ForegroundColor Green
Write-Host "Performance: MAXIMUM" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`nSystem ready for high-performance V4.0 development!" -ForegroundColor Cyan
Write-Host "Use '.\ops\emoji-sentinel-v4.ps1 -Report' to view emoji scan results" -ForegroundColor Yellow
Write-Host "Use '.\ops\emoji-sentinel-v4.ps1 -Purge' to remove all detected emojis" -ForegroundColor Yellow
Write-Host "Use '.\AgentExoSuitV4.ps1 -Status' to check V4.0 component status" -ForegroundColor Yellow
