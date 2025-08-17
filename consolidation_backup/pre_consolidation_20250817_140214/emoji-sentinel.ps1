# Agent Exo-Suit V3.0 - Emoji Sentinel
# Comprehensive emoji detection and logging system

param(
    [switch]$Scan,
    [switch]$Purge,
    [switch]$Report,
    [switch]$Verbose,
    [string]$Path,
    [string]$OutputPath = ".\restore\EMOJI_REPORT.json"
)

# Import required modules
Import-Module Microsoft.PowerShell.Utility -Force
Import-Module Microsoft.PowerShell.Management -Force

# Configuration
$env:EMOJI_SCAN_DIR = if ($Path) { $Path } else { if (Get-Location) { (Get-Location).Path } else { $PWD.Path } }
$env:EMOJI_CACHE_DIR = "C:\scratch\exo-suit\emoji-scan"

# Emoji detection patterns (simplified but comprehensive)
$emojiPatterns = @(
    # Common emoji ranges - using PowerShell-compatible syntax
    '[\u{1F600}-\u{1F64F}]',      # Emoticons
    '[\u{1F300}-\u{1F5FF}]',      # Misc Symbols and Pictographs
    '[\u{1F680}-\u{1F6FF}]',      # Transport and Map
    '[\u{1F1E0}-\u{1F1FF}]',      # Regional Indicator
    '[\u{2600}-\u{26FF}]',        # Misc Symbols
    '[\u{2700}-\u{27BF}]',        # Dingbats
    '[\u{1F900}-\u{1F9FF}]',      # Supplemental Symbols and Pictographs
    '[\u{1F018}-\u{1F270}]',      # Playing Cards
    '[\u{1F000}-\u{1F02F}]',      # Mahjong Tiles
    '[\u{1F0A0}-\u{1F0FF}]',      # Playing Cards
    '[\u{1F100}-\u{1F64F}]',      # Enclosed Alphanumeric Supplement
    '[\u{1F650}-\u{1F67F}]',      # Ornamental Dingbats
    '[\u{1F680}-\u{1F6FF}]',      # Transport and Map Symbols
    '[\u{1F700}-\u{1F77F}]',      # Alchemical Symbols
    '[\u{1F780}-\u{1F7FF}]',      # Geometric Shapes
    '[\u{1F800}-\u{1F8FF}]',      # Supplemental Arrows-C
    '[\u{1F900}-\u{1F9FF}]',      # Supplemental Symbols and Pictographs
    '[\u{1FA00}-\u{1FA6F}]',      # Chess Symbols
    '[\u{1FA70}-\u{1FAFF}]',      # Symbols and Pictographs Extended-A
    '[\u{1FAB0}-\u{1FAFF}]',      # Symbols and Pictographs Extended-B
    '[\u{1FAC0}-\u{1FAFF}]',      # Symbols and Pictographs Extended-C
    '[\u{1FAD0}-\u{1FAFF}]',      # Symbols and Pictographs Extended-D
    '[\u{1FAE0}-\u{1FAFF}]',      # Symbols and Pictographs Extended-E
    '[\u{1FAF0}-\u{1FAFF}]',      # Symbols and Pictographs Extended-F
    '[\u{1FB00}-\u{1FBFF}]',      # Legacy Computing
    '[\u{1FC00}-\u{1FCFF}]',      # Legacy Computing
    '[\u{1FD00}-\u{1FDFF}]',      # Legacy Computing
    '[\u{1FE00}-\u{1FEFF}]',      # Legacy Computing
    '[\u{1FF00}-\u{1FFFF}]',      # Legacy Computing
    '[\u{20000}-\u{2A6DF}]',      # CJK Unified Ideographs Extension B
    '[\u{2A700}-\u{2B73F}]',      # CJK Unified Ideographs Extension C
    '[\u{2B740}-\u{2B81F}]',      # CJK Unified Ideographs Extension D
    '[\u{2B820}-\u{2CEAF}]',      # CJK Unified Ideographs Extension E
    '[\u{2CEB0}-\u{2EBEF}]',      # CJK Unified Ideographs Extension F
    '[\u{2F800}-\u{2FA1F}]',      # CJK Compatibility Ideographs Supplement
    '[\u{30000}-\u{3134F}]',      # CJK Unified Ideographs Extension G
    '[\u{31350}-\u{323AF}]',      # CJK Unified Ideographs Extension H
    '[\u{E000}-\u{F8FF}]',        # Private Use Area
    '[\u{F0000}-\u{FFFFF}]',      # Private Use Area
    '[\u{100000}-\u{10FFFF}]'     # Private Use Area
)

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
    'restore', 'context', 'gpu_rag_env', 'mermaid'
)

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
}

