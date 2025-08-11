# Normal Performance Script for Agent Exo-Suit V2.0
# Restores normal performance settings after AI work

Write-Host " Restoring normal performance mode..."

# Restore balanced power plan
Write-Host "Restoring balanced power plan..."
try {
    powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e
    Write-Host " Balanced power plan restored"
} catch {
    Write-Warning "Could not restore balanced power plan: $($_.Exception.Message)"
}

# Re-enable sleep timers
Write-Host "Re-enabling sleep timers..."
try {
    powercfg -change -standby-timeout-ac 30
    powercfg -change -hibernate-timeout-ac 180
    Write-Host " Sleep timers restored"
} catch {
    Write-Warning "Could not restore sleep timers: $($_.Exception.Message)"
}

# Restore normal disk timeout
Write-Host "Restoring disk timeout..."
try {
    powercfg -change -disk-timeout-ac 0
    powercfg -change -disk-timeout-dc 0
    Write-Host " Disk timeout restored"
} catch {
    Write-Warning "Could not restore disk timeout: $($_.Exception.Message)"
}

# Restore normal CPU settings
Write-Host "Restoring CPU settings..."
try {
    powercfg -change -processor-min-state-ac 5
    powercfg -change -processor-min-state-dc 5
    Write-Host " CPU settings restored"
} catch {
    Write-Warning "Could not restore CPU settings: $($_.Exception.Message)"
}

Write-Host ""
Write-Host " Normal performance mode restored!"
Write-Host "System is now back to balanced power settings."
