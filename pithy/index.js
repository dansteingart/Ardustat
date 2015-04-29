//NodeJS Imports to Make Everything Just Work
var sharejs = require('share').server;

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
var glob = require('glob')
var options = {db: {type: 'none'}};
 
server = http.createServer(app)
sharejs.attach(app, options);

io = require('socket.io')
io = io.listen(server); //Socket Creations
io.set('log level', 1)

//POC = process.argv[2]
POC = "" //trust me
console.log("reflecting changes oK!")


// app.use(express.basicAuth(function(user, pass, callback) {
 
// 	raw = fs.readFileSync("pass.json").toString();
// 	things = JSON.parse(raw);
// 	names = things['things']
// 	var result = null;
// 	for (i in names)
// 	{
// 		nuser = names[i]['user'];
// 		npass = names[i]['pass'];
// 		if (user == nuser & pass == npass )
// 		{
// 			result = (user === nuser && pass === pass);
// 			result = user;
// 			//req.user = user
// 		} 
// 	}
//  	callback(null /* error */, result);

// }));



//big hack to make killing work
var os_offset = 2
if (os.platform() == 'darwin') os_offset = 2

//make required directories
dirs = ['temp_results','code','code_stamped','results','marked_results','images','files']
for (d in dirs)
{
	dird = dirs[d]+POC.toString()
	console.log(dird)
	try
	{
		fs.mkdirSync(dird); 
		console.log(dird+" has been made")
		
	}
	catch (e) 
	{
		console.log(dird+" is in place")
	}
}

codebase = "code"+POC+"/"
histbase = "code_stamped"+POC+"/"
tempbase = "temp_results"+POC+"/"
resbase = "results"+POC+"/"
stored_resbase = "marked_results"+POC+"/"

imgbase = "images"+POC+"/"
filebase = "files"+POC+"/"


//create pithy.py lib if it doesn't already exist
try
{
	checkface = fs.readFileSync(codebase+'/pithy.py').toString()
	console.log("pithy.py is in place")
	
}
catch (e)
{
	console.log("making a pithy library")
	fs.writeFileSync(codebase+'/pithy.py',fs.readFileSync('static/prepend.txt').toString())
}

//create pass.json file if it doesn't already exist
try
{
	checkface = fs.readFileSync('pass'+POC+'.json').toString()
	console.log("pass.json is in place")
	
}
catch (e)
{
	console.log("making a password file")
	fs.writeFileSync('pass'+POC+'.json',fs.readFileSync('static/passmold').toString())
}

