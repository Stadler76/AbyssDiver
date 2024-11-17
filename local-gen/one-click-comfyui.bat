@echo off

@REM you may get a "SmartScreen" warning for this file!
@REM This is NORMAL and is done with any downloaded executable.

echo Installing minimum requirements for one-click comfyui installer.
call install_python.bat
py -m ensurepip
pip install --upgrade pip
pip install -r requirements.txt
py installer.py

pause
