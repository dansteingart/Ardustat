sequenty<br>
========<br>
<br>
An extremely simple synchronous sequential processing module for node<br>
<br>
usage: <br>
<br>
- example 1<br>
<br>
var sequenty = require('sequenty'); <br>
<br>
function f1(cb) // cb: callback by sequenty<br>
{<br> 
   &#160;&#160;console.log("I'm f1");<br>
  &#160;&#160;cb(); // please call this after finshed<br>
}<br>
<br>
function f2(cb)<br>
{<br>
&#160;&#160;console.log("I'm f2");<br>
&#160;&#160;cb();<br>
}<br>
<br>
sequenty.run([f1, f2]);<br>
<br>
- result<br>
<br>
I'm f1<br>
I'm f2<br>
<br>
- example 2<br>
<br>
var f = [];<br>
var queries = [ "select .. blah blah", "update blah blah"];<br>
<br>
for (var i = 0; i < 2; i++)<br>
{<br>
&#160;&#160;f[i] = function(cb, funcIndex) // sequenty gives you cb and funcIndex<br>
&#160;&#160;{<br>
&#160;&#160;&#160;&#160;db.query(queries[funcIndex]);<br>
&#160;&#160;&#160;&#160;cb(); // must be called<br>
&#160;&#160;}<br>
}<br>
<br>
sequenty.run(f);<br>
<br>
