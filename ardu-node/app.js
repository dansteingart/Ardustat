//default stuff

//TODO: change dependencies in the package.json 
//TODO: change the way am getting bower__components. (right now its manual)
//TODO: change firmware so that it prints out last command that wasn't 's0000'

//requirements from npm
var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var mkdirp = require('mkdirp');
var sleep = require('sleep').sleep;
var url = require('url');
var fs = require('fs');
var sys = require('sys');

//ones I probably don't need
var squenty = require('sequenty');
var urllib = require('urllib');

//requirements from files
var routes = require('./routes/index');
var users = require('./routes/users');
var json2csv = require('json2csv');
var functions = require('./functions.js');

//actual setup stuff
var app = express(); //var app = express.createServer();
var http = require('http').createServer(app).listen(3001);
var io = require('socket.io')(http);

//this is stuff for the socket communication I think
var datastream = ""
tcpport = process.argv[3]
if (process.argc == 4) sample_rate = 100
else sample_rate = process.argv[4]

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
//app.use(favicon(__dirname + '/public/favicon.ico'));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', routes);
app.use('/users', users);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

// error handlers
// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
    app.use(function(err, req, res, next) {
        res.status(err.status || 500);
        res.render('error', {
            message: err.message,
            error: err
        });
    });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
        message: err.message,
        error: {}
    });
});

module.exports = ({
  app:app,
});
