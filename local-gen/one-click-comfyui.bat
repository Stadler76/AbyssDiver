@echo off
setlocal enabledelayedexpansion

:: Ensure the script runs in the directory of the batch file
cd /D "%~dp0"

echo Installing minimum requirements for one-click ComfyUI installer.

:: Check for 'py', 'python', or 'python3' in order and set PYTHON_CMD
set "PYTHON_CMD="
where py >nul 2>&1
if %errorlevel% equ 0 (
	set "PYTHON_CMD=py"
) else (
	where python >nul 2>&1
	if %errorlevel% equ 0 (
		set "PYTHON_CMD=python"
	) else (
		where python3 >nul 2>&1
		if %errorlevel% equ 0 (
			set "PYTHON_CMD=python3"
		)
	)
)

echo "%PYTHON_CMD%"

:: If Python command is still not set, install Python
if "%PYTHON_CMD%"=="" (
	echo Python not found. Installing Python...
	if exist install_python_windows.bat (
		call ./install_python_windows.bat
		if %errorlevel% neq 0 (
			echo Failed to install Python. Exiting.
			pause
			exit /b 1
		)
	) else (
		echo install_python_windows.bat not found. Please ensure it exists.
		pause
		exit /b 1
	)

	:: Retry Python detection after installation
	where py >nul 2>&1 && set "PYTHON_CMD=py"
	where python >nul 2>&1 && set "PYTHON_CMD=python"
	where python3 >nul 2>&1 && set "PYTHON_CMD=python3"

	if "%PYTHON_CMD%"=="" (
		echo Python installation failed or not found in PATH. Exiting.
		pause
		exit /b 1
	)
) else (
	echo Python found: %PYTHON_CMD%
)

:: Install required Python packages
echo Installing required Python packages...
%PYTHON_CMD% -m ensurepip
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
	echo Failed to install required Python packages. Exiting.
	exit /b 1
)

:: Run the installer script
echo Running the installer script...
%PYTHON_CMD% installer.py
if %errorlevel% neq 0 (
	echo Installer script failed. Exiting.
	pause
	exit /b 1
)

:: Pause before exiting
echo Installation completed successfully.
pause
exit /b
