#!/bin/bash

# Ensure ntpd is installed
if ! brew list ntp &>/dev/null; then
    echo "ntpd is not installed. Install it using:"
    echo "   brew install ntp"
    exit 1
fi

# Get local IP address
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

if [[ -z "$IP_ADDRESS" ]]; then
    echo "Unable to determine local IP address."
    exit 1
fi

# Start ntpd server
echo "Starting NTP server on $IP_ADDRESS"
sudo /opt/homebrew/sbin/ntpd -g -c /opt/homebrew/etc/ntp.conf

# Check status
echo "NTP server started!"

# Retry `ntpq -p` until we get a valid response
for i in {1..10}; do
    sleep 1  # Wait 1 second between checks
    output=$(ntpq -p 2>&1)
    if [[ ! "$output" =~ "No association ID's returned" ]]; then
        echo "NTP server is synced!"
        echo "$output"
        
        exit 0
    fi
    echo "🔄 Waiting for associations... ($i/10)"
done

# If we never get a valid response, show a message
echo "NTP server did not sync within the expected time. Try running 'ntpq -p' manually."
exit 1