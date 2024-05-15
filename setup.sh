#!/bin/bash

# Download defaults.json from the given URL and save as "defaults.json"
curl -o defaults.json https://raw.githubusercontent.com/shubhamakshit/pwdlv3/main/defaults.linux.json

# Ensure pip is installed by downloading and running get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python_installed=false

if command -v python &> /dev/null
then
    python_installed=true
    echo "Python is installed"
    python get-pip.py
    python -m pip install -r requirements.txt
elif command -v python3 &> /dev/null
then
    python_installed=true
    echo "Python3 is installed"
    python3 get-pip.py
    python3 -m pip install -r requirements.txt
else
    echo "Python is not installed"
    # exit if python is not installed
    exit 1
fi

# Clean up get-pip.py
rm get-pip.py

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if 'alias pwdl' is already present in ~/.bashrc
if ! grep -q "alias pwdl" ~/.bashrc
then
    # Add alias to ~/.bashrc
    echo "alias pwdl='$SCRIPT_DIR/pwdl.py'" >> ~/.bashrc
fi

# Source ~/.bashrc to make the alias available in the current session
source ~/.bashrc

# Notify the user to restart their terminal to apply the alias if not sourced
echo "Please restart your terminal or run 'source ~/.bashrc' to apply the alias."
