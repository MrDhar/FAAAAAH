#!/usr/bin/env bash
# Compiles app.py to native code with Nuitka (macOS + Linux).
# Needs: Xcode Command Line Tools (macOS) or gcc + patchelf (Linux: sudo apt install gcc patchelf python3-dev).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt nuitka zstandard ordered-set
rm -rf dist-nuitka
mkdir -p dist
if [ "$(uname)" = "Darwin" ]; then
  python3 -m nuitka --standalone --enable-plugin=tk-inter --macos-create-app-bundle \
    --macos-app-icon=assets/Faaaaaah.icns --macos-app-name=Faaaaaah \
    --macos-signed-app-name=com.faaaaaah.app --include-data-dir=assets=assets \
    --output-dir=dist-nuitka app.py
  rm -rf dist/Faaaaaah.app && mv dist-nuitka/app.app dist/Faaaaaah.app
  printf '\nBuilt: dist/Faaaaaah.app\n'
else
  python3 -m nuitka --standalone --enable-plugin=tk-inter --include-data-dir=assets=assets \
    --output-filename=Faaaaaah --output-dir=dist-nuitka app.py
  rm -rf dist/Faaaaaah && mv dist-nuitka/app.dist dist/Faaaaaah
  mkdir -p dist/Faaaaaah/usr/share/applications dist/Faaaaaah/usr/share/icons/hicolor/256x256/apps
  cp assets/icon_256.png dist/Faaaaaah/usr/share/icons/hicolor/256x256/apps/faaaaaah.png
  cat > dist/Faaaaaah/usr/share/applications/faaaaaah.desktop <<'DESKTOP'
[Desktop Entry]
Name=Faaaaaah
Comment=A tiny sound for every key you press
Exec=/opt/Faaaaaah/Faaaaaah
Icon=faaaaaah
Terminal=false
Type=Application
Categories=Utility;Audio;
DESKTOP
  printf '\nBuilt: dist/Faaaaaah/\n'
fi
