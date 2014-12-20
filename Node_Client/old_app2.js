//default stuff

//TODO: change dependencies in the package.json 
//TODO: change the way am getting bower__components. (right now its manual)
//TODO: change firmware so that it prints out last command that wasn't 's0000'

//requirements from npm
var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var mkdirp = require('mkdirp');
var sleep = require('sleep').sleep;
var url = require('url');
var fs = require('fs');
var sys = require('sys');

//ones I probably don't need
var squenty = require('sequenty');
var urllib = require('urllib');

//requirements from files
var routes = require('./routes/index');
var users = require('./routes/users');
var json2csv = require('json2csv');
var functions = require('./functions.js');

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
  console.log('serial port opened yay');
});

serialPort.on('error', function(err) {
  console.log(err);
});

//actual setup stuff
var app = express(); //var app = express.createServer();
var http = require('http').createServer(app).listen(3001);
var io = require('socket.io')(http);

//this is stuff for the socket communication I think
var datastream = ""
tcpport = process.argv[3]
if (process.argc == 4) sample_rate = 100
else sample_rate = process.argv[4]

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
        //console.log("received data and sent to write2CSV");
   }
});


//TODO: check with dan if having the queuer thing like this a good idea - means that when i send a command i miss a read -- I think that is great!
setInterval(function()
{
    if (command_list.length > 0) {
        console.log("hopefully wrote command: "+command_list);
        //console.log("CSV_ON is :", CSV_ON);
        //console.log("CSV_NAME is :", CSV_NAME);
        serialPort.write(command_list.shift());
        
    }
    else {
        serialPort.write('s0000');
        //console.log("sent s0000");
    }
    command = '';
}, 50);




