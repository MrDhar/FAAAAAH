#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Faaaaaah"
INSTALL_DIR="${HOME}/.local/opt/Faaaaaah"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"

printf '\033[1;33m\n   FAAAAAAH INSTALLER\n\033[0m'
printf '\033[1;90m   giving every key a voice...\033[0m\n\n'

rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
cp -a "$ROOT/Faaaaaah/." "$INSTALL_DIR/"
cp "$ROOT/Faaaaaah/usr/share/icons/hicolor/256x256/apps/faaaaaah.png" "$ICON_DIR/faaaaaah.png"

cat > "$BIN_DIR/faaaaaah" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/Faaaaaah" "\$@"
EOF
chmod +x "$BIN_DIR/faaaaaah"

cat > "$DESKTOP_DIR/faaaaaah.desktop" <<EOF
[Desktop Entry]
Name=Faaaaaah
Comment=A tiny sound for every key you press
Exec=$BIN_DIR/faaaaaah
Icon=faaaaaah
Terminal=false
Type=Application
Categories=Utility;Audio;
EOF

printf '\033[1;32m   ✓ Faaaaaah installed.\033[0m\n'
printf '\033[1;90m   Launch it from your app menu or run: faaaaaah\033[0m\n\n'
