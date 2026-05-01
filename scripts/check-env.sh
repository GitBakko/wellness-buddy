#!/usr/bin/env bash
set -e

echo "Verifico requisiti dev Wellness Buddy..."
for cmd in node pnpm python3 uv docker psql git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MANCANTE: $cmd — installa prima di procedere"
    exit 1
  fi
done

node_major=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$node_major" -lt 20 ]; then
  echo "Node.js $node_major < 20 — aggiorna a 20 LTS"
  exit 1
fi

py_minor=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$py_minor" -lt 12 ]; then
  echo "Python 3.$py_minor < 3.12 — aggiorna a Python 3.12"
  exit 1
fi

echo "OK — tutti i requisiti sono presenti."
