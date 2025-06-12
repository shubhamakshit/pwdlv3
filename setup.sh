#!/bin/bash

# Function to download and install pip
install_pip() {
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    if [[ $os != "Android" ]]; then
        python get-pip.py
    fi
    rm get-pip.py
}

# Function to install requirements
install_requirements() {
    if command -v python &> /dev/null; then
        echo "Python is installed"
        install_pip
        python -m pip install -r requirements.txt
    elif command -v python3 &> /dev/null; then
        echo "Python3 is installed"
        install_pip
        python3 -m pip install -r requirements.txt
    else
        echo "Python is not installed"
        exit 1
    fi
}

# Function to download and install tools
install_tools() {
    local tool=$1
    local url="https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/$os/$arch/$tool"
    curl -o $SCRIPT_DIR/bin/$tool $url
    chmod +x $SCRIPT_DIR/bin/$tool
}

# Main script execution
arch=$(uname -m)
os=$(uname -o)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p $SCRIPT_DIR/bin

# Download defaults.json
curl -o preferences.json https://raw.githubusercontent.com/shubhamakshit/pwdlv3/main/defaults.linux.json

# Install Python requirements
install_requirements

# Install mp4decrypt and vsd
install_tools "mp4decrypt"
install_tools "vsd"

# Check if -f flag is passed to install ffmpeg
if [[ $1 == "-f" ]]; then
    install_tools "ffmpeg"
    # Add bin to PATH in .bashrc if not already added
    if ! grep -q "export PATH=\$PATH:$SCRIPT_DIR/bin" ~/.bashrc; then
        echo "export PATH=\$PATH:$SCRIPT_DIR/bin" >> ~/.bashrc
    fi
fi

# Check if 'alias pwdl' is already present in ~/.bashrc
if ! grep -q "alias pwdl" ~/.bashrc; then
    echo "alias pwdl='python3 $SCRIPT_DIR/pwdl.py'" >> ~/.bashrc
fi

# Source ~/.bashrc to make changes available in the current session
source ~/.bashrc

# Notify the user
echo "Please restart your terminal or run 'source ~/.bashrc' to apply the alias and path changes."
