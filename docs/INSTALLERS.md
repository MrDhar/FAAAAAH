# Secure distribution / installers

## Important
No software package can honestly be guaranteed to produce zero antivirus warnings. The safest distribution model is:
1. build from a clean, reproducible source tree;
2. code-sign the release;
3. publish SHA-256 checksums;
4. distribute from a stable HTTPS release page.

Do not disable antivirus or ask users to add exclusions.

## Windows
Build the application with `build.bat`, then open `installer/windows/Faaaaaah.iss` in Inno Setup. Before public distribution, sign both the executable and installer with a genuine Authenticode certificate. Use a certificate issued to the actual publisher. Microsoft SmartScreen reputation may still require time to establish trust.

## macOS
Build with `./build-macos.sh`. On a Mac with an Apple Developer ID certificate, run `installer/macos/sign-and-notarize.sh` after configuring its environment variables. Notarization is the normal route to avoiding Gatekeeper warnings for distributed apps.

## Linux
Use `installer/linux/build-tar.sh` for a simple tarball. If distributing an AppImage, sign the release/checksum with a project-controlled GPG key and publish the public key/fingerprint. Linux desktop trust behavior varies by distribution.

## Permissions
Faaaaaah needs global keyboard monitoring to perform its core function. macOS and some Linux environments will ask the user for permission. The app should never request unrelated privileges.
