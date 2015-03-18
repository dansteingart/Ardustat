 //TODO - convert so that can have 3 arudstat's running at the same time
//Sub - seperate out, 
//work out how to make variables non-global, or to have 3 sets of global variables (for 3 different channels)
//ok need send this whole folder to 3_play before I fuck everything up...


//requirements
//------------------------------------------------------------------------------------------------------
//config_page = require('./config.js')
var express = require('express');
var path = require('path');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var mkdirp = require('mkdirp');
var sleep = require('sleep').sleep;
var url = require('url');
var fs = require('fs');
var sys = require('sys');
var urllib = require('urllib');
var json2csv = require('json2csv');
var serialport = require('serialport');
var SerialPort = serialport.SerialPort;

//GLOBAL VARIABLES - Is there a smarter way to do this? Probably - but issue is that it would require rewriting the whole program...
//Not sure if doing something like this will ruin everything or not....
//Not sure what putting 'var' does to a variable either  
//---------------------------------------------------------------------------------------------------

// each variable an associate array - with potential to store up to 3 channels worth.


var calibrate = {};//false
calibrate.ch1 = false; calibrate.ch2 = false; calibrate.ch3 = false;
var resting = {};//false
resting.ch1 = false; resting.ch2 = false; resting.ch3 = false;
var cv = {};//false
cv.ch1 = false; cv.ch2 = false; cv.ch3 = false;
var cv_finisher_flag = {}
cv_finisher_flag.ch1 = false; cv_finisher_flag.ch2 = false; cv_finisher_flag.ch3 = false;
var arb_cycling = {}; //false
arb_cycling.ch1 = false; arb_cycling.ch2 = false; arb_cycling.ch3 = false;
var count = {}; //0
count.ch1 = 0; count.ch2 = 0; count.ch3 = 0;
var lastTime = {}; //''
lastTime.ch1 = 0; lastTime.ch2 = 0; lastTime.ch3 = 0;

//writing GLOBALS
var CSV_ON = {};
CSV_ON.ch1 = false; CSV_ON.ch2 = false; CSV_ON.ch3 = false;
var labels = []; // think this is gonna be same no matter what
var CSV_NAME = {}//'Data/untitled.csv';
var CSV_FOLDER = {}//'';
var kill = {}//};
kill.ch1 = false; kill.ch2 = false; kill.ch3 = false;
var command_list = {};//[]
blen = 300; // buffer length can stay the same
var ts = {};
var headers = {};
var now_time = {}; 

current = {}
last_current = {}

buf = {}//""
last_ardu_reading = {}

//Global Variables for CV
cv_filename = {};
cv_foldername = {};
cv_raw_reading = {};
cv_start = {};//0
cv_dir = {};//1
cv_DAC2 = {};//2.5
cycling = {};//false
cv_set = {};//0
cv_rate = {};//1000
cv_max = {};//1
cv_min = {};//-1
cv_cycle = {};//1
cv_cycle_limit = {};//1
cv_step = {};//0 //where the potential at. 
cv_time  = {};//new Date().getTime() 
cv_arr = {};//[]
last_comm = {};//""
cv_comm = {};//""
cv_settings = {};//{}
cv_ocv_value = {};//0;
volts_per_tick = {};//5/1023 // approx value
cv_relative_to_ocv = {};//false
cv_start_at_ocv = {};//false
cv_resting = {};//false
cv_rest_time = {};//0
cv_reading = {};//'';
cv_finish_value = {}


//Global Variables for Logging
/*
logger = "stopped"
datafile = ""
everyxlog = 1
*/



//Global Variablew for Arb Cyclingq

test_running = {};//false;
test_running.ch1 = false; test_running.ch2 = false; test_running.ch3 = false;
//arb_cycling defined above
arb_cycling_settings = {};//[]
arb_cycling_settings.ch1 = []; arb_cycling_settings.ch2 = []; arb_cycling_settings.ch3 = [];
arb_cycling_step = {};//0
arb_cycling_step_start_time = {};//0
cycling_cycles = {};//0
cycling_cycle = {};//0
cycling_cycle.ch1 = 0; cycling_cycle.ch2 = 0; cycling_cycle.ch3 = 0;
last_current = {};//0
last_potential = {};//0
total_pause_time = {};//0;
total_pause_time.ch1 = 0; total_pause_time.ch2 = 0; total_pause_time.ch3 = 0;
direction = {};//na
cutoff_potential = {} //na
cutoff_current = {} //na

var pause_time = {};//;
var resume_time = {};//;

cyc_folder_name = {};//''
cyc_file_name = {};//''
ardustat_id = {};
ardustat_id.ch1 = 25; ardustat_id.ch2 = 25; ardustat_id.ch3 = 25;//25 //TODO: check that this isn't defined somewhere else, add in functionality for serial port
http_port = {};//8001
setupdata = {}; // 
setupdata.ch1 = {}; setupdata.ch2 = {}; setupdata.ch3 = {};

//Global Functions for Data Parsing
id = {};//25; //TODO change so that you can set the id of the arudstat
vpt = {};//undefined; //volts per tick
mode = {};//0;
var res_table = {};//;

//CALIBRATION PORTION
//What happens
//1) We intitialize a counter, a loop counter,a loop limit and a callibration array
//2) When the function is called we flip the boolean and scan 

counter = {};//0
calloop = {};//0
callimit = {};//2
callimit.ch1 = 2; callimit.ch2 = 2; callimit.ch3 = 2; //changed to 1 for debugging purposes
calibration_array = {};//[]
calibration_array.ch1 = []; calibration_array.ch2 = []; calibration_array.ch3 = [];
rfixed = {};//10000 //TODO - make this a user input thing

//skip a step of the cycler
var skip_time = {};//
skip_time.ch1 = 0; skip_time.ch2 = 0; skip_time.ch3 = 0;
var skip_flag = {};//
skip_flag.ch1 = false; skip_flag.ch2 =  false; skip_flag.ch3 = false;

//function to reset all of the global parameters for the channel after shit has stopped
//should probably be clever and set this at the start as well but yolo.
function reset_globals(channel){ 
  calibrate[channel] = false;
  resting[channel] = false; 
  cv[channel] = false; 
  cv_finisher_flag = false;
  arb_cycling[channel] = false; 
  count[channel] = 0; 
  lastTime[channel] = 0;
  setupdata[channel] = {};
  //kill = ????
  CSV_ON[channel] = false;
  command_list[channel] = [];
  //Global Variables for CV
  cv_start[channel] = {};//0
  cv_dir[channel] = 1
  cv_DAC2[channel] = 2.5
  cv_cycle[channel] = 0;
  cv_step[channel] = 0; //pretty sure not necessary 
  cv_cycle[channel] = 0;
  last_ardu_reading[channel] = ''
  //CYCLER
  arb_cycling_settings[channel]= []; arb_cycling_settings.ch2 = []; arb_cycling_settings.ch3 = [];
  arb_cycling_step[channel] = 0
  arb_cycling_step_start_time[channel] = 0
  cycling_cycles[channel] = 0
  cycling_cycle[channel] = 0
  last_current[channel] = 0
  last_potential[channel] = 0
  total_pause_time[channel] = 0;
  direction[channel] = 'na'
  cutoff_potential[channel] = 'na'
  cutoff_current[channel] = 'na'
  pause_time[channel] = 0;
  resume_time[channel] = 0;
  skip_time[channel] = 0
  skip_flag[channel] = false;
  
  //calibration - don't think there are any issues with this puppy...
  console.log('all of the globals have been reset')

}
//serial port, make folders, socket (preliminary things)
//------------------------------------------------------------------------------------------------------

