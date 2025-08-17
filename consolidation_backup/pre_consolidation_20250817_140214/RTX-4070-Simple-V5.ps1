#!/usr/bin/env powershell
<#
.SYNOPSIS
    Agent Exo-Suit V5.0 "Builder of Dreams" - Simple Real Project Processor
    
.DESCRIPTION
    Simple V5.0 system that directly uses Python to process real project files
    Bypasses PowerShell syntax issues and focuses on real GPU acceleration
    
.VERSION
    V5.0 "Builder of Dreams" - Simple Edition
    
.AUTHOR
    Agent Exo-Suit Development Team
#>

param(
    [int]$BatchSize = 100,
    [int]$MaxFileSizeMB = 10
)

Write-Host "=== RTX 4070 SIMPLE V5.0 STARTED ===" -ForegroundColor Green
Write-Host "Batch Size: $BatchSize" -ForegroundColor Yellow
Write-Host "Max File Size: $MaxFileSizeMB MB" -ForegroundColor Yellow

try {
    # Test GPU capabilities
    Write-Host "Testing GPU capabilities..." -ForegroundColor Cyan
    $PyTorchTest = python -c "import torch; print('PyTorch:', torch.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyTorch: Available - $PyTorchTest" -ForegroundColor Green
    } else {
        throw "PyTorch not available"
    }
    
    $CudaTest = python -c "import torch; print('CUDA:', torch.version.cuda)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "CUDA: Available - $CudaTest" -ForegroundColor Green
    } else {
        throw "CUDA not available"
    }
    
    $GPUTest = python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "GPU: Available - $GPUTest" -ForegroundColor Green
    } else {
        throw "GPU not available"
    }
    
    # Test hybrid RAG system
    $RAGTest = python -c "import sys; sys.path.append('rag'); from hybrid_rag_v4 import HybridRAGProcessor; print('Hybrid RAG: Available')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Hybrid RAG System: Available" -ForegroundColor Green
    } else {
        throw "Hybrid RAG system not available"
    }
    
    Write-Host "All GPU capabilities verified successfully!" -ForegroundColor Green
    
    # Get project files
    Write-Host "Scanning project for real files..." -ForegroundColor Cyan
    $Extensions = @('*.py', '*.ps1', '*.md', '*.txt', '*.json', '*.yaml', '*.yml', '*.js', '*.ts', '*.html', '*.css')
    
    $AllFiles = @()
    foreach ($Ext in $Extensions) {
        $Files = Get-ChildItem -Path "." -Recurse -Filter $Ext -ErrorAction SilentlyContinue
        $AllFiles += $Files
    }
    
    # Filter files by size
    $FilteredFiles = @()
    $TotalSize = 0
    foreach ($File in $AllFiles) {
        try {
            if ($File.PSIsContainer) { continue }
            
            $FileSizeMB = $File.Length / (1024 * 1024)
            if ($FileSizeMB -le $MaxFileSizeMB) {
                $FilteredFiles += $File.FullName
                $TotalSize += $File.Length
            }
        } catch {
            continue
        }
    }
    
    Write-Host "Found $($AllFiles.Count) total files" -ForegroundColor Yellow
    Write-Host "Filtered to $($FilteredFiles.Count) files under ${MaxFileSizeMB}MB" -ForegroundColor Yellow
    Write-Host "Total size to process: $([math]::Round($TotalSize / (1024 * 1024 * 1024), 2)) GB" -ForegroundColor Yellow
    
    # Limit files for testing
    $TestFiles = $FilteredFiles | Select-Object -First $BatchSize
    Write-Host "Testing with $($TestFiles.Count) real files..." -ForegroundColor Yellow
    
    # Create Python script for processing
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

