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
	echo Python not found.
	echo Please head to https://www.python.org/downloads/release/python-311/ and install python with the "Windows x86-64 MSI installer".
	echo Make sure to install in the AppData directory
	echo and have "Add to PATH" selected.\
	echo Once you have done so, close the terminal and run the batch file again.
	echo Press enter to exit...
	pause
	exit /b 1
)

:: Run the uninstaller.py
echo Running the uninstaller.py
call %PYTHON_CMD% uninstaller.py

echo Press enter to exit...
pause
