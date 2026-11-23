#!/usr/bin/env bash
# One-command startup script for Unix / Linux / macOS
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python "$PROJECT_ROOT/scripts/start_stack.py" "$@"