//socket.io is going ot have to send things out on 3 seperate channeles as well, or just emits with the channel number and then the data comes after...
mkdirp('resistance_tables', function(err, data) { 
  if (err) {
    console.log(err) 
  } 
});
//make sure that there is a Data table
mkdirp('Data',function(err,data){
  if(err) {
    console.log(err)
  }
});
console.log('directory is '+__dirname)

var listen = function(app) 
{
  var http = require('http').createServer(app).listen(3001);
  global.io = require('socket.io')(http);
  io_connect();
  global.io.on('connection', function(socket){
    socket.on('chat message', function(msg){
      console.log('chat message: ' + msg);
    });
});
}
function io_connect()
{
  global.io.on('connection', function(socket) {
    console.log('io_connect works');
    //global.io.emit('connection', 'socket.io connected!')
  });
}
function give_status(req,res)
{
  console.log('give status called');
  channel = url.parse(req.url,true).query.channel;
  console.log('channel is:'+channel)
  if (test_running[channel]) {
    response = JSON.stringify( setupdata[channel] )
    console.log(response)
    res.send(response)
  }
  else {
    res.send('nothing happening')
    console.log('nothing happening')
  }

}

function blink_button(req, res)
{
  console.log('blink button called');
  channel = url.parse(req.url,true).query.channel;
  console.log('channel is:'+channel)
  toArd(channel,"b",0)
  res.send('blink done')
}
  

function io_emit(channel, msg)
{
  global.io.emit(channel, msg);
  console.log(channel + ' ' +  msg)
}

//think should be changed to 
/*
function io_emit(channel, msg)
{
  global.io.emit(channel, msg)
}
*/

// open all the serial ports (up to 3) -- how to make sure that the serial ports get the right channel ids?


// going to have to re-do the way i do ports...
devs = ['/dev/tty.usbmodemfd1211','/dev/tty.usbmodemfd1221']
var ports = [];
//startserial = function() {
for (var i = 0; i < devs.length; i++) {
    console.log('this is where we are opening a serial port ' + devs[i]);
    var port = new SerialPort(devs[i],{ baudrate:57600, parser: serialport.parsers.readline("\n") });
    ports.push(port);
}

for (var i = 0; i < ports.length; i++) {
  if ( i == 0 ) channel = 'ch1'
  else if ( i == 1 ) channel = 'ch2'
  else if ( i == 2 ) channel = 'ch3'
  setupHandlers(channel,ports[i]);
}

ports_dict = {}

function setupHandlers(channel,port) {
  console.log('setup handler channel number is ' + channel)
  port.on("open", function (path) {
    console.log('serial port ', port.path ,' is open on channel number ' , channel )
    ports_dict[channel] = port
    port.on("data", function (data) {
      //console.log("here: on channel " + channel + ': ' +data);
      if (data.search('GO') > -1)
      {
        parsed_data = data_parse(channel,data); //this is a synchronous thing and should probably be removed -- I think it might take a neglible amount of time anyway - still I don't like my program being blocked.
        last_ardu_reading[channel] = parsed_data;
        
        if (calibrate[channel]) //this is probably going to freak out cause it's not initialized...
        {
          //console.log('sent to calibration array');
          //console.log(parsed_data);
          calibration_array[channel].push(parsed_data) //TODO: initialize this as an array before this. (this is where the headache wil come in). (but we should be all good)
        }
        now_time[channel] = new Date().getTime();
        ts[channel] = now_time[channel];  //some debugging rubbish
        //console.log('now_time '+now_time.toString());
        //console.log('pause time '+total_pause_time.toString());
        buf[channel] += data;
        var n = buf[channel].indexOf("GO.");
        //console.log(ts[channel])
        //console.log(ts[channel].toString())
        buf[channel] = buf[channel].substr(0,n+2)+","+ts[channel]+","+buf[channel].substr(n+3,buf[channel].length);
        if (buf[channel].length > blen) buf[channel] = buf[channel].substr(buf[channel].length-blen,buf[channel].length);
        //if writing is desired write buf to current CSV_NAME file
        if((CSV_ON[channel] == true) && (kill[channel] == false)){ 
            write2CSV(channel,buf[channel]); 
            console.log("received data and sent to write2CSV on channel " + channel);
          }
       }    
     });
  });
}

//Break Arduino string into useful object
function data_parse(channel,data)
{
  if ( typeof (data) == "string")
  {
    parts = data.replace('.', ',');
	  parts = parts.split(",")
	}
	else
	{
	parts = data
	}
	//console.log(parts);
	//console.log(parts[10]); // shoule be twopointfive_adc 
  out = {}
  //GO,102,351,0,255,0,0,s0000,99,102,524,ST
	//the raw data
	//console.log(data)
	out['dac_set'] = parseFloat(parts[1])
	out['cell_adc'] = parseFloat(parts[2])
	out['dac_adc'] = parseFloat(parts[3])
	out['res_set'] = parseFloat(parts[4])
	//console.log('out res_set below')
	//console.log(out['res_set']);
	out['mode'] = parseInt(parts[6]) //TODO check that this is write
	out['gnd_adc'] = parseFloat(parts[8])
	out['ref_adc'] = parseFloat(parts[9])
	out['twopointfive_adc'] = parseFloat(parts[10])
	//out['id'] = parseInt(parts[11])
	out['last_comm'] = last_comm[channel]
	mode = out['mode']
	//making sense of it
	//console.log("2.5 adc");
	//console.log(out['twopointfive_adc']);
	volts_per_tick = 	2.5/out['twopointfive_adc'] // volts_per_tick is gonna stay the same no matter what channel
	//console.log(volts_per_tick);
	if (vpt == undefined) vpt = volts_per_tick;
	/*
	if (id != out['id'])
	{
		id = out['id'];
		res_table = undefined
	}
	*/
    
	//force ocv when dac_set and dac_adc don't match up
  /*
  if (out['mode'] != 1 & out['dac_set'] - out['dac_adc'] > 900)
    {
        console.log('something is not adding up, forcing ocv')
        set_ocv(channel);
    }
    */

	
	out['cell_potential'] = (out['cell_adc'] - out['gnd_adc']) * volts_per_tick
	out['dac_potential'] = (out['dac_adc'] - out['gnd_adc'])*volts_per_tick
	out['ref_potential'] = out['ref_adc']*volts_per_tick
	out['gnd_potential'] = out['gnd_adc']*volts_per_tick
	out['working_potential'] = (out['cell_adc'] - out['ref_adc']) * volts_per_tick
	last_potential[channel] = out['working_potential']
	if (calibrate[channel] != true)
	{
	  if (res_table[channel]  == undefined)
	  {
		  try
		  {
			  res_table[channel]  = JSON.parse(fs.readFileSync("resistance_tables/unit_"+ardustat_id[channel].toString()+".json").toString())
			  console.log("loaded table "+ardustat_id[channel].toString()) // quick test to see if both syntaxs are gonnna work... only this syntax wil work.
			  //console.log(res_table[channel]);
		  }
		  catch (err)
		  {
			  console.log(err)
			  console.log("no table "+ardustat_id[channel].toString())
			  res_table[channel]  = undefined;
		  }
	  }
	
	  if (res_table[channel].constructor.toString().indexOf("Object")>-1)
	  {
		  out['resistance'] = res_table[channel][out['res_set']]
		  //console.log(out['resistance'])
		  
		  current[channel] = (out['dac_potential']-out['cell_potential'])/out['resistance'] *1000 //current always in milli amps
		  if (mode == 1) out['current'] = 0
		  else out['current'] = current[channel] 
		  last_current[channel]  = out['current'] //same thing that dan did for the potential
	  }
	}
	return out
}



