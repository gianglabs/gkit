#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DPGT_DIR="${PROJECT_ROOT}/DPGT"

echo "[clone] project root: ${PROJECT_ROOT}"

if ! git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[clone] ERROR: ${PROJECT_ROOT} is not a git repository"
  exit 1
fi

echo "[clone] init top-level DPGT submodule"
git -C "${PROJECT_ROOT}" submodule update --init --recursive DPGT

if [ ! -d "${DPGT_DIR}" ]; then
  echo "[clone] ERROR: DPGT directory not found after init"
  exit 1
fi

if [ -f "${DPGT_DIR}/.gitmodules" ]; then
  echo "[clone] rewrite nested submodule URLs to HTTPS"
  sed -i 's#git@github.com:#https://github.com/#g' "${DPGT_DIR}/.gitmodules"
  sed -i 's#git@gitlab.com:#https://gitlab.com/#g' "${DPGT_DIR}/.gitmodules"

  echo "[clone] sync nested submodule config"
  git -C "${DPGT_DIR}" submodule sync --recursive

  echo "[clone] clear cached nested submodule metadata"
  git -C "${DPGT_DIR}" submodule deinit -f --all || true
  rm -rf "${DPGT_DIR}/.git/modules"

  echo "[clone] init nested DPGT submodules"
  git -C "${DPGT_DIR}" submodule update --init --recursive
fi

echo "[clone] done. nested submodule status:"
git -C "${DPGT_DIR}" submodule status --recursive || true
