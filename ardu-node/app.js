//default stuff
var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');



var routes = require('./routes/index');
var users = require('./routes/users');

var app = express(); //var app = express.createServer();
var http = require('http').createServer(app).listen(3001);
var io = require('socket.io')(http);
var json2csv = require('json2csv');
var functions = require('./functions.js');
var mkdirp = require('mkdirp');
var sleep = require('sleep').sleep;

console.log(functions.test);
//maybe i haven't done something here.



//Stuff that dan required and did
//===============================

var url = require('url');
var fs = require('fs');

//Serial Port Stuff:
// TODO: open serial port desired by user.
var serialport = require('serialport');
var SerialPort = serialport.SerialPort;

serialport.list(function(err, ports){
  ports.forEach(function(port) {
    console.log(port.comName);
  });
});

var serialPort = new SerialPort('/dev/ttyACM0',{
  baudrate:57600,
  parser:serialport.parsers.readline('\n')
});


serialPort.on("open", function() {
  console.log('serport opened');
  toArdu();
});

serialPort.on('error', function(err) {
  console.log(err);
});


//function to export that writes to the serialport
toArdu = function(){
  console.log("sending something to the ardustat");
  sleep(1);
  serialPort.write("s0000");
}






var datastream = ""

tcpport = process.argv[3]
if (process.argc == 4) sample_rate = 100
else sample_rate = process.argv[4]

//===============================
//not sure if i need
var sys = require('sys');
//app.use('/flot',express


// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
//app.use(favicon(__dirname + '/public/favicon.ico'));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));


app.use('/', routes);
app.use('/users', users);







var test = "test";

// catch 404 and forward to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
    app.use(function(err, req, res, next) {
        res.status(err.status || 500);
        res.render('error', {
            message: err.message,
            error: err
        });
    });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
        message: err.message,
        error: {}
    });
});

var test = "test";
//exports - trying to export serialPort so can play with it. TODO: waiting on answers from charlie or stack overflow.  

//CSV writing stuff as well as GET calls used in other forwarder. TODO :update github page
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//writer variables initialized
var CSV_ON = false;
var labels = [];
var CSV_NAME = 'Data/untitled.csv';
var CSV_FOLDER = '';
var kill = false;
var command_list = [];
blen = 300; // buffer length


var ts = new Date().getTime();


var headers = {};
for(var j = 0; j<11;j++) {
	headers[j]=labels[j];
}

var count = 0;
var lastTime = 0;
	

//On Data fill a circular buf of the specified length
buf = ""
serialPort.on('data', function(data) {
   ts = new Date().getTime();
   buf += data;
   var n = buf.indexOf("GO.");
   buf = buf.substr(0,n+2)+","+ts+","+buf.substr(n+3,buf.length);
   if (buf.length > blen) buf = buf.substr(buf.length-blen,buf.length);
   //if writing is desired write buf to current CSV_NAME file
   if((CSV_ON == true) && (kill == false)){ 
        write2CSV(buf); 
        console.log("received data and sent to write2CSV");
   }
});

//Write to serial port

writer = function(req,res){	
	if(kill==false) {	
		toSend = req.originalUrl.replace("/write/","")
		toSend = decodeURIComponent(toSend);
        //command = toSend;
//hack to make sure that CSV is turned on - only problem is that it might not know which file to write to - might be better than nothing - anyway i dont think that this is the problem.
        if ((toSend.indexOf("p") > -1) || (toSend.indexOf("g") > -1)) CSV_ON = true;
        command_list.push(toSend);
        //queue.push(toSend);
    		//serialPort.write(toSend);
		res.send(toSend);
	}
	else { res.send("killed :("); }
});

setInterval(function()
{
    if (command_list.length > 0) {
        console.log("hopefully wrote command: "+command_list);
        console.log("CSV_ON is :", CSV_ON);
        console.log("CSV_NAME is :", CSV_NAME);
        serialPort.write(command_list.shift());
        
    }
    else {
        serialPort.write('s0000');
        //console.log("sent s0000");
    }
    command = '';
}, 50);



reader = function(req, res){
	if(kill==false) {
	    console.log("this is the reader");
	    console.log(buf);
	    res.send(buf);
	}
	else { res.send("killed :("); }
};

