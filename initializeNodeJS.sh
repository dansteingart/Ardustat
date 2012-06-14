#!/bin/bash
rm -rf ./NodeJS/Ardustat_Control/node_modules/
cd ./NodeJS/Ardustat_Control
npm install express socket.io serialport mongoskin
