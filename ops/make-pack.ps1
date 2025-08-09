param(
    [Parameter(Mandatory=$true)]
    [string]$proj,
    
    [Parameter(Mandatory=$true)]
    [string]$out
)

# ===== V1.1 ENHANCEMENTS =====
# 7) Quick security / ownership scan
$owners = @{}
$ownersFile = Join-Path $proj 'OWNERS.md'
if (Test-Path $ownersFile) {
    switch -Regex -File $ownersFile {
        '^\s*\*\s*(?<path>[\w\/\-\.\*]+)\s*\|\s*(?<owner>[\w\s,@\-]+)\s*$' {
            $owners[$Matches.path.Trim()] = $Matches.owner.Trim()
        }
    }
}
$ownershipReport = $owners.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{ Path = $_.Key; Owner = $_.Value }
}
$ownershipReport | ConvertTo-Json -Depth 2 | Out-File (Join-Path $out 'ownership.json') -Encoding utf8

# 8) Dependency freshness (npm / cargo / pip) quick view
$lockFiles = @(
    @{ Name='package-lock.json'; Type='npm'   },
    @{ Name='pnpm-lock.yaml';    Type='pnpm'  },
    @{ Name='yarn.lock';         Type='yarn'  },
    @{ Name='Cargo.lock';        Type='cargo' },
    @{ Name='requirements.txt';  Type='pip'   },
    @{ Name='poetry.lock';       Type='pip'   }
)

$freshness = foreach ($lf in $lockFiles) {
    $path = Join-Path $proj $lf.Name
    if (Test-Path $path) {
        $age = ((Get-Date) - (Get-Item $path).LastWriteTime).TotalDays
        [pscustomobject]@{
            Type   = $lf.Type
            Path   = $path
            AgeDays = [math]::Round($age, 1)
        }
    }
}
$freshness | ConvertTo-Json -Depth 2 | Out-File (Join-Path $out 'lock_age.json') -Encoding utf8
