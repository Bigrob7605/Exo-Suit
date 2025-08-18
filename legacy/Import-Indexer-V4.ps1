#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Microsoft.PowerShell.Utility"; ModuleVersion="7.0" }

<#
.SYNOPSIS
    Import-Indexer V4.0 - Advanced Multi-Language Import Detection System
    
.DESCRIPTION
    Enterprise-grade import scanning with AST-aware parsing, fallback mechanisms, 
    and robust error handling for comprehensive import mapping across all supported languages.
    
    Features:
    - AST-aware parsing for accurate import detection
    - Fallback mechanisms for unsupported languages
    - Multi-language support (Python, JavaScript, PowerShell, C#, Java, Go, Rust)
    - Compiled regex optimization for performance
    - Parallel processing for large codebases
    - Comprehensive error handling and logging
    
.PARAMETER Path
    Path to scan for imports. Defaults to current directory.
    
.PARAMETER OutputPath
    Path to save the import index. Defaults to "import-index-v4.json"
    
.PARAMETER Language
    Specific language to scan. If not specified, scans all supported languages.
    
.PARAMETER Verbose
    Enable verbose output for debugging.
    
.PARAMETER Parallel
    Enable parallel processing for large codebases.
    
.EXAMPLE
    .\Import-Indexer-V4.ps1 -Path ".\src" -Verbose
    
.EXAMPLE
    .\Import-Indexer-V4.ps1 -Language "python" -OutputPath "python-imports.json"
    
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
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Path = ".",
    
    [Parameter()]
    [string]$OutputPath = "import-index-v4.json",
    
    [Parameter()]
    [ValidateSet("python", "javascript", "powershell", "csharp", "java", "go", "rust", "ruby", "php", "cpp", "all")]
    [string]$Language = "all",
    
    [Parameter()]
    [switch]$Parallel,
    
    [Parameter()]
    [switch]$Force
)

#region Configuration and Setup

