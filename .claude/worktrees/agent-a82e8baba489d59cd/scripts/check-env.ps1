$ErrorActionPreference = "Stop"
Write-Host "Verifico requisiti dev Wellness Buddy..."

$required = @("node", "pnpm", "python", "uv", "docker", "psql", "git")
foreach ($cmd in $required) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "MANCANTE: $cmd — installa prima di procedere"
        exit 1
    }
}

$nodeVersion = (node -v) -replace 'v',''
$nodeMajor = [int]($nodeVersion.Split('.')[0])
if ($nodeMajor -lt 20) { Write-Host "Node.js $nodeMajor < 20 — aggiorna"; exit 1 }

$pyVersion = (python -c "import sys; print(sys.version_info.minor)")
if ([int]$pyVersion -lt 12) { Write-Host "Python 3.$pyVersion < 3.12 — aggiorna"; exit 1 }

Write-Host "OK — tutti i requisiti sono presenti."
