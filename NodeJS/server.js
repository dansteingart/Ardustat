var http = require("http");
var url = require("url");
var fs = require('fs');
var glob = require('glob');
var qs = require('querystring');

var serialport = require("serialport")
var SerialPort = require("serialport").SerialPort

var serialPort = new SerialPort(glob.globSync("/dev/tty.u*")[0],{baudrate:57600,parser:serialport.parsers.readline("\n") });
var datastream = ""


function onRequest(request, response) {

  indexer = fs.readFileSync('index.html').toString()
  console.log(request.method)
  var pathname = url.parse(request.url).pathname;
  if (pathname == "/senddata") senddata(request,response);
  if (pathname == "/getdata") getdata(request,response);

  	else 
  	{
	route(pathname);
 	response.writeHead(200, {"Content-Type": "html"});
 	response.write(indexer);
	foo = {}
 	foo = {'data':parseData(datastream)}
  	response.end();
	}
}

function senddata(request,response)
{
	if (request.method == 'POST') {
        var body = '';
        request.on('data', function (data) {
			
            body += data;

        });
        request.on('end', function () {
		   	foo = qs.parse(body);
			console.log(foo)
			response.writeHead(200,'OK',{"Content-Type": "text/html"})
			response.write(JSON.stringify(foo))
			console.log(response)
			response.end()
		

        });

    }


}



function route(pathname) 
{
  if (pathname.search("blink")>-1) serialPort.write(" ")
  else if (pathname.search("p")>-1) serialPort.write(pathname.replace("/",""))
  
  return pathname;
}


serialPort.on("data", function (data) {
	if (data.search("GO")>-1)
	{
	d = new Date().getTime()	
	datastream = d+","+data
	}
});


setInterval(function(){
	serialPort.write("s0000")}, 500)

http.createServer(onRequest).listen(8888);
console.log("Server has started.");

function parseData(string)
{
	return string.split(",")
}


