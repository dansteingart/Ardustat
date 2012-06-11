var SerialRunner = require("../index.js").SerialRunner;

var should = require("should");

describe("When running tasks sequentially", function() {
 it("", function(done) {
  var r = new SerialRunner();
  var list = [];
  var numCallback = 10;
  var func = function(i, next) {
   setTimeout(function() {
    list.push(i);
    next();
   }, 20-i);
  }

  for(var i = 0 ; i < numCallback ; i++) {
    r.add(func, i);
  }

  r.run(function() {
   list.length.should.equal(numCallback);
   for(var i=0 ; i < numCallback ; i++) {
    list[i].should.equal(i);
   }
   done();
  });

 });
});
