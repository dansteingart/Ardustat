#!/bin/bash
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
	arduinos=`ls -d /dev/* | grep tty[UA][SC][BM]`
	lines=`ls -d /dev/* | grep tty[UA][SC][BM] | wc -l`

fi
if [[ "$unamestr" == 'Darwin' ]]; then
	arduinos=`ls -d /dev/* | grep tty.usbmodem*`
	lines=`ls -d /dev/* | grep tty.usbmodem* | wc -l`
fi
if [[ $arduinos == "" ]]; then
	echo No arduinos found
	exit
fi
if [[ $lines == "1" ]]; then
	node expresserver.js $arduinos
	exit
fi
echo You appear to have multiple arduinos connected. Please select one:
select fname in $arduinos;
do
	node expresserver.js $fname
	break;
done
