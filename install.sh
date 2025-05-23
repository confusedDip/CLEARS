#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- CONFIGURATION ---
APP_DIR="/usr/bin/authz"
SYMLINK="/usr/bin/clears"


echo "[1/5] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[2/5] Setting up deployment directory at $APP_DIR..."
sudo mkdir -p "$APP_DIR"

echo "[3/5] Copying files to $APP_DIR..."
sudo cp -r * "$APP_DIR"

echo "[4/5] Updating permissions for privileged wrappers..."
sudo chmod +s "$APP_DIR/utilities/wrapper_network_dump"
sudo chmod +s "$APP_DIR/utilities/wrapper_supdate"

echo "[5/5] Creating symbolic link at $SYMLINK..."
sudo ln -sf "$APP_DIR/main.py" "$SYMLINK"
sudo chmod +x "$SYMLINK"

echo "✅ Installation complete. You can now run the tool with: clears."
echo "For starter, run 'clears help'"