//Basic Settings
settings = {
	//"bad_words" : ["rm ","write","while True:","open "],
	"python_path" : "/usr/bin/python",
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
app.use("/"+filebase, express.static(__dirname + "/"+filebase));

//http://stackoverflow.com/a/4698083/565514
function sJAP(objArray, prop, direction){
    if (arguments.length<2) throw new Error("sortJsonArrayByProp requires 2 arguments");
    var direct = arguments.length>2 ? arguments[2] : 1; //Default to ascending

    if (objArray && objArray.constructor===Array){
        var propPath = (prop.constructor===Array) ? prop : prop.split(".");
        objArray.sort(function(a,b){
            for (var p in propPath){
                if (a[propPath[p]] && b[propPath[p]]){
                    a = a[propPath[p]];
                    b = b[propPath[p]];
                }
            }
            // convert numeric strings to integers
            a = a.match(/^\d+$/) ? +a : a;
            b = b.match(/^\d+$/) ? +b : b;
            return ( (a < b) ? -1*direct : ((a > b) ? 1*direct : 0) );
        });
    }
}

activefiles = []
hist_dict = []

function getBigHistory()
{
	out = fs.readdirSync(histbase)

	hist_dict = []
	for (i in activefiles)
	{
	
		its = activefiles[i].replace(".py","")
		things = activefiles[i].replace(".py","_1*")
		globs = glob.sync(histbase+"/"+things)
		hist_dict[hist_dict.length] = {'fil':its,'hits':globs.length}
	}

	//sort files (ht to http://stackoverflow.com/a/10559790)
	hist_dict.sort(function(a, b) {
	               return a.hits - b.hits;
	           });
	hist_dict.reverse()
	
}

//getBigHistory()
/*
setInterval(
	function()
	{
		//getBigHistory()
	},60000)
*/

app.get('/*', function(req, res){

	if (req.params[0] == "") 
	{
		//res.redirect("/"+makeid());
		if (req.params[0] == "") 
		{
			indexer = fs.readFileSync('static/homepage.html').toString()

			//New Files
			//get file list
			out = fs.readdirSync(codebase)
			//sort files (ht to http://stackoverflow.com/a/10559790)
			
			out.sort(function(a, b) {
			               return fs.statSync(codebase + a).ctime - 
			                      fs.statSync(codebase + b).ctime;
			           });
	 		out.reverse()
			
			lts = "" //list to send
			count_limit = 20;
			
			count = 0 
			for (var i in out)
			{	foo = out[i].replace(".py","")
				dater = fs.statSync(codebase + out[i]).ctime.toDateString()
				if (foo != "temper" && foo !=".git") lts += "<span class='leftin'><a href='/"+foo+"'>"+foo+ "</a></span><span class='rightin'> " + dater+"</span><br>";
				count +=1
				if (count > count_limit) break; 
			}

			base_case = 0

			indexer = indexer.replace("##_newthings_##",lts)
			activefiles = out
		
		
			//Hist Files
			//get file list
			
			
				
			lts = "" //list to send
		
			count = 0 
			
			for (j in hist_dict)
			{	
				i = hist_dict[j]['fil']
				k = hist_dict[j]['hits']
			
				if (i != "temper") lts += "<span class='leftin'><a href='/"+i+"'>"+i+ "</a></span><span class='rightin'> " + k+" edits</span><br>";
				count +=1
				if (count > count_limit) break; 
			}

			base_case = "0"

			indexer = indexer.replace("##_changethings_##",lts)


			//New Files
			//get file list
			out = fs.readdirSync(filebase)
			//sort files (ht to http://stackoverflow.com/a/10559790)
			out.sort(function(a, b) {
			               return fs.statSync(filebase + a).ctime - 
			                      fs.statSync(filebase + b).ctime;
			           });
	 		out.reverse()
			lts = "" //list to send
		
			count_limit = 20;
			
			count = 0 
			for (var i in out)
			{	foo = out[i]//.replace(".py","")
				dater = fs.statSync(filebase + out[i]).ctime.toDateString()
				lts += "<span class='leftin'><a href='/files/"+foo+"'>"+foo+ "</a></span><span class='rightin'> " + dater+"</span><br>";
				count +=1
				if (count > count_limit) break; 
			}

			base_case = 0

			indexer = indexer.replace("##_popthings_##",lts)
			

			res.send(indexer)

		}

	}

	else if(req.params[0] == "files/" || req.params[0] == "files")
	{
		indexer = fs.readFileSync('static/filedex.html').toString()
		//get file list
		out = fs.readdirSync(filebase)
		//sort files (ht to http://stackoverflow.com/a/10559790)
		out.sort(function(a, b) {
		               return fs.statSync(filebase + a).ctime - 
		                      fs.statSync(filebase + b).ctime;
		           });
 		out.reverse()
		lts = "" //list to send
		for (i in out)
		{
			lts += "<a href='/"+filebase+out[i]+"'>"+out[i] + "</a> , " + fs.statSync(filebase + out[i]).ctime+"<br>";
		}
		indexer = indexer.replace("##_filesgohere_##",lts)
		res.send(indexer)
		
	}
	else
	{
		indexer = fs.readFileSync('static/index.html').toString()
		res.send(indexer)
	}
  	//console.log(req.params)
});

app.post("*/killer",function(req,res)
	{
		
		x = req.body.page_name;
		console.log(x)
		thispid = processes[x];
		
		console.log("trying to kill " + x)
		if (thispid != undefined)
		{
			console.log("killing "+thispid)
			//exec("kill "+thispid,function(stdout,stderr)
			exec("/usr/bin/python killer.py "+x,function(stdout,stderr)
			
			{
				outer = stdout+","+stderr
				console.log(outer)
				if (outer.search("No such process") == -1)
				{
					console.log(thispid)
					delete processes[x];
					timers[thispid] = false
				}
			})
		}
	res.json({success:true})	
})

app.post('*/run', function(req, res)
{
	x = req.body
	//console.log(x)
	page_name = x['page_name'].replace("/","").split("/")[0]
	script_name = x['script_name']
	prepend = settings.prepend		
	out = ""
	image_list = []
	//io.sockets.emit(page_name,{'out':"waiting for output"}) 
	//Querer to prevent race condition
	send_list.push({'page_name':page_name,'data':{out:"waiting for output"}})
	time = new Date().getTime().toString()
	counter = 0
	data = x['value']
	for (b in settings.bad_words)
	{
		if (data.search(b) > -1)
		{
			out = "Found '"+b+"', this is a BAD WORD"
			res.json({'out':out,'images':image_list})
			break
		}
	}
	temp =""

	full_name = page_name+".py"
	
	try
	{
		temp = fs.readFileSync(codebase+full_name).toString()
	}
	catch (e)
	{
		temp = "dood"
	}

	if (temp != data || temp == "dood")
	{
		
		fs.writeFileSync(codebase+full_name,data);
		fs.writeFileSync(histbase+page_name+"_"+time,data);
		
		if (gitted)
		{
			gitter = "cd code; git add *.py; git commit -m 'auto commit; user:"+req.user+"'; git push"
			exec(gitter);
			console.log('user:'+req.user);
		}
	}

/*	
	data = prepend+data
	while (data.search("showme()")>-1)
	{
		data = data.replace("showme()","save_image('"+page_name+"_"+time+"')\n",1)
		counter ++;
	}
*/	
	
	//fs.writeFileSync(codebase+"temper.py",data)
	res.json({success:true})	
	if (processes[page_name] == undefined) gofer = betterexec(page_name,x)
	console.log(gofer)
	//processes[page_name] = gofer['id']
	processes[page_name] = gofer['name']
	//console.log(processes[page_name])
	console.log(processes)
	timers[processes[page_name]] = true
	
});

app.post('*/history', function(req, res)
{
	x = req.body;
	page_name = x['page_name']
	length = "_1314970891000".length //get length of timestamp
	structure = histbase+page_name+"*"
	thing_list = []

	fils  = fs.readdirSync(histbase)
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


app.post('*/markedresults', function(req, res)
{
	x = req.body;
	page_name = x['page_name']
	console.log(x)
	length = "_1314970891000".length //get length of timestamp
	structure = stored_resbase+page_name+"*"
	thing_list = []

	fils  = fs.readdirSync(stored_resbase)
	for (i in fils)
	{
		console.log(fils[i])
		console.log(page_name)
		if (fils[i].search(page_name+"_") > -1) 
		{
			thing_list.push(fils[i])
		}
	}
		
	fils = thing_list
	fils.sort()
	fils.reverse()
	console.log(fils);
	
	hist_list = []
	for (i in fils)
	{
		//time_part = parseInt(fils[i].split("_")[1])
		time_part = parseInt(fils[i].substr(fils[i].length - length+1))
		marked_name = JSON.parse(fs.readFileSync(stored_resbase+fils[i]))['name']
		hist_list.push([fils[i],marked_name])
	}
	console.log(hist_list);
		
	res.json({'out':hist_list})
});


app.post('*/read', function(req, res)
{
	
	x = req.body
	back_to_pith = {}
	out = "Fill Me Up"
	//page_name = x['page_name'].replace("/","")
	page_name = x['page_name'].replace("/","").split("/")[0]
	
	try{
	try
	{
		out = fs.readFileSync(codebase+page_name+".py").toString()
		
		
	}
	catch (e)
	{
		out = fs.readFileSync(histbase+page_name).toString()		
	}
	}
	catch (e)
	{
		out = "fill me up"
	}

	back_to_pith['script'] = out
	res.json(back_to_pith)
	
	try
	{
		resulters = fs.readFileSync(resbase+page_name).toString()
		resulters = JSON.parse(resulters)	
		//setTimeout(function()
		//{
		//Don't send saved results if this script is running
		if (!processes.hasOwnProperty(page_name)) send_list.push({'page_name':page_name,'data':resulters})
		//},1000);
		
	}
	catch (e)
	{	
		console.log(e)
	}
	
});

app.post('*/readresults', function(req, res)
{
	
	x = req.body
	back_to_pith = {}
	out = "Fill Me Up"
	page_name = x['page_name']
	try
	{
		out = fs.readFileSync(resbase+page_name).toString()		
	}
	catch (e)
	{
		//console.log(e)
		out = "fill me up"
	}
	//console.log(out)
	res.json( JSON.parse(out) )
	
});

app.post('*/copyto',function(req,res)
{
	x = req.body
	page_name = x['page_name'].replace("/","")
	script_name = x['script_name']
	data = x['value']
	full_name = script_name+".py"
	fs.writeFileSync(codebase+full_name,data);
	res.json({success:true,redirect:script_name})	

})

app.post('*/markresult',function(req,res)
{
	x = req.body
	page_name = x['page_name'].replace("/","")
	result_name = x['result_name']
	console.log(result_name)
	result_set = ""
	try
	{
		hacky_name = stored_resbase+page_name+"_"+parseInt(new Date().getTime())
		out = fs.readFileSync(resbase+page_name).toString()		
		result_set = JSON.parse(out)
		result_set['code'] = fs.readFileSync(codebase+page_name+".py").toString()
		result_set['name'] = result_name
		result_set['filename'] = hacky_name
		fs.writeFileSync(hacky_name,JSON.stringify(result_set))
	}
	catch (e)
	{
		//console.log(e)
		out = "fill me up"
	}
	
	console.log(result_set)
})



gitted = false;
for (var i = 0; i < process.argv.length;i++)
{
	if (process.argv[i] == "--gitted") gitted = true;
}

//Start It Up!
server.listen(process.argv[2]);
console.log('Listening on port '+process.argv[2]);

//----------Helper Functions----------------------------

times = {}
//big ups to http://stackoverflow.com/questions/13162136/node-js-is-there-a-way-for-the-callback-function-of-child-process-exec-to-ret/13166437#13166437
function betterexec(nameo,fff)
{
	//fullcmd = "touch temp_results/"+nameo +"; " +settings.python_path+" -W ignore -u '"+__dirname+"/code/"+namemo+".py' > 'temp_results/"+nameo+"'"
	
	parts = fff['page_name'].split("/")
	estring = "";
	for (var i=2; i < parts.length;i++) 
	{
		estring += parts[i]+" ";
	}
	console.log(parts)
	console.log(estring)
	console.log(__dirname)
	essence = __dirname+"/"+codebase+nameo
	big_gulp = settings.python_path+" -u '"+essence+".py' "+estring
	fullcmd = "touch "+tempbase+parts[1] +"; " +big_gulp+" > '"+tempbase+nameo+"'"
	
	start_time = new Date().getTime()
	lastcheck[nameo] = start_time
	times[nameo] = start_time
	chill = exec(fullcmd,
	function (error, stdout, stderr) {
		this_pid = chill.pid
		console.log("this pid is " +this_pid)
		hacky_name = nameo
		timers[processes[hacky_name]] = false
		console.log(hacky_name+" is done")
		end_time = new Date().getTime()
		delete processes[hacky_name];
		delete times[hacky_name];		
		//fils = fs.readdirSync("images")
		exec_time = end_time - start_time;
		foost = fs.readFileSync(tempbase+nameo).toString()
		big_out = {'out':stdout+foost,'outerr':stderr,'images':[],'exec_time':exec_time}
		send_list.push({'page_name':hacky_name,'data':big_out})
		if (stderr.search("Terminated") == -1) fs.writeFileSync(resbase+hacky_name,JSON.stringify(big_out))
		
	})
	//console.log(big_gulp)
	return {'pid':chill.pid + os_offset,'name':essence}
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

//Queue to prevent socket race conditions, fires a message from the buffer every x ms
//TODO: Figure out how to reduce interval time without 
//buffer?
old_send = []
setInterval(function(){
	this_send = send_list.splice(0,1)[0]
	
	if (this_send != undefined) 
	{
			//console.log(send_list.length + " message(s) in queue")
			io.sockets.emit(this_send['page_name'],this_send['data'])
			old_send = this_send
		
	};
},100)




//Process Checker
setInterval(function() {
	for (p in processes)
	{
		bettertop(p)
	
	}
}, 1000);


//flush images
setInterval(function() {
	
	chill = exec("rm images/*",
		function (error, stdout, stderr) 
		{
			console.log(stdout)
			console.log("flushed images")
		}
)
	}, 6000000);
	

lastcheck = {}

function bettertop(p)
{
	try{
		now = new Date().getTime()
		diff = now - times[p]
		filemtime = new Date(fs.statSync(tempbase+p)['mtime']).getTime()
		diff2 = filemtime - lastcheck[p]
		//if ((diff2) > 100)
		//{
			lastcheck[p] = now
			outer = fs.readFileSync(tempbase+p).toString() + "\n<i>been working for " + diff + " ms</i>" 
			send_list.push({'page_name':p,'data':{out:outer}})
	//	}	
		
	}
	catch(e){
		console.log(processes[p]);
		console.log(results)
		console.log(e)
	}
	
}
