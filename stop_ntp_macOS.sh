#!/bin/bash

echo "Stopping NTP server..."

# Kill the NTP daemon
sudo pkill ntpd

echo "NTP server stopped!"