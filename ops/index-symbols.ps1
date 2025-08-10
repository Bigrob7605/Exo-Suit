<#
.SYNOPSIS
  Builds a JSON index of code symbols (functions, classes, variables, …) across a
  source tree using ripgrep (rg).  Falls back to Select-String if rg is absent.

.EXAMPLE
  .\Index-Symbols.ps1 -Root ~/code/myproj -Language py,ts,js -OutDir ./context/latest
#>

param(
    [string] $Root      = $PWD.Path,
    [string] $OutDir    = (Join-Path $Root "context\_latest"),
    [string[]] $Language = @('py', 'js', 'ts', 'ps1', 'go', 'rs', 'c', 'cpp', 'h', 'hpp', 'cs', 'java', 'php')
)

# ------------------------------------------------------------------
# 0. Helpers
# ------------------------------------------------------------------
function Write-Step { param($Msg) Write-Host "==> $Msg" -ForegroundColor Cyan }

# Ensure output directory
$null = New-Item -ItemType Directory -Force -Path $OutDir

# Prefer rg, fall back to Select-String
$rg = if (Get-Command rg -ErrorAction SilentlyContinue) { 'rg' } else { '' }

# ------------------------------------------------------------------
# 1. Define search patterns
#    (regex => symbol kind)
# ------------------------------------------------------------------
$patternTable = @(
    # Functions
    @{ re = '^\s*(?:def\s+(?<name>\w+)\s*\(|(?:export\s+)?(?:function\s+|(?<isArrow>\w+)\s*=>)|\w+\s+\w+\s*\(.*\)\s*\{)'; kind = 'function' }

    # Classes / structs
    @{ re = '^\s*(?:class|struct|interface)\s+(?<name>\w+)'; kind = 'class' }

    # Enums
    @{ re = '^\s*(?:enum)\s+(?<name>\w+)'; kind = 'enum' }

    # Type aliases / interfaces
    @{ re = '^\s*(?:type|interface)\s+(?<name>\w+)'; kind = 'alias' }

    # Constants / variables
    @{ re = '^\s*(?:const|let|var|val)\s+(?<name>\w+)\s*[=\:]'; kind = 'variable' }
)

# ------------------------------------------------------------------
# 2. Build rg arguments
# ------------------------------------------------------------------
$typeArgs = $Language | ForEach-Object { '--type', $_ }
$rgArgs   = @('-n') + $typeArgs + ($patternTable.re -join '|')

# ------------------------------------------------------------------
# 3. Search
# ------------------------------------------------------------------
Write-Step "Searching symbols in $Root …"

$symbols = [System.Collections.Generic.List[object]]::new()

$searchCmd = if ($rg) {
    { rg $rgArgs $Root }
} else {
    {
        $regex = ($patternTable.re -join '|')
        Get-ChildItem $Root -Recurse -File |
            Where-Object { $ext = $_.Extension.TrimStart('.'); $ext -in $Language } |
            ForEach-Object {
                $file = $_.FullName
                Select-String -Path $file -Pattern $regex |
                    ForEach-Object {
                        "$($_.Path):$($_.LineNumber):$($_.Line.Trim())"
                    }
            }
    }
}

# Parse matches into structured objects
$runspacePool = [runspacefactory]::CreateRunspacePool(1, [Environment]::ProcessorCount)
$runspacePool.Open()

$jobs = @()
& $searchCmd | ForEach-Object {
    $line = $_
    $ps = [powershell]::Create().AddScript({
        param($line, $patternTable)
        
        $parts = $line.Split(':', 3)
        if ($parts.Count -lt 3) { return }

        $file = $parts[0]; $lineno = $parts[1]; $text = $parts[2].Trim()

        # Determine kind
        $kind = 'unknown'
        foreach ($pat in $patternTable) {
            if ($text -match $pat.re) {
                $kind = $pat.kind
                break
            }
        }

        # Extract symbol name
        $name = if ($text -match '(?<=^|\s)(?<name>\w+)(?=\s*[\(\=])') { $matches.name } else { 'unknown' }

        [PSCustomObject]@{
            File = $file
            Line = [int]$lineno
            Kind = $kind
            Name = $name
            Signature = $text
        }
    }).AddArgument($line).AddArgument($patternTable)
    
    $ps.RunspacePool = $runspacePool
    $jobs += @{
        PowerShell = $ps
        Handle = $ps.BeginInvoke()
    }
}

# Wait for all jobs to complete
foreach ($job in $jobs) {
    $result = $job.PowerShell.EndInvoke($job.Handle)
    if ($result) {
        $symbols.Add($result)
    }
    $job.PowerShell.Dispose()
}
$runspacePool.Close()

# ------------------------------------------------------------------
# 4. Emit JSON
# ------------------------------------------------------------------
Write-Step "Writing results …"
@{
    Symbols   = $symbols
    Languages = $Language
    Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
} | ConvertTo-Json -Depth 5 -Compress |
    Out-File (Join-Path $OutDir "symbols.json") -Encoding utf8

Write-Host "Done: $(Join-Path $OutDir 'symbols.json')" -ForegroundColor Green
