#!/usr/local/bin/node

var evalContext = {};

for (p in global) {
    evalContext[p] = global[p];
}

evalContext.cl = console.log;

var Script = process.binding('evals').Script

var stdin = process.openStdin();

stdin.setEncoding('utf8');

var shellWrite = function (data) {
    process.stdout.write(data);
};

var shellRead = function () {
    shellWrite('>>> ');
};

var shellProcess = function (data) {
    data = data.replace('\n', '');
    if (data == 'exit') {
        shellExit();
        process.exit(0);
    }
    
    if (data != '.' && data.substr(-1) == '.') {
        temp.push(data.substr(0, data.length - 1));
        data = '.'        
    }
    
    if (data == '.' || (data == '' && temp.length == 0)){
        if (temp.length > 0) {
            var joined = temp.join('\n');
            temp = [];
            var code = 'try { ' + joined + ' } catch (ex) { console.log(ex.stack); }';
            try {
                Script.runInNewContext(code, evalContext, '<inode>');
            } catch (ex) {
                console.log(ex.stack);
            }
        }
        
        shellRead();
    }
    else {
        temp.push(data);
    }
};

var shellExit = function() {
    console.log('');
    console.log('Bye.');
};

var temp = [];

stdin.on('data', function (data) {
    shellProcess(data);
});

stdin.on('end', function () {
    shellExit();
});

process.on('SIGINT', function () {
    console.log('');
    temp = [];
    shellRead();
});

var spawn = require('child_process').spawn;

var nodeVersionProcess = spawn(process.execPath, ['-v']);

nodeVersionProcess.stdout.on('data', function (version) {
    shellWrite('Node ' + version);
    console.log('Command ends with dot in new line.');
    console.log('Single-line command ends with dot on the end');
    console.log('Shortcuts:');
    console.log('cl = console.log');
    shellRead();
});
