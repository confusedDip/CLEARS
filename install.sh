#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- CONFIGURATION ---
APP_DIR="/usr/bin/authz"
SYMLINK="/usr/bin/clears"


echo "[1/7] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[2/7] Setting up deployment directory at $APP_DIR..."
sudo mkdir -p "$APP_DIR"

echo "[3/7] Remove compiled C wrappers..."
rm utilities/wrapper_network_dump
rm utilities/wrapper_supdate

echo "[4/7] Copying files to $APP_DIR..."
sudo cp -r * "$APP_DIR"

echo "[5/7] Compiling C wrappers..."
gcc utilities/wrapper_network_dump.c -o wrapper_network_dump
gcc utilities/wrapper_supdate.c -o wrapper_supdate
sudo mv wrapper_network_dump wrapper_supdate "$APP_DIR/utilities/"

echo "[6/7] Updating permissions for privileged wrappers..."
sudo chmod +s "$APP_DIR/utilities/wrapper_network_dump"
sudo chmod +s "$APP_DIR/utilities/wrapper_supdate"

echo "[7/7] Creating symbolic link at $SYMLINK..."
sudo ln -sf "$APP_DIR/main.py" "$SYMLINK"
sudo chmod +x "$SYMLINK"

echo "✅ Installation complete. You can now run the tool with: clears."
echo "For starter, run 'clears help'"
