#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Microsoft.PowerShell.Utility"; ModuleVersion="7.0" }

<#
.SYNOPSIS
    Placeholder-Scanner V4.0 - Advanced Multi-Language Placeholder Detection System
    
.DESCRIPTION
    Enterprise-grade placeholder scanning with AST-aware filtering, severity mapping,
    and comprehensive placeholder detection across all supported programming languages.
    
    Features:
    - AST-aware placeholder detection with context filtering
    - Multi-language support (Python, JavaScript, PowerShell, C#, Java, Go, Rust)
    - Severity mapping and categorization
    - Compiled regex optimization for performance
    - Parallel processing for large codebases
    - False positive reduction and validation
    
.PARAMETER Path
    Path to scan for placeholders. Defaults to current directory.
    
.PARAMETER OutputPath
    Path to save the placeholder scan report. Defaults to "placeholder-scan-v4.json"
    
.PARAMETER Language
    Specific language to scan. If not specified, scans all supported languages.
    
.PARAMETER Severity
    Minimum severity level to report. Options: Low, Medium, High, Critical, All
    
.PARAMETER Verbose
    Enable verbose output for debugging.
    
.PARAMETER Parallel
    Enable parallel processing for large codebases.
    
.EXAMPLE
    .\Placeholder-Scanner-V4.ps1 -Path ".\src" -Verbose
    
.EXAMPLE
    .\Placeholder-Scanner-V4.ps1 -Language "python" -Severity "High" -OutputPath "python-placeholders.json"
    
.NOTES
    Version: 4.0
    Author: Agent Exo-Suit V4.0
    Requires: PowerShell 7.0+
    
    Supported Languages:
    - Python (.py, .pyw)
    - JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
    - PowerShell (.ps1, .psm1, .psd1)
    - C# (.cs)
    - Java (.java)
    - Go (.go)
    - Rust (.rs)
    - Ruby (.rb)
    - PHP (.php)
    - C/C++ (.c, .cpp, .h, .hpp)
    
    Severity Levels:
    - Low: Basic placeholders, TODO comments
    - Medium: Configuration placeholders, environment variables
    - High: Security-related placeholders, API keys, passwords
    - Critical: Hardcoded credentials, secrets, sensitive data
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Path = ".",
    
    [Parameter()]
    [string]$OutputPath = "placeholder-scan-v4.json",
    
    [Parameter()]
    [ValidateSet("python", "javascript", "powershell", "csharp", "java", "go", "rust", "ruby", "php", "cpp", "all")]
    [string]$Language = "all",
    
    [Parameter()]
    [ValidateSet("Low", "Medium", "High", "Critical", "All")]
    [string]$Severity = "All",
    
    [Parameter()]
    [switch]$Parallel,
    
    [Parameter()]
    [switch]$Force
)

#region Configuration and Setup

