# VisionGap-Engine-V5.ps1
# Agent Exo-Suit V5.0 "Builder of Dreams" - Phase 1 Foundation
# Dream Analysis Engine: Parse markdown documentation and identify gaps

# 🚨 COMPREHENSIVE V5 CORE SYSTEM ARCHITECTURE - READ FIRST
# BEFORE PROCEEDING WITH ANY VISION GAP ANALYSIS OPERATIONS, READ THE COMPLETE V5 CORE SYSTEM ARCHITECTURE:
# - Primary Document: V5_CORE_SYSTEM_ARCHITECTURE.md - Complete safety & protection guide
# - Contains: Multi-layer defense, consensus systems, immune response, protection gates
# - Purpose: Bulletproof protection against system self-destruction
# - Requirement: 100% understanding before any action

param(
    [string]$ProjectPath = ".",
    [string]$OutputPath = "./vision_gap_reports",
    [switch]$Verbose,
    [switch]$GenerateReport
)

# =============================================================================
# VISION GAP ENGINE V5.0 - DREAM ANALYSIS ENGINE
# =============================================================================
# Purpose: Parse markdown documentation and identify gaps between vision and reality
# Component: Phase 1 Foundation - Dream Analysis Engine
# Status: Implementation Phase
# =============================================================================

# Import required modules
Import-Module Microsoft.PowerShell.Utility

# =============================================================================
# CONFIGURATION & SETUP
# =============================================================================

$ScriptVersion = "5.0.0"
$ScriptName = "VisionGap-Engine-V5"
$ScriptCodename = "Dream Analysis Engine"

# Create output directory if it doesn't exist
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    if ($Verbose) {
        Write-Host $logMessage
    }
    
    # Add to log file
    $logFile = Join-Path $OutputPath "vision_gap_engine.log"
    Add-Content -Path $logFile -Value $logMessage
}

function Initialize-Engine {
    Write-Log "Initializing VisionGap Engine V5.0 - Dream Analysis Engine" "INFO"
    Write-Log "Script Version: $ScriptVersion" "INFO"
    Write-Log "Script Codename: $ScriptCodename" "INFO"
    Write-Log "Project Path: $ProjectPath" "INFO"
    Write-Log "Output Path: $OutputPath" "INFO"
    
    # Check Python availability
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python detected: $pythonVersion" "INFO"
    }
    catch {
        Write-Log "Python not found - some features may be limited" "WARN"
    }
    
    # Check for required Python packages
    $requiredPackages = @("markdown", "nltk", "spacy", "transformers")
    foreach ($package in $requiredPackages) {
        try {
            $result = python -c "import $package; print('OK')" 2>&1
            if ($result -eq "OK") {
                Write-Log "Package $package available" "INFO"
            } else {
                Write-Log "Package $package not available" "WARN"
            }
        }
        catch {
            Write-Log "Package $package check failed" "WARN"
        }
    }
}

function Find-MarkdownFiles {
    param([string]$Path)
    
    Write-Log "Scanning for markdown files in: $Path" "INFO"
    
    try {
        $markdownFiles = Get-ChildItem -Path $Path -Recurse -Filter "*.md" | 
                        Where-Object { !$_.PSIsContainer } |
                        Select-Object FullName, Name, Length, LastWriteTime
        
        Write-Log "Found $($markdownFiles.Count) markdown files" "INFO"
        return $markdownFiles
    }
    catch {
        Write-Log "Error scanning for markdown files: $($_.Exception.Message)" "ERROR"
        return @()
    }
}

