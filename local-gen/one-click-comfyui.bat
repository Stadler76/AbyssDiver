@echo off
setlocal enabledelayedexpansion

:: Ensure the script runs in the directory of the batch file
cd /D "%~dp0"

echo Installing minimum requirements for one-click ComfyUI installer.

:: Check if Python is installed
python --version >nul 2>&1
if "!errorlevel!" NEQ "0" (
	echo Python is not installed. Installing Python...
	call ./install_python_windows.bat
	if "!errorlevel!" NEQ "0" (
		echo Failed to install Python. Exiting.
		exit /b 1
	)

	echo Restarting the batch file...
	call "%~dpnx0"
	exit /b
)

:: Ensure pip is installed and upgraded
echo Ensuring pip is installed and upgrading it...
py -m ensurepip
if "!errorlevel!" NEQ "0" (
	echo Failed to ensure pip is installed. Exiting.
	exit /b 1
)

py -m pip install --upgrade pip
if "!errorlevel!" NEQ "0" (
	echo Failed to upgrade pip. Exiting.
	exit /b 1
)

:: Install required Python packages
echo Installing required Python packages...
py -m pip install -r requirements.txt
if "!errorlevel!" NEQ "0" (
	echo Failed to install required Python packages. Exiting.
	exit /b 1
)

:: Run the installer script
echo Running the installer script...
py installer.py
if "!errorlevel!" NEQ "0" (
	echo Installer script failed. Exiting.
	pause
	exit /b 1
)

:: Pause before exiting
echo Installation completed successfully.
pause
exit /b
