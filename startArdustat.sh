#!/bin/bash

#echo -e "Pick one serial port number:"

#ls /dev/ttyACM*

NUM_PORTS=$(ls -l /dev/ttyACM* | wc -l)

#read port_num


rm /data/db/mongod.lock
sleep 1
mongod&
sleep 1
cd NodeJS/Ardustat_Viewer
node view_server.js&
sleep 1
google-chrome "http://localhost:8000"&
sleep 1

cd ../Ardustat_Control

for ((  i = 0 ;  i < $NUM_PORTS;  i++  ))
do
  PORT=/dev/ttyACM$i
  node expresserver.js $PORT $((8888+$i)) 500&
  sleep 1
  google-chrome "http://localhost:$((8888+$i))/cycler"&
  sleep 1
done

$SHELL


#while true; do
#    read -p "Start viewer?" yn
#    case $yn in
#        [Yy]* ) gnome-terminal -e "mongod"; cd NodeJS/Ardustat_Viewer; gnome-terminal -e "node view_server.js"; cd ../../;  break;;
#        [Nn]* ) break;;
#        * ) echo "Please answer yes or no.";;
#    esac
#done
