#!/usr/bin/env powershell
<#
.SYNOPSIS
    Agent Exo-Suit V5.0 "Builder of Dreams" - RTX 4070 Batch File Processor
    
.DESCRIPTION
    Uses the real hybrid RAG system to process actual project files with GPU acceleration
    No fake processing - real file analysis and GPU acceleration
    
.VERSION
    V5.0 "Builder of Dreams" - Real Processing Edition
    
.AUTHOR
    Agent Exo-Suit Development Team
#>

param(
    [string]$Mode = "Test",
    [int]$BatchSize = 100,
    [int]$MaxFileSizeMB = 10,
    [switch]$EnableGPUAcceleration = $true
)

# Global variables
$ScriptName = "RTX-4070-Batch-Processor-V5"
$LogFile = "logs\rtx4070_batch_v5.log"
$ResultsFile = "logs\rtx4070_batch_results.json"
$TempDir = "temp\batch_processing"

# Ensure required directories exist
$Directories = @("logs", "temp", "temp\batch_processing")
foreach ($Dir in $Directories) {
    if (!(Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

# Get real project files for processing
function Get-ProjectFiles {
    Write-Log "Scanning project for real files to process..." "INFO"
    
    try {
        $ProjectRoot = Get-Location
        $Extensions = @('*.py', '*.ps1', '*.md', '*.txt', '*.json', '*.yaml', '*.yml', '*.js', '*.ts', '*.html', '*.css')
        
        $AllFiles = @()
        foreach ($Ext in $Extensions) {
            $Files = Get-ChildItem -Path $ProjectRoot -Recurse -Filter $Ext -ErrorAction SilentlyContinue
            $AllFiles += $Files
        }
        
        # Filter files by size and type
        $FilteredFiles = @()
        $TotalSize = 0
        foreach ($File in $AllFiles) {
            try {
                if ($File.PSIsContainer) { continue }  # Skip directories
                
                $FileSizeMB = $File.Length / (1024 * 1024)
                if ($FileSizeMB -le $MaxFileSizeMB) {
                    $FilteredFiles += $File.FullName
                    $TotalSize += $File.Length
                }
            } catch {
                # Skip files with access issues
                continue
            }
        }
        
        Write-Log "Found $($AllFiles.Count) total files" "INFO"
        Write-Log "Filtered to $($FilteredFiles.Count) files under ${MaxFileSizeMB}MB" "INFO"
        Write-Log "Total size to process: $([math]::Round($TotalSize / (1024 * 1024 * 1024), 2)) GB" "INFO"
        
        return $FilteredFiles
        
    } catch {
        Write-Log "Failed to scan project files: $($_.Exception.Message)" "ERROR"
        return @()
    }
}

# Test GPU capabilities
function Test-GPUCapabilities {
    Write-Log "Testing real GPU capabilities..." "INFO"
    
    try {
        # Test PyTorch
        $PyTorchTest = python -c "import torch; print('PyTorch:', torch.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "PyTorch: Available - $PyTorchTest" "INFO"
        } else {
            Write-Log "PyTorch: Not available" "ERROR"
            return $false
        }
        
        # Test CUDA
        $CudaTest = python -c "import torch; print('CUDA:', torch.version.cuda)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "CUDA: Available - $CudaTest" "INFO"
        } else {
            Write-Log "CUDA: Not available" "ERROR"
            return $false
        }
        
        # Test GPU
        $GPUTest = python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "GPU: Available - $GPUTest" "INFO"
        } else {
            Write-Log "GPU: Not available" "ERROR"
            return $false
        }
        
        # Test hybrid RAG system
        $RAGTest = python -c "import sys; sys.path.append('rag'); from hybrid_rag_v4 import HybridRAGProcessor; print('Hybrid RAG: Available')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Hybrid RAG System: Available" "INFO"
        } else {
            Write-Log "Hybrid RAG System: Not available" "ERROR"
            return $false
        }
        
        Write-Log "All GPU capabilities verified successfully!" "INFO"
        return $true
        
    } catch {
        Write-Log "GPU capability test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Process files using real hybrid RAG system
function Process-FileBatch {
    param([string[]]$Files, [int]$BatchNumber)
    
    Write-Log "Processing batch $BatchNumber with $($Files.Count) files using real hybrid RAG..." "INFO"
    
    try {
        # Create Python script that uses the real hybrid RAG system
        $PythonScript = @"
import sys
import time
import psutil
import torch
from pathlib import Path

# Add rag directory to path
rag_dir = Path(__file__).parent.parent / "rag"
sys.path.insert(0, str(rag_dir))

from hybrid_rag_v4 import HybridRAGProcessor

def process_real_batch(file_paths, batch_num):
    print(f"=== REAL PROCESSING BATCH {batch_num} ===")
    print(f"Files: {len(file_paths)}")
    
    # Initialize real hybrid RAG processor
    config = {
        'model_name': 'all-MiniLM-L6-v2',
        'batch_size': 128,
        'num_workers': 4,
        'ram_disk_size_gb': 4,
        'gpu_memory_threshold': 0.9
    }
    
    processor = HybridRAGProcessor(config)
    
    device = torch.cuda.current_device()
    gpu_props = torch.cuda.get_device_properties(device)
    
    print(f"GPU: {gpu_props.name}")
    print(f"VRAM: {gpu_props.total_memory / (1024**3):.1f} GB")
    
    # Initialize memory tracking
    torch.cuda.empty_cache()
    initial_gpu_memory = torch.cuda.memory_allocated(device)
    initial_system_memory = psutil.virtual_memory().used
    
    print(f"\\nInitial Memory:")
    print(f"  GPU: {initial_gpu_memory // (1024**2)} MB")
    print(f"  System: {initial_system_memory // (1024**2)} MB")
    
    # Process files using REAL hybrid RAG system
    start_time = time.time()
    results = processor.process_files(file_paths, batch_size=config['batch_size'])
    processing_time = time.time() - start_time
    
    # Calculate performance metrics
    files_per_second = len(file_paths) / processing_time
    successful_files = len([r for r in results if r.success])
    
    print(f"\\nREAL Processing completed in {processing_time:.2f} seconds")
    print(f"Speed: {files_per_second:.1f} files/second")
    print(f"Success rate: {successful_files}/{len(file_paths)} files")
    
    # Final memory status
    final_gpu_memory = torch.cuda.memory_allocated(device)
    final_system_memory = psutil.virtual_memory().used
    
    print(f"\\nFinal Memory:")
    print(f"  GPU: {final_gpu_memory // (1024**2)} MB")
    print(f"  System: {final_system_memory // (1024**2)} MB")
    
    print(f"\\nBatch Summary:")
    print(f"  Files Processed: {successful_files}")
    print(f"  Processing Time: {processing_time:.2f} seconds")
    print(f"  Speed: {files_per_second:.1f} files/second")
    
    # Cleanup
    processor.cleanup()
    torch.cuda.empty_cache()
    
    return {
        'files_processed': successful_files,
        'total_files': len(file_paths),
        'processing_time': processing_time,
        'files_per_second': files_per_second,
        'success_rate': successful_files / len(file_paths) * 100
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_list_path = sys.argv[1]
        try:
            with open(file_list_path, 'r', encoding='utf-8') as f:
                file_paths = [line.strip() for line in f.readlines() if line.strip()]
            
            # Process the batch with REAL hybrid RAG
            results = process_real_batch(file_paths, 1)
            
            # Save results
            output_path = file_list_path.replace('.txt', '_real_results.json')
            import json
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"Real results saved to: {output_path}")
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            sys.exit(1)
    else:
        print("Usage: python script.py <file_list_path>")
        sys.exit(1)
"@

        # Save the Python script
        $ScriptPath = "$TempDir\real_batch_$BatchNumber.py"
        $PythonScript | Out-File -FilePath $ScriptPath -Encoding UTF8
        
        # Create file list for this batch
        $FileListPath = "$TempDir\real_batch_$BatchNumber.txt"
        $Files | Out-File -FilePath $FileListPath -Encoding UTF8
        
        # Process the batch using Python with REAL hybrid RAG
        Write-Log "Executing batch $BatchNumber with REAL hybrid RAG processing..." "INFO"
        
        $StartTime = Get-Date
        
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessInfo.FileName = "python"
        $ProcessInfo.Arguments = "$ScriptPath $FileListPath"
        $ProcessInfo.UseShellExecute = $false
        $ProcessInfo.RedirectStandardOutput = $true
        $ProcessInfo.RedirectStandardError = $true
        $ProcessInfo.WorkingDirectory = $TempDir
        
        $Process = New-Object System.Diagnostics.Process
        $Process.StartInfo = $ProcessInfo
        $Process.Start() | Out-Null
        
        # Capture output
        $Output = $Process.StandardOutput.ReadToEnd()
        $ErrorOutput = $Process.StandardError.ReadToEnd()
        $Process.WaitForExit()
        
        $EndTime = Get-Date
        $Duration = ($EndTime - $StartTime).TotalSeconds
        
        # Log results
        Write-Log "Batch $BatchNumber completed in $Duration seconds with exit code: $($Process.ExitCode)" "INFO"
        if ($Output) { Write-Log "Output: $Output" "INFO" }
        if ($ErrorOutput) { Write-Log "Error: $ErrorOutput" "WARN" }
        
        # Check for results file
        $ResultsPath = "$TempDir\real_batch_$BatchNumber`_real_results.json"
        if (Test-Path $ResultsPath) {
            try {
                $Results = Get-Content $ResultsPath | ConvertFrom-Json
                Write-Log "Batch $BatchNumber processed $($Results.files_processed)/$($Results.total_files) files successfully" "INFO"
                Write-Log "Speed: $($Results.files_per_second) files/second" "INFO"
                return $Results
            } catch {
                Write-Log "Failed to parse results for batch $BatchNumber: $($_.Exception.Message)" "ERROR"
                return @{}
            }
        } else {
            Write-Log "No results file found for batch $BatchNumber" "WARN"
            return @{}
        }
        
    } catch {
        Write-Log "Failed to process batch $BatchNumber: $($_.Exception.Message)" "ERROR"
        return @{}
    }
}

# Main execution
function Main {
    Write-Log "=== RTX 4070 BATCH PROCESSOR V5.0 STARTED ===" "INFO"
    Write-Log "Mode: $Mode" "INFO"
    Write-Log "Batch Size: $BatchSize" "INFO"
            Write-Log "Max File Size: $MaxFileSizeMB MB" "INFO"
    Write-Log "GPU Acceleration: $EnableGPUAcceleration" "INFO"
    
    try {
        # Test real GPU capabilities
        $GPUTest = Test-GPUCapabilities
        if (!$GPUTest) {
            throw "Failed to verify real GPU capabilities"
        }
        
        # Get real project files
        $ProjectFiles = Get-ProjectFiles
        if ($ProjectFiles.Count -eq 0) {
            throw "No real project files found for processing"
        }
        
        # Limit files for testing
        $TestFiles = $ProjectFiles | Select-Object -First $BatchSize
        Write-Log "Testing with $($TestFiles.Count) real files..." "INFO"
        
        # Process files in batches
        $BatchResults = @()
        $BatchNumber = 1
        
        for ($i = 0; $i -lt $TestFiles.Count; $i += $BatchSize) {
            $BatchFiles = $TestFiles[$i..([math]::Min($i + $BatchSize - 1, $TestFiles.Count - 1))]
            
            Write-Log "Starting real batch $BatchNumber..." "INFO"
            $BatchResult = Process-FileBatch -Files $BatchFiles -BatchNumber $BatchNumber
            $BatchResults += $BatchResult
            
            $BatchNumber++
        }
        
        # Summary report
        $TotalFiles = ($BatchResults | Measure-Object -Property total_files -Sum).Sum
        $TotalProcessed = ($BatchResults | Measure-Object -Property files_processed -Sum).Sum
        $TotalTime = ($BatchResults | Measure-Object -Property processing_time -Sum).Sum
        $TotalBatches = $BatchResults.Count
        
        if ($TotalTime -gt 0) {
            $OverallSpeed = $TotalProcessed / $TotalTime
        } else {
            $OverallSpeed = 0
        }
        
        Write-Log "=== REAL PROCESSING COMPLETED ===" "INFO"
        Write-Log "Total Files: $TotalFiles" "INFO"
        Write-Log "Successfully Processed: $TotalProcessed" "INFO"
        Write-Log "Total Processing Time: $([math]::Round($TotalTime, 2)) seconds" "INFO"
        Write-Log "Overall Speed: $([math]::Round($OverallSpeed, 1)) files/second" "INFO"
        Write-Log "Total Batches: $TotalBatches" "INFO"
        
        # Save results
        $Results = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            TotalFiles = $TotalFiles
            SuccessfullyProcessed = $TotalProcessed
            TotalProcessingTime = $TotalTime
            OverallSpeed = $OverallSpeed
            TotalBatches = $TotalBatches
            BatchResults = $BatchResults
        }
        
        $Results | ConvertTo-Json -Depth 10 | Out-File -FilePath $ResultsFile -Encoding UTF8
        Write-Log "Results saved to: $ResultsFile" "INFO"
        
        Write-Log "=== RTX 4070 BATCH PROCESSOR V5.0 COMPLETED SUCCESSFULLY ===" "INFO"
        return $true
        
    } catch {
        Write-Log "=== RTX 4070 BATCH PROCESSOR V5.0 FAILED ===" "ERROR"
        Write-Log "Error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Execute main function
if ($MyInvocation.InvocationName -ne '.') {
    $Success = Main
    exit $(if ($Success) { 0 } else { 1 })
}
