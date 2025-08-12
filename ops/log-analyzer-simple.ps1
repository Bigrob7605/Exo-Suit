# Agent Exo-Suit V5.0 "Builder of Dreams" - Simple Log Analyzer
# Purpose: Handle massive log files by parsing in chunks and providing intelligent summaries
# Version: 5.0.0
# Date: August 12, 2025

param(
    [Parameter(Mandatory=$true)]
    [string]$LogPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "log_analysis_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json",
    
    [Parameter(Mandatory=$false)]
    [int]$ChunkSize = 1000
)

# Initialize logging
$LogStartTime = Get-Date
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Agent Exo-Suit V5.0 'Builder of Dreams' - Simple Log Analyzer Starting..." -ForegroundColor Green

# Validate file exists
if (-not (Test-Path $LogPath)) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [ERROR] Log file not found: $LogPath" -ForegroundColor Red
    exit 1
}

# Get file information
$FileInfo = Get-Item $LogPath
$FileSizeMB = [math]::Round($FileInfo.Length / 1MB, 2)
$FileSizeGB = [math]::Round($FileInfo.Length / 1GB, 2)

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Analyzing log file: $($FileInfo.Name)" -ForegroundColor Cyan
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] File size: $FileSizeMB MB ($FileSizeGB GB)" -ForegroundColor Cyan

# Initialize analysis results
$AnalysisResults = @{
    FileInfo = @{
        Name = $FileInfo.Name
        SizeBytes = $FileInfo.Length
        SizeMB = $FileSizeMB
        SizeGB = $FileSizeGB
        LastModified = $FileInfo.LastWriteTime
        CreationTime = $FileInfo.CreationTime
    }
    Analysis = @{
        StartTime = $LogStartTime
        ChunkSize = $ChunkSize
        ProcessingMode = "Chunked Analysis"
    }
    Summary = @{
        TotalLines = 0
        ProcessedChunks = 0
        ProcessingTime = 0
        ErrorCount = 0
        WarningCount = 0
        InfoCount = 0
        CriticalIssues = @()
        KeyMetrics = @{}
        Recommendations = @()
    }
    DetailedAnalysis = @{}
}

# Function to analyze log chunk
function Analyze-LogChunk {
    param([string[]]$Lines, [int]$ChunkNumber)
    
    $ChunkResults = @{
        ChunkNumber = $ChunkNumber
        LineCount = $Lines.Count
        ErrorLines = @()
        WarningLines = @()
        InfoLines = @()
        CriticalIssues = @()
        Metrics = @{}
    }
    
    foreach ($Line in $Lines) {
        $AnalysisResults.Summary.TotalLines++
        
        # Analyze line content
        if ($Line -match "ERROR|CRITICAL|FAILED|EXCEPTION") {
            $ChunkResults.ErrorLines += $Line
            $AnalysisResults.Summary.ErrorCount++
            
            # Check for critical issues
            if ($Line -match "CRITICAL|FATAL|SEVERE") {
                $ChunkResults.CriticalIssues += $Line
                $AnalysisResults.Summary.CriticalIssues += $Line
            }
        }
        elseif ($Line -match "WARNING|WARN") {
            $ChunkResults.WarningLines += $Line
            $AnalysisResults.Summary.WarningCount++
        }
        elseif ($Line -match "INFO|SUCCESS|PASSED") {
            $ChunkResults.InfoLines += $Line
            $AnalysisResults.Summary.InfoCount++
        }
        
        # Extract key metrics
        if ($Line -match "(\d+)\s*files") {
            $FileCount = [int]($Matches[1])
            if (-not $ChunkResults.Metrics.ContainsKey("FileCount")) {
                $ChunkResults.Metrics["FileCount"] = @()
            }
            $ChunkResults.Metrics["FileCount"] += $FileCount
        }
        
        if ($Line -match "(\d+)\s*emojis") {
            $EmojiCount = [int]($Matches[1])
            if (-not $ChunkResults.Metrics.ContainsKey("EmojiCount")) {
                $ChunkResults.Metrics["EmojiCount"] = @()
            }
            $ChunkResults.Metrics["EmojiCount"] += $EmojiCount
        }
        
        if ($Line -match "(\d+\.\d+)\s*seconds") {
            $Duration = [double]($Matches[1])
            if (-not $ChunkResults.Metrics.ContainsKey("Duration")) {
                $ChunkResults.Metrics["Duration"] = @()
            }
            $ChunkResults.Metrics["Duration"] += $Duration
        }
    }
    
    return $ChunkResults
}

