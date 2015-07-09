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
<input type="textbox" id="logfile"> </input></span><br> \
<button id="logger">Start Log</button> <span id="log_file_name"> </span>'

divvers['cvcommanders'] = 'Setting Commands <br>\
V max<input type="textbox" id="v_max" value="1"> </input><br>\
V min<input type="textbox" id="v_min" value="-1"> </input><br>\
V start<input type="textbox" id="v_start" value ="0"> </input><br>\
CV rate<input type="textbox" id="rate" value="1"> </input> (mV/s)<br>\
Cycle Count<input type="textbox" id="cycles" value="1"> </input> <br>\
<button id="startcv">CV Start</button></span><br><br>'


for (key in divvers)
{
	divved = "#"+key;
	if ($(divved).length == 1) 
	{
		console.log(divved)
	$(divved).html(divvers[key])	
	}
}