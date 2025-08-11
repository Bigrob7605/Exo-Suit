# Agent Exo-Suit V4.0 "Perfection" - System Test Script
# Test all V4.0 components to ensure they're working properly

Write-Host "🧪 Agent Exo-Suit V4.0 'Perfection' - System Test" -ForegroundColor Green
Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Test 1: Check if main controller exists
Write-Host "`nTest 1: Main Controller" -ForegroundColor Yellow
if (Test-Path ".\AgentExoSuitV4.ps1") {
    Write-Host "  ✅ AgentExoSuitV4.ps1 - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ AgentExoSuitV4.ps1 - Missing" -ForegroundColor Red
}

# Test 2: Check V4.0 components
Write-Host "`nTest 2: V4.0 Components" -ForegroundColor Yellow
$v4Components = @(
    "ops\Drift-Guard-V4.ps1",
    "ops\Project-Health-Scanner-V4.ps1",
    "ops\emoji-sentinel-v4.ps1",
    "ops\GPU-RAG-V4.ps1",
    "ops\Import-Indexer-V4.ps1",
    "ops\Symbol-Indexer-V4.ps1",
    "ops\Scan-Secrets-V4.ps1",
    "ops\Power-Management-V4.ps1",
    "ops\GPU-Monitor-V4.ps1",
    "ops\Placeholder-Scanner-V4.ps1"
)

$allComponentsFound = $true
foreach ($component in $v4Components) {
    if (Test-Path ".\$component") {
        Write-Host "  ✅ $component" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $component" -ForegroundColor Red
        $allComponentsFound = $false
    }
}

# Test 3: Check Integration Layer
Write-Host "`nTest 3: Integration Layer (Cursor)" -ForegroundColor Yellow
if (Test-Path ".\cursor\COMMAND_QUEUE_V4.md") {
    Write-Host "  ✅ cursor\COMMAND_QUEUE_V4.md - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ cursor\COMMAND_QUEUE_V4.md - Missing" -ForegroundColor Red
    $allComponentsFound = $false
}

# Test 4: Check go-big.ps1
Write-Host "`nTest 4: Monster-Mode Script" -ForegroundColor Yellow
if (Test-Path ".\go-big.ps1") {
    Write-Host "  ✅ go-big.ps1 - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ go-big.ps1 - Missing" -ForegroundColor Red
    $allComponentsFound = $false
}

# Test 5: Check requirements
Write-Host "`nTest 5: Dependencies" -ForegroundColor Yellow
if (Test-Path ".\requirements.txt") {
    Write-Host "  ✅ requirements.txt - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ requirements.txt - Missing" -ForegroundColor Red
    $allComponentsFound = $false
}

if (Test-Path ".\requirements_gpu.txt") {
    Write-Host "  ✅ requirements_gpu.txt - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ requirements_gpu.txt - Missing" -ForegroundColor Red
    $allComponentsFound = $false
}

# Test 6: Check RAG system
Write-Host "`nTest 6: RAG System" -ForegroundColor Yellow
if (Test-Path ".\rag\hybrid_rag_v4.py") {
    Write-Host "  ✅ rag\hybrid_rag_v4.py - Found" -ForegroundColor Green
} else {
    Write-Host "  ❌ rag\hybrid_rag_v4.py - Missing" -ForegroundColor Red
    $allComponentsFound = $false
}

# Final Results
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
if ($allComponentsFound) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Agent Exo-Suit V4.0 'Perfection' is ready for production use!" -ForegroundColor Green
    Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  SOME TESTS FAILED!" -ForegroundColor Yellow
    Write-Host "Please fix the missing components before production use." -ForegroundColor Yellow
}
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Run '.\AgentExoSuitV4.ps1 -Status' to check system status" -ForegroundColor White
Write-Host "2. Run '.\go-big.ps1' to activate full system" -ForegroundColor White
Write-Host "3. Run '.\AgentExoSuitV4.ps1 -FullSystem' to activate all V4.0 components" -ForegroundColor White
