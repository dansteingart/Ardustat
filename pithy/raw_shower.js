//NodeJS Imports to Make Everything Just Work
var http = require("http"); //HTTP Server
var url = require("url"); // URL Handling
var fs = require('fs'); // Filesystem Access (writing files)
var os = require("os"); //OS lib, used here for detecting which operating system we're using
var util = require("util");
var express = require('express'); //App Framework (similar to web.py abstraction)
var app = express();
var os = require("os")
var exec = require('child_process').exec;
//var sh = require('execSync');
var cors = require('cors');
server = http.createServer(app)

//Basic Settings
settings = {
	"python_path" : "python",
	'prepend' : ""	
}

//Set Static Directories
app.use(express.bodyParser());
app.use(cors());
app.use("/static", express.static(__dirname + '/static'));
app.use("/images", express.static(__dirname + '/images'));


app.get('/*', function(req, res){

	if (req.params[0] == "") 
	{
		res.send("try harder");
	}

	else
	{
		
		//here's were we do a lot of fun stuff
		try
		{
			nameo = req.url
			parts = nameo.split("/");
			estring = "";
			for (var i=2; i < parts.length;i++) 
			{
				estring += parts[i]+" ";
			}
			fullcmd = settings.python_path+" -u '"+__dirname+"/code/"+parts[1]+".py' "+estring
			//this is bad
			//var sys = require('sys')
			//var exec = require('child_process').exec;
			//function puts(error, stdout, stderr) { sys.puts(stdout) }
			
			exec(fullcmd,
					function(error, stdout, stderr)
					{
						res.send(stdout);
					}
				)
			//results = sh.exec(fullcmd)
			//res.send(results.stdout)
		}
		catch (err)
		{
			console.log(err)
		}
		//console.log(req.url)
		//res.send("you tried harder")
		
	}
});



//Start It Up!
server.listen(process.argv[2]);
console.log('Listening on port '+process.argv[2]);

