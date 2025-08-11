# Agent Exo-Suit V4.0 "PERFECTION" - Secret Scanner
# Ultra-robust secret detection with comprehensive SARIF/JUnit output

[CmdletBinding()]
param(
    [switch]$Strict,
    [Parameter(Mandatory = $false)]
    [ValidateScript({ 
        if ([string]::IsNullOrEmpty($_)) { return $true }
        if (Test-Path $_ -PathType Container) { return $true }
        throw "Root path '$_' does not exist or is not a directory"
    })]
    [string]$Root = (Get-Location),
    
    [Parameter(Mandatory = $false)]
    [ValidateScript({ 
        $dir = Split-Path $_ -Parent
        if ([string]::IsNullOrEmpty($dir) -or (Test-Path $dir -PathType Container)) { return $true }
        throw "Output directory '$dir' does not exist"
    })]
    [string]$OutDir = "$Root\restore",
    
    [ValidateSet('sarif', 'junit', 'legacy', 'all', 'auto')]
    [string]$Format = 'auto',
    

    [switch]$Parallel,
    [switch]$Benchmark,
    [int]$MaxFileSizeMB = 1,
    [int]$MaxMatches = 100,
    [double]$EntropyThreshold = 4.2,
    [int]$RegexTimeoutSeconds = 2,
    [string[]]$CustomRules,
    [string[]]$ExcludePaths,
    [string[]]$IncludeExtensions,
    [switch]$GenerateAllowlist,
    [switch]$DetailedOutput
)

