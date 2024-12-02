@echo off
setlocal enabledelayedexpansion

:: Ensure the script runs in the directory of the batch file
cd /D "%~dp0"

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

:: If Python command is still not set, install Python
if "%PYTHON_CMD%"=="" (
	call install_git_python.bat
	pause
	exit /b 1
)

:: Check for the git command
where git >nul 2>&1
if %errorlevel% neq 0 (
	call install_git_python.bat
	pause
	exit /b 1
)

:: Install required Python packages
echo Upgrading pip.
"%PYTHON_CMD%" -m pip install --upgrade pip
echo Installing installer.py packages.
"%PYTHON_CMD%" -m pip install tqdm requests

:: Run the installer.py
echo Running the installer.py
call "%PYTHON_CMD%" installer.py

echo Press enter to exit...
pause
