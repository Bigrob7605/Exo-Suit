# Agent Exo-Suit V4.0 "PERFECTION" - Power Management
# Advanced power plan management with intelligent optimization and monitoring

[CmdletBinding()]
param(
    [ValidateSet('List', 'Get', 'Set', 'Create', 'Delete', 'Optimize', 'Monitor', 'Benchmark')]
    [string]$Mode = 'List',
    
    [Parameter(Mandatory=$false)]
    [string]$PlanName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$PlanGuid = "",
    
    [switch]$Force,
    
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
        $logPath = Join-Path (Get-Location) "power_management_v4.log"
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
    
    # Check if running as Administrator
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Log " Not running as Administrator. Some operations may fail." -Color Yellow
    } else {
        Write-Log " Running as Administrator" -Color Green
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize
    $memoryGB = [math]::Round($memory / 1024 / 1024, 2)
    Write-Log " Available memory: $memoryGB GB" -Color Green
    
    return $true
}

# ===== POWER PLAN MANAGEMENT =====
function Get-PowerPlans {
    Write-Log " Retrieving power plans..." -Color Cyan
    
    try {
        $plans = @()
        
        # Get all power schemes
        $schemes = powercfg /list 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            foreach ($line in $schemes) {
                if ($line -match 'Power Scheme GUID: ([a-f0-9\-]+) \((.+?)\)') {
                    $guid = $matches[1]
                    $name = $matches[2]
                    
                    # Get additional details
                    $details = powercfg /query $guid 2>$null
                    
                    $plan = @{
                        Guid = $guid
                        Name = $name
                        IsActive = $false
                        Description = ""
                        Source = ""
                    }
                    
                    # Check if this is the active plan
                    $activePlan = powercfg /getactivescheme 2>$null
                    if ($activePlan -match $guid) {
                        $plan.IsActive = $true
                    }
                    
                    # Extract description if available
                    if ($details -match 'Description:\s*(.+)') {
                        $plan.Description = $matches[1].Trim()
                    }
                    
                    $plans += $plan
                }
            }
            
            Write-Log " Retrieved $($plans.Count) power plans" -Color Green
            return $plans
        } else {
            Write-Log " Failed to retrieve power plans" -Color Red
            return @()
        }
        
    } catch {
        Write-Log " Error retrieving power plans: $_" -Color Red
        return @()
    }
}

function Get-PowerPlanDetails {
    param([string]$PlanGuid)
    
    Write-Log " Getting power plan details for: $PlanGuid" -Color Cyan
    
    try {
        if ([string]::IsNullOrEmpty($PlanGuid)) {
            Write-Log " Plan GUID is required" -Color Red
            return $null
        }
        
        $details = powercfg /query $PlanGuid 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            $planDetails = @{
                Guid = $PlanGuid
                Settings = @()
                SubGroups = @()
            }
            
            $currentSubGroup = ""
            $currentSetting = ""
            
            foreach ($line in $details) {
                if ($line -match 'Subgroup GUID: ([a-f0-9\-]+) \((.+?)\)') {
                    $currentSubGroup = $matches[2]
                    $planDetails.SubGroups += $currentSubGroup
                } elseif ($line -match 'Power Setting GUID: ([a-f0-9\-]+) \((.+?)\)') {
                    $currentSetting = $matches[2]
                } elseif ($line -match 'Current AC Power Setting Index:\s*(\d+)') {
                    $acValue = $matches[1]
                    $planDetails.Settings += @{
                        Name = $currentSetting
                        SubGroup = $currentSubGroup
                        ACValue = $acValue
                        DCValue = ""
                    }
                } elseif ($line -match 'Current DC Power Setting Index:\s*(\d+)') {
                    $dcValue = $matches[1]
                    # Update the last setting with DC value
                    if ($planDetails.Settings.Count -gt 0) {
                        $planDetails.Settings[-1].DCValue = $dcValue
                    }
                }
            }
            
            Write-Log " Retrieved details for power plan" -Color Green
            return $planDetails
        } else {
            Write-Log " Failed to get power plan details" -Color Red
            return $null
        }
        
    } catch {
        Write-Log " Error getting power plan details: $_" -Color Red
        return $null
    }
}

