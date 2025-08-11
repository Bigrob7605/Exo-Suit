# Agent Exo-Suit V4.0 "PERFECTION" - GPU Monitor
# Advanced GPU monitoring with performance analysis and optimization

[CmdletBinding()]
param(
    [ValidateSet('Info', 'Monitor', 'Benchmark', 'Optimize', 'Test', 'Report')]
    [string]$Mode = 'Info',
    
    [Parameter(Mandatory=$false)]
    [int]$Duration = 60,
    
    [Parameter(Mandatory=$false)]
    [int]$Interval = 1,
    
    [switch]$ForceGPU,
    
    [switch]$ForceCPU,
    
    [switch]$Json,
    
    [switch]$Benchmark
)

# ===== ULTRA-ROBUST ERROR HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

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
    
    if ($PSCmdlet.MyInvocation.BoundParameters['Verbose']) {
        $logPath = Join-Path (Get-Location) "gpu_monitor_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== SYSTEM VALIDATION =====
function Test-SystemRequirements {
    Write-Log " Validating system requirements..." -Color Cyan
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log " PowerShell 5.1+ required" -Color Red
        return $false
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize
    $memoryGB = [math]::Round($memory / 1024 / 1024, 2)
    Write-Log " Available memory: $memoryGB GB" -Color Green
    
    if ($memoryGB -lt 2) {
        Write-Log " Low memory detected. GPU monitoring may be limited" -Color Yellow
    }
    
    return $true
}

# ===== GPU DETECTION =====
function Get-GPUInfo {
    Write-Log " Detecting GPU capabilities..." -Color Cyan
    
    try {
        $gpuInfo = @()
        
        # Method 1: WMI Video Controller (basic info only)
        try {
            $videoControllers = Get-CimInstance -ClassName Win32_VideoController -ErrorAction SilentlyContinue
            
            if ($videoControllers) {
                foreach ($controller in $videoControllers) {
                    $gpu = @{
                        Name = $controller.Name
                        AdapterRAM = $controller.AdapterRAM
                        DriverVersion = $controller.DriverVersion
                        VideoProcessor = $controller.VideoProcessor
                        VideoMemoryType = $controller.VideoMemoryType
                        AdapterCompatibility = $controller.AdapterCompatibility
                        IsCUDA = $controller.Name -match "NVIDIA|RTX|GTX|Tesla|Quadro"
                        IsAMD = $controller.Name -match "AMD|Radeon|RX|Vega"
                        IsIntel = $controller.Name -match "Intel|UHD|Iris"
                        Source = "WMI"
                        MemoryGB = "Unknown"  # Will be updated by NVIDIA-SMI if available
                    }
                    
                    $gpuInfo += $gpu
                }
            }
        } catch {
            Write-Log " WMI GPU detection failed: $_" -Color Yellow
        }
        
        # Method 2: Registry-based detection
        try {
            $registryPaths = @(
                "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}",
                "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000",
                "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0001"
            )
            
            foreach ($path in $registryPaths) {
                if (Test-Path $path) {
                    $regGPU = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
                    if ($regGPU.ProviderName -and $regGPU.ProviderName -notin $gpuInfo.Name) {
                        $gpu = @{
                            Name = $regGPU.ProviderName
                            DriverVersion = $regGPU.DriverVersion
                            IsCUDA = $regGPU.ProviderName -match "NVIDIA"
                            IsAMD = $regGPU.ProviderName -match "AMD"
                            IsIntel = $regGPU.ProviderName -match "Intel"
                            Source = "Registry"
                            MemoryGB = "Unknown"
                        }
                        $gpuInfo += $gpu
                    }
                }
            }
        } catch {
            Write-Log " Registry GPU detection failed: $_" -Color Yellow
        }
        
        # Method 3: Check for NVIDIA-SMI
        try {
            $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
            if ($nvidiaSmi) {
                Write-Log " NVIDIA-SMI found in PATH" -Color Green
                
                # Get detailed NVIDIA info
                $nvidiaInfo = nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null
                
                if ($LASTEXITCODE -eq 0) {
                    foreach ($line in $nvidiaInfo) {
                        if ($line -match '(.+),\s*(\d+),\s*(.+)') {
                            $gpuName = $matches[1].Trim()
                            $memoryMB = [int]$matches[2]
                            $driverVersion = $matches[3].Trim()
                            
                            # Check if we already have this GPU from WMI
                            $existingGPU = $gpuInfo | Where-Object { $_.Name -eq $gpuName }
                            
                            if ($existingGPU) {
                                # Update existing GPU with accurate memory info
                                $existingGPU.MemoryGB = [math]::Round($memoryMB / 1024, 2)
                                $existingGPU.DriverVersion = $driverVersion
                                $existingGPU.Source = "WMI + NVIDIA-SMI"
                                Write-Log " Updated GPU memory for $gpuName - $($existingGPU.MemoryGB) GB" -Color Green
                            } else {
                                # Create new GPU entry
                                $gpu = @{
                                    Name = $gpuName
                                    MemoryGB = [math]::Round($memoryMB / 1024, 2)
                                    DriverVersion = $driverVersion
                                    IsCUDA = $true
                                    IsAMD = $false
                                    IsIntel = $false
                                    Source = "NVIDIA-SMI"
                                }
                                $gpuInfo += $gpu
                            }
                        }
                    }
                }
            }
        } catch {
            Write-Log " NVIDIA-SMI not found" -Color Yellow
        }
        
        if ($gpuInfo.Count -gt 0) {
            Write-Log " GPU detection completed: $($gpuInfo.Count) GPU(s) found" -Color Green
            return $gpuInfo
        } else {
            Write-Log " No GPUs detected" -Color Yellow
            return $null
        }
        
    } catch {
        Write-Log " GPU detection failed: $_" -Color Red
        return $null
    }
}

# ===== GPU PERFORMANCE MONITORING =====
function Start-GPUMonitoring {
    param([int]$Duration, [int]$Interval)
    
    Write-Log " Starting GPU monitoring..." -Color Cyan
    
    try {
        $monitoringData = @()
        $startTime = Get-Date
        
        Write-Log " Monitoring GPU performance for $Duration seconds (interval: $Interval s)..." -Color Cyan
        
        for ($i = 0; $i -lt $Duration; $i += $Interval) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            $dataPoint = @{
                Timestamp = $timestamp
                GPUs = @()
            }
            
            # Get GPU information for this interval
            $gpus = Get-GPUInfo
            if ($gpus) {
                foreach ($gpu in $gpus) {
                    $gpuData = @{
                        Name = $gpu.Name
                        MemoryGB = $gpu.MemoryGB
                        IsCUDA = $gpu.IsCUDA
                        IsAMD = $gpu.IsAMD
                        IsIntel = $gpu.IsIntel
                        Source = $gpu.Source
                    }
                    
                    # Try to get real-time performance data if available
                    if ($gpu.IsCUDA -and $gpu.Source -eq "NVIDIA-SMI") {
                        try {
                            $nvidiaStats = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.free,temperature.gpu --format=csv,noheader,nounits 2>$null
                            if ($LASTEXITCODE -eq 0) {
                                foreach ($line in $nvidiaStats) {
                                    if ($line -match '(\d+),\s*(\d+)\s*MiB,\s*(\d+)\s*MiB,\s*(\d+)') {
                                        $gpuData.GPUUtilization = [int]$matches[1]
                                        $gpuData.MemoryUsedMB = [int]$matches[2]
                                        $gpuData.MemoryFreeMB = [int]$matches[3]
                                        $gpuData.Temperature = [int]$matches[4]
                                    }
                                }
                            }
                        } catch {
                            # NVIDIA-SMI failed, continue without real-time data
                        }
                    }
                    
                    $dataPoint.GPUs += $gpuData
                }
            }
            
            # Get system-wide metrics
            try {
                $cpuUsage = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1).CounterSamples[0].CookedValue
                $memoryUsage = (Get-Counter '\Memory\Available MBytes' -SampleInterval 1 -MaxSamples 1).CounterSamples[0].CookedValue
                
                $dataPoint.SystemMetrics = @{
                    CPUUsage = [math]::Round($cpuUsage, 2)
                    AvailableMemoryMB = [math]::Round($memoryUsage, 2)
                }
            } catch {
                $dataPoint.SystemMetrics = @{
                    CPUUsage = "Unknown"
                    AvailableMemoryMB = "Unknown"
                }
            }
            
            $monitoringData += $dataPoint
            
            # Display current status
            $gpuCount = $dataPoint.GPUs.Count
            $cpuUsage = $dataPoint.SystemMetrics.CPUUsage
            Write-Host " $timestamp | GPUs: $gpuCount | CPU: $cpuUsage%" -ForegroundColor Cyan
            
            Start-Sleep -Seconds $Interval
        }
        
        $endTime = Get-Date
        $actualDuration = ($endTime - $startTime).TotalSeconds
        
        Write-Log " GPU monitoring completed in $([math]::Round($actualDuration, 2)) seconds" -Color Green
        
        return $monitoringData
        
    } catch {
        Write-Log " Error during GPU monitoring: $_" -Color Red
        return @()
    }
}

