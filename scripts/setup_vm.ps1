# setup_vm.ps1 — Run once on a fresh Windows Server 2022 / Windows 10/11 VM
# to install Docker Desktop and deploy the Economic Shock Detector stack.
#
# Usage (run as Administrator in PowerShell):
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\setup_vm.ps1

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

# ── 1. Require Administrator ───────────────────────────────────────────────────
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
        ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Please run this script as Administrator."
    exit 1
}

# ── 2. Enable WSL 2 and Hyper-V (required by Docker Desktop) ──────────────────
Write-Step "Enabling WSL 2..."
wsl --install --no-distribution
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2

Write-Step "Enabling Hyper-V..."
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V /all /norestart

# ── 3. Install Chocolatey (package manager) ────────────────────────────────────
Write-Step "Installing Chocolatey..."
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    $env:Path += ";$env:AllUsersProfile\chocolatey\bin"
} else {
    Write-Host "Chocolatey already installed — skipping." -ForegroundColor Yellow
}

# ── 4. Install Docker Desktop ──────────────────────────────────────────────────
Write-Step "Installing Docker Desktop..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    choco install docker-desktop -y
    Write-Host "Docker Desktop installed. A reboot is required before continuing." -ForegroundColor Yellow
} else {
    Write-Host "Docker already installed — skipping." -ForegroundColor Yellow
}

# ── 5. Install Git ─────────────────────────────────────────────────────────────
Write-Step "Installing Git..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    choco install git -y
    $env:Path += ";$env:ProgramFiles\Git\cmd"
} else {
    Write-Host "Git already installed — skipping." -ForegroundColor Yellow
}

# ── 6. Verify ─────────────────────────────────────────────────────────────────
Write-Step "Verifying installations..."
try { docker --version }        catch { Write-Warning "Docker not yet available — reboot required." }
try { docker compose version }  catch { Write-Warning "Docker Compose not yet available — reboot required." }
git --version

# ── 7. Next steps ──────────────────────────────────────────────────────────────
Write-Host @"

============================================================
  Setup complete. Follow these steps after rebooting:
============================================================

  1. Reboot the VM:
         Restart-Computer

  2. Start Docker Desktop from the Start Menu and wait for
     the whale icon to appear in the system tray (green).

  3. Clone your project:
         git clone <your-repo-url>
         cd WorldBank

  4. Copy the example env file and fill in your secrets:
         copy .env.example .env
         notepad .env

  5. Build and start all services:
         docker compose up --build -d

  6. Open in your browser:
         Frontend  : http://localhost:8501
         API docs  : http://localhost:8000/docs

  7. To stop everything:
         docker compose down
============================================================
"@ -ForegroundColor Green

Write-Host "`nReboot now? (y/n): " -NoNewline -ForegroundColor Yellow
$reboot = Read-Host
if ($reboot -eq 'y') { Restart-Computer }