#!/bin/bash

# You may need to give file execution permissions on Linux!
# chmod +x one-click-install.sh

echo Installing minimum requirements for one-click comfyui installer.

if command -v python3 &>/dev/null; then
	# installed already
else
	echo "Restarting the script..."
	call install_python.sh
	exec "$0" "$@"
fi


py -m ensurepip
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m py installer.py
read -p "Press enter to continue..." -n1 -s
