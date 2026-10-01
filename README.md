<p align="center">
  <img src="docs/images/banner.svg" alt="Faaaaaah - a tiny sound for every key you press" width="100%">
</p>

<p align="center">
  <img alt="Windows" src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?logo=windows&logoColor=white&style=for-the-badge">
  <img alt="macOS" src="https://img.shields.io/badge/macOS-12%2B-000000?logo=apple&logoColor=white&style=for-the-badge">
  <img alt="Linux" src="https://img.shields.io/badge/Linux-X11-FCC624?logo=linux&logoColor=black&style=for-the-badge">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white&style=for-the-badge">
</p>

<p align="center">
  <b>Faaaaaah</b> is a tiny desktop app that plays a sound every time you press a key.<br>
  Ships with the legendary <i>FAAAAAH</i>. Bring your own MP3 or WAV if you want.
</p>

<p align="center">
  <a href="#-install">Install</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-build-from-source">Build</a> •
  <a href="#-troubleshooting">Troubleshooting</a> •
  <a href="#-faq">FAQ</a>
</p>

---

## ✨ Features

- 🔊 **Plays on every keypress**, system-wide, in any app
- 🎚️ **Volume slider** and one-click **on/off** toggle
- 🎵 **Custom sounds**: add your own `.mp3` or `.wav` and switch between them
- 🤫 **Modifier keys stay silent** (Shift, Ctrl, Alt, Cmd) and held keys don't spam
- ⚡ **Low latency** audio with overlapping playback, so fast typing sounds right
- 💾 **Remembers** your sound, volume and on/off state
- 🔒 **No admin rights, no network, no telemetry.** Nothing you type is stored or sent anywhere

---

## 📦 Install

