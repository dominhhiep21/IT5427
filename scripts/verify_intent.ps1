# Chuỗi xác nhận bốn bước của intent (team.md > ## Deployment).
#
# Chạy: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1
# Dừng ngay ở bước đỏ đầu tiên và trả mã thoát của bước đó.
# Không bỏ bước nào vì "lần trước vẫn chạy được".

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repo

$python = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

function Invoke-Step {
    param([string]$Label, [string[]]$Arguments)

    Write-Host ""
    Write-Host "=== $Label ===" -ForegroundColor Cyan

    & $python -X utf8 @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "THAT BAI o buoc: $Label (ma $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Invoke-Step "1/4 bo test nhanh" @("-m", "pytest", "-m", "not slow")
Invoke-Step "2/4 pipeline day du" @("-m", "src.pipeline", "run", "--stage", "all")
Invoke-Step "3/4 tang stats (bao cao + tep mo hinh)" @("-m", "src.pipeline", "run", "--stage", "stats")
Invoke-Step "4/4 toan bo bo test + cong phu 80%" @(
    "-m", "pytest", "--cov=src", "--cov-fail-under=80"
)

Write-Host ""
Write-Host "=== XONG: bon buoc deu xanh ===" -ForegroundColor Green
Write-Host "Buoc 5 la mo dashboard: python -X utf8 -m src.dashboard (kiem bang mat)."
exit 0
