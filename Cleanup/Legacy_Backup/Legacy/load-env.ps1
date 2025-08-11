# Load environment variables from .env file
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object {
        $key, $value = $_ -split '=', 2
        Set-Variable -Name $key -Value $value -Scope Global
    }
}