function Initialize-EmojiSentinel {
    """Initialize the emoji detection system"""
    Write-Host "Agent Exo-Suit V3.0 - Emoji Sentinel Initializing..." -ForegroundColor Cyan
    
    # Validate scan directory
    if ([string]::IsNullOrEmpty($env:EMOJI_SCAN_DIR)) {
        $env:EMOJI_SCAN_DIR = $PWD.Path
        Write-Host "Using current directory as scan directory: $env:EMOJI_SCAN_DIR" -ForegroundColor Yellow
    } else {
        Write-Host "Using specified scan directory: $env:EMOJI_SCAN_DIR" -ForegroundColor Green
    }
    
    # Create cache directory
    if (!(Test-Path $env:EMOJI_CACHE_DIR)) {
        try {
            New-Item -ItemType Directory -Path $env:EMOJI_CACHE_DIR -Force | Out-Null
            Write-Host "Created emoji scan cache directory: $env:EMOJI_CACHE_DIR" -ForegroundColor Green
        } catch {
            Write-Warning "Failed to create cache directory: $_"
            $env:EMOJI_CACHE_DIR = ".\emoji-cache"
            New-Item -ItemType Directory -Path $env:EMOJI_CACHE_DIR -Force | Out-Null
            Write-Host "Using fallback cache directory: $env:EMOJI_CACHE_DIR" -ForegroundColor Yellow
        }
    }
    
    # Test emoji detection capability with comprehensive approach
    $testString = "Test string with emoji "
    $hasEmoji = Test-EmojiInString $testString
    
    if ($hasEmoji) {
        Write-Host "Emoji detection capability validated" -ForegroundColor Green
    } else {
        Write-Warning "Emoji detection may need adjustment"
    }
    
    Write-Host "Emoji Sentinel ready for deployment" -ForegroundColor Green
}

