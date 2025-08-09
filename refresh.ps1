# Refresh script for Agent Exo-Suit V1.1
# Ensures folders exist and checks for ripgrep dependency

New-Item -ItemType Directory -Force -Path "$PSScriptRoot\context\_latest" | Out-Null

# Check for ripgrep but don't fail if missing
$hasRipgrep = Get-Command rg -ErrorAction SilentlyContinue
if (-not $hasRipgrep) { 
    Write-Warning "ripgrep (rg) not found. Some features will be limited."
    Write-Warning "Install ripgrep for full functionality: https://github.com/BurntSushi/ripgrep#installation"
}

# Run the core functionality
Write-Host "Running Agent Exo-Suit V1.1 refresh..."

# Create context directory if it doesn't exist
$contextDir = Join-Path $PSScriptRoot "context\_latest"
New-Item -ItemType Directory -Force -Path $contextDir | Out-Null

# Run make-pack.ps1
if (Test-Path "$PSScriptRoot\ops\make-pack.ps1") {
    Write-Host "Running make-pack.ps1..."
    & "$PSScriptRoot\ops\make-pack.ps1" "$PSScriptRoot" "$contextDir"
} else {
    Write-Warning "make-pack.ps1 not found"
}

# Run index-symbols.ps1 (only if ripgrep is available)
if ($hasRipgrep -and (Test-Path "$PSScriptRoot\ops\index-symbols.ps1")) {
    Write-Host "Running index-symbols.ps1..."
    & "$PSScriptRoot\ops\index-symbols.ps1" "$PSScriptRoot"
} else {
    Write-Host "Skipping index-symbols.ps1 (ripgrep not available or script not found)"
}

# Run index-imports.ps1 (only if ripgrep is available)
if ($hasRipgrep -and (Test-Path "$PSScriptRoot\ops\index-imports.ps1")) {
    Write-Host "Running index-imports.ps1..."
    & "$PSScriptRoot\ops\index-imports.ps1" "$PSScriptRoot"
} else {
    Write-Host "Skipping index-imports.ps1 (ripgrep not available or script not found)"
}

# Run placeholder-scan.ps1
if (Test-Path "$PSScriptRoot\ops\placeholder-scan.ps1") {
    Write-Host "Running placeholder-scan.ps1..."
    & "$PSScriptRoot\ops\placeholder-scan.ps1" "$PSScriptRoot"
} else {
    Write-Warning "placeholder-scan.ps1 not found"
}

# Run drift-gate.ps1
if (Test-Path "$PSScriptRoot\ops\drift-gate.ps1") {
    Write-Host "Running drift-gate.ps1..."
    & "$PSScriptRoot\ops\drift-gate.ps1" -json
} else {
    Write-Warning "drift-gate.ps1 not found"
}

Write-Host "Refresh complete! Check $contextDir for generated files."
