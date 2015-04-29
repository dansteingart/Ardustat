#!/bin/bash
if `ping -c 1 google.com | grep -q "64 bytes"`; then
    echo internet up
else
    echo internet down
    nmcli nm enable false
    nmcli nm enable true
    nmcli c up id puwireless
fi
