var taxman = require('./taxman')

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



// Create another taxman to that computes a value asynchronously
var asynchronousComputation = taxman(function(callback) {
    console.log("Doing lots of hard work, for real this time...")
    setTimeout(function() {
        var x = 3 * 5
        callback(null, x)
    }, 1000)
})

// Get the computation value (this first call will start the computation)
asynchronousComputation(function(error, value) {
    if (error) {
        console.error("2a: computation failed")
    } else {
        console.log("2a: success! result = ", value)
    }
})

// Get the computation value (this call will wait until the value is computed)
asynchronousComputation(function(error, value) {
    if (error) {
        console.error("2b: computation failed")
    } else {
        console.log("2b: success! result = ", value)
    }
})



// Create another taxman to that computes a value asynchronously
var erroneousComputation = taxman(function(callback) {
    console.log("Doing lots of hard work, for real this time, not sure I can make it...")
    callback(new Error("I fail"))
})

// Get the computation value (this first call will start the computation, synchronously, in this case)
erroneousComputation(function(error, value) {
    if (error) {
        console.error("3a: computation failed")
    } else {
        console.log("3a: success! result = ", value)
    }
})

// Get the computation value (this will re-execute the computation, since there was an error the previous time)
erroneousComputation(function(error, value) {
    if (error) {
        console.error("3b: computation failed")
    } else {
        console.log("3b: success! result = ", value)
    }
})