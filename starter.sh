#!/bin/bash
cd pithy
forever start index.js 4001
forever start raw_shower.js 4004
cd ..
npm start