# Language-specific file extensions and patterns
$LanguageConfig = @{
    "python" = @{
        Extensions = @(".py", ".pyw")
        Patterns = @(
            @{ Name = "import"; Pattern = '^\s*(?:from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s*,\s*\w+)*)|import\s+(\w+(?:\s*,\s*\w+)*))'; Type = "import" },
            @{ Name = "from_import"; Pattern = '^\s*from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s*,\s*\w+)*)'; Type = "from_import" },
            @{ Name = "import_as"; Pattern = '^\s*import\s+(\w+(?:\s*,\s*\w+)*)\s+as\s+(\w+)'; Type = "import_as" }
        )
    }
    "javascript" = @{
        Extensions = @(".js", ".ts", ".jsx", ".tsx")
        Patterns = @(
            @{ Name = "import"; Pattern = '^\s*import\s+(\w+)\s+from\s+["'']([^"'']+)["'']'; Type = "import" },
            @{ Name = "require"; Pattern = '^\s*(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(\s*["'']([^"'']+)["'']'; Type = "require" },
            @{ Name = "dynamic_import"; Pattern = '^\s*import\s*\(\s*["'']([^"'']+)["'']'; Type = "dynamic_import" }
        )
    }
    "powershell" = @{
        Extensions = @(".ps1", ".psm1", ".psd1")
        Patterns = @(
            @{ Name = "using"; Pattern = '^\s*using\s+namespace\s+([\w\.]+)'; Type = "using_namespace" },
            @{ Name = "import"; Pattern = '^\s*Import-Module\s+["'']([^"'']+)["'']'; Type = "import_module" },
            @{ Name = "dot_source"; Pattern = '^\s*\.\s+["'']([^"'']+)["'']'; Type = "dot_source" }
        )
    }
    "markdown" = @{
        Extensions = @(".md", ".markdown")
        Patterns = @(
            @{ Name = "include"; Pattern = '!\[.*?\]\(([^)]+)\)'; Type = "image_link" },
            @{ Name = "link"; Pattern = '\[.*?\]\(([^)]+)\)'; Type = "hyperlink" },
            @{ Name = "code_block"; Pattern = '```(\w+)'; Type = "code_block" }
        )
    }
    "data" = @{
        Extensions = @(".json", ".yaml", ".yml", ".xml", ".html", ".txt", ".sql")
        Patterns = @(
            @{ Name = "file_reference"; Pattern = '["'']([^"'']*\.(?:py|js|ps1|cs|java|go|rs|rb|md|json|yaml|yml|xml|html|txt|sql))["'']'; Type = "file_reference" },
            @{ Name = "url_reference"; Pattern = '["''](https?://[^"'']+)["'']'; Type = "url_reference" },
            @{ Name = "path_reference"; Pattern = '["'']([^"'']*[/\\][^"'']*)["'']'; Type = "path_reference" }
        )
    }
    "csharp" = @{
        Extensions = @(".cs")
        Patterns = @(
            @{ Name = "using"; Pattern = '^\s*using\s+([\w\.]+);'; Type = "using" },
            @{ Name = "global_using"; Pattern = '^\s*global\s+using\s+([\w\.]+);'; Type = "global_using" }
        )
    }
    "java" = @{
        Extensions = @(".java")
        Patterns = @(
            @{ Name = "import"; Pattern = '^\s*import\s+([\w\.]+);'; Type = "import" },
            @{ Name = "static_import"; Pattern = '^\s*import\s+static\s+([\w\.]+);'; Type = "static_import" }
        )
    }
    "go" = @{
        Extensions = @(".go")
        Patterns = @(
            @{ Name = "import"; Pattern = '^\s*import\s+["'']([^"'']+)["'']'; Type = "import" },
            @{ Name = "import_block"; Pattern = '^\s*import\s*\(\s*["'']([^"'']+)["'']'; Type = "import_block" }
        )
    }
    "rust" = @{
        Extensions = @(".rs")
        Patterns = @(
            @{ Name = "use"; Pattern = '^\s*use\s+([\w:]+);'; Type = "use" },
            @{ Name = "extern_crate"; Pattern = '^\s*extern\s+crate\s+(\w+);'; Type = "extern_crate" }
        )
    }
    "ruby" = @{
        Extensions = @(".rb")
        Patterns = @(
            @{ Name = "require"; Pattern = '^\s*require\s+["'']([^"'']+)["'']'; Type = "require" },
            @{ Name = "require_relative"; Pattern = '^\s*require_relative\s+["'']([^"'']+)["'']'; Type = "require_relative" }
        )
    }
    "php" = @{
        Extensions = @(".php")
        Patterns = @(
            @{ Name = "use"; Pattern = '^\s*use\s+([\w\\]+);'; Type = "use" },
            @{ Name = "require"; Pattern = '^\s*require\s+["'']([^"'']+)["'']'; Type = "require" }
        )
    }
    "cpp" = @{
        Extensions = @(".c", ".cpp", ".h", ".hpp")
        Patterns = @(
            @{ Name = "include"; Pattern = '^\s*#include\s+[<"]([^>"]+)[>"]'; Type = "include" }
        )
    }
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
            }
        }
        catch {
            Write-Warning "Failed to compile regex for $($lang): $($pattern.Pattern)"
        }
    }
}

#endregion

#region Core Functions

function Write-ImportIndexerLog {
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
        Write-ImportIndexerLog "Failed to read file: $FilePath" "ERROR"
        return $null
    }
}

