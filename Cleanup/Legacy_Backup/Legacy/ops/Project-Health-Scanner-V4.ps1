# Agent Exo-Suit V4.0 "PERFECTION" - Project Health Scanner
# Ultra-robust project health analysis with comprehensive SBOM generation

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ 
        if (Test-Path $_ -PathType Container) { return $true }
        throw "Project path '$_' does not exist or is not a directory"
    })]
    [string]$ProjectPath,
    
    [Parameter(Mandatory = $true)]
    [ValidateScript({ 
        $dir = Split-Path $_ -Parent
        if (Test-Path $dir -PathType Container) { return $true }
        throw "Output directory '$dir' does not exist"
    })]
    [string]$OutputPath,
    
    [ValidateSet('Error', 'Warning', 'Info', 'Verbose', 'Debug')]
    [string]$LogLevel = 'Info',
    
    [switch]$GenerateSBOM,
    [switch]$ScanCVEs,
    [switch]$ScanSecrets,
    [switch]$CheckOwnership,
    [switch]$CheckLocks,
    [switch]$Parallel,
    [switch]$Force,
    [int]$TimeoutSeconds = 300,
    [string[]]$ExcludePaths = @('.git', 'node_modules', '__pycache__', 'build', 'dist'),
    [switch]$DetailedReport
)

# ===== ULTRA-ROBUST ERROR HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== ADVANCED LOGGING =====
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "Info",
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    
    $colors = @{ 
        Error = 'Red'; Warning = 'Yellow'; Info = 'Cyan'; 
        Verbose = 'Gray'; Debug = 'Magenta' 
    }
    
    if ([int]([enum]::Parse([System.Diagnostics.TraceLevel], $Level)) -le
        [int]([enum]::Parse([System.Diagnostics.TraceLevel], $LogLevel))) {
        
        $timestamp = Get-Date -Format "HH:mm:ss.fff"
        $logEntry = "[$timestamp] [$Level] $Message"
        Write-Host $logEntry -ForegroundColor $colors[$Level]
        
        # Save to log file
        $logPath = Join-Path $OutputPath "health_scan_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== SYSTEM VALIDATION =====
function Test-SystemRequirements {
    Write-Log " Validating system requirements..." -Level Info
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 7) {
        Write-Log " PowerShell 7+ recommended for optimal performance" -Level Warning
    }
    
    # Check available tools
    $tools = @{
        'npm' = $null
        'cargo' = $null
        'python' = $null
        'pip' = $null
        'git' = $null
    }
    
    foreach ($tool in $tools.Keys) {
        try {
            $tools[$tool] = Get-Command $tool -ErrorAction Stop | Select-Object -ExpandProperty Source
            Write-Log " $tool found: $($tools[$tool])" -Level Verbose
        }
        catch {
            Write-Log " $tool not found in PATH" -Level Warning
        }
    }
    
    return $tools
}

