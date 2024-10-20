#!/bin/bash

# Directory to search, default is the current directory
directory=${1:-.}

# Find all .py files, excluding __pycache__, and calculate their total size
total_size=$(find "$directory" -type f -name "*.py" ! -path "*/__pycache__/*" -exec du -ch {} + | grep total$ | awk '{print $1}')

# Output the total size
echo "Total size of Python files in '$directory' (excluding __pycache__): $total_size"