# ===== ULTRA-ROBUST ERROR HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== ADVANCED LOGGING =====
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    
    $colors = @{ 
        Error = 'Red'; Warning = 'Yellow'; Info = 'Cyan'; 
        Verbose = 'Gray'; Debug = 'Magenta' 
    }
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry -ForegroundColor $colors[$Level]
    
    if ($PSCmdlet.MyInvocation.BoundParameters['Verbose']) {
        $logPath = Join-Path $OutDir "secrets_scan_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== ENHANCED SECRET DETECTION RULES =====
$script:enhancedRules = @(
    # AWS Secrets
    @{ 
        Name = 'AWS_ACCESS_KEY_ID'; 
        Pattern = '^AKIA[0-9A-Z]{16}$'; 
        Description = 'AWS Access Key ID detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.95
    },
    @{ 
        Name = 'AWS_SECRET_ACCESS_KEY'; 
        Pattern = '(?is)aws_secret_access_key.{0,10}([A-Za-z0-9/+=]{40})'; 
        Description = 'AWS Secret Access Key detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = 4.5;
        Confidence = 0.95
    },
    @{ 
        Name = 'AWS_SESSION_TOKEN'; 
        Pattern = '(?is)aws_session_token.{0,10}([A-Za-z0-9/+=]{300,})'; 
        Description = 'AWS Session Token detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = 4.3;
        Confidence = 0.9
    },
    
    # Google Cloud
    @{ 
        Name = 'GCP_SA_KEY'; 
        Pattern = '(?is)"type"\s*:\s*"service_account"'; 
        Description = 'Google Cloud Service Account key detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.85
    },
    @{ 
        Name = 'GCP_API_KEY'; 
        Pattern = 'AIza[0-9A-Za-z\-_]{35}'; 
        Description = 'Google Cloud API Key detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.9
    },
    
    # Azure
    @{ 
        Name = 'AZURE_CONNECTION_STRING'; 
        Pattern = '(?is)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+'; 
        Description = 'Azure Storage Connection String detected';
        Severity = 'BLOCK';
        Category = 'Cloud Credentials';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.9
    },
    
    # Private Keys
    @{ 
        Name = 'RSA_PRIVATE_KEY'; 
        Pattern = '-----BEGIN RSA PRIVATE KEY-----'; 
        Description = 'RSA Private Key detected';
        Severity = 'BLOCK';
        Category = 'Cryptographic Keys';
        CWE = 'CWE-321';
        Entropy = $null;
        Confidence = 0.95
    },
    @{ 
        Name = 'EC_PRIVATE_KEY'; 
        Pattern = '-----BEGIN EC PRIVATE KEY-----'; 
        Description = 'EC Private Key detected';
        Severity = 'BLOCK';
        Category = 'Cryptographic Keys';
        CWE = 'CWE-321';
        Entropy = $null;
        Confidence = 0.95
    },
    @{ 
        Name = 'OPENSSH_PRIVATE_KEY'; 
        Pattern = '-----BEGIN OPENSSH PRIVATE KEY-----'; 
        Description = 'OpenSSH Private Key detected';
        Severity = 'BLOCK';
        Category = 'Cryptographic Keys';
        CWE = 'CWE-321';
        Entropy = $null;
        Confidence = 0.95
    },
    @{ 
        Name = 'DSA_PRIVATE_KEY'; 
        Pattern = '-----BEGIN DSA PRIVATE KEY-----'; 
        Description = 'DSA Private Key detected';
        Severity = 'BLOCK';
        Category = 'Cryptographic Keys';
        CWE = 'CWE-321';
        Entropy = $null;
        Confidence = 0.95
    },
    
    # JWT Tokens
    @{ 
        Name = 'JWT_TOKEN'; 
        Pattern = '^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'; 
        Description = 'JWT Token detected';
        Severity = 'WARN';
        Category = 'Authentication';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.8
    },
    
    # Slack
    @{ 
        Name = 'SLACK_TOKEN'; 
        Pattern = '^xox[baprs]-[A-Za-z0-9-]+$'; 
        Description = 'Slack Token detected';
        Severity = 'BLOCK';
        Category = 'API Keys';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.9
    },
    
    # GitHub
    @{ 
        Name = 'GITHUB_CLASSIC_TOKEN'; 
        Pattern = '^ghp_[A-Za-z0-9]{36,}$'; 
        Description = 'GitHub Classic Token detected';
        Severity = 'BLOCK';
        Category = 'API Keys';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.9
    },
    @{ 
        Name = 'GITHUB_FINE_TOKEN'; 
        Pattern = '^github_pat_[A-Za-z0-9_]{36,}$'; 
        Description = 'GitHub Fine-grained Token detected';
        Severity = 'BLOCK';
        Category = 'API Keys';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.9
    },
    
    # Generic Environment Variables
    @{ 
        Name = 'ENV_GENERIC_SECRET'; 
        Pattern = '(?im)^[A-Z_]{3,}\s*=\s*([A-Za-z0-9/+=]{20,})$'; 
        Description = 'Generic environment variable secret detected';
        Severity = 'WARN';
        Category = 'Environment Variables';
        CWE = 'CWE-532';
        Entropy = $EntropyThreshold;
        Confidence = 0.7
    },
    
    # Database Connection Strings
    @{ 
        Name = 'DATABASE_CONNECTION_STRING'; 
        Pattern = '(?is)(mongodb|postgresql|mysql|sqlserver)://[^:]+:[^@]+@[^/]+'; 
        Description = 'Database connection string with credentials detected';
        Severity = 'BLOCK';
        Category = 'Database';
        CWE = 'CWE-532';
        Entropy = $null;
        Confidence = 0.85
    },
    
    # API Keys
    @{ 
        Name = 'GENERIC_API_KEY'; 
        Pattern = '(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)\s*[=:]\s*([A-Za-z0-9/+=]{20,})'; 
        Description = 'Generic API key detected';
        Severity = 'WARN';
        Category = 'API Keys';
        CWE = 'CWE-532';
        Entropy = 4.0;
        Confidence = 0.7
    }
)

# ===== ENHANCED ALLOWLIST =====
$script:enhancedAllowlist = @{
    'ENV_GENERIC_SECRET' = @('EXAMPLE', 'PLACEHOLDER', 'YOUR_SECRET_HERE', 'CHANGE_ME', 'TODO')
    'GENERIC_API_KEY' = @('EXAMPLE', 'PLACEHOLDER', 'YOUR_API_KEY', 'CHANGE_ME', 'TODO')
    'JWT_TOKEN' = @('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.token')
}

# ===== ENHANCED ENTROPY CALCULATION =====
function Get-ShannonEntropy {
    param([string]$Text)
    
    if ([string]::IsNullOrEmpty($Text)) { return 0 }
    
    try {
        $freq = @{}
        foreach ($c in $Text.ToCharArray()) { 
            if ($freq.ContainsKey($c)) { $freq[$c]++ } else { $freq[$c] = 1 }
        }
        
        $len = $Text.Length
        $entropy = 0
        
        foreach ($v in $freq.Values) {
            $p = $v / $len
            $entropy -= $p * [Math]::Log($p, 2)
        }
        
        return [math]::Round($entropy, 3)
    }
    catch {
        Write-Log " Error calculating entropy: $_" -Level Warning
        return 0
    }
}

# ===== ENHANCED ALLOWLIST TESTING =====
function Test-Allowlist {
    param($RuleName, $Value)
    
    if ($script:enhancedAllowlist.ContainsKey($RuleName)) {
        foreach ($pattern in $script:enhancedAllowlist[$RuleName]) {
            if ($Value -like "*$pattern*") { return $true }
        }
    }
    
    return $false
}

# ===== ENHANCED FILE SCANNING =====
function Scan-FileForSecrets {
    param(
        [System.IO.FileInfo]$File,
        [array]$Rules,
        [hashtable]$Options
    )
    
    $results = [System.Collections.Generic.List[psobject]]::new()
    
    try {
        # Check file size
        if ($File.Length -gt ($Options.MaxFileSizeMB * 1MB)) {
            return $results
        }
        
        # Read file content
        $content = [IO.File]::ReadAllText($File.FullName)
        
        foreach ($rule in $Rules) {
            try {
                $regex = [regex]::new($rule.Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase, 
                    [timespan]::FromSeconds($Options.RegexTimeoutSeconds))
                
                $matches = $regex.Matches($content)
                $matchCount = [Math]::Min($matches.Count, $Options.MaxMatches)
                
                for ($i = 0; $i -lt $matchCount; $i++) {
                    $match = $matches[$i]
                    $secret = if ($match.Groups.Count -gt 1) { $match.Groups[1].Value } else { $match.Value }
                    
                    # Skip if entropy check fails
                    if ($rule.Entropy -and (Get-ShannonEntropy $secret) -lt $rule.Entropy) { 
                        continue 
                    }
                    
                    # Skip if in allowlist
                    if (Test-Allowlist $rule.Name $secret) { 
                        continue 
                    }
                    
                    # Calculate line number
                    $beforeMatch = $content.Substring(0, $match.Index)
                    $lineNumber = ($beforeMatch -split "`r?`n").Count
                    
                    # Get context
                    $lineStart = $beforeMatch.LastIndexOf("`n")
                    if ($lineStart -eq -1) { $lineStart = 0 } else { $lineStart++ }
                    
                    $lineEnd = $content.IndexOf("`n", $match.Index)
                    if ($lineEnd -eq -1) { $lineEnd = $content.Length }
                    
                    $lineContent = $content.Substring($lineStart, $lineEnd - $lineStart).Trim()
                    $context = $lineContent.Substring([math]::Max(0, $match.Index - $lineStart - 30), 60)
                    
                    $result = [PSCustomObject]@{
                        File = $File.FullName
                        Rule = $rule.Name
                        Description = $rule.Description
                        Sample = $secret.Substring(0, [Math]::Min($secret.Length, 60))
                        Severity = $rule.Severity
                        Category = $rule.Category
                        CWE = $rule.CWE
                        Line = $lineNumber
                        Column = $match.Index - $lineStart + 1
                        LineContent = $lineContent
                        Context = $context
                        Entropy = (Get-ShannonEntropy $secret)
                        Confidence = $rule.Confidence
                        DetectionTime = Get-Date
                        FileSize = $File.Length
                        FileExtension = $File.Extension
                    }
                    
                    $results.Add($result)
                }
            }
            catch {
                Write-Log " Error processing rule $($rule.Name) in $($File.Name): $_" -Level Warning
            }
        }
    }
    catch {
        Write-Log " Error scanning file $($File.Name): $_" -Level Warning
    }
    
    return $results
}

# ===== ENHANCED SARIF OUTPUT =====
function Export-SARIFReport {
    param([array]$Findings, [string]$OutputPath)
    
    Write-Log " Generating SARIF report..." -Level Info
    
    $sarif = @{
        version = "2.1.0"
        $schema = "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json"
        runs = @(@{
            tool = @{ 
                driver = @{ 
                    name = "Agent-Exo-Suit-V4-Secret-Scanner"
                    version = "4.0.0"
                    informationUri = "https://github.com/your-org/agent-exo-suit"
                    rules = @()
                }
            }
            automationDetails = @{
                id = "secrets-scan-v4"
                runGuid = [System.Guid]::NewGuid().ToString()
            }
            results = @()
            invocations = @(@{
                executionSuccessful = $true
                startTimeUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                endTimeUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                toolExecutionNotifications = @()
            })
        })
    }
    
    # Add rules
    $uniqueRules = $Findings | Group-Object Rule
    foreach ($ruleGroup in $uniqueRules) {
        $rule = $script:enhancedRules | Where-Object { $_.Name -eq $ruleGroup.Name } | Select-Object -First 1
        
        $sarif.runs[0].tool.driver.rules += @{
            id = $ruleGroup.Name
            name = $ruleGroup.Name
            shortDescription = @{ text = $rule.Description }
            helpUri = "https://cwe.mitre.org/data/definitions/$($rule.CWE).html"
            properties = @{
                category = $rule.Category
                severity = $rule.Severity
                confidence = $rule.Confidence
                cwe = $rule.CWE
            }
        }
    }
    
    # Add results
    foreach ($finding in $Findings) {
        $sarif.runs[0].results += @{
            ruleId = $finding.Rule
            level = if ($finding.Severity -eq 'BLOCK') { 'error' } else { 'warning' }
            message = @{ 
                text = $finding.Description
                arguments = @($finding.Sample, $finding.File)
            }
            locations = @(@{
                physicalLocation = @{ 
                    artifactLocation = @{ 
                        uri = [uri]$finding.File
                        uriBaseId = "%SRCROOT%"
                    }
                    region = @{ 
                        startLine = $finding.Line
                        startColumn = $finding.Column
                        endLine = $finding.Line
                        endColumn = $finding.Column + $finding.Sample.Length
                    }
                }
            })
            properties = @{
                category = $finding.Category
                confidence = $finding.Confidence
                entropy = $finding.Entropy
                cwe = $finding.CWE
                context = $finding.Context
                sample = $finding.Sample
            }
        }
    }
    
    # Save SARIF report
    $sarifPath = Join-Path $OutputPath "secrets_v4.sarif"
    $sarif | ConvertTo-Json -Depth 10 | Out-File $sarifPath -Encoding UTF8
    
    Write-Log " SARIF report saved: $sarifPath" -Level Info
    return $sarifPath
}

# ===== ENHANCED JUNIT OUTPUT =====
function Export-JUnitReport {
    param([array]$Findings, [string]$OutputPath)
    
    Write-Log " Generating JUnit report..." -Level Info
    
    $testCases = @()
    $totalTests = 0
    $totalFailures = 0
    
    # Group findings by rule
    $ruleGroups = $Findings | Group-Object Rule
    
    foreach ($ruleGroup in $ruleGroups) {
        $rule = $script:enhancedRules | Where-Object { $_.Name -eq $ruleGroup.Name } | Select-Object -First 1
        
        $testCases += @"
    <testcase name="$($ruleGroup.Name)" classname="SecretScanner" time="0">
      <failure message="$($rule.Description)" type="SecretDetected">
        <![CDATA[
Rule: $($ruleGroup.Name)
Category: $($rule.Category)
Severity: $($rule.Severity)
CWE: $($rule.CWE)
Findings: $($ruleGroup.Count)
        ]]>
      </failure>
    </testcase>
"@
        
        $totalTests++
        $totalFailures++
    }
    
    $xml = @"
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Agent-Exo-Suit-V4-Secret-Scanner" tests="$totalTests" failures="$totalFailures" errors="0" time="0">
  <testsuite name="Secret Detection" tests="$totalTests" failures="$totalFailures" errors="0" time="0">
$($testCases -join "`n")
  </testsuite>
</testsuites>
"@
    
    # Save JUnit report
    $junitPath = Join-Path $OutputPath "secrets_v4.junit.xml"
    $xml | Out-File $junitPath -Encoding UTF8
    
    Write-Log " JUnit report saved: $junitPath" -Level Info
    return $junitPath
}

# ===== MAIN SCANNING FUNCTION =====
function Start-SecretScan {
    param([string]$RootPath)
    
    Write-Log " Starting V4.0 Ultra-robust Secret Scan..." -Level Info
    Write-Log " Root directory: $RootPath" -Level Info
    
    $startTime = Get-Date
    
    # Get files to scan
    $excludeDirs = @(
        'node_modules', 'dist', 'build', 'target', 'bin', 'obj', '__pycache__',
        '.git', 'restore', 'context', 'rag', 'telemetry', 'cache', 'gpu_rag_env',
        'mermaid', 'rag_env', 'test-emoji-pack'
    )
    
    if ($ExcludePaths) {
        $excludeDirs += $ExcludePaths
    }
    
    $excludeExtensions = @('.dll', '.exe', '.png', '.jpg', '.gif', '.ico', '.zip', '.tar', '.gz', '.mo', '.so')
    
    # Get all files first, then filter
    $allFiles = @(Get-ChildItem -LiteralPath $RootPath -Recurse -File -ErrorAction SilentlyContinue)
    
    if ($IncludeExtensions) {
        $files = @($allFiles | Where-Object { 
            $_.Extension -in $IncludeExtensions -and 
            -not ($_.FullName -split '\\' | Where-Object { $_ -in $excludeDirs })
        })
    } else {
        $files = @($allFiles | Where-Object { 
            $_.Extension -notin $excludeExtensions -and 
            -not ($_.FullName -split '\\' | Where-Object { $_ -in $excludeDirs })
        })
    }
    
    # Ensure $files is always an array
    if ($null -eq $files) { $files = @() }
    
    Write-Log " Found $($files.Count) files to scan" -Level Info
    
    # Scan files
    $allFindings = @()
    
    # Ensure $allFindings is always an array
    if ($null -eq $allFindings) { $allFindings = @() }
    
    if ($Parallel -and $files.Count -gt 10) {
        Write-Log " Using parallel processing..." -Level Info
        
        $options = @{
            MaxFileSizeMB = $MaxFileSizeMB
            MaxMatches = $MaxMatches
            RegexTimeoutSeconds = $RegexTimeoutSeconds
        }
        
        $allFindings = $files | ForEach-Object -ThrottleLimit ([Environment]::ProcessorCount) -Parallel {
            $file = $_
            $rules = $using:script:enhancedRules
            $options = $using:options
            
            # Import functions in parallel context
            function Get-ShannonEntropy([string]$Text) {
                if ([string]::IsNullOrEmpty($Text)) { return 0 }
                $freq = @{}
                foreach ($c in $Text.ToCharArray()) { 
                    if ($freq.ContainsKey($c)) { $freq[$c]++ } else { $freq[$c] = 1 }
                }
                $len = $Text.Length
                $entropy = 0
                foreach ($v in $freq.Values) {
                    $p = $v / $len
                    $entropy -= $p * [Math]::Log($p, 2)
                }
                return [math]::Round($entropy, 3)
            }
            
            function Test-Allowlist($RuleName, $Value) {
                $allowlist = @{
                    'ENV_GENERIC_SECRET' = @('EXAMPLE', 'PLACEHOLDER', 'YOUR_SECRET_HERE')
                    'GENERIC_API_KEY' = @('EXAMPLE', 'PLACEHOLDER', 'YOUR_API_KEY')
                }
                if ($allowlist.ContainsKey($RuleName)) {
                    foreach ($pattern in $allowlist[$RuleName]) {
                        if ($Value -like "*$pattern*") { return $true }
                    }
                }
                return $false
            }
            
            try {
                if ($file.Length -gt ($options.MaxFileSizeMB * 1MB)) { return @() }
                
                $content = [IO.File]::ReadAllText($file.FullName)
                $results = @()
                
                foreach ($rule in $rules) {
                    try {
                        $regex = [regex]::new($rule.Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
                        $matches = $regex.Matches($content)
                        
                        for ($i = 0; $i -lt [Math]::Min($matches.Count, $options.MaxMatches); $i++) {
                            $match = $matches[$i]
                            $secret = if ($match.Groups.Count -gt 1) { $match.Groups[1].Value } else { $match.Value }
                            
                            if ($rule.Entropy -and (Get-ShannonEntropy $secret) -lt $rule.Entropy) { continue }
                            if (Test-Allowlist $rule.Name $secret) { continue }
                            
                            $beforeMatch = $content.Substring(0, $match.Index)
                            $lineNumber = ($beforeMatch -split "`r?`n").Count
                            
                            $results += [PSCustomObject]@{
                                File = $file.FullName
                                Rule = $rule.Name
                                Description = $rule.Description
                                Sample = $secret.Substring(0, [Math]::Min($secret.Length, 60))
                                Severity = $rule.Severity
                                Category = $rule.Category
                                CWE = $rule.CWE
                                Line = $lineNumber
                                Column = 1
                                LineContent = "Parallel processing - full content not available"
                                Context = $secret.Substring(0, [Math]::Min($secret.Length, 40))
                                Entropy = (Get-ShannonEntropy $secret)
                                Confidence = $rule.Confidence
                                DetectionTime = Get-Date
                                FileSize = $file.Length
                                FileExtension = $file.Extension
                            }
                        }
                    }
                    catch { }
                }
                
                return $results
            }
            catch {
                return @()
            }
        }
        
        # Flatten results
        $allFindings = $allFindings | Where-Object { $_ -ne $null } | ForEach-Object { $_ }
    } else {
        Write-Log " Using sequential processing..." -Level Info
        
        foreach ($file in $files) {
            $findings = Scan-FileForSecrets -File $file -Rules $script:enhancedRules -Options @{
                MaxFileSizeMB = $MaxFileSizeMB
                MaxMatches = $MaxMatches
                RegexTimeoutSeconds = $RegexTimeoutSeconds
            }
            
            if ($null -ne $findings -and $findings.Count -gt 0) {
                $allFindings += $findings
                
                if ($PSCmdlet.MyInvocation.BoundParameters['Verbose']) {
                    Write-Log " Found $($findings.Count) secrets in: $($file.Name)" -Level Verbose
                }
            }
        }
    }
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Generate reports
    $reports = @{}
    
    if ($Format -in @('sarif', 'all')) {
        $reports.SARIF = Export-SARIFReport -Findings $allFindings -OutputPath $OutDir
    }
    
    if ($Format -in @('junit', 'all')) {
        $reports.JUnit = Export-JUnitReport -Findings $allFindings -OutputPath $OutDir
    }
    
    if ($Format -in @('legacy', 'all', 'auto')) {
        $legacyPath = Join-Path $OutDir "SECRETS_REPORT_V4.json"
        $allFindings | Select-Object File, Rule, Description, Sample, Severity, Category, CWE, Line, Entropy, Confidence | 
            ConvertTo-Json -Depth 4 | Out-File $legacyPath -Encoding UTF8
        $reports.Legacy = $legacyPath
    }
    
    # Generate summary
    $summary = @{
        ScanStartTime = $startTime.ToString("yyyy-MM-dd HH:mm:ss")
        ScanEndTime = $endTime.ToString("yyyy-MM-dd HH:mm:ss")
        DurationSeconds = [math]::Round($duration, 2)
        TotalFilesScanned = $files.Count
        TotalSecretsFound = $allFindings.Count
        BlockingSecrets = @($allFindings | Where-Object { $_.Severity -eq 'BLOCK' }).Count
        WarningSecrets = @($allFindings | Where-Object { $_.Severity -eq 'WARN' }).Count
        ProcessingMode = if ($Parallel) { "Parallel" } else { "Sequential" }
        ReportsGenerated = $reports.Keys
        Version = "4.0.0"
    }
    
    # Save summary
    $summaryPath = Join-Path $OutDir "secrets_scan_v4_summary.json"
    $summary | ConvertTo-Json -Depth 5 | Out-File $summaryPath -Encoding UTF8
    
    # Display results
    Write-Log "`n Secret Scan Complete!" -Level Info
    Write-Log " Duration: $duration seconds" -Level Info
    Write-Log " Files scanned: $($files.Count)" -Level Info
    Write-Log " Total secrets found: $($allFindings.Count)" -Level Info
    Write-Log " Blocking: $($summary.BlockingSecrets)" -Level Info
    Write-Log " Warnings: $($summary.WarningSecrets)" -Level Info
    
    foreach ($report in $reports.GetEnumerator()) {
        Write-Log " $($report.Key) report: $($report.Value)" -Level Info
    }
    
    return @{
        Summary = $summary
        Findings = $allFindings
        Reports = $reports
    }
}

# ===== MAIN EXECUTION =====
try {
    Write-Log " Agent Exo-Suit V4.0 'PERFECTION' - Secret Scanner Starting..." -Level Info
    
    # Create output directory
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    
    # Start scanning
    $results = Start-SecretScan -RootPath $Root
    
    # Check for blocking secrets
    $blockingSecrets = $results.Findings | Where-Object { $_.Severity -eq 'BLOCK' }
    
    if ($blockingSecrets.Count -gt 0 -or $Strict) {
        Write-Log " Blocking secrets found or strict mode enabled" -Level Error
        exit 3
    } elseif ($results.Findings.Count -gt 0) {
        Write-Log " Warning secrets found" -Level Warning
        exit 2
    } else {
        Write-Log " No secrets found - codebase is clean!" -Level Info
        exit 0
    }
    
} catch {
    Write-Log " Fatal error: $_" -Level Error
    Write-Log " Stack trace: $($_.ScriptStackTrace)" -Level Error
    exit 1
}

Write-Log " V4.0 Secret Scanner ready for production deployment!" -Level Info
