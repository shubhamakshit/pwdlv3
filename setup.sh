#!/bin/bash

# Download defaults.json from the given URL and save as "defaults.json"
curl -o defaults.json https://raw.githubusercontent.com/shubhamakshit/pwdlv3/main/defaults.linux.json

# Rest of your setup script goes here

# check if python/python3 is installed (if installed then install required packages)
if command -v python &> /dev/null
then
    echo "Python is installed"
    python -m pip install -r requirements.txt
elif command -v python3 &> /dev/null
then
    echo "Python3 is installed"
    python3 -m pip install -r requirements.txt
else
    echo "Python is not installed"
    # exit if python is not installed
    exit 1
fi


# Check if 'alias pwdl' is already present in ~/.bashrc
if ! grep -q "alias pwdl" ~/.bashrc
then
    # Check if python3 is available
    if command -v python3 &> /dev/null
    then
        echo "alias pwdl='python3 pwdl.py'" >> ~/.bashrc
    else
        # Fall back to python if python3 is not available
        echo "alias pwdl='python pwdl.py'" >> ~/.bashrc
    fi
fi



