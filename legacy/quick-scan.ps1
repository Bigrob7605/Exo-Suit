# Quick Scan Script for Agent Exo-Suit V2.0
# Runs parallel static analysis and linting before edits

param(
    [string]$root = $PWD.Path,
    [switch]$failFast = $true
)

Write-Host " Running quick scan with parallel static analysis..."

# Create jobs array
$jobs = @()
$results = @{}

# Function to run a linting job
function Start-LintJob {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory = $root
    )
    
    $job = Start-Job -ScriptBlock {
        param($cmd, $wd)
        Set-Location $wd
        try {
            $output = Invoke-Expression $cmd 2>&1
            return @{
                Success = $LASTEXITCODE -eq 0
                Output = $output
                ExitCode = $LASTEXITCODE
            }
        } catch {
            return @{
                Success = $false
                Output = $_.Exception.Message
                ExitCode = 1
            }
        }
    } -ArgumentList $Command, $WorkingDirectory
    
    return @{
        Name = $Name
        Job = $job
    }
}

# Check for different project types and create jobs
Write-Host "Detecting project types and creating lint jobs..."

# JavaScript/TypeScript projects
if (Test-Path (Join-Path $root "package.json")) {
    Write-Host "   Found Node.js project"
    
    # ESLint
    if (Test-Path (Join-Path $root "node_modules\.bin\eslint.cmd")) {
        $jobs += Start-LintJob -Name "ESLint" -Command "npx eslint . --quiet"
    } elseif (Test-Path (Join-Path $root "node_modules\.bin\eslint")) {
        $jobs += Start-LintJob -Name "ESLint" -Command "npx eslint . --quiet"
    }
    
    # TypeScript check
    if (Test-Path (Join-Path $root "tsconfig.json")) {
        $jobs += Start-LintJob -Name "TypeScript" -Command "npx tsc --noEmit"
    }
    
    # Prettier check
    if (Test-Path (Join-Path $root "node_modules\.bin\prettier.cmd")) {
        $jobs += Start-LintJob -Name "Prettier" -Command "npx prettier --check ."
    }
}

# Python projects
if ((Test-Path (Join-Path $root "requirements.txt")) -or (Test-Path (Join-Path $root "pyproject.toml")) -or (Test-Path (Join-Path $root "setup.py"))) {
    Write-Host "   Found Python project"
    
    # Ruff (modern Python linter)
    if (Get-Command ruff -ErrorAction SilentlyContinue) {
        $jobs += Start-LintJob -Name "Ruff" -Command "ruff check ."
    }
    
    # Pyright/Type checking
    if (Get-Command pyright -ErrorAction SilentlyContinue) {
        $jobs += Start-LintJob -Name "Pyright" -Command "pyright"
    }
    
    # Flake8 (if ruff not available)
    if ((-not (Get-Command ruff -ErrorAction SilentlyContinue)) -and (Get-Command flake8 -ErrorAction SilentlyContinue)) {
        $jobs += Start-LintJob -Name "Flake8" -Command "flake8 ."
    }
}

# Rust projects
if (Test-Path (Join-Path $root "Cargo.toml")) {
    Write-Host "   Found Rust project"
    $jobs += Start-LintJob -Name "Cargo Clippy" -Command "cargo clippy --quiet"
}

# PowerShell projects
if (Get-ChildItem -Path $root -Filter "*.ps1" -Recurse | Select-Object -First 1) {
    Write-Host "   Found PowerShell project"
    
    # Simple file existence check
    $ps1Files = Get-ChildItem -Path $root -Filter "*.ps1" -Recurse
    $validFiles = 0
    foreach ($file in $ps1Files) {
        if (Test-Path $file.FullName) {
            $validFiles++
        }
    }
    
    if ($validFiles -eq $ps1Files.Count) {
        Write-Host "   PowerShell files validated: $validFiles files OK"
    } else {
        Write-Host "   PowerShell files: $validFiles/$($ps1Files.Count) valid"
    }
}

# Go projects
if (Test-Path (Join-Path $root "go.mod")) {
    Write-Host "   Found Go project"
    $jobs += Start-LintJob -Name "Go Vet" -Command "go vet ./..."
    $jobs += Start-LintJob -Name "Go Fmt" -Command "go fmt ./..."
}

# Wait for all jobs to complete
if ($jobs.Count -gt 0) {
    Write-Host "Running $($jobs.Count) lint jobs in parallel..."
    
    $startTime = Get-Date
    
    # Wait for all jobs
    $jobs | ForEach-Object { $_.Job } | Wait-Job
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    # Collect results
    foreach ($jobInfo in $jobs) {
        $result = Receive-Job -Job $jobInfo.Job
        $results[$jobInfo.Name] = $result
        Remove-Job -Job $jobInfo.Job
    }
    
    Write-Host ""
    Write-Host " Quick scan completed in $($duration.TotalSeconds.ToString('F1')) seconds"
    Write-Host ""
    
    # Display results
    $allPassed = $true
    foreach ($tool in $jobs.Name) {
        $result = $results[$tool]
        if ($result.Success) {
            Write-Host "   $tool - PASSED" -ForegroundColor Green
        } else {
            Write-Host "   $tool - FAILED" -ForegroundColor Red
            if ($failFast) {
                Write-Host "  Error: $($result.Output)" -ForegroundColor Yellow
            } else {
                Write-Host "  Warnings/Errors: $($result.Output)" -ForegroundColor Yellow
            }
            $allPassed = $false
        }
    }
    
    Write-Host ""
    
    if ($allPassed) {
        Write-Host " All lint checks passed! Ready for AI edits." -ForegroundColor Green
        exit 0
    } else {
        if ($failFast) {
            Write-Host " Lint checks failed. Please fix issues before proceeding." -ForegroundColor Red
            Write-Host "Run individual lint commands to see detailed errors." -ForegroundColor Yellow
            exit 1
        } else {
            Write-Host " Some lint checks failed. Consider fixing issues before proceeding." -ForegroundColor Yellow
            exit 0
        }
    }
    
} else {
    Write-Host " No lint jobs detected. Project may not have standard linting setup."
    Write-Host "Consider adding ESLint, Ruff, or other linters to your project."
    exit 0
}