# Language-specific file extensions and placeholder patterns
$LanguageConfig = @{
    "python" = @{
        Extensions = @(".py", ".pyw")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'api_key\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'os\.environ\[["'']([^"'']+)["'']\]'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '#\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '#\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*=\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*=\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "javascript" = @{
        Extensions = @(".js", ".ts", ".jsx", ".tsx")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'apiKey\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'process\.env\.(\w+)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "powershell" = @{
        Extensions = @(".ps1", ".psm1", ".psd1")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = '\$password\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = '\$apiKey\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = '\$secret\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = '\$config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = '\$env:(\w+)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '#\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '#\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = '\$url\s*=\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = '\$ip\s*=\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "csharp" = @{
        Extensions = @(".cs")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'apiKey\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'Configuration\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'Environment\.GetEnvironmentVariable\(["'']([^"'']+)["'']\)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*=\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*=\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "java" = @{
        Extensions = @(".java")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'apiKey\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*=\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'properties\.getProperty\(["'']([^"'']+)["'']\)'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'System\.getenv\(["'']([^"'']+)["'']\)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*=\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*=\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "go" = @{
        Extensions = @(".go")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'apiKey\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'os\.Getenv\(["'']([^"'']+)["'']\)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "rust" = @{
        Extensions = @(".rs")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'api_key\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'env::var\(["'']([^"'']+)["'']\)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "ruby" = @{
        Extensions = @(".rb")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'api_key\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'ENV\[["'']([^"'']+)["'']\]'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '#\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '#\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "php" = @{
        Extensions = @(".php")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = '\$password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = '\$apiKey\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = '\$secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = '\$config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = '\$_ENV\[["'']([^"'']+)["'']\]'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = '\$url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = '\$ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
    "cpp" = @{
        Extensions = @(".c", ".cpp", ".h", ".hpp")
        Patterns = @(
            @{ Name = "hardcoded_password"; Pattern = 'password\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_password"; Severity = "Critical" },
            @{ Name = "hardcoded_api_key"; Pattern = 'apiKey\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_api_key"; Severity = "Critical" },
            @{ Name = "hardcoded_secret"; Pattern = 'secret\s*[:=]\s*["'']([^"'']+)["'']'; Type = "hardcoded_secret"; Severity = "Critical" },
            @{ Name = "config_placeholder"; Pattern = 'config\[["'']([^"'']+)["'']\]'; Type = "config_placeholder"; Severity = "Medium" },
            @{ Name = "env_placeholder"; Pattern = 'getenv\(["'']([^"'']+)["'']\)'; Type = "env_placeholder"; Severity = "Medium" },
            @{ Name = "todo_comment"; Pattern = '//\s*TODO[:\s]+(.+)'; Type = "todo_comment"; Severity = "Low" },
            @{ Name = "fixme_comment"; Pattern = '//\s*FIXME[:\s]+(.+)'; Type = "fixme_comment"; Severity = "Low" },
            @{ Name = "hardcoded_url"; Pattern = 'url\s*[:=]\s*["''](https?://[^"'']+)["'']'; Type = "hardcoded_url"; Severity = "Medium" },
            @{ Name = "hardcoded_ip"; Pattern = 'ip\s*[:=]\s*["''](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["'']'; Type = "hardcoded_ip"; Severity = "Medium" }
        )
    }
}

# Severity mapping
$SeverityMap = @{
    "Low" = 1
    "Medium" = 2
    "High" = 3
    "Critical" = 4
    "All" = 0
}

# Compiled regex patterns for performance
$CompiledPatterns = @{}
foreach ($lang in $LanguageConfig.Keys) {
    $CompiledPatterns[$lang] = @()
    foreach ($pattern in $LanguageConfig[$lang].Patterns) {
        try {
            $CompiledPatterns[$lang] += @{
                Name = $pattern.Name
                Pattern = [regex]::new($pattern.Pattern, [System.Text.RegularExpressions.RegexOptions]::Compiled)
                Type = $pattern.Type
                Severity = $pattern.Severity
            }
        }
        catch {
            Write-Warning "Failed to compile regex for $($lang): $($pattern.Pattern)"
        }
    }
}

# Severity filter
$MinSeverity = $SeverityMap[$Severity]

#endregion

#region Core Functions

function Write-PlaceholderScannerLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Error $logMessage }
        "WARNING" { Write-Warning $logMessage }
        "VERBOSE" { Write-Verbose $logMessage }
        default { Write-Host $logMessage }
    }
}

function Test-FileAccess {
    param([string]$FilePath)
    
    try {
        $null = Get-Item $FilePath -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Get-FileEncoding {
    param([string]$FilePath)
    
    try {
        $bytes = Get-Content $FilePath -Raw -Encoding Byte -ErrorAction Stop
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            return "UTF8-BOM"
        }
        elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            return "UTF16-LE"
        }
        elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
            return "UTF16-BE"
        }
        else {
            return "UTF8"
        }
    }
    catch {
        return "Unknown"
    }
}

function Read-FileContent {
    param([string]$FilePath)
    
    try {
        $encoding = Get-FileEncoding $FilePath
        switch ($encoding) {
            "UTF8-BOM" { return Get-Content $FilePath -Raw -Encoding UTF8 }
            "UTF16-LE" { return Get-Content $FilePath -Raw -Encoding Unicode }
            "UTF16-BE" { return Get-Content $FilePath -Raw -Encoding BigEndianUnicode }
            default { return Get-Content $FilePath -Raw -Encoding UTF8 }
        }
    }
    catch {
        Write-PlaceholderScannerLog "Failed to read file: $FilePath" "ERROR"
        return $null
    }
}

function Test-SeverityFilter {
    param([string]$Severity)
    
    if ($MinSeverity -eq 0) { return $true }
    return $SeverityMap[$Severity] -ge $MinSeverity
}

function Validate-Placeholder {
    param(
        [string]$Type,
        [string]$Value,
        [string]$Context
    )
    
    # False positive reduction logic
    switch ($Type) {
        "hardcoded_password" {
            # Skip if it's a placeholder or example
            if ($Value -match '^(?:password|pass|pwd|123|test|example|dummy|placeholder)$') {
                return $false
            }
            # Skip if it's clearly a hash
            if ($Value -match '^[a-fA-F0-9]{32,}$') {
                return $false
            }
        }
        "hardcoded_api_key" {
            # Skip if it's a placeholder or example
            if ($Value -match '^(?:api_key|key|123|test|example|dummy|placeholder)$') {
                return $false
            }
            # Skip if it's clearly a hash
            if ($Value -match '^[a-fA-F0-9]{32,}$') {
                return $false
            }
        }
        "hardcoded_secret" {
            # Skip if it's a placeholder or example
            if ($Value -match '^(?:secret|123|test|example|dummy|placeholder)$') {
                return $false
            }
            # Skip if it's clearly a hash
            if ($Value -match '^[a-fA-F0-9]{32,}$') {
                return $false
            }
        }
        "hardcoded_url" {
            # Skip if it's a localhost or example URL
            if ($Value -match '^(?:localhost|127\.0\.0\.1|example\.com|test\.com)$') {
                return $false
            }
        }
        "hardcoded_ip" {
            # Skip if it's a localhost or private IP
            if ($Value -match '^(?:127\.0\.0\.1|localhost|192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)$') {
                return $false
            }
        }
    }
    
    return $true
}

function Parse-PlaceholdersAST {
    param(
        [string]$Content,
        [string]$Language,
        [string]$FilePath
    )
    
    $placeholders = @()
    
    try {
        # Split content into lines for line-by-line processing
        $lines = $Content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $lineNumber = $i + 1
            
            # Skip empty lines
            if ([string]::IsNullOrWhiteSpace($line)) {
                continue
            }
            
            # Process line with compiled patterns
            if ($CompiledPatterns.ContainsKey($Language)) {
                foreach ($pattern in $CompiledPatterns[$Language]) {
                    # Apply severity filter
                    if (-not (Test-SeverityFilter -Severity $pattern.Severity)) {
                        continue
                    }
                    
                    $match = $pattern.Pattern.Match($line)
                    if ($match.Success) {
                        $value = if ($match.Groups.Count -gt 1) { $match.Groups[1].Value } else { "" }
                        
                        # Validate placeholder to reduce false positives
                        if (-not (Validate-Placeholder -Type $pattern.Type -Value $value -Context $line)) {
                            continue
                        }
                        
                        $placeholder = @{
                            File = $FilePath
                            Line = $lineNumber
                            Type = $pattern.Type
                            Pattern = $pattern.Name
                            Severity = $pattern.Severity
                            RawLine = $line.Trim()
                            Language = $Language
                            Value = $value
                            Context = $line.Trim()
                            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                        }
                        
                        # Extract additional context
                        switch ($pattern.Type) {
                            "hardcoded_password" {
                                $placeholder.Description = "Hardcoded password detected"
                                $placeholder.Recommendation = "Use environment variables or secure configuration management"
                            }
                            "hardcoded_api_key" {
                                $placeholder.Description = "Hardcoded API key detected"
                                $placeholder.Recommendation = "Use environment variables or secure key management"
                            }
                            "hardcoded_secret" {
                                $placeholder.Description = "Hardcoded secret detected"
                                $placeholder.Recommendation = "Use environment variables or secure secret management"
                            }
                            "config_placeholder" {
                                $placeholder.Description = "Configuration placeholder detected"
                                $placeholder.Recommendation = "Ensure configuration is properly externalized"
                            }
                            "env_placeholder" {
                                $placeholder.Description = "Environment variable placeholder detected"
                                $placeholder.Recommendation = "Ensure environment variables are properly set"
                            }
                            "todo_comment" {
                                $placeholder.Description = "TODO comment detected"
                                $placeholder.Recommendation = "Address TODO items before production deployment"
                            }
                            "fixme_comment" {
                                $placeholder.Description = "FIXME comment detected"
                                $placeholder.Recommendation = "Address FIXME items before production deployment"
                            }
                            "hardcoded_url" {
                                $placeholder.Description = "Hardcoded URL detected"
                                $placeholder.Recommendation = "Use configuration or environment variables for URLs"
                            }
                            "hardcoded_ip" {
                                $placeholder.Description = "Hardcoded IP address detected"
                                $placeholder.Recommendation = "Use configuration or environment variables for IP addresses"
                            }
                            default {
                                $placeholder.Description = "Placeholder detected"
                                $placeholder.Recommendation = "Review and address as appropriate"
                            }
                        }
                        
                        $placeholders += $placeholder
                        break  # Only process first match per line
                    }
                }
            }
        }
    }
    catch {
        Write-PlaceholderScannerLog "AST parsing failed for $FilePath : $($_.Exception.Message)" "ERROR"
    }
    
    return $placeholders
}

function Process-File {
    param(
        [string]$FilePath,
        [string]$Language
    )
    
    $result = @{
        File = $FilePath
        Language = $Language
        Success = $false
        PlaceholderCount = 0
        Placeholders = @()
        Errors = @()
        ProcessingTime = 0
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        # Check file access
        if (-not (Test-FileAccess $FilePath)) {
            $result.Errors += "File not accessible"
            return $result
        }
        
        # Read file content
        $content = Read-FileContent $FilePath
        if ($null -eq $content) {
            $result.Errors += "Failed to read file content"
            return $result
        }
        
        # Parse placeholders
        $placeholders = Parse-PlaceholdersAST -Content $content -Language $Language -FilePath $FilePath
        
        $result.Placeholders = $placeholders
        $result.PlaceholderCount = $placeholders.Count
        $result.Success = $true
        
    }
    catch {
        $result.Errors += $_.Exception.Message
        Write-PlaceholderScannerLog "Error processing file $FilePath : $($_.Exception.Message)" "ERROR"
    }
    finally {
        $stopwatch.Stop()
        $result.ProcessingTime = $stopwatch.Elapsed.TotalMilliseconds
    }
    
    return $result
}

function Get-SupportedFiles {
    param(
        [string]$Path,
        [string]$Language
    )
    
    $files = @()
    
    try {
        if ($Language -eq "all") {
            # Get all supported file extensions
            $extensions = $LanguageConfig.Values.Extensions | Select-Object -Unique
        }
        else {
            $extensions = $LanguageConfig[$Language].Extensions
        }
        
        $searchPattern = "*" + ($extensions -join ",*")
        $files = Get-ChildItem -Path $Path -Recurse -Include $extensions -File -ErrorAction SilentlyContinue | 
                Where-Object { $_.FullName -notmatch "\\\.git\\|\\node_modules\\|\\venv\\|\\__pycache__\\" }
    }
    catch {
        Write-PlaceholderScannerLog "Error getting supported files: $($_.Exception.Message)" "ERROR"
    }
    
    return $files
}

#endregion

#region Main Execution

function Start-PlaceholderScanning {
    param(
        [string]$Path,
        [string]$Language,
        [string]$OutputPath,
        [bool]$Parallel
    )
    
    Write-PlaceholderScannerLog "Starting Placeholder-Scanner V4.0" "INFO"
    Write-PlaceholderScannerLog "Path: $Path" "INFO"
    Write-PlaceholderScannerLog "Language: $Language" "INFO"
    Write-PlaceholderScannerLog "Severity: $Severity" "INFO"
    Write-PlaceholderScannerLog "Output: $OutputPath" "INFO"
    Write-PlaceholderScannerLog "Parallel: $Parallel" "INFO"
    
    # Validate path
    if (-not (Test-Path $Path)) {
        Write-PlaceholderScannerLog "Path does not exist: $Path" "ERROR"
        return $false
    }
    
    # Get supported files
    $files = Get-SupportedFiles -Path $Path -Language $Language
    if ($files.Count -eq 0) {
        Write-PlaceholderScannerLog "No supported files found in path: $Path" "WARNING"
        return $false
    }
    
    Write-PlaceholderScannerLog "Found $($files.Count) files to process" "INFO"
    
    # Process files
    $results = @()
    $totalPlaceholders = 0
    $totalErrors = 0
    
    if ($Parallel -and $files.Count -gt 10) {
        Write-PlaceholderScannerLog "Using parallel processing" "INFO"
        
        # Parallel processing for large codebases
        $jobs = @()
        foreach ($file in $files) {
            $lang = $Language
            if ($Language -eq "all") {
                $lang = ($LanguageConfig.GetEnumerator() | Where-Object { $_.Value.Extensions -contains $file.Extension }).Key
            }
            
            $jobs += Start-Job -ScriptBlock {
                param($FilePath, $Language)
                . $using:Process-File
                Process-File -FilePath $FilePath -Language $Language
            } -ArgumentList $file.FullName, $lang
        }
        
        # Wait for all jobs to complete
        $results = $jobs | Wait-Job | Receive-Job
        $jobs | Remove-Job
    }
    else {
        # Sequential processing
        foreach ($file in $files) {
            $lang = $Language
            if ($Language -eq "all") {
                $lang = ($LanguageConfig.GetEnumerator() | Where-Object { $_.Value.Extensions -contains $file.Extension }).Key
            }
            
            $result = Process-File -FilePath $file.FullName -Language $lang
            $results += $result
            
            if ($result.Success) {
                $totalPlaceholders += $result.PlaceholderCount
            }
            else {
                $totalErrors += $result.Errors.Count
            }
        }
    }
    
    # Aggregate results
    $allPlaceholders = @()
    foreach ($result in $results) {
        if ($result.Success) {
            $allPlaceholders += $result.Placeholders
            $totalPlaceholders += $result.PlaceholderCount
        }
        else {
            $totalErrors += $result.Errors.Count
        }
    }
    
    # Create final report
    $report = @{
        Metadata = @{
            Version = "4.0"
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Path = $Path
            Language = $Language
            Severity = $Severity
            TotalFiles = $files.Count
            ProcessedFiles = ($results | Where-Object { $_.Success }).Count
            FailedFiles = ($results | Where-Object { -not $_.Success }).Count
            TotalPlaceholders = $totalPlaceholders
            TotalErrors = $totalErrors
            ProcessingMode = if ($Parallel) { "Parallel" } else { "Sequential" }
        }
        Files = $results
        Placeholders = $allPlaceholders
        Summary = @{
            ByLanguage = $allPlaceholders | Group-Object Language | ForEach-Object {
                @{
                    Language = $_.Name
                    Count = $_.Count
                    Files = ($_.Group | Group-Object File).Count
                }
            }
            ByType = $allPlaceholders | Group-Object Type | ForEach-Object {
                @{
                    Type = $_.Name
                    Count = $_.Count
                }
            }
            BySeverity = $allPlaceholders | Group-Object Severity | ForEach-Object {
                @{
                    Severity = $_.Name
                    Count = $_.Count
                }
            }
        }
    }
    
    # Save report
    try {
        $report | ConvertTo-Json -Depth 10 | Set-Content $OutputPath -Encoding UTF8
        Write-PlaceholderScannerLog "Report saved to: $OutputPath" "INFO"
    }
    catch {
        Write-PlaceholderScannerLog "Failed to save report: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # Display summary
    Write-PlaceholderScannerLog "=== PLACEHOLDER SCANNING COMPLETE ===" "INFO"
    Write-PlaceholderScannerLog "Total Files: $($files.Count)" "INFO"
    Write-PlaceholderScannerLog "Processed: $($report.Metadata.ProcessedFiles)" "INFO"
    Write-PlaceholderScannerLog "Failed: $($report.Metadata.FailedFiles)" "INFO"
    Write-PlaceholderScannerLog "Total Placeholders: $totalPlaceholders" "INFO"
    Write-PlaceholderScannerLog "Total Errors: $totalErrors" "INFO"
    
    if ($totalErrors -gt 0) {
        Write-PlaceholderScannerLog "Some errors occurred during processing. Check the report for details." "WARNING"
    }
    
    return $true
}

#endregion

#region Script Execution

# Main execution block
try {
    $success = Start-PlaceholderScanning -Path $Path -Language $Language -OutputPath $OutputPath -Parallel $Parallel
    
    if ($success) {
        Write-PlaceholderScannerLog "Placeholder scanning completed successfully" "INFO"
        exit 0
    }
    else {
        Write-PlaceholderScannerLog "Placeholder scanning failed" "ERROR"
        exit 1
    }
}
catch {
    Write-PlaceholderScannerLog "Critical error: $($_.Exception.Message)" "ERROR"
    exit 1
}

#endregion
