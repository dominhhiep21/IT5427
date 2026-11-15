<#
.SYNOPSIS
    Chạy dự án Olist: dựng dữ liệu, phân tích, dashboard, kiểm thử.

.DESCRIPTION
    Gói các lệnh thường dùng thành một chỗ. Tự nhận biết nhánh đang đứng để chọn
    đúng lệnh: nhánh `main` chỉ có 4 tầng pipeline và CLI `src.analytics`;
    nhánh feature có thêm tầng `stats`, tệp mô hình và tab dự đoán.

.PARAMETER Task
    menu (mặc định), setup, data, analytics, check, dashboard, test, all, stop.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run.ps1

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run.ps1 -Task all

.NOTES
    Mọi lệnh Python chạy UTF-8. Dừng ngay ở bước đỏ đầu tiên.
#>
[CmdletBinding()]
param(
    [ValidateSet('menu', 'setup', 'data', 'analytics', 'check', 'dashboard', 'test', 'all', 'stop')]
    [string]$Task = 'menu'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = '1'

# Console Windows mặc định không phải UTF-8; đặt lại để chữ tiếng Việt không bị lỗi font.
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    Write-Verbose 'Không đổi được encoding của console.'
}

$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
$Python = if (Test-Path $VenvPython) { $VenvPython } else { 'python' }

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host "==> $Text" -ForegroundColor Cyan
}

function Invoke-Py {
    param([string]$Label, [string[]]$Arguments)
    Write-Step $Label
    & $Python -X utf8 @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Bước thất bại: $Label (mã thoát $LASTEXITCODE)"
    }
}

function Get-BranchName {
    try {
        $name = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0 -and $name) { return $name.Trim() }
    } catch {
        return '(không rõ)'
    }
    return '(không rõ)'
}

function Test-StatsStage {
    $file = Join-Path $Root 'src\pipeline\stages.py'
    return (Test-Path $file) -and ((Get-Content -Raw -Path $file) -match '"stats"')
}

function Test-AnalyticsCli {
    return Test-Path (Join-Path $Root 'src\analytics\__main__.py')
}

function Get-DashboardProcesses {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*src.dashboard*' }
}

function Stop-Dashboard {
    $running = Get-DashboardProcesses
    if (-not $running) {
        Write-Host "Không có dashboard nào đang chạy." -ForegroundColor DarkGray
        return
    }
    foreach ($process in $running) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "Đã tắt tiến trình $($process.ProcessId)." -ForegroundColor Yellow
    }
}

function Show-Context {
    $branch = Get-BranchName
    $stats = if (Test-StatsStage) { 'có' } else { 'không' }
    $analytics = if (Test-AnalyticsCli) { 'có' } else { 'không' }
    Write-Host "Nhánh: $branch | tầng stats: $stats | CLI src.analytics: $analytics" -ForegroundColor DarkGray
    Write-Host "Python: $Python" -ForegroundColor DarkGray
}

function Invoke-Setup {
    if (-not (Test-Path $VenvPython)) {
        Write-Step 'Tạo môi trường .venv'
        & python -m venv --system-site-packages .venv
        if ($LASTEXITCODE -ne 0) { throw 'Không tạo được .venv (cần Python 3.13 trên PATH).' }
    }
    Invoke-Py 'Cài phụ thuộc' @('-m', 'pip', 'install', '-r', 'requirements.txt')
}

function Invoke-Data {
    Invoke-Py 'Dựng dữ liệu: mart + KPI' @('-m', 'src.pipeline', 'run', '--stage', 'all')
    if (Test-StatsStage) {
        Invoke-Py 'Sinh báo cáo phân tích + tệp mô hình' @('-m', 'src.pipeline', 'run', '--stage', 'stats')
    } else {
        Write-Host "Nhánh này không có tầng 'stats' — bỏ qua bước sinh tệp mô hình." -ForegroundColor DarkYellow
    }
}

function Invoke-Analytics {
    if (-not (Test-AnalyticsCli)) {
        Write-Host 'Nhánh này không có CLI src.analytics — bỏ qua.' -ForegroundColor DarkYellow
        return
    }
    Invoke-Py 'Phân tích + đối soát (ghi docs/ và data/reports/analysis/)' @('-m', 'src.analytics')
}

function Invoke-Check {
    if (-not (Test-AnalyticsCli)) {
        Write-Host 'Nhánh này không có cổng đối soát — bỏ qua.' -ForegroundColor DarkYellow
        return
    }
    Invoke-Py 'Đối soát chỉ số (--check)' @('-m', 'src.analytics', '--check')
}

function Invoke-Tests {
    Invoke-Py 'Bộ test nhanh' @('-m', 'pytest', '-m', 'not slow', '-q')
}

function Invoke-Dashboard {
    Stop-Dashboard
    Write-Step 'Mở dashboard'
    Write-Host 'Địa chỉ: http://127.0.0.1:8050  (Ctrl+C để dừng)' -ForegroundColor Green
    & $Python -X utf8 -m src.dashboard
}

function Invoke-All {
    Invoke-Tests
    Invoke-Data
    Invoke-Analytics
    Invoke-Check
    Write-Step 'Xong phần dữ liệu và kiểm thử'
    Write-Host 'Chạy dashboard bằng: -Task dashboard' -ForegroundColor Green
}

function Show-Menu {
    while ($true) {
        Write-Host ""
        Show-Context
        Write-Host '1. setup      - tạo .venv và cài phụ thuộc'
        Write-Host '2. data       - dựng dữ liệu (và tệp mô hình nếu nhánh có stats)'
        Write-Host '3. analytics  - phân tích + đối soát'
        Write-Host '4. check      - chỉ đối soát, lỗi thì dừng'
        Write-Host '5. test       - bộ test nhanh'
        Write-Host '6. dashboard  - mở dashboard (Ctrl+C để dừng)'
        Write-Host '7. all        - test + data + analytics + check'
        Write-Host '8. stop       - tắt dashboard đang chạy nền'
        Write-Host '0. thoát'
        $choice = Read-Host 'Chọn'
        switch ($choice) {
            '1' { Invoke-Setup }
            '2' { Invoke-Data }
            '3' { Invoke-Analytics }
            '4' { Invoke-Check }
            '5' { Invoke-Tests }
            '6' { Invoke-Dashboard }
            '7' { Invoke-All }
            '8' { Stop-Dashboard }
            '0' { return }
            default { Write-Host 'Lựa chọn không hợp lệ.' -ForegroundColor Red }
        }
    }
}

Show-Context
switch ($Task) {
    'menu' { Show-Menu }
    'setup' { Invoke-Setup }
    'data' { Invoke-Data }
    'analytics' { Invoke-Analytics }
    'check' { Invoke-Check }
    'dashboard' { Invoke-Dashboard }
    'test' { Invoke-Tests }
    'all' { Invoke-All }
    'stop' { Stop-Dashboard }
}
