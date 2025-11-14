#!/bin/bash

# Shepherd Raspberry Pi Setup Script
# This script sets up both frontend and backend apps for the Shepherd project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi or compatible system
print_status "Starting Shepherd Raspberry Pi setup..."

# 1. Clone repo and init submodules
print_status "Cloning repository and initializing submodules..."
if [ ! -d "shepherd" ]; then
    git clone https://github.com/jasonbirchler/shepherd.git
    cd shepherd
    git submodule update --init
    print_status "Repository cloned and submodules initialized"
else
    print_warning "Repository already exists, skipping clone..."
    cd shepherd
    git submodule update --init
    print_status "Submodules updated"
fi

# 2. Install packages
print_status "Installing system packages..."
sudo apt update
sudo apt-get install -y \
    libasound2-dev \
    libatlas-base-dev \
    libcairo2-dev \
    libcurl4-openssl-dev \
    libfreetype6-dev \
    libglu1-mesa-dev \
    libjack-jackd2-dev \
    libssl-dev \
    libusb-1.0-0-dev \
    libwebkit2gtk-4.0-dev \
    libx11-dev \
    libxcomposite-dev \
    libxcursor-dev \
    libxext-dev \
    libxinerama-dev \
    libxrandr-dev \
    libxrender-dev \
    mesa-common-dev \
    openssl \
    python3-dev \
    xvfb

print_status "System packages installed successfully"

# 3. Build backend app
print_status "Building backend application..."
cd ~/shepherd/Shepherd/Builds/LinuxMakefile
make CONFIG=Release -j4
print_status "Backend app built successfully"

# Return to root directory
cd ~/shepherd

# 4. Create JSON files only if they don't already exist
print_status "Setting up configuration files..."
mkdir -p ~/Documents/Shepherd

if [ ! -f ~/Documents/Shepherd/backendSettings.json ]; then
    touch ~/Documents/Shepherd/backendSettings.json
    print_status "Created backendSettings.json"
else
    print_warning "backendSettings.json already exists, skipping..."
fi

if [ ! -f ~/Documents/Shepherd/hardwareDevices.json ]; then
    touch ~/Documents/Shepherd/hardwareDevices.json
    print_status "Created hardwareDevices.json"
else
    print_warning "hardwareDevices.json already exists, skipping..."
fi

# 5. Setup Python environment
print_status "Setting up Python virtual environment..."
cd ~/shepherd/Push2Controller/

if [ ! -d "venv" ]; then
    python -m venv venv
    print_status "Python virtual environment created"
else
    print_warning "Virtual environment already exists, skipping creation..."
fi

# Activate virtual environment
source venv/bin/activate
print_status "Python virtual environment activated"

# 6. Install Python requirements
print_status "Installing Python requirements..."
pip install -r requirements.txt
print_status "Python requirements installed successfully"

# Deactivate virtual environment (services will handle activation when they run)
deactivate

# 7. Setup services for both frontend and backend
print_status "Setting up systemd services..."

# Check if service files exist
if [ -f ~/shepherd/Shepherd/RaspberryPi/services/shepherd ]; then
    sudo cp ~/shepherd/Shepherd/RaspberryPi/services/shepherd /lib/systemd/system/shepherd.service
    print_status "Shepherd service copied"
else
    print_warning "Shepherd service file not found, skipping..."
fi

if [ -f ~/shepherd/Shepherd/RaspberryPi/services/push2controller ]; then
    sudo cp ~/shepherd/Shepherd/RaspberryPi/services/push2controller /lib/systemd/system/shepherd_controller.service
    print_status "Push2Controller service copied"
else
    print_warning "Push2Controller service file not found, skipping..."
fi

# Enable services (only if files were copied)
if [ -f /lib/systemd/system/shepherd.service ]; then
    sudo systemctl enable shepherd
    sudo systemctl start shepherd
    print_status "Shepherd service started"
fi

if [ -f /lib/systemd/system/shepherd_controller.service ]; then
    sudo systemctl enable shepherd_controller
    sudo systemctl start shepherd_controller
    print_status "Push2Controller service started"
fi

print_status "Setup completed successfully!"
print_status "Services have been enabled for auto-start on boot."
print_status ""
print_status "To start services immediately (optional):"
print_status "  sudo systemctl start shepherd"
print_status "  sudo systemctl start shepherd_controller"
print_status ""
print_status "To check service status:"
print_status "  sudo systemctl status shepherd"
print_status "  sudo systemctl status shepherd_controller"
