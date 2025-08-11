# Debug script to test emoji detection
Write-Host "Testing emoji detection logic..." -ForegroundColor Cyan

# Test the current detection method
function Test-EmojiInString {
    param([string]$Text)
    
    Write-Host "Testing string: '$Text'" -ForegroundColor Yellow
    Write-Host "String length: $($Text.Length)" -ForegroundColor White
    
    foreach ($char in $Text.ToCharArray()) {
        $codePoint = [int][char]$char
        $hexCode = "0x{0:X4}" -f $codePoint
        
        Write-Host "Char: '$char' - Code: $codePoint ($hexCode)" -ForegroundColor White
        
        if ($codePoint -gt 0xFFFF) {
            Write-Host "  -> FLAGGED AS EMOJI!" -ForegroundColor Red
        } else {
            Write-Host "  -> Not emoji" -ForegroundColor Green
        }
    }
}

# Test some sample strings
$testStrings = @(
    "Hello World",
    "Test with emoji ",
    "PowerShell script",
    "File: Git-Drift.ps1",
    "Status: FULLY OPERATIONAL"
)

foreach ($testString in $testStrings) {
    Write-Host "`n" + "="*50 -ForegroundColor Cyan
    Test-EmojiInString $testString
}