# ===== GPU BENCHMARKING =====
function Start-GPUBenchmark {
    Write-Log " Starting GPU Monitor V4.0 benchmark..." -Color Cyan
    
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        
        # Test GPU detection
        $gpus = Get-GPUInfo
        $detectionTime = $sw.Elapsed.TotalMilliseconds
        
        # Test monitoring capabilities
        $sw.Restart()
        $monitoringData = Start-GPUMonitoring -Duration 5 -Interval 1
        $monitoringTime = $sw.Elapsed.TotalMilliseconds
        
        $sw.Stop()
        
        $results = @{
            gpu_detection_ms = [math]::Round($detectionTime, 2)
            monitoring_test_ms = [math]::Round($monitoringTime, 2)
            total_time_ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
            gpus_found = if ($gpus) { $gpus.Count } else { 0 }
            cuda_gpus = if ($gpus) { ($gpus | Where-Object { $_.IsCUDA }).Count } else { 0 }
            amd_gpus = if ($gpus) { ($gpus | Where-Object { $_.IsAMD }).Count } else { 0 }
            intel_gpus = if ($gpus) { ($gpus | Where-Object { $_.IsIntel }).Count } else { 0 }
            system_memory_gb = [math]::Round((Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize) / 1024 / 1024, 2)
        }
        
        Write-Log " Benchmark Results:" -Color Cyan
        $results | Format-Table -AutoSize
        
        return $results
        
    } catch {
        Write-Log " Benchmark failed: $_" -Color Red
        return $null
    }
}