function Test-EmojiInString {
    param([string]$Text)
    """Test if a string contains any emojis using comprehensive Unicode ranges"""
    
    # Check for emojis in various Unicode ranges
    foreach ($char in $Text.ToCharArray()) {
        $codePoint = [int][char]$char
        
        # Check if character is in emoji ranges
        if ($codePoint -ge 0x1F600 -and $codePoint -le 0x1F64F) { return $true }  # Emoticons
        if ($codePoint -ge 0x1F300 -and $codePoint -le 0x1F5FF) { return $true }  # Misc Symbols and Pictographs
        if ($codePoint -ge 0x1F680 -and $codePoint -le 0x1F6FF) { return $true }  # Transport and Map
        if ($codePoint -ge 0x1F1E0 -and $codePoint -le 0x1F1FF) { return $true }  # Regional Indicator
        if ($codePoint -ge 0x2600 -and $codePoint -le 0x26FF) { return $true }    # Misc Symbols
        if ($codePoint -ge 0x2700 -and $codePoint -le 0x27BF) { return $true }    # Dingbats
        if ($codePoint -ge 0x1F900 -and $codePoint -le 0x1F9FF) { return $true }  # Supplemental Symbols and Pictographs
        if ($codePoint -ge 0x1F018 -and $codePoint -le 0x1F270) { return $true }  # Playing Cards
        if ($codePoint -ge 0x1F000 -and $codePoint -le 0x1F02F) { return $true }  # Mahjong Tiles
        if ($codePoint -ge 0x1F0A0 -and $codePoint -le 0x1F0FF) { return $true }  # Playing Cards
        if ($codePoint -ge 0x1F100 -and $codePoint -le 0x1F64F) { return $true }  # Enclosed Alphanumeric Supplement
        if ($codePoint -ge 0x1F650 -and $codePoint -le 0x1F67F) { return $true }  # Ornamental Dingbats
        if ($codePoint -ge 0x1F700 -and $codePoint -le 0x1F77F) { return $true }  # Alchemical Symbols
        if ($codePoint -ge 0x1F780 -and $codePoint -le 0x1F7FF) { return $true }  # Geometric Shapes
        if ($codePoint -ge 0x1F800 -and $codePoint -le 0x1F8FF) { return $true }  # Supplemental Arrows-C
        if ($codePoint -ge 0x1FA00 -and $codePoint -le 0x1FA6F) { return $true }  # Chess Symbols
        if ($codePoint -ge 0x1FAB0 -and $codePoint -le 0x1FAFF) { return $true }  # Symbols and Pictographs Extended
        if ($codePoint -ge 0x1FB00 -and $codePoint -le 0x1FBFF) { return $true }  # Legacy Computing
        if ($codePoint -ge 0x1FC00 -and $codePoint -le 0x1FCFF) { return $true }  # Legacy Computing
        if ($codePoint -ge 0x1FD00 -and $codePoint -le 0x1FDFF) { return $true }  # Legacy Computing
        if ($codePoint -ge 0x1FE00 -and $codePoint -le 0x1FEFF) { return $true }  # Legacy Computing
        if ($codePoint -ge 0x1FF00 -and $codePoint -le 0x1FFFF) { return $true }  # Legacy Computing
        if ($codePoint -ge 0x20000 -and $codePoint -le 0x2A6DF) { return $true }  # CJK Unified Ideographs Extension B
        if ($codePoint -ge 0x2A700 -and $codePoint -le 0x2B73F) { return $true }  # CJK Unified Ideographs Extension C
        if ($codePoint -ge 0x2B740 -and $codePoint -le 0x2B81F) { return $true }  # CJK Unified Ideographs Extension D
        if ($codePoint -ge 0x2B820 -and $codePoint -le 0x2CEAF) { return $true }  # CJK Unified Ideographs Extension E
        if ($codePoint -ge 0x2CEB0 -and $codePoint -le 0x2EBEF) { return $true }  # CJK Unified Ideographs Extension F
        if ($codePoint -ge 0x2F800 -and $codePoint -le 0x2FA1F) { return $true }  # CJK Compatibility Ideographs Supplement
        if ($codePoint -ge 0x30000 -and $codePoint -le 0x3134F) { return $true }  # CJK Unified Ideographs Extension G
        if ($codePoint -ge 0x31350 -and $codePoint -le 0x323AF) { return $true }  # CJK Unified Ideographs Extension H
        if ($codePoint -ge 0xE000 -and $codePoint -le 0xF8FF) { return $true }     # Private Use Area
        if ($codePoint -ge 0xF0000 -and $codePoint -le 0xFFFFF) { return $true }   # Private Use Area
        if ($codePoint -ge 0x100000 -and $codePoint -le 0x10FFFF) { return $true } # Private Use Area
        if ($codePoint -gt 0xFFFF) { return $true }  # Any other high Unicode characters
    }
    return $false
}

