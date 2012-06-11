Serial
====

Serial is a Node.JS module to serially/sequentially run asynchronous functions.


Usage
====
    var SerialRunner = require("serial").SerialRunner;
    var runner = new SerialRunner();
    
    runner.add(function1, param1).add(function2, param2);
    runner.add(function3, param3);
    
    runner.run(function() {
        console.log("done");
    });


    function function1(param, callback) {
        // do smthg
        callback();
    }

License
=====
MIT
