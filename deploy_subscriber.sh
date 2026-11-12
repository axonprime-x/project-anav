#!/bin/bash
set -e

REPO_URL="https://github.com/axonprime-x/project-anav.git"
INSTALL_DIR="/opt/project-anav-client"
BRANCH="subscriber-client"

echo "=== [ANAV] Provisioning Subscriber Node ==="

if [ ! -d "$INSTALL_DIR/.git" ]; then
    sudo git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
else
    cd "$INSTALL_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
fi

cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip fastapi uvicorn sqlite3

sudo chown -R anav-subscriber:anav-subscriber "$INSTALL_DIR"
echo "=== [ANAV] Subscriber Environment Ready ==="