function Get-EmojisInString {
    param([string]$Text)
    """Extract all emojis from a string with their positions using comprehensive Unicode ranges"""
    
    $emojis = @()
    
    for ($i = 0; $i -lt $Text.Length; $i++) {
        $char = $Text[$i]
        $codePoint = [int][char]$char
        
        # Check if character is in emoji ranges
        $isEmoji = $false
        
        if ($codePoint -ge 0x1F600 -and $codePoint -le 0x1F64F) { $isEmoji = $true }  # Emoticons
        elseif ($codePoint -ge 0x1F300 -and $codePoint -le 0x1F5FF) { $isEmoji = $true }  # Misc Symbols and Pictographs
        elseif ($codePoint -ge 0x1F680 -and $codePoint -le 0x1F6FF) { $isEmoji = $true }  # Transport and Map
        elseif ($codePoint -ge 0x1F1E0 -and $codePoint -le 0x1F1FF) { $isEmoji = $true }  # Regional Indicator
        elseif ($codePoint -ge 0x2600 -and $codePoint -le 0x26FF) { $isEmoji = $true }    # Misc Symbols
        elseif ($codePoint -ge 0x2700 -and $codePoint -le 0x27BF) { $isEmoji = $true }    # Dingbats
        elseif ($codePoint -ge 0x1F900 -and $codePoint -le 0x1F9FF) { $isEmoji = $true }  # Supplemental Symbols and Pictographs
        elseif ($codePoint -ge 0x1F018 -and $codePoint -le 0x1F270) { $isEmoji = $true }  # Playing Cards
        elseif ($codePoint -ge 0x1F000 -and $codePoint -le 0x1F02F) { $isEmoji = $true }  # Mahjong Tiles
        elseif ($codePoint -ge 0x1F0A0 -and $codePoint -le 0x1F0FF) { $isEmoji = $true }  # Playing Cards
        elseif ($codePoint -ge 0x1F100 -and $codePoint -le 0x1F64F) { $isEmoji = $true }  # Enclosed Alphanumeric Supplement
        elseif ($codePoint -ge 0x1F650 -and $codePoint -le 0x1F67F) { $isEmoji = $true }  # Ornamental Dingbats
        elseif ($codePoint -ge 0x1F700 -and $codePoint -le 0x1F77F) { $isEmoji = $true }  # Alchemical Symbols
        elseif ($codePoint -ge 0x1F780 -and $codePoint -le 0x1F7FF) { $isEmoji = $true }  # Geometric Shapes
        elseif ($codePoint -ge 0x1F800 -and $codePoint -le 0x1F8FF) { $isEmoji = $true }  # Supplemental Arrows-C
        elseif ($codePoint -ge 0x1FA00 -and $codePoint -le 0x1FA6F) { $isEmoji = $true }  # Chess Symbols
        elseif ($codePoint -ge 0x1FAB0 -and $codePoint -le 0x1FAFF) { $isEmoji = $true }  # Symbols and Pictographs Extended
        elseif ($codePoint -ge 0x1FB00 -and $codePoint -le 0x1FBFF) { $isEmoji = $true }  # Legacy Computing
        elseif ($codePoint -ge 0x1FC00 -and $codePoint -le 0x1FCFF) { $isEmoji = $true }  # Legacy Computing
        elseif ($codePoint -ge 0x1FD00 -and $codePoint -le 0x1FDFF) { $isEmoji = $true }  # Legacy Computing
        elseif ($codePoint -ge 0x1FE00 -and $codePoint -le 0x1FEFF) { $isEmoji = $true }  # Legacy Computing
        elseif ($codePoint -ge 0x1FF00 -and $codePoint -le 0x1FFFF) { $isEmoji = $true }  # Legacy Computing
        elseif ($codePoint -ge 0x20000 -and $codePoint -le 0x2A6DF) { $isEmoji = $true }  # CJK Unified Ideographs Extension B
        elseif ($codePoint -ge 0x2A700 -and $codePoint -le 0x2B73F) { $isEmoji = $true }  # CJK Unified Ideographs Extension C
        elseif ($codePoint -ge 0x2B740 -and $codePoint -le 0x2B81F) { $isEmoji = $true }  # CJK Unified Ideographs Extension D
        elseif ($codePoint -ge 0x2B820 -and $codePoint -le 0x2CEAF) { $isEmoji = $true }  # CJK Unified Ideographs Extension E
        elseif ($codePoint -ge 0x2CEB0 -and $codePoint -le 0x2EBEF) { $isEmoji = $true }  # CJK Unified Ideographs Extension F
        elseif ($codePoint -ge 0x2F800 -and $codePoint -le 0x2FA1F) { $isEmoji = $true }  # CJK Unified Ideographs Supplement
        elseif ($codePoint -ge 0x30000 -and $codePoint -le 0x3134F) { $isEmoji = $true }  # CJK Unified Ideographs Extension G
        elseif ($codePoint -ge 0x31350 -and $codePoint -le 0x323AF) { $isEmoji = $true }  # CJK Unified Ideographs Extension H
        elseif ($codePoint -ge 0xE000 -and $codePoint -le 0xF8FF) { $isEmoji = $true }     # Private Use Area
        elseif ($codePoint -ge 0xF0000 -and $codePoint -le 0xFFFFF) { $isEmoji = $true }   # Private Use Area
        elseif ($codePoint -ge 0x100000 -and $codePoint -le 0x10FFFF) { $isEmoji = $true } # Private Use Area
        elseif ($codePoint -gt 0xFFFF) { $isEmoji = $true }  # Any other high Unicode characters
        
        if ($isEmoji) {
            $emojiObj = [PSCustomObject]@{
                Emoji = $char
                Index = $i
                Length = 1
            }
            $emojis += $emojiObj
        }
    }
    
    return $emojis
}

