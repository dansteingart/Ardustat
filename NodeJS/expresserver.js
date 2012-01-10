var http = require("http");
var url = require("url");
var fs = require('fs');
var glob = require('glob');
var qs = require('querystring');
var express = require('express'),
    app = express.createServer();
	app.use(express.bodyParser());
	app.use(app.router);

io = require('socket.io').listen(app);

var serialport = require("serialport")
var SerialPort = require("serialport").SerialPort

var serialPort = new SerialPort(glob.globSync("/dev/tty.u*")[0],{baudrate:57600,parser:serialport.parsers.readline("\n") });
var datastream = ""

app.use("/flot", express.static(__dirname + '/flot'));
app.use("/socket.io", express.static(__dirname + '/node_modules/socket.io/lib'));


app.get('/', function(req, res){
	indexer = fs.readFileSync('index.html').toString()
    res.send(indexer);
});

function setArduino(req,res)
{
	serialPort.write(req.body.fudge)
	console.log(req.body)
	res.send(req.body)
	
}

app.post('/senddata', setArduino,function(req, res,next){
	console.log(req.body)
	res.send(req.body)
	
});

fudge = "factor"

app.post('/getdata',function(req, res){
	res.send(req.app.settings)
});


function datadoer()
{
	return datastream
}

app.listen(8888);
console.log('Express server started on port %s', app.address().port);

function data_parse(data)
{
	parts = data.split(",")
	out = {}
	out['dac_set'] = parts[1]
	out['cell_adc'] = parts[2]
	out['dac_adc'] = parts[3]
	out['res_set'] = parts[4]
	out['gnd_adc'] = parts[8]
	
	return out
	
	
}



serialPort.on("data", function (data) {
	if (data.search("GO")>-1)
	{
	foo = data_parse(data);
	d = new Date().getTime()	
	foo['time'] = d
	 io.sockets.emit('new_data',{'ardudata':foo} )
	app.set('ardudata',foo)
	}
});


setInterval(function(){
	serialPort.write("s0000")}, 100)

