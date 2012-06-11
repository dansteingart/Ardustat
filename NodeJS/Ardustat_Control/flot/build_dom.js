divvers = {}

divvers['commanders'] = 'Setting Commands <br> \
<select id="mode_choices"> \
  <option>potentiostat</option> \
  <option>galvanostat</option> \
  <option>moveground</option> \
\
</select><input type="textbox" id="input"> </input> <span id="status"> </span><br> \
<button id="send">send</button><button id="blink">blink</button><button id="ocv">ocv</button><br><br>'


divvers['loggers'] = 'Log Functions<br> \
<div id="logentrybox">Log Name<input type="textbox" id="logfile"> </input><br> \
Log Every <input type="textbox" id="everyxlog" value="1"> </input> events (roughly 100 ms per event)</div> \
<button id="logger">Start Log</button> <span id="log_file_name"> </span>'

divvers['cvcommanders'] = 'Setting Commands <br>\
V max<input type="textbox" id="v_max" value="1"> </input><br>\
V min<input type="textbox" id="v_min" value="-1"> </input><br>\
V start<input type="textbox" id="v_start" value ="0"> </input><br>\
CV rate<input type="textbox" id="rate" value="1"> </input> (mV/s)<br>\
Cycle Count<input type="textbox" id="cycles" value="1"> </input> <br>\
<button id="startcv">CV Start</button></span><br><br>'

divvers['finding_error']='Finding Error<br>\
Measured Current<input type="textbox" id="input_current"> </input> \
<button id="find_error">Find!</button><br>'

divvers['cyclingcommanders'] = 'Setting Commands <br>\
<textarea id="cyclingtext" class="areatext"></textarea><br>\
<select id="cyclingpresets"> </select> <input id="cyclingname"></input><button id="cyclingsave">Save Cycling Parameters</button>\
<button id="startcycling">Cycling Start</button></span><br><br>'


for (key in divvers)
{
	divved = "#"+key;
	if ($(divved).length == 1) 
	{
		console.log(divved)
	$(divved).html(divvers[key])	
	}
}