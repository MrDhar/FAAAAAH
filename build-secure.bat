@echo off
setlocal
cd /d "%~dp0"
REM Optional hardened build using Nuitka. Requires a working C compiler/MinGW.
where python >nul 2>&1 || (echo Python is required.& exit /b 1)
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements.txt nuitka zstandard ordered-set || exit /b 1
python -m nuitka --standalone --assume-yes-for-downloads --enable-plugin=tk-inter ^
  --windows-console-mode=disable --windows-icon-from-ico=assets\Faaaaaah.ico ^
  --include-data-dir=assets=assets --company-name=Faaaaaah --product-name=Faaaaaah ^
  --file-version=1.0.0.0 --product-version=1.0.0.0 --output-dir=dist-nuitka --output-filename=Faaaaaah.exe main.py
if errorlevel 1 exit /b 1
if exist dist\Faaaaaah rmdir /s /q dist\Faaaaaah
if not exist dist mkdir dist
move dist-nuitka\main.dist dist\Faaaaaah >nul
echo Built: dist\Faaaaaah\Faaaaaah.exe