function Set-ActivePowerPlan {
    param([string]$PlanGuid)
    
    Write-Log " Setting active power plan..." -Color Cyan
    
    try {
        if ([string]::IsNullOrEmpty($PlanGuid)) {
            Write-Log " Plan GUID is required" -Color Red
            return $false
        }
        
        $result = powercfg /setactive $PlanGuid 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log " Power plan activated successfully" -Color Green
            return $true
        } else {
            Write-Log " Failed to activate power plan: $result" -Color Red
            return $false
        }
        
    } catch {
        Write-Log " Error setting active power plan: $_" -Color Red
        return $false
    }
}

function New-PowerPlan {
    param([string]$PlanName, [string]$BasePlanGuid = "381b4222-f694-41f0-9685-ff5bb260df2e")
    
    Write-Log " Creating new power plan..." -Color Cyan
    
    try {
        if ([string]::IsNullOrEmpty($PlanName)) {
            Write-Log " Plan name is required" -Color Red
            return $null
        }
        
        # Create new power plan
        $result = powercfg /duplicatescheme $BasePlanGuid $PlanName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            # Extract the new GUID from the result
            if ($result -match 'Power Scheme GUID: ([a-f0-9\-]+)') {
                $newGuid = $matches[1]
                Write-Log " Power plan created successfully: $newGuid" -Color Green
                return $newGuid
            } else {
                Write-Log " Power plan created but GUID not found in output" -Color Yellow
                return $true
            }
        } else {
            Write-Log " Failed to create power plan: $result" -Color Red
            return $null
        }
        
    } catch {
        Write-Log " Error creating power plan: $_" -Color Red
        return $null
    }
}

function Remove-PowerPlan {
    param([string]$PlanGuid, [switch]$Force)
    
    Write-Log " Removing power plan..." -Color Cyan
    
    try {
        if ([string]::IsNullOrEmpty($PlanGuid)) {
            Write-Log " Plan GUID is required" -Color Red
            return $false
        }
        
        # Check if this is the active plan
        $activePlan = powercfg /getactivescheme 2>$null
        if ($activePlan -match $PlanGuid) {
            if (-not $Force) {
                Write-Log " Cannot remove active power plan. Use -Force to override." -Color Red
                return $false
            } else {
                Write-Log " Removing active power plan..." -Color Yellow
            }
        }
        
        $result = powercfg /deletescheme $PlanGuid 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log " Power plan removed successfully" -Color Green
            return $true
        } else {
            Write-Log " Failed to remove power plan: $result" -Color Red
            return $false
        }
        
    } catch {
        Write-Log " Error removing power plan: $_" -Color Red
        return $false
    }
}

# ===== POWER OPTIMIZATION =====
function Optimize-PowerPlan {
    param([string]$PlanGuid, [string]$OptimizationType = "Balanced")
    
    Write-Log " Optimizing power plan..." -Color Cyan
    
    try {
        if ([string]::IsNullOrEmpty($PlanGuid)) {
            Write-Log " Plan GUID is required" -Color Red
            return $false
        }
        
        $optimizations = @{}
        
        switch ($OptimizationType) {
            "Performance" {
                Write-Log " Applying performance optimizations..." -Color Cyan
                
                # CPU performance
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 100 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 100 2>$null
                
                # Minimum processor state
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 100 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 100 2>$null
                
                # System cooling policy
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 94d3a615-a899-4ac5-ae2b-e4d8f634196f 1 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 94d3a615-a899-4ac5-ae2b-e4d8f634196f 1 2>$null
                
                $optimizations.Performance = $true
            }
            
            "PowerSaver" {
                Write-Log " Applying power saver optimizations..." -Color Cyan
                
                # CPU performance
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 5 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 5 2>$null
                
                # Minimum processor state
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 5 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 5 2>$null
                
                # System cooling policy
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 94d3a615-a899-4ac5-ae2b-e4d8f634196f 2 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 94d3a615-a899-4ac5-ae2b-e4d8f634196f 2 2>$null
                
                $optimizations.PowerSaver = $true
            }
            
            "Balanced" {
                Write-Log " Applying balanced optimizations..." -Color Cyan
                
                # CPU performance
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 50 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6f93-4227-ad87-e9a3feec08d1 50 2>$null
                
                # Minimum processor state
                powercfg /setacvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 50 2>$null
                powercfg /setdcvalueindex $PlanGuid 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 50 2>$null
                
                $optimizations.Balanced = $true
            }
        }
        
        Write-Log " Power plan optimization completed" -Color Green
        return $true
        
    } catch {
        Write-Log " Error optimizing power plan: $_" -Color Red
        return $false
    }
}

