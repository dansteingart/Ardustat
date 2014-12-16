var sequenty = require('../lib/sequenty');

function f1(cb)
{
  console.log("I'm f1");
  cb();
}

function f2(cb)
{
  console.log("I'm f2");
  cb();
}

sequenty.run([f1, f2]);
