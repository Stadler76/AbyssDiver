setlocal enabledelayedexpansion

@echo off

@REM you may get a "SmartScreen" warning for this file!
@REM This is NORMAL and is done with any downloaded executable.

@REM set the directory to the batch file's directory
cd /D "%~dp0"

echo Installing minimum requirements for one-click comfyui installer.

python --version >nul 2>&1
if "!errorlevel!"=="0" (
	call install_python.bat

	echo Restarting the batch file...
	call "%~dpnx0"
	exit /b
)

py -m ensurepip
pip install --upgrade pip
pip install -r requirements.txt
py installer.py

pause