function Analyze-MarkdownContent {
    param([string]$FilePath)
    
    Write-Log "Analyzing markdown file: $FilePath" "INFO"
    
    try {
        $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
        $fileName = Split-Path $FilePath -Leaf
        
        # Basic markdown analysis
        $analysis = @{
            FileName = $fileName
            FilePath = $FilePath
            FileSize = (Get-Item $FilePath).Length
            LineCount = ($content -split "`n").Count
            WordCount = ($content -split "\s+" | Where-Object { $_ -match '\w' }).Count
            CharacterCount = $content.Length
            LastModified = (Get-Item $FilePath).LastWriteTime
        }
        
        # Header analysis
        $headers = [regex]::Matches($content, '^#{1,6}\s+(.+)$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        $analysis.HeaderCount = $headers.Count
        $analysis.Headers = $headers | ForEach-Object { $_.Groups[1].Value.Trim() }
        
        # Link analysis
        $links = [regex]::Matches($content, '\[([^\]]+)\]\(([^)]+)\)')
        $analysis.LinkCount = $links.Count
        $analysis.Links = $links | ForEach-Object { @{ Text = $_.Groups[1].Value; URL = $_.Groups[2].Value } }
        
        # Code block analysis
        $codeBlocks = [regex]::Matches($content, '```[\w]*\n(.*?)\n```', [System.Text.RegularExpressions.RegexOptions]::Singleline)
        $analysis.CodeBlockCount = $codeBlocks.Count
        
        # List analysis
        $lists = [regex]::Matches($content, '^[\s]*[-*+]\s+', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        $analysis.ListItemCount = $lists.Count
        
        # Image analysis
        $images = [regex]::Matches($content, '!\[([^\]]*)\]\(([^)]+)\)')
        $analysis.ImageCount = $images.Count
        
        return $analysis
    }
    catch {
        Write-Log "Error analyzing file $FilePath : $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Detect-Gaps {
    param([array]$Analyses)
    
    Write-Log "Detecting gaps between documentation and implementation" "INFO"
    
    $gaps = @()
    
    foreach ($analysis in $Analyses) {
        if ($null -eq $analysis) { continue }
        
        $fileGaps = @()
        
        # Check for missing content
        if ($analysis.WordCount -lt 100) {
            $fileGaps += @{
                Type = "Content Gap"
                Severity = "Medium"
                Description = "File has very little content ($($analysis.WordCount) words)"
                Recommendation = "Expand content with more detailed information"
            }
        }
        
        # Check for missing headers
        if ($analysis.HeaderCount -eq 0) {
            $fileGaps += @{
                Type = "Structure Gap"
                Severity = "High"
                Description = "File has no headers - poor structure"
                Recommendation = "Add proper markdown headers for better organization"
            }
        }
        
        # Check for broken links
        foreach ($link in $analysis.Links) {
            if ($link.URL -notmatch '^https?://' -and $link.URL -notmatch '^#') {
                # Internal link - check if file exists
                $internalPath = Join-Path (Split-Path $analysis.FilePath -Parent) $link.URL
                if (!(Test-Path $internalPath)) {
                    $fileGaps += @{
                        Type = "Link Gap"
                        Severity = "Medium"
                        Description = "Broken internal link: $($link.URL)"
                        Recommendation = "Fix or remove broken link"
                    }
                }
            }
        }
        
        # Check for missing code examples
        if ($analysis.CodeBlockCount -eq 0 -and $analysis.FileName -match '\.md$') {
            # This might be a technical document that should have code examples
            if ($analysis.FileName -match '(guide|tutorial|example|howto)', 'i') {
                $fileGaps += @{
                    Type = "Code Gap"
                    Severity = "Low"
                    Description = "Technical document lacks code examples"
                    Recommendation = "Add relevant code examples to improve clarity"
                }
            }
        }
        
        if ($fileGaps.Count -gt 0) {
            $gaps += @{
                FileName = $analysis.FileName
                FilePath = $analysis.FilePath
                Gaps = $fileGaps
                GapCount = $fileGaps.Count
            }
        }
    }
    
    Write-Log "Detected $($gaps.Count) files with gaps" "INFO"
    return $gaps
}

function Extract-Requirements {
    param([array]$Analyses)
    
    Write-Log "Extracting requirements from documentation" "INFO"
    
    $requirements = @()
    
    foreach ($analysis in $Analyses) {
        if ($null -eq $analysis) { continue }
        
        # Look for requirement patterns
        $content = Get-Content -Path $analysis.FilePath -Raw -Encoding UTF8
        
        # Find requirement statements
        $reqPatterns = @(
            'must\s+(?:be|have|support|include|provide)',
            'should\s+(?:be|have|support|include|provide)',
            'will\s+(?:be|have|support|include|provide)',
            'shall\s+(?:be|have|support|include|provide)',
            'requires?\s+(?:to|that)',
            'needs?\s+(?:to|that)',
            'expects?\s+(?:to|that)'
        )
        
        foreach ($pattern in $reqPatterns) {
            $matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            foreach ($match in $matches) {
                $context = $content.Substring([Math]::Max(0, $match.Index - 100), 
                                            [Math]::Min(200, $content.Length - $match.Index + 100))
                
                $requirements += @{
                    FileName = $analysis.FileName
                    FilePath = $analysis.FilePath
                    Pattern = $pattern
                    Match = $match.Value
                    Context = $context.Trim()
                    LineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
                }
            }
        }
    }
    
    Write-Log "Extracted $($requirements.Count) requirements" "INFO"
    return $requirements
}

function Generate-GapReport {
    param(
        [array]$Analyses,
        [array]$Gaps,
        [array]$Requirements
    )
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = Join-Path $OutputPath "vision_gap_report_$timestamp.md"
    
    Write-Log "Generating gap analysis report: $reportFile" "INFO"
    
    $report = @"
# Vision Gap Analysis Report - Agent Exo-Suit V5.0

**Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Engine**: VisionGap-Engine-V5.ps1  
**Version**: $ScriptVersion  
**Project Path**: $ProjectPath  

## Executive Summary

This report identifies gaps between project documentation and implementation, providing actionable insights for project completion and improvement.

### Key Metrics
- **Files Analyzed**: $($Analyses.Count)
- **Files with Gaps**: $($Gaps.Count)
- **Requirements Identified**: $($Requirements.Count)
- **Total Issues Found**: $(($Gaps | ForEach-Object { $_.GapCount } | Measure-Object -Sum).Sum)

## Detailed Analysis

### Files Analyzed
| File | Size | Words | Headers | Links | Code Blocks |
|------|------|-------|---------|-------|-------------|
"@

    foreach ($analysis in $Analyses) {
        if ($null -eq $analysis) { continue }
        $report += "`n| $($analysis.FileName) | $([math]::Round($analysis.FileSize/1KB, 1))KB | $($analysis.WordCount) | $($analysis.HeaderCount) | $($analysis.LinkCount) | $($analysis.CodeBlockCount) |"
    }
    
    $report += @"

### Gap Analysis

"@

    foreach ($gapFile in $Gaps) {
        $report += "`n#### $($gapFile.FileName)`n"
        $report += "**Path**: $($gapFile.FilePath)`n"
        $report += "**Gaps Found**: $($gapFile.GapCount)`n`n"
        
        foreach ($gap in $gapFile.Gaps) {
            $report += "- **$($gap.Type)** ($($gap.Severity)): $($gap.Description)`n"
            $report += "  - *Recommendation*: $($gap.Recommendation)`n`n"
        }
    }
    
    $report += @"

### Requirements Extraction

"@

    foreach ($req in $Requirements) {
        $report += "`n#### $($req.FileName) - Line $($req.LineNumber)`n"
        $report += "**Pattern**: $($req.Pattern)`n"
        $report += "**Match**: $($req.Match)`n"
        $report += "**Context**: $($req.Context)`n`n"
    }
    
    $report += @"

## Recommendations

### Immediate Actions
1. **Fix Critical Gaps**: Address all high-severity gaps first
2. **Validate Links**: Check and fix all broken internal links
3. **Improve Structure**: Add headers to files lacking structure
4. **Expand Content**: Add more detail to files with low word counts

### Long-term Improvements
1. **Requirement Tracking**: Implement systematic requirement tracking
2. **Documentation Standards**: Establish consistent documentation standards
3. **Regular Audits**: Schedule regular gap analysis reviews
4. **Automated Validation**: Implement automated documentation validation

## Next Steps

1. Review this report with project stakeholders
2. Prioritize gap resolution based on severity and impact
3. Assign resources to address identified gaps
4. Schedule follow-up gap analysis after improvements

---

*Report generated by VisionGap-Engine-V5.ps1 - Dream Analysis Engine*  
*Agent Exo-Suit V5.0 "Builder of Dreams" - Phase 1 Foundation*
"@

    try {
        Set-Content -Path $reportFile -Value $report -Encoding UTF8
        Write-Log "Report generated successfully: $reportFile" "INFO"
        return $reportFile
    }
    catch {
        Write-Log "Error generating report: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    Write-Log "Starting VisionGap Engine V5.0 - Dream Analysis Engine" "INFO"
    
    try {
        # Initialize engine
        Initialize-Engine
        
        # Find markdown files
        $markdownFiles = Find-MarkdownFiles -Path $ProjectPath
        if ($markdownFiles.Count -eq 0) {
            Write-Log "No markdown files found in project path" "WARN"
            return
        }
        
        # Analyze each file
        $analyses = @()
        foreach ($file in $markdownFiles) {
            $analysis = Analyze-MarkdownContent -FilePath $file.FullName
            if ($analysis) {
                $analyses += $analysis
            }
        }
        
        # Detect gaps
        $gaps = Detect-Gaps -Analyses $analyses
        
        # Extract requirements
        $requirements = Extract-Requirements -Analyses $analyses
        
        # Generate report if requested
        if ($GenerateReport) {
            $reportFile = Generate-GapReport -Analyses $analyses -Gaps $gaps -Requirements $requirements
            if ($reportFile) {
                Write-Log "Vision gap analysis complete. Report saved to: $reportFile" "INFO"
            }
        }
        
        # Summary output
        Write-Log "Vision Gap Analysis Complete" "INFO"
        Write-Log "Files Analyzed: $($analyses.Count)" "INFO"
        Write-Log "Files with Gaps: $($gaps.Count)" "INFO"
        Write-Log "Requirements Found: $($requirements.Count)" "INFO"
        
        # Return results for further processing
        return @{
            Analyses = $analyses
            Gaps = $gaps
            Requirements = $requirements
            Summary = @{
                FilesAnalyzed = $analyses.Count
                FilesWithGaps = $gaps.Count
                RequirementsFound = $requirements.Count
                TotalIssues = ($gaps | ForEach-Object { $_.GapCount } | Measure-Object -Sum).Sum
            }
        }
    }
    catch {
        Write-Log "Critical error in main execution: $($_.Exception.Message)" "ERROR"
        Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
        return $null
    }
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

if ($MyInvocation.InvocationName -ne ".") {
    # Script was called directly
    $results = Main
    
    if ($results) {
        Write-Host "`nVision Gap Analysis Complete!" -ForegroundColor Green
        Write-Host "Files Analyzed: $($results.Summary.FilesAnalyzed)" -ForegroundColor Cyan
        Write-Host "Files with Gaps: $($results.Summary.FilesWithGaps)" -ForegroundColor Yellow
        Write-Host "Requirements Found: $($results.Summary.RequirementsFound)" -ForegroundColor Cyan
        Write-Host "Total Issues: $($results.Summary.TotalIssues)" -ForegroundColor Red
        
        if ($GenerateReport) {
            Write-Host "`nReport generated in: $OutputPath" -ForegroundColor Green
        }
    } else {
        Write-Host "Vision Gap Analysis failed!" -ForegroundColor Red
        exit 1
    }
} else {
    # Script was dot-sourced
    Write-Log "VisionGap-Engine-V5.ps1 loaded as module" "INFO"
}
