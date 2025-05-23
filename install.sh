#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- CONFIGURATION ---
REPO_URL="https://github.com/confusedDip/collab-network.git"  # Replace this with your actual GitHub/Repo URL
APP_DIR="/usr/bin/authz"
SYMLINK="/usr/bin/clears"

echo "[1/6] Cloning the repository..."
git clone "$REPO_URL"
REPO_NAME=$(basename "$REPO_URL" .git)
cd "$REPO_NAME"

echo "[2/6] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[3/6] Setting up deployment directory at $APP_DIR..."
sudo mkdir -p "$APP_DIR"

echo "[4/6] Copying files to $APP_DIR..."
sudo cp -r * "$APP_DIR"

echo "[5/6] Updating permissions for privileged wrappers..."
sudo chmod +s "$APP_DIR/utilities/wrapper_network_dump"
sudo chmod +s "$APP_DIR/utilities/wrapper_supdate"

echo "[6/6] Creating symbolic link at $SYMLINK..."
sudo ln -sf "$APP_DIR/main.py" "$SYMLINK"
sudo chmod +x "$SYMLINK"

echo "✅ Installation complete. You can now run the tool with: clears"
