[CmdletBinding()]
param(
    [int]$maxSizeMB = 50,
    [string[]]$allow = @('.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico', '.ttf', '.woff', '.woff2')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ------------------------------------------------------------------
# 1.  PATH / CONSTANTS
# ------------------------------------------------------------------
$root = git rev-parse --show-toplevel 2>$null
if (-not $root) { $root = $PWD.Path }
$restoreDir = Join-Path $root 'restore'
$reportFile = Join-Path $restoreDir 'BINARY_GUARD.json'
New-Item -ItemType Directory -Force -Path $restoreDir | Out-Null

$binaryExt = @(
    '.exe', '.dll', '.so', '.dylib', '.bin', '.pak',
    '.mp4', '.mkv', '.zip', '.7z', '.rar', '.iso', '.pdf'
)
$blockedExt = $binaryExt + $allow

# ------------------------------------------------------------------
# 2.  FILE COLLECTION
# ------------------------------------------------------------------
$files = git ls-files -z 2>$null | ForEach-Object { [IO.Path]::Combine($root, $_) }
if (-not $files) { $files = Get-ChildItem -LiteralPath $root -File -Recurse | ForEach-Object FullName }

# ------------------------------------------------------------------
# 3.  RULE ENGINE
# ------------------------------------------------------------------
$rules = @(
    @{
        Name   = 'oversize'
        Test   = { param($f, $ext, $size)
                   $size -ge $maxSizeMB -and $allow -notcontains $ext }
    },
    @{
        Name   = 'binary'
        Test   = { param($f, $ext, $size)
                   $binaryExt -contains $ext }
    }
)

# ------------------------------------------------------------------
# 4.  SCAN
# ------------------------------------------------------------------
$issues = foreach ($f in $files) {
    $ext = [IO.Path]::GetExtension($f).ToLower()
    try {
        $size = [math]::Round((Get-Item -LiteralPath $f).Length / 1MB, 2)
    }
    catch { continue }

    foreach ($r in $rules) {
        if (& $r.Test $f $ext $size) {
            [pscustomobject]@{
                file   = $f.Substring($root.Length).TrimStart('\', '/')
                sizeMB = $size
                reason = $r.Name
            }
            break
        }
    }
}

# ------------------------------------------------------------------
# 5.  OUTPUT
# ------------------------------------------------------------------
$issues | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $reportFile -Encoding utf8

if ($issues.Count) {
    Write-Error "Binary/oversize files detected. See $reportFile"
    exit 4
}
else {
    Write-Host "Binary guard clean."
}
