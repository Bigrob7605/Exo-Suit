<#
.SYNOPSIS
    Project health & security quick-scan (V1.2)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$proj,

    [Parameter(Mandatory = $true)]
    [string]$out,

    [ValidateSet('Error', 'Warning', 'Info', 'Verbose')]
    [string]$LogLevel = 'Info'
)

begin {
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'

    # ---- helpers -----------------------------------------------------------
    function Write-Log {
        param(
            [Parameter(Mandatory)][string]$Message,
            [ValidateSet('Error', 'Warning', 'Info', 'Verbose')][string]$Level = 'Info'
        )
        $colors = @{ Error = 'Red'; Warning = 'Yellow'; Info = 'Cyan'; Verbose = 'Gray' }
        if ([int]([enum]::Parse([System.Diagnostics.TraceLevel], $Level)) -le
            [int]([enum]::Parse([System.Diagnostics.TraceLevel], $LogLevel))) {
            Write-Host "[$(Get-Date -f HH:mm:ss)] $Message" -ForegroundColor $colors[$Level]
        }
    }

    function Invoke-Parallel {
        param([scriptblock]$ScriptBlock, [array]$InputObject, [int]$Throttle = 5)
        $runspacePool = [runspacefactory]::CreateRunspacePool(1, $Throttle)
        $runspacePool.Open()
        $jobs = foreach ($item in $InputObject) {
            $ps = [powershell]::Create().AddScript($ScriptBlock).AddArgument($item)
            $ps.RunspacePool = $runspacePool
            @{ Pipe = $ps; Handle = $ps.BeginInvoke() }
        }
        foreach ($j in $jobs) {
            $j.Pipe.EndInvoke($j.Handle) | Write-Output
            $j.Pipe.Dispose()
        }
        $runspacePool.Close()
    }

    # ---- paths -------------------------------------------------------------
    New-Item -ItemType Directory -Path $out -Force | Out-Null
}

