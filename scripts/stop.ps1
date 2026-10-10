# Stop the BookShop process started by scripts\start.ps1 (DEC-013).
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop.ps1 [-ConfigPath <file>]
param([string]$ConfigPath)
$ErrorActionPreference = 'Stop'

if ($ConfigPath) { . $ConfigPath }
if (-not $env:BOOKSHOP_DATA_DIR) { throw 'BOOKSHOP_DATA_DIR is not set.' }

$pidFile = Join-Path (Join-Path $env:BOOKSHOP_DATA_DIR 'run') 'bookshop.pid'
if (-not (Test-Path $pidFile)) {
    Write-Output 'BookShop is not running (no PID file).'
    exit 0
}
$id = Get-Content $pidFile | Select-Object -First 1
$proc = Get-Process -Id $id -ErrorAction SilentlyContinue
if ($proc) {
    Stop-Process -Id $id -Force
    $proc.WaitForExit(10000) | Out-Null
}
Remove-Item $pidFile -Force
Write-Output "BookShop stopped (PID $id)."
