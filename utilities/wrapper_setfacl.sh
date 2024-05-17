#!/bin/bash

# Ensure correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 group resource_path context"
    exit 1
fi

# Extract arguments
action="$1"
resource_path="$2"
context="$3"

# Execute the setfacl command with sudo privileges
sudo setfacl -"${action}" "g:${context}" "${resource_path}"