function Scan-FileForEmojis {
    param(
        [string]$FilePath,
        [switch]$Verbose
    )
    """Scan a single file for emojis"""
    
    $results = @()
    
    try {
        if (!(Test-Path $FilePath)) {
            return $results
        }
        
        # Check file size
        $fileSize = (Get-Item $FilePath).Length
        if ($fileSize -gt 50MB) {
            if ($Verbose) {
                Write-Host "Skipping large file: $FilePath ($([math]::Round($fileSize / 1MB, 1)) MB)" -ForegroundColor Yellow
            }
            return $results
        }
        
        # Read file content
        $content = Get-Content $FilePath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($null -eq $content) {
            return $results
        }
        
        # Split into lines
        $lines = $content -split "`n"
        
        for ($lineNum = 0; $lineNum -lt $lines.Count; $lineNum++) {
            $line = $lines[$lineNum]
            $lineNumber = $lineNum + 1
            
            if (Test-EmojiInString $line) {
                if ($Verbose) {
                    Write-Host "  Found emoji in line $lineNumber - '$line'" -ForegroundColor Yellow
                }
                
                $emojis = Get-EmojisInString $line
                
                if ($Verbose) {
                    Write-Host "  Extracted emojis: $($emojis.Count)" -ForegroundColor Yellow
                }
                
                                foreach ($emoji in $emojis) {
                    if ($emoji -and $emoji.Emoji) {
                        if ($Verbose) {
                            Write-Host "    Processing emoji: '$($emoji.Emoji)' at index $($emoji.Index)" -ForegroundColor Cyan
                        }
                        
                        $context = ""
                        $start = [math]::Max(0, $emoji.Index - 20)
                        $end = [math]::Min($line.Length, $emoji.Index + $emoji.Length + 20)
                        $context = $line.Substring($start, $end - $start)
                        
                        $result = [EmojiDetectionResult]::new()
                        $result.FilePath = $FilePath
                        $result.LineNumber = $lineNumber
                        $result.ColumnNumber = $emoji.Index + 1
                        $result.Emoji = $emoji.Emoji
                        $result.Context = $context
                        $result.LineContent = $line
                        $result.FileExtension = [System.IO.Path]::GetExtension($FilePath)
                        $result.DetectionTime = Get-Date
                        $result.Severity = "HIGH"
                        
                        if ($Verbose) {
                            Write-Host "    Created result object: $($result.FilePath):$($result.LineNumber):$($result.ColumnNumber)" -ForegroundColor Green
                        }
                        
                        $results += $result
                    } else {
                        if ($Verbose) {
                            Write-Host "    Skipping invalid emoji object: $($emoji | ConvertTo-Json -Compress)" -ForegroundColor Red
                        }
                    }
                }
        }
    }
        
    } catch {
        if ($Verbose) {
            Write-Warning "Error scanning file $FilePath : $_"
        }
    }
    
    return $results
}

