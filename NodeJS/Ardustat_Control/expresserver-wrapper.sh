#!/bin/bash

firstrun=`sed -n '1p' ./config`				#The first line of the file named 'config'
if [[ "$firstrun" == 'firstrun' ]]; then
	echo "First run. Installing node.js libraries..."
	bash ./initializeNodeJS.sh
	rm ./config
	touch ./config
	echo notfirstrun > ./config
	echo "Finished installing node.js libraries"
fi

unamestr=`uname`							#The architecture of the machine
if [[ "$unamestr" == 'Linux' ]]; then
	arduinos=`ls -d /dev/* | grep tty[UA][SC][BM]` 				#anything of the form /dev/ttyACM* or /dev/ttyUSB*
	numofarduinos=`ls -d /dev/* | grep tty[UA][SC][BM] | wc -l` #number of results returned

fi
if [[ "$unamestr" == 'Darwin' ]]; then
	arduinos=`ls -d /dev/* | grep tty.usbmodem*`
	numofarduinos=`ls -d /dev/* | grep tty.usbmodem* | wc -l`  #Number of results returned
fi
if [[ $arduinos == "" ]]; then
	echo No arduinos found
	exit
fi
if [[ $numofarduinos == "1" ]]; then
	node expresserver.js $arduinos
	exit
fi
echo You appear to have multiple arduinos connected. Please select one:
select fname in $arduinos;
do
	node expresserver.js $fname
	break;
done
