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
		echo "You are required to install python."
		echo "Please head to the page https://git-scm.com/download/linux and follow the instructions to install for your linux distribution."
		echo "Once you have installed it, please restart the one-click-comfyui.sh."
	elif [[ "$(uname -s)" == "Darwin" ]]; then
		echo "Python is not installed. Proceeding to download the installer for MacOS..."
		INSTALLER_URL="https://www.python.org/ftp/python/3.11.8/python-3.11.8-macos11.pkg"
		INSTALLER_PATH="/tmp/python-3.11.8-macos11.pkg"

		echo "Downloading Python 3.11.8 installer..."
		curl -o "$INSTALLER_PATH" "$INSTALLER_URL"

		if [[ $? -eq 0 ]]; then
			echo "Download complete. Opening the installer..."
			echo "Follow the on-screen instructions to complete the installation."
			open "$INSTALLER_PATH"
		else
			echo "Failed to download the installer. Please try again or visit:"
			echo "$INSTALLER_URL"
			echo "and install manually."
			exit 1
		fi
	fi
	echo "Press enter to exit the terminal then restart it by opening it again."
	read -p ""
	exit 1
fi

# Check if Git is installed
GIT_CMD=$(command -v git)

if [[ -n "$GIT_CMD" ]]; then
	echo "Git is already installed."
	git --version
else
	echo "Git is not installed."

	if [[ "$(uname -s)" == "Linux" ]]; then
		echo "You are required to install Git."
		echo "Please head to https://git-scm.com/download/linux for instructions specific to your Linux distribution."
		echo "Once installed, restart this script."
	elif [[ "$(uname -s)" == "Darwin" ]]; then
		echo "Git is not installed on your Mac."
		echo "Please visit https://git-scm.com/download/mac to download and install Git."
		echo "Follow the instructions on the website to complete the installation."
	fi

	echo "Press Enter to exit the terminal, then restart it by opening it again after installation."
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
