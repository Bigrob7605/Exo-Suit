<#
  Builds FAISS index of source + docs
#>
$ErrorActionPreference = 'Stop'

# Load environment variables
$envFile = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object {
        $key, $value = $_ -split '=', 2
        Set-Variable -Name $key -Value $value -Scope Global
    }
}

$tmp = Join-Path $env:TEMP "rag_files.txt"
Get-ChildItem -Recurse -File -Include *.py,*.js,*.ts,*.md,*.txt,*.yml,*.yaml `
  -Exclude node_modules,target,__pycache__,dist,build | % FullName | Out-File $tmp
python "$PSScriptRoot\build_index.py" --filelist $tmp
