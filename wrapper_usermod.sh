#!/bin/bash

# Ensure correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 correct_context user"
    exit 1
fi

# Extract arguments
correct_context="$1"
user="$2"

# Execute the usermod command with sudo privileges
sudo usermod -aG "${correct_context}" "${user}"
