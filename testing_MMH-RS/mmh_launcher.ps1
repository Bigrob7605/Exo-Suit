# =====================================================================
#  MMH-RS Universal Launcher v1.2.5  (PowerShell edition – upgraded)
#  Universal Digital DNA Format
# =====================================================================
#  • Same menus, same colours, same behaviour
#  • Cleaner code, reusable helpers, input validation
# =====================================================================

# ---------- Colours ----------
$col = @{
    Cyan    = [ConsoleColor]::Cyan
    Green   = [ConsoleColor]::Green
    Yellow  = [ConsoleColor]::Yellow
    Blue    = [ConsoleColor]::Blue
    Magenta = [ConsoleColor]::Magenta
    White   = [ConsoleColor]::White
    Gray    = [ConsoleColor]::Gray
    Red     = [ConsoleColor]::Red
}

# ---------- Helpers ----------
function Clear-Screen { Clear-Host }

function Write-Line([string]$text, [ConsoleColor]$colour = $col.White) {
    Write-Host $text -ForegroundColor $colour
}

function Read-Validated([string]$prompt) {
    do {
        $in = Read-Host $prompt
    } while ([string]::IsNullOrWhiteSpace($in))
    return $in.Trim()
}

function Pause-AnyKey([string]$msg = "Press Enter to continue...") {
    Read-Host $msg | Out-Null
}

# ---------- Main Menu ----------
function Show-MainMenu {
    Clear-Screen
    Write-Line ""
    Write-Line "┌─────────────────────────────────────────────────────────────┐" $col.Cyan
    Write-Line "│                MMH-RS Universal Launcher                    │" $col.Cyan
    Write-Line "│              Universal Digital DNA Format                   │" $col.Cyan
    Write-Line "│                        v1.2.5                              │" $col.Cyan
    Write-Line "├─────────────────────────────────────────────────────────────┤" $col.Cyan
    Write-Line "│ 🎯 Select Launch Option:                                    │" $col.White
    Write-Line "│                                                             │" $col.White
    Write-Line "│ 1. 🚀 Quick Start (Interactive Menu)                       │" $col.Green
    Write-Line "│ 2. ⚡ Quick System Test (100MB Validation)                 │" $col.Yellow
    Write-Line "│ 3. 🔧 Comprehensive System Test (Full Validation)          │" $col.Blue
    Write-Line "│ 4. 📊 Benchmark Tiers (All 5 Tiers)                        │" $col.Magenta
    Write-Line "│ 5. 🤖 Agent System (6 Options)                             │" $col.Cyan
    Write-Line "│ 6. 🗂️  File Operations (Pack/Unpack/Verify)                │" $col.White
    Write-Line "│ 7. 🎛️  Custom Command (Direct CLI Access)                  │" $col.Gray
    Write-Line "│ 8. ℹ️  System Information                                   │" $col.Blue
    Write-Line "│ 9. 📖 About MMH-RS                                          │" $col.Green
    Write-Line "│ 0. 🚪 Exit                                                   │" $col.Red
    Write-Line "├─────────────────────────────────────────────────────────────┤" $col.Cyan
    Write-Line "│ 💡 Tip: Press Ctrl+C at any time to abort operations       │" $col.Yellow
    Write-Host "│ Enter your choice: " -NoNewline -ForegroundColor White
}

# ---------- File Operations ----------
function Show-FileOpsMenu {
    Clear-Screen
    Write-Line ""
    Write-Line "🗂️  File Operations Menu" $col.Cyan
    Write-Line "┌─────────────────────────────────────────────────────────────┐" $col.Cyan
    Write-Line "│ 🎯 Select File Operation:                                   │" $col.White
    Write-Line "│                                                             │" $col.White
    Write-Line "│ 1. 📦 Pack File                                             │" $col.Green
    Write-Line "│ 2. 📤 Unpack File                                           │" $col.Blue
    Write-Line "│ 3. ✅ Verify File Integrity                                 │" $col.Yellow
    Write-Line "│ 4. 🧪 Generate Test Data                                    │" $col.Magenta
    Write-Line "│ 0. 🔙 Back to Main Menu                                     │" $col.Red
    Write-Line "├─────────────────────────────────────────────────────────────┤" $col.Cyan
}

