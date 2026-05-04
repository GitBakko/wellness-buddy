# deploy/scripts/package-release.ps1
# Wellness Buddy — build + zip production release on dev workstation.
#
# Usage (from repo root):
#   pwsh deploy/scripts/package-release.ps1
#   pwsh deploy/scripts/package-release.ps1 -SkipFrontendBuild   # if dist already current
#
# Output: dist-package/wellness-buddy-<git-sha>-<yyyyMMdd-HHmm>.zip
#
# Contents:
#   backend/        — source (no .venv, __pycache__, tests, .pytest_cache, *.pyc)
#   frontend/dist/  — pre-built PWA assets
#   deploy/         — install scripts + .env template + IIS web.config + win-acme README
#   DEPLOY.md
#   .planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md
#   VERSION.txt     — git sha + build timestamp + APP_VERSION
#
# Pwsh 7+. Run from repo root. Requires: git, pnpm, Node 22+.

[CmdletBinding()]
param(
    [switch]$SkipFrontendBuild,
    [string]$AppVersion = '0.2.0',
    [string]$OutputDir = 'dist-package'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ─── Sanity checks ──────────────────────────────────────────────────
if (-not (Test-Path 'package.json') -or -not (Test-Path 'backend/pyproject.toml')) {
    Write-Error 'Run from repo root (where package.json + backend/pyproject.toml live).'
    exit 1
}

foreach ($tool in @('git', 'pnpm', 'node')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "$tool not in PATH. Install before running."
        exit 1
    }
}

# ─── Identifiers ────────────────────────────────────────────────────
$gitSha = (git rev-parse --short HEAD).Trim()
$gitBranch = (git rev-parse --abbrev-ref HEAD).Trim()
$gitDirty = (git status --porcelain).Trim()
$timestamp = Get-Date -Format 'yyyyMMdd-HHmm'
$buildDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'

if ($gitDirty) {
    Write-Warning "Working tree has uncommitted changes. Build sha=$gitSha but content may differ."
}

Write-Host '=== Wellness Buddy — Production Package Build ===' -ForegroundColor Cyan
Write-Host "  Git SHA:    $gitSha (branch: $gitBranch)"
Write-Host "  App ver:    $AppVersion"
Write-Host "  Build date: $buildDate"
Write-Host ''

# ─── 1. Frontend build ──────────────────────────────────────────────
if (-not $SkipFrontendBuild) {
    Write-Host '[1/4] Frontend production build...' -ForegroundColor Yellow

    if (-not (Test-Path 'node_modules')) {
        Write-Host '  pnpm install --frozen-lockfile'
        pnpm install --frozen-lockfile
        if ($LASTEXITCODE -ne 0) { exit 1 }
    }

    $env:VITE_BUILD_HASH = $gitSha
    $env:VITE_APP_VERSION = $AppVersion
    pnpm --filter frontend build
    if ($LASTEXITCODE -ne 0) { Write-Error 'Frontend build failed.'; exit 1 }

    if (-not (Test-Path 'frontend/dist/index.html')) {
        Write-Error 'frontend/dist/index.html missing after build.'
        exit 1
    }
    Write-Host '  Frontend dist OK.' -ForegroundColor Green
} else {
    Write-Host '[1/4] Skipping frontend build (--SkipFrontendBuild).' -ForegroundColor DarkYellow
    if (-not (Test-Path 'frontend/dist/index.html')) {
        Write-Error 'frontend/dist/index.html missing. Run without -SkipFrontendBuild first.'
        exit 1
    }
}

# ─── 2. Stage files in temp dir ─────────────────────────────────────
Write-Host '[2/4] Staging files...' -ForegroundColor Yellow

$stageRoot = Join-Path ([System.IO.Path]::GetTempPath()) "wellness-buddy-pkg-$timestamp"
$pkgName = "wellness-buddy-$gitSha-$timestamp"
$stageDir = Join-Path $stageRoot $pkgName

if (Test-Path $stageRoot) { Remove-Item $stageRoot -Recurse -Force }
New-Item -ItemType Directory -Path $stageDir -Force | Out-Null