//TODO: if document already exists - don't overwrite?
function write2CSV(channel,chunk) {
  //console.log('write2CSV called');
  //console.log(chunk)
	//start of document
    //console.log("this is the chunk that gets sent to write2csv ", chunk);
    //TODO: remove this debugging stuff
  /*
  fs.appendFile('log.txt',chunk, function (err){
      if (err) throw err;
  });
*/
  //for debug
  //if (total_pause_time[channel] > 0) fs.appendFileSync('log.txt', 'jimmy \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
  console.log('in write2csv channel is ', channel)
	if(count[channel]==0) {
		//write column headers to csv file (optional) -- using 'writeFile' here to overwrite old data on file
		json2csv({data: headers, fields: ['0','1','2','3','4','5','6','7','8','9','10'], hasCSVColumnTitle: false}, function(err, csv) {
			if (err) console.log(err);
			fs.writeFile(CSV_NAME[channel].toString(), csv, function(err) {
				if (err) throw err;
			});
		});
  //console.log('csv started')
  //console.log(CSV_NAME[channel])
	count[channel]=1;
	}

	else{
	
		    var orig = chunk;
        //console.log('orig below')
        //console.log(chunk)
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
          //console.log('chunks below')
          //console.log(chunks)
          //if (parseInt(chunks[0]) < 10000) 
          //{
          
            //console.log("woah chunky timestamp is small");
            //fs.appendFile('log.txt', "chunky timestamp is smaller than 10000", function (err) 
            //{
              //if (err) throw err;
            //});
          //}
          //else 
          //{
            //console.log(chunks[0])
            //console.log(total_pause_time[channel])

            chunks[0] = parseInt(chunks[0]) - total_pause_time[channel]
            //don't write entries more than once
            //console.log(lastTime[channel])
            if(parseInt(chunks[0])>parseInt(lastTime[channel])) 
            {
	            //count++;
	            foo = {};
	            for(var j = 0; j<11;j++) {
		            foo[j]=chunks[j];
	            }
	            //write data values to appropriate columns in csv 
	            json2csv({data: foo, fields: ['0','1','2','3','4','5','6','7','8','9','10'], hasCSVColumnTitle: false}, function(err, csv) {
		            if (err) console.log(err);
		               
                          //console.log("this is the part from write2CSV that gets written: ",csv);
                          //fs.appendFile('log.txt',csv, function (err){
                             // if (err) throw err;
                          //});
		            fs.appendFileSync(CSV_NAME[channel], csv)
                //console.log('csv has been appended')
	            });
	            //set lastTime to current time if current time is greater
	            lastTime[channel]=chunks[0];
            }
            else
            {
                //console.log("chunks timestamp is less than last time");
                //console.log("chunks[0] is ",chunks[0]," lastTime is ",lastTime);
                //fs.appendFile('log.txt','chunks is ' + chunks[0] + " ", function (err){
                   // if (err) throw err;
               // });
               // fs.appendFile('log.txt',' last time is ' + lastTime[channel] + " ", function (err){
               //     if (err) throw err;
               // });
                chunk = '';
                chunks = '';
            }
          //}
    }
  }
}
//======================================================================================================
//functions to communicate how urls used to 

function toArd(channel,command,value)
{
	last_comm[channel] = ardupadder(command,value)
	//serialPort.write(ardupadder(command,value));	
	l_writer(channel,last_comm[channel])
	//console.log(last_comm[channel])
}
function l_writer(channel,stringer) {	
  //console.log('l writer has actually been called - for fucks sakes - why doesnt this append to the command list?')
  //console.log(stringer)
  command_list[channel].push(stringer);
  /*
	if(kill[channel]==false) {
	  command_list[channel].push(stringer);
	}
	else if( ( kill[channel]==true ) && ( stringer == '-0000') ){
	  console.log('this is where the problems are');
	  console.log(channel)
	  command_list[channel].push(stringer);
	}
	//TODO make this more robust
	else { 
	  console.log("killed :(");
  };
  */
  //console.log(command_list[channel])
};

function l_reader(channel) { //returns string
  if (kill[channel] == false) {
    var reading = buf
    var orig = buf
    if (reading.indexOf("GO")!=-1 && reading.indexOf("ST")!=-1){
	    var start = orig.indexOf("GO");
	    reading = orig.substr(start,reading.length);
	    var temp = reading;
	    orig = reading;
	    var end = orig.indexOf("ST");
	    //remove post-'ST' data from current chunk
	    chunk = reading.substr(0,end+2);
	    //console.log(chunk+","+count);
	    //remove current chunk from original chunk for later analysis
	    reading = reading.substr(end+2,orig.length);
	    //create array of data values
	    var chunks = chunk.split(",");
	    //var temp = reading;
	    //TODO: figure out why this doesn't wanna print - real werid but whatever. Take out all the console checks.
	    //console.info(" why wont this print? ", temp); //this is perhaps the weirdest shit ever.
	    //console.log(reading.length);
	    //console.log("chunks is now " +chunks);
	    //console.info(chunks.length);
	    return chunks;
  }
    else {console.log("something here is fucked with l_reader");
    }
      
  }
  	else { console.log("killed") }
};

