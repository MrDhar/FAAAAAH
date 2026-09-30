@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1 || (echo Python 3.12+ is required.& exit /b 1)
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements.txt || exit /b 1
python -m PyInstaller --noconfirm --clean --windowed --name "Faaaaaah" --icon "assets\Faaaaaah.ico" --add-data "assets;assets" main.py || exit /b 1
echo Built: dist\Faaaaaah\Faaaaaah.exe
