# RUN_CHAOS_ENGINE.ps1 - V5 Chaos Engineering Launcher
# Purpose: Launch chaos engineering to prove V5 is bulletproof
# Author: Kai (Agent Exo-Suit V5.0)
# Status: PHASE 1A - Foundation Hardening

Write-Host "🚀 CHAOSE_ENGINE LAUNCHER - Making V5 Unfuckwithable!" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "🔍 Checking required packages..." -ForegroundColor Yellow

$requiredPackages = @("psutil", "tracemalloc")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "✅ $package - Available" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package - Missing" -ForegroundColor Red
        $missingPackages += $package
    }
}

# Install missing packages
if ($missingPackages.Count -gt 0) {
    Write-Host "📦 Installing missing packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        Write-Host "Installing $package..." -ForegroundColor Cyan
        pip install $package
    }
}

# Create necessary directories
$directories = @("logs", "reports", "config")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Green
    }
}

# Display chaos levels
Write-Host "`n🎯 Available Chaos Levels:" -ForegroundColor Magenta
Write-Host "  LOW     - Gentle testing (1% failure rate)" -ForegroundColor White
Write-Host "  MEDIUM  - Standard testing (5% failure rate)" -ForegroundColor Yellow
Write-Host "  HIGH    - Aggressive testing (10% failure rate)" -ForegroundColor Red
Write-Host "  EXTREME - Brutal testing (20% failure rate)" -ForegroundColor DarkRed

# Get user input for chaos level
Write-Host "`n🔥 Select Chaos Level:" -ForegroundColor Cyan
Write-Host "1. LOW (Recommended for first run)" -ForegroundColor White
Write-Host "2. MEDIUM (Standard testing)" -ForegroundColor Yellow
Write-Host "3. HIGH (Aggressive testing)" -ForegroundColor Red
Write-Host "4. EXTREME (Brutal testing)" -ForegroundColor DarkRed

do {
    $choice = Read-Host "`nEnter choice (1-4)"
} while ($choice -notin @("1", "2", "3", "4"))

$chaosLevels = @("low", "medium", "high", "extreme")
$selectedLevel = $chaosLevels[[int]$choice - 1]

Write-Host "`n🎯 Selected Chaos Level: $($selectedLevel.ToUpper())" -ForegroundColor Magenta

# Display what will happen
Write-Host "`n⚠️  WARNING: This will test V5 under extreme conditions!" -ForegroundColor Red
Write-Host "The chaos engine will:" -ForegroundColor Yellow
Write-Host "  • Randomly corrupt files" -ForegroundColor White
Write-Host "  • Inject memory leaks" -ForegroundColor White
Write-Host "  • Starve GPU resources" -ForegroundColor White
Write-Host "  • Simulate process crashes" -ForegroundColor White
Write-Host "  • Monitor system health" -ForegroundColor White
Write-Host "  • Generate comprehensive reports" -ForegroundColor White

Write-Host "`n💪 V5's Phoenix Recovery system will be tested to the limit!" -ForegroundColor Green

# Confirm before starting
$confirm = Read-Host "`n🚀 Ready to make V5 bulletproof? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "🛑 Chaos engineering cancelled." -ForegroundColor Yellow
    exit 0
}

# Launch chaos engine
Write-Host "`n🚀 LAUNCHING CHAOSE_ENGINE..." -ForegroundColor Green
Write-Host "V5 will now be tested under extreme conditions!" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop when ready." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Yellow

try {
    # Run chaos engine with selected level
    python "ops/CHAOSE_ENGINE.py" --level $selectedLevel
    
} catch {
    Write-Host "`n❌ Chaos engine failed to start: $_" -ForegroundColor Red
    Write-Host "Check the logs for more details." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Chaos engineering complete!" -ForegroundColor Green
Write-Host "Check the generated report for V5's robustness score." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow
