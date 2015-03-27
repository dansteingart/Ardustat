#!/bin/bash
cd pithy
if `forever list | grep -q "4001"`; then
    echo forever already running
else
	forever start index.js 4001
	forever start raw_shower.js 4004
fi
cd ..
npm start