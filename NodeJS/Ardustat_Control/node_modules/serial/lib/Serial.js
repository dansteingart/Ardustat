/** Very simple chaining mecanism to serially execute asynchronous functions
 *
 */

function SerialRunner() {

    this.last;
    this.first;

    /** first arg if the function to call.
     * Other args are params.
     */
    this.add = function() {

        var func = arguments[0];

        var args = [];
        for(var i=1; i < arguments.length ; i++) {
            //console.log("saving arg "+i+": "+arguments[i]);
            args.push(arguments[i]);
        }


        if(!this.first) {
            //logger.info("First "+params);
            this.first = new ChainItem(func, args);
            this.last = this.first;
        } else {
            //logger.info("Chaining "+params);
            var chainItem = new ChainItem(func, args);
            this.last.next = chainItem;
            this.last = chainItem;
        }

        return this;
    }

    this.run = function(done) {
        if(done) {
            this.add(done);
        }

        if(this.first) {
            //console.log("** running first");
            this.first.run();
        } else {
            throw new Error("You must call add() before calling run()");
        }
    }


    function ChainItem(func, args) {
        this.args = args;
        this.func = func;
        var self = this;

        this.run = function() {
            //console.log("running func");
            if(self.args) {
                //console.log("has args");
                function next() {
                    //console.log("run func done. next()");
                    if(self.next) {
                        //logger.info("next of "+self.args);
                        self.next.run();
                    } else {
                        console.log("ERR: no next");
                        //logger.info("no next for "+self.args);
                    }
                }
                this.args.push(next);
                func.apply(this, self.args);
            } else {
                //console.log("no args");
                func(next);
            }
        }
    }
}

exports.SerialRunner = SerialRunner;
