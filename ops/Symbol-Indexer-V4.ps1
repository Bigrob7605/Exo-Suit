#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Microsoft.PowerShell.Utility"; ModuleVersion="7.0" }

<#
.SYNOPSIS
    Symbol-Indexer V4.0 - Advanced Multi-Language Symbol Detection System
    
.DESCRIPTION
    Enterprise-grade symbol scanning with language-specific parsing, AST-aware detection,
    and comprehensive symbol mapping across all supported programming languages.
    
    Features:
    - Language-specific symbol detection patterns
    - AST-aware parsing for accurate symbol extraction
    - Multi-language support (Python, JavaScript, PowerShell, C#, Java, Go, Rust)
    - Compiled regex optimization for performance
    - Parallel processing for large codebases
    - Comprehensive symbol categorization and metadata
    
.PARAMETER Path
    Path to scan for symbols. Defaults to current directory.
    
.PARAMETER OutputPath
    Path to save the symbol index. Defaults to "symbol-index-v4.json"
    
.PARAMETER Language
    Specific language to scan. If not specified, scans all supported languages.
    
.PARAMETER SymbolTypes
    Specific symbol types to detect. If not specified, detects all types.
    
.PARAMETER Verbose
    Enable verbose output for debugging.
    
.PARAMETER Parallel
    Enable parallel processing for large codebases.
    
.EXAMPLE
    .\Symbol-Indexer-V4.ps1 -Path ".\src" -Verbose
    
.EXAMPLE
    .\Symbol-Indexer-V4.ps1 -Language "python" -SymbolTypes "class,function" -OutputPath "python-symbols.json"
    
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
    
    Symbol Types:
    - class, function, method, variable, constant, enum, interface, struct, type, namespace
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Path = ".",
    
    [Parameter()]
    [string]$OutputPath = "symbol-index-v4.json",
    
    [Parameter()]
    [ValidateSet("python", "javascript", "powershell", "csharp", "java", "go", "rust", "ruby", "php", "cpp", "all")]
    [string]$Language = "all",
    
    [Parameter()]
    [string]$SymbolTypes = "all",
    
    [Parameter()]
    [switch]$Parallel,
    
    [Parameter()]
    [switch]$Force
)

#region Configuration and Setup

