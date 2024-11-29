#!/bin/bash

# You may need to give file execution permissions on Linux!
# chmod +x one-click-install.sh

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
	echo "Python is not installed. Please install Python 3.10.X/3.11.X with pip."
	if [[ "$(uname -s)" == "Linux" ]]; then
		echo "You will be prompted to install it now."
		sudo apt install python3
		sudo apt install python3-pip
		sudo apt install python3-venv
	fi
	echo "Press enter to exit the terminal and restart it."
	read -p ""
	exit 1
fi

# Upgrade pip using the detected Python command
$PYTHON_CMD -m pip install --upgrade pip
if [ $? -ne 0 ]; then
	echo "Failed to upgrade pip. Press enter to exit."
	read -p ""
	exit 1
fi

# Install required Python packages
echo "Installing required installer.py packages."
$PYTHON_CMD -m pip install requests tqdm
echo "Installing proxy packages."
$PYTHON_CMD -m pip install pydantic pillow websocket-client aiohttp
if [ $? -ne 0 ]; then
	echo "Failed to install the required packages. Press enter to exit."
	read -p ""
	exit 1
fi

# Run the installer script
echo "Running the installer.py script..."
$PYTHON_CMD installer.py
if [ $? -ne 0 ]; then
	echo "Installer script failed. Exiting."
	read -p ""
	exit 1
fi
