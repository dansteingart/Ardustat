###pithy is

	1. concise and forcefully expressive, or
	2. containing much pith

code should be 1, not 2.  

sometimes you want to share code and see what it does on the same page.  sometimes you want to do this for python with scientific computing.  enter pithy.  

pithy has code on the left, and output on the right.  all changes are saved, and the url is freely shareable.  pithy has been tested against sophomores and juniors in chemical engineering successfully.  

pithy is python for sharing plots and numerical output, among other things.  it's really pretty cool, but you have to play with it for a bit to see why.  go to the [wiki](https://github.com/dansteingart/pithy/wiki) to get a sense of what it can do.

###you might say

pithy is just like [ipython notebook](http://ipython.org/notebook.html), or the [adafruit learning system IDE](http://learn.adafruit.com/), or `<insert your favorite web ide here>`, and i'd be flattered.  but it's got subtle differences, and the best way to understand them is this:

the incomparable [aaron swartz](http://en.wikipedia.org/wiki/Aaron_Swartz) made a couple of web page/wiki/blog/information engines that are awesome and (imho) radically underappreciated.  they are [jottit](https://www.jottit.com/) and [infogami](https://github.com/infogami/infogami).  The beauty of these programs is the expansiveness of what they can do coupled with the minimal overhead of what you need to get something done.  

here's why they're great: you go to a url.  if the url exists, you can read what's there.  you might be able to add to it.  if the url doesn't exist, then within 5 seconds you can make it exist.  minimal (if any) logging in, and close to zero friction between you and new content.  no laborious wizards nor setup queues.  no "file menu".  no "really?".  just writing.  if you needed to go back, you could.  

i learned python because aaron spoke highly of it, and pithy is inspired by aaron's approach to adding content to the web, but rather that verbally expressive content this is intended for quantitative analyses.  

why is this useful?  imagine you write an analysis of a dynamic dataset in r, or matlab, or whatever.  now imagine if that analysis could be viewed, edited non-destructively, rolled back and/or forked instantaneously by anyone without a login or cumbersome sign-in steps.  now imagine that this analysis is also a standalone web page that can be automatically refreshed.

this is pithy.  it does that.

###big warning
pithy runs arbitrary python on your machine and sends the output back to the browser in a fairly clear manner.  this is convenient, this is also potentially SUPER DANGEROUS.  thus far there is an optional attempt at code scrubbing to stop people from writing local files, reading local files and `rm -rf`-ing your stuff, but it is most definitely not sandboxed nor bullet proof.  it is currently _not enabled_.  thus, pithy should be run on a server:

1. that is routinely backed up (like all good servers should be)
2. has nothing that you don't want the world to see that is not encrypted (ditto)
3. that can suffer some downtime if someone does something stupid

the [raspberry pi](http://www.raspberrypi.org/) is an awesome server for this very thing

because pithy just runs from a directory, standard http authentication can be applied to make stuff safe.

###pithy requires 

1. a fairly up to date (not 3.0 though) python installation
2. [node.js](http://nodejs.org/)  (0.8.16 or better)
3. science stuff! I like [EPD](http://www.enthought.com/products/epd_free.php), but scipy, numpy and matplotlib should be sufficient 

###installation/usage 

1. clone repository to where you want stuff
2. cd to that directory
3. run "node index.js 8001" where 8001 is the port number (change to whatever you want)
4. navigate to http://localhost:8001  (or wherever you put stuff).  you should see a page, and the URL should have a random string of characters appened.  try some python.
5. the default user is "user" and pass is "pass" (no quotes, change this in the index.js file right now, line 
5. now add whatever name you want to the URL (numbers,letters and (-,_) only.  run some code here.  share the url if you're running on an accessisible server.  repeat.  now you're pithy.


###example

pithy tries to plot things nicely, and in order.  best to learn by example here:

paste this into your pithy page to generate a graph


    from pithy import *
	
    a = linspace(0,1,100)
    b = sqrt(a)
    c = a**2

    plot(a,b,'k')
    plot(a,c,'k')
    showme()
    clf()

    plot(a,b,'k')
    plot(a,c,'k')
    xlabel("x")
    ylabel("y")
    title("Now With Labels")
    showme() 

everything here is pure [pylab](http://www.scipy.org/PyLab) except for showme(), which does some behind the scenes magic to generate a plot and save the figure.  

###acknowledgements

Pithy was made possible in part with support from NSF Grant CMMI 1031208.

Pithy was made better with feedback from many students at CCNY and Princeton.  Thanks.

