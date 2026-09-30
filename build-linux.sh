#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm --clean --onedir --windowed --name "Faaaaaah" --add-data "assets:assets" main.py
mkdir -p "dist/Faaaaaah/usr/share/applications" "dist/Faaaaaah/usr/share/icons/hicolor/256x256/apps"
cp assets/icon_256.png "dist/Faaaaaah/usr/share/icons/hicolor/256x256/apps/faaaaaah.png"
cat > "dist/Faaaaaah/usr/share/applications/faaaaaah.desktop" <<'DESKTOP'
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
