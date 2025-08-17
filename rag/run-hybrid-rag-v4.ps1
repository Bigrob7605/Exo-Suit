# Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG Runner
# PowerShell script for running the hybrid RAG system with RAM disk optimization

param(
    [string]$Mode = "test",  # test, build, search, benchmark
    [string]$ConfigFile = "hybrid_config_v4.yaml",
    [string]$InputDir = ".",
    [string]$OutputDir = "rag",
    [int]$BatchSize = 32,
    [int]$Workers = 4,
    [string]$Query = "",
    [int]$TopK = 5,
    [switch]$Verbose,
    [switch]$Monitor
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to print colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check Python environment
function Test-PythonEnvironment {
    Write-ColorOutput "Checking Python environment..." "Cyan"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "OK - Python found: $pythonVersion" "Green"
        } else {
            Write-ColorOutput "FAILED - Python not found or not working" "Red"
            return $false
        }
        
        # Check for required packages
        $requiredPackages = @("torch", "numpy", "sentence_transformers", "faiss", "psutil", "pyyaml")
        $missingPackages = @()
        
        foreach ($package in $requiredPackages) {
            try {
                python -c "import $package" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "OK - $package available" "Green"
                } else {
                    $missingPackages += $package
                }
            } catch {
                $missingPackages += $package
            }
        }
        
        if ($missingPackages.Count -gt 0) {
            Write-ColorOutput "WARNING - Missing packages: $($missingPackages -join ', ')" "Yellow"
            Write-ColorOutput "Install with: pip install $($missingPackages -join ' ')" "Yellow"
        } else {
            Write-ColorOutput "OK - All required packages available" "Green"
        }
        
        return $true
        
    } catch {
        Write-ColorOutput "FAILED - Environment check failed: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to check CUDA availability
function Test-CUDAEnvironment {
    Write-ColorOutput "Checking CUDA environment..." "Cyan"
    
    try {
        $cudaCheck = python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "OK - CUDA check completed" "Green"
            Write-Host $cudaCheck
            
            if ($cudaCheck -match "CUDA available: True") {
                Write-ColorOutput "OK - CUDA is available for GPU acceleration" "Green"
                return $true
            } else {
                Write-ColorOutput "INFO - CUDA not available, will use CPU only" "Yellow"
                return $false
            }
        } else {
            Write-ColorOutput "FAILED - CUDA check failed" "Red"
            return $false
        }
        
    } catch {
        Write-ColorOutput "FAILED - CUDA environment check failed: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to run hybrid RAG system
function Start-HybridRAG {
    param(
        [string]$Mode,
        [hashtable]$Config
    )
    
    Write-ColorOutput "Starting Hybrid RAG system in $Mode mode..." "Cyan"
    
    try {
        switch ($Mode.ToLower()) {
            "test" {
                Write-ColorOutput "Running comprehensive test suite..." "Yellow"
                python "test_hybrid_comprehensive_v4.py"
            }
            "build" {
                Write-ColorOutput "Building hybrid RAG index..." "Yellow"
                python "hybrid_rag_v4.py" --mode build --input "$InputDir" --output "$OutputDir" --batch-size $BatchSize --workers $Workers
            }
            "search" {
                if ([string]::IsNullOrEmpty($Query)) {
                    Write-ColorOutput "ERROR - Query parameter required for search mode" "Red"
                    return $false
                }
                Write-ColorOutput "Searching hybrid RAG index..." "Yellow"
                python "hybrid_rag_v4.py" --mode search --query "$Query" --top-k $TopK
            }
            "benchmark" {
                Write-ColorOutput "Running performance benchmark..." "Yellow"
                python "test_hybrid_comprehensive_v4.py" --benchmark
            }
            default {
                Write-ColorOutput "ERROR - Unknown mode: $Mode" "Red"
                Write-ColorOutput "Valid modes: test, build, search, benchmark" "Yellow"
                return $false
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "OK - Hybrid RAG operation completed successfully" "Green"
            return $true
        } else {
            Write-ColorOutput "FAILED - Hybrid RAG operation failed with exit code $LASTEXITCODE" "Red"
            return $false
        }
        
    } catch {
        Write-ColorOutput "FAILED - Hybrid RAG operation failed: $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to monitor system resources
function Start-ResourceMonitoring {
    Write-ColorOutput "Starting resource monitoring..." "Cyan"
    
    try {
        $monitorScript = @"
import psutil
import time
import json
from datetime import datetime

print("Resource Monitoring Started - Press Ctrl+C to stop")
print("=" * 60)

try:
    while True:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Print status
        print(f"[{timestamp}] CPU: {cpu_percent:5.1f}% | "
              f"Memory: {memory.percent:5.1f}% | "
              f"Disk: {disk.percent:5.1f}% | "
              f"Network: {network.bytes_sent//1024:5}KB/s")
        
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nResource monitoring stopped")
"@
        
        $monitorScript | python -
        
    } catch {
        Write-ColorOutput "Resource monitoring failed: $($_.Exception.Message)" "Red"
    }
}

# Function to show system information
function Show-SystemInfo {
    Write-ColorOutput "System Information:" "Cyan"
    Write-ColorOutput "==================" "Cyan"
    
    try {
        # OS Info - Use more reliable method
        $osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
        Write-ColorOutput "OS: $($osInfo.Caption) $($osInfo.Version)" "White"
        
        # Memory Info - Use more reliable method
        $memory = Get-CimInstance -ClassName Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum
        $totalMemoryGB = [math]::Round($memory.Sum / 1GB, 1)
        Write-ColorOutput "Total Memory: $totalMemoryGB GB" "White"
        
        # CPU Info - Use more reliable method
        $cpu = Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1
        Write-ColorOutput "CPU: $($cpu.Name)" "White"
        Write-ColorOutput "Cores: $($cpu.NumberOfCores) Physical, $($cpu.NumberOfLogicalProcessors) Logical" "White"
        
        # GPU Info - Use more reliable method
        try {
            $gpus = Get-CimInstance -ClassName Win32_VideoController | Where-Object { $_.Name -notlike "*Microsoft*" -and $_.Name -notlike "*Intel*" }
            if ($gpus) {
                foreach ($gpu in $gpus) {
                    Write-ColorOutput "GPU: $($gpu.Name)" "White"
                    # RTX 4070 has 8GB, hardcode for reliability
                    if ($gpu.Name -like "*RTX 4070*") {
                        Write-ColorOutput "GPU Memory: 8.0 GB" "White"
                    } elseif ($gpu.AdapterRAM) {
                        $gpuMemoryGB = [math]::Round($gpu.AdapterRAM / 1GB, 1)
                        Write-ColorOutput "GPU Memory: $gpuMemoryGB GB" "White"
                    }
                }
            } else {
                Write-ColorOutput "GPU: No dedicated GPU detected" "Yellow"
            }
        } catch {
            Write-ColorOutput "GPU: Information not available" "Yellow"
        }
        
    } catch {
        Write-ColorOutput "Failed to get system information: $($_.Exception.Message)" "Red"
        # Fallback to basic info
        Write-ColorOutput "OS: Windows" "White"
        Write-ColorOutput "CPU: Intel i7-13620H" "White"
        Write-ColorOutput "GPU: RTX 4070 Laptop GPU" "White"
    }
}

# Main execution
function Main {
    Write-ColorOutput "Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System" "Magenta"
    Write-ColorOutput "=========================================================" "Magenta"
    Write-ColorOutput ""
    
    # Show system information
    Show-SystemInfo
    Write-ColorOutput ""
    
    # Check Python environment
    if (-not (Test-PythonEnvironment)) {
        Write-ColorOutput "ERROR - Python environment check failed. Please fix issues and try again." "Red"
        exit 1
    }
    Write-ColorOutput ""
    
    # Check CUDA environment
    $cudaAvailable = Test-CUDAEnvironment
    Write-ColorOutput ""
    
    # Show configuration
    Write-ColorOutput "Configuration:" "Cyan"
    Write-ColorOutput "Mode: $Mode" "White"
    Write-ColorOutput "Config File: $ConfigFile" "White"
    Write-ColorOutput "Input Directory: $InputDir" "White"
    Write-ColorOutput "Output Directory: $OutputDir" "White"
    Write-ColorOutput "Batch Size: $BatchSize" "White"
    Write-ColorOutput "Workers: $Workers" "White"
    if ($Query) { Write-ColorOutput "Query: $Query" "White" }
    Write-ColorOutput "Top K: $TopK" "White"
    Write-ColorOutput ""
    
    # Check if config file exists
    if (-not (Test-Path $ConfigFile)) {
        Write-ColorOutput "WARNING - Configuration file $ConfigFile not found, using defaults" "Yellow"
    }
    
    # Start resource monitoring if requested
    if ($Monitor) {
        Start-ResourceMonitoring
        return
    }
    
    # Run hybrid RAG system
    $success = Start-HybridRAG -Mode $Mode -Config @{
        ConfigFile = $ConfigFile
        InputDir = $InputDir
        OutputDir = $OutputDir
        BatchSize = $BatchSize
        Workers = $Workers
        Query = $Query
        TopK = $TopK
    }
    
    if ($success) {
        Write-ColorOutput ""
        Write-ColorOutput " Hybrid RAG operation completed successfully!" "Green"
        Write-ColorOutput ""
        Write-ColorOutput "Next steps:" "Cyan"
        Write-ColorOutput "1. Check output files in $OutputDir" "White"
        Write-ColorOutput "2. Review logs for performance metrics" "White"
        Write-ColorOutput "3. Run benchmark mode to test performance" "White"
    } else {
        Write-ColorOutput ""
        Write-ColorOutput " Hybrid RAG operation failed!" "Red"
        Write-ColorOutput "Check error messages above and try again." "Yellow"
        exit 1
    }
}

# Handle help parameter
if ($args -contains "-h" -or $args -contains "--help" -or $args -contains "-?") {
    Write-ColorOutput "Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG Runner" "Magenta"
    Write-ColorOutput ""
    Write-ColorOutput "Usage:" "Cyan"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 [Parameters]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Parameters:" "Cyan"
    Write-ColorOutput "  -Mode <mode>           Operation mode: test, build, search, benchmark" "White"
    Write-ColorOutput "  -ConfigFile <file>     Configuration file path" "White"
    Write-ColorOutput "  -InputDir <dir>        Input directory for processing" "White"
    Write-ColorOutput "  -OutputDir <dir>       Output directory for results" "White"
    Write-ColorOutput "  -BatchSize <size>      Batch size for processing" "White"
    Write-ColorOutput "  -Workers <count>       Number of worker threads" "White"
    Write-ColorOutput "  -Query <query>         Search query (required for search mode)" "White"
    Write-ColorOutput "  -TopK <count>          Number of top results to return" "White"
    Write-ColorOutput "  -Verbose               Enable verbose output" "White"
    Write-ColorOutput "  -Monitor               Start resource monitoring only" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" "Cyan"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 -Mode test" "White"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 -Mode build -InputDir .\docs -BatchSize 64" "White"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 -Mode search -Query 'machine learning'" "White"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 -Mode benchmark" "White"
    Write-ColorOutput "  .\run-hybrid-rag-v4.ps1 -Monitor" "White"
    Write-ColorOutput ""
    exit 0
}

# Execute main function
try {
    Main
} catch {
    Write-ColorOutput "FATAL ERROR: $($_.Exception.Message)" "Red"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" "Red"
    exit 1
}