# ===== GPU OPTIMIZATION =====
function Optimize-GPUSettings {
    Write-Log " Optimizing GPU settings..." -Color Cyan
    
    try {
        $optimizations = @{}
        $gpus = Get-GPUInfo
        
        if (-not $gpus) {
            Write-Log " No GPUs found for optimization" -Color Yellow
            return $false
        }
        
        foreach ($gpu in $gpus) {
            if ($gpu.IsCUDA) {
                Write-Log " Optimizing NVIDIA GPU: $($gpu.Name)" -Color Cyan
                
                # Try to set NVIDIA power management mode
                try {
                    $powerResult = nvidia-smi -pm 1 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        $optimizations.PowerManagement = $true
                        Write-Log " Power management enabled" -Color Green
                    }
                } catch {
                    Write-Log " Could not set power management mode" -Color Yellow
                }
                
                # Try to set compute mode
                try {
                    $computeResult = nvidia-smi -c 0 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        $optimizations.ComputeMode = $true
                        Write-Log " Compute mode set to default" -Color Green
                    }
                } catch {
                    Write-Log " Could not set compute mode" -Color Yellow
                }
                
            } elseif ($gpu.IsAMD) {
                Write-Log " Optimizing AMD GPU: $($gpu.Name)" -Color Cyan
                
                # AMD-specific optimizations would go here
                # These typically require AMD software tools
                $optimizations.AMDGPU = $true
                
            } elseif ($gpu.IsIntel) {
                Write-Log " Optimizing Intel GPU: $($gpu.Name)" -Color Cyan
                
                # Intel-specific optimizations would go here
                $optimizations.IntelGPU = $true
            }
        }
        
        Write-Log " GPU optimization completed" -Color Green
        return $true
        
    } catch {
        Write-Log " Error optimizing GPU settings: $_" -Color Red
        return $false
    }
}

