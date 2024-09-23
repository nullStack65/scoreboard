#!/bin/sh
cd ~
rm -rf scoreboard
git clone https://github.com/nullStack65/scoreboard.git
exec /usr/bin/python3 ~/scoreboard/main.py