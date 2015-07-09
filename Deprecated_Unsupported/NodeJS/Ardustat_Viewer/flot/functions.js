	
	
	
	//Globals
	logger = "stopped";
	var options = {
	    yaxis: { },
	    xaxis: { mode: "time" },
		points: {
			show: false ,
			radius: .5},
		lines: { show: true},
		selection: { mode: "x" }
		
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
	
	
	function frontPage(dict)
	{
		out = JSON.stringify(dict)
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/getdata',
			data: {'data':out},
		  	success: function(stuff){
			

			if ($("#central_info").length > 0 & collect == 'central_info') listCollections(stuff)


			}
		});

	}
	
	function plotlinker(filename)
	{
		return '<a href="/plotter/'+filename.replace("%","%25")+'">'+filename+'</a>'
	}

	function listCollections(stuff)
	{
		stuff = stuff['data']
		out_text = "<table>"
		for (j = 0; j < stuff.length;j++)
		{
			out_text+="<tr><td>"+plotlinker(stuff[j]['filename'])+"</td><td>"+new Date(stuff[j]['time']).toLocaleString()+"</td></tr>"
			
		}
		out_text += "</table>"
		$("#central_info").html(out_text)
		
	}
	
	function plot_cv(stuff)
	{
		//console.log(stuff)
		cv_arr = flotformat(stuff,'V','I')
		$.plot($("#flot_cv"), [cv_arr],options_cv);
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
					//dest.push("null")
				}
			}
			dest.push([row[xlab], row[ylab]]);
    	}
    	return dest;
	}
	
	foo = []
	function plot_all(data)
	{
		foo = data;
		if ($("#flot_potential").length >0)
		{
			console.log($("#flot_potential").length )
			flotfoo = []   
			flotfoo.push({'data':flotformat(foo,'time','working_potential'),'label':'working_potential','color':'red'});
			$.plot($("#flot_potential"), flotfoo,options);
		}
		if ($("#flot_current").length > 0)
		{
			flotfoo = []   
			flotfoo.push({'data':flotformat(foo,'time','current'),'label':'current','color':'red'});
			$.plot($("#flot_current"), flotfoo,options);
		}
	}
	
	function plot_all_range(event,ranges)
	{
		options['xaxis']['min'] = ranges.xaxis.from;
		options['xaxis']['max'] = ranges.xaxis.to;
		plot_all(foo)
	}
	
	$(window).resize(function(){plot_all(foo)})
	