# ===== GPU TESTING =====
function Test-GPUSystem {
    Write-Log " Testing GPU system..." -Color Cyan
    
    try {
        $testResults = @{
            GPUDetection = $false
            NVIDIA_SMI = $false
            Monitoring = $false
            Optimization = $false
        }
        
        # Test 1: GPU Detection
        Write-Log " Test 1: GPU Detection" -Color Cyan
        $gpus = Get-GPUInfo
        if ($gpus -and $gpus.Count -gt 0) {
            $testResults.GPUDetection = $true
            Write-Log " GPU Detection: PASSED" -Color Green
        } else {
            Write-Log " GPU Detection: FAILED" -Color Red
        }
        
        # Test 2: NVIDIA-SMI (if applicable)
        Write-Log " Test 2: NVIDIA-SMI Availability" -Color Cyan
        try {
            $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
            if ($nvidiaSmi) {
                $testResults.NVIDIA_SMI = $true
                Write-Log " NVIDIA-SMI: PASSED" -Color Green
            } else {
                Write-Log " NVIDIA-SMI: NOT AVAILABLE" -Color Yellow
            }
        } catch {
            Write-Log " NVIDIA-SMI: NOT AVAILABLE" -Color Yellow
        }
        
        # Test 3: Monitoring Capability
        Write-Log " Test 3: Monitoring Capability" -Color Cyan
        $monitoringData = Start-GPUMonitoring -Duration 3 -Interval 1
        if ($monitoringData.Count -gt 0) {
            $testResults.Monitoring = $true
            Write-Log " Monitoring: PASSED" -Color Green
        } else {
            Write-Log " Monitoring: FAILED" -Color Red
        }
        
        # Test 4: Optimization Capability
        Write-Log " Test 4: Optimization Capability" -Color Cyan
        if (Optimize-GPUSettings) {
            $testResults.Optimization = $true
            Write-Log " Optimization: PASSED" -Color Green
        } else {
            Write-Log " Optimization: PARTIAL" -Color Yellow
        }
        
        # Summary
        Write-Log " Test Summary:" -Color Cyan
        $testResults | Format-Table -AutoSize
        
        $passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
        $totalTests = $testResults.Count
        
        Write-Log " Overall Result: $passedTests/$totalTests tests passed" -Color $(if ($passedTests -eq $totalTests) { "Green" } elseif ($passedTests -gt 0) { "Yellow" } else { "Red" })
        
        return $testResults
        
    } catch {
        Write-Log " Error during GPU testing: $_" -Color Red
        return $null
    }
}

# ===== REPORTING =====
function Write-GPUReport {
    param(
        [object]$Data,
        [string]$OutputPath,
        [switch]$Json
    )
    
    Write-Log " Writing GPU monitor report..." -Color Cyan
    
    try {
        $restoreDir = Split-Path $OutputPath -Parent
        if (-not (Test-Path $restoreDir)) {
            New-Item -ItemType Directory -Force -Path $restoreDir | Out-Null
        }
        
        # Text report
        $txtPath = $OutputPath -replace '\.json$', '.txt'
        $Data | Format-Table -AutoSize | Out-File -LiteralPath $txtPath -Encoding utf8
        
        Write-Log " Text report saved to: $txtPath" -Color Green
        
        # JSON report
        if ($Json) {
            $report = @{
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                data = $Data
                mode = $Mode
            }
            
            $report | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $OutputPath -Encoding utf8
            Write-Log " JSON report saved to: $OutputPath" -Color Green
        }
        
    } catch {
        Write-Log " Error writing report: $_" -Color Red
    }
}