function Start-EmojiScan {
    """Start comprehensive emoji scan of the codebase"""
    
    Write-Host "Starting comprehensive emoji scan..." -ForegroundColor Cyan
    Write-Host "Scan directory: $env:EMOJI_SCAN_DIR" -ForegroundColor Yellow
    
    $startTime = Get-Date
    $allResults = @()
    $scannedFiles = 0
    $filesWithEmojis = 0
    
    # Get all files to scan
    $allFiles = Get-ChildItem -Path $env:EMOJI_SCAN_DIR -Recurse -File | Where-Object {
        $ext = $_.Extension.ToLower()
        $dir = $_.DirectoryName
        
        # Check if file extension should be scanned
        $shouldScan = $scanExtensions -contains $ext
        
        # Check if directory should be excluded
        $excluded = $false
        foreach ($excludeDir in $excludeDirs) {
            if ($dir -like "*\$excludeDir*") {
                $excluded = $true
                break
            }
        }
        
        return $shouldScan -and -not $excluded
    }
    
    Write-Host "Found $($allFiles.Count) files to scan" -ForegroundColor Cyan
    
    # Scan each file
    foreach ($file in $allFiles) {
        $scannedFiles++
        
        if ($scannedFiles % 100 -eq 0) {
            $progress = [math]::Round(($scannedFiles / $allFiles.Count) * 100, 1)
            Write-Progress -Activity "Emoji Scan Progress" -Status "$scannedFiles / $($allFiles.Count) files" -PercentComplete $progress
        }
        
        $results = Scan-FileForEmojis -FilePath $file.FullName -Verbose:$Verbose
        
        if ($results.Count -gt 0) {
            $filesWithEmojis++
            $allResults += $results
            
            if ($Verbose) {
                Write-Host "Found $($results.Count) emojis in: $($file.Name)" -ForegroundColor Red
            }
        }
    }
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Generate scan summary
    $scanSummary = @{
        ScanStartTime = $startTime
        ScanEndTime = $endTime
        DurationSeconds = $duration
        TotalFilesScanned = $scannedFiles
        FilesWithEmojis = $filesWithEmojis
        TotalEmojisFound = $allResults.Count
        ScanDirectory = $env:EMOJI_SCAN_DIR
        ExcludedDirectories = $excludeDirs
        ScannedExtensions = $scanExtensions
    }
    
    # Save results
    $resultsData = @{
        Summary = $scanSummary
        Detections = if ($allResults -and $allResults.Count -gt 0) {
            $allResults | ForEach-Object {
                if ($_ -and $_.FilePath) {
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
                    }
                }
            } | Where-Object { $_ -ne $null }
        } else {
            @()
        }
    }
    
    # Ensure output directory exists
    $outputDir = Split-Path $OutputPath -Parent
    if (!(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Save JSON report
    $resultsData | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
    
    # Save human-readable report
    $txtReportPath = $OutputPath -replace '\.json$', '.txt'
    $txtReport = @"
AGENT EXO-SUIT V3.0 - EMOJI SCAN REPORT
========================================

Scan Summary:
- Start Time: $($startTime.ToString("yyyy-MM-dd HH:mm:ss"))
- End Time: $($endTime.ToString("yyyy-MM-dd HH:mm:ss"))
- Duration: $duration seconds
- Files Scanned: $scannedFiles
- Files with Emojis: $filesWithEmojis
- Total Emojis Found: $($allResults.Count)
- Scan Directory: $env:EMOJI_SCAN_DIR

"@
    
    if ($allResults.Count -gt 0) {
        $txtReport += "`nEMOJI DETECTIONS:`n"
        $txtReport += "================`n`n"
        
        $groupedResults = $allResults | Group-Object FilePath
        
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
        $txtReport += "`nNO EMOJIS FOUND! Codebase is clean.`n"
    }
    
    $txtReport | Out-File -FilePath $txtReportPath -Encoding UTF8
    
    # Display results
    Write-Host "`nEmoji Scan Complete!" -ForegroundColor Green
    Write-Host "Duration: $duration seconds" -ForegroundColor Cyan
    Write-Host "Files scanned: $scannedFiles" -ForegroundColor Cyan
    Write-Host "Files with emojis: $filesWithEmojis" -ForegroundColor $(if ($filesWithEmojis -gt 0) { "Red" } else { "Green" })
    Write-Host "Total emojis found: $($allResults.Count)" -ForegroundColor $(if ($allResults.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "Report saved to: $OutputPath" -ForegroundColor Yellow
    Write-Host "Text report: $txtReportPath" -ForegroundColor Yellow
    
    return $resultsData
}

function Start-EmojiPurge {
    """Purge all detected emojis from the codebase"""
    
    Write-Host "Starting emoji purge operation..." -ForegroundColor Red
    Write-Host "WARNING: This will modify files in place!" -ForegroundColor Red
    
    $confirm = Read-Host "Are you sure you want to continue? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Emoji purge cancelled" -ForegroundColor Yellow
        return
    }
    
    # Load previous scan results
    if (!(Test-Path $OutputPath)) {
        Write-Host "No scan results found. Please run a scan first." -ForegroundColor Red
        return
    }
    
    $scanResults = Get-Content $OutputPath | ConvertFrom-Json
    
    if ($scanResults.Detections.Count -eq 0) {
        Write-Host "No emojis to purge!" -ForegroundColor Green
        return
    }
    
    $purgedCount = 0
    $modifiedFiles = @()
    
    # Group by file for efficient processing
    $groupedResults = $scanResults.Detections | Group-Object FilePath
    
    foreach ($group in $groupedResults) {
        $filePath = $group.Name
        $detections = $group.Group | Sort-Object LineNumber -Descending
        
        Write-Host "Processing: $filePath" -ForegroundColor Cyan
        
        try {
            # Read file content
            $content = Get-Content $filePath -Raw -Encoding UTF8
            $lines = $content -split "`n"
            $modified = $false
            
            # Process detections in reverse order to maintain line numbers
            foreach ($detection in $detections) {
                $lineIndex = $detection.LineNumber - 1
                if ($lineIndex -lt $lines.Count) {
                    $originalLine = $lines[$lineIndex]
                    $newLine = $originalLine -replace $detection.Emoji, ''
                    
                    if ($newLine -ne $originalLine) {
                        $lines[$lineIndex] = $newLine
                        $modified = $true
                        $purgedCount++
                        
                        if ($Verbose) {
                            Write-Host "  Line $($detection.LineNumber): Removed '$($detection.Emoji)'" -ForegroundColor Yellow
                        }
                    }
                }
            }
            
            # Write back to file if modified
            if ($modified) {
                $newContent = $lines -join "`n"
                Set-Content -Path $filePath -Value $newContent -Encoding UTF8 -NoNewline
                $modifiedFiles += $filePath
                Write-Host "  Modified: $filePath" -ForegroundColor Green
            }
            
        } catch {
            Write-Warning "Error processing file $filePath : $_"
        }
    }
    
    Write-Host "`nEmoji Purge Complete!" -ForegroundColor Green
    Write-Host "Emojis purged: $purgedCount" -ForegroundColor Green
    Write-Host "Files modified: $($modifiedFiles.Count)" -ForegroundColor Green
    
    if ($modifiedFiles.Count -gt 0) {
        Write-Host "Modified files:" -ForegroundColor Yellow
        foreach ($file in $modifiedFiles) {
            Write-Host "  $file" -ForegroundColor Yellow
        }
    }
}

function Show-EmojiReport {
    """Display emoji scan report"""
    
    if (!(Test-Path $OutputPath)) {
        Write-Host "No scan results found. Please run a scan first." -ForegroundColor Red
        return
    }
    
    $scanResults = Get-Content $OutputPath | ConvertFrom-Json
    
    Write-Host "`nAGENT EXO-SUIT V3.0 - EMOJI SCAN REPORT" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    $summary = $scanResults.Summary
    Write-Host "Scan Summary:" -ForegroundColor Yellow
    Write-Host "  Start Time: $($summary.ScanStartTime)" -ForegroundColor White
    Write-Host "  Duration: $($summary.DurationSeconds) seconds" -ForegroundColor White
    Write-Host "  Files Scanned: $($summary.TotalFilesScanned)" -ForegroundColor White
    Write-Host "  Files with Emojis: $($summary.FilesWithEmojis)" -ForegroundColor White
    Write-Host "  Total Emojis: $($summary.TotalEmojisFound)" -ForegroundColor White
    
    if ($scanResults.Detections.Count -gt 0) {
        Write-Host "`nEmoji Detections:" -ForegroundColor Red
        Write-Host "-" * 30 -ForegroundColor Red
        
        $groupedResults = $scanResults.Detections | Group-Object FilePath
        
        foreach ($group in $groupedResults) {
            Write-Host "`nFile: $($group.Name)" -ForegroundColor Yellow
            Write-Host "Emojis: $($group.Count)" -ForegroundColor Red
            
            foreach ($detection in $group.Group) {
                Write-Host "  Line $($detection.LineNumber): $($detection.Emoji) - $($detection.Context)" -ForegroundColor White
            }
        }
    } else {
        Write-Host "`nNO EMOJIS FOUND! Codebase is clean." -ForegroundColor Green
    }
}

# Main execution
try {
    # Ensure we have a valid working directory
    if ([string]::IsNullOrEmpty($PWD.Path)) {
        Set-Location (Split-Path $PSCommandPath -Parent)
        Write-Host "Set working directory to script location: $PWD.Path" -ForegroundColor Yellow
    }
    
    Initialize-EmojiSentinel
    
    if ($Scan) {
        Start-EmojiScan
    } elseif ($Purge) {
        Start-EmojiPurge
    } elseif ($Report) {
        Show-EmojiReport
    } else {
        # Default: run scan
        Start-EmojiScan
    }
    
} catch {
    Write-Error "Emoji Sentinel error: $_"
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