starter = function(req,res) {
	var temp = req.originalUrl.replace("/startCSV/","")
	temp = decodeURIComponent(temp);
	count = 0;
	if(CSV_ON == false) {
	if(temp!="") { CSV_NAME = 'Data/' + temp +'.csv'; }

//stuff to create folder if not already there  
    var CSV_PARTS = CSV_NAME.split("/");
    for (var i = 0; i < CSV_PARTS.length-1; i++){
    CSV_FOLDER += CSV_PARTS[i] + "/";
}
    CSV_FOLDER = CSV_FOLDER.substring(0,CSV_FOLDER.length-1);
    console.log("CSV_folder "+CSV_FOLDER);
    mkdirp(CSV_FOLDER, function(err) { 
});
	CSV_ON = true;
	res.send('CSV WRITING HAS BEGUN! Current output file: ' + CSV_NAME);
	console.log('writing data to: ' + CSV_NAME);
	}
	else {
	res.send('ALREADY WRITING TO FILE: ' + CSV_NAME);
	}
});
stopper = function(req,res) {
	if(CSV_ON == true) {
	CSV_NAME = 'Data/untitled.csv';
	res.send('CSV WRITING HAS BEEN MANUALLY STOPPED! Output file name reset to: ' + CSV_NAME);
	console.log('NOT writing to csv');
	CSV_ON = false;
	}
	else {
	res.send('WRITING ALREADY STOPPED!!!');
	}
});

name_setter = function(req,res) {
	var OLD_NAME = CSV_NAME;
	var temp = req.originalUrl.replace("/setName/","")
	CSV_NAME = 'Data/' + decodeURIComponent(temp)+'.csv'; //change here so that if there is a .csv then you don't attach this
	res.send('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
	console.log('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
});

killer = function(req,res) {
	serialPort.write("-0000");
	kill = true;
	console.log('python-forwarder interaction has been killed!');
	res.send('python-forwarder interaction has been killed!');
});

reviver =  function(req,res) {
	kill = false;
	console.log('python-forwarder interaction has resumed!');
	res.send('python-forwarder interaction has resumed!');
});

function write2CSV(chunk) {

	//start of document
    console.log("this is the chunk that gets sent to write2csv ", chunk);
    fs.appendFile('log.txt',chunk, function (err){
        if (err) throw err;
    });
	if(count==0) {
		//write column headers to csv file (optional) -- using 'writeFile' here to overwrite old data on file
		json2csv({data: headers, fields: ['0','1','2','3','4','5','6','7','8','9','10'], hasCSVColumnTitle: false}, function(err, csv) {
			if (err) console.log(err);
			fs.writeFile(CSV_NAME, csv, function(err) {
				if (err) throw err;
			});
		});
	count=1;
	}

	else{
	
		    var orig = chunk;
		    //if there is still a GO->ST pair left in chunk
		    while(orig.indexOf("GO")!=-1 && orig.indexOf("ST")!=-1) {
			    var start = orig.indexOf("GO");
			    //remove pre-'GO' data from both
			    chunk = orig.substr(start+3,orig.length);
			    orig = chunk;
			    var end = orig.indexOf("ST");
			    //remove post-'ST' data from current chunk
			    chunk = orig.substr(0,end-1);
			    //console.log(chunk+","+count);
			    //remove current chunk from original chunk for later analysis
			    orig = orig.substr(end+2,orig.length);
			    //create array of data values
			    var chunks = chunk.split(",");
                if (parseInt(chunks[0]) < 10000) {
                    console.log("woah chunky timestamp is small");
                    fs.appendFile('log.txt', "chunky timestamp is smaller than 10000", function (err) {
                        if (err) throw err;
                    });
                }
                else {
                
			        //don't write entries more than once
                    fs.appendFile('log.txt',"attempting to go into if statement", function (err){
                    if (err) throw err;
                    });
			        if(parseInt(chunks[0])>parseInt(lastTime)) {
                        
				        //count++;
				        foo = {};
				        for(var j = 0; j<11;j++) {
					        foo[j]=chunks[j];
				        }
				        //write data values to appropriate columns in csv 
				        json2csv({data: foo, fields: ['0','1','2','3','4','5','6','7','8','9','10'], hasCSVColumnTitle: false}, function(err, csv) {
					        if (err) console.log(err);
                            console.log("this is the part from write2CSV that gets written: ",csv);
                            fs.appendFile('log.txt',csv, function (err){
                                if (err) throw err;
                            });
					        fs.appendFileSync(CSV_NAME, csv)
				        });
				        //set lastTime to current time if current time is greater
				        lastTime=chunks[0];
			        }
                    else{
                        console.log("chunks timestamp is less than last time");
                        console.log("chunks[0] is ",chunks[0]," lastTime is ",lastTime);
                        fs.appendFile('log.txt',chunks[0] + " ", function (err){
                            if (err) throw err;
                        });
                        fs.appendFile('log.txt',lastTime + " ", function (err){
                            if (err) throw err;
                        });
                        chunk = '';
                        chunks = '';
                        }


                    }
              }
			
	}
	

}
//exporting a whole bunch of stuff to the router - might get charlie to help me clean this shit up.
module.exports = ({
  toArdu:toArdu(),
  serialPort:serialPort,
  test:test,
  app:app,
  reader:reader,
  writer:writer,
  starter:starter,
  stopper:stopper,
  name_setter:name_setter,
  killer: killer,
  reviver:reviver,
});
