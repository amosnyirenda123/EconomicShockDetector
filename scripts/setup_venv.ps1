# Create a project venv with Python 3.11 (required for scikit-learn / scipy wheels).
# Usage (from repo root):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   .\scripts\setup_venv.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "Project root: $Root"

$py311 = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
if (-not $py311) {
    Write-Error "Python 3.11 not found. Install from https://www.python.org/downloads/ or use Docker."
    exit 1
}

Write-Host "Using Python: $py311"
Set-Location $Root

if (Test-Path ".venv") {
    Write-Host "Removing existing .venv ..."
    Remove-Item -Recurse -Force ".venv"
}

& py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host ""
Write-Host "Done. Activate with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
