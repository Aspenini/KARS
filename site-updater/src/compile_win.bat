@echo off
REM Check if Python is installed
where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Attempting to install Python via winget...
    winget install --id=Python.Python.3 --silent
    if errorlevel 1 (
        echo Failed to install Python. Please install it manually.
        pause
        exit /b 1
    )
    echo Python installed successfully.
) else (
    echo Python is installed.
)

echo Installing dependencies...
pip install -r requirements.txt

echo Compiling app.py with PyInstaller...
pyinstaller app.py --name=KARS-Updater --onefile --noconsole --icon=../../img/favicon.ico

pause