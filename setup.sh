sudo apt update
sudo apt install xorg python3-tk python3-pip
pip3 install -r requirements.txt
mv xinitrc ~/.xinitrc
chmod +x ~/.xinitrc
mv xorg.conf /etc/X11/xorg.conf
echo "startx" >> ~/.bashrc