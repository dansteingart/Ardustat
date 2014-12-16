app_page = require('./app.js')
config_page = require('./config.js')
app = app_page.app;
toArdu = app_page.toArdu;
test = app_page.test;
serialPort = config_page.serialPort;
sleep = require('sleep').sleep
var squenty = require('sequenty');
var urllib = require('urllib'); //data is a buff instance https://www.npmjs.org/package/urllib




console.log("serialPort : " + serialPort);
console.log("this is functions :" + toArdu);
console.log("test " + test);

/*
		urllib.request('http://localhost:3001/startCSV/somefolder/somefile2', function (err,data,res) {
		  if (err) {
		    throw err;
		  }
		  console.log('status code: '+res.statusCode);
		  console.log('headers: ' + res.headers);
		  
		  console.log('data '+data.toString());
    });
*/
//abstracted url calls - doing it this way for debugging purposes and because I'm lazy. and also why not.
//once people are using it then I can change things.
//------------------------------------------------------------------------
hostsite = 'http://localhost:3001/'
function swrite(stringer){
  urllib.request(hostsite+'write/'+stringer, function (err,data,res) {
    if(err) {
      throw err;
    }
    console.log('wrote '+data.toString());
  });
};

//TODO: change to a call back
function sread(callback){
  urllib.request(hostsite+'read/', function (err,data,res) {
    console.log('here is the data: ' + data.toString());
    cv_reading = data.toString();
    callback();
  });
};
function startCSV(stringer){
  urllib.request(hostsite+'startCSV/'+stringer, function (err,data,res) {
    if(err) {
      
      throw err;
    }
    console.log('start ' +data.toString());
  });
};
function stopCSV(){
  urllib.request(hostsite+'stopCSV/', function (err,data,res) {
    if(err) {
      throw err;
    }
    console.log('stop '+ data.toString());
  });
};
function kill(){
  urllib.request(hostsite+'kill/', function (err,data,res) {
    if(err) {
      throw err;
    }
    console.log('kill ' + data.toString());
  });
};
function revive(){
  urllib.request(hostsite+'unkill/', function (err,data,res) {
    if(err) {
      throw err;
    }
    console.log( data.toString() );
  });
};
//---------------------------------------------------------------------------

  

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

		startCSV('some_folder2/some_file2');
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

// export functionality
module.exports = {
  logstuff:logstuff,
  setstuff:setstuff,
  test:test
};
