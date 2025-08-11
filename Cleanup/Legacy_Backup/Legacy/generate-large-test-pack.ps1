# Generate Large Test Pack for GPU-RAG-V4.0 Stress Testing
param(
    [string]$OutputPath = ".\large-test-pack",
    [int]$FileCount = 50
)

Write-Host "Generating Large Test Pack for GPU-RAG-V4.0 Stress Testing" -ForegroundColor Green
Write-Host "Output: $OutputPath" -ForegroundColor Cyan
Write-Host "File Count: $FileCount" -ForegroundColor Cyan

# Create output directory
if (Test-Path $OutputPath) {
    Remove-Item $OutputPath -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputPath | Out-Null

# Generate files
for ($i = 1; $i -le $FileCount; $i++) {
    # Select file type
    $ext = @('py', 'js', 'md', 'json', 'txt') | Get-Random
    
    # Generate filename
    $filename = "large_test_$($i.ToString('000')).$ext"
    $filepath = Join-Path $OutputPath $filename
    
    # Generate content based on file type
    switch ($ext) {
        'py' {
            $content = "# Python Test File $i`n"
            $content += "import os`nimport sys`nimport json`nimport torch`nimport numpy as np`n"
            $content += "from typing import List, Dict, Optional`n`n"
            $content += "class TestClass${i}:`n"
            $content += "    def __init__(self, name: str):`n"
            $content += "        self.name = name`n"
            $content += "        self.data = []`n`n"
            $content += "    def add_data(self, item: str) -> None:`n"
            $content += "        self.data.append(item)`n"
            $content += "        print(f'Added: {item} - Success')`n`n"
            $content += "    def process_data(self) -> List[str]:`n"
            $content += "        return [f'Processed: {item}' for item in self.data]`n`n"
            $content += "if __name__ == '__main__':`n"
            $content += "    test = TestClass${i}('TestInstance${i}')`n"
            $content += "    test.add_data('sample_data_${i}')`n"
            $content += "    test.add_data('test_data_validation')`n"
            $content += "    print('Test completed successfully!')`n"
        }
        'js' {
            $content = "// JavaScript Test File $i`n"
            $content += "class TestModule${i} {`n"
            $content += "    constructor(name) {`n"
            $content += "        this.name = name;`n"
            $content += "        this.data = [];`n"
            $content += "    }`n`n"
            $content += "    addData(item) {`n"
            $content += "        this.data.push({`n"
            $content += "            id: Date.now(),`n"
            $content += "            content: item,`n"
            $content += "            timestamp: new Date().toISOString()`n"
            $content += "        });`n"
            $content += "        console.log('Added data: ' + item + ' - Success');`n"
            $content += "    }`n"
            $content += "}`n`n"
            $content += "const testModule = new TestModule${i}('StressTest${i}');`n"
            $content += "for (let i = 0; i < 100; i++) {`n"
            $content += "    testModule.addData('stress_test_data_' + i + '_data');`n"
            $content += "}`n"
            $content += "console.log('Stress test completed!');`n"
        }
        'md' {
            $content = "# Large Test Document $i`n`n"
            $content += "This is a comprehensive test document for GPU-RAG-V4.0.`n"
            $content += "Generated document ID: TEST-$($i.ToString('000'))`n"
            $content += "Status: Ready`n"
        }
        'json' {
            $content = "{`n"
            $content += "    `"test_file_id`": `"$($i.ToString('000'))`",`n"
            $content += "    `"status`": `"ready_for_execution`",`n"
            $content += "    `"tags`": [`"test`", `"stress`", `"gpu`"]`n"
            $content += "}`n"
        }
        'txt' {
            $content = "LARGE TEST PAYLOAD FILE $($i.ToString('000'))`n`n"
            $content += "This is a large text file for GPU-RAG-V4.0 stress testing.`n"
            $content += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
        }
    }
    
    if ($ext -in @('md', 'txt')) {
        $additionalContent = "`n" + ("Extra line for file $i - additional content " * (Get-Random -Minimum 5 -Maximum 20))
        $content += $additionalContent
    }
    
    $content | Out-File -FilePath $filepath -Encoding UTF8
    Write-Host "Generated: $filename" -ForegroundColor Green
}

Write-Host "`nLarge Test Pack Generation Complete!" -ForegroundColor Green
Write-Host "Total Files: $FileCount" -ForegroundColor Cyan
Write-Host "Output Directory: $OutputPath" -ForegroundColor Cyan
Write-Host "`nReady for GPU-RAG-V4.0 Stress Testing!" -ForegroundColor Yellow
