Param(
  [string]$BaseReq = "requirements/base.txt",
  [string]$DevReq = "requirements/development.txt",
  [switch]$Dev
)

Write-Host "[uv] 初始化虚拟环境 (.venv)" -ForegroundColor Cyan
uv venv

Write-Host "[uv] 安装基础依赖: $BaseReq" -ForegroundColor Cyan
uv pip install -r $BaseReq

if ($Dev -and (Test-Path $DevReq)) {
  Write-Host "[uv] 安装开发依赖: $DevReq" -ForegroundColor Cyan
  uv pip install -r $DevReq
}

Write-Host "[uv] 完成。建议执行: uv python pin 3.10 以固定Python版本" -ForegroundColor Green