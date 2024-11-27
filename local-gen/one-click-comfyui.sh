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
	echo "Python is not installed. Installing Python..."
	./install_python_linux_macos.sh
	if [ $? -ne 0 ]; then
		echo "Failed to install Python. Exiting."
		exit 1
	fi

	echo "Restarting the script..."
	exec "$0" "$@"
fi

# Upgrade pip using the detected Python command
$PYTHON_CMD -m pip install --upgrade pip
if [ $? -ne 0 ]; then
	echo "Failed to upgrade pip. Exiting."
	exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
	echo "Failed to install required Python packages. Exiting."
	exit 1
fi

# Run the installer script
echo "Running the installer script..."
$PYTHON_CMD installer.py
if [ $? -ne 0 ]; then
	echo "Installer script failed. Exiting."
	read -p ""
	exit 1
fi

echo "Installation completed successfully."
read -p "Press Enter to continue..." -n1 -s
