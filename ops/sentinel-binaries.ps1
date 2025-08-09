param(
  [int]$maxSizeMB = 50,
  [string[]]$allow = @('.png','.jpg','.jpeg','.webp','.gif','.ico','.ttf','.woff','.woff2')
)

$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
New-Item -ItemType Directory -Force -Path 'restore' | Out-Null

$binaryExt = @('.exe','.dll','.so','.dylib','.bin','.pak','.mp4','.mkv','.zip','.7z','.rar','.iso','.pdf')
$allExt = $binaryExt + $allow

$tracked = git ls-files -z 2>$null | ForEach-Object {$_} | Where-Object {$_ -ne ''} 
if (-not $tracked) { $tracked = (Get-ChildItem -Recurse -File | % FullName) }

$issues = @()
foreach ($p in $tracked) {
  $ext = [IO.Path]::GetExtension($p).ToLower()
  $sizeMB = 0
  try { $sizeMB = [math]::Round((Get-Item $p).Length / 1MB, 2) } catch { continue }
  if ($sizeMB -ge $maxSizeMB -and -not ($allow -contains $ext)) {
    $issues += [pscustomobject]@{ file=$p; sizeMB=$sizeMB; reason="oversize" }
  } elseif ($binaryExt -contains $ext) {
    $issues += [pscustomobject]@{ file=$p; sizeMB=$sizeMB; reason="binary" }
  }
}

$path = 'restore/BINARY_GUARD.json'
$issues | ConvertTo-Json -Depth 3 | Out-File $path -Encoding utf8
if ($issues.Count -gt 0) {
  Write-Error "Binary/oversize files detected. See $path"
  exit 4
} else {
  Write-Host "Binary guard clean."
}
