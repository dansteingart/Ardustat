//NodeJS Imports to Make Everything Just Work
var http = require("http"); //HTTP Server
var url = require("url"); // URL Handling
var fs = require('fs'); // Filesystem Access (writing files)
var os = require("os"); //OS lib, used here for detecting which operating system we're using
var util = require("util");
var express = require('express'); //App Framework (similar to web.py abstraction)
var app = express();
var exec = require('child_process').exec,
    child;
var spawn = require('child_process').spawn,
	child;
var os = require("os")
var sh = require("execSync")
server = http.createServer(app)
io = require('socket.io')
io = io.listen(server); //Socket Creations
io.set('log level', 1)


//big hack to make killing working
var os_offset = 1
if (os.platform() == 'darwin') os_offset = 2

//make required directories
dirs = ['temp_results','code','code_stamped','results','images']
for (d in dirs)
{
	try
	{
		fs.mkdirSync(dirs[d]); 
		console.log(dirs[d]+" has been made")
		
	}
	catch (e) 
	{
		console.log(dirs[d]+" is in place")
	}
}


//create pithy.py lib if it doesn't already exist
try
{
	checkface = fs.readFileSync('code/pithy.py').toString()
}
catch (e)
{
	console.log("making a pithy library")
	fs.writeFileSync('code/pithy.py',fs.readFileSync('static/prepend.txt').toString())
}

//Basic Settings
settings = {
	//"bad_words" : ["rm ","write","while True:","open "],
	"python_path" : "python",
	//'prepend' : "fs.readFileSync('static/prepend.txt').toString()"
	'prepend' : ""
	
}


//Clean Up Via: http://stackoverflow.com/a/9918524/565514
var clients = {}
io.sockets.on('connection', function(socket) {
  	console.log(socket.id +" Connected")
  	var count = 0;
	for (var k in clients) {if (clients.hasOwnProperty(k)) {++count;}}
	console.log("Clients Connected:"+count)
	clients[socket.id] = socket;

  socket.on('disconnect', function() {
	console.log(socket.id +" Disconnected")
  	var count = 0;
	for (var k in clients) {if (clients.hasOwnProperty(k)) {++count;}}
	console.log("Clients Connected:"+count)
    delete clients[socket.id];
  });
});


//Process Management variables
var timers = []
var processes = {}
var send_list = []
var spawn_list = {}
var intervalers = {}
var results = {}

//Set Static Directories
app.use(express.bodyParser());
app.use("/static", express.static(__dirname + '/static'));
app.use("/images", express.static(__dirname + '/images'));


app.get('/*', function(req, res){

	if (req.params[0] == "") 
	{
		res.send("try harder");
	}

	else
	{
		indexer = fs.readFileSync('static/shindex.html').toString()
		res.send(indexer)
	}
  	//console.log(req.params)
});

app.post("*/killer",function(req,res)
	{
		x = req.body;
		page_name = x['page_name'].replace("/","");
		thispid = processes[page_name];
		console.log(thispid)
		delete processes[page_name];
		timers[thispid] = false
		if (thispid != undefined)
		{
			console.log("killing "+thispid)
			exec("kill "+thispid,function(stdout,stderr)
			{
				console.log(stdout+","+stderr)
			})
		}
	res.json({success:true})	
})

app.post('*/run', function(req, res)
{
	x = req.body
	//console.log(x)
	page_name = x['page_name']
	parts = page_name.split("/");
	estring = "";
	for (p in parts)
	{
		estring += parts[p]+" ";
	}
	
	out = ""
	image_list = []
	//io.sockets.emit(page_name,{'out':"waiting for output"}) 
	//Querer to prevent race condition
	send_list.push({'page_name':parts[1],'data':{out:"waiting for output"}})
	time = new Date().getTime().toString()
	counter = 0

	full_name = parts[1]+".py"
	
	try
	{
		temp = fs.readFileSync("code/"+full_name).toString()
	}
	catch (e)
	{
		temp = "dood"
	}

	data = temp
	/*
	while (data.search("showme()")>-1)
	{
		gd = page_name.split("-")[0];
		
		data = data.replace("showme()","save_image('"+gd+"')\n",1)
		counter ++;
	}
	*/
	fs.writeFileSync("code/temper.py",data)
	res.json({success:true})	
	processes[parts[1]] = betterexec(page_name)
	console.log(processes[parts[1]])
	timers[processes[parts[1]]] = true
	
});

