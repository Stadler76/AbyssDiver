#!/bin/bash

# You may need to give file execution permissions on Linux!
# chmod +x uninstall-comfyui.sh

echo "Installing minimum requirements for one-click ComfyUI installer."

# Check for 'py', 'python', or 'python3' in order
if command -v py &>/dev/null; then
	PYTHON_CMD="py"
elif command -v python &>/dev/null; then
	PYTHON_CMD="python"
elif command -v python3 &>/dev/null; then
	PYTHON_CMD="python3"
else
	PYTHON_CMD=""
fi

# If Python is found, print its version and proceed, otherwise install Python
if [[ -n "$PYTHON_CMD" ]]; then
	echo "Python is already installed."
	$PYTHON_CMD --version
else
	echo "Python is not installed. Please install python 3.10.X/3.11.X."
	echo "Once you do so, press enter to exit the terminal and restart it."
	read -p ""
	exit 1
fi

# Run the installer script
echo "Running uninstaller.py"
$PYTHON_CMD uninstaller.py
if [ $? -ne 0 ]; then
	echo "Installer script failed. Press enter to exit."
	read -p ""
	exit 1
fi
