#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${APPLE_SIGNING_IDENTITY:?Set APPLE_SIGNING_IDENTITY to your Developer ID Application identity}"
: "${APPLE_NOTARY_PROFILE:?Set APPLE_NOTARY_PROFILE for xcrun notarytool}"
APP="dist/Faaaaaah.app"
DMG="dist-installer/Faaaaaah.dmg"
ENT="installer/macos/entitlements.plist"
[ -d "$APP" ] || { echo "Build the app first: ./build-macos.sh" >&2; exit 1; }
codesign --deep --force --options runtime --timestamp --entitlements "$ENT" --sign "$APPLE_SIGNING_IDENTITY" "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"
./installer/macos/make-dmg.sh
codesign --timestamp --sign "$APPLE_SIGNING_IDENTITY" "$DMG"
xcrun notarytool submit "$DMG" --keychain-profile "$APPLE_NOTARY_PROFILE" --wait
xcrun stapler staple "$APP"
xcrun stapler staple "$DMG"
spctl --assess --type execute --verbose=2 "$APP"
spctl --assess --type open --context context:primary-signature --verbose=2 "$DMG"
printf '\nSigned and notarized: %s\n' "$DMG"