app.post('*/history', function(req, res)
{
	x = req.body;
	page_name = x['page_name'].replace("/","")
	length = "_1314970891000".length //get length of timestamp
	structure = "code_stamped/"+page_name+"*"
	thing_list = []

	fils  = fs.readdirSync("code_stamped")
	for (i in fils)
	{
		if (fils[i].search(page_name+"_") > -1) 
		{
			thing_list.push(fils[i])
		}
	}
		
	fils = thing_list
	fils.sort()
	fils.reverse()
	hist_list = []
	for (i in fils)
	{
		//time_part = parseInt(fils[i].split("_")[1])
		time_part = parseInt(fils[i].substr(fils[i].length - length+1))
		//console.log(time_part)
		date = new Date(time_part)
		hour = date.getHours()
		min = date.getMinutes()
		sec = date.getSeconds()
		day = date.getDate()
		month = date.getMonth()
		year = date.getYear()
		time_part = month+"/"+day+"/"+year+" "+hour+":"+min+":"+sec;
		hist_list.push([fils[i],date.toISOString()])
	}
		
	res.json({'out':hist_list})
});





//Start It Up!
server.listen(process.argv[2]);
console.log('Listening on port '+process.argv[2]);

//----------Helper Functions----------------------------

times = {}
//big ups to http://stackoverflow.com/questions/13162136/node-js-is-there-a-way-for-the-callback-function-of-child-process-exec-to-ret/13166437#13166437
function betterexec(nameo)
{
	parts = nameo.split("/");
	estring = "";
	for (var i=2; i < parts.length;i++) 
	{
		estring += parts[i]+" ";
	}
	
	fullcmd = "touch temp_results/"+parts[1] +"; " +settings.python_path+" -u '"+__dirname+"/code/temper.py' "+estring+" > 'temp_results/"+parts[1]+"'"
	
	start_time = new Date().getTime()
	lastcheck[nameo] = start_time
	times[nameo] = start_time
	chill = exec(fullcmd,
	function (error, stdout, stderr) {
		this_pid = chill.pid
		console.log("this pid is " +this_pid)
		hacky_name = nameo
		timers[processes[parts[1]]] = false
		console.log(parts[1]+" is done")
		end_time = new Date().getTime()
		delete processes[parts[1]];
		delete times[parts[1]];		
		//fils = fs.readdirSync("images")
		exec_time = end_time - start_time;
		foost = fs.readFileSync('temp_results/'+parts[1]).toString()
		console.log(foost)
		console.log(stderr)
		big_out = {'out':stdout+foost,'outerr':stderr,'images':[],'exec_time':exec_time}
		send_list.push({'page_name':nameo,'data':big_out})
		if (stderr.search("Terminated") == -1) fs.writeFileSync("results/"+parts[1],JSON.stringify(big_out))
		
	})
	return chill.pid + os_offset
}

//Makes random page
//cribbed from http://stackoverflow.com/a/1349426/565514
function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

//Queue to prevent socket race conditions, fires a message from the buffer every 500 ms
//TODO: Figure out how to reduce interval time without 
setInterval(function(){
	this_send = send_list.splice(0,1)[0]
	if (this_send != undefined) 
	{
		console.log(this_send)
		
		//console.log(send_list.length + " message(s) in queue")
		io.sockets.emit(this_send['page_name'],this_send['data'])
	};
},500)




//Process Checker
setInterval(function() {
	for (p in processes)
	{
		//bettertop(p)
	
	}
}, 50);

lastcheck = {}

