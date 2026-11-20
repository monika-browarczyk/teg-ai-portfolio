#!/bin/sh
# Install the locked course environment without changing the system Python.
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PROJECT_ROOT/.cache/uv}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$PROJECT_ROOT/.tools/python}"

if command -v uv >/dev/null 2>&1; then
    UV_BIN=$(command -v uv)
else
    UV_BIN="$PROJECT_ROOT/.tools/bootstrap/bin/uv"
    if [ ! -x "$UV_BIN" ]; then
        python3 -m venv "$PROJECT_ROOT/.tools/bootstrap"
        "$PROJECT_ROOT/.tools/bootstrap/bin/python" -m pip install --disable-pip-version-check --no-cache-dir 'uv==0.13.9'
    fi
fi

"$UV_BIN" sync --locked "$@"
if [ ! -e .env ]; then
    (umask 077; cp .env.example .env)
fi
printf '\nŚrodowisko gotowe. Zacznij od:\n  .venv/bin/python mini_project_1/src/check.py\n'
