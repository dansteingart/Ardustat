var express = require('express');
var router = express.Router();
var fs = require('fs');
var functions = require('../functions_3_play.js');
reader = functions.reader;
writer = functions.writer,
starter = functions.starter,
stopper = functions.stopper,
name_setter = functions.name_setter,
reviver = functions.reviver,
//console.log(' the app is ' + app_page);

// urls for forwarder - serialport interactions. 
router.get('/write/*',function(req,res) {
  writer(req,res);
});
router.get('/read/*',function(req,res) {
  reader(req,res);
});
router.get('/startCSV/*',function(req,res) {
  starter(req,res);
});
router.get('/stopCSV/*',function(req,res) {
  stopper(req,res);
});
router.get('/setName/*',function(req,res) {
  name_setter(req,res);
});

//Add in the channel to URL
router.get('/killing/*',function(req,res) {
  functions.killer(req,res);
});
router.get('/pauser/*',function(req,res) {
  functions.pauser(req,res);
});
router.get('/reviver/*',function(req,res) {
  functions.reviver(req,res,functions.flag_resume);
});
router.get('/step_skip/*',function(req,res) {
  functions.step_skip(req,res);
});


/* GET home page. */ 
router.get('/', function(req, res){
  indexer = fs.readFileSync('views/index.html').toString()
  res.send(indexer);
});

router.get('/daniel', function(req, res){
	indexer = fs.readFileSync('views/daniel.html').toString()
  res.send(indexer);
});

router.get('/debug', function(req, res){
  indexer = fs.readFileSync('views/debug.html').toString()
  res.send(indexer);
});

router.get('/show_setup/*',function(req,res) {
  functions.show_setup(req,res);
});

router.get('/Analysis', function(req, res){
	indexer = fs.readFileSync('views/Analysis/index.html').toString()
	functions.analysis_display(req,res,indexer)
});

router.post('/show_files', functions.file_display, function(req, res, next) {
  console.log("this is the router")
  functions.file_display
});

router.get('/getstatus', functions.give_status, function(req, res, next) {
  console.log("this is the router")
});

router.get('/blink_button', functions.blink_button, function(req, res, next) {
  console.log("this is the router")
});

router.post('/senddata', functions.setstuff, function(req, res, next) {
  console.log("this is the router")
  //res.send("Working on it...");
});

//Channel 1 routes
router.get('/Channel1', function(req, res){
	indexer = fs.readFileSync('views/Channel1/index.html').toString()
  res.send(indexer);
});

router.get('/Channel1/CV', function(req, res) {
  indexer = fs.readFileSync('views/Channel1/cv.html').toString()
  res.send(indexer);
});

router.get('/Channel1/Cycler', function(req, res) {
  indexer = fs.readFileSync('views/Channel1/cycler.html').toString()
  res.send(indexer);
});

router.get('/Channel1/Calibration', function(req, res) {
  indexer = fs.readFileSync('views/Channel1/calibration.html').toString()
  res.send(indexer);
});

//-------------------------------------------------------------------
router.get('/Channel2', function(req, res){
  indexer = fs.readFileSync('views/Channel2/index.html').toString()
  res.send(indexer);
});

router.get('/Channel2/CV', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/cv.html').toString() 
  functions.replacer_2(req,res,indexer)
});

router.get('/Channel2/Cycler', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/cycler.html').toString() 
  functions.replacer_2(req,res,indexer)
});

router.get('/Channel2/Calibration', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/calibration.html').toString() 
  functions.replacer_2(req,res,indexer)
});

//-------------------------------------------------------------------
router.get('/Channel3', function(req, res){
  indexer = fs.readFileSync('views/Channel3/index.html').toString()
  res.send(indexer);
});

router.get('/Channel3/CV', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/cv.html').toString() 
  functions.replacer_3(req,res,indexer)
});

router.get('/Channel3/Cycler', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/cycler.html').toString() 
  functions.replacer_3(req,res,indexer)
});

router.get('/Channel3/Calibration', function(req, res, next){
  indexer = fs.readFileSync('views/Channel1/calibration.html').toString() 
  functions.replacer_3(req,res,indexer)
});

module.exports = router;
