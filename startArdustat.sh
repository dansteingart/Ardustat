#!/bin/bash

echo -e "Pick one serial port number:"

ls /dev/ttyACM*

read port_num

PORT=/dev/ttyACM$port_num


while true; do
    read -p "Start viewer?" yn
    case $yn in
        [Yy]* ) gnome-terminal -e "mongod"; cd NodeJS/Ardustat_Viewer; gnome-terminal -e "node view_server.js"; cd ../../;  break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

cd NodeJS/Ardustat_Control

gnome-terminal -e "node expresserver.js $PORT $((8888+$port_num))"

google-chrome "http://localhost:$((8888+$port_num))/cycler" "http://localhost:$((8888+$port_num))/debug" "http://localhost:8000"
