# Building

## Run from source
Python 3.11+ with Tkinter (`python3-tk` on Debian/Ubuntu, `python3-tkinter` on Fedora, `tk` on Arch, python.org build on macOS).

    python3 -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
    pip install pynput pygame
    python main.py

## Standard build (PyInstaller)
`build.bat` (Windows), `./build-macos.sh`, `./build-linux.sh`.

## Optional: native-compiled build (Nuitka)
`build-secure.bat` (Windows) or `./build-secure.sh` (macOS / Linux) compile `main.py` to native code instead of packing bytecode. The output layout is the same as the standard build, so the installer scripts work unchanged. Needs a C compiler (Windows: Nuitka can download MinGW-w64; macOS: Xcode Command Line Tools; Linux: `gcc patchelf python3-dev`).
This doesn't hide anything for an open-source project; it's just an alternative build with somewhat faster startup on some machines.

## Releasing
Sign every release, publish SHA-256 checksums, and upload installers to the GitHub Releases page. See `INSTALLERS.md`.