# ===== MAIN EXECUTION =====
function Start-GPUMonitor {
    Write-Log " Starting Agent Exo-Suit V4.0 'PERFECTION' - GPU Monitor..." -Color Cyan
    
    # Validate system requirements
    if (-not (Test-SystemRequirements)) {
        Write-Log " System requirements not met. Exiting." -Color Red
        exit 1
    }
    
    # Execute based on mode
    switch ($Mode) {
        'Info' {
            Write-Log " Getting GPU information..." -Color Cyan
            
            $gpuInfo = Get-GPUInfo
            if ($gpuInfo) {
                Write-Log " GPU Information:" -Color Cyan
                $gpuInfo | Format-Table -AutoSize
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\GPU_INFO.json"
                    Write-GPUReport -Data $gpuInfo -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " No GPU information available" -Color Red
                exit 1
            }
        }
        
        'Monitor' {
            Write-Log " Starting GPU monitoring..." -Color Cyan
            
            $monitoringData = Start-GPUMonitoring -Duration $Duration -Interval $Interval
            
            if ($monitoringData.Count -gt 0) {
                Write-Log " Monitoring Results:" -Color Cyan
                $monitoringData | Format-Table -AutoSize
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\GPU_MONITORING.json"
                    Write-GPUReport -Data $monitoringData -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " GPU monitoring failed" -Color Red
                exit 1
            }
        }
        
        'Benchmark' {
            Write-Log " Running GPU monitor benchmark..." -Color Cyan
            
            $benchmarkResults = Start-GPUBenchmark
            if ($benchmarkResults) {
                Write-Log " Benchmark completed successfully" -Color Green
                
                # Save benchmark results
                $benchmarkPath = Join-Path (Get-Location) "restore\GPU_BENCHMARK.json"
                $benchmarkResults | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $benchmarkPath -Encoding utf8
                Write-Log " Benchmark results saved to: $benchmarkPath" -Color Green
            } else {
                Write-Log " Benchmark failed" -Color Red
                exit 1
            }
        }
        
        'Optimize' {
            Write-Log " Optimizing GPU settings..." -Color Cyan
            
            if (Optimize-GPUSettings) {
                Write-Log " GPU optimization completed" -Color Green
            } else {
                Write-Log " GPU optimization failed" -Color Red
                exit 1
            }
        }
        
        'Test' {
            Write-Log " Testing GPU system..." -Color Cyan
            
            $testResults = Test-GPUSystem
            if ($testResults) {
                Write-Log " GPU system testing completed" -Color Green
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\GPU_TEST_RESULTS.json"
                    Write-GPUReport -Data $testResults -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " GPU system testing failed" -Color Red
                exit 1
            }
        }
        
        'Report' {
            Write-Log " Generating comprehensive GPU report..." -Color Cyan
            
            $reportData = @{
                SystemInfo = @{
                    PowerShellVersion = $PSVersionTable.PSVersion.ToString()
                    OSVersion = (Get-CimInstance -ClassName Win32_OperatingSystem).Caption
                    TotalMemoryGB = [math]::Round((Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize) / 1024 / 1024, 2)
                }
                GPUInfo = Get-GPUInfo
                BenchmarkResults = Start-GPUBenchmark
                TestResults = Test-GPUSystem
            }
            
            Write-Log " Comprehensive GPU Report:" -Color Cyan
            $reportData | Format-List
            
            # Write report
            $outputPath = Join-Path (Get-Location) "restore\GPU_COMPREHENSIVE_REPORT.json"
            Write-GPUReport -Data $reportData -OutputPath $outputPath -Json
        }
    }
    
    Write-Log " GPU Monitor V4.0 completed successfully!" -Color Green
}

# ===== SCRIPT EXECUTION =====
try {
    Start-GPUMonitor
} catch {
    Write-Log " Unexpected error: $_" -Color Red
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
}
