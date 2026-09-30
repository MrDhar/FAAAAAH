#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
./build-linux.sh
ARCH="$(uname -m)"
rm -rf dist-package dist-installer
mkdir -p dist-package/Faaaaaah
cp -a dist/Faaaaaah/. dist-package/Faaaaaah/Faaaaaah/
cp installer/linux/install.sh dist-package/Faaaaaah/install.sh
chmod +x dist-package/Faaaaaah/install.sh
mkdir -p dist-package/Faaaaaah/Faaaaaah/usr/share/icons/hicolor/256x256/apps
tar -C dist-package -czf "Faaaaaah-linux-${ARCH}.tar.gz" Faaaaaah
mkdir -p dist-installer
mv "Faaaaaah-linux-${ARCH}.tar.gz" dist-installer/
sha256sum "dist-installer/Faaaaaah-linux-${ARCH}.tar.gz" > "dist-installer/Faaaaaah-linux-${ARCH}.tar.gz.sha256"
printf '\nBuilt: dist-installer/Faaaaaah-linux-%s.tar.gz\n' "$ARCH"
