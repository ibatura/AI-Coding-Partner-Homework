#!/bin/bash
# Coverage gate: blocks git push if test coverage is below 80%.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================"
echo " Coverage Gate — minimum threshold: 80%"
echo "============================================"

if ! command -v pytest &>/dev/null; then
  echo "ERROR: pytest not found. Install with: pip install pytest pytest-cov"
  exit 1
fi

pytest \
  --cov=agents \
  --cov=integrator \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -q
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "============================================"
  echo " PUSH BLOCKED: coverage is below 80% or tests failed."
  echo " Fix failing tests or add coverage before pushing."
  echo "============================================"
  exit 1
fi

echo ""
echo "============================================"
echo " Coverage check passed. Push allowed."
echo "============================================"
exit 0
