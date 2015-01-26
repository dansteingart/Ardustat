//app.js
var app = express(); //var app = express.createServer();
var http = require('http').createServer(app).listen(3001);
var io = require('socket.io')(http);

io.on('connection', function(socket){
  console.log('a user connected');
});


This works well.

If I change it to:

//app.js 
var app = express(); //var app = express.createServer();
var http = require('http').createServer(app).listen(3001);
var io = require('socket.io')(http);

module.exports = {
  app:app,
  io:io
};

//functions.js

app_page = require('./app.js')
app = app_page.app;
io = app_page.io;

io.on('connection', function(socket){
  console.log('a user connected');
});


//I get an error - Cannot call method 'on' of undefined