process {
    Write-Log "Scanning $proj  $out" -Level Info

    # -----------------------------------------------------------------------
    # 1) Ownership (OWNERS.md + CODEOWNERS fallback)
    # -----------------------------------------------------------------------
    Write-Log "Building ownership map " -Level Verbose
    $owners = @{}
    $ownersFile = Join-Path $proj 'OWNERS.md'
    $codeOwners = @(
        (Join-Path $proj '.github/CODEOWNERS'),
        (Join-Path $proj 'CODEOWNERS')
    ) | Where-Object { Test-Path $_ }
    if (Test-Path $ownersFile) {
        switch -Regex -File $ownersFile {
            '^\s*\*\s*(?<path>[\w\/\-\.\*]+)\s*\|\s*(?<owner>[\w\s,@\-]+)\s*$' {
                $owners[$Matches.path.Trim()] = $Matches.owner.Trim()
            }
        }
    }
    elseif ($codeOwners) {
        switch -Regex -File $codeOwners[0] {
            '^\s*(?<path>[\S]+)\s+(?<owner>[@\w\-\/,]+)' {
                $owners[$Matches.path.Trim()] = $Matches.owner.Trim()
            }
        }
    }
    $owners.GetEnumerator() | ForEach-Object {
        [pscustomobject]@{ Path = $_.Key; Owner = $_.Value }
    } | ConvertTo-Json -Depth 2 | Out-File (Join-Path $out 'ownership.json')

    # -----------------------------------------------------------------------
    # 2) Lock-file freshness (parallel + signed)
    # -----------------------------------------------------------------------
    Write-Log "Measuring lock-file age " -Level Verbose
    $lockFiles = @(
        @{ Name = 'package-lock.json'; Type = 'npm' },
        @{ Name = 'pnpm-lock.yaml';    Type = 'pnpm' },
        @{ Name = 'yarn.lock';         Type = 'yarn' },
        @{ Name = 'Cargo.lock';        Type = 'cargo' },
        @{ Name = 'requirements.txt';  Type = 'pip' },
        @{ Name = 'poetry.lock';       Type = 'pip' }
    )

    $freshness = Invoke-Parallel -InputObject $lockFiles -ScriptBlock {
        param($lf)
        $path = Join-Path $using:proj $lf.Name
        if (Test-Path $path) {
            $age = ((Get-Date) - (Get-Item $path).LastWriteTime).TotalDays
            [pscustomobject]@{
                Type    = $lf.Type
                Path    = $path
                AgeDays = [math]::Round($age, 1)
            }
        }
    }
    $freshness | ConvertTo-Json -Depth 2 | Out-File (Join-Path $out 'lock_age.json')

    # -----------------------------------------------------------------------
    # 3) SBOM (npm, cargo, pip)
    # -----------------------------------------------------------------------
    Write-Log "Generating SBOMs " -Level Verbose
    $sbomDir = Join-Path $out 'sbom'
    New-Item -ItemType Directory -Path $sbomDir -Force | Out-Null

    if (Test-Path (Join-Path $proj 'package.json')) {
        try {
            npm install -g @cyclonedx/cdxgen 2>&1 | Out-Null
            cdxgen -o (Join-Path $sbomDir 'npm_sbom.json') $proj 2>&1 | Out-Null
            Write-Log "npm SBOM written" -Level Verbose
        }
        catch { Write-Log "npm SBOM failed: $_" -Level Warning }
    }

    if (Test-Path (Join-Path $proj 'Cargo.toml')) {
        try {
            cargo install cargo-cyclonedx 2>&1 | Out-Null
            Push-Location $proj
            cargo cyclonedx --format json 2>&1 | Out-Null
            Move-Item (Join-Path $proj '*.json') (Join-Path $sbomDir 'cargo_sbom.json') -Force
            Pop-Location
            Write-Log "cargo SBOM written" -Level Verbose
        }
        catch { Write-Log "cargo SBOM failed: $_" -Level Warning }
    }

    if ((Test-Path (Join-Path $proj 'requirements.txt')) -or (Get-ChildItem $proj -Filter '*.py' -Recurse -ErrorAction SilentlyContinue)) {
        try {
            pip install cyclonedx-bom 2>&1 | Out-Null
            python -m cyclonedx_py requirements -o (Join-Path $sbomDir 'pip_sbom.json') $proj 2>&1 | Out-Null
            Write-Log "pip SBOM written" -Level Verbose
        }
        catch { Write-Log "pip SBOM failed: $_" -Level Warning }
    }

    # -----------------------------------------------------------------------
    # 4) CVE scan (npm audit, cargo audit, pip-audit)
    # -----------------------------------------------------------------------
    Write-Log "Running CVE audits " -Level Verbose
    $cveDir = Join-Path $out 'cve'
    New-Item -ItemType Directory -Path $cveDir -Force | Out-Null

    if (Test-Path (Join-Path $proj 'package.json')) {
        try {
            npm audit --json 2>$null | Out-File (Join-Path $cveDir 'npm_audit.json')
            Write-Log "npm audit complete" -Level Verbose
        }
        catch { Write-Log "npm audit failed: $_" -Level Warning }
    }

    if (Test-Path (Join-Path $proj 'Cargo.toml')) {
        try {
            cargo install cargo-audit 2>&1 | Out-Null
            Push-Location $proj
            cargo audit --json 2>&1 | Out-File (Join-Path $cveDir 'cargo_audit.json')
            Pop-Location
            Write-Log "cargo audit complete" -Level Verbose
        }
        catch { Write-Log "cargo audit failed: $_" -Level Warning }
    }

    if ((Test-Path (Join-Path $proj 'requirements.txt')) -or (Get-ChildItem $proj -Filter '*.py' -Recurse -ErrorAction SilentlyContinue)) {
        try {
            pip install pip-audit 2>&1 | Out-Null
            python -m pip_audit --format=json --desc --output (Join-Path $cveDir 'pip_audit.json') $proj 2>&1 | Out-Null
            Write-Log "pip audit complete" -Level Verbose
        }
        catch { Write-Log "pip audit failed: $_" -Level Warning }
    }

    # -----------------------------------------------------------------------
    # 5) Secret-scan (gitleaks)
    # -----------------------------------------------------------------------
    Write-Log "Scanning for secrets " -Level Verbose
    $gitleaksPath = Join-Path $out 'secrets.json'
    try {
        $gitleaksExe = "$env:TEMP\gitleaks\gitleaks.exe"
        if (-not (Test-Path $gitleaksExe)) {
            if ($IsWindows) {
                $url = 'https://github.com/gitleaks/gitleaks/releases/download/v8.28.0/gitleaks_8.28.0_windows_x64.zip'
                Invoke-WebRequest $url -OutFile "$env:TEMP\gitleaks.zip"
                Expand-Archive "$env:TEMP\gitleaks.zip" "$env:TEMP\gitleaks" -Force
            }
            else {
                brew install gitleaks 2>&1 | Out-Null
            }
        }
        & $gitleaksExe detect --source $proj --report-format json --report-path $gitleaksPath 2>&1 | Out-Null
        Write-Log "gitleaks scan complete" -Level Verbose
    }
    catch { Write-Log "gitleaks scan failed: $_" -Level Warning }

    # -----------------------------------------------------------------------
    Write-Log "All done - results in $out" -Level Info
}

end {
    Write-Log "Project health scan completed successfully" -Level Info
}