//TODO:this is where we can stop overwrites... or send warning to the user... that would be sweet.
function l_starter(channel,folder_file,value) {
  fs.writeFileSync("log.txt",'hey dan')
  console.log('l_starter has been called');
  console.log(CSV_NAME[channel])
  console.log(folder_file)

	if(CSV_ON[channel] == false) {
	if(folder_file !="" ) { CSV_NAME[channel] = 'Data/' + folder_file +'.csv'; }
  console.log('csv name is ', CSV_NAME[channel])

  console.log(CSV_NAME[channel])
  //stuff to create folder if not already there  
  var CSV_PARTS = CSV_NAME[channel].split("/");
  CSV_FOLDER[channel] = ''
  for (var i = 0; i < CSV_PARTS.length-1; i++)
  {
    CSV_FOLDER[channel] += CSV_PARTS[i] + "/";
  }
  console.log('CSV folder is ', CSV_FOLDER[channel]);
  CSV_FOLDER[channel] = CSV_FOLDER[channel].substring(0,CSV_FOLDER[channel].length-1);
  console.log("CSV_folder " , CSV_FOLDER[channel]);
  mkdirp(CSV_FOLDER[channel], function(err) { //TODO: make this recursive - just need to set call-back to make sure that
  //TODO: make sure this is in a callback sequence so that nothing super fucked up happens.
    console.log('error making the folder is ', err);
  //this might not happen synchronously but it shouldn't matter too much
});
  
  
	CSV_ON[channel] = true;
	kill[channel] = false; // added kill = false to starter.
	//res.send('CSV WRITING HAS BEGUN! Current output file: ' + CSV_NAME);
	console.log('writing data to: ' , CSV_NAME[channel]);
	
  setupdata[channel] = value
	//log setup data
	setupdata[channel].ardustat_id = ardustat_id[channel] //making sure that this is correct is all
	setupdata_json = JSON.stringify(setupdata[channel]) //TODO: this is blocking but should be super quick anyway.. //TODO: still need to overwrite files

	console.log('setupdata below');
	console.log(setupdata_json)
	fs.writeFile(CSV_NAME[channel].replace('.csv','setup.json'), setupdata_json)
	}
	else {
	//res.send('ALREADY WRITING TO FILE: ' + CSV_NAME);
	console.log('something messed up with the startCSV');
	}
};

function l_stopper(channel) 
{
  test_running[channel] = false;
	kill[channel] = true;
	console.log('method control has been stopped, and CSV writing has been killed');
	CSV_ON[channel] = false;
  test_finished(channel)

}
//killer, reviver, and skipper are at end where the abstracted functions are.

//============================================================================================================================

//could write a flag that decides if things are already running, if they are - tell the browser to fuck off

//Maybe only open serial port when user says to?  -- Figure out best way to do this...
//takes in data and sends to right place

//TODO - make this more robust - take in value of the ardustat trying to play with and only sets for that ardustat.
//have to have 3 forwarders running simultaneously - best way to do it i think are dictionaries and to have every function accept an id or channel parameter.
function setstuff(req,res)
{
 //TODO urgent - if there is a test running - should tell user and user should have option to stop the test.
  channel = req.body.channel
  //console.log(req.body)
  

  console.log('the req.body is ' , req.body)
  console.log('the channel is ' , req.body.channel);
  if (test_running[channel])
  {
    console.log('test running');
    //cool - steal things from what I wrote below.
    
    res.send()
  }
  else
  {
    console.log(' called');
    try {
      
      
      if (req.body.ardustat_id_setter != undefined){
        console.log('ardustat_id sent');
        ardustat_id[channel] = req.body.ardustat_id_setter;
        out = fs.readdirSync(__dirname+'/resistance_tables/'); //cool i think things are working
        console.log('out is  ' + out)
        if (out.indexOf('unit_'+ardustat_id[channel].toString()+'.json') > -1){
          console.log('res_table is here');
          res_table[channel]  = JSON.parse(fs.readFileSync("resistance_tables/unit_"+ardustat_id[channel].toString()+".json").toString())
          console.log("loaded table "+ardustat_id[channel].toString())
          res.send('res_table is here');
        }
        else {
          console.log("res_table isn't here");
          res.send("res_table isn't here");
        }
      }

      else if(req.body.filename_check != undefined){
        console.log('checking for file')
        check_folder_name = req.body.folder_name; //quick check to see if this will work
        check_file_name = req.body.file_name;
        console.log('file ' + check_file_name)
        try{
          out = fs.readdirSync(__dirname+'/Data/'+check_folder_name); //cool i think things are working
          console.log('out is  ' + out)
          if (out.indexOf(check_file_name+'.csv') > -1){
            console.log('file is here');
            res.send('filename already used');
          }
          else {
            console.log("file isn't here");
            res.send("file isn't here");
          }
        }
        catch(e){
          console.log(e)
          res.send('file not here')
        }

      }
      //var parsed = JSON.parse(req.body);
      //console.log(parsed);
    //from the debug page
      else if (req.body.arducomm != undefined){
        //console.log("this is the function setstuff, this is the req.body " +  req.body.arducomm);
        res.send('hello from server');
      }
      
    //checks if abstracted command (cv, cycle etc)
      else if (req.body.electro_function != undefined) 
      {
        console.log('gonna do some ' + req.body.electro_function);
        calibrate[channel] = false;
        cv[channel] = false
        cv_finisher_flag[channel] = false;
        arb_cycling[channel] = false;
        
        //see what the commmand is - then send the values
        command = req.body.electro_function;
        value = req.body
        

        if (command == "calibration")
	      {
		      console.log("calibration should start");
		      console.log("value of resistor is "+req.body.resistor_value);
		      calibrator(channel,req.body.resistor_value);
		      res.send('calibration called on channel ' + channel);
	      }
        //now check what kind of function user wants - and call that function
        if (command == 'cyclic_voltammetry')
        {
          console.log("setting cv now!");
          //for debugging
          console.log(value);
          cv_start_go(channel,value);
          res.send('cyclic voltammetry called on channel ' + channel);
        }
      }
      
      else if (req.body.cycle_array != undefined) 
      {
        console.log('cycling should start');
        calibrate[channel] = false;
        cv[channel] = false
        cv_finisher_flag[channel] = false
        //console.log("req.body.cycle_array");
        //console.log(req.body.cycle_array)
        parsed = JSON.parse(req.body.cycle_array);
        console.log(parsed)
        arb_cycling[channel] = true;
        cycling_start_go(channel, parsed);
        res.send('hello')
      }
      else
      {
      console.log("something else was sent");
      console.log(req.body);
      res.send('hello')
      }
    }
    catch (e) {
      console.log(e);
    }
  }
  //res.send('hello') //trying to shut this thing up
  return false;
}

//CV stuff
//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//Global Variables for CV



function readingLog(channel) {
  return cv_reading[channel];
};
  

// figure out ways to print all of this stuff so i know whats going on... dont really trust console.log though

function cv_start_go(channel,value)
{
    //read in values and put them in the global variables. yay.
    test_running[channel] = true;
    
    console.log('cv_start_go called, yay');
		cv_arr[channel] = [] // ??
		cv_filename[channel] = value['file_name'];
		cv_foldername[channel] = value['folder_name'];
		console.log('starting');
		console.log(cv_foldername[channel]);
		if (value['cv_dir'] == 'charging') cv_dir[channel] = 1;
		if (value['cv_dir'] == 'discharging') cv_dir[channel] = -1;
		cv_rate[channel] =  (1/parseFloat(value['rate']))*1000*5	//convert mV/s to a wait time
		cv_max[channel] = parseFloat(value['max_potential'])
		cv_min[channel] = parseFloat(value['min_potential'])
		cv_cycle_limit[channel] = parseFloat(value['number_of_cycles']*2) //dan must of doubled 
		cv_cycle[channel] = 0;
		console.log('cv_cycle ',cv_cycle[channel]);
		cv[channel] = false //if this is true - cv_stepper will run - don't want this to happen right now because going into  rest step first...
    cv_finisher_flag[channel] = false
		cv_time[channel]  = new Date().getTime()	
		//cv_step = cv_start
		cv_DAC2[channel] = parseFloat(value['DAC2_value']);
    cv_raw_reading[channel] = ''
    cv_rest_time[channel] = value['rest_time']; //TODO: check that this is the right key.
    cv_relative_to_ocv[channel] = value['relative_to_ocv']; //TODO make this so you can do it for either voltage. 
    //flags for the starter
    if (value['start_at_ocv']) 
    { 
      cv_start_at_ocv[channel] = true
    }
    else{ 
      cv_step[channel] = value['other_start_volt'];
    }
    //start stuff
    cv_send_cycle(channel,cv_cycle[channel])
    
    console.log(channel,cv_foldername[channel]+'/'+cv_filename[channel])
		l_starter(channel,cv_foldername[channel]+'/'+cv_filename[channel],value);

    //TODO: abstract reading
    //TODO: make this more robust
		cv_reading[channel] = last_ardu_reading[channel]
		//console.log('cv_reading[channel] below');
		//console.log(cv_reading[channel]);
		 //TODO: instead of do this in a node like way instead of a pythonic way
		//console.log("this is logging the cv_reading " + cv_reading);
		 //this will set volts_per_tick
		
		//move the ground and set ocv
		moveground(channel,cv_DAC2[channel]);
		cv_resting[channel] = true;
		//cv_rester(channel);
		cv_start[channel] = parseFloat(value['cv_start'])
}

