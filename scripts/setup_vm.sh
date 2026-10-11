#!/bin/bash
# setup_vm.sh — Run once on a fresh Ubuntu 22.04 VM to install Docker
# and deploy the Economic Shock Detector stack.
#
# Usage:
#   chmod +x setup_vm.sh
#   ./setup_vm.sh

set -e

echo "==> Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "==> Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg lsb-release

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

echo "==> Adding current user to docker group (re-login required)..."
sudo usermod -aG docker "$USER"

echo "==> Enabling Docker on boot..."
sudo systemctl enable docker
sudo systemctl start docker

echo "==> Verifying Docker installation..."
docker --version
docker compose version

echo ""
echo "==> Docker installed successfully."
echo ""
echo "Next steps:"
echo "  1. Re-login or run: newgrp docker"
echo "  2. Clone your project: git clone <your-repo-url>"
echo "  3. cd into the project root"
echo "  4. Copy .env.example to .env and fill in secrets"
echo "  5. Run: docker compose up --build -d"
echo "  6. Frontend: http://<VM_IP>:8501"
echo "  7. Backend API docs: http://<VM_IP>:8000/docs"