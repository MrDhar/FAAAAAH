@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pip || exit /b 1
py -m pip install -r requirements.txt || exit /b 1
py -m PyInstaller --noconfirm --clean --windowed --name "Faaaaaah" --icon "assets\Faaaaaah.ico" --add-data "assets;assets" app.py
if errorlevel 1 exit /b 1
echo Built: dist\Faaaaaah\Faaaaaah.exe