function cv_send_cycle(channel,cycle){
  if (cycle % 2 == 1) cycle_to_send = (cycle+1)/2
  else cycle_to_send = cycle/2
  console.log('sending cycle ' + cycle_to_send);
  toArd(channel,'y',cycle_to_send)
}



function cv_rester(channel){
  //console.info("cv_rester");
  var time = new Date().getTime()
  if ((time - cv_time[channel]) >(cv_rest_time[channel] * 1000) ) //everything is in milli seconds. 
    { 
      console.log('rest_time is over');
      //take a reading
		  cv_reading[channel] = last_ardu_reading[channel]
		  cv_ocv_value[channel] = cv_reading[channel]['working_potential']
		  
		  
		  //set final things //TODO wishlist - make this fancier - user can set more things. 
		  if (cv_start_at_ocv[channel] == true) cv_step[channel] = cv_ocv_value[channel];
		  if (cv_relative_to_ocv[channel]) {
		    cv_max[channel] = cv_max[channel] + cv_ocv_value[channel];
		    cv_min[channel] = cv_min[channel] + cv_ocv_value[channel];
		  }
		  
		  //set the potential to the start and go for your life I guess.
		  console.log(cv_ocv_value[channel]);
		  console.log(cv_step[channel]);
		  potentiostat(channel,cv_step[channel])
      cv_finish_value[channel] = cv_step[channel] //the finish value is the same as the start value... could make this fancier.. but can't really be bothered right now...

		  
		  //set cv to on
		  cv[channel] = true;
		  cv_resting[channel] = false
  }
}

function cv_stepper(channel)
{
	//console.log('stepped into cv');
	//console.log(cv_step);
	var time = new Date().getTime()	//only a local variable so things should be all good. 
	if (time - cv_time[channel] > cv_rate[channel])
	{
		console.log("next step")
		cv_time[channel] = time
		cv_step[channel] = cv_step[channel] + cv_dir[channel]*.005
		if (cv_step[channel] > cv_max[channel] & cv_dir[channel] == 1)
		{
			cv_dir[channel] = -1
			cv_cycle[channel]++
			cv_send_cycle(channel,cv_cycle[channel])
			console.log('twice the cycle number is now ',cv_cycle[channel])
		}
		
		else if (cv_step[channel] < cv_min[channel] & cv_dir[channel] == -1)
		{
			cv_dir[channel] = 1
			cv_cycle[channel]++
			cv_send_cycle(channel,cv_cycle[channel])
			console.log('twice the cycle number is now ',cv_cycle[channel])
		}
		if (cv_cycle[channel] >= cv_cycle_limit[channel]) 
		{
			cv[channel] = false
      //make a new function - cv_finisher, and new flag - send it back to ocv.
      cv_finisher_flag[channel] = true;
      cv_finisher(channel)
			//test_finished(channel)
		}
		else
		{
		  console.log("cv_step of channel " + channel);
			console.log(cv_step[channel])
			potentiostat(channel,cv_step[channel])
		}
	}
}
//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// Cycling Section
//==============================================================================================================

//URGENT: When cycling input comes in, how have I indexed it? By adding a channel to the mix am I going to mess it up?
//cycling input looks as follows:
//[{"electro_function":"cycle"},{"cycles":4},{"cyc_mode":"galvanostatic","cyc_value":"1","time_cutoff":"10","voltage_cutoff":"0","current_cutoff":"0"},{"cyc_mode":"galvanostatic","cyc_value":"-1","time_cutoff":"15","voltage_cutoff":"0","current_cutoff":"0"},{"cyc_mode":"galvanostatic","cyc_value":"2","time_cutoff":"5","voltage_cutoff":"0","current_cutoff":"0"},{"cyc_mode":"galvanostatic","cyc_value":"-2","time_cutoff":"10","voltage_cutoff":"0","current_cutoff":"0"}] 

//call this function to return to ocv or pre-specified value at the end of the cv.
function cv_finisher_flag(channel){
  console.log('cv finisher flag')
  if (cv_step[channel] < cv_finish_value[channel]){
    cv_dir[channel] = 1
  }
  else if (cv_step[channel] > cv_finish_value[channel]){
    cv_dir[channel] = -1
  }
  else if (cv_step[channel] == cv_finish_value[channel]){
    console.log('WOW - cv_step was the same as cv_finsih value upon entry')
    test_finished(channel)
  }
  else {
    throw 'Something in the cv_finisher_flag is undefined'
  }
  var time = new Date().getTime() 
  if (time - cv_time[channel] > cv_rate[channel])
  {
    console.log("next step")
    cv_time[channel] = time
    cv_step[channel] = cv_step[channel] + cv_dir[channel]*.005
    if (cv_step[channel] > cv_finish_value[channel]) {
      console.log('finsih value reached')
      cv_finisher_flag = false;
      test_finished(channel)
    }
  }
}


function cycling_start_go(channel,value)
{
  //console.log(value)
  //console.log(value[0])
  //console.log(value[1])
  //console.log(value[2])




  test_running[channel] = true;
  //console.log("this is cycling_start_go on channel " + channel);
  total_pause_time[channel] = 0; 
  moveground(channel,2.5)

  arb_cycling_settings[channel] = []
	arb_cycling_step[channel] = 0
	//arb_cycling[channel] = false // really?
	arb_cycling_step_start_time[channel] = new Date().getTime()
  
  for (var i = 2; i < value.length; i++) {
    arb_cycling_settings[channel].push(value[i])
  }
  //console.log(arb_cycling_settings)
  console.log(arb_cycling_settings[channel])
  //console.log(arb_cycling_settings[channel][0])
  //console.log(arb_cycling_settings[channel][0].cyc_mode)
  //debugging()
  console.log('cyc folder should be ' + value[1].cyc_folder)
  cyc_folder_name[channel] = value[1].cyc_folder
  cyc_file_name[channel] = value[1].cyc_file_name
  cycling_cycles[channel] = value[1].cyc_cycles
  //TODO: add in stuff for ardustat_id, serial_port, http_port
  
  //start logging to csv
  console.log(cyc_folder_name[channel]+'/'+cyc_file_name[channel])
  l_starter(channel,cyc_folder_name[channel]+'/'+cyc_file_name[channel],value);
  
	//console.log('cycle settings on channel ' + channel + 'are ' + arb_cycling_settings[channel])

	arb_cycling[channel] = true
	cycling_mode(channel)
	toArd(channel,'y',cycling_cycle[channel])
	console.log('sent this cycle to arduino ', cycling_cycle[channel]);
  console.log('cycling_start_go over')
	
}