# ===== POWER MONITORING =====
function Start-PowerMonitoring {
    param([int]$Duration = 60)
    
    Write-Log " Starting power monitoring..." -Color Cyan
    
    try {
        $monitoringData = @()
        $startTime = Get-Date
        
        Write-Log " Monitoring power consumption for $Duration seconds..." -Color Cyan
        
        for ($i = 0; $i -lt $Duration; $i++) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            
            # Get current power plan
            $activePlan = powercfg /getactivescheme 2>$null
            $currentPlan = if ($activePlan -match 'Power Scheme GUID: ([a-f0-9\-]+) \((.+?)\)') { $matches[2] } else { "Unknown" }
            
            # Get battery status if available
            $battery = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue
            $batteryStatus = if ($battery) { 
                if ($battery.BatteryStatus -eq 1) { "Discharging" }
                elseif ($battery.BatteryStatus -eq 2) { "AC Power" }
                else { "Unknown" }
            } else { "No Battery" }
            
            # Get CPU usage
            $cpuUsage = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1).CounterSamples[0].CookedValue
            
            $dataPoint = @{
                Timestamp = $timestamp
                PowerPlan = $currentPlan
                BatteryStatus = $batteryStatus
                CPUUsage = [math]::Round($cpuUsage, 2)
            }
            
            $monitoringData += $dataPoint
            
            # Display current status
            Write-Host " $timestamp | Plan: $currentPlan | Battery: $batteryStatus | CPU: $($dataPoint.CPUUsage)%" -ForegroundColor Cyan
            
            Start-Sleep -Seconds 1
        }
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-Log " Power monitoring completed in $([math]::Round($duration, 2)) seconds" -Color Green
        
        return $monitoringData
        
    } catch {
        Write-Log " Error during power monitoring: $_" -Color Red
        return @()
    }
}

