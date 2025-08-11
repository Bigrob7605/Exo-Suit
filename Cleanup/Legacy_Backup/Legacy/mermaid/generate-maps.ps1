<#
  Auto-produces dependency & route diagrams
#>
$ErrorActionPreference='Continue'
if (Test-Path package.json) {
  npm ls --json 2>$null | Out-File mermaid/dep.json
  python mermaid\dep2mmd.py
}
