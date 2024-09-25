#!/bin/bash

# Update package lists
sudo apt update

# Install Xorg, Python3 Tkinter, and pip (with automatic yes to prompts)
sudo apt install xorg python3-tk python3-pip -y

# Install Python requirements
pip3 install -r requirements.txt

# Move and set up .xinitrc
mv xinitrc ~/.xinitrc
chmod +x ~/.xinitrc

# Set up X11 configuration
sudo mv xorg.conf /etc/X11/xorg.conf

# Set up systemd service for starting X
sudo mv setup.sh /etc/systemd/system/startx.service
sudo systemctl daemon-reload
sudo systemctl enable startx.service
sudo systemctl start startx.service

# Reboot the system
sudo reboot