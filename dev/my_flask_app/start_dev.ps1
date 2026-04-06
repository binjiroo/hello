$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

Write-Host "[1/3] Checking port 5000..."
$listeners = netstat -ano | Select-String ":5000"
$pids = @()

foreach ($line in $listeners) {
    $parts = ($line -split "\s+") | Where-Object { $_ -ne "" }
    if ($parts.Length -ge 5 -and $parts[3] -eq "LISTENING") {
        $pids += $parts[4]
    }
}

$pids = $pids | Sort-Object -Unique

if ($pids.Count -eq 0) {
    Write-Host "No process is listening on port 5000."
} else {
    foreach ($pid in $pids) {
        Write-Host "Stopping PID $pid on port 5000..."
        Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
}

$pythonPath = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    throw "venv\Scripts\python.exe was not found."
}

Write-Host "[2/3] Starting Flask development server..."
Write-Host "    URL: http://127.0.0.1:5000/h_size/"
Write-Host "[3/3] Press Ctrl+C to stop the server."

& $pythonPath -m flask --app app:create_app run --debug --no-reload
