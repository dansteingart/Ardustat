// author: Andy Shin, andyshin.as@gmail.com, 2013.11.25

exports.run = function(funcs)
{
	var i = 0;	
	var recursive = function()
	{
		funcs[i](function() 
		{
			i++;
			
			if (i < funcs.length)
				recursive();
		}, i);
	};
	
	recursive();	
}