//i am getting closer!

//KEY Learning Point: When you append an object to a string, it gets its toString method called, which for a plain object just gives the infamous "[object Object]". To log an object, you should just pass it straight into the console.log function as an argument, like so:

function debugging(){
  console.log('debug ' , arb_cycling_settings)
  console.log('debug ' , arb_cycling_settings['ch1'])
  console.log(arb_cycling_settings['ch1'][0].cyc_mode)
}

//cycling stepper - if next step is ordered. call next_step().
// big issue - could be some niggles with the limits if next_step is called - should probably give some time to settle.
// so, if user requests skip_step - next_step called - timer for 2 a second is called - lets cell settle so no unecessary skipping occurs

// this needs to be made fancier i think
//TODO: add in capacity limit stuff?


function cycling_stepper(channel)
{
	//console.log("cycling_stepper");
	time = new Date().getTime()
	var this_set = arb_cycling_settings[channel][arb_cycling_step[channel]] //this set is delclared locally I believe...
	if (this_set['time_cutoff'] == '') this_set['time_cutoff'] = 0
	var next_time = this_set['time_cutoff'] * 1000 //same with next_time 
	//console.log("next time is ")
	//console.log(next_time	
	if (this_set['cyc_value'] < 0) direction[channel] = 'discharge'
	else { direction[channel] = 'charge' }
	
	cutoff_potential[channel] = this_set['voltage_cutoff']
	cutoff_current[channel] = this_set['current_cutoff']
  if (this_set['cyc_mode'] == 'galvanostat') console.log('galvanostatic and the cutoff potential is ',cutoff_potential[channel])
  if (this_set['cyc_mode'] == 'potentiostat') console.log('potentiostatic and the cutoff current is ', cutoff_current[channel])

	way = 1 //declared locally
	if (direction[channel] == "discharge") way = -1
	this_time = time-arb_cycling_step_start_time[channel]
	//console.log(next_time - this_time)
  //console.log('just checking what skip flag is ', skip_flag[channel] ) 
  //console.log(time)
 // console.log(skip_time[channel])
  //console.log(this_set['cyc_mode'])
  //console.log(direction[channel])
  //console.log(last_potential[channel])
  //console.log(cutoff_potential[channel])
  
	if (next_time != 0 & next_time < this_time) 
	{
	  console.log('time exceeded')
	 	next_step(channel) //things might get tricky.
	}
  if (((skip_flag[channel]) & (time - skip_time[channel] > 500)) || (!skip_flag[channel])) // lets cell settle after skip step 
  {
    //console.log('did you go into main loop thing?')
    skip_flag[channel] = false;
	  if (this_set['cyc_mode'] == 'galvanostatic') 
	  {
	    console.log('went into galvanostat part');
	    console.log('direction ',direction[channel]);
	    console.log('last_potential ', last_potential[channel]);
	    console.log('cutoff_potential ', cutoff_potential[channel]);
	    if ( direction[channel] == "charge" & (last_potential[channel] > cutoff_potential[channel]) )
	    {
	      console.log('cutoff potential reached on channel ' + channel)
	      skip_flag[channel] = true;
		    next_step(channel)
	    }
	    else if (direction[channel] == "discharge" & last_potential[channel] < cutoff_potential[channel])
	    {
	      console.log('cutoff potential reached on channel ' + channel)
	      skip_flag[channel] = true;
		    next_step(channel)
	    }
	  }
	  else if (this_set['cyc_mode'] == 'Potentiostatic')
	  {
	    console.log('went into potentiostatic thing');
	    console.log('last current is ', last_current[channel])
	    console.log('cuurrent cutoff is ', cutoff_current[channel])
	    if ( Math.abs(last_current[channel]) < Math.abs(cutoff_current[channel]) ) 
	    {
	      console.log('cutoff current reached on channel ' + channel);
	      next_step(channel)
	      skip_flag[channel] = true;
	    }
	  }

	}
	else console.log('did nothing');
}


// TODO: tidy things up - this can be done a little later though.
function next_step(channel)
{
  console.log('next_step called on channel ' + channel);
  var quit = false; //quit is local
	arb_cycling_step[channel]++
  console.log('cycle number is ', cycling_cycle[channel])
  console.log('step number is ', arb_cycling_step[channel])

	if (arb_cycling_step[channel] >= arb_cycling_settings[channel].length) 
	{

	  arb_cycling_step[channel] = 0
    cycling_cycle[channel]++

	  if (cycling_cycle[channel] < cycling_cycles[channel]) 
    { 
      console.log('new cycle sent to the arduino ' , cycling_cycle[channel])
      console.log(cycling_cycle[channel])
      toArd(channel, 'y', cycling_cycle[channel])
    } //change to make sure that cycles can go forever and ever...
	  else
	  {
	    test_finished(channel);
	    arb_cycling[channel] = false //stops going back into loop
	    quit = true
	  }
	}
  else{
    console.log('next step in cycle')
  }
  console.log(quit)
	if (quit != true) cycling_mode(channel) //if quit is true - then things will stop ( I hope )
	//TODO:add in the ability to pause and skip steps while cycling. 
}

function cycling_mode(channel)
{
  console.log("cycling_mode on channel " + channel);
  //console.log(arb_cycling_step[channel])
	arb_cycling_step_start_time[channel] = new Date().getTime()
  //console.log('arb cycling settings ' , arb_cycling_settings[channel] )
	this_set = arb_cycling_settings[channel][arb_cycling_step[channel]]
  console.log(this_set) // checking if this_set is always local - I hope so... Seems like it. But could become issue I guess.
	if (this_set['cyc_mode']=='Potentiostatic')
	{
		potentiostat(channel,parseFloat(this_set['cyc_value']))
		console.log("set potentiostat");
	}
	if (this_set['cyc_mode']=='galvanostatic')
	{
		if (this_set['value'] == 0) set_ocv(channel)
		else galvanostat(channel,parseFloat(this_set['cyc_value']))
		console.log("set galvanostat");
	}
	if (this_set['cyc_mode'] == 'Rest')
	{
    console.log('this is a rest step')
	  set_ocv(channel)
	  console.log("set rest");
	}
}
//===================================================================================

//calibration section
//____________________________________________________________________________________


function calibrator(channel, value)
{
	rfixed[channel] = parseFloat(value)
	//console.log(rfixed)
	calibrate[channel] = false
	counter[channel] = 0
	calloop[channel] = 0
  toArd(channel,"R","0255");
	setTimeout(function(){calibrate[channel] = true},100)
	console.log("this is the calibrator on channel " + channel);
}


