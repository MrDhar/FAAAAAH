#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
APP="dist/Faaaaaah.app"
DMG="dist-installer/Faaaaaah.dmg"
STAGE="dist-dmg"
[ -d "$APP" ] || { echo "Build the app first: ./build-macos.sh" >&2; exit 1; }
rm -rf "$STAGE" dist-installer
mkdir -p "$STAGE/.background" dist-installer
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
cp installer/macos/dmg-background.png "$STAGE/.background/background.png"
hdiutil create -volname "Faaaaaah" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
rm -rf "$STAGE"
printf '\nBuilt: %s\n' "$DMG"