# Function to generate intelligent summary
function Generate-IntelligentSummary {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Generating intelligent summary..." -ForegroundColor Yellow
    
    # Analyze critical issues
    if ($AnalysisResults.Summary.CriticalIssues.Count -gt 0) {
        $AnalysisResults.Summary.Recommendations += "CRITICAL: Address $($AnalysisResults.Summary.CriticalIssues.Count) critical issues immediately"
    }
    
    # Analyze error patterns
    if ($AnalysisResults.Summary.ErrorCount -gt 0) {
        $ErrorRate = [math]::Round(($AnalysisResults.Summary.ErrorCount / $AnalysisResults.Summary.TotalLines) * 100, 2)
        $AnalysisResults.Summary.Recommendations += "ERRORS: $ErrorRate% error rate detected - review error handling"
    }
    
    # Analyze performance metrics
    if ($AnalysisResults.Summary.KeyMetrics.ContainsKey("Duration")) {
        $AvgDuration = ($AnalysisResults.Summary.KeyMetrics["Duration"] | Measure-Object -Average).Average
        $AnalysisResults.Summary.KeyMetrics["AverageDuration"] = [math]::Round($AvgDuration, 2)
        
        if ($AvgDuration -gt 10) {
            $AnalysisResults.Summary.Recommendations += "PERFORMANCE: Average processing time is $AvgDuration seconds - consider optimization"
        }
    }
    
    # Analyze file processing metrics
    if ($AnalysisResults.Summary.KeyMetrics.ContainsKey("FileCount")) {
        $TotalFiles = ($AnalysisResults.Summary.KeyMetrics["FileCount"] | Measure-Object -Sum).Sum
        $AnalysisResults.Summary.KeyMetrics["TotalFilesProcessed"] = $TotalFiles
        
        if ($TotalFiles -gt 10000) {
            $AnalysisResults.Summary.Recommendations += "SCALE: Large-scale processing detected ($TotalFiles files) - verify system capacity"
        }
    }
    
    # Analyze emoji metrics
    if ($AnalysisResults.Summary.KeyMetrics.ContainsKey("EmojiCount")) {
        $TotalEmojis = ($AnalysisResults.Summary.KeyMetrics["EmojiCount"] | Measure-Object -Sum).Sum
        $AnalysisResults.Summary.KeyMetrics["TotalEmojisFound"] = $TotalEmojis
        
        if ($TotalEmojis -gt 100000) {
            $AnalysisResults.Summary.Recommendations += "COMPLIANCE: Massive emoji violation detected ($TotalEmojis emojis) - immediate cleanup required"
        }
    }
    
    # Generate health score
    $HealthScore = 100
    if ($AnalysisResults.Summary.CriticalIssues.Count -gt 0) { $HealthScore -= 30 }
    if ($AnalysisResults.Summary.ErrorCount -gt 0) { $HealthScore -= 20 }
    if ($AnalysisResults.Summary.WarningCount -gt 0) { $HealthScore -= 10 }
    
    $AnalysisResults.Summary.KeyMetrics["HealthScore"] = [math]::Max(0, $HealthScore)
    
    # Add health assessment
    if ($HealthScore -ge 90) {
        $AnalysisResults.Summary.Recommendations += "HEALTH: System health is EXCELLENT ($HealthScore/100)"
    } elseif ($HealthScore -ge 70) {
        $AnalysisResults.Summary.Recommendations += "HEALTH: System health is GOOD ($HealthScore/100)"
    } elseif ($HealthScore -ge 50) {
        $AnalysisResults.Summary.Recommendations += "HEALTH: System health is FAIR ($HealthScore/100) - attention needed"
    } else {
        $AnalysisResults.Summary.Recommendations += "HEALTH: System health is POOR ($HealthScore/100) - immediate intervention required"
    }
}

