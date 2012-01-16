divvers = {}

divvers['commanders'] = 'Setting Commands <br> \
<select id="mode_choices"> \
  <option>potentiostat</option> \
  <option>galvanostat</option> \
  <option>moveground</option> \
\
</select><input type="textbox" id="input"> </input> <span id="status"> </span><br> \
<button id="send">send</button><button id="blink">blink</button><button id="ocv">ocv</button><br><br> \
Log Functions<br> \
<input type="textbox" id="logfile"> </input></span><br> \
<button id="logger">Start Log</button> <span id="log_file_name"> </span>'



for (key in divvers)
{
	divved = "#"+key;
	console.log(divved)
	if ($(divved).length == 1) $(divved).html(divvers[key])
}