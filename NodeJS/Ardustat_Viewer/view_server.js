/*
TODO:

- Add command line variable for serial port
- Cycling Routines (think on framework)

*/

//Set it up
var http = require("http"); //HTTP Server
var url = require("url"); // URL Handling
var fs = require('fs'); // Filesystem Access (writing files)
var glob = require('glob'); // Easy directory searches (from python)
var express = require('express'), //App Framework (similar to web.py abstraction)
    app = express.createServer();
	app.use(express.bodyParser());
	app.use(app.router);

//MongoDB stuff
db_connected = false
try
{
	//var Mongolian = require("mongolian")
	//var server = new Mongolian
	var mongo = require('mongoskin');
	var db = mongo.db("localhost:27017/ardustat")
	db_connected = true
	central_info = "central_info"
	
}
catch (err)
{
	console.log(err)
}



//Express Redirects
//Static Redirects
app.use("/flot", express.static(__dirname + '/flot'));


//On Home Page
app.get('/', function(req, res){
	
	indexer = fs.readFileSync('index.html').toString()
    res.send(indexer);
});

app.get('/cv/*', function(req, res){
	
	indexer = fs.readFileSync('cv.html').toString()
    res.send(indexer);
});

//Accept data (all pages, throws to setStuff()
app.post('/senddata', setStuff,function(req, res,next){
	//console.log(req.body)
	res.send(req.body)
	
});

//Presocket Connect, may reuse when flat files/mongodb is implements
app.post('/getdata',getStuff,function(req, res){
	res.send(req.app.settings)
});

//Start listener on this port
//TODO: link to aruino id: e.g. board 16 is port 8016
app.listen(8000);
console.log('Express server started on port %s', app.address().port);

//Program Functions
function setStuff(req,res)
{
	///req.body.stuff

	
}

function getStuff(req,res)
{
	collection = req.body.collection
	q = req.body.query
	if (q == '') q = null
	if (collection == 'central_info')
	{		
		db.collectionNames(function(err,data){res.send(data)})
	}
	else
	{
		console.log(req.body)
		db.collection(collection).find(q).toArray(function(err,data)
		{
			res.send(data)
			
		})
	}


}