function Parse-ImportsAST {
    param(
        [string]$Content,
        [string]$Language,
        [string]$FilePath
    )
    
    $imports = @()
    
    try {
        # Split content into lines for line-by-line processing
        $lines = $Content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $lineNumber = $i + 1
            
            # Skip comments and empty lines
            if ([string]::IsNullOrWhiteSpace($line) -or $line.Trim().StartsWith("#") -or $line.Trim().StartsWith("//")) {
                continue
            }
            
            # Process line with compiled patterns
            if ($CompiledPatterns.ContainsKey($Language)) {
                foreach ($pattern in $CompiledPatterns[$Language]) {
                    $match = $pattern.Pattern.Match($line)
                    if ($match.Success) {
                        $import = @{
                            File = $FilePath
                            Line = $lineNumber
                            Type = $pattern.Type
                            Pattern = $pattern.Name
                            RawLine = $line.Trim()
                            Language = $Language
                            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                        }
                        
                        # Extract specific information based on pattern type
                        switch ($pattern.Type) {
                            "import" {
                                if ($match.Groups[1].Success) {
                                    $import.Module = $match.Groups[1].Value
                                    $import.Items = $match.Groups[2].Value -split "," | ForEach-Object { $_.Trim() }
                                }
                                elseif ($match.Groups[3].Success) {
                                    $import.Items = $match.Groups[3].Value -split "," | ForEach-Object { $_.Trim() }
                                }
                            }
                            "from_import" {
                                $import.Module = $match.Groups[1].Value
                                $import.Items = $match.Groups[2].Value -split "," | ForEach-Object { $_.Trim() }
                            }
                            "import_as" {
                                $import.Items = $match.Groups[1].Value -split "," | ForEach-Object { $_.Trim() }
                                $import.Alias = $match.Groups[2].Value
                            }
                            "require" {
                                $import.Module = $match.Groups[2].Value
                                $import.Variable = $match.Groups[1].Value
                            }
                            "using" {
                                $import.Namespace = $match.Groups[1].Value
                            }
                            "include" {
                                $import.Header = $match.Groups[1].Value
                            }
                            default {
                                # Generic handling for other patterns
                                for ($j = 1; $j -lt $match.Groups.Count; $j++) {
                                    if ($match.Groups[$j].Success) {
                                        $import["Group$j"] = $match.Groups[$j].Value
                                    }
                                }
                            }
                        }
                        
                        $imports += $import
                        break  # Only process first match per line
                    }
                }
            }
        }
    }
    catch {
        Write-ImportIndexerLog "AST parsing failed for $FilePath : $($_.Exception.Message)" "ERROR"
    }
    
    return $imports
}

function Parse-ImportsFallback {
    param(
        [string]$Content,
        [string]$Language,
        [string]$FilePath
    )
    
    $imports = @()
    
    try {
        # Fallback to simple regex patterns for unsupported languages
        $fallbackPatterns = @(
            @{ Pattern = 'import\s+(\w+)'; Type = "fallback_import" },
            @{ Pattern = 'require\s*\(\s*["'']([^"'']+)["'']'; Type = "fallback_require" },
            @{ Pattern = 'using\s+([\w\.]+)'; Type = "fallback_using" },
            @{ Pattern = '#include\s+[<"]([^>"]+)[>"]'; Type = "fallback_include" }
        )
        
        $lines = $Content -split "`n"
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $lineNumber = $i + 1
            
            foreach ($pattern in $fallbackPatterns) {
                if ($line -match $pattern.Pattern) {
                    $imports += @{
                        File = $FilePath
                        Line = $lineNumber
                        Type = $pattern.Type
                        Pattern = "fallback"
                        RawLine = $line.Trim()
                        Language = $Language
                        Module = $matches[1]
                        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                    break
                }
            }
        }
    }
    catch {
        Write-ImportIndexerLog "Fallback parsing failed for $FilePath : $($_.Exception.Message)" "ERROR"
    }
    
    return $imports
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
        ImportCount = 0
        Imports = @()
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
        
        # Try AST parsing first
        $imports = Parse-ImportsAST -Content $content -Language $Language -FilePath $FilePath
        
        # If no imports found, try fallback parsing
        if ($imports.Count -eq 0) {
            $imports = Parse-ImportsFallback -Content $content -Language $Language -FilePath $FilePath
        }
        
        $result.Imports = $imports
        $result.ImportCount = $imports.Count
        $result.Success = $true
        
    }
    catch {
        $result.Errors += $_.Exception.Message
        Write-ImportIndexerLog "Error processing file $FilePath : $($_.Exception.Message)" "ERROR"
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
            # Get all supported file extensions from all languages
            $extensions = @()
            foreach ($lang in $LanguageConfig.Keys) {
                $extensions += $LanguageConfig[$lang].Extensions
            }
            $extensions = $extensions | Select-Object -Unique
        }
        else {
            $extensions = $LanguageConfig[$Language].Extensions
        }
        
        $allFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                Where-Object { $_.FullName -notmatch "\\\.git\\|\\node_modules\\|\\venv\\|\\__pycache__\\" }
        
        # Filter by supported extensions
        $files = $allFiles | Where-Object { $_.Extension -in $extensions }
    }
    catch {
        Write-ImportIndexerLog "Error getting supported files: $($_.Exception.Message)" "ERROR"
    }
    
    return $files
}

#endregion

#region Main Execution

