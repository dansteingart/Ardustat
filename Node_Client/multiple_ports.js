// just a boy trying to open multiple serial ports without program crashing...

var serialport = require('serialport');
var SerialPort = serialport.SerialPort;

//can maybe write this synchronously
devs = []

serialport.list(function(err, ports){
  console.log('ports and shit')
  ports.forEach(function(port) {
    console.log(' these are the port names ' + port.comName);
    if (port.comName.indexOf('modem') > -1)
    {
      //devs.push(port.comName)
    }
  });
  //startserial()
});

devs = ['/dev/tty.usbmodemfd121']
var ports = [];
//startserial = function() {
for (var i = 0; i < devs.length; i++) {
    console.log('this is where we are opening a serial port ' + devs[i]);
    var port = new SerialPort(devs[i],{ baudrate:57600, parser: serialport.parsers.readline("\n") });
    ports.push(port);
}
//}

for (var i = 0; i < ports.length; i++) {
  setupHandlers(ports[i]);
}

function setupHandlers(port) {
  port.on("open", function (path) {
  	console.log('serial port is open ' + port )
    port.write("Helo World\n", function(err,res) {
       if(err) console.log('err ' + err);
         console.log('results ' + res);
     });         

     port.on("data", function (data) {
       console.log("here: "+data);
     });
  });
}


t2 = setInterval(function()
{
  ports[0].write('s0000')
  console.log('wrote some stuff')
}, 500);