# ===== BENCHMARKING =====
function Start-PowerBenchmark {
    Write-Log " Starting Power Management V4.0 benchmark..." -Color Cyan
    
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        
        # Test power plan retrieval
        $plans = Get-PowerPlans
        $retrievalTime = $sw.Elapsed.TotalMilliseconds
        
        # Test power plan details
        $sw.Restart()
        if ($plans.Count -gt 0) {
            $details = Get-PowerPlanDetails -PlanGuid $plans[0].Guid
            $detailsTime = $sw.Elapsed.TotalMilliseconds
        } else {
            $detailsTime = 0
        }
        
        $sw.Stop()
        
        $results = @{
            power_plan_retrieval_ms = [math]::Round($retrievalTime, 2)
            power_plan_details_ms = [math]::Round($detailsTime, 2)
            total_time_ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
            power_plans_found = $plans.Count
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

# ===== REPORTING =====
function Write-PowerReport {
    param(
        [object]$Data,
        [string]$OutputPath,
        [switch]$Json
    )
    
    Write-Log " Writing power management report..." -Color Cyan
    
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
function Start-PowerManagement {
    Write-Log " Starting Agent Exo-Suit V4.0 'PERFECTION' - Power Management..." -Color Cyan
    
    # Validate system requirements
    if (-not (Test-SystemRequirements)) {
        Write-Log " System requirements not met. Exiting." -Color Red
        exit 1
    }
    
    # Execute based on mode
    switch ($Mode) {
        'List' {
            Write-Log " Listing power plans..." -Color Cyan
            
            $plans = Get-PowerPlans
            if ($plans.Count -gt 0) {
                Write-Log " Power Plans:" -Color Cyan
                $plans | Format-Table -AutoSize
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\POWER_PLANS.json"
                    Write-PowerReport -Data $plans -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " No power plans found" -Color Red
                exit 1
            }
        }
        
        'Get' {
            if ([string]::IsNullOrEmpty($PlanGuid)) {
                Write-Log " Plan GUID required for Get mode" -Color Red
                exit 1
            }
            
            Write-Log " Getting power plan details..." -Color Cyan
            
            $details = Get-PowerPlanDetails -PlanGuid $PlanGuid
            if ($details) {
                Write-Log " Power Plan Details:" -Color Cyan
                $details | Format-List
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\POWER_PLAN_DETAILS.json"
                    Write-PowerReport -Data $details -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " Failed to get power plan details" -Color Red
                exit 1
            }
        }
        
        'Set' {
            if ([string]::IsNullOrEmpty($PlanGuid)) {
                Write-Log " Plan GUID required for Set mode" -Color Red
                exit 1
            }
            
            Write-Log " Setting active power plan..." -Color Cyan
            
            if (Set-ActivePowerPlan -PlanGuid $PlanGuid) {
                Write-Log " Power plan activated successfully" -Color Green
            } else {
                Write-Log " Failed to activate power plan" -Color Red
                exit 1
            }
        }
        
        'Create' {
            if ([string]::IsNullOrEmpty($PlanName)) {
                Write-Log " Plan name required for Create mode" -Color Red
                exit 1
            }
            
            Write-Log " Creating new power plan..." -Color Cyan
            
            $newGuid = New-PowerPlan -PlanName $PlanName
            if ($newGuid) {
                Write-Log " Power plan created successfully: $newGuid" -Color Green
            } else {
                Write-Log " Failed to create power plan" -Color Red
                exit 1
            }
        }
        
        'Delete' {
            if ([string]::IsNullOrEmpty($PlanGuid)) {
                Write-Log " Plan GUID required for Delete mode" -Color Red
                exit 1
            }
            
            Write-Log " Deleting power plan..." -Color Cyan
            
            if (Remove-PowerPlan -PlanGuid $PlanGuid -Force:$Force) {
                Write-Log " Power plan deleted successfully" -Color Green
            } else {
                Write-Log " Failed to delete power plan" -Color Red
                exit 1
            }
        }
        
        'Optimize' {
            if ([string]::IsNullOrEmpty($PlanGuid)) {
                Write-Log " Plan GUID required for Optimize mode" -Color Red
                exit 1
            }
            
            Write-Log " Optimizing power plan..." -Color Cyan
            
            if (Optimize-PowerPlan -PlanGuid $PlanGuid) {
                Write-Log " Power plan optimization completed" -Color Green
            } else {
                Write-Log " Failed to optimize power plan" -Color Red
                exit 1
            }
        }
        
        'Monitor' {
            Write-Log " Starting power monitoring..." -Color Cyan
            
            $monitoringData = Start-PowerMonitoring -Duration 30
            
            if ($monitoringData.Count -gt 0) {
                Write-Log " Monitoring Results:" -Color Cyan
                $monitoringData | Format-Table -AutoSize
                
                # Write report if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\POWER_MONITORING.json"
                    Write-PowerReport -Data $monitoringData -OutputPath $outputPath -Json
                }
            } else {
                Write-Log " Power monitoring failed" -Color Red
                exit 1
            }
        }
        
        'Benchmark' {
            Write-Log " Running power management benchmark..." -Color Cyan
            
            $benchmarkResults = Start-PowerBenchmark
            if ($benchmarkResults) {
                Write-Log " Benchmark completed successfully" -Color Green
                
                # Save benchmark results
                $benchmarkPath = Join-Path (Get-Location) "restore\POWER_BENCHMARK.json"
                $benchmarkResults | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $benchmarkPath -Encoding utf8
                Write-Log " Benchmark results saved to: $benchmarkPath" -Color Green
            } else {
                Write-Log " Benchmark failed" -Color Red
                exit 1
            }
        }
    }
    
    Write-Log " Power Management V4.0 completed successfully!" -Color Green
}

# ===== SCRIPT EXECUTION =====
try {
    Start-PowerManagement
} catch {
    Write-Log " Unexpected error: $_" -Color Red
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
}