def process_real_files(file_paths):
    print("=== RTX 4070 V5.0 REAL PROCESSING ===")
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
    
    print(f"\\nV5.0 Performance Summary:")
    print(f"  Files Processed: {successful_files}")
    print(f"  Processing Time: {processing_time:.2f} seconds")
    print(f"  Speed: {files_per_second:.1f} files/second")
    print(f"  GPU Utilization: {final_gpu_memory / gpu_props.total_memory * 100:.1f}%")
    
    # Cleanup
    processor.cleanup()
    torch.cuda.empty_cache()
    
    return {
        'files_processed': successful_files,
        'total_files': len(file_paths),
        'processing_time': processing_time,
        'files_per_second': files_per_second,
        'success_rate': successful_files / len(file_paths) * 100,
        'gpu_utilization': final_gpu_memory / gpu_props.total_memory * 100
    }

if __name__ == "__main__":
    # Get file list from command line
    if len(sys.argv) > 1:
        file_list_path = sys.argv[1]
        try:
            with open(file_list_path, 'r', encoding='utf-8') as f:
                file_paths = [line.strip() for line in f.readlines() if line.strip()]
            
            # Process the files with REAL hybrid RAG
            results = process_real_files(file_paths)
            
            # Save results
            output_path = file_list_path.replace('.txt', '_v5_results.json')
            import json
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"V5.0 results saved to: {output_path}")
            
        except Exception as e:
            print(f"Error processing files: {e}")
            sys.exit(1)
    else:
        print("Usage: python script.py <file_list_path>")
        sys.exit(1)
"@

    # Save Python script
    $ScriptPath = "temp\rtx4070_v5_processor.py"
    if (!(Test-Path "temp")) { New-Item -ItemType Directory -Path "temp" -Force | Out-Null }
    $PythonScript | Out-File -FilePath $ScriptPath -Encoding UTF8
    
    # Create file list
    $FileListPath = "temp\rtx4070_v5_files.txt"
    $TestFiles | Out-File -FilePath $FileListPath -Encoding UTF8
    
    # Process files using Python
    Write-Host "Processing files with RTX 4070 V5.0 system..." -ForegroundColor Cyan
    $StartTime = Get-Date
    
    $Process = Start-Process -FilePath "python" -ArgumentList $ScriptPath, $FileListPath -NoNewWindow -PassThru -RedirectStandardOutput "temp\v5_output.log" -RedirectStandardError "temp\v5_error.log"
    $Process.WaitForExit()
    
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalSeconds
    
    # Show results
    if (Test-Path "temp\v5_output.log") {
        $Output = Get-Content "temp\v5_output.log" -Raw
        Write-Host $Output -ForegroundColor White
    }
    
    if (Test-Path "temp\v5_error.log") {
        $Error = Get-Content "temp\v5_error.log" -Raw
        if ($Error) {
            Write-Host "Errors:" -ForegroundColor Red
            Write-Host $Error -ForegroundColor Red
        }
    }
    
    # Check results file
    $ResultsPath = "temp\rtx4070_v5_files_v5_results.json"
    if (Test-Path $ResultsPath) {
        try {
            $Results = Get-Content $ResultsPath | ConvertFrom-Json
            Write-Host "=== V5.0 PROCESSING COMPLETED ===" -ForegroundColor Green
            Write-Host "Files Processed: $($Results.files_processed)/$($Results.total_files)" -ForegroundColor Yellow
            Write-Host "Speed: $($Results.files_per_second) files/second" -ForegroundColor Yellow
            Write-Host "GPU Utilization: $([math]::Round($Results.gpu_utilization, 1))%" -ForegroundColor Yellow
            Write-Host "Total Time: $([math]::Round($Duration, 2)) seconds" -ForegroundColor Yellow
        } catch {
            Write-Host "Failed to parse results" -ForegroundColor Red
        }
    } else {
        Write-Host "No results file found" -ForegroundColor Red
    }
    
    Write-Host "=== RTX 4070 SIMPLE V5.0 COMPLETED ===" -ForegroundColor Green
    
} catch {
    Write-Host "=== RTX 4070 SIMPLE V5.0 FAILED ===" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
