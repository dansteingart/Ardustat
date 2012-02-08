#!/bin/bash

echo -e "Pick one serial port number:"

ls /dev/ttyACM*

read port_num

PORT=/dev/ttyACM$port_num


while true; do
    read -p "Start viewer?" yn
    case $yn in
        [Yy]* ) gnome-terminal -e "mongod"; cd NodeJS/Ardustat_Viewer; gnome-terminal -e "node view_server.js"; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

cd ../Ardustat_Control

gnome-terminal -e "node expresserver.js $PORT $((8888+$port_num))"

google-chrome "http://localhost:$((8888+$port_num))" "http://localhost:8000"

