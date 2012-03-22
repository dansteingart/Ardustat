#!/bin/bash


# This script takes care of setting up a new laptop for Ardustat use. You may need to run "chmod 777 installArdustat.sh on
# on this file to make it work.

cd ..
wget https://github.com/dansteingart/Ardustat/zipball/master
unzip master -d ArdustatNew
rm master
cp -rf ArdustatNew Ardustat
rm -rf ArdustatNew
