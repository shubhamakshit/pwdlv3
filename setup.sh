#!/bin/bash

# Download defaults.json from the given URL and save as "defaults.json"
curl -o defaults.json https://raw.githubusercontent.com/shubhamakshit/pwdlv3/main/defaults.linux.json

# Ensure pip is installed by downloading and running get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python_installed=false

# get architecture and os
# supported (linux64 , linuxarm, androidaarch64)

arch=$(uname -m)
os=$(uname -o)

if command -v python &> /dev/null
then
    python_installed=true
    echo "Python is installed"
    if [[ $os == "Android" ]]
    then
        echo "Python is installed but get pip not supported on android"
    else
        python get-pip.py
    fi
    python -m pip install -r requirements.txt 
elif command -v python3 &> /dev/null
then
    python_installed=true
    echo "Python3 is installed"
    if [[ $os == "Android" ]]
    then
        echo "Python is installed but get pip not supported on android"
    else
        python get-pip.py
    fi
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

mp4decrypt_url="https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/$os/$arch/mp4decrypt"
vsd_url="https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/$os/$arch/vsd"

# download mp4decrypt and vsd to bin
mkdir -p $SCRIPT_DIR/bin
curl -o $SCRIPT_DIR/bin/mp4decrypt $mp4decrypt_url
curl -o $SCRIPT_DIR/bin/vsd $vsd_url
chmod +x $SCRIPT_DIR/bin/*

# Check if 'alias pwdl' is already present in ~/.bashrc
if ! grep -q "alias pwdl" ~/.bashrc
then
    # Add alias to ~/.bashrc
    echo "alias pwdl='python3 $SCRIPT_DIR/pwdl.py'" >> ~/.bashrc
fi

# Source ~/.bashrc to make the alias available in the current session
source ~/.bashrc

# Notify the user to restart their terminal to apply the alias if not sourced
echo "Please restart your terminal or run 'source ~/.bashrc' to apply the alias."
