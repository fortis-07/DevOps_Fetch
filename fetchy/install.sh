#!/bin/bash

# Install Python and pip if not already installed
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# Install required Python packages
pip3 install -r requirements.txt

# Copy the main script to /usr/local/bin
sudo cp devopsfetch.py /usr/local/bin/devopsfetch
sudo chmod +x /usr/local/bin/devopsfetch

# Set up systemd service
sudo cp devopsfetch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable devopsfetch.service
sudo systemctl start devopsfetch.service

echo "DevOpsFetch has been installed and the service has been started."
