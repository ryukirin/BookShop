param(
    [string]$ConfigPath,
    [int]$TimeoutSeconds = 15
)
$ErrorActionPreference = 'Stop'
if ($ConfigPath) {
    $resolvedConfig = (Resolve-Path -LiteralPath $ConfigPath).Path
    . $resolvedConfig
}
if (-not $env:BOOKSHOP_DATABASE_PATH) { throw '缺少 BOOKSHOP_DATABASE_PATH' }
$database = [System.IO.Path]::GetFullPath($env:BOOKSHOP_DATABASE_PATH)
$runDirectory = [System.IO.Path]::GetDirectoryName($database)
$pidFile = Join-Path $runDirectory 'bookshop.pid'
$stopFile = Join-Path $runDirectory 'bookshop.stop'
if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) { throw '未找到 BookShop PID 文件；请检查日志' }
$targetPid = [int](Get-Content -Raw -LiteralPath $pidFile)
[System.IO.File]::WriteAllText($stopFile, 'stop', [System.Text.Encoding]::ASCII)
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (-not (Get-Process -Id $targetPid -ErrorAction SilentlyContinue)) {
        Write-Output "BookShop 已优雅停止，PID=$targetPid"
        return
    }
    Start-Sleep -Milliseconds 200
}
throw "等待 BookShop 优雅停止超时，PID=$targetPid；未强制终止，请人工诊断"