Grab the latest build for your system from the
[**Releases page**](https://github.com/YOUR_USERNAME/Faaaaaah/releases/latest).

<details open>
<summary><b>🪟 Windows 10 / 11</b></summary>

1. Download **`Faaaaaah-Setup.exe`**.
2. Run it and follow the wizard. No administrator rights are needed; it installs for your user.
3. Launch **Faaaaaah** from the Start menu or desktop shortcut.

> **SmartScreen warning?** New or unsigned apps can trigger *"Windows protected your PC"*.
> If you downloaded from this repository's Releases page, click **More info → Run anyway**.
> You can verify the download first with the checksum (see [Verify your download](#-verify-your-download)).

**Uninstall:** Settings → Apps → Installed apps → Faaaaaah → Uninstall.

</details>

<details>
<summary><b>🍎 macOS 12+</b></summary>

1. Download **`Faaaaaah.dmg`**.
2. Open it and drag **Faaaaaah** into **Applications**.
3. Launch Faaaaaah. If macOS says the app can't be verified (unsigned builds only), right-click the app → **Open** → **Open**.
4. **Grant permission.** Global key detection needs it. Go to
   **System Settings → Privacy & Security** and enable Faaaaaah under
   **Accessibility** and **Input Monitoring**, then restart the app.

**Uninstall:** drag Faaaaaah from Applications to the Trash.

</details>

<details>
<summary><b>🐧 Linux (x86_64 / arm64)</b></summary>

Faaaaaah listens for keys through X11, so it works best on an **X11 session**
(see [Wayland note](#-troubleshooting)).

```bash
# 1. Download and extract (pick the file matching your CPU: x86_64 or aarch64)
tar -xzf Faaaaaah-linux-x86_64.tar.gz
sudo mv Faaaaaah /opt/Faaaaaah

# 2. Add it to your app menu
sudo cp /opt/Faaaaaah/usr/share/applications/faaaaaah.desktop /usr/share/applications/
sudo cp /opt/Faaaaaah/usr/share/icons/hicolor/256x256/apps/faaaaaah.png \
        /usr/share/icons/hicolor/256x256/apps/

# 3. Run it
/opt/Faaaaaah/Faaaaaah
```

No `sudo`? Extract anywhere and run `./Faaaaaah/Faaaaaah` directly.

**Uninstall:**
```bash
sudo rm -rf /opt/Faaaaaah /usr/share/applications/faaaaaah.desktop \
            /usr/share/icons/hicolor/256x256/apps/faaaaaah.png
```

</details>

<details>
<summary><b>🐍 Run from source (any OS)</b></summary>

Requires **Python 3.11+** with Tkinter.

| OS | Get Python + Tk |
|---|---|
| Windows | [python.org](https://www.python.org/downloads/) installer (Tk is included) |
| macOS | [python.org](https://www.python.org/downloads/) installer, or `brew install python-tk` |
| Debian / Ubuntu | `sudo apt install python3 python3-pip python3-tk` |
| Fedora | `sudo dnf install python3 python3-pip python3-tkinter` |
| Arch | `sudo pacman -S python tk` |

> ⚠️ On macOS, use python.org's Python or Homebrew's. The system Python ships an old Tk that can't load the mascot image.

```bash
git clone https://github.com/YOUR_USERNAME/Faaaaaah.git
cd Faaaaaah
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pynput pygame
python main.py
```

</details>

### 🔐 Verify your download

Each release publishes SHA-256 checksums. Compare yours before installing:

```bash
# Linux / macOS
shasum -a 256 Faaaaaah.dmg

# Windows (PowerShell)
Get-FileHash .\Faaaaaah-Setup.exe -Algorithm SHA256
```

---

## 🎮 Usage

1. Open **Faaaaaah** — it's ready straight away.
2. Type anywhere. Every key goes **FAAAAAH**.
3. Use the **toggle** in the top-right corner to pause the sound, and the **slider** to adjust the volume.
4. Click **▶ Play Faaaaaah** to test the sound.

## 🎬 Demo

Watch Faaaaaah in action:

[▶️ Play the Faaaaaah Demo](docs/images/Picsart_26-10-01_14-20-23-222.mp4)

### Adding your own sounds

1. Click **+ Add Sound** and pick an `.mp3` or `.wav`.
2. Click any sound in the list to select it, or **▶** to preview it.
3. **Delete** removes a custom sound. The built-in one can't be removed.

Short sounds (under ~1 second) work best for fast typing.

### Where things are stored

| | Location |
|---|---|
| Windows | `%APPDATA%\Faaaaaah\` |
| macOS | `~/Library/Application Support/Faaaaaah/` |
| Linux | `~/.local/share/Faaaaaah/` (or `$XDG_DATA_HOME/Faaaaaah/`) |

Inside: `settings.json` and a `sounds/` folder. Use **Open sound folder** in the app to jump there.

---

## 🛠️ Build from source

You need Python 3.11+ (with Tk, see the table above).

| OS | Command | Output |
|---|---|---|
| Windows | `build.bat` | `dist\Faaaaaah\Faaaaaah.exe` |
| macOS | `./build-macos.sh` (or double-click `build-macos.command`) | `dist/Faaaaaah.app` |
| Linux | `./build-linux.sh` | `dist/Faaaaaah/` |

Then make installers:

| OS | How |
|---|---|
| Windows | Open `installer/windows/Faaaaaah.iss` in [Inno Setup](https://jrsoftware.org/isinfo.php) and compile → `dist-installer/Faaaaaah-Setup.exe` |
| macOS | `installer/macos/sign-and-notarize.sh` (needs an Apple Developer ID) → `dist-installer/Faaaaaah.dmg` |
| Linux | `installer/linux/build-tar.sh` → `dist-installer/Faaaaaah-linux-<arch>.tar.gz` + `.sha256` |

See [`docs/INSTALLERS.md`](docs/INSTALLERS.md) for code-signing and notarization guidance and [`docs/BUILDING.md`](docs/BUILDING.md) for more.

<details>
<summary><b>📁 Project layout</b></summary>

```
Faaaaaah/
├── main.py                  # the whole app (Tkinter UI, pygame audio, pynput keys)
├── assets/                 # sound, mascot, icons
├── docs/                   # installer docs + README images
├── installer/              # Windows (Inno Setup), macOS (sign/notarize), Linux (tar)
├── build.bat               # Windows build
├── build-macos.sh          # macOS build
├── build-linux.sh          # Linux build
└── requirements.txt
```

</details>

---

## 🩹 Troubleshooting

<details>
<summary><b>No sound when I type</b></summary>

- Check the toggle says **Sound On** and the volume isn't at 0%.
- Click **Play Faaaaaah**. If that is silent too, check your system output device.
- The status in the top right shows problems such as *Audio library missing* or *Could not listen for keys*.
</details>

<details>
<summary><b>macOS: works only when Faaaaaah is focused</b></summary>

Permission is missing. Enable Faaaaaah under **Privacy & Security → Accessibility** and **Input Monitoring**, remove and re-add it if it's already listed, then restart the app.
</details>

<details>
<summary><b>Linux: nothing happens on Wayland</b></summary>

Wayland doesn't let normal apps listen to global key presses, so detection may only work while XWayland apps are focused. Log in with an **X11 / Xorg session** from your login screen's gear icon.
</details>

<details>
<summary><b>Linux: <code>No module named tkinter</code></b></summary>

Install Tk for your distro (see the [Run from source](#-install) table).
</details>

<details>
<summary><b>Windows: antivirus flags the app</b></summary>

Apps that watch the keyboard often trigger heuristics, and Faaaaaah has to watch keys to work. The source is all in [`main.py`](main.py) and you can build it yourself. Please don't disable your antivirus; verify the [checksum](#-verify-your-download) instead.
</details>

---

## ❓ FAQ

**Does it record what I type?**
No. It only reacts to "a key was pressed" and never looks at which key (other than ignoring modifiers), and it never stores or sends anything. Read [`on_press`](main.py) yourself; it's a few lines.

**Does it need admin / root?**
No.

**Why does it need Accessibility / Input Monitoring on macOS?**
That's the only way macOS lets an app hear key presses outside its own window.

---

## 🔒 Security

Official releases should be code-signed and published with SHA-256 checksums. Only download Faaaaaah from this repository's Releases page, or build it yourself from source. See [`docs/INSTALLERS.md`](docs/INSTALLERS.md).

## 📄 License

MIT, see [`LICENSE`](LICENSE). Contributions welcome: open an issue or pull request.

<p align="center">
  <img src="docs/images/mascot.gif" width="120" alt="">
  <br>
  <sub>Made with too much caffeine and one very loud cat.</sub>
</p>

## Project structure

```text
main.py                         App entry point
faaaaaah/core/config.py        Paths, branding, theme constants
faaaaaah/core/settings.py      Persistent settings
faaaaaah/core/audio.py         Audio engine
faaaaaah/core/keyboard.py      Global keyboard listener
faaaaaah/core/keys.py          Key normalization helpers
faaaaaah/core/sounds.py        Custom/preset sound library
faaaaaah/ui/widgets.py         Reusable UI controls
faaaaaah/ui/dialogs.py         Key assignment dialog
faaaaaah/ui/app.py             UI composition and page behavior
installer/                     OS-specific installers
assets/                        Mascot, icon and preset sound
```

The core services are intentionally separated from the UI so changing the interface does not require changing audio, keyboard, settings, or sound-library code.

## v6 UI update
- Redesigned the Assign Key flow as an explicit, user-friendly three-step wizard.
- Key capture starts only after the user clicks “Press a key”.
- Added clear progress indicators, selected-key feedback, sound selection feedback, and preview labels.
- Improved Now Playing and Key Sounds explanatory text.


### Sound toggle behavior
- The **Default sound** toggle controls only keys without a key-specific assignment.
- Every key-specific assignment has its own **On/Off** toggle in **Key Sounds**.
- Turning Default sound off does not silence an enabled key-specific sound.
- Key-specific toggle states are saved and restored between launches.
