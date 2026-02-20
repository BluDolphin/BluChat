#!/bin/bash
# restart NetworkManager when wlan0 disappeared
sudo systemctl restart NetworkManager

while true; do
    if [ "$(nmcli -g GENERAL.STATE dev show wlan0)" = "30 (disconnected)" ]; then
        echo "wlan0 disconnected"
        sudo systemctl restart NetworkManager
    fi
    echo "wlan0 state: $(nmcli -g GENERAL.STATE dev show wlan0)"
    sleep 30
done