#!/bin/bash

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "Python is already installed."
    python3 --version
    exit 0
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Mac"
    echo "Please manually install Python from https://www.python.org/downloads/macos/ under Stable Released labeled 'Download macOS 64-bit universal2 installer'"
    read -p "Press Enter to continue..."
    exit 0
else
    echo "Linux"
    echo "Please manually install Python using the following guide: https://www.geeksforgeeks.org/how-to-install-python-on-linux/"
    echo "Preferably use Python 3.8 - 3.12"
    echo "ALSO download pip along with Python."
    read -p "Press Enter to continue..."
    exit 0
fi

# Verify the installation
if command -v python3 &>/dev/null; then
    echo "Python successfully installed."
    python3 --version
else
    echo "Python installation failed."
    exit 1
fi
