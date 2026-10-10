# Start BookShop (waitress, single process) in the background (DEC-013, MIG-RULE-022).
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1 [-ConfigPath <file>]
# The BOOKSHOP_* environment variables must be set, or provided by the optional config file.
param([string]$ConfigPath)
$ErrorActionPreference = 'Stop'

if ($ConfigPath) { . $ConfigPath }
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run 'py -3.12 -m venv .venv' and install requirements.txt first."
}
if (-not $env:BOOKSHOP_DATA_DIR) { throw 'BOOKSHOP_DATA_DIR is not set.' }

$runDir = Join-Path $env:BOOKSHOP_DATA_DIR 'run'
$logDir = Join-Path $env:BOOKSHOP_DATA_DIR 'logs'
New-Item -ItemType Directory -Force -Path $runDir, $logDir | Out-Null
$pidFile = Join-Path $runDir 'bookshop.pid'

if (Test-Path $pidFile) {
    $old = Get-Content $pidFile | Select-Object -First 1
    if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
        throw "BookShop is already running (PID $old)."
    }
    Remove-Item $pidFile -Force
}

$env:PYTHONUTF8 = '1'

# Pre-flight check in this console, so configuration errors are visible before going to the background.
& $python -m bookshop_web check
if ($LASTEXITCODE -ne 0) { throw "Configuration check failed (exit code $LASTEXITCODE)." }

# Start hidden via ShellExecute: the service inherits no handles from the caller, so a caller that
# captures this script's output through pipes is not kept waiting. Runtime logs: logs\bookshop.log.
$proc = Start-Process -FilePath $python -ArgumentList '-m', 'bookshop_web', 'serve' -WorkingDirectory $root `
    -WindowStyle Hidden -PassThru
Set-Content -Path $pidFile -Value $proc.Id -Encoding ascii

$port = 8080
if ($env:BOOKSHOP_PORT) { $port = [int]$env:BOOKSHOP_PORT }
$address = '127.0.0.1'
if ($env:BOOKSHOP_HOST -and $env:BOOKSHOP_HOST -ne '0.0.0.0') { $address = $env:BOOKSHOP_HOST }

$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
    if ($proc.HasExited) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        throw "BookShop exited with code $($proc.ExitCode). See $(Join-Path $logDir 'bookshop.log')."
    }
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($address, $port)
        $client.Close()
        Write-Output "BookShop started (PID $($proc.Id)): http://${address}:$port/BookShop/"
        exit 0
    } catch {
        Start-Sleep -Milliseconds 300
    }
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
throw 'BookShop did not start listening within 30 seconds.'
