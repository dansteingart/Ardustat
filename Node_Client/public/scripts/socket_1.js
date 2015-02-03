var socket = io();
//testing things - this is how to submit something
// test
socket.on('console message', function(msg){
  console.log(msg)
});
// on stop message from server - stop things.
socket.on('stop message', function(msg){
  console.log('stop message called')
  showReturnButton();
  testOver();
});
// changed to an ajax request. 

