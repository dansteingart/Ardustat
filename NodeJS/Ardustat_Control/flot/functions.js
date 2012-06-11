	
	//Globals
	logger = "stopped";
	var options = {
	    yaxis: { },
	    xaxis: { mode: "time" },
		points: {
			show: false ,
			radius: .5},
		lines: { show: true}
	};
	
	var options_cv = {
	    yaxis: { },
	    xaxis: { },
		points: {
			show: false ,
			radius: .5},
		lines: { show: true}
	};
	
	
	big_arr = []
	
 
	
	cv_arr = []
	cv_comm = ""
	hold_array = []
	hold_array['x'] = []
	hold_array['y'] = []
	last_comm = ""

	var socket = io.connect('/');

	
	//Socket Stuff
 	socket.on('new_data', function (data) {
		
		out_text = ""
		fata = data.ardudata
		if (fata['cv_settings'] != undefined) cvprocess(fata)
		if (fata['arb_cycling_settings'] != undefined) cyclingprocess(fata)
		
		logcheck(fata)
		cvstatus(fata)
		big_arr.push(data.ardudata)
		
		while (big_arr.length > 100) big_arr.shift(0)
		plot_all(big_arr)
	});

	
	//Functions
	function logcheck(fata)
	{

		logger = fata['logger'].toString()
		if (fata['datafile'] != undefined)
		{
			datafile = fata['datafile'] 
		} 
		else
		{
			datafile = ""
		}
	
		if (logger == "started")
		{
			$("#logger").html("Stop Log")
			$("#log_file_name").text(datafile)
			
			$("#logentrybox").hide()
		
		}
		else if (logger == "stopped")
		{
			$("#logger").html("Start Log")
			$("#log_file_name").text("")
			$("#logentrybox").show()
			
		}
	}
	
	function cvstatus(fata)
	{
		
		if ($("#cvstatus").length > 0 & fata['cv_settings'] != undefined)
		{
			mata = fata['cv_settings']
			for (var key in mata)
			{
				if (mata.hasOwnProperty(key)) 
				{
					out_text+=key+": "+mata[key]+"<br>"
				}
			}
	
			$("#cvstatus").html(out_text);
		}
	}
	
	$("#send").click(function(){
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {command:$("#mode_choices").val(),value:$("#input").val()},
		  	success: function(stuff){
				$("#status").html("all good").fadeIn().fadeOut()
			}
		});
				
	});
	
	$("#find_error").click(function(){
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {command:"find_error",value:$("#input_current").val()},
			success: function(stuff){
				console.log(stuff);
			}
		});
				
	});
	
	$("#blink").click(function(){
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {arducomm:" "},
		  	success: function(stuff){
				console.log(stuff);
			}
		});
		
	});
	
	$("#ocv").click(function(){
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {command:"ocv",value:""},
		  	success: function(stuff){
				console.log(stuff);
			}
		});
		
	});
	
	$("#logger").click(function(){
			if (logger == "stopped") logger = "started"
			else logger = "stopped"
			everyxlog = $("#everyxlog").val()
			console.log(logger);
			$.ajax({
				type: 'POST',
			  	dataType: "json",
			  	async: true,
			  	url: '/senddata',
			  	data: {logger:logger,datafilename:$("#logfile").val(),everyxlog:everyxlog},
			  	success: function(stuff){
					console.log(stuff);
				}
			});

	});
	
	$("#startcv").click(function(){
		cv_arr = []
		values = {}
		values['rate'] = $("#rate").val()
		values['v_max']= $("#v_max").val()
		values['v_min']= $("#v_min").val()
		values['v_start']= $("#v_start").val()
		values['cycles']= $("#cycles").val()
		
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {command:"cv",value:values},
		  	success: function(stuff){
				$("#status").html("all good").fadeIn().fadeOut()
			}
		});
				
	});
	
	$("#startcycling").click(function(){
		cv_arr = []
		values = $("#cyclingtext").val().split("\n")
		
		
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/senddata',
		  	data: {command:"cycling",value:values},
		  	success: function(stuff){
				$("#status").html("all good").fadeIn().fadeOut()
			}
		});
				
	});
	
	
	$("#cyclingsave").click(function(){ 
			values = {name:$("#cyclingname").val(),program:$("#cyclingtext").val()}
		
			$.ajax({
				type: 'POST',
			  	dataType: "json",
			  	async: true,
			  	url: '/senddata',
			  	data: {programs:"cyclingsave",value:values},
			  	success: function(stuff){
					fillprograms(stuff)
					$("#status").html("all good").fadeIn().fadeOut()
					
				}
			});
		
		
		})
	
	cycling_programs = {}
	
	function fillprograms(stuff)
	{
		out = ""
		for (var i = 0; i < stuff.length;i++)
		{
			cycling_programs[stuff[i]['name']] = stuff[i]['program']
			out+="<option>"+stuff[i]['name']+"</option>" 
		}
		$("#cyclingpresets").html(out)
	}
	
	$("#cyclingpresets").change(function()
	{
		$("#cyclingtext").val(cycling_programs[$("#cyclingpresets option:selected").text()])
	})
	
	if 	($("#cyclingpresets").length == 1)
	{
			$.ajax({
				type: 'POST',
			  	dataType: "json",
			  	async: true,
			  	url: '/senddata',
			  	data: {programs:"cyclingpresetsget",value:{}},
			  	success: function(stuff){
					fillprograms(stuff)
					
				}}
			)
	}
	
	function cyclingprocess(data)
	{
		if ($("#cyclingtext").length == 1)
		{
			
			if ($("#cyclingtext").val() == "")
			{
				this_foo = data['arb_cycling_settings']
				console.log(this_foo)
				out = ""
				for  (var o = 0; o < this_foo.length ;o++)
				{
					out += JSON.stringify(this_foo[o])+"\n"
				}
				$("#cyclingtext").val(out)
				
				
			}
			
		}
	}
	
	function cvprocess(data)
		{	foo = data
			last_comm = foo['last_comm']
			if (cv_comm != last_comm & cv_comm != "")
			{
				 cv_comm = last_comm
				 x = 0
				 y = 0
				 for (j = 0; j<hold_array['x'].length;j++ )
				 {
				 	x = x+hold_array['x'][j]
				 	y = y+hold_array['y'][j]
				 }
				 x = x/hold_array['x'].length
				 y = y/hold_array['y'].length
				 hold_array['x'] = []
				 hold_array['y'] = []
				if (cv_arr.length > 0) 
				{
					old_x = cv_arr[cv_arr.length-1][0]
				 	if (Math.abs(x-old_x) > .05) cv_arr.push([null]);
			 	}
				 cv_arr.push([x,y]);
				 
				 //io.sockets.emit('cv_data',{'cv_data':cv_arr} )
				$.plot($("#flot_cv"), [cv_arr],options_cv);
				
				//console.log(cv_arr)

			 }
			 else if (cv_comm == "")
			 {
			    cv_comm = last_comm
				hold_array['x'] = []
				hold_array['y'] = []
				
			 }
			hold_array['x'].push(foo['working_potential'])
			hold_array['y'].push(foo['current'])

	}
	
	function grabData(dict)
	{
		dict = JSON.stringify(dict)
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/getdata',
			data: {'data':dict},
		  	success: function(stuff){
							
				if ($("#central_info").length > 0 & stuff['collect'] == 'central_info') listCollections(stuff)
				else if ($("#plots").length > 0 ) plot_all(stuff['data'])
				else {
				console.log("what the hell do I do with this")
				console.log(stuff)
				}
			}
		});
		
	}
	
	
	function flotformat(source,xlab,ylab) {
		start = source[0][xlab]
		end = source[source.length - 1][xlab]
		diff = Math.abs(start - end)
		avdiff = diff/source.length
    	var i, l,
        	dest = [],
        	row;

    	for(i = 0, l = source.length; i < l; i++) 
		{ 
        	row = source[i];
			if (i > 0)
			{
				if (Math.abs(source[i][xlab] - source[i-1][xlab]) > avdiff*10) 
				{
					dest.push("null")
				}
			}
			dest.push([row[xlab], row[ylab]]);
    	}
    	return dest;
	}
	
	function plot_all(data)
	{
		foo = data;
		if ($("#flot_potential").length >0)
		{
//			console.log($("#flot_potential").length )
			flotfoo = []   
			flotfoo.push({'data':flotformat(foo,'time','working_potential'),'label':'working_potential','color':'red'});
			$.plot($("#flot_potential"), flotfoo,options);
		}
		if ($("#flot_current").length > 0)
		{
			flotfoo = []   
			flotfoo.push({'data':flotformat(foo,'time','Current_pin'),'label':'Current','color':'red'});
			$.plot($("#flot_current"), flotfoo,options);
		}
	}