#!/usr/bin/env python

# (C) 2002-2009 Chris Liechti <cliechti@gmx.net>
# redirect data from a TCP/IP connection to a serial port and vice versa
# requires Python 2.2 'cause socket.sendall is used

# (C) 2010 Ben Kempke <bpkempke@umich.edu>
# modified to dump all serial activity to file, accept multiple connections, and 
# support an optional server uplink


import sys
import os
import time
import threading
import socket
import codecs
import time
import datetime
import serial
import base64

# create a class which handles one connection's traffic
class ClientConnectionThread( threading.Thread):
    def __init__(self, channel, serial_thread):
        self.channel = channel
        self.alive = True
        self.serial_thread = serial_thread
        self.data_output_queue = []
        self.data_output_queue_lock = threading.Condition()
        threading.Thread.__init__(self)
        
        self.thread_write = threading.Thread(target=self.writer)
        self.thread_write.setDaemon(True)
        self.thread_write.setName('client->writer')
        self.thread_write.start()
        
    def run(self):
        while self.alive:
            try:
                data = self.channel.recv(1024)
                if not data:
                    break
                self.serial_thread.serialwrite(data)
            except socket.error:
                self.alive = False
                
        self.alive = False
            
        #remove this thread from the serial thread to keep things clean
        if not self.keep_alive():
            self.serial_thread.removeconnection(self)
        
    def writer(self):
        while self.alive:
            self.data_output_queue_lock.acquire()
            while len(self.data_output_queue) == 0:
                self.data_output_queue_lock.wait()
            transmit_items = self.data_output_queue
            self.data_output_queue = []
            self.data_output_queue_lock.release()
            
            try:
                for data in transmit_items:
                    self.channel.sendall(data)
            except socket.error:
                self.alive = False
                
        sys.stdout.write("stop...")
        
    def keep_alive(self):
        return False

    def send_data(self, data):
        self.data_output_queue_lock.acquire()
        self.data_output_queue.append(data)
        self.data_output_queue_lock.notify()
        self.data_output_queue_lock.release()
        
class AutoForward( threading.Thread):
    def __init__(self, file_name, start_time, num_retries, wait_time, serial_thread):
        self.file_name = file_name
        self.start_time = start_time
        self.num_retries = num_retries
        self.wait_time = wait_time
        self.serial_thread = serial_thread
        self.fp = open(self.file_name, 'rb')
        self.data = self.fp.read()
        self.fp.close()
        threading.Thread.__init__(self)

    def run(self):
        # wait for the beginning of the transmission time
        while time.time() < self.start_time:
            time.sleep(.5)
        
        # Now that we've reached the correct time, start transmitting the file data out to the serial port
        for i in range(self.num_retries):
            self.serial_thread.serialwrite(self.data)
            print "Transmitting contents of " + self.file_name + "(#" + str(i+1) + ")"
            for j in range(self.wait_time):
                time.sleep(1)

  
class UplinkConnectionThread(ClientConnectionThread):
    def __init__(self, uplink_server_name, uplink_server_port, serial_thread):
        self.uplink_server_name = uplink_server_name
        self.uplink_server_port = uplink_server_port
        self.open_connection()
        ClientConnectionThread.__init__(self, self.channel, serial_thread)
        
    def run(self):
        while True:
            if not self.alive:
                sys.stdout.write("Retrying uplink connection to %s:%s\n" % (self.uplink_server_name, self.uplink_server_port))
                self.open_connection()
                self.alive = True
            ClientConnectionThread.run(self)
            time.sleep(5)
            
    def writer(self):
        while True:
            while not self.alive:
                time.sleep(5)
            ClientConnectionThread.writer(self)
        
    def open_connection(self):
        try:
            self.channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.channel.connect((self.uplink_server_name, self.uplink_server_port))
        except socket.error:
            sys.stdout.write("Trouble connecting to uplink server...\n")

    def keep_alive(self):
        return True


