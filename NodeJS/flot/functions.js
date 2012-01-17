	
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
		logcheck(fata)
		for (var key in fata)
		{
			if (fata.hasOwnProperty(key)) 
			{
				out_text+=key+": "+fata[key]+"<br>"
			}
		}
	
		$("#update_values").html(out_text);
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
			
			$("#logfile").hide()
		
		}
		else if (logger == "stopped")
		{
			$("#logger").html("Start Log")
			$("#log_file_name").text("")
			$("#logfile").show()
			
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
			
			console.log(logger)
			$.ajax({
				type: 'POST',
			  	dataType: "json",
			  	async: true,
			  	url: '/senddata',
			  	data: {logger:logger,datafilename:$("#logfile").val()},
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
	
	function grabData()
	{
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/getdata',
		  	success: function(stuff){
				//console.log(stuff);
				big_arr.push(stuff.ardudata)
				while (big_arr > 100) big_arr.shift(0)
				plot_all(big_arr)
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
		flotfoo = []   
		flotfoo.push({'data':flotformat(foo,'time','working_potential'),'label':'working_potential','color':'red'});
		$.plot($("#flot_potential"), flotfoo,options);
		
		flotfoo = []   
		flotfoo.push({'data':flotformat(foo,'time','current'),'label':'current','color':'red'});
		$.plot($("#flot_current"), flotfoo,options);

	}
