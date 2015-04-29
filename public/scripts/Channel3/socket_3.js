var socket = io();
//no need to be complicated. Have a different socket.js script for each. Server globally emits message, with channel number as type - instruction as message. 
channel = 'ch3'

socket.on('connection', function(msg) {
	console.log(msg)
});

socket.on(channel, function(msg){
	console.log('message has been received on channel ' + channel + 'the message is ' + msg);
	if (msg == 'stop message'){
		showReturnButton();
		testOver()
	}
	else if (msg == 'calibration finished'){
		goCalibrationFinished()
	}
});

    
