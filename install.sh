#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- CONFIGURATION ---
APP_DIR="/usr/bin/authz"
SYMLINK="/usr/bin/clears"
CN_DIR="/etc/project"


echo "[1/9] Installing Python dependencies..."
sudo pip3 install -r requirements.txt
sudo apt install acl -y

echo "[2/9] Setting up deployment directory at $APP_DIR..."
sudo mkdir -p "$APP_DIR"

echo "[3/9] Remove compiled C wrappers..."
rm utilities/wrapper_network_dump
rm utilities/wrapper_supdate

echo "[4/9] Copying files to $APP_DIR..."
sudo cp -r * "$APP_DIR"

echo "[5/9] Updating the owner..."
sudo chown -R root "$APP_DIR"

echo "[6/9] Compiling C wrappers..."
gcc utilities/wrapper_network_dump.c -o wrapper_network_dump
gcc utilities/wrapper_supdate.c -o wrapper_supdate
sudo mv wrapper_network_dump wrapper_supdate "$APP_DIR/utilities/"

echo "[7/9] Updating permissions for privileged wrappers..."
sudo chown -R root "$APP_DIR/utilities/wrapper_network_dump"
sudo chmod +s "$APP_DIR/utilities/wrapper_network_dump"
sudo chown -R root "$APP_DIR/utilities/wrapper_supdate"
sudo chmod +s "$APP_DIR/utilities/wrapper_supdate"

echo "[8/9] Creating symbolic link at $SYMLINK..."
sudo ln -sf "$APP_DIR/main.py" "$SYMLINK"
sudo chmod +x "$SYMLINK"

echo "[9/9] Setting up directory at $CN_DIR for Collaboration Networks..."
sudo mkdir -p "$CN_DIR"

echo "✅ Installation complete. You can now run the tool with: clears."
echo "For starter, run 'clears help'"