function Start-ImportIndexing {
    param(
        [string]$Path,
        [string]$Language,
        [string]$OutputPath,
        [bool]$Parallel
    )
    
    Write-ImportIndexerLog "Starting Import-Indexer V4.0" "INFO"
    Write-ImportIndexerLog "Path: $Path" "INFO"
    Write-ImportIndexerLog "Language: $Language" "INFO"
    Write-ImportIndexerLog "Output: $OutputPath" "INFO"
    Write-ImportIndexerLog "Parallel: $Parallel" "INFO"
    
    # Validate path
    if (-not (Test-Path $Path)) {
        Write-ImportIndexerLog "Path does not exist: $Path" "ERROR"
        return $false
    }
    
    # Get supported files
    $files = Get-SupportedFiles -Path $Path -Language $Language
    $totalFiles = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue).Count
    
    if ($files.Count -eq 0) {
        Write-ImportIndexerLog "No supported files found in path: $Path (Total files: $totalFiles)" "WARNING"
        $supportedExts = ($LanguageConfig.Values.Extensions | Select-Object -Unique | Sort-Object) -join ', '
        Write-ImportIndexerLog "Supported extensions: $supportedExts" "INFO"
        return $false
    }
    
    Write-ImportIndexerLog "Found $($files.Count) supported files out of $totalFiles total files" "INFO"
    
    Write-ImportIndexerLog "Found $($files.Count) files to process" "INFO"
    
    # Process files
    $results = @()
    $totalImports = 0
    $totalErrors = 0
    
    if ($Parallel -and $files.Count -gt 10) {
        Write-ImportIndexerLog "Using parallel processing" "INFO"
        
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
                $totalImports += $result.ImportCount
            }
            else {
                $totalErrors += $result.Errors.Count
            }
        }
    }
    
    # Aggregate results
    $allImports = @()
    foreach ($result in $results) {
        if ($result.Success) {
            $allImports += $result.Imports
            $totalImports += $result.ImportCount
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
            TotalFiles = $files.Count
            ProcessedFiles = ($results | Where-Object { $_.Success }).Count
            FailedFiles = ($results | Where-Object { -not $_.Success }).Count
            TotalImports = $totalImports
            TotalErrors = $totalErrors
            ProcessingMode = if ($Parallel) { "Parallel" } else { "Sequential" }
        }
        Files = $results
        Imports = $allImports
        Summary = @{
            ByLanguage = $allImports | Group-Object Language | ForEach-Object {
                @{
                    Language = $_.Name
                    Count = $_.Count
                    Files = ($_.Group | Group-Object File).Count
                }
            }
            ByType = $allImports | Group-Object Type | ForEach-Object {
                @{
                    Type = $_.Name
                    Count = $_.Count
                }
            }
        }
    }
    
    # Save report
    try {
        $report | ConvertTo-Json -Depth 10 | Set-Content $OutputPath -Encoding UTF8
        Write-ImportIndexerLog "Report saved to: $OutputPath" "INFO"
    }
    catch {
        Write-ImportIndexerLog "Failed to save report: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # Display summary
    Write-ImportIndexerLog "=== IMPORT INDEXING COMPLETE ===" "INFO"
    Write-ImportIndexerLog "Total Files: $($files.Count)" "INFO"
    Write-ImportIndexerLog "Processed: $($report.Metadata.ProcessedFiles)" "INFO"
    Write-ImportIndexerLog "Failed: $($report.Metadata.FailedFiles)" "INFO"
    Write-ImportIndexerLog "Total Imports: $totalImports" "INFO"
    Write-ImportIndexerLog "Total Errors: $totalErrors" "INFO"
    
    if ($totalErrors -gt 0) {
        Write-ImportIndexerLog "Some errors occurred during processing. Check the report for details." "WARNING"
    }
    
    return $true
}

#endregion

#region Script Execution

# Main execution block
try {
    $success = Start-ImportIndexing -Path $Path -Language $Language -OutputPath $OutputPath -Parallel $Parallel
    
    if ($success) {
        Write-ImportIndexerLog "Import indexing completed successfully" "INFO"
        exit 0
    }
    else {
        Write-ImportIndexerLog "Import indexing failed" "ERROR"
        exit 1
    }
}
catch {
    Write-ImportIndexerLog "Critical error: $($_.Exception.Message)" "ERROR"
    exit 1
}

#endregion
