param(
    [string]$ConfigPath,
    [switch]$Background
)
$ErrorActionPreference = 'Stop'
if ($ConfigPath) {
    $resolvedConfig = (Resolve-Path -LiteralPath $ConfigPath).Path
    . $resolvedConfig
}
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$python = (Get-Command python -ErrorAction Stop).Source
if ($Background) {
    $process = Start-Process -FilePath $python -ArgumentList @('-m', 'bookshop_app.server') -WorkingDirectory $repo -WindowStyle Hidden -PassThru
    Write-Output "BookShop 后台进程已请求启动，PID=$($process.Id)。请检查 /BookShop/health 和日志确认。"
} else {
    Push-Location -LiteralPath $repo
    try {
        & $python -m bookshop_app.server
        if ($LASTEXITCODE -ne 0) { throw "BookShop 服务异常退出，退出码=$LASTEXITCODE" }
    } finally {
        Pop-Location
    }
}