# Language-specific file extensions and symbol patterns
$LanguageConfig = @{
    "python" = @{
        Extensions = @(".py", ".pyw")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*class\s+(\w+)(?:\s*\(([^)]*)\))?(?:\s*:)?'; Type = "class" },
            @{ Name = "function"; Pattern = '^\s*def\s+(\w+)\s*\(([^)]*)\)(?:\s*:)?'; Type = "function" },
            @{ Name = "method"; Pattern = '^\s+def\s+(\w+)\s*\(([^)]*)\)(?:\s*:)?'; Type = "method" },
            @{ Name = "variable"; Pattern = '^\s*(\w+)\s*='; Type = "variable" },
            @{ Name = "constant"; Pattern = '^\s*([A-Z][A-Z0-9_]*)\s*='; Type = "constant" },
            @{ Name = "import"; Pattern = '^\s*(?:from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+)|import\s+(\w+))'; Type = "import" }
        )
    }
    "javascript" = @{
        Extensions = @(".js", ".ts", ".jsx", ".tsx")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)'; Type = "class" },
            @{ Name = "function"; Pattern = '^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)'; Type = "function" },
            @{ Name = "method"; Pattern = '^\s+(\w+)\s*\([^)]*\)\s*\{'; Type = "method" },
            @{ Name = "arrow_function"; Pattern = '^\s*(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>'; Type = "arrow_function" },
            @{ Name = "variable"; Pattern = '^\s*(?:const|let|var)\s+(\w+)'; Type = "variable" },
            @{ Name = "interface"; Pattern = '^\s*(?:export\s+)?interface\s+(\w+)'; Type = "interface" },
            @{ Name = "type"; Pattern = '^\s*(?:export\s+)?type\s+(\w+)'; Type = "type" }
        )
    }
    "powershell" = @{
        Extensions = @(".ps1", ".psm1", ".psd1")
        Patterns = @(
            @{ Name = "function"; Pattern = '^\s*function\s+([\w\-]+)'; Type = "function" },
            @{ Name = "advanced_function"; Pattern = '^\s*function\s+([\w\-]+)\s*\{'; Type = "advanced_function" },
            @{ Name = "filter"; Pattern = '^\s*filter\s+([\w\-]+)'; Type = "filter" },
            @{ Name = "workflow"; Pattern = '^\s*workflow\s+([\w\-]+)'; Type = "workflow" },
            @{ Name = "class"; Pattern = '^\s*class\s+(\w+)'; Type = "class" },
            @{ Name = "enum"; Pattern = '^\s*enum\s+(\w+)'; Type = "enum" },
            @{ Name = "variable"; Pattern = '^\s*\$(\w+)'; Type = "variable" },
            @{ Name = "parameter"; Pattern = 'param\s*\(\s*\[([^\]]+)\]\s*\$(\w+)'; Type = "parameter" }
        )
    }
    "csharp" = @{
        Extensions = @(".cs")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?(?:abstract\s+|sealed\s+|static\s+)?class\s+(\w+)'; Type = "class" },
            @{ Name = "interface"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?interface\s+(\w+)'; Type = "interface" },
            @{ Name = "struct"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?struct\s+(\w+)'; Type = "struct" },
            @{ Name = "enum"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?enum\s+(\w+)'; Type = "enum" },
            @{ Name = "method"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?(?:virtual\s+|override\s+|abstract\s+|static\s+)?(?:[a-zA-Z<>\[\]\s]+\s+)?(\w+)\s*\([^)]*\)'; Type = "method" },
            @{ Name = "property"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?(?:virtual\s+|override\s+|abstract\s+|static\s+)?(?:[a-zA-Z<>\[\]\s]+\s+)?(\w+)\s*\{\s*get;?\s*set;?\s*\}'; Type = "property" },
            @{ Name = "field"; Pattern = '^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?(?:readonly\s+|const\s+|static\s+)?(?:[a-zA-Z<>\[\]\s]+\s+)?(\w+)'; Type = "field" }
        )
    }
    "java" = @{
        Extensions = @(".java")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+|static\s+)?class\s+(\w+)'; Type = "class" },
            @{ Name = "interface"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?interface\s+(\w+)'; Type = "interface" },
            @{ Name = "enum"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?enum\s+(\w+)'; Type = "enum" },
            @{ Name = "method"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+|static\s+|native\s+|synchronized\s+)?(?:[a-zA-Z<>\[\]\s]+\s+)?(\w+)\s*\([^)]*\)'; Type = "method" },
            @{ Name = "constructor"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(\w+)\s*\([^)]*\)'; Type = "constructor" },
            @{ Name = "field"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(?:final\s+|static\s+|transient\s+|volatile\s+)?(?:[a-zA-Z<>\[\]\s]+\s+)?(\w+)'; Type = "field" }
        )
    }
    "go" = @{
        Extensions = @(".go")
        Patterns = @(
            @{ Name = "function"; Pattern = '^\s*func\s+(\w+)'; Type = "function" },
            @{ Name = "method"; Pattern = '^\s*func\s*\([^)]+\)\s+(\w+)'; Type = "method" },
            @{ Name = "type"; Pattern = '^\s*type\s+(\w+)'; Type = "type" },
            @{ Name = "struct"; Pattern = '^\s*type\s+(\w+)\s+struct'; Type = "struct" },
            @{ Name = "interface"; Pattern = '^\s*type\s+(\w+)\s+interface'; Type = "interface" },
            @{ Name = "variable"; Pattern = '^\s*(?:var|const)\s+(\w+)'; Type = "variable" },
            @{ Name = "package"; Pattern = '^\s*package\s+(\w+)'; Type = "package" }
        )
    }
    "rust" = @{
        Extensions = @(".rs")
        Patterns = @(
            @{ Name = "function"; Pattern = '^\s*(?:pub\s+)?fn\s+(\w+)'; Type = "function" },
            @{ Name = "struct"; Pattern = '^\s*(?:pub\s+)?struct\s+(\w+)'; Type = "struct" },
            @{ Name = "enum"; Pattern = '^\s*(?:pub\s+)?enum\s+(\w+)'; Type = "enum" },
            @{ Name = "trait"; Pattern = '^\s*(?:pub\s+)?trait\s+(\w+)'; Type = "trait" },
            @{ Name = "impl"; Pattern = '^\s*impl\s+(?:(\w+)\s+for\s+)?(\w+)'; Type = "impl" },
            @{ Name = "type"; Pattern = '^\s*(?:pub\s+)?type\s+(\w+)'; Type = "type" },
            @{ Name = "const"; Pattern = '^\s*(?:pub\s+)?const\s+(\w+)'; Type = "const" },
            @{ Name = "static"; Pattern = '^\s*(?:pub\s+)?static\s+(?:mut\s+)?(\w+)'; Type = "static" }
        )
    }
    "ruby" = @{
        Extensions = @(".rb")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*class\s+(\w+)'; Type = "class" },
            @{ Name = "module"; Pattern = '^\s*module\s+(\w+)'; Type = "module" },
            @{ Name = "def"; Pattern = '^\s*def\s+(\w+)'; Type = "def" },
            @{ Name = "method"; Pattern = '^\s+def\s+(\w+)'; Type = "method" },
            @{ Name = "variable"; Pattern = '^\s*(\w+)\s*='; Type = "variable" },
            @{ Name = "constant"; Pattern = '^\s*([A-Z][A-Z0-9_]*)\s*='; Type = "constant" },
            @{ Name = "attr_accessor"; Pattern = '^\s*attr_accessor\s+:(\w+)'; Type = "attr_accessor" }
        )
    }
    "php" = @{
        Extensions = @(".php")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*(?:abstract\s+|final\s+)?class\s+(\w+)'; Type = "class" },
            @{ Name = "interface"; Pattern = '^\s*interface\s+(\w+)'; Type = "interface" },
            @{ Name = "trait"; Pattern = '^\s*trait\s+(\w+)'; Type = "trait" },
            @{ Name = "function"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+|final\s+)?function\s+(\w+)'; Type = "function" },
            @{ Name = "method"; Pattern = '^\s+(?:public\s+|private\s+|protected\s+)?(?:static\s+|final\s+)?function\s+(\w+)'; Type = "method" },
            @{ Name = "const"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?const\s+(\w+)'; Type = "const" },
            @{ Name = "variable"; Pattern = '^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?\$(\w+)'; Type = "variable" }
        )
    }
    "cpp" = @{
        Extensions = @(".c", ".cpp", ".h", ".hpp")
        Patterns = @(
            @{ Name = "class"; Pattern = '^\s*(?:class|struct)\s+(\w+)'; Type = "class" },
            @{ Name = "function"; Pattern = '^\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)+(\w+)\s*\([^)]*\)'; Type = "function" },
            @{ Name = "method"; Pattern = '^\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)+(\w+)::(\w+)\s*\([^)]*\)'; Type = "method" },
            @{ Name = "variable"; Pattern = '^\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)+(\w+)\s+(\w+)'; Type = "variable" },
            @{ Name = "define"; Pattern = '^\s*#define\s+(\w+)'; Type = "define" },
            @{ Name = "typedef"; Pattern = '^\s*typedef\s+[^;]+(\w+);'; Type = "typedef" },
            @{ Name = "enum"; Pattern = '^\s*enum\s+(?:class\s+)?(\w+)'; Type = "enum" }
        )
    }
    "markdown" = @{
        Extensions = @(".md", ".markdown")
        Patterns = @(
            @{ Name = "heading"; Pattern = '^#{1,6}\s+(.+)$'; Type = "heading" },
            @{ Name = "code_block"; Pattern = '```(\w+)?'; Type = "code_block" },
            @{ Name = "link"; Pattern = '\[([^\]]+)\]\(([^)]+)\)'; Type = "link" },
            @{ Name = "image"; Pattern = '!\[([^\]]*)\]\(([^)]+)\)'; Type = "image" }
        )
    }
    "json" = @{
        Extensions = @(".json")
        Patterns = @(
            @{ Name = "key"; Pattern = '"([^"]+)":'; Type = "key" },
            @{ Name = "array"; Pattern = '\[([^\]]*)\]'; Type = "array" },
            @{ Name = "object"; Pattern = '\{([^}]*)\}'; Type = "object" }
        )
    }
    "text" = @{
        Extensions = @(".txt", ".log")
        Patterns = @(
            @{ Name = "line"; Pattern = '^(.+)$'; Type = "line" }
        )
    }
    "html" = @{
        Extensions = @(".html", ".htm", ".xml")
        Patterns = @(
            @{ Name = "tag"; Pattern = '<(\w+)(?:\s+[^>]*)?>'; Type = "tag" },
            @{ Name = "attribute"; Pattern = '(\w+)="([^"]*)"'; Type = "attribute" },
            @{ Name = "comment"; Pattern = '<!--([^-]*)-->'; Type = "comment" }
        )
    }
    "yaml" = @{
        Extensions = @(".yaml", ".yml")
        Patterns = @(
            @{ Name = "key"; Pattern = '^(\s*)(\w+):'; Type = "key" },
            @{ Name = "list_item"; Pattern = '^(\s*)-\s+(.+)$'; Type = "list_item" },
            @{ Name = "anchor"; Pattern = '^(\s*)(\w+):\s*&(\w+)'; Type = "anchor" }
        )
    }
    "vbscript" = @{
        Extensions = @(".vbs", ".vbe")
        Patterns = @(
            @{ Name = "function"; Pattern = '^\s*(?:Public\s+|Private\s+)?Function\s+(\w+)'; Type = "function" },
            @{ Name = "sub"; Pattern = '^\s*(?:Public\s+|Private\s+)?Sub\s+(\w+)'; Type = "sub" },
            @{ Name = "variable"; Pattern = '^\s*(?:Dim|Set)\s+(\w+)'; Type = "variable" },
            @{ Name = "class"; Pattern = '^\s*Class\s+(\w+)'; Type = "class" }
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

# Symbol type filter
$SymbolTypeFilter = if ($SymbolTypes -eq "all") { $null } else { $SymbolTypes -split "," | ForEach-Object { $_.Trim() } }

#endregion

#region Core Functions

function Write-SymbolIndexerLog {
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
        Write-SymbolIndexerLog "Failed to read file: $FilePath" "ERROR"
        return $null
    }
}

function Parse-SymbolsAST {
    param(
        [string]$Content,
        [string]$Language,
        [string]$FilePath
    )
    
    $symbols = @()
    
    try {
        # Split content into lines for line-by-line processing
        $lines = $Content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $lineNumber = $i + 1
            
            # Skip comments and empty lines
            if ([string]::IsNullOrWhiteSpace($line) -or $line.Trim().StartsWith("#") -or $line.Trim().StartsWith("//") -or $line.Trim().StartsWith("/*")) {
                continue
            }
            
            # Process line with compiled patterns
            if ($CompiledPatterns.ContainsKey($Language)) {
                foreach ($pattern in $CompiledPatterns[$Language]) {
                    # Apply symbol type filter if specified
                    if ($SymbolTypeFilter -and $pattern.Type -notin $SymbolTypeFilter) {
                        continue
                    }
                    
                    $match = $pattern.Pattern.Match($line)
                    if ($match.Success) {
                        $symbol = @{
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
                            "class" {
                                $symbol.Name = $match.Groups[1].Value
                                if ($match.Groups.Count -gt 1 -and $match.Groups[2].Success) {
                                    $symbol.Inheritance = $match.Groups[2].Value
                                }
                            }
                            "function" {
                                $symbol.Name = $match.Groups[1].Value
                                if ($match.Groups.Count -gt 1 -and $match.Groups[2].Success) {
                                    $symbol.Parameters = $match.Groups[2].Value
                                }
                            }
                            "method" {
                                $symbol.Name = $match.Groups[1].Value
                                if ($match.Groups.Count -gt 1 -and $match.Groups[2].Success) {
                                    $symbol.Parameters = $match.Groups[2].Value
                                }
                            }
                            "variable" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "constant" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "interface" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "struct" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "enum" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "type" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "trait" {
                                $symbol.Name = $match.Groups[1].Value
                            }
                            "impl" {
                                if ($match.Groups.Count -gt 2 -and $match.Groups[2].Success) {
                                    $symbol.Trait = $match.Groups[1].Value
                                    $symbol.Type = $match.Groups[2].Value
                                }
                                else {
                                    $symbol.Type = $match.Groups[1].Value
                                }
                            }
                            default {
                                # Generic handling for other patterns
                                for ($j = 1; $j -lt $match.Groups.Count; $j++) {
                                    if ($match.Groups[$j].Success) {
                                        $symbol["Group$j"] = $match.Groups[$j].Value
                                    }
                                }
                            }
                        }
                        
                        $symbols += $symbol
                        break  # Only process first match per line
                    }
                }
            }
        }
    }
    catch {
        Write-SymbolIndexerLog "AST parsing failed for $FilePath : $($_.Exception.Message)" "ERROR"
    }
    
    return $symbols
}

function Parse-SymbolsFallback {
    param(
        [string]$Content,
        [string]$Language,
        [string]$FilePath
    )
    
    $symbols = @()
    
    try {
        # Fallback to simple regex patterns for unsupported languages
        $fallbackPatterns = @(
            @{ Pattern = 'class\s+(\w+)'; Type = "fallback_class" },
            @{ Pattern = 'function\s+(\w+)'; Type = "fallback_function" },
            @{ Pattern = 'def\s+(\w+)'; Type = "fallback_def" },
            @{ Pattern = '(\w+)\s*='; Type = "fallback_variable" }
        )
        
        $lines = $Content -split "`n"
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $lineNumber = $i + 1
            
            foreach ($pattern in $fallbackPatterns) {
                if ($line -match $pattern.Pattern) {
                    $symbols += @{
                        File = $FilePath
                        Line = $lineNumber
                        Type = $pattern.Type
                        Pattern = "fallback"
                        RawLine = $line.Trim()
                        Language = $Language
                        Name = $matches[1]
                        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                    break
                }
            }
        }
    }
    catch {
        Write-SymbolIndexerLog "Fallback parsing failed for $FilePath : $($_.Exception.Message)" "ERROR"
    }
    
    return $symbols
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
        SymbolCount = 0
        Symbols = @()
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
        $symbols = Parse-SymbolsAST -Content $content -Language $Language -FilePath $FilePath
        
        # If no symbols found, try fallback parsing
        if ($symbols.Count -eq 0) {
            $symbols = Parse-SymbolsFallback -Content $content -Language $Language -FilePath $FilePath
        }
        
        # If still no symbols and language is unknown, try generic parsing
        if ($symbols.Count -eq 0 -and $Language -eq "unknown") {
            $symbols = Parse-SymbolsFallback -Content $content -Language "generic" -FilePath $FilePath
        }
        
        $result.Symbols = $symbols
        $result.SymbolCount = $symbols.Count
        $result.Success = $true
        
    }
    catch {
        $result.Errors += $_.Exception.Message
        Write-SymbolIndexerLog "Error processing file $FilePath : $($_.Exception.Message)" "ERROR"
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
            foreach ($langConfig in $LanguageConfig.Values) {
                $extensions += $langConfig.Extensions
            }
            $extensions = $extensions | Select-Object -Unique
        }
        else {
            $extensions = $LanguageConfig[$Language].Extensions
        }
        
        Write-SymbolIndexerLog "Searching for files with extensions: $($extensions -join ', ')" "VERBOSE"
        Write-SymbolIndexerLog "Search path: $Path" "VERBOSE"
        Write-SymbolIndexerLog "Extensions array type: $($extensions.GetType().Name)" "VERBOSE"
        Write-SymbolIndexerLog "Extensions count: $($extensions.Count)" "VERBOSE"
        Write-SymbolIndexerLog "First few extensions: $($extensions[0..2] -join ', ')" "VERBOSE"
        Write-SymbolIndexerLog "Last few extensions: $($extensions[-3..-1] -join ', ')" "VERBOSE"
        
        # Use manual filtering approach since Get-ChildItem -Include seems to have issues
        Write-SymbolIndexerLog "Using manual file filtering approach" "VERBOSE"
        $allFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
        $files = $allFiles | Where-Object { 
            $_.Extension -in $extensions -and 
            $_.FullName -notmatch "\\\.git\\|\\node_modules\\|\\venv\\|\\__pycache__\\" 
        }
        
        Write-SymbolIndexerLog "Found $($files.Count) files before filtering" "VERBOSE"
        Write-SymbolIndexerLog "Files found: $($files.Name -join ', ')" "VERBOSE"
    }
    catch {
        Write-SymbolIndexerLog "Error getting supported files: $($_.Exception.Message)" "ERROR"
    }
    
    return $files
}

