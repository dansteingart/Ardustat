----------------------How to run Imprint Energy's Battery Tester------------------

1. Make sure that the arduino board is hooked up via usb to the laptop.
2. Make sure that the aligator clips are hooked up to some battery with the positive and negative clips hooked up correctly.
3. Run the connect.bat file (double-click). You should see a command window pop up saying "waiting for connection on 7777"
If you do not see this, remove the USB cable and try again.
4. Keep this window open, do not close it. Minimize it.
4. Run the batterytester.bat file. This will bring up the program.


-----------------------Galvanostat/Potentiostat tests------------------------------

1. Select the appropriate tab for whichever test you want to run. Fill in the necessary fields with the parameters you wish
to use.
2. Click "Run!". After a few seconds, you should see plots starting to form in real time on the graph. If nothing happens,
try to close the program and re-try running it.
3. You can adjust the x min and x max to focus on certain parts of the voltage and current graphs. 
4. If you want to save your test run, pause the graph, and select "save graph" from the file menu.
5. Select the location you want to save to, and name your test, e.g. "GalvoTest". Make sure to add no extensions!
6. You will see several files generated in the directory you selected. The ".txt" file is a log of all the voltages and currents.
The ".png" is a screenshot of the graph at the time you saved.


-------------------------Loading saved plots---------------------------------------
1. Sometimes you will need to load saved plots using the batterytest software. You can do this by selecting the "load result"
tab from the program.
2. Select the "load" button.
3. Locate the file you saved previously without any extensions, e.g. "GalvoTest".
4. You should see the graph loaded again. You can pan and zoom the graph as you wish. 
