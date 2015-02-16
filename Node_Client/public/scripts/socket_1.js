var socket = io();
//testing things - this is how to submit something
// test
socket.on('console message', function(msg){
  console.log(msg)
});
// on stop message from server - stop things.
// this needs to be made more specific
socket.on('stop message', function(msg){
  console.log('stop message called')
  showReturnButton();
  testOver();
});
// changed to an ajax request. 

socket.on('calibration', function(msg){
  console.log('calibration called with this message '+msg);
  if (msg == 'finished'){
    //call a function in calibration.js
    goCalibrationFinished()
  }
});
    
