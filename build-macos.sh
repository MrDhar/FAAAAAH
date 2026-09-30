#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name "Faaaaaah" \
  --icon "assets/Faaaaaah.icns" --osx-bundle-identifier "com.faaaaaah.app" \
  --add-data "assets:assets" app.py
printf '\nBuilt: dist/Faaaaaah.app\n'