//because looping around - think I need to make out_table and final_table channel dependent... 
out_table = {}
final_table = {}


//kinda like declaring global variables right next to functions that use them...
function calibrate_step(channel)
{
		counter[channel]++;
		console.log('calibrate step ',counter[channel])
		if (counter[channel] > 255)
		{
			counter[channel] = 0	
			calloop[channel]++
      console.log('call loop is ' + calloop[channel]) 
      console.log('call limit is ' + callimit[channel])
			if (calloop[channel] > callimit[channel])
			{
				calibrate[channel] = false
				out_table[channel] = {} //outtable local 
				//console.log('making final table');
				//console.log(calibration_array[channel]);
				//console.log(calibration_array[channel].length)
				for (i = 0; i < calibration_array[channel].length; i++)
				{
					this_foo = calibration_array[channel][i] //this_foo is local
					//console.log(this_foo);
					res_set = this_foo['res_set'] //local
					dac_potential = this_foo['dac_potential']
					cell_potential = this_foo['cell_potential']
					gnd_potential = this_foo['gnd_potential']
					res_value = rfixed[channel]*(((dac_potential-gnd_potential)/(cell_potential-gnd_potential)) - 1)					
					if (out_table[channel][res_set] == undefined) out_table[channel][res_set] = []
					out_table[channel][res_set].push(res_value)
				}
				//console.log('out table below');
				//console.log(out_table)
				final_table[channel] = {}
				for (var key in out_table[channel])
				{
					if (out_table[channel].hasOwnProperty(key)) 
					{
						arr = out_table[channel][key]
						sum = 0
						for (var i = 0; i < arr.length; i ++)
						{
							sum = sum + arr[i]
						}
						average = sum/(arr.length)
						final_table[channel][key] = average
					}
				  
				}
				console.log('final_table is ' ,final_table[channel] , ' on channel ' + channel)
        //TODO: create resistance table folder if there isn't one.
        console.log(ardustat_id[channel])
				fs.writeFileSync("resistance_tables/unit_"+ardustat_id[channel].toString()+".json",JSON.stringify(final_table[channel])) //should be cool that this is synchrnous
        //TODO urgent - child process that automagically calls the python script.
				res_table[channel] = undefined;
				io_emit(channel, 'calibration finished'); //TODO channel change
        //TODO: call a python program that converts the json file into a pickle file for later use... should be easy enough to do.
			}
		} 
		setTimeout(function(){toArd(channel,"r",counter[channel])},50);
}
//_____________________________________________________________________________________

//SETTING FUNCTIONS that abstracted electro stuff calls.


// could either hack like have done in python - or could try and do properly like node
function moveground(channel,value)
{

	value_to_ardustat = value / volts_per_tick; //value_to_ardustat local, value is given, volts_per_tick always the same
	//console.log("moveground");
	//console.log(value + " " + volts_per_tick);
	//console.log(value_to_ardustat);
	toArd(channel,"d",value_to_ardustat)
	toArd(channel,"-","0000");
}

//sets arudstat to open circuit potential
function set_ocv(channel)
{
  toArd(channel,'-',0);
}

function potentiostat(channel,value)
{
	value_to_ardustat = value / volts_per_tick;
	toArd(channel,"p",value_to_ardustat)
}

