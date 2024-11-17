#!/bin/bash

# You may need to give file execution permissions on Linux!
# chmod +x one-click-install.sh

echo Installing minimum requirements for one-click comfyui installer.
call install_python.sh
py -m ensurepip
pip install --upgrade pip
pip install -r requirements.txt
py installer.py
read -p "Press enter to continue..." -n1 -s