//TODO: if document already exists - don't overwrite? 
function write2CSV(chunk) {

	//start of document
    //console.log("this is the chunk that gets sent to write2csv ", chunk);
    //TODO: remove this debugging stuff
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
                    //console.log("woah chunky timestamp is small");
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
                            //console.log("this is the part from write2CSV that gets written: ",csv);
                            fs.appendFile('log.txt',csv, function (err){
                                if (err) throw err;
                            });
					        fs.appendFileSync(CSV_NAME, csv)
				        });
				        //set lastTime to current time if current time is greater
				        lastTime=chunks[0];
			        }
                    else{
                        //console.log("chunks timestamp is less than last time");
                        //console.log("chunks[0] is ",chunks[0]," lastTime is ",lastTime);
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

//control functions from old_functions.js 
//==================================================================================================================================================================================
//renamed to setstuff - function takes in whatever data was sent from user - sends it to the right place. 
function setstuff(req,res)
{
  try {
  //from the debug page
    if (req.body.arducomm != undefined){
      console.log("this is the function setstuff, this is the req.body " +  req.body.arducomm);
      toArdu();
      console.log(toArdu);
      console.log(serialPort);
      console.log(jim);
      res.send(req.body.arducomm);
    }
  //checks if abstracted command (cv, cycle etc)
    if (req.body.electro_function != undefined) 
    {
      console.log('gonna do some ' + req.body.electro_function);
      calibrate = false;
      cv = false
      arb_cycling = false;
      
      //see what the commmand is - then send the values
      command = req.body.electro_function;
      value = req.body
      //serialPort.write('s0000');
      
      //quick check to see that everything is in order.
      //console.log('this is a quick check from the function setstuff');
      //console.log(command);
      //console.log(value);
      
      //now check what kind of function user wants - and call that function
      if (command == 'cyclic_voltammetry')
      {
        console.log("setting cv now!");
        //for debugging
        console.log(value);
        cv_start_go(value);
      }
    }
  }
  catch (e) {
    console.log(e);
  }
}
// cv stuff from dan

//Global Variables for CV
cv_start = 0
cv_dir = 1
cv_DAC2 = 2.5
cv = false
cycling = false
cv_set = 0
cv_dir = 1
cv_rate = 1000
cv_max = 1
cv_min = -1
cv_cycle = 1
cv_cycle_limit = 1
cv_step = 0
cv_time  = new Date().getTime()	
cv_arr = []
last_comm = ""
cv_comm = ""
cv_settings = {}
cv_ocv_value = 0;

//approx value for volts_per_tick - to be used later I think.
volts_per_tick = 5/1023
//Global Variables for Logging
logger = "stopped"
datafile = ""
everyxlog = 1

cv_reading = '';

function readingLog() {
  return cv_reading;
};
  


function cv_start_go(value)
{
    //read in values and put them in the global variables. yay.
    console.log('cv_start_go called, yay');
		cv_arr = [] // ??
		//convert mV/s to a wait time
		if (value['cv_dir'] == 'charging') cv_dir = 1;
		if (value['cv_dir'] == 'discharging') cv_dir = -1;
		cv_rate =  (1/parseFloat(value['rate']))*1000*5
		cv_max = parseFloat(value['max_potential'])
		cv_min = parseFloat(value['min_potential'])
		cv_cycle_limit = parseFloat(value['number_of_cycles']*2) //dan must of doubled this for some reason in cv_stepper
		cv_cycle = 0 
		cv = true //if this is true - cv_stepper will run
		cv_time  = new Date().getTime()	
		//cv_step = cv_start
		DAC2_val = parseFloat(value['DAC2_value']);

		//debug stuff - sequenty to make sure its all synchronous

		l_startCSV('some_folder2/some_file2');
		jim = sread(readingLog);
		
		
		
		
		//start the cv stuff
		

		// debug stuff real quick - will abstract in a minute.
		
		
		
		//take a reading so can set stuff -- should be constantly taking readings anyway - so can just pick off from buffer.
		
		
		if (value['start_at_ocv'] != undefined) cv_start = cv_ocv_value //TODO: edit so can make this relative to ocv
		else cv_start = value['other_start_volt'];
		if (value['relative_to_ocv'] != undefined) 
		{ 
		  cv_min = cv_min + cv_ocv_value;
		  cv_max = cv_max + cv_ocv_value;
		}
		
		
		//move the ground and set ocv
		moveground(DAC2_val);
		
		
		//change file name
		
		
		//start CSV logging
		
		//rest for amount of time should rest
		
		//set the potential to be the start potential
		
		
		
		
		
		potentiostat(cv_step)
		cv_settings = value
		cv_settings['cycle'] = cv_cycle
		
		//relative to ocv stuff done after ocv is calculated.
		
		cv_start = parseFloat(value['cv_start'])
}

// could either hack like have done in python - or could try and do properly like node
function moveground(value)
{
	value_to_ardustat = value / volts_per_tick;
	toArd("d",value_to_ardustat)
	ocv()
}

//sets arudstat to open circuit potential
function ocv()
{
  swrite('-0000');
}



// for debugging only
function logstuff(req,res)
{
  try {
    console.log(req.body);
    res.send('hopefull this fixes things');
    console.log(req.body.electro_function);
    }
  catch (e) {
    console.log(e);
  }
}
var test = "test";


// makes the string good for sending to the ardustat
function ardupadder(command,number)
{
	number = parseInt(number)
	if (number < 0) number=Math.abs(number)+2000
	//console.log(number)
	padding = "";
	if (number < 10) padding = "000";
	else if (number < 100) padding= "00";
	else if (number < 1000) padding= "0";
	ard_out = command+padding+number.toString()
	return ard_out
	
}

//these are functions that can be called directly from the browser - setup to go through the router as well - almost irrelevant for now
//=================================================================================================================================================================================
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
};


reader = function(req, res){
	if(kill==false) {
	    console.log("this is from app.js");
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
    mkdirp(CSV_FOLDER, function(err) { //TODO: make this recursive?? shoudl already be... but didnt work - oh well. 
});
//TODO: add Data folder to git ignore. 
	CSV_ON = true;
	res.send('CSV WRITING HAS BEGUN! Current output file: ' + CSV_NAME);
	console.log('writing data to: ' + CSV_NAME);
	}
	else {
	res.send('ALREADY WRITING TO FILE: ' + CSV_NAME);
	}
};
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
};

name_setter = function(req,res) {
	var OLD_NAME = CSV_NAME;
	var temp = req.originalUrl.replace("/setName/","")
	CSV_NAME = 'Data/' + decodeURIComponent(temp)+'.csv'; //change here so that if there is a .csv then you don't attach this
	res.send('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
	console.log('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
};

killer = function(req,res) {
	serialPort.write("-0000");
	kill = true;
	console.log('python-forwarder interaction has been killed, and CSV writing has been paused');
	res.send('python-forwarder interaction has been killed, and CSV writing has been paused');
	CSV_ON = false;
};

reviver =  function(req,res) {
	kill = false;
	console.log('python-forwarder interaction has resumed!');
	res.send('python-forwarder interaction has resumed!');
};
//exporting a whole bunch of stuff to the router for url debugging stuff
module.exports = ({
  app:app,
  setstuff:setstuff,
  reader:reader,
  writer:writer,
  starter:starter,
  stopper:stopper,
  name_setter:name_setter,
  killer: killer,
  reviver:reviver
});
