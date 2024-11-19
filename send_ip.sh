#!/bin/bash

# Function to check internet connectivity
check_internet() {
    # Ping a reliable public server (Google DNS)
    ping -q -c 1 -W 1 8.8.8.8 >/dev/null 2>&1
    return $?
}
# Wait until connected to the internet
echo "Waiting for an internet connection..."
while ! check_internet; do
    sleep 2
done
echo "Connected to the internet!"

IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "IP address ${IP_ADDRESS}"

# Adam's Duke VM
SERVER_URL="http://67.159.75.8:5000"

# Send IP address to the Duke VM
curl -G "${SERVER_URL}/${IP_ADDRESS}"