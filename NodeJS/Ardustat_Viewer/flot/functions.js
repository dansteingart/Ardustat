	
	
	
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
	
	function grabData(collect,quer)
	{
		$.ajax({
			type: 'POST',
		  	dataType: "json",
		  	async: true,
		  	url: '/getdata',
			data: {collection:collect,query:quer},
		  	success: function(stuff){
							
				if ($("#central_info").length > 0 & collect == 'central_info') listCollections(stuff)
				else if ($("#flot_cv").length > 0 & collect.search("_cv")>-1) plot_cv(stuff)
				else (console.log(stuff))
				
			}
		});
		
	}

	function listCollections(stuff)
	{
		out_text = "<table>"
		for (j = 0; j < stuff.length;j++)
		{
			out_text+="<tr>"
			for (var key in stuff[j])
			{
				if (stuff[j].hasOwnProperty(key) ) 
				{   
					doob = stuff[j][key].replace("ardustat.","")
					link = ""
					if (stuff[j][key].search("_cv") > -1) link ="<a href='/cv/"+doob+"'>link</a>"	
					out_text+="<td>"+doob+" "+link+"</td>"
				}	
			}
			out_text+="</tr>"
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
	
	