# Main processing logic
try {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Starting chunked analysis..." -ForegroundColor Yellow
    
    $Reader = [System.IO.StreamReader]::new($LogPath)
    $ChunkNumber = 0
    $Lines = @()
    
    while (-not $Reader.EndOfStream) {
        $Line = $Reader.ReadLine()
        $Lines += $Line
        
        if ($Lines.Count -ge $ChunkSize) {
            $ChunkNumber++
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Processing chunk $ChunkNumber..." -ForegroundColor Cyan
            
            $ChunkResults = Analyze-LogChunk -Lines $Lines -ChunkNumber $ChunkNumber
            $AnalysisResults.DetailedAnalysis["Chunk_$ChunkNumber"] = $ChunkResults
            $AnalysisResults.Summary.ProcessedChunks++
            
            $Lines = @()
        }
    }
    
    # Process remaining lines
    if ($Lines.Count -gt 0) {
        $ChunkNumber++
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Processing final chunk $ChunkNumber..." -ForegroundColor Cyan
        
        $ChunkResults = Analyze-LogChunk -Lines $Lines -ChunkNumber $ChunkNumber
        $AnalysisResults.DetailedAnalysis["Chunk_$ChunkNumber"] = $ChunkResults
        $AnalysisResults.Summary.ProcessedChunks++
    }
    
    $Reader.Close()
    
    # Calculate processing time
    $ProcessingTime = (Get-Date) - $LogStartTime
    $AnalysisResults.Summary.ProcessingTime = $ProcessingTime.TotalSeconds
    
    # Generate intelligent summary
    Generate-IntelligentSummary
    
    # Save results
    $AnalysisResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
    
    # Display summary
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] [SUCCESS] Log analysis completed!" -ForegroundColor Green
    Write-Host "`nANALYSIS SUMMARY:" -ForegroundColor Cyan
    Write-Host "  - File: $($FileInfo.Name)" -ForegroundColor White
    Write-Host "  - Size: $FileSizeMB MB ($FileSizeGB GB)" -ForegroundColor White
    Write-Host "  - Total Lines: $($AnalysisResults.Summary.TotalLines)" -ForegroundColor White
    Write-Host "  - Chunks Processed: $($AnalysisResults.Summary.ProcessedChunks)" -ForegroundColor White
    Write-Host "  - Processing Time: $([math]::Round($ProcessingTime.TotalSeconds, 2)) seconds" -ForegroundColor White
    Write-Host "  - Health Score: $($AnalysisResults.Summary.KeyMetrics.HealthScore)/100" -ForegroundColor White
    
    Write-Host "`nISSUES DETECTED:" -ForegroundColor Yellow
    Write-Host "  - Errors: $($AnalysisResults.Summary.ErrorCount)" -ForegroundColor White
    Write-Host "  - Warnings: $($AnalysisResults.Summary.WarningCount)" -ForegroundColor White
    Write-Host "  - Critical Issues: $($AnalysisResults.Summary.CriticalIssues.Count)" -ForegroundColor White
    
    Write-Host "`nRECOMMENDATIONS:" -ForegroundColor Green
    foreach ($Recommendation in $AnalysisResults.Summary.Recommendations) {
        Write-Host "  - $Recommendation" -ForegroundColor White
    }
    
    Write-Host "`nResults saved to: $OutputPath" -ForegroundColor Cyan
    
} catch {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [ERROR] Analysis failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] [INFO] V5.0 Simple Log Analyzer completed successfully!" -ForegroundColor Green
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Ready for production deployment!" -ForegroundColor Green
