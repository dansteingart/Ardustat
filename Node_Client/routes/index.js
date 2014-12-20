var express = require('express');
app_page = require('../app.js');
var router = express.Router();
var fs = require('fs');
var functions = require('../functions.js');
reader = functions.reader;
writer = functions.writer,
starter = functions.starter,
stopper = functions.stopper,
name_setter = functions.name_setter,
killer = functions. killer,
reviver = functions.reviver,

// urls for forwarder - serialport interactions. 
router.get('/write/*',function(req,res) {
  writer(req,res);
});
router.get('/read/',function(req,res) {
  reader(req,res);
});
router.get('/startCSV/*',function(req,res) {
  starter(req,res);
});
router.get('/stopCSV/',function(req,res) {
  stopper(req,res);
});
router.get('/kill/',function(req,res) {
  killer(req,res);
});
router.get('/unkill/',function(req,res) {
  reviver(req,res);
});
router.get('/setName/*',function(req,res) {
  name_setter(req,res);
});


/* GET home page. */
router.get('/', function(req, res) {
  res.render('index', { title: 'Express' });
});

//this is hacky and there has to be a better way to do it but it works. so for now, it stays.
router.get('/daniel', function(req, res){
	indexer = fs.readFileSync('views/daniel.html').toString()
  res.send(indexer);
});

router.get('/debug', function(req, res){
  indexer = fs.readFileSync('views/debug.html').toString()
  res.send(indexer);
});

router.post('/senddata', functions.setstuff, function(req, res, next) {
  console.log("this is the router, why doesn't this print anything?: " + req.body);
  res.send("Working on it...");
});

router.get('/cv', function(req, res) {
  indexer = fs.readFileSync('views/cv.html').toString()
  res.send(indexer);
});

router.get('/cycler', function(req, res) {
  indexer = fs.readFileSync('views/cycler.html').toString()
  res.send(indexer);
});

module.exports = router;
