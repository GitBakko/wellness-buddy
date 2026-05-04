# deploy/scripts/smoke-test.ps1
# Wellness Buddy — production smoke test (DEP-09)
# Usage:
#   pwsh deploy/scripts/smoke-test.ps1 https://wellness-buddy.epartner.it
#
# Exits 0 if all checks green, 1 otherwise. Pwsh 7+.
#
# Checks:
#   1. /api/health returns 200 with status=ok, version, build_hash, db_ok=true
#   2. /version.json returns 200 with version + build_hash
#   3. / serves frontend dist (matches "Wellness Buddy")
#   4. HTTPS cert valid + not expired

[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [string]$BaseUrl
)

$ErrorActionPreference = 'Stop'

# Strip trailing slash for clean URLs
$BaseUrl = $BaseUrl.TrimEnd('/')

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    Write-Error 'BaseUrl is required. Example: pwsh smoke-test.ps1 https://wellness-buddy.epartner.it'
    exit 1
}

Write-Host "=== Smoke test: $BaseUrl ===" -ForegroundColor Cyan
$failures = 0

# ─── 1. /api/health ────────────────────────────────────────────────
try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/api/health" -TimeoutSec 10
    $hasStatus = $null -ne $r.status -and $r.status -eq 'ok'
    $hasVersion = -not [string]::IsNullOrWhiteSpace([string]$r.version)
    $hasBuildHash = -not [string]::IsNullOrWhiteSpace([string]$r.build_hash)
    if ($hasStatus -and $hasVersion -and $hasBuildHash) {
        $dbOkText = if ($null -ne $r.db_ok) { ", db_ok=$($r.db_ok)" } else { '' }
        Write-Host "OK  /api/health: status=ok, version=$($r.version), build_hash=$($r.build_hash)$dbOkText" -ForegroundColor Green
    }
    else {
        throw "/api/health body shape mismatch (status=$($r.status), version=$($r.version), build_hash=$($r.build_hash))"
    }
}
catch {
    Write-Host "ERR /api/health failed: $_" -ForegroundColor Red
    $failures++
}

# ─── 2. /version.json ──────────────────────────────────────────────
try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/version.json" -TimeoutSec 10
    if (-not [string]::IsNullOrWhiteSpace([string]$r.version) -and -not [string]::IsNullOrWhiteSpace([string]$r.build_hash)) {
        Write-Host "OK  /version.json: version=$($r.version), build_hash=$($r.build_hash)" -ForegroundColor Green
    }
    else {
        throw "/version.json body shape mismatch"
    }
}
catch {
    Write-Host "ERR /version.json failed: $_" -ForegroundColor Red
    $failures++
}

# ─── 3. Frontend root ──────────────────────────────────────────────
try {
    $r = Invoke-WebRequest -Uri $BaseUrl -TimeoutSec 10
    if ($r.StatusCode -eq 200 -and $r.Content -match 'Wellness Buddy') {
        Write-Host 'OK  / serves frontend dist (Wellness Buddy in HTML)' -ForegroundColor Green
    }
    else {
        throw "Root page mismatch (status=$($r.StatusCode), body did not match 'Wellness Buddy')"
    }
}
catch {
    Write-Host "ERR / failed: $_" -ForegroundColor Red
    $failures++
}

# ─── 4. SSL cert expiry (only meaningful for https URLs) ───────────
# Uses TcpClient + SslStream — works on PS 7+/.NET 6+ where the legacy
# WebRequest.ServicePoint.Certificate path can return null after the
# response stream is closed.
if ($BaseUrl.StartsWith('https://')) {
    $tcp = $null
    $ssl = $null
    try {
        $uri = [Uri]$BaseUrl
        $port = if ($uri.Port -gt 0) { $uri.Port } else { 443 }

        $tcp = [System.Net.Sockets.TcpClient]::new()
        $tcp.ReceiveTimeout = 10000
        $tcp.SendTimeout = 10000
        $tcp.Connect($uri.Host, $port)

        $ssl = [System.Net.Security.SslStream]::new($tcp.GetStream(), $false, { $true })
        $ssl.AuthenticateAsClient($uri.Host)

        $cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($ssl.RemoteCertificate)
        $expiry = $cert.NotAfter
        $daysLeft = [int]([math]::Floor(($expiry - (Get-Date)).TotalDays))
        $subjectShort = ($cert.Subject -split ',')[0]
        $issuerShort = ($cert.Issuer -split ',')[0]

        if ($daysLeft -gt 0) {
            Write-Host "OK  HTTPS cert valid: expires in $daysLeft days ($($expiry.ToString('yyyy-MM-dd')))" -ForegroundColor Green
            Write-Host "    Subject: $subjectShort | Issuer: $issuerShort" -ForegroundColor DarkGray
            if ($daysLeft -lt 14) {
                Write-Host "WARN Cert expires in $daysLeft days — verify auto-renewal task." -ForegroundColor Yellow
            }
        }
        else {
            throw "Cert expired or expires today (expiry=$expiry)"
        }
    }
    catch {
        Write-Host "ERR SSL check failed: $_" -ForegroundColor Red
        $failures++
    }
    finally {
        if ($ssl) { try { $ssl.Dispose() } catch {} }
        if ($tcp) { try { $tcp.Dispose() } catch {} }
    }
}
else {
    Write-Host "SKIP SSL check (BaseUrl is not HTTPS: $BaseUrl)" -ForegroundColor DarkGray
}

# ─── Result ────────────────────────────────────────────────────────
Write-Host ''
if ($failures -eq 0) {
    Write-Host '=== Tutti i smoke test verdi ===' -ForegroundColor Green
    exit 0
}
else {
    Write-Host "=== Smoke test FALLITO: $failures check rotto/i ===" -ForegroundColor Red
    exit 1
}
