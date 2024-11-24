#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Mac"
    echo "Please manually install Python from https://www.python.org/downloads/macos/ under Stable Released labeled 'Download macOS 64-bit universal2 installer'"
    read -p "Press Enter to continue..."
    exit 0
fi

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "Python is already installed."
    python3 --version
    exit 0
fi

# Update package list
echo "Updating package list..."
sudo apt-get update -y

# Install Python
echo "Installing Python..."
sudo apt-get install -y python3 python3-pip

# Verify the installation
if command -v python3 &>/dev/null; then
    echo "Python successfully installed."
    python3 --version
else
    echo "Python installation failed."
    exit 1
fi