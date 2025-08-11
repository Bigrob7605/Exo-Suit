# Quick V4 Component Test - Identify Issues for 100% Operation
Write-Host "=== AGENT EXO-SUIT V4.0 QUICK TEST ===" -ForegroundColor Cyan
Write-Host "Testing each component to identify issues..." -ForegroundColor Yellow
Write-Host ""

$components = @(
    @{Name="Emoji Sentinel V4.0"; Script="ops\emoji-sentinel-v4.ps1"; Args="-Path 'test-emoji-pack'"},
    @{Name="Symbol Indexer V4.0"; Script="ops\Symbol-Indexer-V4.ps1"; Args="-Path 'test-emoji-pack'"},
    @{Name="Drift Guard V4.0"; Script="ops\Drift-Guard-V4.ps1"; Args="-Path 'test-emoji-pack'"},
    @{Name="Import Indexer V4.0"; Script="ops\Import-Indexer-V4.ps1"; Args="-Path 'test-emoji-pack'"},
    @{Name="Placeholder Scanner V4.0"; Script="ops\Placeholder-Scanner-V4.ps1"; Args="-Path 'test-emoji-pack'"},
    @{Name="Project Health Scanner V4.0"; Script="ops\Project-Health-Scanner-V4.ps1"; Args="-ProjectPath 'test-emoji-pack' -OutputPath 'restore'"},
    @{Name="Scan Secrets V4.0"; Script="ops\Scan-Secrets-V4.ps1"; Args="-Root 'test-emoji-pack'"}
)

foreach ($comp in $components) {
    Write-Host "Testing: $($comp.Name)" -ForegroundColor White
    try {
        $result = & pwsh -ExecutionPolicy Bypass -File $comp.Script $comp.Args.Split(' ')
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {
            Write-Host "  ✓ PASSED (Exit: $LASTEXITCODE)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ FAILED (Exit: $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== QUICK TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host "Check results above to identify components needing fixes." -ForegroundColor Yellow
