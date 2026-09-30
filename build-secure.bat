@echo off
setlocal
cd /d "%~dp0"
REM Compiles app.py to native code with Nuitka (no readable .py / easy-to-decompile .pyc ships).
REM Needs a C compiler; Nuitka offers to download MinGW-w64 on first run.
py -m pip install --upgrade pip || exit /b 1
py -m pip install -r requirements.txt nuitka zstandard ordered-set || exit /b 1
py -m nuitka --standalone --assume-yes-for-downloads --enable-plugin=tk-inter ^
  --windows-console-mode=disable --windows-icon-from-ico=assets\Faaaaaah.ico ^
  --include-data-dir=assets=assets --company-name=Faaaaaah --product-name=Faaaaaah ^
  --file-version=1.0.0.0 --product-version=1.0.0.0 --output-dir=dist-nuitka --output-filename=Faaaaaah.exe app.py
if errorlevel 1 exit /b 1
if exist dist\Faaaaaah rmdir /s /q dist\Faaaaaah
if not exist dist mkdir dist
move dist-nuitka\app.dist dist\Faaaaaah >nul
echo Built: dist\Faaaaaah\Faaaaaah.exe