class Redirector:
    def __init__(self, serial_instance, srv, stationname, radioid, ser_newline=None, net_newline=None, spy=False):
        self.serial = serial_instance
        self.ser_newline = ser_newline
        self.net_newline = net_newline
        self.spy = spy
        self.srv = srv
        self.stationname = stationname
        self.lastsavedtime = 0
        self._write_lock = threading.Lock()
        self._historic_data_lock = threading.Lock()
        self.historic_data = str()
        self.radio_id = radioid
        self.client_queue = []

    def shortcut(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial->socket')
        self.thread_read.start()
		
		#Set up a logging thread which checks the 
        self.thread_log = threading.Thread(target=self.logger)
        self.thread_log.setDaemon(True)
        self.thread_log.setName('serial->logger')
        self.thread_log.start()
        
#        self.logger()
        
#        self.writer()

    def addconnection(self, client):
        self.client_queue.append(client)
        
    def removeconnection(self, client):
        self.client_queue.remove(client)
		
    def logger(self):
        while self.alive:
            time.sleep(1)
            
            # Need to make sure two threads aren't modifying historic_data at the same time
            self._historic_data_lock.acquire()
            if self.historic_data:
                #Log the incoming data, as a hex string
                today = datetime.date.today()
                todaystring = today.strftime("%m%d%y")
                fid = open(self.stationname + "_serial_log_" + todaystring + ".dat", "a")
                utct = datetime.datetime.utcnow()
                t = time.mktime(utct.timetuple())      # append the timestamp of this incoming data
                self.lastsavedtime = t
                fid.write("\n\n" + utct.strftime("%m/%d/%Y %I:%M:%S (") + str(self.radio_id) + ", " + str(len(self.historic_data)) + ")\n")
                fid.write(base64.b64encode(self.historic_data))
                #fid.write(''.join( [ "%02X" % ord( x ) for x in data ] ).strip())
                fid.close()
                self.historic_data = str();
            self._historic_data_lock.release()

    def reader(self):
        """loop forever and copy serial->socket"""
        #sys.stdout.write("got some data....")
        while self.alive:
            data = self.serial.read(1)              # read one, blocking
            n = self.serial.inWaiting()             # look if there is more
            if n:
                data = data + self.serial.read(n)   # and get as much as possible
            if data:
                
                # append the currently-read data onto the historic data array
                self._historic_data_lock.acquire()
                self.historic_data += data
                self._historic_data_lock.release()
                
                # the spy shows what's on the serial port, so log it before converting newlines
                if self.spy:
                    sys.stdout.write(codecs.escape_encode(data)[0])
                    sys.stdout.flush()
                if self.ser_newline and self.net_newline:
                    # do the newline conversion
                    # XXX fails for CR+LF in input when it is cut in half at the begin or end of the string
                    data = net_newline.join(data.split(ser_newline))
                
                for client in self.client_queue:
                    client.send_data(data)
        self.alive = False
        
    def serialwrite(self, data):
        self.serial.write(data)

    def stop(self):
        sys.stdout.write("stopping")
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()


if __name__ == '__main__':
    import optparse

    def autofiles_callback(option, opt_str, value, parser):
        value = getattr(parser.values, option.dest)
        if value is None:
            value = []

        for arg in parser.rargs:
            if arg[:1] == "-":
                break
            value.append(arg)

        del parser.rargs[:len(value)]
        setattr(parser.values, option.dest, value)


    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "Simple Serial to Network (TCP/IP) redirector.",
        epilog = """\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")

    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages",
        default = False
    )

    parser.add_option("--spy",
        dest = "spy",
        action = "store_true",
        help = "peek at the communication and print all data to the console",
        default = False
    )

    group = optparse.OptionGroup(parser,
        "Serial Port",
        "Serial port settings"
    )
    parser.add_option_group(group)

    group.add_option("-p", "--port",
        dest = "port",
        help = "port, a number (default 0) or a device name",
        default = None
    )

    group.add_option("-b", "--baud",
        dest = "baudrate",
        action = "store",
        type = 'int',
        help = "set baud rate, default: %default",
        default = 9600
    )

    group.add_option("", "--parity",
        dest = "parity",
        action = "store",
        help = "set parity, one of [N, E, O], default=%default",
        default = 'N'
    )

    group.add_option("--rtscts",
        dest = "rtscts",
        action = "store_true",
        help = "enable RTS/CTS flow control (default off)",
        default = False
    )
    
    group.add_option("--clientmode",
        dest = "clientmode",
        action = "store_true",
        help = "enable reverse-client socket mode",
        default = False
    )
    
    group.add_option("-u", "--uplinkaddr",
        dest = "uplink_address",
        action = "store",
        help = "set uplink server address",
        default = "yourserverhere.com"
    )
    
    group.add_option("-U", "--uplinkport",
        dest = "uplink_port",
        action = "store",
        type = 'int',
        help = "set uplink server port",
        default = 13500
    )

    group.add_option("--xonxoff",
        dest = "xonxoff",
        action = "store_true",
        help = "enable software flow control (default off)",
        default = False
    )

    group.add_option("--rts",
        dest = "rts_state",
        action = "store",
        type = 'int',
        help = "set initial RTS line state (possible values: 0, 1)",
        default = None
    )

    group.add_option("--dtr",
        dest = "dtr_state",
        action = "store",
        type = 'int',
        help = "set initial DTR line state (possible values: 0, 1)",
        default = None
    )

    group = optparse.OptionGroup(parser,
        "Network settings",
        "Network configuration."
    )
    parser.add_option_group(group)

    group.add_option("-P", "--localport",
        dest = "local_port",
        action = "store",
        type = 'int',
        help = "local TCP port",
        default = 7777
    )

    group = optparse.OptionGroup(parser,
        "Newline Settings",
        "Convert newlines between network and serial port. Conversion is normally disabled and can be enabled by --convert."
    )
    parser.add_option_group(group)

    group.add_option("-c", "--convert",
        dest = "convert",
        action = "store_true",
        help = "enable newline conversion (default off)",
        default = False
    )
	
    group.add_option("-n", "--name",
        dest = "stationname",
        action = "store",
        help = "set station name",
        default = "default"
    )
    
    group.add_option("-i", "--id",
        dest = "radioid",
        action = "store",
        help = "set radio id",
        default = 0
    )

    group.add_option("--net-nl",
        dest = "net_newline",
        action = "store",
        help = "type of newlines that are expected on the network (default: %default)",
        default = "LF"
    )

    group.add_option("--ser-nl",
        dest = "ser_newline",
        action = "store",
        help = "type of newlines that are expected on the serial port (default: %default)",
        default = "CR+LF"
    )

    # options for the auto file-uploader
    group.add_option("-F",
        dest = "auto_files",
        action = "callback",
        callback = autofiles_callback,
        default = []
    )

    (options, args) = parser.parse_args()


    # get port and baud rate from command line arguments or the option switches
    port = options.port
    baudrate = options.baudrate
    if args:
        if options.port is not None:
            parser.error("no arguments are allowed, options only when --port is given")
        port = args.pop(0)
        if args:
            try:
                baudrate = int(args[0])
            except ValueError:
                parser.error("baud rate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: port = 0

    # check newline modes for network connection
    mode = options.net_newline.upper()
    if mode == 'CR':
        net_newline = '\r'
    elif mode == 'LF':
        net_newline = '\n'
    elif mode == 'CR+LF' or mode == 'CRLF':
        net_newline = '\r\n'
    else:
        parser.error("Invalid value for --net-nl. Valid are 'CR', 'LF' and 'CR+LF'/'CRLF'.")

    # check newline modes for serial connection
    mode = options.ser_newline.upper()
    if mode == 'CR':
        ser_newline = '\r'
    elif mode == 'LF':
        ser_newline = '\n'
    elif mode == 'CR+LF' or mode == 'CRLF':
        ser_newline = '\r\n'
    else:
        parser.error("Invalid value for --ser-nl. Valid are 'CR', 'LF' and 'CR+LF'/'CRLF'.")

    # connect to serial port
    ser = serial.Serial()
    ser.port     = port
    ser.baudrate = baudrate
    ser.parity   = options.parity
    ser.rtscts   = options.rtscts
    ser.xonxoff  = options.xonxoff
    ser.timeout  = 1     # required so that the reader thread can exit

    if not options.quiet:
        sys.stderr.write("--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit\n")
        sys.stderr.write("--- %s %s,%s,%s,%s ---\n" % (ser.portstr, ser.baudrate, 8, ser.parity, 1))

    try:
        ser.open()
    except serial.SerialException:
        sys.stderr.write("Could not open serial port %s: \n" % (ser.portstr))
        sys.exit(1)

    if options.rts_state is not None:
        ser.setRTS(options.rts_state)

    if options.dtr_state is not None:
        ser.setDTR(options.dtr_state)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # srv.settimeout(1)
    srv.bind( ('', options.local_port) )
    srv.listen(5)
            
    # enter network <-> serial loop
    r = Redirector(
        ser,
        srv,
        options.stationname,
        options.radioid,
        options.convert and ser_newline or None,
        options.convert and net_newline or None,
        options.spy,
    )
    r.shortcut()
    
    # if requested, request an uplink connection to the server/port of interest
    if options.clientmode:
        newuplink = UplinkConnectionThread(options.uplink_address, options.uplink_port, r)
        newuplink.start()
        r.addconnection(newuplink)

    for i in range(len(options.auto_files)/5):
        start_index = i*5
        filename = options.auto_files[start_index]
        start_day = options.auto_files[start_index+1]
        start_time = options.auto_files[start_index+2]
        wait_time = options.auto_files[start_index+3]
        num_retries = options.auto_files[start_index+4]
        start_time = time.mktime(time.strptime(start_day + " " + start_time, "%m%d%y %H:%M:%S")) - time.timezone
        print filename + " being transmitted " + num_retries + " times at " + wait_time + " second intervals starting " + str((start_time - time.time())/3600) + " hours from now"
        wait_time = int(wait_time)
        num_retries = int(num_retries)
        new_auto_uplink = AutoForward(filename, start_time, num_retries, wait_time, r)
        new_auto_uplink.start()
        
    
    # Wait for incoming connections
    sys.stderr.write("Waiting for connection on %s...\n" % options.local_port)
    try:
        while True:
            channel, details = srv.accept()
            newclient = ClientConnectionThread(channel, r)
            newclient.start()
            r.addconnection(newclient)
    except KeyboardInterrupt:
        pass
        

    sys.stderr.write('\n--- exit ---\n')

