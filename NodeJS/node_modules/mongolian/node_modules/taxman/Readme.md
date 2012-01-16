node-taxman
===========
Taxman caches values for you.

Introduction
------------
This module was inspired by the need for an easy way to asynchronously compute a value once, but use it in multiple
places.

Examples
--------
    var taxman = require('taxman')
    
    // Create a taxman to compute the value
    var computation = taxman(function(callback) {
        console.log("Doing lots of hard work...")
        var x = 3 * 5
        callback(null, x)
    })

    // Get the computation value (this first call will start the computation, synchronously, in this case)
    computation(function(error, value) {
        if (error) {
            console.error("1a: computation failed")
        } else {
            console.log("1a: success! result = ", value)
        }
    })

    // Get the computation value again (retrieves cached value)
    computation(function(error, value) {
        if (error) {
            console.error("1b: computation failed")
        } else {
            console.log("1b: success! result = ", value)
        }
    })

    // Reset the cache
    computation.reset()

    // Get the computation value (this will re-compute the value)
    computation(function(error, value) {
        if (error) {
            console.error("1c: computation failed")
        } else {
            console.log("1c: success! result = ", value)
        }
    })

Outputs:

    Doing lots of hard work...
    1a: success! result =  15
    1b: success! result =  15
    Doing lots of hard work...
    1c: success! result =  15


See [test.js][1] for more examples.

License
-------
Taxman is open source software under the [zlib license][2].

[1]: https://github.com/marcello3d/node-taxman/blob/master/test.js
[2]: https://github.com/marcello3d/node-taxman/blob/master/LICENSE