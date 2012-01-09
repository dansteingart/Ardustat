var http = require("http");
var url = require("url");

var serialport = require("serialport")
var SerialPort = require("serialport").SerialPort
var serialPort = new SerialPort("/dev/tty.usbmodemfd131",{baudrate:57600,parser:serialport.parsers.readline("\n") });
var datastream = ""

function onRequest(request, response) {
  var pathname = url.parse(request.url).pathname;
  console.log("Request for " + pathname + " received.");
  route(pathname);
  response.writeHead(200, {"Content-Type": "text/plain"});
  response.write("Hello World,"+pathname);
  foo = {}
  foo = {'data':parseData(datastream)}
  response.write(JSON.stringify(foo));
  response.end();
}




function route(pathname) 
{
  console.log("About to route a request for " + pathname);
  if (pathname.search("blink")>-1) serialPort.write(" ")
  else if (pathname.search("p")>-1) serialPort.write(pathname.replace("/",""))
  
  return pathname;
}


serialPort.on("data", function (data) {
	datastream = data;
	console.log(data);
});


setInterval(function(){
	serialPort.write("s0000")}, 500)

http.createServer(onRequest).listen(8888);
console.log("Server has started.");

function parseData(string)
{
	return string.split(",")
}