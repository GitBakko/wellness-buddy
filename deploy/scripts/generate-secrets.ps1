# deploy/scripts/generate-secrets.ps1
# Wellness Buddy — generate SECRET_KEY (D-24) + DB password (D-25)
#
# Outputs to STDOUT only — never persisted to disk by this script.
# Copy values straight into backend/.env. They will not be shown again.
# Pwsh 7+ (cross-platform). Use $ErrorActionPreference Stop to fail fast.

$ErrorActionPreference = 'Stop'

function New-HexString {
    param([Parameter(Mandatory)][int]$Bytes)
    if ($Bytes -lt 16) { throw "Bytes must be >= 16 (256-bit minimum). Got $Bytes." }
    $buffer = [byte[]]::new($Bytes)
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($buffer) } finally { $rng.Dispose() }
    return ([System.BitConverter]::ToString($buffer)).Replace('-', '').ToLower()
}

function New-UrlSafePassword {
    param([Parameter(Mandatory)][int]$Bytes)
    if ($Bytes -lt 16) { throw "Bytes must be >= 16. Got $Bytes." }
    $buffer = [byte[]]::new($Bytes)
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($buffer) } finally { $rng.Dispose() }
    # URL-safe base64: replace + / with - _, strip = padding
    $b64 = [Convert]::ToBase64String($buffer)
    return $b64.Replace('+', '-').Replace('/', '_').Replace('=', '')
}

Write-Host '=== Wellness Buddy — Secret Generation ===' -ForegroundColor Cyan
Write-Host ''

# SECRET_KEY: 32 bytes -> 64 hex chars per CONTEXT D-24
$secretKey = New-HexString -Bytes 32
if ($secretKey.Length -ne 64) {
    throw "Generated SECRET_KEY has wrong length: $($secretKey.Length) (expected 64)"
}

Write-Host 'SECRET_KEY (copia in backend/.env):'
Write-Host $secretKey -ForegroundColor Yellow
Write-Host ''

# DB password: 24 bytes URL-safe base64 (~32 chars) per D-25
$dbPwd = New-UrlSafePassword -Bytes 24
Write-Host 'DATABASE_URL password (per ALTER USER + DATABASE_URL):'
Write-Host $dbPwd -ForegroundColor Yellow
Write-Host ''

Write-Host 'Comando SQL pronto da incollare in psql:'
Write-Host "  ALTER USER wnbd WITH PASSWORD '$dbPwd';" -ForegroundColor Green
Write-Host ''

Write-Host 'Riga DATABASE_URL pronta per backend/.env:'
Write-Host "  DATABASE_URL=postgresql+asyncpg://wnbd:$dbPwd@localhost:5432/WellnessBuddy" -ForegroundColor Green
Write-Host ''

Write-Host 'ATTENZIONE: copia subito i valori nel file backend/.env.' -ForegroundColor Red
Write-Host 'I valori NON saranno mostrati di nuovo.' -ForegroundColor Red
