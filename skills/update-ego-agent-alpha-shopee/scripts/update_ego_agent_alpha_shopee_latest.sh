#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="ego-agent-alpha-shopee"
PIP_INDEX_URL="${EGO_AGENT_ALPHA_PIP_INDEX_URL:-https://pypi.shopee.io/simple}"

print_step() {
  echo
  echo "==> $1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: missing required command: $1" >&2
    exit 1
  fi
}

require_cmd python3
require_cmd bash

print_step "Step 1/4: uninstall synced skills/agents (if command is available)"
if command -v "${PACKAGE_NAME}" >/dev/null 2>&1; then
  "${PACKAGE_NAME}" uninstall-skills --platform auto
else
  echo "Skip: ${PACKAGE_NAME} command not found."
fi

print_step "Step 2/4: uninstall package"
python3 -m pip uninstall -y "${PACKAGE_NAME}" || true

print_step "Step 3/4: install latest package from index"
python3 -m pip install -i "${PIP_INDEX_URL}" --force-reinstall "${PACKAGE_NAME}"

print_step "Step 4/4: install bundled skills/agents"
"${PACKAGE_NAME}" install-skills --platform auto

echo
echo "Done: ${PACKAGE_NAME} is updated and skills/agents are installed."
