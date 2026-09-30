#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
./build-linux.sh
ARCH="$(uname -m)"
OUT="dist-installer/Faaaaaah-linux-${ARCH}.tar.gz"
mkdir -p dist-installer
tar -C dist -czf "$OUT" Faaaaaah
sha256sum "$OUT" > "$OUT.sha256"