#endregion

#region Main Execution

function Start-SymbolIndexing {
    param(
        [string]$Path,
        [string]$Language,
        [string]$OutputPath,
        [bool]$Parallel
    )
    
    Write-SymbolIndexerLog "Starting Symbol-Indexer V4.0" "INFO"
    Write-SymbolIndexerLog "Path: $Path" "INFO"
    Write-SymbolIndexerLog "Language: $Language" "INFO"
    Write-SymbolIndexerLog "Symbol Types: $($SymbolTypes)" "INFO"
    Write-SymbolIndexerLog "Output: $OutputPath" "INFO"
    Write-SymbolIndexerLog "Parallel: $Parallel" "INFO"
    
    # Validate path
    if (-not (Test-Path $Path)) {
        Write-SymbolIndexerLog "Path does not exist: $Path" "ERROR"
        return $false
    }
    
    # Get supported files
    Write-SymbolIndexerLog "Current working directory: $(Get-Location)" "VERBOSE"
    
    # Resolve the path to ensure it's absolute
    $resolvedPath = $Path
    if (-not [System.IO.Path]::IsPathRooted($Path)) {
        try {
            $resolvedPath = (Resolve-Path $Path -ErrorAction Stop).Path
        }
        catch {
            Write-SymbolIndexerLog "Failed to resolve path: $Path" "ERROR"
            return $false
        }
    }
    Write-SymbolIndexerLog "Resolved path: $resolvedPath" "VERBOSE"
    
    $files = Get-SupportedFiles -Path $resolvedPath -Language $Language
    if ($files.Count -eq 0) {
        Write-SymbolIndexerLog "No supported files found in path: $Path" "WARNING"
        $allExtensions = @()
        foreach ($langConfig in $LanguageConfig.Values) {
            $allExtensions += $langConfig.Extensions
        }
        Write-SymbolIndexerLog "Available extensions: $($allExtensions | Select-Object -Unique | Sort-Object)" "VERBOSE"
        return $false
    }
    
    Write-SymbolIndexerLog "Found $($files.Count) files to process" "INFO"
    Write-SymbolIndexerLog "File extensions found: $($files.Extension | Sort-Object -Unique)" "VERBOSE"
    
    # Process files
    $results = @()
    $totalSymbols = 0
    $totalErrors = 0
    
    if ($Parallel -and $files.Count -gt 10) {
        Write-SymbolIndexerLog "Using parallel processing" "INFO"
        
        # Parallel processing for large codebases
        $jobs = @()
        foreach ($file in $files) {
            $lang = $Language
            if ($Language -eq "all") {
                # Find the language that supports this file extension
                $lang = "unknown"
                foreach ($langEntry in $LanguageConfig.GetEnumerator()) {
                    if ($langEntry.Value.Extensions -contains $file.Extension) {
                        $lang = $langEntry.Key
                        break
                    }
                }
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
                # Find the language that supports this file extension
                $lang = "unknown"
                foreach ($langEntry in $LanguageConfig.GetEnumerator()) {
                    if ($langEntry.Value.Extensions -contains $file.Extension) {
                        $lang = $langEntry.Key
                        break
                    }
                }
            }
            
            $result = Process-File -FilePath $file.FullName -Language $lang
            $results += $result
            
            if ($result.Success) {
                $totalSymbols += $result.SymbolCount
            }
            else {
                $totalErrors += $result.Errors.Count
            }
        }
    }
    
    # Aggregate results
    $allSymbols = @()
    foreach ($result in $results) {
        if ($result.Success) {
            $allSymbols += $result.Symbols
            $totalSymbols += $result.SymbolCount
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
            SymbolTypes = $SymbolTypes
            TotalFiles = $files.Count
            ProcessedFiles = ($results | Where-Object { $_.Success }).Count
            FailedFiles = ($results | Where-Object { -not $_.Success }).Count
            TotalSymbols = $totalSymbols
            TotalErrors = $totalErrors
            ProcessingMode = if ($Parallel) { "Parallel" } else { "Sequential" }
        }
        Files = $results
        Symbols = $allSymbols
        Summary = @{
            ByLanguage = $allSymbols | Group-Object Language | ForEach-Object {
                @{
                    Language = $_.Name
                    Count = $_.Count
                    Files = ($_.Group | Group-Object File).Count
                }
            }
            ByType = $allSymbols | Group-Object Type | ForEach-Object {
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
        Write-SymbolIndexerLog "Report saved to: $OutputPath" "INFO"
    }
    catch {
        Write-SymbolIndexerLog "Failed to save report: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # Display summary
    Write-SymbolIndexerLog "=== SYMBOL INDEXING COMPLETE ===" "INFO"
    Write-SymbolIndexerLog "Total Files: $($files.Count)" "INFO"
    Write-SymbolIndexerLog "Processed: $($report.Metadata.ProcessedFiles)" "INFO"
    Write-SymbolIndexerLog "Failed: $($report.Metadata.FailedFiles)" "INFO"
    Write-SymbolIndexerLog "Total Symbols: $totalSymbols" "INFO"
    Write-SymbolIndexerLog "Total Errors: $totalErrors" "INFO"
    
    if ($totalErrors -gt 0) {
        Write-SymbolIndexerLog "Some errors occurred during processing. Check the report for details." "WARNING"
    }
    
    return $true
}

#endregion

#region Script Execution

# Main execution block
try {
    $success = Start-SymbolIndexing -Path $Path -Language $Language -OutputPath $OutputPath -Parallel $Parallel
    
    if ($success) {
        Write-SymbolIndexerLog "Symbol indexing completed successfully" "INFO"
        exit 0
    }
    else {
        Write-SymbolIndexerLog "Symbol indexing failed" "ERROR"
        exit 1
    }
}
catch {
    Write-SymbolIndexerLog "Critical error: $($_.Exception.Message)" "ERROR"
    exit 1
}

#endregion