function Invoke-FileOps {
    do {
        Show-FileOpsMenu
        $choice = Read-Host "Enter your choice"
        switch ($choice) {
            "1" { Invoke-PackFile }
            "2" { Invoke-UnpackFile }
            "3" { Invoke-VerifyFile }
            "4" { Invoke-GenerateTestData }
            "0" { return }
            default {
                Write-Line "❌ Invalid choice. Please try again." $col.Red
                Start-Sleep 2
            }
        }
    } while ($true)
}

# ---------- File helpers ----------
function Invoke-PackFile {
    Write-Line ""
    Write-Line "📦 Pack File Operation" $col.Green
    $in  = Read-Validated "Enter input file path"
    $out = Read-Validated "Enter output file path"
    cargo run --release -- pack $in $out
    Write-Line "✅ Pack operation completed!" $col.Green
    Pause-AnyKey
}

function Invoke-UnpackFile {
    Write-Line ""
    Write-Line "📤 Unpack File Operation" $col.Blue
    $in  = Read-Validated "Enter input file path"
    $out = Read-Validated "Enter output file path"
    cargo run --release -- unpack $in $out
    Write-Line "✅ Unpack operation completed!" $col.Green
    Pause-AnyKey
}

function Invoke-VerifyFile {
    Write-Line ""
    Write-Line "✅ Verify File Integrity" $col.Yellow
    $orig = Read-Validated "Enter original file path"
    $rest = Read-Validated "Enter restored file path"
    cargo run --release -- verify $orig $rest
    Write-Line "✅ Verify operation completed!" $col.Green
    Pause-AnyKey
}

function Invoke-GenerateTestData {
    Write-Line ""
    Write-Line "🧪 Generate Test Data" $col.Magenta
    $out     = Read-Validated "Enter output file path"
    $sizeStr = Read-Validated "Enter size in MB"
    cargo run --release -- gen $out $sizeStr
    Write-Line "✅ Test data generation completed!" $col.Green
    Pause-AnyKey
}

# ---------- Custom command ----------
function Invoke-CustomCommand {
    Write-Line ""
    Write-Line "🎛️  Custom Command Access" $col.Gray
    $cmd = Read-Validated "Enter your MMH-RS command (e.g., --cpu-hdd, --about)"
    cargo run --release $cmd
    Write-Line "✅ Custom command completed!" $col.Green
    Pause-AnyKey
}

# ---------- Main loop ----------
do {
    Show-MainMenu
    $choice = Read-Host
    switch ($choice) {
        "1" {
            Write-Line ""
            Write-Line "🚀 Starting MMH-RS Interactive Menu..." $col.Green
            cargo run --release
        }
        "2" {
            Write-Line ""
            Write-Line "⚡ Running Quick System Test (100MB Validation)..." $col.Yellow
            cargo run --release -- --comprehensive-system-test
            Write-Line ""
            Write-Line "✅ Quick test completed!" $col.Green
            Pause-AnyKey
        }
        "3" {
            Write-Line ""
            Write-Line "🔧 Running Comprehensive System Test (Full Validation)..." $col.Blue
            cargo run --release -- --comprehensive-system-test
            Write-Line ""
            Write-Line "✅ Comprehensive test completed!" $col.Green
            Pause-AnyKey
        }
        "4" {
            Write-Line ""
            Write-Line "📊 Launching Benchmark Tiers Menu..." $col.Magenta
            Write-Line "🎯 This will open the interactive benchmark menu"
            Write-Line ""
            cargo run --release
        }
        "5" {
            Write-Line ""
            Write-Line "🤖 Launching Agent System..." $col.Cyan
            Write-Line "🎯 This will open the interactive agent menu"
            Write-Line ""
            cargo run --release
        }
        "6" { Invoke-FileOps }
        "7" { Invoke-CustomCommand }
        "8" {
            Write-Line ""
            Write-Line "ℹ️  System Information" $col.Blue
            cargo run --release -- --cpu-hdd
            Write-Line ""
            Write-Line "✅ System information displayed!" $col.Green
            Pause-AnyKey
        }
        "9" {
            Write-Line ""
            Write-Line "📖 About MMH-RS" $col.Green
            cargo run --release -- --about
            Write-Line ""
            Write-Line "✅ About information displayed!" $col.Green
            Pause-AnyKey
        }
        "0" {
            Write-Line ""
            Write-Line "👋 Thank you for using MMH-RS Universal Launcher!" $col.Cyan
            Write-Line "🚀 Universal Digital DNA Format - v1.2.5" $col.Cyan
            Write-Line ""
            exit
        }
        default {
            Write-Line "❌ Invalid choice. Please try again." $col.Red
            Start-Sleep 2
        }
    }
} while ($true) 