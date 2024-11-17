#!/bin/bash

# You may need to give file execution permissions on Linux!
# chmod +x one-click-install.sh

echo "Installing minimum requirements for one-click ComfyUI installer."

# Check if Python is installed
if command -v python3 &>/dev/null; then
	echo "Python is already installed."
else
	echo "Python is not installed. Installing Python..."
	./install_python.sh
	if [ $? -ne 0 ]; then
		echo "Failed to install Python. Exiting."
		exit 1
	fi

	echo "Restarting the script..."
	exec "$0" "$@"
fi

# Ensure pip is installed and upgraded
echo "Ensuring pip is installed and upgrading it..."
python3 -m ensurepip --default-pip
if [ $? -ne 0 ]; then
	echo "Failed to ensure pip is installed. Exiting."
	exit 1
fi

python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
	echo "Failed to upgrade pip. Exiting."
	exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
	echo "Failed to install required Python packages. Exiting."
	exit 1
fi

# Run the installer script
echo "Running the installer script..."
python3 installer.py
if [ $? -ne 0 ]; then
	echo "Installer script failed. Exiting."
	exit 1
fi

echo "Installation completed successfully."
read -p "Press Enter to continue..." -n1 -s