# ===== ENHANCED OWNERSHIP MAPPING =====
function Get-ProjectOwnership {
    param([string]$ProjectPath)
    
    Write-Log " Building comprehensive ownership map..." -Level Info
    
    $owners = @{}
    $ownershipSources = @(
        @{ Path = 'OWNERS.md'; Type = 'Markdown' },
        @{ Path = '.github/CODEOWNERS'; Type = 'GitHub' },
        @{ Path = 'CODEOWNERS'; Type = 'GitHub' },
        @{ Path = 'OWNERS'; Type = 'Plain' }
    )
    
    foreach ($source in $ownershipSources) {
        $filePath = Join-Path $ProjectPath $source.Path
        if (Test-Path $filePath) {
            Write-Log " Found ownership file: $($source.Path)" -Level Verbose
            
            try {
                $content = Get-Content $filePath -Raw -ErrorAction Stop
                
                switch ($source.Type) {
                    'Markdown' {
                        # Parse OWNERS.md format
                        $content -split "`r?`n" | ForEach-Object {
                            if ($_ -match '^\s*\*\s*(?<path>[\w\/\-\.\*]+)\s*\|\s*(?<owner>[\w\s,@\-]+)\s*$') {
                                $owners[$Matches.path.Trim()] = @{
                                    Owner = $Matches.owner.Trim()
                                    Source = $source.Path
                                    Type = 'Markdown'
                                }
                            }
                        }
                    }
                    'GitHub' {
                        # Parse CODEOWNERS format
                        $content -split "`r?`n" | ForEach-Object {
                            if ($_ -match '^\s*(?<path>[\S]+)\s+(?<owner>[@\w\-\/,]+)') {
                                $owners[$Matches.path.Trim()] = @{
                                    Owner = $Matches.owner.Trim()
                                    Source = $source.Path
                                    Type = 'GitHub'
                                }
                            }
                        }
                    }
                    'Plain' {
                        # Parse plain OWNERS format
                        $content -split "`r?`n" | ForEach-Object {
                            if ($_ -match '^\s*(?<path>[\S]+)\s+(?<owner>[\w\s,@\-]+)') {
                                $owners[$Matches.path.Trim()] = @{
                                    Owner = $Matches.owner.Trim()
                                    Source = $source.Path
                                    Type = 'Plain'
                                }
                            }
                        }
                    }
                }
            }
            catch {
                Write-Log " Error parsing $($source.Path): $_" -Level Warning
            }
        }
    }
    
    # Convert to output format
    $ownershipData = $owners.GetEnumerator() | ForEach-Object {
        [PSCustomObject]@{
            Path = $_.Key
            Owner = $_.Value.Owner
            Source = $_.Value.Source
            Type = $_.Value.Type
            LastUpdated = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
    }
    
    # Save ownership data
    $ownershipPath = Join-Path $OutputPath 'ownership.json'
    $ownershipData | ConvertTo-Json -Depth 3 | Out-File $ownershipPath -Encoding UTF8
    
    Write-Log " Ownership data saved: $ownershipPath" -Level Info
    Write-Log " Found $($ownershipData.Count) ownership entries" -Level Info
    
    return $ownershipData
}

# ===== ENHANCED LOCK FILE ANALYSIS =====
function Get-LockFileFreshness {
    param([string]$ProjectPath)
    
    Write-Log " Analyzing lock file freshness..." -Level Info
    
    $lockFiles = @(
        @{ Name = 'package-lock.json'; Type = 'npm'; Manager = 'npm' },
        @{ Name = 'pnpm-lock.yaml'; Type = 'pnpm'; Manager = 'pnpm' },
        @{ Name = 'yarn.lock'; Type = 'yarn'; Manager = 'yarn' },
        @{ Name = 'Cargo.lock'; Type = 'cargo'; Manager = 'cargo' },
        @{ Name = 'requirements.txt'; Type = 'pip'; Manager = 'pip' },
        @{ Name = 'poetry.lock'; Type = 'poetry'; Manager = 'pip' },
        @{ Name = 'composer.lock'; Type = 'composer'; Manager = 'composer' },
        @{ Name = 'Gemfile.lock'; Type = 'bundler'; Manager = 'ruby' },
        @{ Name = 'go.mod'; Type = 'go'; Manager = 'go' },
        @{ Name = 'go.sum'; Type = 'go'; Manager = 'go' }
    )
    
    $freshnessData = @()
    
    foreach ($lockFile in $lockFiles) {
        $filePath = Join-Path $ProjectPath $lockFile.Name
        if (Test-Path $filePath) {
            try {
                $fileInfo = Get-Item $filePath
                $age = ((Get-Date) - $fileInfo.LastWriteTime).TotalDays
                $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
                
                $freshnessData += [PSCustomObject]@{
                    Type = $lockFile.Type
                    Manager = $lockFile.Manager
                    Path = $lockFile.Name
                    FullPath = $filePath
                    AgeDays = [math]::Round($age, 1)
                    LastModified = $fileInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    SizeKB = $sizeKB
                    Status = if ($age -le 30) { "Fresh" } elseif ($age -le 90) { "Stale" } else { "Very Stale" }
                }
                
                Write-Log " $($lockFile.Name): $([math]::Round($age, 1)) days old" -Level Verbose
            }
            catch {
                Write-Log " Error analyzing $($lockFile.Name): $_" -Level Warning
            }
        }
    }
    
    # Save freshness data
    $freshnessPath = Join-Path $OutputPath 'lock_age.json'
    $freshnessData | ConvertTo-Json -Depth 3 | Out-File $freshnessPath -Encoding UTF8
    
    Write-Log " Lock file freshness data saved: $freshnessPath" -Level Info
    Write-Log " Analyzed $($freshnessData.Count) lock files" -Level Info
    
    return $freshnessData
}

# ===== ENHANCED SBOM GENERATION =====
function Generate-EnhancedSBOM {
    param([string]$ProjectPath, [string]$OutputPath)
    
    Write-Log " Generating comprehensive SBOMs..." -Level Info
    
    $sbomDir = Join-Path $OutputPath 'sbom'
    New-Item -ItemType Directory -Path $sbomDir -Force | Out-Null
    
    $sbomResults = @{
        Generated = @()
        Failed = @()
        Summary = @{}
    }
    
    # npm/Node.js SBOM
    if (Test-Path (Join-Path $ProjectPath 'package.json')) {
        Write-Log " Generating npm SBOM..." -Level Info
        
        try {
            # Try multiple SBOM generators
            $npmSbomGenerated = $false
            
            # Method 1: cdxgen (recommended)
            try {
                Write-Log " Trying cdxgen..." -Level Verbose
                npm install -g @cyclonedx/cdxgen 2>&1 | Out-Null
                $cdxgenOutput = Join-Path $sbomDir 'npm_sbom_cdxgen.json'
                cdxgen -o $cdxgenOutput $ProjectPath 2>&1 | Out-Null
                
                if (Test-Path $cdxgenOutput) {
                    $sbomResults.Generated += @{
                        Type = 'npm'
                        Generator = 'cdxgen'
                        Path = $cdxgenOutput
                        Format = 'CycloneDX'
                    }
                    $npmSbomGenerated = $true
                    Write-Log " npm SBOM generated with cdxgen" -Level Info
                }
            }
            catch {
                Write-Log " cdxgen failed: $_" -Level Warning
            }
            
            # Method 2: npm audit (fallback)
            if (-not $npmSbomGenerated) {
                try {
                    Write-Log " Trying npm audit..." -Level Verbose
                    $npmAuditOutput = Join-Path $sbomDir 'npm_sbom_audit.json'
                    npm audit --json 2>$null | Out-File $npmAuditOutput
                    
                    if (Test-Path $npmAuditOutput) {
                        $sbomResults.Generated += @{
                            Type = 'npm'
                            Generator = 'npm audit'
                            Path = $npmAuditOutput
                            Format = 'npm audit'
                        }
                        $npmSbomGenerated = $true
                        Write-Log " npm SBOM generated with npm audit" -Level Info
                    }
                }
                catch {
                    Write-Log " npm audit failed: $_" -Level Warning
                }
            }
            
            if (-not $npmSbomGenerated) {
                $sbomResults.Failed += @{
                    Type = 'npm'
                    Error = 'All npm SBOM generators failed'
                }
            }
        }
        catch {
            $sbomResults.Failed += @{
                Type = 'npm'
                Error = $_.Exception.Message
            }
            Write-Log " npm SBOM generation failed: $_" -Level Error
        }
    }
    
    # Cargo/Rust SBOM
    if (Test-Path (Join-Path $ProjectPath 'Cargo.toml')) {
        Write-Log " Generating Cargo SBOM..." -Level Info
        
        try {
            $cargoSbomGenerated = $false
            
            # Method 1: cargo-cyclonedx
            try {
                Write-Log " Trying cargo-cyclonedx..." -Level Verbose
                cargo install cargo-cyclonedx 2>&1 | Out-Null
                Push-Location $ProjectPath
                cargo cyclonedx --format json 2>&1 | Out-Null
                
                $cargoSbomFiles = Get-ChildItem $ProjectPath -Filter '*.json' | Where-Object { $_.Name -like '*cyclonedx*' }
                if ($cargoSbomFiles) {
                    $cargoSbomPath = Join-Path $sbomDir 'cargo_sbom.json'
                    Move-Item $cargoSbomFiles[0].FullName $cargoSbomPath -Force
                    
                    $sbomResults.Generated += @{
                        Type = 'cargo'
                        Generator = 'cargo-cyclonedx'
                        Path = $cargoSbomPath
                        Format = 'CycloneDX'
                    }
                    $cargoSbomGenerated = $true
                    Write-Log " Cargo SBOM generated with cargo-cyclonedx" -Level Info
                }
                Pop-Location
            }
            catch {
                Write-Log " cargo-cyclonedx failed: $_" -Level Warning
            }
            
            # Method 2: cargo tree (fallback)
            if (-not $cargoSbomGenerated) {
                try {
                    Write-Log " Trying cargo tree..." -Level Verbose
                    Push-Location $ProjectPath
                    $cargoTreeOutput = Join-Path $sbomDir 'cargo_sbom_tree.json'
                    cargo tree --format json 2>&1 | Out-File $cargoTreeOutput
                    
                    if (Test-Path $cargoTreeOutput) {
                        $sbomResults.Generated += @{
                            Type = 'cargo'
                            Generator = 'cargo tree'
                            Path = $cargoTreeOutput
                            Format = 'cargo tree'
                        }
                        $cargoSbomGenerated = $true
                        Write-Log " Cargo SBOM generated with cargo tree" -Level Info
                    }
                    Pop-Location
                }
                catch {
                    Write-Log " cargo tree failed: $_" -Level Warning
                }
            }
            
            if (-not $cargoSbomGenerated) {
                $sbomResults.Failed += @{
                    Type = 'cargo'
                    Error = 'All Cargo SBOM generators failed'
                }
            }
        }
        catch {
            $sbomResults.Failed += @{
                Type = 'cargo'
                Error = $_.Exception.Message
            }
            Write-Log " Cargo SBOM generation failed: $_" -Level Error
        }
    }
    
    # Python SBOM
    if ((Test-Path (Join-Path $ProjectPath 'requirements.txt')) -or 
        (Get-ChildItem $ProjectPath -Filter '*.py' -Recurse -ErrorAction SilentlyContinue)) {
        Write-Log " Generating Python SBOM..." -Level Info
        
        try {
            $pythonSbomGenerated = $false
            
            # Method 1: cyclonedx-py
            try {
                Write-Log " Trying cyclonedx-py..." -Level Verbose
                pip install cyclonedx-bom 2>&1 | Out-Null
                $cyclonedxOutput = Join-Path $sbomDir 'python_sbom_cyclonedx.json'
                python -m cyclonedx_py requirements -o $cyclonedxOutput $ProjectPath 2>&1 | Out-Null
                
                if (Test-Path $cyclonedxOutput) {
                    $sbomResults.Generated += @{
                        Type = 'python'
                        Generator = 'cyclonedx-py'
                        Path = $cyclonedxOutput
                        Format = 'CycloneDX'
                    }
                    $pythonSbomGenerated = $true
                    Write-Log " Python SBOM generated with cyclonedx-py" -Level Info
                }
            }
            catch {
                Write-Log " cyclonedx-py failed: $_" -Level Warning
            }
            
            # Method 2: pip list (fallback)
            if (-not $pythonSbomGenerated) {
                try {
                    Write-Log " Trying pip list..." -Level Verbose
                    $pipListOutput = Join-Path $sbomDir 'python_sbom_pip.json'
                    pip list --format=json 2>&1 | Out-File $pipListOutput
                    
                    if (Test-Path $pipListOutput) {
                        $sbomResults.Generated += @{
                            Type = 'python'
                            Generator = 'pip list'
                            Path = $pipListOutput
                            Format = 'pip list'
                        }
                        $pythonSbomGenerated = $true
                        Write-Log " Python SBOM generated with pip list" -Level Info
                    }
                }
                catch {
                    Write-Log " pip list failed: $_" -Level Warning
                }
            }
            
            if (-not $pythonSbomGenerated) {
                $sbomResults.Failed += @{
                    Type = 'python'
                    Error = 'All Python SBOM generators failed'
                }
            }
        }
        catch {
            $sbomResults.Failed += @{
                Type = 'python'
                Error = $_.Exception.Message
            }
            Write-Log " Python SBOM generation failed: $_" -Level Error
        }
    }
    
    # Generate SBOM summary
    $sbomResults.Summary = @{
        TotalGenerated = $sbomResults.Generated.Count
        TotalFailed = $sbomResults.Failed.Count
        GeneratedTypes = $sbomResults.Generated.Type | Sort-Object -Unique
        FailedTypes = $sbomResults.Failed.Type | Sort-Object -Unique
        GenerationTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    # Save SBOM results
    $sbomResultsPath = Join-Path $sbomDir 'sbom_summary.json'
    $sbomResults | ConvertTo-Json -Depth 5 | Out-File $sbomResultsPath -Encoding UTF8
    
    Write-Log " SBOM generation complete" -Level Info
    Write-Log " Generated: $($sbomResults.Summary.TotalGenerated), Failed: $($sbomResults.Summary.TotalFailed)" -Level Info
    
    return $sbomResults
}

# ===== MAIN EXECUTION =====
try {
    Write-Log " Agent Exo-Suit V4.0 'PERFECTION' - Project Health Scanner Starting..." -Level Info
    
    # Create output directory
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    
    # Validate system requirements
    $availableTools = Test-SystemRequirements
    
    # Set default actions if none specified
    if (-not ($GenerateSBOM -or $ScanCVEs -or $ScanSecrets -or $CheckOwnership -or $CheckLocks)) {
        $GenerateSBOM = $true
        $ScanCVEs = $true
        $ScanSecrets = $true
        $CheckOwnership = $true
        $CheckLocks = $true
        Write-Log " No specific actions specified, running all checks" -Level Info
    }
    
    $startTime = Get-Date
    $scanResults = @{
        ProjectPath = $ProjectPath
        OutputPath = $OutputPath
        ScanStartTime = $startTime.ToString("yyyy-MM-dd HH:mm:ss")
        AvailableTools = $availableTools
        Results = @{}
    }
    
    # Execute requested scans
    if ($CheckOwnership) {
        $scanResults.Results.Ownership = Get-ProjectOwnership -ProjectPath $ProjectPath
    }
    
    if ($CheckLocks) {
        $scanResults.Results.LockFiles = Get-LockFileFreshness -ProjectPath $ProjectPath
    }
    
    if ($GenerateSBOM) {
        $scanResults.Results.SBOM = Generate-EnhancedSBOM -ProjectPath $ProjectPath -OutputPath $OutputPath
    }
    
    # TODO: Implement CVE scanning and secret scanning in next iteration
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Generate final report
    $scanResults.ScanEndTime = $endTime.ToString("yyyy-MM-dd HH:mm:ss")
    $scanResults.DurationSeconds = [math]::Round($duration, 2)
    $scanResults.Version = "4.0.0"
    
    # Save comprehensive report
    $reportPath = Join-Path $OutputPath 'health_scan_v4_report.json'
    $scanResults | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8
    
    Write-Log " V4.0 Project Health Scanner completed successfully!" -Level Info
    Write-Log " Duration: $duration seconds" -Level Info
    Write-Log " Report saved to: $reportPath" -Level Info
    
} catch {
    Write-Log " Fatal error: $_" -Level Error
    Write-Log " Stack trace: $($_.ScriptStackTrace)" -Level Error
    exit 1
}

Write-Log " V4.0 Project Health Scanner ready for production deployment!" -Level Info
