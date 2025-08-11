# Agent Exo-Suit V4.0 "PERFECTION" - Emoji Sentinel
# Ultra-robust emoji detection and logging system with bulletproof path handling

[CmdletBinding()]
param(
    [switch]$Scan,
    [switch]$Purge,
    [switch]$Report,
    [switch]$EnableVerbose,
    [Parameter(Mandatory=$false)]
    [string]$Path = ".",  # DEFAULT TO CURRENT DIR (Fix #1)
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\restore\EMOJI_REPORT.json",  # SAFE DEFAULT (Fix #2)
    [switch]$Force,
    [switch]$Benchmark,
    [int]$MaxFileSizeMB = 10,
    [switch]$SkipBinary,
    [switch]$Parallel
)

# ===== BULLETPROOF PATH HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Emergency fallback paths
$script:SafeScanPath = $null
$script:SafeOutputDir = $null

# ===== ADVANCED LOGGING =====
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry -ForegroundColor $Color
    
    if ($EnableVerbose) {
        $logPath = Join-Path (Get-Location) "emoji_sentinel_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== SYSTEM VALIDATION =====
function Test-SystemRequirements {
    Write-Log " Validating system requirements..." -Color Cyan
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 7) {
        Write-Log " PowerShell 7+ recommended for optimal performance" -Color Yellow
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize
    $memoryGB = [math]::Round($memory / 1024 / 1024, 2)
    Write-Log " Available memory: $memoryGB GB" -Color Green
    
    if ($memoryGB -lt 2) {
        Write-Log " Low memory detected. Consider reducing MaxFileSizeMB" -Color Yellow
    }
    
    # Check parallel processing capability
    $cpuCores = (Get-CimInstance -ClassName Win32_Processor).NumberOfLogicalProcessors
    Write-Log " CPU cores: $cpuCores" -Color Green
    
    if ($Parallel -and $cpuCores -lt 2) {
        Write-Log " Single core detected. Parallel processing disabled" -Color Yellow
        $script:Parallel = $false
    }
}

# ===== PATH VALIDATION ENGINE =====
function Get-SafeAbsolutePath {
    param([string]$InputPath, [string]$Context = "Path")
    
    try {
        # Handle null/empty
        if ([string]::IsNullOrWhiteSpace($InputPath)) {
            Write-Log " Empty $Context provided, using current directory" -Color Yellow
            return (Get-Location).Path
        }
        
        # Expand relative paths
        $absolutePath = [System.IO.Path]::GetFullPath($InputPath)
        
        # Create directory if doesn't exist
        if ($Context -eq "Output" -and !(Test-Path $absolutePath)) {
            $dir = Split-Path $absolutePath -Parent
            if (!(Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log " Created output directory: $dir" -Color Green
            }
        }
        
        return $absolutePath
    }
    catch {
        Write-Log " Invalid ${Context}: '$InputPath'" -Color Red
        Write-Log "   Error: $_" -Color Red
        return (Get-Location).Path  # Emergency fallback
    }
}

# ===== ENHANCED SCAN PATH RESOLUTION =====
function Resolve-ScanPath {
    param([string]$InputPath)
    
    $safePath = Get-SafeAbsolutePath -InputPath $InputPath -Context "Scan"
    
    # Ensure directory exists
    if (!(Test-Path $safePath -PathType Container)) {
        try {
            New-Item -ItemType Directory -Path $safePath -Force | Out-Null
            Write-Log " Created scan directory: $safePath" -Color Green
        }
        catch {
            Write-Log " Using fallback directory: $(Get-Location)" -Color Yellow
            return (Get-Location).Path
        }
    }
    
    return $safePath
}

# ===== ENHANCED EMOJI DETECTION =====
class EmojiDetectionResult {
    [string]$FilePath
    [int]$LineNumber
    [int]$ColumnNumber
    [string]$Emoji
    [string]$Context
    [string]$LineContent
    [string]$FileExtension
    [datetime]$DetectionTime
    [string]$Severity
    [string]$UnicodeRange
    [int]$CodePoint
    [double]$Confidence
}

# Ultra-comprehensive emoji patterns with performance optimization
$script:emojiRanges = @(
    @{ Start = 0x1F600; End = 0x1F64F; Name = "Emoticons" },
    @{ Start = 0x1F300; End = 0x1F5FF; Name = "Misc Symbols and Pictographs" },
    @{ Start = 0x1F680; End = 0x1F6FF; Name = "Transport and Map" },
    @{ Start = 0x1F1E0; End = 0x1F1FF; Name = "Regional Indicator" },
    @{ Start = 0x2600; End = 0x26FF; Name = "Misc Symbols" },
    @{ Start = 0x2700; End = 0x27BF; Name = "Dingbats" },
    @{ Start = 0x1F900; End = 0x1F9FF; Name = "Supplemental Symbols and Pictographs" },
    @{ Start = 0x1F018; End = 0x1F270; Name = "Playing Cards" },
    @{ Start = 0x1F000; End = 0x1F02F; Name = "Mahjong Tiles" },
    @{ Start = 0x1F0A0; End = 0x1F0FF; Name = "Playing Cards" },
    @{ Start = 0x1F100; End = 0x1F64F; Name = "Enclosed Alphanumeric Supplement" },
    @{ Start = 0x1F650; End = 0x1F67F; Name = "Ornamental Dingbats" },
    @{ Start = 0x1F700; End = 0x1F77F; Name = "Alchemical Symbols" },
    @{ Start = 0x1F780; End = 0x1F7FF; Name = "Geometric Shapes" },
    @{ Start = 0x1F800; End = 0x1F8FF; Name = "Supplemental Arrows-C" },
    @{ Start = 0x1FA00; End = 0x1FA6F; Name = "Chess Symbols" },
    @{ Start = 0x1FAB0; End = 0x1FAFF; Name = "Symbols and Pictographs Extended" },
    @{ Start = 0x1FB00; End = 0x1FBFF; Name = "Legacy Computing" },
    @{ Start = 0x1FC00; End = 0x1FCFF; Name = "Legacy Computing" },
    @{ Start = 0x1FD00; End = 0x1FDFF; Name = "Legacy Computing" },
    @{ Start = 0x1FE00; End = 0x1FEFF; Name = "Legacy Computing" },
    @{ Start = 0x1FF00; End = 0x1FFFF; Name = "Legacy Computing" },
    @{ Start = 0x20000; End = 0x2A6DF; Name = "CJK Unified Ideographs Extension B" },
    @{ Start = 0x2A700; End = 0x2B73F; Name = "CJK Unified Ideographs Extension C" },
    @{ Start = 0x2B740; End = 0x2B81F; Name = "CJK Unified Ideographs Extension D" },
    @{ Start = 0x2B820; End = 0x2CEAF; Name = "CJK Unified Ideographs Extension E" },
    @{ Start = 0x2CEB0; End = 0x2EBEF; Name = "CJK Unified Ideographs Extension F" },
    @{ Start = 0x2F800; End = 0x2FA1F; Name = "CJK Compatibility Ideographs Supplement" },
    @{ Start = 0x30000; End = 0x3134F; Name = "CJK Unified Ideographs Extension G" },
    @{ Start = 0x31350; End = 0x323AF; Name = "CJK Unified Ideographs Extension H" },
    @{ Start = 0xE000; End = 0xF8FF; Name = "Private Use Area" },
    @{ Start = 0xF0000; End = 0xFFFFF; Name = "Private Use Area" },
    @{ Start = 0x100000; End = 0x10FFFF; Name = "Private Use Area" }
)

function Test-EmojiInString {
    param([string]$Text)
    
    if ([string]::IsNullOrEmpty($Text)) { return $false }
    
    foreach ($char in $Text.ToCharArray()) {
        $codePoint = [int][char]$char
        
        # Check if character is in any emoji range
        foreach ($range in $script:emojiRanges) {
            if ($codePoint -ge $range.Start -and $codePoint -le $range.End) {
                return $true
            }
        }
        
        # Check for high Unicode characters
        if ($codePoint -gt 0xFFFF) { return $true }
    }
    return $false
}

function Get-EmojisInString {
    param([string]$Text)
    
    $emojis = @()
    
    for ($i = 0; $i -lt $Text.Length; $i++) {
        $char = $Text[$i]
        $codePoint = [int][char]$char
        
        # Check if character is in any emoji range
        foreach ($range in $script:emojiRanges) {
            if ($codePoint -ge $range.Start -and $codePoint -le $range.End) {
                $emojis += [PSCustomObject]@{
                    Character = $char
                    CodePoint = $codePoint
                    Position = $i
                    Range = $range.Name
                    Confidence = 1.0
                }
                break
            }
        }
        
        # Check for high Unicode characters
        if ($codePoint -gt 0xFFFF) {
            $emojis += [PSCustomObject]@{
                Character = $char
                CodePoint = $codePoint
                Position = $i
                Range = "High Unicode"
                Confidence = 0.8
            }
        }
    }
    
    return $emojis
}

# ===== ENHANCED FILE PROCESSING =====
function Test-FileShouldScan {
    param(
        [System.IO.FileInfo]$File,
        [string]$ScanPath,
        [string[]]$ExcludeDirs,
        [string[]]$ScanExtensions,
        [int]$MaxFileSizeMB
    )
    
    # Check file size
    $fileSizeMB = [math]::Round($File.Length / 1MB, 2)
    if ($fileSizeMB -gt $MaxFileSizeMB) {
        Write-Log " Skipping large file: $($File.Name) ($fileSizeMB MB)" -Color Yellow
        return $false
    }
    
    # Check extension
    $ext = $File.Extension.ToLower()
    if ($ScanExtensions -notcontains $ext) {
        return $false
    }
    
    # Check if in excluded directory
    $relativePath = ""
    try {
        if ($File.FullName.Length -gt $ScanPath.Length) {
            $relativePath = $File.FullName.Substring($ScanPath.Length).TrimStart('\', '/')
        } else {
            $relativePath = $File.Name
        }
        
        # Ensure we have a valid relative path
        if ([string]::IsNullOrEmpty($relativePath)) {
            $relativePath = $File.Name
        }
    }
    catch {
        $relativePath = $File.Name
    }
    
    $pathParts = $relativePath -split '[\\/]'
    
    foreach ($excludeDir in $ExcludeDirs) {
        if ($pathParts -contains $excludeDir) {
            return $false
        }
    }
    
    # Binary file detection
    if ($SkipBinary) {
        try {
            $sample = [System.IO.File]::ReadAllBytes($File.FullName)
            if ($sample.Length -gt 1024) { $sample = $sample[0..1023] }
            
            # Check for null bytes (binary indicator)
            if ($sample -contains 0) {
                Write-Log " Skipping binary file: $($File.Name)" -Color Yellow
                return $false
            }
        }
        catch {
            Write-Log " Could not read file for binary detection: $($File.Name)" -Color Yellow
        }
    }
    
    return $true
}

function Scan-FileForEmojis {
    param(
        [string]$FilePath,
        [string]$ScanPath
    )
    
    # Validate parameters
    if ([string]::IsNullOrEmpty($FilePath)) {
        Write-Log " Error: FilePath is null or empty" -Color Yellow
        return @()
    }
    
    if ([string]::IsNullOrEmpty($ScanPath)) {
        Write-Log " Error: ScanPath is null or empty" -Color Yellow
        return @()
    }
    
    # Final safety check - ensure FilePath is a valid, resolvable path
    try {
        $resolvedPath = [System.IO.Path]::GetFullPath($FilePath)
        if ([string]::IsNullOrEmpty($resolvedPath) -or $resolvedPath.Length -lt 3) {
            Write-Log " Error: FilePath cannot be resolved: $FilePath" -Color Yellow
            return @()
        }
    }
    catch {
        Write-Log " Error: FilePath validation failed: $FilePath" -Color Yellow
        return @()
    }
    
    try {
        # Additional validation
        if (-not (Test-Path $FilePath -PathType Leaf)) {
            Write-Log " Warning: File not found: $FilePath" -Color Yellow
            return @()
        }
        
        try {
            if ($EnableVerbose) {
                Write-Log " Debug: About to read file: $FilePath" -Color Cyan
            }
            $content = Get-Content -Path $FilePath -Raw -Encoding UTF8 -ErrorAction Stop
            
            # Handle null content (empty files)
            if ($null -eq $content) {
                if ($EnableVerbose) {
                    Write-Log " Debug: File is empty, setting content to empty string" -Color Cyan
                }
                $content = ""
            }
            
            # Ensure content is a string
            if ($content -is [array]) {
                $content = $content -join "`n"
            }
            if ($content -isnot [string]) {
                $content = $content.ToString()
            }
            
            if ($EnableVerbose) {
                Write-Log " Debug: Successfully read file, content type: $($content.GetType().Name), length: $($content.Length)" -Color Cyan
            }
        }
        catch {
            Write-Log " Warning: Could not read file $FilePath : $_" -Color Yellow
            return @()
        }
        
        if ([string]::IsNullOrEmpty($content)) {
            return @()
        }
        
        $emojis = Get-EmojisInString $content
        $results = @()
        
        foreach ($emoji in $emojis) {
            # Get line number and context
            $beforeEmoji = $content.Substring(0, $emoji.Position)
            $lineNumber = ($beforeEmoji -split "`r?`n").Count
            $lineStart = $beforeEmoji.LastIndexOf("`n")
            if ($lineStart -eq -1) { $lineStart = 0 } else { $lineStart++ }
            
            $lineEnd = $content.IndexOf("`n", $emoji.Position)
            if ($lineEnd -eq -1) { $lineEnd = $content.Length }
            
            # Safe line content extraction
            $lineLength = $lineEnd - $lineStart
            if ($lineLength -gt 0) {
                $lineContent = $content.Substring($lineStart, $lineLength).Trim()
            } else {
                $lineContent = ""
            }
            
            # Safe context extraction
            $contextStart = [math]::Max(0, $emoji.Position - $lineStart - 20)
            $contextLength = [math]::Min(40, $lineContent.Length - $contextStart)
            if ($contextLength -gt 0) {
                $context = $lineContent.Substring($contextStart, $contextLength)
            } else {
                $context = $lineContent
            }
            
            # Create relative path safely
            $relativePath = ""
            try {
                if ($FilePath.Length -gt $ScanPath.Length) {
                    $relativePath = $FilePath.Substring($ScanPath.Length).TrimStart('\', '/')
                } else {
                    $relativePath = $FilePath
                }
                
                # Ensure we have a valid relative path
                if ([string]::IsNullOrEmpty($relativePath)) {
                    $relativePath = [System.IO.Path]::GetFileName($FilePath)
                }
            }
            catch {
                $relativePath = [System.IO.Path]::GetFileName($FilePath)
            }
            
            $result = [EmojiDetectionResult]@{
                FilePath = $relativePath
                LineNumber = $lineNumber
                ColumnNumber = $emoji.Position - $lineStart + 1
                Emoji = $emoji.Character
                Context = $context
                LineContent = $lineContent
                FileExtension = [System.IO.Path]::GetExtension($FilePath)
                DetectionTime = Get-Date
                Severity = if ($emoji.Confidence -gt 0.9) { "HIGH" } else { "MEDIUM" }
                UnicodeRange = $emoji.Range
                CodePoint = $emoji.CodePoint
                Confidence = $emoji.Confidence
            }
            
            $results += $result
        }
        
        return $results
        
    }
    catch {
        Write-Log " Error scanning file $FilePath : $_" -Color Yellow
        return @()
    }
}

# ===== MAIN SCANNING FUNCTION =====
function Start-EmojiScan {
    param([string]$ScanPath)
    
    Write-Log " Starting V4.0 Ultra-robust Emoji Scan..." -Color Cyan
    Write-Log " Scan directory: $ScanPath" -Color Green
    
    $startTime = Get-Date
    $allResults = @()
    $scannedFiles = 0
    $filesWithEmojis = 0
    
    # File extensions to scan
    $scanExtensions = @(
        '.ps1', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.less',
        '.md', '.txt', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf',
        '.bat', '.cmd', '.sh', '.bash', '.zsh', '.fish', '.c', '.cpp', '.h', '.hpp',
        '.java', '.kt', '.swift', '.go', '.rs', '.php', '.rb', '.pl', '.lua', '.r',
        '.sql', '.psm1', '.psd1', '.psc1', '.vbs', '.wsf', '.hta', '.reg'
    )
    
    # Directories to exclude
    $excludeDirs = @(
        '.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', 'venv',
        'env', '.env', 'build', 'dist', 'target', 'bin', 'obj', '.vs', '.vscode',
        'restore', 'context', 'gpu_rag_env', 'mermaid', 'rag_env', 'test-emoji-pack'
    )
    
    # Get all files to scan
    Write-Log " Discovering files..." -Color Cyan
    
    try {
        $allFiles = Get-ChildItem -Path $ScanPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            if ($null -eq $_ -or [string]::IsNullOrEmpty($_.FullName)) {
                Write-Log " Warning: Skipping file with null or empty FullName" -Color Yellow
                return $false
            }
            
            # Additional validation - ensure FullName is a valid path
            try {
                $testPath = $_.FullName
                if ([string]::IsNullOrEmpty($testPath) -or $testPath.Length -lt 3) {
                    Write-Log " Warning: Skipping file with invalid path length: $testPath" -Color Yellow
                    return $false
                }
                
                # Test if the path can be resolved
                $resolvedPath = [System.IO.Path]::GetFullPath($testPath)
                if ([string]::IsNullOrEmpty($resolvedPath)) {
                    Write-Log " Warning: Skipping file with unresolvable path: $testPath" -Color Yellow
                    return $false
                }
            }
            catch {
                Write-Log " Warning: Skipping file with path validation error: $($_.FullName)" -Color Yellow
                return $false
            }
            
            Test-FileShouldScan -File $_ -ScanPath $ScanPath -ExcludeDirs $excludeDirs -ScanExtensions $scanExtensions -MaxFileSizeMB $MaxFileSizeMB
        }
        
        # Filter out any remaining null or invalid files
        $allFiles = $allFiles | Where-Object { 
            $null -ne $_ -and 
            -not [string]::IsNullOrEmpty($_.FullName) -and 
            $_.FullName.Length -gt 3
        }
        
        Write-Log " Found $($allFiles.Count) valid files to scan" -Color Green
    }
    catch {
        Write-Log " Error discovering files: $_" -Color Red
        throw "Failed to discover files: $_"
    }
    
    if ($allFiles.Count -eq 0) {
        Write-Log " No files found to scan" -Color Yellow
        return @{
            Summary = @{
                ScanStartTime = $startTime
                ScanEndTime = Get-Date
                DurationSeconds = 0
                TotalFilesScanned = 0
                FilesWithEmojis = 0
                TotalEmojisFound = 0
                ScanDirectory = $ScanPath
                ExcludedDirectories = $excludeDirs
                ScannedExtensions = $scanExtensions
                Version = "4.0.0"
            }
            Detections = @()
        }
    }
    
    # Scan files
    if ($EnableVerbose) {
        Write-Log " Debug: Parallel flag: $Parallel" -Color Cyan
        Write-Log " Debug: File count: $($allFiles.Count)" -Color Cyan
        Write-Log " Debug: Parallel condition: $($Parallel -and $allFiles.Count -gt 10)" -Color Cyan
    }
    
    if ($Parallel -and $allFiles.Count -gt 10) {
        Write-Log " Using parallel processing..." -Color Cyan
        $allResults = $allFiles | ForEach-Object -ThrottleLimit ([Environment]::ProcessorCount) -Parallel {
            $file = $_
            $scanPath = $using:ScanPath
            
            # Import functions in parallel context
            function Test-EmojiInString {
                param([string]$Text)
                if ([string]::IsNullOrEmpty($Text)) { return $false }
                
                foreach ($char in $Text.ToCharArray()) {
                    $codePoint = [int][char]$char
                    if ($codePoint -ge 0x1F600 -and $codePoint -le 0x1F64F) { return $true }
                    if ($codePoint -ge 0x1F300 -and $codePoint -le 0x1F5FF) { return $true }
                    if ($codePoint -ge 0x1F680 -and $codePoint -le 0x1F6FF) { return $true }
                    if ($codePoint -gt 0xFFFF) { return $true }
                }
                return $false
            }
            
            try {
                $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
                if ([string]::IsNullOrEmpty($content) -or -not (Test-EmojiInString $content)) {
                    return @()
                }
                
                # Simple emoji detection for parallel processing
                $results = @()
                $lines = $content -split "`r?`n"
                
                for ($i = 0; $i -lt $lines.Length; $i++) {
                    $line = $lines[$i]
                    if (Test-EmojiInString $line) {
                        # Create relative path safely for parallel processing
                        $relativePath = ""
                        try {
                            if ($file.FullName.Length -gt $scanPath.Length) {
                                $relativePath = $file.FullName.Substring($scanPath.Length).TrimStart('\', '/')
                            } else {
                                $relativePath = $file.FullName
                            }
                            
                            # Ensure we have a valid relative path
                            if ([string]::IsNullOrEmpty($relativePath)) {
                                $relativePath = $file.Name
                            }
                        }
                        catch {
                            $relativePath = $file.Name
                        }
                        
                        $results += [PSCustomObject]@{
                            FilePath = $relativePath
                            LineNumber = $i + 1
                            ColumnNumber = 1
                            Emoji = ""  # Placeholder for parallel processing
                            Context = $line.Substring(0, [math]::Min(40, $line.Length))
                            LineContent = $line
                            FileExtension = $file.Extension
                            DetectionTime = Get-Date
                            Severity = "HIGH"
                            UnicodeRange = "Parallel"
                            CodePoint = 0
                            Confidence = 1.0
                        }
                    }
                }
                
                return $results
            }
            catch {
                return @()
            }
        }
        
        # Flatten results
        $allResults = $allResults | Where-Object { $_ -ne $null } | ForEach-Object { $_ }
        $scannedFiles = $allFiles.Count
        $filesWithEmojis = ($allResults | Group-Object FilePath).Count
    }
    else {
        Write-Log " Using sequential processing..." -Color Cyan
        
        # Initialize allResults for sequential processing
        $allResults = @()
        
        foreach ($file in $allFiles) {
            $scannedFiles++
            
            # Validate file path before processing
            if ([string]::IsNullOrEmpty($file.FullName)) {
                Write-Log " Warning: Skipping file with empty FullName" -Color Yellow
                continue
            }
            
            # Debug: Log the current file being processed
            if ($EnableVerbose) {
                Write-Log " Processing file: $($file.FullName)" -Color Cyan
            }
            
            if ($scannedFiles % 100 -eq 0) {
                $progress = [math]::Round(($scannedFiles / $allFiles.Count) * 100, 1)
                Write-Progress -Activity "Emoji Scan Progress" -Status "$scannedFiles / $($allFiles.Count) files" -PercentComplete $progress
            }
            
            # Global error handler for any path-related issues
            try {
                # Additional debugging for file path
                if ($EnableVerbose) {
                    Write-Log " Debug: File object type: $($file.GetType().Name)" -Color Cyan
                    Write-Log " Debug: File.FullName: '$($file.FullName)'" -Color Cyan
                    Write-Log " Debug: File.Name: '$($file.Name)'" -Color Cyan
                    Write-Log " Debug: ScanPath: '$ScanPath'" -Color Cyan
                }
                
                # Extra validation before calling Scan-FileForEmojis
                if ([string]::IsNullOrWhiteSpace($file.FullName)) {
                    Write-Log " Warning: Skipping file with null/empty FullName: $($file.Name)" -Color Yellow
                    continue
                }
                
                $results = Scan-FileForEmojis -FilePath $file.FullName -ScanPath $ScanPath
            }
            catch [System.Management.Automation.ParameterBindingException] {
                if ($_.Exception.Message -like "*Cannot bind argument to parameter 'Path' because it is an empty string*") {
                    Write-Log " Warning: Skipping file with empty path binding: $($file.FullName)" -Color Yellow
                    continue
                }
                Write-Log " Error processing file $($file.FullName): $_" -Color Red
                continue
            }
            catch {
                Write-Log " Error processing file $($file.FullName): $_" -Color Red
                continue
            }
            
            # Ensure results is an array
            if ($null -eq $results) { $results = @() }
            if ($results -isnot [array]) { $results = @($results) }
            
            if ($results.Count -gt 0) {
                $filesWithEmojis++
                $allResults += $results
                
                if ($EnableVerbose) {
                    Write-Log " Found $($results.Count) emojis in: $($file.Name)" -Color Red
                }
            }
        }
    }
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    if ($EnableVerbose) {
        Write-Log " Debug: Scan completed, processing results..." -Color Cyan
        Write-Log " Debug: allResults count: $($allResults.Count)" -Color Cyan
        Write-Log " Debug: allResults type: $($allResults.GetType().Name)" -Color Cyan
    }
    
    # Final safety check - filter out any results with empty FilePath
    if ($null -eq $allResults) { $allResults = @() }
    $validResults = $allResults | Where-Object { $_ -and $_.FilePath -and -not [string]::IsNullOrEmpty($_.FilePath) }
    if ($null -eq $validResults) { $validResults = @() }
    $validFilesWithEmojis = if ($validResults.Count -gt 0) { ($validResults | Group-Object FilePath).Count } else { 0 }
    
    if ($EnableVerbose) {
        Write-Log " Debug: validResults count: $($validResults.Count)" -Color Cyan
        Write-Log " Debug: validFilesWithEmojis: $validFilesWithEmojis" -Color Cyan
    }
    
    # Generate scan summary
    $scanSummary = @{
        ScanStartTime = $startTime
        ScanEndTime = $endTime
        DurationSeconds = [math]::Round($duration, 2)
        TotalFilesScanned = $scannedFiles
        FilesWithEmojis = $validFilesWithEmojis
        TotalEmojisFound = $validResults.Count
        ScanDirectory = $ScanPath
        ExcludedDirectories = $excludeDirs
        ScannedExtensions = $scanExtensions
        Version = "4.0.0"
        ProcessingMode = if ($Parallel) { "Parallel" } else { "Sequential" }
        MaxFileSizeMB = $MaxFileSizeMB
        SkipBinary = $SkipBinary
    }
    
    # Update allResults to only contain valid results
    $allResults = $validResults
    
    # Save results
    if ($EnableVerbose) {
        Write-Log " Debug: Creating resultsData object..." -Color Cyan
        Write-Log " Debug: allResults count: $($allResults.Count)" -Color Cyan
        Write-Log " Debug: scanSummary created successfully" -Color Cyan
    }
    
    # Create detections array safely
    $detectionsArray = @()
    if ($allResults -and $allResults.Count -gt 0) {
        if ($EnableVerbose) {
            Write-Log " Debug: Processing detections..." -Color Cyan
        }
        $detectionsArray = @($allResults | ForEach-Object {
            if ($_ -and $_.FilePath -and -not [string]::IsNullOrEmpty($_.FilePath)) {
                @{
                    FilePath = $_.FilePath
                    LineNumber = $_.LineNumber
                    ColumnNumber = $_.ColumnNumber
                    Emoji = $_.Emoji
                    Context = $_.Context
                    LineContent = $_.LineContent
                    FileExtension = $_.FileExtension
                    DetectionTime = if ($_.DetectionTime) { $_.DetectionTime.ToString("yyyy-MM-dd HH:mm:ss") } else { (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") }
                    Severity = $_.Severity
                    UnicodeRange = $_.UnicodeRange
                    CodePoint = $_.CodePoint
                    Confidence = $_.Confidence
                }
            }
        } | Where-Object { $_ -ne $null -and $_ -and $_.FilePath -and -not [string]::IsNullOrEmpty($_.FilePath) })
    } else {
        if ($EnableVerbose) {
            Write-Log " Debug: No detections, using empty array" -Color Cyan
        }
        $detectionsArray = @()
    }
    
    # Ensure detectionsArray is always an array
    if ($detectionsArray -isnot [array]) {
        $detectionsArray = @($detectionsArray)
    }
    
    $resultsData = @{
        Summary = $scanSummary
        Detections = $detectionsArray
    }
    
    if ($EnableVerbose) {
        Write-Log " Debug: resultsData object created successfully" -Color Cyan
        Write-Log " Debug: resultsData.Summary count: $($resultsData.Summary.Count)" -Color Cyan
        Write-Log " Debug: resultsData.Detections count: $($resultsData.Detections.Count)" -Color Cyan
    }
    
    Write-Log " Scan completed successfully. Returning results to main execution." -Color Green
    
    if ($EnableVerbose) {
        Write-Log " Debug: About to return resultsData..." -Color Cyan
        Write-Log " Debug: resultsData type: $($resultsData.GetType().Name)" -Color Cyan
        Write-Log " Debug: resultsData keys: $($resultsData.Keys -join ', ')" -Color Cyan
    }
    
    return $resultsData
}

# ===== BENCHMARKING =====
function Start-EmojiBenchmark {
    param([string]$scanPath)
    
    Write-Log " Starting V4.0 Emoji Sentinel Benchmark..." -Color Cyan
    
    $benchmarkResults = @{
        Sequential = @{}
        Parallel = @{}
        Summary = @{}
    }
    
    # Test sequential processing
    Write-Log " Testing sequential processing..." -Color Yellow
    $script:Parallel = $false
    $startTime = Get-Date
    $sequentialResults = Start-EmojiScan -ScanPath $scanPath
    $sequentialDuration = ((Get-Date) - $startTime).TotalSeconds
    
    $benchmarkResults.Sequential = @{
        Duration = $sequentialDuration
        FilesScanned = $sequentialResults.Summary.TotalFilesScanned
        EmojisFound = $sequentialResults.Summary.TotalEmojisFound
        Performance = [math]::Round($sequentialResults.Summary.TotalFilesScanned / $sequentialDuration, 2)
    }
    
    # Test parallel processing
    Write-Log " Testing parallel processing..." -Color Yellow
    $script:Parallel = $true
    $startTime = Get-Date
    $parallelResults = Start-EmojiScan -ScanPath $scanPath
    $parallelDuration = ((Get-Date) - $startTime).TotalSeconds
    
    $benchmarkResults.Parallel = @{
        Duration = $parallelDuration
        FilesScanned = $parallelResults.Summary.TotalFilesScanned
        EmojisFound = $parallelResults.Summary.TotalEmojisFound
        Performance = [math]::Round($parallelResults.Summary.TotalFilesScanned / $parallelDuration, 2)
    }
    
    # Calculate improvements
    $speedup = if ($parallelDuration -gt 0) { [math]::Round($sequentialDuration / $parallelDuration, 2) } else { 0 }
    $efficiency = if ($speedup -gt 0) { [math]::Round(($speedup / [Environment]::ProcessorCount) * 100, 1) } else { 0 }
    
    $benchmarkResults.Summary = @{
        Speedup = $speedup
        Efficiency = $efficiency
        RecommendedMode = if ($speedup -gt 1.2) { "Parallel" } else { "Sequential" }
        CpuCores = [Environment]::ProcessorCount
    }
    
    # Display benchmark results
    Write-Log "`n BENCHMARK RESULTS:" -Color Cyan
    Write-Log "=====================" -Color Cyan
    Write-Log " Sequential: $($benchmarkResults.Sequential.Duration)s ($($benchmarkResults.Sequential.Performance) files/sec)" -Color Yellow
    Write-Log " Parallel: $($benchmarkResults.Parallel.Duration)s ($($benchmarkResults.Parallel.Performance) files/sec)" -Color Yellow
    Write-Log " Speedup: ${speedup}x" -Color Green
    Write-Log " Efficiency: ${efficiency}%" -Color Green
    Write-Log " Recommended: $($benchmarkResults.Summary.RecommendedMode)" -Color Cyan
    
    # Save benchmark results
    $benchmarkPath = $OutputPath -replace '\.json$', '_benchmark.json'
    $benchmarkResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $benchmarkPath -Encoding UTF8
    Write-Log " Benchmark saved to: $benchmarkPath" -Color Green
    
    return $benchmarkResults
}

# ===== MAIN EXECUTION =====
try {
    Write-Log " Agent Exo-Suit V4.0 'PERFECTION' - Emoji Sentinel Starting..." -Color Cyan
    
    # Validate system requirements
    Test-SystemRequirements
    
    # Resolve scan path
    $scanPath = Resolve-ScanPath -InputPath $Path
    
    # Initialize
    Write-Log " System validation complete" -Color Green
    Write-Log " Scan path: $scanPath" -Color Green
    Write-Log " Configuration:" -Color Green
    Write-Log "   - Max file size: $MaxFileSizeMB MB" -Color White
    Write-Log "   - Skip binary: $SkipBinary" -Color White
    Write-Log "   - Parallel: $Parallel" -Color White
    Write-Log "   - Verbose: $EnableVerbose" -Color White
    
    # Execute based on parameters
    if ($Scan) {
        try {
            Start-EmojiScan -ScanPath $scanPath
        }
        catch [System.Management.Automation.ParameterBindingException] {
            Write-Log " Parameter binding error in scan: $_" -Color Red
            throw
        }
    }
    elseif ($Purge) {
        Write-Log " Purge functionality not yet implemented in V4.0" -Color Yellow
        Write-Log " Use V3.0 for purge operations" -Color Yellow
    }
    elseif ($Report) {
        Write-Log " Report functionality not yet implemented in V4.0" -Color Yellow
        Write-Log " Use V3.0 for report viewing" -Color Yellow
    }
    elseif ($Benchmark) {
        try {
            Start-EmojiBenchmark -ScanPath $scanPath
        }
        catch [System.Management.Automation.ParameterBindingException] {
            Write-Log " Parameter binding error in benchmark: $_" -Color Red
            throw
        }
    }
    else {
        # Default: run scan
        try {
            Write-Log " Starting default emoji scan..." -Color Cyan
            $scanResults = Start-EmojiScan -ScanPath $scanPath
            
            if ($scanResults) {
                Write-Log " Scan completed successfully. Saving results..." -Color Green
                
                # Debug output path
                Write-Log " Debug: OutputPath value: '$OutputPath'" -Color Cyan
                Write-Log " Debug: OutputPath type: $($OutputPath.GetType().Name)" -Color Cyan
                Write-Log " Debug: OutputPath length: $($OutputPath.Length)" -Color Cyan
                
                # Ensure output directory exists
                $outputDir = Split-Path $OutputPath -Parent
                Write-Log " Debug: Output directory: '$outputDir'" -Color Cyan
                
                # Handle case where output path is just a filename (no directory)
                if ([string]::IsNullOrEmpty($outputDir)) {
                    Write-Log " Debug: Output path is just a filename, using current directory" -Color Cyan
                    $outputDir = (Get-Location).Path
                }
                
                if (!(Test-Path $outputDir)) {
                    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
                }
                
                # Save JSON report
                Write-Log " Debug: About to save to: '$OutputPath'" -Color Cyan
                $scanResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
                Write-Log " Results saved to: $OutputPath" -Color Green
                
                # Generate and save text report
                $txtReportPath = $OutputPath -replace '\.json$', '.txt'
                $txtReport = @"
AGENT EXO-SUIT V4.0 "PERFECTION" - EMOJI SCAN REPORT
====================================================

Scan Summary:
- Files Scanned: $($scanResults.Summary.TotalFilesScanned)
- Files with Emojis: $($scanResults.Summary.FilesWithEmojis)
- Total Emojis Found: $($scanResults.Summary.TotalEmojisFound)
- Scan Directory: $scanPath
- Processing Mode: $(if ($Parallel) { "Parallel" } else { "Sequential" })
- Max File Size: $MaxFileSizeMB MB
- Skip Binary: $SkipBinary
- Version: 4.0.0

"@
                
                if ($scanResults.Detections.Count -gt 0) {
                    $txtReport += "`nEMOJI DETECTIONS:`n"
                    $txtReport += "================`n`n"
                    
                    $groupedResults = $scanResults.Detections | Group-Object FilePath
                    foreach ($group in $groupedResults) {
                        $txtReport += "FILE: $($group.Name)`n"
                        $txtReport += "Emojis found: $($group.Count)`n"
                        $txtReport += "-" * 50 + "`n"
                        
                        foreach ($result in $group.Group) {
                            $txtReport += "Line $($result.LineNumber), Column $($result.ColumnNumber): $($result.Emoji)`n"
                            $txtReport += "Context: $($result.Context)`n"
                            $txtReport += "`n"
                        }
                        $txtReport += "`n"
                    }
                } else {
                    $txtReport += "`n NO EMOJIS FOUND! Codebase is clean and professional.`n"
                }
                
                $txtReport | Out-File -FilePath $txtReportPath -Encoding UTF8
                Write-Log " Text report saved to: $txtReportPath" -Color Green
                
                Write-Log " Default scan completed successfully!" -Color Green
            } else {
                Write-Log " Scan returned no results" -Color Yellow
            }
        }
        catch [System.Management.Automation.ParameterBindingException] {
            Write-Log " Parameter binding error in default scan: $_" -Color Red
            Write-Log " Attempting to continue with error recovery..." -Color Yellow
            
            # Try to run a minimal scan with error recovery
            try {
                Write-Log " Running minimal scan with error recovery..." -Color Cyan
                $minimalResults = @{
                    Summary = @{
                        ScanStartTime = Get-Date
                        ScanEndTime = Get-Date
                        DurationSeconds = 0
                        TotalFilesScanned = 0
                        FilesWithEmojis = 0
                        TotalEmojisFound = 0
                        ScanDirectory = $scanPath
                        ExcludedDirectories = @()
                        ScannedExtensions = @()
                        Version = "4.0.0"
                        ProcessingMode = "Error Recovery"
                        MaxFileSizeMB = $MaxFileSizeMB
                        SkipBinary = $SkipBinary
                        ErrorRecovery = $true
                        ErrorMessage = $_.Exception.Message
                    }
                    Detections = @()
                }
                
                # Save minimal results
                $minimalResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
                Write-Log " Minimal scan completed with error recovery" -Color Green
                return
            }
            catch {
                Write-Log " Error recovery failed: $_" -Color Red
                throw
            }
        }
    }
    
    Write-Log " V4.0 Emoji Sentinel completed successfully!" -Color Green
    
} catch [System.Management.Automation.ParameterBindingException] {
    if ($_.Exception.Message -like "*Cannot bind argument to parameter 'Path' because it is an empty string*") {
        Write-Log " Fatal error: Parameter binding error - empty path detected" -Color Red
        Write-Log " This usually indicates a file with an invalid or empty path" -Color Red
        Write-Log " Stack trace: $($_.ScriptStackTrace)" -Color Red
        exit 1
    }
    Write-Log " Fatal error: $_" -Color Red
    Write-Log " Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
} catch {
    Write-Log " Fatal error: $_" -Color Red
    Write-Log " Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
}

Write-Log " V4.0 Emoji Sentinel ready for production deployment!" -Color Green
