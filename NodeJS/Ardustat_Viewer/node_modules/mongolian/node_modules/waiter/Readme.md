node-waiter
===========
A simple way to wait for multiple asynchronous calls to return in Node.js.

Introduction
------------
Just a little utility class I wrote for dealing with parallel code. It lets you spin off a bunch of asynchronous
operations and wait for them to finish.

Waiter is similar to other projects like [Step][1], [async][2], and [Seq][3], but with a focus on parallel operations
that return values.

Examples
--------

Read three files asynchronously.

    var waiter = new Waiter
    var aFile = waiter(),
        bFile = waiter(),
        cFile = waiter()
    fs.readFile('a.txt', aFile)
    fs.readFile('b.txt', bFile)
    fs.readFile('c.txt', cFile)
    // wait for them to finish
    waiter.waitForAll(function(error) {
        if (error) {
            // inspect individual errors in aFile.error, bFile.error, and cFile.error
            throw "oh no!"
        }
        // do something with aFile.value, bFile.value, and cFile.value
    })

You can call waiter() as many times as you want --- but call them all before calling waitForAll!

    var files = [ ... ]
    var waiter = new Waiter

    var filesContent = files.map(function(file) {
        // Alternative syntax, pass a function into waiter(), and get the callback as an argument
        return waiter(function(done) {
            fs.readFile(file,done)
        })
    })
    waiter.waitForAll(function(error) {
        // do something with error or fileContents[x].value
    }, 2000) // optional timeout parameter


Don't care about the values? You don't have to store the result of waiter():

    var waiter = new Waiter
    fs.writeFile('a.txt', 'hello a!', waiter())
    fs.writeFile('b.txt', 'hello b!', waiter())
    fs.writeFile('c.txt', 'hello c!', waiter())
    waiter.waitForAll(function(error) {
        if (error) {
            console.error("Oh no!", error)
        } else {
            // all files have been written successfully!
        }
    })

Alternative syntax if you don't care about the values:

    new Waiter(
        function(done) {
            fs.writeFile('a.txt', 'hello a!', done)
        },
        function(done) {
            fs.writeFile('b.txt', 'hello b!', done)
        }
    ).waitForAll(function(error) {
        // same old...
    })

License
-------
Waiter is open source software under the [zlib license][1].

[1]: https://github.com/creationix/step
[2]: https://github.com/caolan/async
[3]: https://github.com/substack/node-seq
[4]: https://github.com/marcello3d/node-mongolian/blob/master/LICENSE