//Set Galvanostat
//This stuff won't handle negative currents... 
//TODO: check if potentiostat handles negative curents.
function galvanostat(channel,value)//TODO:go through and fix this.
{ 
  value = value/1000
	foovalue = Math.abs(value)
	//First Match R
	r_guess = 1/foovalue //used to be 0.1 changed cause thats what i did in python. 
	console.log('r_guess',r_guess)
	target = 1000000
	r_best = 0
	set_best = 0
	for (var key in res_table[channel])
	{
		if (Math.abs(r_guess-res_table[channel][key]) < target)
		{
			//console.log("got something better")
			console.log('key is ',key);
			target = Math.abs(r_guess-res_table[channel][key]) 
			r_best = res_table[channel][key]
			set_best = key
			
		}
	} 
	//console.log(res_table) //why is this undefined?

	//now solve for V
	delta_potential = Math.abs(value*r_best)
	console.log('r_best ', r_best);
	console.log('value ' , value);
	console.log('volts per tick ' , volts_per_tick)
	value_to_ardustat = delta_potential / volts_per_tick;
	//some hacks cause i'm tired as
	if (value_to_ardustat > 1023) {value_to_ardustat = 1023}
	if (value < 0) { value_to_ardustat = value_to_ardustat +2000 }
	
	console.log('value_to_ardustat ' , value_to_ardustat + ' on channel ' + channel);
	console.log('set_best', set_best+ ' on channel ' + channel)
	console.log('value to ardustat ', value_to_ardustat+ ' on channel ' + channel)
	toArd(channel,"r",parseInt(set_best))
	toArd(channel,"g",parseInt(value_to_ardustat))
	
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
function ardupadder(command,number) // not sure if channel needed...
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

//Because these are called directly from browser - I think channel needs to be included in, and then extracted from the URL string
//Might play with this a little later... Unecessary and complicated to play with right now...
writer = function(req,res){	
	if(kill==false) {	
		toSend = req.originalUrl.replace("/write/","")
		toSend = decodeURIComponent(toSend);
        //command = toSend;
//hack to make sure that CSV is turned on - only problem is that it might not know which file to write to - might be better than nothing - anyway i dont think that this is the problem.
        if ((toSend.indexOf("p") > -1) || (toSend.indexOf("g") > -1)) CSV_ON = true;
        command_list[channel].push(toSend);
        //queue.push(toSend);
    		//serialPort.write(toSend);
		res.send(toSend);
	}
	else { res.send("killed :("); }
};


reader = function(req, res){
	if(kill==false) {
	    //console.log("this is from app.js");
	    console.log('buffer is ' +buf); //console.log doesn't actually work - I think that the function res.send gets called first which exits out of it. 
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

//Need to have channel for these...
function pauser(req,res)
{
  var temp = req.originalUrl.replace("/pauser/","") //For sure this isn't the fastest way to do it, but yolo swag monster...
  channel = decodeURIComponent(temp);
  console.log('pauser has been called on channel ' + channel)

	test_running[channel] = true;
	kill[channel] = true;
	console.log('method control has been paused, and CSV writing has been paused');
	res.send('method control has been pause, and CSV writing has been pause');
	CSV_ON[channel] = false;
	pause_time[channel] = new Date().getTime()
}

function test_finished(channel) // yay this can be called somewhat normally...
{
  console.log('test finished called on channel ' + channel);
  set_ocv(channel)
	console.log('method control has been stopped and CSV writing has been killed')
  test_running[channel] = false;
	kill[channel] = true;
	CSV_ON[channel] = false;
  setTimeout(function(){reset_globals(channel)},1000)

	io_emit(channel, 'stop message'); // io_emit(channel, 'stop message')
	//should also save the position. incase program crashes.
}


function killer(req,res) 
{
  var temp = req.originalUrl.replace("/killing/","") //For sure this isn't the fastest way to do it, but yolo swag monster...
  channel = decodeURIComponent(temp);
  channel = channel.toString()

  console.log('killer called on channel:'+channel);
  set_ocv(channel)
  test_finished(channel)
	res.send('method control has been stopped, and CSV writing has been killed')
};

//resume control and forwarding to csv
function reviver(req,res,callback) 
{
  var temp = req.originalUrl.replace("/reviver/","") //For sure this isn't the fastest way to do it, but yolo swag monster...
  channel = decodeURIComponent(temp);

	console.log('reviver called on channel ' + channel );
	res.send('reviver called');
	if (cv[channel]) { cv_time[channel] = new Date().getTime()	 }
  if (arb_cycling[channel]) { arb_cycling_step_start_time[channel] = new Date().getTime()	 }
  console.log('time set to start of step')
  l_writer(channel,last_comm[channel]) //sets the command the same as before 
  console.log('this is what we are reviving to ' + last_comm[channel]);
  resume_time[channel] = new Date().getTime()
  total_pause_time[channel] = total_pause_time[channel] + (resume_time[channel] - pause_time[channel]);
  console.log('total_pause_time of channel ' + channel +' is ' + total_pause_time[channel]);
  callback(channel)
};

function flag_resume(channel)
{
  console.log('flag_resume called on channel ' + channel);
  kill[channel] = false;
  CSV_ON[channel] = true;
}


function step_skip(req,res)
{
  var temp = req.originalUrl.replace("/step_skip/","") //For sure this isn't the fastest way to do it, but yolo swag monster...
  channel = decodeURIComponent(temp);

  console.log('step skip has been called on channel ' + channel)
  next_step(channel)
  skip_time[channel] = new Date().getTime()
  skip_flag[channel] = true;
  res.send('step has been skipped')
}

//trying to show files that have been uploaded.
//try and show folders - then can click on folders to see files in them 
function analysis_display(req,res,indexer)
{
  console.log('analysis_display has been called');
	out = fs.readdirSync('Data/')
	console.log('the data is ' + out) ;
  lts = '<div id="folders" >'
  count_limit = 20;

  count = 0 
  for (var i in out)
  {	
    foo = out[i]
	  if (foo != "temper") lts += "<button id='"+foo+"'>"+foo+ "</button><br>";
	  count +=1
	  if (count > count_limit) break; 
  }
  lts += '</div>'
  indexer = indexer.replace("##_newthings_##",lts);
  res.send(indexer);
}

function file_display(req,res)
{
  console.log('file_display called');
  console.log(req.body.folder) 
  folder = req.body.folder
  out = fs.readdirSync('Data/'+folder)
  console.log('the files are ' + out);
  res.send(out)
  io_emit('analysis','hey dan you can nap now');
}
//This is the thing that runs everything! 
// Need to make this work with seperate channels.
//==========================================================

//can write this really ugly - no one really cares. 
command_list = {}
command_list.ch1 = []
command_list.ch2 = []
command_list.ch3 = []

t2 = setInterval(function()
{
  command_list.ch1.push('s0000');
  command_list.ch2.push('s0000');
  command_list.ch3.push('s0000');

  if (calibrate.ch1) calibrate_step('ch1')
  if (calibrate.ch2) calibrate_step('ch2')
  if (calibrate.ch3) calibrate_step('ch3')

  if (cv_resting.ch1) cv_rester('ch1')
  if (cv_resting.ch2) cv_rester('ch2')
  if (cv_resting.ch3) cv_rester('ch3')
   //this is the resting phase at the start of a cv
  if ((cv.ch1) && (kill.ch1 == false)) cv_stepper('ch1')
  if ((cv.ch2) && (kill.ch2 == false)) cv_stepper('ch2')
  if ((cv.ch3) && (kill.ch3 == false)) cv_stepper('ch3')

  if ((cv_finisher_flag.ch1) && (kill.ch1 == false)) cv_finisher('ch1')
  if ((cv_finisher_flag.ch2) && (kill.ch2 == false)) cv_finisher('ch2')
  if ((cv_finisher_flag.ch3) && (kill.ch3 == false)) cv_finisher('ch3')

  if ((arb_cycling.ch1) && (kill.ch1 == false)) cycling_stepper('ch1')
  if ((arb_cycling.ch2) && (kill.ch2 == false)) cycling_stepper('ch2')
  if ((arb_cycling.ch3) && (kill.ch3 == false)) cycling_stepper('ch3')

}, 1000);

t1 = setInterval(function()
{
  //console.log('print something');
  if (ports.length > 0)
  {
  //console.log('got here')
  	if (command_list.ch1.length > 0)
  	{
  	  //console.log(command_list.ch1);
  		sout = command_list.ch1.shift();
  		//if (sout != "s0000") console.log('sout on ch1 is '+sout);
      //if (ports.length > 0 ) ports[0].write(sout);	
      if (ports.length > 0 ) ports_dict.ch1.write(sout);  
      //console.log(ports_dict)
  	}
  }
  if (ports.length > 1)
  {
    if (command_list.ch2.length > 0)
    {
      sout = command_list.ch2.shift();
      //if (sout != "s0000") console.log('sout on ch2 is '+sout);
      if (ports.length > 1 ) ports_dict.ch2.write(sout);  
    }
  }
  if (ports.length > 2)
  {
    if (command_list.ch3.length > 0)
    {
      sout = command_list.ch3.shift();
      //if (sout != "s0000") console.log('sout on ch3 is '+sout);
      if (ports.length > 1 ) ports_dict.ch3.write(sout);  
    }
  }
},15)

function replacer_2(req,res,indexer){
  console.log('replacer called');
  //indexer = indexer.replace("##_channel_##",'something else');
  indexer = indexer.replace("channel = 'ch1'","channel = 'ch2'");
  indexer = indexer.replace("document.getElementById('navbar-channel1').setAttribute('class', 'active')","document.getElementById('navbar-channel2').setAttribute('class', 'active')")
  indexer = indexer.replace('<script src="/scripts/Channel1/socket_1.js"></script>','<script src="/scripts/Channel2/socket_2.js"></script>')
  res.send(indexer);
  console.log('replacer finished') 
}

function replacer_3(req,res,indexer){
  console.log('replacer called');
  indexer = indexer.replace("channel = 'ch1'","channel = 'ch3'");
  indexer = indexer.replace("document.getElementById('navbar-channel1').setAttribute('class', 'active')","document.getElementById('navbar-channel3').setAttribute('class', 'active')")
  indexer = indexer.replace('<script src="/scripts/Channel1/socket_1.js"></script>','<script src="/scripts/Channel3/socket_3.js"></script>')
  res.send(indexer);
  console.log('replacer finished') 
}
//==========================================================
// export functionality
module.exports = {
  blink_button:blink_button,
  replacer_2:replacer_2,
  replacer_3:replacer_3,
  logstuff:logstuff,
  setstuff:setstuff,
  test:test,
  reader:reader,
  writer:writer,
  starter:starter,
  stopper:stopper,
  name_setter:name_setter,
  killer: killer,
  pauser: pauser,
  reviver:reviver,
  flag_resume:flag_resume,
  step_skip:step_skip,
  file_display:file_display,
  analysis_display:analysis_display,
  listen:listen,
  give_status:give_status
};


