/* 
Ardustat Forwareader: a serial to http proxy driven by ghetto get calls; NOW WITH THE ABILITY TO CSV-WRITE YOUR DATA!
requirements 
   -- serialport -> npm install serialport
   -- express -> npm install express
   -- sleep -> npm install sleep
   -- fs -> npm install fs
   -- json2csv -> npm install json2csv

to start: node AS_forwaread.js [HTTP PORT] [SERIAL PORT] [BAUD] [BUFFER LENGTH] [AS/SS]
to read: http://[yourip]:[spec'd port]/read/  -> returns the last [buffer length] bytes from the serial port as a string
to write: http://[yourip]:[spec'd port]/write/[your string here]
to start csv writing: http://[yourip]:[spec'd port]/startCSV/[optional: file name here; defaults to 'untitled']
to stop csv writing: http://[yourip]:[spec'd port]/stopCSV/
to change csv output file: http://[yourip]:[spec'd port]/setName/[new file name here]

*/

//forwarder requirements
var express = require('express');
var sleep = require("sleep").sleep;
var SerialPort = require("serialport").SerialPort ;
//csv-writer requirements
var json2csv = require('json2csv');
var fs = require('fs');
var http = require('http');
var mkdirp = require('mkdirp');
var kill = false;
var command_list = [];

//address of linux-box proxy -- ONLY USE WITH HTTP.request

/*proxy_address = 'steingart.princeton.edu';
path = '/ardustat_02/read/';*/


//names of data categories in order for simplestat (ss) and ardustat (as) -- defaults to SS
SS = "TS OUTVOLT ADC-volt DAC RES SETOUT MODE HOLDSTRING ADC-GND ADC-REF ARD-TIME";
AS = "TS OUTVOLT ADC-volt DAC RES SETOUT MODE HOLDSTRING ADC-GND ADC-REF ARD-TIME";
//writer variables initialized
var CSV_ON = false;
var labels = [];
var CSV_NAME = 'Data/untitled.csv';
var CSV_FOLDER = '';

fs.writeFile('log.txt', 'hey - this is the forwarder', function(err) {
    if (err) throw err;
});

parts = process.argv

var ts = new Date().getTime();

if (parts.length < 6)
{
	console.log("usage: node nodeforwader.js [HTTP PORT] [SERIAL PORT] [BAUD] [BUFFER LENGTH] [AS/SS]") // buffer length usually 300
	process.exit(1);
}

else
{
	console.log(parts);
	hp = parts[2] //http port
	sp = parts[3] //serial port
	baud = parseInt(parts[4]) //baud rate
	blen = parseInt(parts[5]) //buffer length
	//use appropriate headers AS vs. SS (defaults to SS)
	if(parts[6]=="AS") { labels = AS.split(" "); }
	else { labels = SS.split(" "); }
}

var app = express();

app.listen(hp);

var serialPort = new SerialPort(sp, 
	{ baudrate: baud }
);

serialPort.on("open", function () { 
	console.log('open');
	
	//instructions
	console.log("to read: http://[yourip]:[spec'd port]/read/");
	console.log("to write: http://[yourip]:[spec'd port]/write/[your string here]");
	console.log("to start csv writing: http://[yourip]:[spec'd port]/startCSV/[opt file name]");
	console.log("to stop csv writing: http://[yourip]:[spec'd port]/stopCSV/");
	console.log("to change output file: http://[yourip]:[spec'd port]/setName/[new file name]");
});  

//sleep for 5 seconds for arduino serialport purposes
for (var i=0; i<5; i++ )
{
	console.log(i);
	sleep(1); 
}

/*Http.request options; method is GET for reading data
var options = {
  //host: proxy_address,
  //path: path,
  host: '127.0.0.1',
  port: '8001',
  path: '/read/',
  method: 'GET'
};*/

//'headers' will be used to write to column titles in csv
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
   else{
      //console.log("either the CSV is off - or the interaction has been killed");
   }
});

//Write to serial port

app.get('/write/*',function(req,res){	
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
        //console.log("hopefully wrote command: "+command_list);
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



app.get('/read/', function(req, res){
	if(kill==false) {
	    //console.log(buf);
	    res.send(buf);
	}
	else { res.send("killed :("); }

});

app.get('/startCSV/*', function(req,res) {
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
app.get('/stopCSV/', function(req,res) {
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
app.get('/setName/*', function(req,res) {
	var OLD_NAME = CSV_NAME;
	var temp = req.originalUrl.replace("/setName/","")
	CSV_NAME = 'Data/' + decodeURIComponent(temp)+'.csv'; //change here so that if there is a .csv then you don't attach this
	res.send('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
	console.log('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
});

app.get('/kill/', function(req,res) {
	serialPort.write("-0000");
	kill = true;
	console.log('python-forwarder interaction has been killed!');
	res.send('python-forwarder interaction has been killed!');
});

app.get('/unkill/', function(req,res) {
	kill = false;
	console.log('python-forwarder interaction has resumed!');
	res.send('python-forwarder interaction has resumed!');
});

app.get('/setName/*', function(req,res) {
	var OLD_NAME = CSV_NAME;
	var temp = req.originalUrl.replace("/setName/","")
	CSV_NAME = 'Data/' + decodeURIComponent(temp)+'.csv'; //change here so that if there is a .csv then you don't attach this
	res.send('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
	console.log('Original output file: \"' + OLD_NAME + '\" --> New output file: \"' + CSV_NAME + "\"");
});


function write2CSV(chunk) {

	//start of document
    //console.log("this is the chunk that gets sent to write2csv ", chunk);
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