# 2a. Backend (exclude virtualenv, caches, tests)
$backendExcludes = @('.venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'tests', '*.pyc', '*.pyo', 'htmlcov', '.coverage')
robocopy 'backend' (Join-Path $stageDir 'backend') /E /XD .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache tests htmlcov /XF '*.pyc' '*.pyo' '.coverage' /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
if ($LASTEXITCODE -gt 7) { Write-Error "robocopy backend failed (exit $LASTEXITCODE)."; exit 1 }

# 2b. Frontend dist only
robocopy 'frontend/dist' (Join-Path $stageDir 'frontend/dist') /E /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
if ($LASTEXITCODE -gt 7) { Write-Error "robocopy frontend/dist failed (exit $LASTEXITCODE)."; exit 1 }

# 2c. Deploy scripts + IIS + win-acme + .env example
robocopy 'deploy' (Join-Path $stageDir 'deploy') /E /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
if ($LASTEXITCODE -gt 7) { Write-Error "robocopy deploy failed (exit $LASTEXITCODE)."; exit 1 }

# 2d. Top-level docs
Copy-Item 'DEPLOY.md' $stageDir
Copy-Item 'README.md' $stageDir -ErrorAction SilentlyContinue

# 2e. Production checklist
$checklistSrc = '.planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md'
if (Test-Path $checklistSrc) {
    Copy-Item $checklistSrc (Join-Path $stageDir 'DEPLOY-CHECKLIST.md')
}

# 2f. VERSION.txt
$versionContent = @"
Wellness Buddy — Production Build
==================================
APP_VERSION:  $AppVersion
GIT_SHA:      $gitSha
GIT_BRANCH:   $gitBranch
BUILD_DATE:   $buildDate
DIRTY_TREE:   $([bool]$gitDirty)
PACKAGE:      $pkgName

Install order:
  1. Read DEPLOY-CHECKLIST.md from §0 (this package onwards).
  2. Extract this zip to C:\Apps\WellnessBuddy on Windows Server 2019.
  3. Follow checklist sections 1 → 13 in order.
"@
$versionContent | Out-File -FilePath (Join-Path $stageDir 'VERSION.txt') -Encoding utf8

Write-Host "  Staged at: $stageDir" -ForegroundColor Green

# ─── 3. Zip ─────────────────────────────────────────────────────────
Write-Host '[3/4] Compressing archive...' -ForegroundColor Yellow

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$zipPath = Join-Path $OutputDir "$pkgName.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path "$stageDir\*" -DestinationPath $zipPath -CompressionLevel Optimal
if (-not (Test-Path $zipPath)) { Write-Error 'Zip creation failed.'; exit 1 }

$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "  Archive: $zipPath ($zipSize MB)" -ForegroundColor Green

# ─── 4. SHA256 manifest ─────────────────────────────────────────────
Write-Host '[4/4] Generating SHA256 checksum...' -ForegroundColor Yellow

$hash = (Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLower()
$shaFile = "$zipPath.sha256"
"$hash *$pkgName.zip" | Out-File -FilePath $shaFile -Encoding ascii
Write-Host "  SHA256: $hash" -ForegroundColor Green
Write-Host "  Saved:  $shaFile" -ForegroundColor Green

# ─── Cleanup stage ──────────────────────────────────────────────────
Remove-Item $stageRoot -Recurse -Force

# ─── Summary ────────────────────────────────────────────────────────
Write-Host ''
Write-Host '=== Build complete ===' -ForegroundColor Cyan
Write-Host "  Output:  $zipPath"
Write-Host "  Size:    $zipSize MB"
Write-Host "  SHA256:  $hash"
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Yellow
Write-Host "  1. Transfer $zipPath to Windows Server 2019 via RDP / SCP / network share"
Write-Host "  2. Verify SHA256 on server: Get-FileHash $pkgName.zip -Algorithm SHA256"
Write-Host "  3. Extract to C:\Apps\WellnessBuddy"
Write-Host "  4. Open DEPLOY-CHECKLIST.md and follow §1 onwards"
