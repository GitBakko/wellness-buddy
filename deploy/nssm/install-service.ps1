# deploy/nssm/install-service.ps1
# Wellness Buddy — install backend as Windows service via NSSM (DEP-01)
#
# Idempotent: stops + removes existing service before re-installing.
# Requires NSSM 2.24+ on PATH and uv on PATH. Run as Administrator.
# Service runs as NT AUTHORITY\LocalService for least privilege.
#
# Usage:
#   pwsh deploy/nssm/install-service.ps1                              # remote DB (no local PG dependency)
#   pwsh deploy/nssm/install-service.ps1 -PostgresService postgresql-x64-16  # local PG dependency

[CmdletBinding()]
param(
    [string]$PostgresService = ''  # empty = remote DB on LAN, no local service dependency
)

$ErrorActionPreference = 'Stop'

$serviceName = 'WellnessBuddyAPI'
$appRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$backendDir = Join-Path $appRoot 'backend'
$logsDir = Join-Path $appRoot 'logs'
$envFile = Join-Path $backendDir '.env'

Write-Host '=== Wellness Buddy — NSSM service installer ===' -ForegroundColor Cyan
Write-Host "App root: $appRoot"
Write-Host "Backend:  $backendDir"
Write-Host "Logs:     $logsDir"

# ─── Pre-flight checks ────────────────────────────────────────────
if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found: $backendDir"
}

if (-not (Test-Path $envFile)) {
    Write-Host "WARN backend\.env not found at $envFile — service will fail to start until it exists." -ForegroundColor Yellow
}

$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssm) {
    throw 'nssm not found on PATH. Install from https://nssm.cc/ and add C:\Tools\nssm to PATH.'
}
$nssmExe = $nssm.Source

$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
    throw 'uv not found on PATH. Install via: iwr -useb https://astral.sh/uv/install.ps1 | iex'
}
$uvPath = $uv.Source
Write-Host "nssm:     $nssmExe"
Write-Host "uv:       $uvPath"

# ─── Check Administrator privilege ────────────────────────────────
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [System.Security.Principal.WindowsPrincipal]::new($currentUser)
if (-not $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'This script must be run as Administrator.'
}

# ─── Logs directory ───────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

# ─── Stop + remove existing service ───────────────────────────────
$existing = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing service '$serviceName'..." -ForegroundColor Yellow
    if ($existing.Status -eq 'Running') {
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    & $nssmExe remove $serviceName confirm | Out-Null
    Start-Sleep -Seconds 1
}

# ─── Install ─────────────────────────────────────────────────────
Write-Host "Installing service '$serviceName'..." -ForegroundColor Cyan

# Build AppParameters: uv run uvicorn ...
$appParams = "run --directory `"$backendDir`" uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log"

# Equivalent shell form: `nssm install $serviceName $uvPath`
& $nssmExe install $serviceName $uvPath | Out-Null
& $nssmExe set $serviceName AppParameters $appParams | Out-Null
& $nssmExe set $serviceName AppDirectory $backendDir | Out-Null
& $nssmExe set $serviceName DisplayName 'Wellness Buddy API' | Out-Null
& $nssmExe set $serviceName Description 'FastAPI backend per Wellness Buddy PWA. 1 Uvicorn worker, port 8000.' | Out-Null
& $nssmExe set $serviceName Start SERVICE_AUTO_START | Out-Null

# DependOnService only when local PostgreSQL service exists (skip for remote DB).
if ($PostgresService -ne '') {
    $pgService = Get-Service -Name $PostgresService -ErrorAction SilentlyContinue
    if ($pgService) {
        Write-Host "Adding service dependency: $PostgresService" -ForegroundColor Cyan
        & $nssmExe set $serviceName DependOnService $PostgresService | Out-Null
    } else {
        Write-Host "WARN: -PostgresService '$PostgresService' not found locally — skipping DependOnService" -ForegroundColor Yellow
    }
} else {
    Write-Host 'Remote DB scenario — no local PG service dependency.' -ForegroundColor DarkGray
}

# Logging: stdout + stderr -> rotated files
& $nssmExe set $serviceName AppStdout (Join-Path $logsDir 'stdout.log') | Out-Null
& $nssmExe set $serviceName AppStderr (Join-Path $logsDir 'stderr.log') | Out-Null
& $nssmExe set $serviceName AppRotateFiles 1 | Out-Null
& $nssmExe set $serviceName AppRotateOnline 1 | Out-Null
& $nssmExe set $serviceName AppRotateBytes 10485760 | Out-Null  # 10 MB

# Crash recovery
& $nssmExe set $serviceName AppExit Default Restart | Out-Null
& $nssmExe set $serviceName AppRestartDelay 5000 | Out-Null

# Run as LocalService for least privilege (DEPLOY.md threat T-DEPLOY-01).
# If file ACLs need elevated access, switch to a dedicated service account
# (NT SERVICE\WellnessBuddyAPI) or LocalSystem and document in DEPLOY.md.
& $nssmExe set $serviceName ObjectName 'NT AUTHORITY\LocalService' | Out-Null

# ─── Start ───────────────────────────────────────────────────────
Write-Host 'Starting service...' -ForegroundColor Cyan
Start-Service $serviceName
Start-Sleep -Seconds 2

Get-Service $serviceName | Format-List Name, Status, StartType, DisplayName

Write-Host ''
Write-Host 'Servizio installato. Verifica:' -ForegroundColor Green
Write-Host '  Invoke-WebRequest http://127.0.0.1:8000/api/health' -ForegroundColor Green
Write-Host ''
Write-Host "Log: $logsDir\stdout.log + stderr.log (rotazione 10 MB)"
