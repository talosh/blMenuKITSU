#
# FilmLight API Python bindings
#

# We require Python 2.7 or later, 3.4 or later
import sys
if sys.version_info[0] == 2:
    assert sys.version_info >= (2,7)
elif sys.version_info[0] > 2:
    assert sys.version_info >= (3,4)


import os
import platform
import websocket
import json
import random
import subprocess
import traceback

if sys.version_info[0] > 2:
    import enum

###############################################################################
#
# Library
#
# Library of interface types.
# Used to create object instances.

class Library:
    
    Classes = {}
    Decoders = {}

    @staticmethod
    def register_class( name, cls ):
        Library.Classes[name] = cls

    @staticmethod
    def get_classes():
        return Library.Classes.keys()

    @staticmethod
    def get_class(name):
        return Library.Classes[name]

    @staticmethod
    def create_instance(name, conn, target):
        cls = Library.Classes[name];
        return cls(conn, target)

    @staticmethod
    def register_decoder(otype, fn):
        Library.Decoders[otype] = fn

    @staticmethod
    def get_decoder(otype):
        return Library.Decoders.get(otype)


###############################################################################
#
# Types
#
# Define some basic types used by FilmLight API Interfaces

# Timecode
#
# Class representing an SMPTE timecode

class Timecode:
    def __init__(self, h, m, s, f, phase, fps, wrap ):
        self.hour = h
        self.minute = m
        self.second = s
        self.frame = f
        self.phase = phase
        self.fps = fps
        self.wrap = wrap

    def __str__(self):
        return "%02d:%02d:%02d:%02d" % (self.hour, self.minute, self.second, self.frame)

    def __repr__(self):
        return "<Timecode %02d:%02d:%02d:%02d,%d,%s>" % (self.hour, self.minute, self.second, self.frame, self.phase, self.fps)

    @staticmethod
    def from_dict(o):
        return Timecode(
            o.get("h"),
            o.get("m"),
            o.get("s"),
            o.get("f"),
            o.get("phase"),
            o.get("fps"),
            o.get("wrap")
        )

    def json(self):
        return {
            "_type": "timecode",
            "h": self.hour,
            "m": self.minute,
            "s": self.second,
            "f": self.frame,
            "phase": self.phase,
            "fps": self.fps,
            "wrap": self.wrap
        }

Library.register_decoder( "timecode", Timecode.from_dict )

# Keycode
#
# Class representing a Keycode type

class Keycode:
    def __init__(self, stock, feet, frames, perfs, gearing):
        self.stock = stock
        self.feet = feet
        self.frames = frames
        self.perfs = perfs
        self.gearing = gearing

    def __str__(self):
        if self.stock != None and self.stock != "":
            return "%s %05d+%02d.%d,%s" % (self.stock, self.feet, self.frames, self.perfs,self.gearing)
        else:
            return "%05d+%02d.%d,%s" % (self.feet, self.frames, self.perfs,self.gearing)
    
    def __repr__(self):
        if self.stock != None and self.stock != "":
            return "<Keycode %s %05d+%02d.%d,%s>" % (self.stock, self.feet, self.frames, self.perfs,self.gearing)
        else:
            return "<Keycode %05d+%02d.%d,%s>" % (self.feet, self.frames, self.perfs,self.gearing)

    @staticmethod
    def from_dict(o):
        return Keycode(
            o.get("stock"),
            o.get("feet"),
            o.get("frames"),
            o.get("perfs"),
            o.get("gearing")
        )

    def json(self):
        return {
            "_type": "keycode",
            "stock": self.stock,
            "feet": self.feet,
            "frames": self.frames,
            "perfs": self.perfs,
            "gearing": self.gearing
        }    

Library.register_decoder( "keycode", Keycode.from_dict )

# FrameNumber
#
# Class representing a frame number

class FrameNumber:
    def __init__(self, frame):
        self.frame = frame

    def __str__(self):
        return "%d" % self.frame

    def __repr__(self):
        return "<FrameNumber %d>" % self.frame

    @staticmethod
    def from_dict(o):
        return FrameNumber( o.get("frame") )

    def json(self):
        return { 
            "_type": "framenumber", 
            "frame": self.frame 
        }

Library.register_decoder( "framenumber", FrameNumber.from_dict )

# FLAPIException
#
# Thrown when an exception occurs

class FLAPIException(Exception):
    
    def __init__( self, msg ):
        self.msg = msg

    def __str__(self):
        return self.msg

# Interface
#
# Base class for all remote interface objects

class Interface:

    def __init__(self, conn, target):
        self.conn = conn
        self.target = target
        # Mapping from signal name to set of functions that handle signal
        self.handlers = {}

    def __str__(self):
        return "%s id %d" % (type(self).__name__, self.target)

    def __repr__(self):
        return "<flapi %s id %d>" % (type(self).__name__, self.target)

    # release()
    #
    # Call to release client and server-side resources for this object
    
    def release(self):
        if self.target == None:
            raise FLAPIException( "Attempt to release an object that has no instance" )
        self.conn.forget(self.target)
        self.target = None
   
    # connect( signal, handler )
    #
    # Connect 'handler' function to named signal.
    #
    # This function will be called whenever the named signal is generated
    # on the server.
    
    def connect(self, signal, handler): 
        if self.handlers.get(signal) == None:
            # Create new set to contain functions that are to be called
            # in response to this signal
            self.handlers[signal] = set()
            # Tell server that we are observing this signal from this object
            self.conn.connect_signal( self.target, signal )

        # Add function to set of handlers
        self.handlers[signal].add( handler )

    # disconnect( signal, handler )
    #
    # Disconnect 'handler' function from named signal.
    
    def disconnect(self, signal, handler):

        # Find list of functions handling this signal
        sighandlers = self.handlers.get(signal)
        if sighandlers == None:
            return

        # Remove handler from set
        if handler in sighandlers:
            sighandlers.remove(handler)

        # If set now empty, clear set and tell server no-one is observering
        # this signal any longer
        if len(sighandlers) == 0:
            self.handlers[signal] = None
            self.conn.disconnect_signal( self.target, signal )

    #### Private
    
    # json()
    # 
    # Return json representation of this object
    
    def json(self):
        return { "_handle": type(self).__name__, "_id": self.target }


    # dispatch( signal, args )
    #
    # Called by Connection to dispatch an asynchronous signal and its arguments
    # to any registered handler functions.
    
    def dispatch(self, signal, args):
        sighandlers = self.handlers.get(signal)
        if sighandlers == None:
            return

        result = None
        for h in sighandlers:
            try:
                r = h( self, signal, args )
                if result == None and r != None:
                    result = r
            except Exception as ex:
                print( "Failed to dispatch signal '%s' to handler '%s'" % (signal, h) )
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()

        return result

# APIJSONEncoder
#
# Specialised JSONEncoder which handles serialising flapi types

class APIJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr( o, 'json'):
            return o.json()
        elif isinstance( o, (set,frozenset) ):
            o2 = { "_type": "set" }
            for k in o:
                o2[k] = 1
            return o2
        elif isinstance( o, enum.Enum ):
            return o.value
        else:
            return json.JSONEncoder.default(self,o)

###############################################################################
#
# Connection
#
# Open a connection to the FilmLight API.
#
# There are two ways to open a connection to the FilmLight API:
#
# 1. Create new connection
#
#       Create a new Connection instance to the FilmLight API service on
#       local/remote host.
#
#       You can create multiple Connection objects for interacting
#       with flapi services on different hosts.
#
# 2. Open an existing global connection
#
#       This is the case when your script has been launched as a helper/service
#       by a FilmLight application, and the FLAPI_PORT environment variable
#       has been defined.
#
#       The connection can then be used to communicate with the parent FilmLight 
#       application.
#
#       There will only be one Connection object in this case.
#

class Connection:

    globalConn = None

    ###########################################################################
    # Public
    ###########################################################################

    def __init__(self, hostname="localhost", port=1984, username=None, password=None, token=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.token = token
        
        # Subprocess when flapid is launched using launch() method
        self.flapiPath = None
        self.process = None

        # Map of msg id to callback for pending async method calls
        self.pending_msgs = {}

        # Map of msg id to None or a reply for pending results of synchronous
        # method calls. If the value is None, then this indicates that there
        # is a wait method in the call stack waiting for a synchronous result
        # for that message id and that a matching reply has yet to be received.
        # If it's non-None (i.e. a reply), then we've received a matching reply
        # and are now simply waiting for the call stack to unwind so the waiting
        # wait() call can process the result (bug 58753).
        self.pending_sync_replies = {}

        self.websocket = None
        self.id = 1
        if os.environ.get("FLAPI_DEBUG") == "1":
            self.debug = 1 
        else:
            self.debug = 0        
        self.handles = {}
        self.setup_interfaces()
        
        # When debugging, used to count the nesting level when there are
        # recursive calls to wait().
        if self.debug:
            self.wait_nest_level = 0
       
    def set_debug(self,debug):
        self.debug = debug

    def connect(self):
        if self.websocket == None:
            return self.connect_ws()
        else:
            return True

    def is_connected(self):
        return (self.websocket != None)

    def close(self):
        if self.websocket != None:
            self.websocket.close()
            self.websocket = None

    def launch(self, product=None, version=None, flapiPath=None):
        # Find path to flapid executable
        if flapiPath is None:
            flapiPath = self.get_flapid_path(product, version)
        
        # Make fifo to receive flapid port number
        fifoPath = "/tmp/flapid-fifo-%d" % os.getpid()
        os.mkfifo( fifoPath )
        
        self.flapiPath = flapiPath

        # Launch flapid process
        args = [ flapiPath, "--slave", "--flmon", "--fifo", fifoPath ]
        self.process = subprocess.Popen(args)

        # Read port number back from fifo
        flapiPort = None
        with open(fifoPath, "r") as fp:
            flapiPort = int(fp.readline())

        os.unlink( fifoPath )

        if flapiPort is None:
            raise FLAPIException( "Cannot fetch port number from flapid" )

        self.hostname = "localhost"
        self.port = flapiPort

        return self.connect_ws()
    
    @staticmethod
    def get():
        # Is a connection already open?
        if Connection.globalConn != None:
            return Connection.globalConn

        # Lookup FLAPI_PORT environment variable
        flapi_port = os.environ.get( "FLAPI_PORT" )
        if flapi_port == None:
            return None

        # Create connection to localhost on FLAPI_PORT
        conn = Connection("localhost", int(flapi_port), None, None)
        conn.connect()
        Connection.globalConn = conn
        return conn

    def get_permissions():
        return self.call( None, "get_permissions", None )

    ###########################################################################
    # Private
    ###########################################################################

    def setup_interfaces(self):
        # Get list of interface classes
        clss = Library.get_classes()
        for clsName in clss:
            # Create instance of interface class with target=None
            # This allows calling static methods on the class.
            #
            # Assign it to the Connection as an attribute.
            setattr( self, clsName, Library.create_instance(clsName, self, None) )

    @staticmethod
    def get_token_path():
        homeDir = os.environ.get("HOME")
        if platform.system() == "Linux":
            return homeDir + "/.filmlight/flapi-token"
        elif platform.system() == "Darwin":
            return homeDir + "/Library/Preferences/FilmLight/flapi-token"
        else:
            return None

    @staticmethod
    def read_token():
        tokenPath = Connection.get_token_path()
        if tokenPath is None:
            return None

        token = None
        try:
            with open( tokenPath ) as fp:
                lines = fp.read().splitlines()
                if len(lines) > 0:
                    token = lines[0]
        except:
            pass

        # Generate a token file. This can be read by flapid and used to
        # authenticate the user.
        if token == None:
            token = "%032x" % random.getrandbits(128)

            tokenDir = os.path.dirname(tokenPath)
            if sys.version_info[0] == 2:
                if not os.path.exists(tokenDir):
                    os.makedirs( tokenDir )
            else:
                os.makedirs( tokenDir, exist_ok=True )

            with open( tokenPath, "w" ) as fp:
                fp.write(token)

        return token

    def get_flapid_path(self, product, version):
        flapiPath = os.environ.get("FLAPI_PATH")
        if flapiPath is not None:
            return flapiPath

        # Determine which product to launch
        if product is None or product == "baselight":
            if os.uname().sysname == "Darwin":
                product="Baselight"
            else:
                product="baselight"

        elif product == "daylight":
            if os.uname().sysname == "Darwin":
                product="Daylight"
            else:
                product="daylight"

        elif product == "baselightserver":
            if os.uname().sysname == "Darwin":
                product="BaselightServer"
                flapiPath = "/Applications/%s/%s/Utilities/Tools/flapid" % (product, version)
            else:
                product="baselightserver"

        else:
            raise FLAPIException("Invalid product name " + product)

        if os.uname().sysname == "Darwin":
            if version is None:
                flapiPath = "/Applications/%s/Current/Utilities/Tools/flapid" % (product)
            else:
                flapiPath = "/Applications/%s/%s/Utilities/Tools/flapid" % (product, version)
        else:
            if version is None:
                flapiPath = "/usr/fl/%s/bin/flapid" % (product)
            else:
                flapiPath = "/usr/fl/%s-%s/bin/flapid" % (product, version)

        return flapiPath
    
    def connect_ws(self):
        try:
            self.websocket = websocket.create_connection( "ws://%s:%d/" % (self.hostname, self.port) )
        except Exception as err:
            raise FLAPIException( "Cannot connect to %s: %s" % (self.hostname, err) )

        # If hostname is localhost, and we have a valid token file, use that token to
        # authenticate with the server
        curUser = os.environ.get("USER")
        curToken = os.environ.get("FLAPI_TOKEN" )
        if curToken is None:
            curToken = Connection.read_token()
        if ((self.hostname == "localhost") and 
                (self.username == None or self.username == curUser) and
                (self.password == None) and
                (self.token == None) and
                (curToken != None)):
            self.username = curUser
            self.token = curToken

        # If we are not running flapid as a launch process, send connect message to authenticate
        if self.process is None:
            # Send 'connect' message
            args = {
                "method": "connect",
                "username": self.username,
                "password": self.password,
                "token": self.token,
            }

            try:
                result = self.send_message( args )
                if result != 1:
                    raise FLAPIException( "Authentication failed" )
            except Exception as err:
                raise FLAPIException( "Cannot connect to %s: %s" % (self.hostname, err) )

        return True

    def decode_obj( self, o ):
        # check if o is a handle reference
        o_handle = o.get("_handle")
        o_id = o.get("_id")
        o_type = o.get("_type")

        if o_handle != None and o_id != None:
            # find existing handle
            iface = self.handles.get(o_id)
            if iface != None:
                return iface

            # create new instance
            iface = Library.create_instance(o_handle, self, o_id)
            self.handles[o_id] = iface
            return iface

        elif o_type == "set":
            # Convert into Python set 
            return set( filter( lambda k : k != "_type", o ) )

        elif o_type != None:
            decoder = Library.get_decoder(o_type)
            return decoder(o)

        else:
            return o
   
    # Send message to server
    #
    # To send asynchronously, pass a callback
    # To block until message reply is received, set block=True
    #
    def send_message(self, msg, block=True, callback=None):
        # allocate message id
        if block == True or callback != None:
            msg["id"] = self.id
            self.id += 1

        # convert to JSON
        msg_json = json.dumps( msg, cls=APIJSONEncoder )
        if self.debug:
            print( "FLAPI Client: Sending JSON:\n%s\n" % msg_json )

        # send to server
        self.websocket.send( msg_json )

        # if blocking, wait on response
        if block == True:
            return self.wait(msg)
       
        # If non-blocking, register callback if required
        if callback != None:
            self.pending_msgs[msg["id"]] = callback
       
    # Wait on messages from server
    #
    # If message is an async signal, it will be dispatched
    # If message is result for async method, callback will be invoked
    # If waiting on result for a specific method, function will return
    #   when the result for that function is received
    # Otherwise it will exit after the first message
    #
    def wait(self, waitOnMsg=None):
        if self.debug:
            self.wait_nest_level+=1
            print("FLAPI Client: wait, IN nest_level=%d >>>>>>>>>>>>>>>>>>>>" % self.wait_nest_level)
        if waitOnMsg != None:
            waitid = waitOnMsg.get("id")
            # Write a placeholder into the dictionary where pending async
            # replies are written so later code knows that something is
            # expected..
            self.pending_sync_replies[waitid] = None
        else:
            waitid = None

        if self.debug:
            print( "FLAPI Client: wait, msgid %s" % waitid )

        while True:
            # Check that the connection has not been closed
            # (via async method callback or async signal)
            if self.websocket == None:
                if self.debug:
                    print("FLAPI Client: wait, RETURN nest_level=%d <<<<<<<<<<<<<<<<<<" % self.wait_nest_level)
                    self.wait_nest_level -= 1
                return

            # Receive message from websocket
            buf = self.websocket.recv()
            if buf == None:
                raise FLAPIException( "Connection closed" )
                
            if self.debug:
                print( "FLAPI Client: Received JSON:\n%s\n" % buf )

            # Parse JSON
            reply = json.loads( buf, object_hook=self.decode_obj )

            msgid = reply.get("id")

            # Handle async signal
            if reply.get("method") == "signal":
                # Lookup target
                target = reply["target"]

                obj = self.handles.get( target );
                params = reply.get("params")
                if params == None:
                    raise FLAPIException( "'signal' message has no params")

                signame = params.get("signal")
                if signame == None:
                    raise FLAPIException( "'signal' params has no signal name")

                sigargs = params.get("args")

                sigres = None
                if obj != None:
                    sigres = obj.dispatch( signame, sigargs ) 

                # Check if this signal is synchronous, we must send a reply
                sigid = params.get("sigid")
                issync = params.get("sync")
                if issync == 1:
                    sigreply = {
                        "jsonrpc": "2.0",
                        "method": "signal_result",
                        "target": target,
                        "params": {
                            "sigid": sigid,
                            "result": sigres
                        }
                    }
                    self.send_message( sigreply, False, None )
            
            # Handle async method completion
            elif msgid != None and self.pending_msgs.get(msgid) != None:
                # Invoke callback
                cb = self.pending_msgs[msgid]
                cb()

                # Remove from pending messages
                del self.pending_msgs[msgid]

            # Handle synchronous method replies
            elif msgid != None and msgid in self.pending_sync_replies:
                if self.debug:
                    print( "FLAPI Client: storing sync method result for msgid %s" % msgid )
                self.pending_sync_replies[msgid] = reply

            # If we're not waiting on a specific message, exit after message received.
            elif waitOnMsg == None:
                if self.debug:
                    print( "FLAPI Client: wait, not waitid, exiting" )
                    print("FLAPI Client: wait, RETURN nest_level=%d <<<<<<<<<<<<<<<<<<" % self.wait_nest_level)
                    self.wait_nest_level -= 1
                return

            # If we're waiting for the result of a syncronous method call, look
            # to see if a matching reply has arrived and been stored away..
            if waitid != None:
                stored_reply = self.pending_sync_replies.get(waitid)
                if stored_reply != None:
                    del self.pending_sync_replies[waitid]
                                
                    error = stored_reply.get("error");
                    if error != None:
                        raise FLAPIException( error.get("message") )

                    if self.debug:
                        print( "FLAPI Client: wait, got stored result for %s" % waitid )
                        print("FLAPI Client: wait, RETURN nest_level=%d <<<<<<<<<<<<<<<<<<" % self.wait_nest_level)
                        self.wait_nest_level -= 1
                    return stored_reply.get("result")

            # Otherwise, run again until we receive result
            if self.debug:
                print("FLAPI Client: wait, GO AROUND AGAIN nest_level=%d ----------------------" % self.wait_nest_level )
            
    # Send method call to server
    #
    def call(self, target, method, params, block=True, callback=None):
        
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "target": target,
            "params": params
        }

        return self.send_message( msg, block, callback )

    # Subscribe to signal from object
    #
    def connect_signal(self, target, signal):

        msg = {
            "jsonrpc": "2.0",
            "method": "connect_signal",
            "target": target,
            "params": { "signal": signal }
        }
        
        return self.send_message( msg, True, None )

    # Unsubscribe from signal from object
    #
    def disconnect_signal(self, target, signal):

        msg = {
            "jsonrpc": "2.0",
            "method": "disconnect_signal",
            "target": target,
            "params": { "signal": signal }
        }
        
        return self.send_message( msg, True, None )

    # Forget object
    #
    def forget(self, target):

        msg = {
            "jsonrpc": "2.0",
            "method": "forget",
            "target": target,
        }
        
        return self.send_message( msg, True, None )

    # Register a plugin script with the host application
    #
    def register_script(self, scriptPath, version, status):
        msg = {
            "jsonrpc": "2.0",
            "method": "register_script",
            "path": scriptPath,
            "version": version,
            "status" : status
        }

        return self.send_message( msg, False, None )
        

###############################################################################
# Constants
#  AUDIOSEQ_TYPE : Type of Audio in an Audio Sequence
#    AUDIOSEQTYPE_NONE : No Audio
#    AUDIOSEQTYPE_FILE : Audio File
#    AUDIOSEQTYPE_STEMS : Audio Stems
#    AUDIOSEQTYPE_MOVIE : Audio from Movie
#    AUDIOSEQTYPE_TONE : Audio is generated Tone
if sys.version_info[0] >= 3:
    class AUDIOSEQ_TYPE(enum.Enum):
        AUDIOSEQTYPE_NONE="AST_NONE"
        AUDIOSEQTYPE_FILE="AST_FILE"
        AUDIOSEQTYPE_STEMS="AST_STEMS"
        AUDIOSEQTYPE_MOVIE="AST_MOVIE"
        AUDIOSEQTYPE_TONE="AST_TONE"
        def describe(self):
            descs = {
                AUDIOSEQ_TYPE.AUDIOSEQTYPE_NONE: "No Audio",
                AUDIOSEQ_TYPE.AUDIOSEQTYPE_FILE: "Audio File",
                AUDIOSEQ_TYPE.AUDIOSEQTYPE_STEMS: "Audio Stems",
                AUDIOSEQ_TYPE.AUDIOSEQTYPE_MOVIE: "Audio from Movie",
                AUDIOSEQ_TYPE.AUDIOSEQTYPE_TONE: "Audio is generated Tone",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSEQ_TYPE}

AUDIOSEQTYPE_NONE="AST_NONE"
AUDIOSEQTYPE_FILE="AST_FILE"
AUDIOSEQTYPE_STEMS="AST_STEMS"
AUDIOSEQTYPE_MOVIE="AST_MOVIE"
AUDIOSEQTYPE_TONE="AST_TONE"
#  AUDIOSYNCSTATUS : Status info related to audio sync progress
#    AUDIOSYNCSTATUS_FAIL : Failure during audio sync operation
#    AUDIOSYNCSTATUS_WARN : Warning during audio sync operation
#    AUDIOSYNCSTATUS_INFO : Info from audio sync operation
#    AUDIOSYNCSTATUS_NOTE : Note from audio sync operation
#    AUDIOSYNCSTATUS_SCAN : Filesystem scanning progress
if sys.version_info[0] >= 3:
    class AUDIOSYNCSTATUS(enum.Enum):
        AUDIOSYNCSTATUS_FAIL="FAIL"
        AUDIOSYNCSTATUS_WARN="WARN"
        AUDIOSYNCSTATUS_INFO="INFO"
        AUDIOSYNCSTATUS_NOTE="NOTE"
        AUDIOSYNCSTATUS_SCAN="SCAN"
        def describe(self):
            descs = {
                AUDIOSYNCSTATUS.AUDIOSYNCSTATUS_FAIL: "Failure during audio sync operation",
                AUDIOSYNCSTATUS.AUDIOSYNCSTATUS_WARN: "Warning during audio sync operation",
                AUDIOSYNCSTATUS.AUDIOSYNCSTATUS_INFO: "Info from audio sync operation",
                AUDIOSYNCSTATUS.AUDIOSYNCSTATUS_NOTE: "Note from audio sync operation",
                AUDIOSYNCSTATUS.AUDIOSYNCSTATUS_SCAN: "Filesystem scanning progress",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNCSTATUS}

AUDIOSYNCSTATUS_FAIL="FAIL"
AUDIOSYNCSTATUS_WARN="WARN"
AUDIOSYNCSTATUS_INFO="INFO"
AUDIOSYNCSTATUS_NOTE="NOTE"
AUDIOSYNCSTATUS_SCAN="SCAN"
#  AUDIOSYNC_CRITERIA : Values for AudioSyncSettings Criteria
#    AUDIOSYNC_CRITERIA_TIMECODE : Timecode
#    AUDIOSYNC_CRITERIA_SRCTIMECODE : Source Timecode
#    AUDIOSYNC_CRITERIA_DATESRCTIMECODE : Date & Source Timecode
#    AUDIOSYNC_CRITERIA_SCENETAKE : Scene & Take
#    AUDIOSYNC_CRITERIA_SHOTSCENETAKE : Shot Scene & Take
if sys.version_info[0] >= 3:
    class AUDIOSYNC_CRITERIA(enum.Enum):
        AUDIOSYNC_CRITERIA_TIMECODE="Timecode"
        AUDIOSYNC_CRITERIA_SRCTIMECODE="SrcTimecode"
        AUDIOSYNC_CRITERIA_DATESRCTIMECODE="DateSrcTimecode"
        AUDIOSYNC_CRITERIA_SCENETAKE="SceneTake"
        AUDIOSYNC_CRITERIA_SHOTSCENETAKE="ShotSceneTake"
        def describe(self):
            descs = {
                AUDIOSYNC_CRITERIA.AUDIOSYNC_CRITERIA_TIMECODE: "Timecode",
                AUDIOSYNC_CRITERIA.AUDIOSYNC_CRITERIA_SRCTIMECODE: "Source Timecode",
                AUDIOSYNC_CRITERIA.AUDIOSYNC_CRITERIA_DATESRCTIMECODE: "Date & Source Timecode",
                AUDIOSYNC_CRITERIA.AUDIOSYNC_CRITERIA_SCENETAKE: "Scene & Take",
                AUDIOSYNC_CRITERIA.AUDIOSYNC_CRITERIA_SHOTSCENETAKE: "Shot Scene & Take",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_CRITERIA}

AUDIOSYNC_CRITERIA_TIMECODE="Timecode"
AUDIOSYNC_CRITERIA_SRCTIMECODE="SrcTimecode"
AUDIOSYNC_CRITERIA_DATESRCTIMECODE="DateSrcTimecode"
AUDIOSYNC_CRITERIA_SCENETAKE="SceneTake"
AUDIOSYNC_CRITERIA_SHOTSCENETAKE="ShotSceneTake"
#  AUDIOSYNC_FPS : Values for AudioSyncSettings FPS
#    AUDIOSYNC_FPS_23976 : 23.976 fps
#    AUDIOSYNC_FPS_24000 : 24 fps
#    AUDIOSYNC_FPS_25000 : 25 fps
#    AUDIOSYNC_FPS_29970 : 29.97 fps
#    AUDIOSYNC_FPS_2997DF : 29.97 fps DF
#    AUDIOSYNC_FPS_30000 : 30 fps
#    AUDIOSYNC_FPS_48000 : 48 fps
#    AUDIOSYNC_FPS_50000 : 50 fps
#    AUDIOSYNC_FPS_59940 : 59.94 fps
#    AUDIOSYNC_FPS_60000 : 60 fps
if sys.version_info[0] >= 3:
    class AUDIOSYNC_FPS(enum.Enum):
        AUDIOSYNC_FPS_23976="23976"
        AUDIOSYNC_FPS_24000="24000"
        AUDIOSYNC_FPS_25000="25000"
        AUDIOSYNC_FPS_29970="29970"
        AUDIOSYNC_FPS_2997DF="2997DF"
        AUDIOSYNC_FPS_30000="30000"
        AUDIOSYNC_FPS_48000="48000"
        AUDIOSYNC_FPS_50000="50000"
        AUDIOSYNC_FPS_59940="59940"
        AUDIOSYNC_FPS_60000="60000"
        def describe(self):
            descs = {
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_23976: "23.976 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_24000: "24 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_25000: "25 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_29970: "29.97 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_2997DF: "29.97 fps DF",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_30000: "30 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_48000: "48 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_50000: "50 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_59940: "59.94 fps",
                AUDIOSYNC_FPS.AUDIOSYNC_FPS_60000: "60 fps",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_FPS}

AUDIOSYNC_FPS_23976="23976"
AUDIOSYNC_FPS_24000="24000"
AUDIOSYNC_FPS_25000="25000"
AUDIOSYNC_FPS_29970="29970"
AUDIOSYNC_FPS_2997DF="2997DF"
AUDIOSYNC_FPS_30000="30000"
AUDIOSYNC_FPS_48000="48000"
AUDIOSYNC_FPS_50000="50000"
AUDIOSYNC_FPS_59940="59940"
AUDIOSYNC_FPS_60000="60000"
#  AUDIOSYNC_METADATA : Values for AudioSyncSettings Metadata
#    AUDIOSYNC_METADATA_SCENETAKE : Scene & Take
#    AUDIOSYNC_METADATA_DATE : Date
if sys.version_info[0] >= 3:
    class AUDIOSYNC_METADATA(enum.Enum):
        AUDIOSYNC_METADATA_SCENETAKE="SceneTake"
        AUDIOSYNC_METADATA_DATE="Date"
        def describe(self):
            descs = {
                AUDIOSYNC_METADATA.AUDIOSYNC_METADATA_SCENETAKE: "Scene & Take",
                AUDIOSYNC_METADATA.AUDIOSYNC_METADATA_DATE: "Date",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_METADATA}

AUDIOSYNC_METADATA_SCENETAKE="SceneTake"
AUDIOSYNC_METADATA_DATE="Date"
#  AUDIOSYNC_RATIO : Values for AudioSyncSettings Ratio
#    AUDIOSYNC_RATIO_1_TO_1 : 1:1
#    AUDIOSYNC_RATIO_1001_TO_1000 : 1001:1000
#    AUDIOSYNC_RATIO_1000_TO_1001 : 1000:1001
#    AUDIOSYNC_RATIO_25_TO_24 : 25:24
#    AUDIOSYNC_RATIO_24_TO_25 : 24:25
if sys.version_info[0] >= 3:
    class AUDIOSYNC_RATIO(enum.Enum):
        AUDIOSYNC_RATIO_1_TO_1="1:1"
        AUDIOSYNC_RATIO_1001_TO_1000="1001:1000"
        AUDIOSYNC_RATIO_1000_TO_1001="1000:1001"
        AUDIOSYNC_RATIO_25_TO_24="25:24"
        AUDIOSYNC_RATIO_24_TO_25="24:25"
        def describe(self):
            descs = {
                AUDIOSYNC_RATIO.AUDIOSYNC_RATIO_1_TO_1: "1:1",
                AUDIOSYNC_RATIO.AUDIOSYNC_RATIO_1001_TO_1000: "1001:1000",
                AUDIOSYNC_RATIO.AUDIOSYNC_RATIO_1000_TO_1001: "1000:1001",
                AUDIOSYNC_RATIO.AUDIOSYNC_RATIO_25_TO_24: "25:24",
                AUDIOSYNC_RATIO.AUDIOSYNC_RATIO_24_TO_25: "24:25",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_RATIO}

AUDIOSYNC_RATIO_1_TO_1="1:1"
AUDIOSYNC_RATIO_1001_TO_1000="1001:1000"
AUDIOSYNC_RATIO_1000_TO_1001="1000:1001"
AUDIOSYNC_RATIO_25_TO_24="25:24"
AUDIOSYNC_RATIO_24_TO_25="24:25"
#  AUDIOSYNC_READLTC : Values for AudioSyncSettings ReadLTC
#    AUDIOSYNC_READLTC_NO : No
#    AUDIOSYNC_READLTC_CHANNEL : From Channel
#    AUDIOSYNC_READLTC_TRACK : From Track
if sys.version_info[0] >= 3:
    class AUDIOSYNC_READLTC(enum.Enum):
        AUDIOSYNC_READLTC_NO="No"
        AUDIOSYNC_READLTC_CHANNEL="Channel"
        AUDIOSYNC_READLTC_TRACK="Track"
        def describe(self):
            descs = {
                AUDIOSYNC_READLTC.AUDIOSYNC_READLTC_NO: "No",
                AUDIOSYNC_READLTC.AUDIOSYNC_READLTC_CHANNEL: "From Channel",
                AUDIOSYNC_READLTC.AUDIOSYNC_READLTC_TRACK: "From Track",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_READLTC}

AUDIOSYNC_READLTC_NO="No"
AUDIOSYNC_READLTC_CHANNEL="Channel"
AUDIOSYNC_READLTC_TRACK="Track"
#  AUDIOSYNC_SUBSEARCH : Values for AudioSyncSettings SubSearch
#    AUDIOSYNC_SUBSEARCH_ALL : All Sub-Directories
#    AUDIOSYNC_SUBSEARCH_NAMED : Sub-Directories Named
#    AUDIOSYNC_SUBSEARCH_NEAREST : Nearest Sub-Directory Named
if sys.version_info[0] >= 3:
    class AUDIOSYNC_SUBSEARCH(enum.Enum):
        AUDIOSYNC_SUBSEARCH_ALL="All"
        AUDIOSYNC_SUBSEARCH_NAMED="Named"
        AUDIOSYNC_SUBSEARCH_NEAREST="Nearest"
        def describe(self):
            descs = {
                AUDIOSYNC_SUBSEARCH.AUDIOSYNC_SUBSEARCH_ALL: "All Sub-Directories",
                AUDIOSYNC_SUBSEARCH.AUDIOSYNC_SUBSEARCH_NAMED: "Sub-Directories Named",
                AUDIOSYNC_SUBSEARCH.AUDIOSYNC_SUBSEARCH_NEAREST: "Nearest Sub-Directory Named",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIOSYNC_SUBSEARCH}

AUDIOSYNC_SUBSEARCH_ALL="All"
AUDIOSYNC_SUBSEARCH_NAMED="Named"
AUDIOSYNC_SUBSEARCH_NEAREST="Nearest"
#  AUDIO_RATE : Audio Sample Rate
#    AUDIO_RATE_44100 : 44.1 kHz
#    AUDIO_RATE_48000 : 48 kHz
#    AUDIO_RATE_96000 : 96 kHz
if sys.version_info[0] >= 3:
    class AUDIO_RATE(enum.Enum):
        AUDIO_RATE_44100=44100
        AUDIO_RATE_48000=48000
        AUDIO_RATE_96000=96000
        def describe(self):
            descs = {
                AUDIO_RATE.AUDIO_RATE_44100: "44.1 kHz",
                AUDIO_RATE.AUDIO_RATE_48000: "48 kHz",
                AUDIO_RATE.AUDIO_RATE_96000: "96 kHz",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in AUDIO_RATE}

AUDIO_RATE_44100=44100
AUDIO_RATE_48000=48000
AUDIO_RATE_96000=96000
#  BLGEXPORT_LOCKGRADE : Values for BLGExportSettings LockGrade
#    BLGEXPORT_LOCKGRADE_READWRITE : No
#    BLGEXPORT_LOCKGRADE_LOCKED : Yes
if sys.version_info[0] >= 3:
    class BLGEXPORT_LOCKGRADE(enum.Enum):
        BLGEXPORT_LOCKGRADE_READWRITE="ReadWrite"
        BLGEXPORT_LOCKGRADE_LOCKED="Locked"
        def describe(self):
            descs = {
                BLGEXPORT_LOCKGRADE.BLGEXPORT_LOCKGRADE_READWRITE: "No",
                BLGEXPORT_LOCKGRADE.BLGEXPORT_LOCKGRADE_LOCKED: "Yes",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BLGEXPORT_LOCKGRADE}

BLGEXPORT_LOCKGRADE_READWRITE="ReadWrite"
BLGEXPORT_LOCKGRADE_LOCKED="Locked"
#  BLGEXPORT_SCALE : Values for BLGExportSettings Scale
#    BLGEXPORT_SCALE_1 : Full
#    BLGEXPORT_SCALE_2 : Half
#    BLGEXPORT_SCALE_4 : Quarter
#    BLGEXPORT_SCALE_16 : Sixteenth
if sys.version_info[0] >= 3:
    class BLGEXPORT_SCALE(enum.Enum):
        BLGEXPORT_SCALE_1=1
        BLGEXPORT_SCALE_2=2
        BLGEXPORT_SCALE_4=4
        BLGEXPORT_SCALE_16=16
        def describe(self):
            descs = {
                BLGEXPORT_SCALE.BLGEXPORT_SCALE_1: "Full",
                BLGEXPORT_SCALE.BLGEXPORT_SCALE_2: "Half",
                BLGEXPORT_SCALE.BLGEXPORT_SCALE_4: "Quarter",
                BLGEXPORT_SCALE.BLGEXPORT_SCALE_16: "Sixteenth",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BLGEXPORT_SCALE}

BLGEXPORT_SCALE_1=1
BLGEXPORT_SCALE_2=2
BLGEXPORT_SCALE_4=4
BLGEXPORT_SCALE_16=16
#  BURNIN_BORDER : Define border type for burnin text item
#    BURNIN_BORDER_NONE : No border
#    BURNIN_BORDER_RECTANGLE : Rectangle
#    BURNIN_BORDER_LOZENGE : Lozenge
if sys.version_info[0] >= 3:
    class BURNIN_BORDER(enum.Enum):
        BURNIN_BORDER_NONE="none"
        BURNIN_BORDER_RECTANGLE="rect"
        BURNIN_BORDER_LOZENGE="loz"
        def describe(self):
            descs = {
                BURNIN_BORDER.BURNIN_BORDER_NONE: "No border",
                BURNIN_BORDER.BURNIN_BORDER_RECTANGLE: "Rectangle",
                BURNIN_BORDER.BURNIN_BORDER_LOZENGE: "Lozenge",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BURNIN_BORDER}

BURNIN_BORDER_NONE="none"
BURNIN_BORDER_RECTANGLE="rect"
BURNIN_BORDER_LOZENGE="loz"
#  BURNIN_HALIGN : Define horizontal alignment of burnin text item
#    BURNIN_HALIGN_LEFT : Left aligned
#    BURNIN_HALIGN_CENTER : Center aligned
#    BURNIN_HALIGN_RIGHT : Right aligned
if sys.version_info[0] >= 3:
    class BURNIN_HALIGN(enum.Enum):
        BURNIN_HALIGN_LEFT=0
        BURNIN_HALIGN_CENTER=1
        BURNIN_HALIGN_RIGHT=2
        def describe(self):
            descs = {
                BURNIN_HALIGN.BURNIN_HALIGN_LEFT: "Left aligned",
                BURNIN_HALIGN.BURNIN_HALIGN_CENTER: "Center aligned",
                BURNIN_HALIGN.BURNIN_HALIGN_RIGHT: "Right aligned",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BURNIN_HALIGN}

BURNIN_HALIGN_LEFT=0
BURNIN_HALIGN_CENTER=1
BURNIN_HALIGN_RIGHT=2
#  BURNIN_ITEM_TYPE : Specify burnin item type
#    BURNIN_ITEM_TEXT : Text item
#    BURNIN_ITEM_IMAGE : Image item
if sys.version_info[0] >= 3:
    class BURNIN_ITEM_TYPE(enum.Enum):
        BURNIN_ITEM_TEXT="text"
        BURNIN_ITEM_IMAGE="image"
        def describe(self):
            descs = {
                BURNIN_ITEM_TYPE.BURNIN_ITEM_TEXT: "Text item",
                BURNIN_ITEM_TYPE.BURNIN_ITEM_IMAGE: "Image item",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BURNIN_ITEM_TYPE}

BURNIN_ITEM_TEXT="text"
BURNIN_ITEM_IMAGE="image"
#  BURNIN_VALIGN : Define vertical alignment of burnin text item
#    BURNIN_VALIGN_TOP : Top aligned
#    BURNIN_VALIGN_MIDDLE : Middle aligned
#    BURNIN_VALIGN_BOTTOM : Bottom aligned
if sys.version_info[0] >= 3:
    class BURNIN_VALIGN(enum.Enum):
        BURNIN_VALIGN_TOP=0
        BURNIN_VALIGN_MIDDLE=1
        BURNIN_VALIGN_BOTTOM=2
        def describe(self):
            descs = {
                BURNIN_VALIGN.BURNIN_VALIGN_TOP: "Top aligned",
                BURNIN_VALIGN.BURNIN_VALIGN_MIDDLE: "Middle aligned",
                BURNIN_VALIGN.BURNIN_VALIGN_BOTTOM: "Bottom aligned",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in BURNIN_VALIGN}

BURNIN_VALIGN_TOP=0
BURNIN_VALIGN_MIDDLE=1
BURNIN_VALIGN_BOTTOM=2
#  CDLEXPORT_CDLLAYER : Values for CDLExportSettings CDLLayer
#    CDLEXPORT_CDLLAYER_TOP : Top
#    CDLEXPORT_CDLLAYER_BOTTOM : Bottom
#    CDLEXPORT_CDLLAYER_CUSTOM : Layer n
if sys.version_info[0] >= 3:
    class CDLEXPORT_CDLLAYER(enum.Enum):
        CDLEXPORT_CDLLAYER_TOP="top"
        CDLEXPORT_CDLLAYER_BOTTOM="bottom"
        CDLEXPORT_CDLLAYER_CUSTOM="custom"
        def describe(self):
            descs = {
                CDLEXPORT_CDLLAYER.CDLEXPORT_CDLLAYER_TOP: "Top",
                CDLEXPORT_CDLLAYER.CDLEXPORT_CDLLAYER_BOTTOM: "Bottom",
                CDLEXPORT_CDLLAYER.CDLEXPORT_CDLLAYER_CUSTOM: "Layer n",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CDLEXPORT_CDLLAYER}

CDLEXPORT_CDLLAYER_TOP="top"
CDLEXPORT_CDLLAYER_BOTTOM="bottom"
CDLEXPORT_CDLLAYER_CUSTOM="custom"
#  CDLEXPORT_FORMAT : Values for CDLExportSettings Format
#    CDLEXPORT_FORMAT_CC : .cc file	Color Correction, one correction per file
#    CDLEXPORT_FORMAT_CCC : .ccc file	Color Correction Collection, all corrections in one file
if sys.version_info[0] >= 3:
    class CDLEXPORT_FORMAT(enum.Enum):
        CDLEXPORT_FORMAT_CC="CC"
        CDLEXPORT_FORMAT_CCC="CCC"
        def describe(self):
            descs = {
                CDLEXPORT_FORMAT.CDLEXPORT_FORMAT_CC: ".cc file	Color Correction, one correction per file",
                CDLEXPORT_FORMAT.CDLEXPORT_FORMAT_CCC: ".ccc file	Color Correction Collection, all corrections in one file",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CDLEXPORT_FORMAT}

CDLEXPORT_FORMAT_CC="CC"
CDLEXPORT_FORMAT_CCC="CCC"
#  CUBEEXPORT_CUBERESOLUTION : Values for CubeExportSettings CubeResolution
#    CUBEEXPORT_CUBERESOLUTION_DEFAULT : Default
#    CUBEEXPORT_CUBERESOLUTION_16 : 16x16x16
#    CUBEEXPORT_CUBERESOLUTION_17 : 17x17x17
#    CUBEEXPORT_CUBERESOLUTION_32 : 32x32x32
#    CUBEEXPORT_CUBERESOLUTION_33 : 33x33x33
#    CUBEEXPORT_CUBERESOLUTION_64 : 64x64x64
if sys.version_info[0] >= 3:
    class CUBEEXPORT_CUBERESOLUTION(enum.Enum):
        CUBEEXPORT_CUBERESOLUTION_DEFAULT=-1
        CUBEEXPORT_CUBERESOLUTION_16=16
        CUBEEXPORT_CUBERESOLUTION_17=17
        CUBEEXPORT_CUBERESOLUTION_32=32
        CUBEEXPORT_CUBERESOLUTION_33=33
        CUBEEXPORT_CUBERESOLUTION_64=64
        def describe(self):
            descs = {
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_DEFAULT: "Default",
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_16: "16x16x16",
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_17: "17x17x17",
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_32: "32x32x32",
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_33: "33x33x33",
                CUBEEXPORT_CUBERESOLUTION.CUBEEXPORT_CUBERESOLUTION_64: "64x64x64",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_CUBERESOLUTION}

CUBEEXPORT_CUBERESOLUTION_DEFAULT=-1
CUBEEXPORT_CUBERESOLUTION_16=16
CUBEEXPORT_CUBERESOLUTION_17=17
CUBEEXPORT_CUBERESOLUTION_32=32
CUBEEXPORT_CUBERESOLUTION_33=33
CUBEEXPORT_CUBERESOLUTION_64=64
#  CUBEEXPORT_EXTENDEDRANGES : Values for CubeExportSettings ExtendedRanges
#    CUBEEXPORT_EXTENDEDRANGES_NO : No
#    CUBEEXPORT_EXTENDEDRANGES_LINEAR : Linear
#    CUBEEXPORT_EXTENDEDRANGES_LOG : Log
if sys.version_info[0] >= 3:
    class CUBEEXPORT_EXTENDEDRANGES(enum.Enum):
        CUBEEXPORT_EXTENDEDRANGES_NO="No"
        CUBEEXPORT_EXTENDEDRANGES_LINEAR="Linear"
        CUBEEXPORT_EXTENDEDRANGES_LOG="Log"
        def describe(self):
            descs = {
                CUBEEXPORT_EXTENDEDRANGES.CUBEEXPORT_EXTENDEDRANGES_NO: "No",
                CUBEEXPORT_EXTENDEDRANGES.CUBEEXPORT_EXTENDEDRANGES_LINEAR: "Linear",
                CUBEEXPORT_EXTENDEDRANGES.CUBEEXPORT_EXTENDEDRANGES_LOG: "Log",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_EXTENDEDRANGES}

CUBEEXPORT_EXTENDEDRANGES_NO="No"
CUBEEXPORT_EXTENDEDRANGES_LINEAR="Linear"
CUBEEXPORT_EXTENDEDRANGES_LOG="Log"
#  CUBEEXPORT_LUT1OPTIONS : Values for CubeExportSettings LUT1Options
#    CUBEEXPORT_LUT1OPTIONS_INPUT : Input Transform
#    CUBEEXPORT_LUT1OPTIONS_GRADE : Grade
#    CUBEEXPORT_LUT1OPTIONS_OUTPUT : Output Transform
if sys.version_info[0] >= 3:
    class CUBEEXPORT_LUT1OPTIONS(enum.Enum):
        CUBEEXPORT_LUT1OPTIONS_INPUT="Input"
        CUBEEXPORT_LUT1OPTIONS_GRADE="Grade"
        CUBEEXPORT_LUT1OPTIONS_OUTPUT="Output"
        def describe(self):
            descs = {
                CUBEEXPORT_LUT1OPTIONS.CUBEEXPORT_LUT1OPTIONS_INPUT: "Input Transform",
                CUBEEXPORT_LUT1OPTIONS.CUBEEXPORT_LUT1OPTIONS_GRADE: "Grade",
                CUBEEXPORT_LUT1OPTIONS.CUBEEXPORT_LUT1OPTIONS_OUTPUT: "Output Transform",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_LUT1OPTIONS}

CUBEEXPORT_LUT1OPTIONS_INPUT="Input"
CUBEEXPORT_LUT1OPTIONS_GRADE="Grade"
CUBEEXPORT_LUT1OPTIONS_OUTPUT="Output"
#  CUBEEXPORT_LUT2OPTIONS : Values for CubeExportSettings LUT2Options
#    CUBEEXPORT_LUT2OPTIONS_INPUT : Input Transform
#    CUBEEXPORT_LUT2OPTIONS_GRADE : Grade
#    CUBEEXPORT_LUT2OPTIONS_OUTPUT : Output Transform
if sys.version_info[0] >= 3:
    class CUBEEXPORT_LUT2OPTIONS(enum.Enum):
        CUBEEXPORT_LUT2OPTIONS_INPUT="Input"
        CUBEEXPORT_LUT2OPTIONS_GRADE="Grade"
        CUBEEXPORT_LUT2OPTIONS_OUTPUT="Output"
        def describe(self):
            descs = {
                CUBEEXPORT_LUT2OPTIONS.CUBEEXPORT_LUT2OPTIONS_INPUT: "Input Transform",
                CUBEEXPORT_LUT2OPTIONS.CUBEEXPORT_LUT2OPTIONS_GRADE: "Grade",
                CUBEEXPORT_LUT2OPTIONS.CUBEEXPORT_LUT2OPTIONS_OUTPUT: "Output Transform",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_LUT2OPTIONS}

CUBEEXPORT_LUT2OPTIONS_INPUT="Input"
CUBEEXPORT_LUT2OPTIONS_GRADE="Grade"
CUBEEXPORT_LUT2OPTIONS_OUTPUT="Output"
#  CUBEEXPORT_LUT3OPTIONS : Values for CubeExportSettings LUT3Options
#    CUBEEXPORT_LUT3OPTIONS_INPUT : Input Transform
#    CUBEEXPORT_LUT3OPTIONS_GRADE : Grade
#    CUBEEXPORT_LUT3OPTIONS_OUTPUT : Output Transform
if sys.version_info[0] >= 3:
    class CUBEEXPORT_LUT3OPTIONS(enum.Enum):
        CUBEEXPORT_LUT3OPTIONS_INPUT="Input"
        CUBEEXPORT_LUT3OPTIONS_GRADE="Grade"
        CUBEEXPORT_LUT3OPTIONS_OUTPUT="Output"
        def describe(self):
            descs = {
                CUBEEXPORT_LUT3OPTIONS.CUBEEXPORT_LUT3OPTIONS_INPUT: "Input Transform",
                CUBEEXPORT_LUT3OPTIONS.CUBEEXPORT_LUT3OPTIONS_GRADE: "Grade",
                CUBEEXPORT_LUT3OPTIONS.CUBEEXPORT_LUT3OPTIONS_OUTPUT: "Output Transform",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_LUT3OPTIONS}

CUBEEXPORT_LUT3OPTIONS_INPUT="Input"
CUBEEXPORT_LUT3OPTIONS_GRADE="Grade"
CUBEEXPORT_LUT3OPTIONS_OUTPUT="Output"
#  CUBEEXPORT_LUTFORMAT : Values for CubeExportSettings LUTFormat
#    CUBEEXPORT_LUTFORMAT_TRUELIGHT : Truelight cube
#    CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D : Truelight 1D
#    CUBEEXPORT_LUTFORMAT_AMIRA : AMIRA
#    CUBEEXPORT_LUTFORMAT_ARRI : Arri
#    CUBEEXPORT_LUTFORMAT_AUTODESK : Autodesk
#    CUBEEXPORT_LUTFORMAT_AUTODESK_1D : Autodesk 1D
#    CUBEEXPORT_LUTFORMAT_AUTODESK_1DF : Autodesk 1D half float
#    CUBEEXPORT_LUTFORMAT_AUTODESK_MESH : Autodesk Lustre (Mesh)
#    CUBEEXPORT_LUTFORMAT_AUTODESK_CTF : Autodesk CTF
#    CUBEEXPORT_LUTFORMAT_BMD : BMD
#    CUBEEXPORT_LUTFORMAT_BARCO : Barco
#    CUBEEXPORT_LUTFORMAT_BLACKMAGIC : BlackMagic
#    CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D : BlackMagic 1D
#    CUBEEXPORT_LUTFORMAT_CANON_1D : Canon gamma 1D
#    CUBEEXPORT_LUTFORMAT_CANON_3D : Canon gamut 3D
#    CUBEEXPORT_LUTFORMAT_CINESPACE : CineSpace
#    CUBEEXPORT_LUTFORMAT_COLORFRONT_1D : Colorfront 1D
#    CUBEEXPORT_LUTFORMAT_COLORFRONT_3D : Colorfront 3D
#    CUBEEXPORT_LUTFORMAT_DVS : DVS
#    CUBEEXPORT_LUTFORMAT_DVS_1D : DVS 1D
#    CUBEEXPORT_LUTFORMAT_DAVINCI : DaVinci
#    CUBEEXPORT_LUTFORMAT_EVERTZ : Evertz
#    CUBEEXPORT_LUTFORMAT_ICC : ICC
#    CUBEEXPORT_LUTFORMAT_IRIDAS : IRIDAS
#    CUBEEXPORT_LUTFORMAT_IRIDAS_1D : IRIDAS 1D
#    CUBEEXPORT_LUTFORMAT_LUTHER : LUTher
#    CUBEEXPORT_LUTFORMAT_NUCODA : Nucoda
#    CUBEEXPORT_LUTFORMAT_PANASONIC : Panasonic
#    CUBEEXPORT_LUTFORMAT_PANDORA : Pandora
#    CUBEEXPORT_LUTFORMAT_QUANTEL : Quantel
#    CUBEEXPORT_LUTFORMAT_QUANTEL_65 : Quantel 65x65x65
#    CUBEEXPORT_LUTFORMAT_SCRATCH : Scratch
#    CUBEEXPORT_LUTFORMAT_SONY : Sony
#    CUBEEXPORT_LUTFORMAT_SONY_BVME : Sony BVME
if sys.version_info[0] >= 3:
    class CUBEEXPORT_LUTFORMAT(enum.Enum):
        CUBEEXPORT_LUTFORMAT_TRUELIGHT="Truelight"
        CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D="Truelight_1D"
        CUBEEXPORT_LUTFORMAT_AMIRA="AMIRA"
        CUBEEXPORT_LUTFORMAT_ARRI="Arri"
        CUBEEXPORT_LUTFORMAT_AUTODESK="Autodesk"
        CUBEEXPORT_LUTFORMAT_AUTODESK_1D="Autodesk_1D"
        CUBEEXPORT_LUTFORMAT_AUTODESK_1DF="Autodesk_1Df"
        CUBEEXPORT_LUTFORMAT_AUTODESK_MESH="Autodesk_Mesh"
        CUBEEXPORT_LUTFORMAT_AUTODESK_CTF="Autodesk_ctf"
        CUBEEXPORT_LUTFORMAT_BMD="BMD"
        CUBEEXPORT_LUTFORMAT_BARCO="Barco"
        CUBEEXPORT_LUTFORMAT_BLACKMAGIC="BlackMagic"
        CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D="BlackMagic_1D"
        CUBEEXPORT_LUTFORMAT_CANON_1D="Canon_1D"
        CUBEEXPORT_LUTFORMAT_CANON_3D="Canon_3D"
        CUBEEXPORT_LUTFORMAT_CINESPACE="CineSpace"
        CUBEEXPORT_LUTFORMAT_COLORFRONT_1D="Colorfront_1D"
        CUBEEXPORT_LUTFORMAT_COLORFRONT_3D="Colorfront_3D"
        CUBEEXPORT_LUTFORMAT_DVS="DVS"
        CUBEEXPORT_LUTFORMAT_DVS_1D="DVS_1D"
        CUBEEXPORT_LUTFORMAT_DAVINCI="DaVinci"
        CUBEEXPORT_LUTFORMAT_EVERTZ="Evertz"
        CUBEEXPORT_LUTFORMAT_ICC="ICC"
        CUBEEXPORT_LUTFORMAT_IRIDAS="IRIDAS"
        CUBEEXPORT_LUTFORMAT_IRIDAS_1D="IRIDAS_1D"
        CUBEEXPORT_LUTFORMAT_LUTHER="LUTher"
        CUBEEXPORT_LUTFORMAT_NUCODA="Nucoda"
        CUBEEXPORT_LUTFORMAT_PANASONIC="Panasonic"
        CUBEEXPORT_LUTFORMAT_PANDORA="Pandora"
        CUBEEXPORT_LUTFORMAT_QUANTEL="Quantel"
        CUBEEXPORT_LUTFORMAT_QUANTEL_65="Quantel_65"
        CUBEEXPORT_LUTFORMAT_SCRATCH="Scratch"
        CUBEEXPORT_LUTFORMAT_SONY="Sony"
        CUBEEXPORT_LUTFORMAT_SONY_BVME="Sony_BVME"
        def describe(self):
            descs = {
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_TRUELIGHT: "Truelight cube",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D: "Truelight 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AMIRA: "AMIRA",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_ARRI: "Arri",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AUTODESK: "Autodesk",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AUTODESK_1D: "Autodesk 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AUTODESK_1DF: "Autodesk 1D half float",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AUTODESK_MESH: "Autodesk Lustre (Mesh)",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_AUTODESK_CTF: "Autodesk CTF",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_BMD: "BMD",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_BARCO: "Barco",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_BLACKMAGIC: "BlackMagic",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D: "BlackMagic 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_CANON_1D: "Canon gamma 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_CANON_3D: "Canon gamut 3D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_CINESPACE: "CineSpace",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_COLORFRONT_1D: "Colorfront 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_COLORFRONT_3D: "Colorfront 3D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_DVS: "DVS",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_DVS_1D: "DVS 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_DAVINCI: "DaVinci",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_EVERTZ: "Evertz",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_ICC: "ICC",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_IRIDAS: "IRIDAS",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_IRIDAS_1D: "IRIDAS 1D",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_LUTHER: "LUTher",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_NUCODA: "Nucoda",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_PANASONIC: "Panasonic",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_PANDORA: "Pandora",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_QUANTEL: "Quantel",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_QUANTEL_65: "Quantel 65x65x65",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_SCRATCH: "Scratch",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_SONY: "Sony",
                CUBEEXPORT_LUTFORMAT.CUBEEXPORT_LUTFORMAT_SONY_BVME: "Sony BVME",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_LUTFORMAT}

CUBEEXPORT_LUTFORMAT_TRUELIGHT="Truelight"
CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D="Truelight_1D"
CUBEEXPORT_LUTFORMAT_AMIRA="AMIRA"
CUBEEXPORT_LUTFORMAT_ARRI="Arri"
CUBEEXPORT_LUTFORMAT_AUTODESK="Autodesk"
CUBEEXPORT_LUTFORMAT_AUTODESK_1D="Autodesk_1D"
CUBEEXPORT_LUTFORMAT_AUTODESK_1DF="Autodesk_1Df"
CUBEEXPORT_LUTFORMAT_AUTODESK_MESH="Autodesk_Mesh"
CUBEEXPORT_LUTFORMAT_AUTODESK_CTF="Autodesk_ctf"
CUBEEXPORT_LUTFORMAT_BMD="BMD"
CUBEEXPORT_LUTFORMAT_BARCO="Barco"
CUBEEXPORT_LUTFORMAT_BLACKMAGIC="BlackMagic"
CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D="BlackMagic_1D"
CUBEEXPORT_LUTFORMAT_CANON_1D="Canon_1D"
CUBEEXPORT_LUTFORMAT_CANON_3D="Canon_3D"
CUBEEXPORT_LUTFORMAT_CINESPACE="CineSpace"
CUBEEXPORT_LUTFORMAT_COLORFRONT_1D="Colorfront_1D"
CUBEEXPORT_LUTFORMAT_COLORFRONT_3D="Colorfront_3D"
CUBEEXPORT_LUTFORMAT_DVS="DVS"
CUBEEXPORT_LUTFORMAT_DVS_1D="DVS_1D"
CUBEEXPORT_LUTFORMAT_DAVINCI="DaVinci"
CUBEEXPORT_LUTFORMAT_EVERTZ="Evertz"
CUBEEXPORT_LUTFORMAT_ICC="ICC"
CUBEEXPORT_LUTFORMAT_IRIDAS="IRIDAS"
CUBEEXPORT_LUTFORMAT_IRIDAS_1D="IRIDAS_1D"
CUBEEXPORT_LUTFORMAT_LUTHER="LUTher"
CUBEEXPORT_LUTFORMAT_NUCODA="Nucoda"
CUBEEXPORT_LUTFORMAT_PANASONIC="Panasonic"
CUBEEXPORT_LUTFORMAT_PANDORA="Pandora"
CUBEEXPORT_LUTFORMAT_QUANTEL="Quantel"
CUBEEXPORT_LUTFORMAT_QUANTEL_65="Quantel_65"
CUBEEXPORT_LUTFORMAT_SCRATCH="Scratch"
CUBEEXPORT_LUTFORMAT_SONY="Sony"
CUBEEXPORT_LUTFORMAT_SONY_BVME="Sony_BVME"
#  CUBEEXPORT_LUTRESOLUTION : Values for CubeExportSettings LUTResolution
#    CUBEEXPORT_LUTRESOLUTION_DEFAULT : Default
#    CUBEEXPORT_LUTRESOLUTION_1024 : 1024
#    CUBEEXPORT_LUTRESOLUTION_4096 : 4096
#    CUBEEXPORT_LUTRESOLUTION_16384 : 16384
if sys.version_info[0] >= 3:
    class CUBEEXPORT_LUTRESOLUTION(enum.Enum):
        CUBEEXPORT_LUTRESOLUTION_DEFAULT=-1
        CUBEEXPORT_LUTRESOLUTION_1024=1024
        CUBEEXPORT_LUTRESOLUTION_4096=4096
        CUBEEXPORT_LUTRESOLUTION_16384=16384
        def describe(self):
            descs = {
                CUBEEXPORT_LUTRESOLUTION.CUBEEXPORT_LUTRESOLUTION_DEFAULT: "Default",
                CUBEEXPORT_LUTRESOLUTION.CUBEEXPORT_LUTRESOLUTION_1024: "1024",
                CUBEEXPORT_LUTRESOLUTION.CUBEEXPORT_LUTRESOLUTION_4096: "4096",
                CUBEEXPORT_LUTRESOLUTION.CUBEEXPORT_LUTRESOLUTION_16384: "16384",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_LUTRESOLUTION}

CUBEEXPORT_LUTRESOLUTION_DEFAULT=-1
CUBEEXPORT_LUTRESOLUTION_1024=1024
CUBEEXPORT_LUTRESOLUTION_4096=4096
CUBEEXPORT_LUTRESOLUTION_16384=16384
#  CUBEEXPORT_NUMLUTS : Values for CubeExportSettings NumLUTs
#    CUBEEXPORT_NUMLUTS_1 : 1
#    CUBEEXPORT_NUMLUTS_2 : 2
#    CUBEEXPORT_NUMLUTS_3 : 3
if sys.version_info[0] >= 3:
    class CUBEEXPORT_NUMLUTS(enum.Enum):
        CUBEEXPORT_NUMLUTS_1=1
        CUBEEXPORT_NUMLUTS_2=2
        CUBEEXPORT_NUMLUTS_3=3
        def describe(self):
            descs = {
                CUBEEXPORT_NUMLUTS.CUBEEXPORT_NUMLUTS_1: "1",
                CUBEEXPORT_NUMLUTS.CUBEEXPORT_NUMLUTS_2: "2",
                CUBEEXPORT_NUMLUTS.CUBEEXPORT_NUMLUTS_3: "3",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in CUBEEXPORT_NUMLUTS}

CUBEEXPORT_NUMLUTS_1=1
CUBEEXPORT_NUMLUTS_2=2
CUBEEXPORT_NUMLUTS_3=3
#  DECODEPARAM_TYPE : Data type for a DecodeParameterDefinition
#    DECODEPARAMTYPE_INTEGER : Integer value
#    DECODEPARAMTYPE_FLOAT : Floating-point value
#    DECODEPARAMTYPE_BOOLEAN : Boolean value, represented as 1 or 0
#    DECODEPARAMTYPE_CHOICE : A choice for a set of discrete values
#    DECODEPARAMTYPE_FILE : Filename or path to a file
if sys.version_info[0] >= 3:
    class DECODEPARAM_TYPE(enum.Enum):
        DECODEPARAMTYPE_INTEGER="Integer"
        DECODEPARAMTYPE_FLOAT="Float"
        DECODEPARAMTYPE_BOOLEAN="Boolean"
        DECODEPARAMTYPE_CHOICE="Choice"
        DECODEPARAMTYPE_FILE="File"
        def describe(self):
            descs = {
                DECODEPARAM_TYPE.DECODEPARAMTYPE_INTEGER: "Integer value",
                DECODEPARAM_TYPE.DECODEPARAMTYPE_FLOAT: "Floating-point value",
                DECODEPARAM_TYPE.DECODEPARAMTYPE_BOOLEAN: "Boolean value, represented as 1 or 0",
                DECODEPARAM_TYPE.DECODEPARAMTYPE_CHOICE: "A choice for a set of discrete values",
                DECODEPARAM_TYPE.DECODEPARAMTYPE_FILE: "Filename or path to a file",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in DECODEPARAM_TYPE}

DECODEPARAMTYPE_INTEGER="Integer"
DECODEPARAMTYPE_FLOAT="Float"
DECODEPARAMTYPE_BOOLEAN="Boolean"
DECODEPARAMTYPE_CHOICE="Choice"
DECODEPARAMTYPE_FILE="File"
#  DECODEQUALITY : Decode Qulity to use for decoding source images for RAW codecs
#    DECODEQUALITY_HIGH : Use highest quality RAW decode
#    DECODEQUALITY_OPTIMISED : Use nearest decode quality for render format/resolution
#    DECODEQUALITY_DRAFT : Use fastest decode quality
if sys.version_info[0] >= 3:
    class DECODEQUALITY(enum.Enum):
        DECODEQUALITY_HIGH="GMDQ_OPTIMISED_UNLESS_HIGH"
        DECODEQUALITY_OPTIMISED="GMDQ_OPTIMISED"
        DECODEQUALITY_DRAFT="GMDQ_DRAFT"
        def describe(self):
            descs = {
                DECODEQUALITY.DECODEQUALITY_HIGH: "Use highest quality RAW decode",
                DECODEQUALITY.DECODEQUALITY_OPTIMISED: "Use nearest decode quality for render format/resolution",
                DECODEQUALITY.DECODEQUALITY_DRAFT: "Use fastest decode quality",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in DECODEQUALITY}

DECODEQUALITY_HIGH="GMDQ_OPTIMISED_UNLESS_HIGH"
DECODEQUALITY_OPTIMISED="GMDQ_OPTIMISED"
DECODEQUALITY_DRAFT="GMDQ_DRAFT"
#  DIAGSTATUS : Status of diagnostic test
#    DIAG_READY : Ready to run
#    DIAG_WAITING : Waiting on pre-requisite test to complete
#    DIAG_RUNNING : Test is running
#    DIAG_PASS : Diagnostic passed
#    DIAG_WARNING : Diagnostic completed with warnings
#    DIAG_FAILED : Diagnostiic test failed
#    DIAG_SKIP : Skipped
if sys.version_info[0] >= 3:
    class DIAGSTATUS(enum.Enum):
        DIAG_READY="ready"
        DIAG_WAITING="waiting"
        DIAG_RUNNING="running"
        DIAG_PASS="pass"
        DIAG_WARNING="warning"
        DIAG_FAILED="failed"
        DIAG_SKIP="skipped"
        def describe(self):
            descs = {
                DIAGSTATUS.DIAG_READY: "Ready to run",
                DIAGSTATUS.DIAG_WAITING: "Waiting on pre-requisite test to complete",
                DIAGSTATUS.DIAG_RUNNING: "Test is running",
                DIAGSTATUS.DIAG_PASS: "Diagnostic passed",
                DIAGSTATUS.DIAG_WARNING: "Diagnostic completed with warnings",
                DIAGSTATUS.DIAG_FAILED: "Diagnostiic test failed",
                DIAGSTATUS.DIAG_SKIP: "Skipped",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in DIAGSTATUS}

DIAG_READY="ready"
DIAG_WAITING="waiting"
DIAG_RUNNING="running"
DIAG_PASS="pass"
DIAG_WARNING="warning"
DIAG_FAILED="failed"
DIAG_SKIP="skipped"
#  DIAGWEIGHT : Weight of test
#    DIAGWEIGHT_LIGHT : Light tests
#    DIAGWEIGHT_MEDIUM : Medium tests
#    DIAGWEIGHT_HEAVY : Heavy tests
if sys.version_info[0] >= 3:
    class DIAGWEIGHT(enum.Enum):
        DIAGWEIGHT_LIGHT="DM_LIGHT"
        DIAGWEIGHT_MEDIUM="DM_MEDIUM"
        DIAGWEIGHT_HEAVY="DM_HEAVY"
        def describe(self):
            descs = {
                DIAGWEIGHT.DIAGWEIGHT_LIGHT: "Light tests",
                DIAGWEIGHT.DIAGWEIGHT_MEDIUM: "Medium tests",
                DIAGWEIGHT.DIAGWEIGHT_HEAVY: "Heavy tests",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in DIAGWEIGHT}

DIAGWEIGHT_LIGHT="DM_LIGHT"
DIAGWEIGHT_MEDIUM="DM_MEDIUM"
DIAGWEIGHT_HEAVY="DM_HEAVY"
#  DIALOG_ITEM_TYPE : Type for a DynamicDialogItem used in a DynamicDialog
#    DIT_STRING : String
#    DIT_INTEGER : Integer
#    DIT_FLOAT : Floating-point number
#    DIT_TIMECODE : Timecode
#    DIT_DROPDOWN : Dropdown
#    DIT_LIST : List of items
#    DIT_TOGGLE : Toggle Button
#    DIT_TOGGLE_SET : Set of Toggle buttons
#    DIT_TOGGLE_DROPDOWN : Dropdown menu to allow toggling multiple items
#    DIT_TOGGLE_LIST : List of toggle items
#    DIT_RADIO_GROUP : Set of radio buttons
#    DIT_FILEPATH : File Path
#    DIT_IMAGEPATH : Image Path
#    DIT_DIRECTORY : Directory Path
#    DIT_SHOT_SELECTION : Shot Selection
#    DIT_STATIC_TEXT : Static Text
#    DIT_SHOT_CATEGORY : Shot Category
#    DIT_SHOT_CATEGORY_SET : Shot Category Set
#    DIT_MARK_CATEGORY : Shot Category
#    DIT_MARK_CATEGORY_SET : Mark Category Set
if sys.version_info[0] >= 3:
    class DIALOG_ITEM_TYPE(enum.Enum):
        DIT_STRING="String"
        DIT_INTEGER="Integer"
        DIT_FLOAT="Float"
        DIT_TIMECODE="Timecode"
        DIT_DROPDOWN="Dropdown"
        DIT_LIST="List"
        DIT_TOGGLE="Toggle"
        DIT_TOGGLE_SET="ToggleSet"
        DIT_TOGGLE_DROPDOWN="ToggleDropdown"
        DIT_TOGGLE_LIST="ToggleList"
        DIT_RADIO_GROUP="RadioGroup"
        DIT_FILEPATH="File"
        DIT_IMAGEPATH="Image"
        DIT_DIRECTORY="Directory"
        DIT_SHOT_SELECTION="ShotSelection"
        DIT_STATIC_TEXT="StaticText"
        DIT_SHOT_CATEGORY="ShotCategory"
        DIT_SHOT_CATEGORY_SET="CategorySet"
        DIT_MARK_CATEGORY="MarkCategory"
        DIT_MARK_CATEGORY_SET="MarkCategorySet"
        def describe(self):
            descs = {
                DIALOG_ITEM_TYPE.DIT_STRING: "String",
                DIALOG_ITEM_TYPE.DIT_INTEGER: "Integer",
                DIALOG_ITEM_TYPE.DIT_FLOAT: "Floating-point number",
                DIALOG_ITEM_TYPE.DIT_TIMECODE: "Timecode",
                DIALOG_ITEM_TYPE.DIT_DROPDOWN: "Dropdown",
                DIALOG_ITEM_TYPE.DIT_LIST: "List of items",
                DIALOG_ITEM_TYPE.DIT_TOGGLE: "Toggle Button",
                DIALOG_ITEM_TYPE.DIT_TOGGLE_SET: "Set of Toggle buttons",
                DIALOG_ITEM_TYPE.DIT_TOGGLE_DROPDOWN: "Dropdown menu to allow toggling multiple items",
                DIALOG_ITEM_TYPE.DIT_TOGGLE_LIST: "List of toggle items",
                DIALOG_ITEM_TYPE.DIT_RADIO_GROUP: "Set of radio buttons",
                DIALOG_ITEM_TYPE.DIT_FILEPATH: "File Path",
                DIALOG_ITEM_TYPE.DIT_IMAGEPATH: "Image Path",
                DIALOG_ITEM_TYPE.DIT_DIRECTORY: "Directory Path",
                DIALOG_ITEM_TYPE.DIT_SHOT_SELECTION: "Shot Selection",
                DIALOG_ITEM_TYPE.DIT_STATIC_TEXT: "Static Text",
                DIALOG_ITEM_TYPE.DIT_SHOT_CATEGORY: "Shot Category",
                DIALOG_ITEM_TYPE.DIT_SHOT_CATEGORY_SET: "Shot Category Set",
                DIALOG_ITEM_TYPE.DIT_MARK_CATEGORY: "Shot Category",
                DIALOG_ITEM_TYPE.DIT_MARK_CATEGORY_SET: "Mark Category Set",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in DIALOG_ITEM_TYPE}

DIT_STRING="String"
DIT_INTEGER="Integer"
DIT_FLOAT="Float"
DIT_TIMECODE="Timecode"
DIT_DROPDOWN="Dropdown"
DIT_LIST="List"
DIT_TOGGLE="Toggle"
DIT_TOGGLE_SET="ToggleSet"
DIT_TOGGLE_DROPDOWN="ToggleDropdown"
DIT_TOGGLE_LIST="ToggleList"
DIT_RADIO_GROUP="RadioGroup"
DIT_FILEPATH="File"
DIT_IMAGEPATH="Image"
DIT_DIRECTORY="Directory"
DIT_SHOT_SELECTION="ShotSelection"
DIT_STATIC_TEXT="StaticText"
DIT_SHOT_CATEGORY="ShotCategory"
DIT_SHOT_CATEGORY_SET="CategorySet"
DIT_MARK_CATEGORY="MarkCategory"
DIT_MARK_CATEGORY_SET="MarkCategorySet"
#  EXPORTSTATUS : Status info related to Export progress
#    EXPORTSTATUS_FAIL : Failure during export operation
#    EXPORTSTATUS_WARN : Warning during export operation
#    EXPORTSTATUS_INFO : Info from export operation
#    EXPORTSTATUS_NOTE : Note from export operation
#    EXPORTSTATUS_SCAN : Filesystem scanning progress
if sys.version_info[0] >= 3:
    class EXPORTSTATUS(enum.Enum):
        EXPORTSTATUS_FAIL="FAIL"
        EXPORTSTATUS_WARN="WARN"
        EXPORTSTATUS_INFO="INFO"
        EXPORTSTATUS_NOTE="NOTE"
        EXPORTSTATUS_SCAN="SCAN"
        def describe(self):
            descs = {
                EXPORTSTATUS.EXPORTSTATUS_FAIL: "Failure during export operation",
                EXPORTSTATUS.EXPORTSTATUS_WARN: "Warning during export operation",
                EXPORTSTATUS.EXPORTSTATUS_INFO: "Info from export operation",
                EXPORTSTATUS.EXPORTSTATUS_NOTE: "Note from export operation",
                EXPORTSTATUS.EXPORTSTATUS_SCAN: "Filesystem scanning progress",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORTSTATUS}

EXPORTSTATUS_FAIL="FAIL"
EXPORTSTATUS_WARN="WARN"
EXPORTSTATUS_INFO="INFO"
EXPORTSTATUS_NOTE="NOTE"
EXPORTSTATUS_SCAN="SCAN"
#  EXPORTTYPE : Type of Exporter
#    EXPORTTYPE_STILL : Stills Exporter
#    EXPORTTYPE_BLG : BLG Exporter
#    EXPORTTYPE_CUBE : Cube Exporter
#    EXPORTTYPE_CDL : CDL Exporter
if sys.version_info[0] >= 3:
    class EXPORTTYPE(enum.Enum):
        EXPORTTYPE_STILL="Still"
        EXPORTTYPE_BLG="BLG"
        EXPORTTYPE_CUBE="Cube"
        EXPORTTYPE_CDL="CDL"
        def describe(self):
            descs = {
                EXPORTTYPE.EXPORTTYPE_STILL: "Stills Exporter",
                EXPORTTYPE.EXPORTTYPE_BLG: "BLG Exporter",
                EXPORTTYPE.EXPORTTYPE_CUBE: "Cube Exporter",
                EXPORTTYPE.EXPORTTYPE_CDL: "CDL Exporter",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORTTYPE}

EXPORTTYPE_STILL="Still"
EXPORTTYPE_BLG="BLG"
EXPORTTYPE_CUBE="Cube"
EXPORTTYPE_CDL="CDL"
#  EXPORT_CATEGORYMATCH : Values for Exporter CategoryMatch field
#    EXPORT_CATEGORYMATCH_ALL : All Categories
#    EXPORT_CATEGORYMATCH_ANY : Any Category
if sys.version_info[0] >= 3:
    class EXPORT_CATEGORYMATCH(enum.Enum):
        EXPORT_CATEGORYMATCH_ALL="all"
        EXPORT_CATEGORYMATCH_ANY="any"
        def describe(self):
            descs = {
                EXPORT_CATEGORYMATCH.EXPORT_CATEGORYMATCH_ALL: "All Categories",
                EXPORT_CATEGORYMATCH.EXPORT_CATEGORYMATCH_ANY: "Any Category",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORT_CATEGORYMATCH}

EXPORT_CATEGORYMATCH_ALL="all"
EXPORT_CATEGORYMATCH_ANY="any"
#  EXPORT_FRAMES : Values for Exporter Frames field
#    EXPORT_FRAMES_FIRST : First Frame
#    EXPORT_FRAMES_POSTER : Poster Frame
#    EXPORT_FRAMES_MARKED : Marked Frames
#    EXPORT_FRAMES_CURRENT : Current Frame
if sys.version_info[0] >= 3:
    class EXPORT_FRAMES(enum.Enum):
        EXPORT_FRAMES_FIRST="First"
        EXPORT_FRAMES_POSTER="Poster"
        EXPORT_FRAMES_MARKED="Marked"
        EXPORT_FRAMES_CURRENT="Current"
        def describe(self):
            descs = {
                EXPORT_FRAMES.EXPORT_FRAMES_FIRST: "First Frame",
                EXPORT_FRAMES.EXPORT_FRAMES_POSTER: "Poster Frame",
                EXPORT_FRAMES.EXPORT_FRAMES_MARKED: "Marked Frames",
                EXPORT_FRAMES.EXPORT_FRAMES_CURRENT: "Current Frame",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORT_FRAMES}

EXPORT_FRAMES_FIRST="First"
EXPORT_FRAMES_POSTER="Poster"
EXPORT_FRAMES_MARKED="Marked"
EXPORT_FRAMES_CURRENT="Current"
#  EXPORT_OVERWRITE : Values for Exporter Overwrite field
#    EXPORT_OVERWRITE_SKIP : Skip
#    EXPORT_OVERWRITE_REPLACE : Replace
if sys.version_info[0] >= 3:
    class EXPORT_OVERWRITE(enum.Enum):
        EXPORT_OVERWRITE_SKIP="Skip"
        EXPORT_OVERWRITE_REPLACE="Replace"
        def describe(self):
            descs = {
                EXPORT_OVERWRITE.EXPORT_OVERWRITE_SKIP: "Skip",
                EXPORT_OVERWRITE.EXPORT_OVERWRITE_REPLACE: "Replace",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORT_OVERWRITE}

EXPORT_OVERWRITE_SKIP="Skip"
EXPORT_OVERWRITE_REPLACE="Replace"
#  EXPORT_SOURCE : Values for Exporter Source field
#    EXPORT_SOURCE_ALLSHOTS : All Shots
#    EXPORT_SOURCE_SELECTEDSHOTS : Selected Shots
#    EXPORT_SOURCE_CURRENTSHOT : Current Shot
#    EXPORT_SOURCE_SHOTSINFILTER : Shots in Filter
#    EXPORT_SOURCE_SHOTSOFCATEGORY : Shots of Category
if sys.version_info[0] >= 3:
    class EXPORT_SOURCE(enum.Enum):
        EXPORT_SOURCE_ALLSHOTS="AllShots"
        EXPORT_SOURCE_SELECTEDSHOTS="SelectedShots"
        EXPORT_SOURCE_CURRENTSHOT="CurrentShot"
        EXPORT_SOURCE_SHOTSINFILTER="ShotsInFilter"
        EXPORT_SOURCE_SHOTSOFCATEGORY="ShotsOfCategory"
        def describe(self):
            descs = {
                EXPORT_SOURCE.EXPORT_SOURCE_ALLSHOTS: "All Shots",
                EXPORT_SOURCE.EXPORT_SOURCE_SELECTEDSHOTS: "Selected Shots",
                EXPORT_SOURCE.EXPORT_SOURCE_CURRENTSHOT: "Current Shot",
                EXPORT_SOURCE.EXPORT_SOURCE_SHOTSINFILTER: "Shots in Filter",
                EXPORT_SOURCE.EXPORT_SOURCE_SHOTSOFCATEGORY: "Shots of Category",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORT_SOURCE}

EXPORT_SOURCE_ALLSHOTS="AllShots"
EXPORT_SOURCE_SELECTEDSHOTS="SelectedShots"
EXPORT_SOURCE_CURRENTSHOT="CurrentShot"
EXPORT_SOURCE_SHOTSINFILTER="ShotsInFilter"
EXPORT_SOURCE_SHOTSOFCATEGORY="ShotsOfCategory"
#  EXPORT_STEREO : Values for Exporter Stereo field
#    EXPORT_STEREO_CURRENT : Current Eye
#    EXPORT_STEREO_LEFT : Left Eye
#    EXPORT_STEREO_RIGHT : Right Eye
#    EXPORT_STEREO_BOTH : Left & Right Eyes
#    EXPORT_STEREO_SINGLESTACKSTEREO : Single Stack Stereo (BLG exports only)
if sys.version_info[0] >= 3:
    class EXPORT_STEREO(enum.Enum):
        EXPORT_STEREO_CURRENT="Current"
        EXPORT_STEREO_LEFT="Left"
        EXPORT_STEREO_RIGHT="Right"
        EXPORT_STEREO_BOTH="Both"
        EXPORT_STEREO_SINGLESTACKSTEREO="SingleStackStereo"
        def describe(self):
            descs = {
                EXPORT_STEREO.EXPORT_STEREO_CURRENT: "Current Eye",
                EXPORT_STEREO.EXPORT_STEREO_LEFT: "Left Eye",
                EXPORT_STEREO.EXPORT_STEREO_RIGHT: "Right Eye",
                EXPORT_STEREO.EXPORT_STEREO_BOTH: "Left & Right Eyes",
                EXPORT_STEREO.EXPORT_STEREO_SINGLESTACKSTEREO: "Single Stack Stereo (BLG exports only)",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in EXPORT_STEREO}

EXPORT_STEREO_CURRENT="Current"
EXPORT_STEREO_LEFT="Left"
EXPORT_STEREO_RIGHT="Right"
EXPORT_STEREO_BOTH="Both"
EXPORT_STEREO_SINGLESTACKSTEREO="SingleStackStereo"
#  FIELDORDER : Field order behaviour
#    FIELDORDER_PROGRESSIVE : Progressive
#    FIELDORDER_UPPER : Upper-field first (PAL/SECAM)
#    FIELDORDER_LOWER : Lower-field first (NTSC)
if sys.version_info[0] >= 3:
    class FIELDORDER(enum.Enum):
        FIELDORDER_PROGRESSIVE="None"
        FIELDORDER_UPPER="upper"
        FIELDORDER_LOWER="lower"
        def describe(self):
            descs = {
                FIELDORDER.FIELDORDER_PROGRESSIVE: "Progressive",
                FIELDORDER.FIELDORDER_UPPER: "Upper-field first (PAL/SECAM)",
                FIELDORDER.FIELDORDER_LOWER: "Lower-field first (NTSC)",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in FIELDORDER}

FIELDORDER_PROGRESSIVE="None"
FIELDORDER_UPPER="upper"
FIELDORDER_LOWER="lower"
#  FORMATSET_SCOPE : Defines the scope that a FormatSet is defined in
#    FORMATSET_SCOPE_FACTORY : Factory formats built-in to the software
#    FORMATSET_SCOPE_GLOBAL : Global Formats from the global formats database
#    FORMATSET_SCOPE_JOB : Formats defined for a given job in a database
#    FORMATSET_SCOPE_SCENE : Formats defined for a given scene
if sys.version_info[0] >= 3:
    class FORMATSET_SCOPE(enum.Enum):
        FORMATSET_SCOPE_FACTORY="factory"
        FORMATSET_SCOPE_GLOBAL="global"
        FORMATSET_SCOPE_JOB="job"
        FORMATSET_SCOPE_SCENE="scene"
        def describe(self):
            descs = {
                FORMATSET_SCOPE.FORMATSET_SCOPE_FACTORY: "Factory formats built-in to the software",
                FORMATSET_SCOPE.FORMATSET_SCOPE_GLOBAL: "Global Formats from the global formats database",
                FORMATSET_SCOPE.FORMATSET_SCOPE_JOB: "Formats defined for a given job in a database",
                FORMATSET_SCOPE.FORMATSET_SCOPE_SCENE: "Formats defined for a given scene",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in FORMATSET_SCOPE}

FORMATSET_SCOPE_FACTORY="factory"
FORMATSET_SCOPE_GLOBAL="global"
FORMATSET_SCOPE_JOB="job"
FORMATSET_SCOPE_SCENE="scene"
#  FSFILTER : Type of items to return from Filesystem get_items method
#    FSFILTER_FILE : Return files
#    FSFILTER_DIR : Return directories
if sys.version_info[0] >= 3:
    class FSFILTER(enum.Enum):
        FSFILTER_FILE="file"
        FSFILTER_DIR="directory"
        def describe(self):
            descs = {
                FSFILTER.FSFILTER_FILE: "Return files",
                FSFILTER.FSFILTER_DIR: "Return directories",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in FSFILTER}

FSFILTER_FILE="file"
FSFILTER_DIR="directory"
#  IMAGESEARCHER_METADATA_TRACK : Metadata track to use to group image files together into sequences
#    ISMT_FRAME_NUMBER : Collate frames into sequences based on frame number
#    ISMT_TIMECODE_1 : Collate frames into sequences based on Timecode 1
#    ISMT_TIMECODE_2 : Collate frames into sequences based on Timecode 2
#    ISMT_KEYCODE_1 : Collate frames into sequences based on Keycode
if sys.version_info[0] >= 3:
    class IMAGESEARCHER_METADATA_TRACK(enum.Enum):
        ISMT_FRAME_NUMBER="FSMT_FRAME_NUMBER"
        ISMT_TIMECODE_1="FSMT_TIMECODE_1"
        ISMT_TIMECODE_2="FSMT_TIMECODE_2"
        ISMT_KEYCODE_1="FSMT_KEYCODE_1"
        def describe(self):
            descs = {
                IMAGESEARCHER_METADATA_TRACK.ISMT_FRAME_NUMBER: "Collate frames into sequences based on frame number",
                IMAGESEARCHER_METADATA_TRACK.ISMT_TIMECODE_1: "Collate frames into sequences based on Timecode 1",
                IMAGESEARCHER_METADATA_TRACK.ISMT_TIMECODE_2: "Collate frames into sequences based on Timecode 2",
                IMAGESEARCHER_METADATA_TRACK.ISMT_KEYCODE_1: "Collate frames into sequences based on Keycode",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in IMAGESEARCHER_METADATA_TRACK}

ISMT_FRAME_NUMBER="FSMT_FRAME_NUMBER"
ISMT_TIMECODE_1="FSMT_TIMECODE_1"
ISMT_TIMECODE_2="FSMT_TIMECODE_2"
ISMT_KEYCODE_1="FSMT_KEYCODE_1"
#  IMAGETRANSFORM_MODE : Specify filtering kernel to use for image resampling/transform operations
#    IMAGETRANSFORM_ADAPTIVE : Adaptive
#    IMAGETRANSFORM_BOX : Square Average (Box filter)
#    IMAGETRANSFORM_CIRCLE : Circle average
#    IMAGETRANSFORM_COMPOSITE : Composite
#    IMAGETRANSFORM_CUBIC : Fixed Cubic
#    IMAGETRANSFORM_CUBIC_SPLINE : Fixed Cubic Spline
#    IMAGETRANSFORM_LANCZOS : Fixed Lanczos 4-tap
#    IMAGETRANSFORM_6LANCZOS : Fixed Lanczos 6-tap
#    IMAGETRANSFORM_6QUINTIC : Fixed Quintic 6-tap
#    IMAGETRANSFORM_GAUSSIAN : Fixed Gaussian
#    IMAGETRANSFORM_CATMULL_ROM : Fixed Catmull-Rom
#    IMAGETRANSFORM_SIMON : Fixed Simon
#    IMAGETRANSFORM_LINEAR : Fixed Linear
#    IMAGETRANSFORM_NEAREST : Fixed Nearest Pixel
#    IMAGETRANSFORM_SHARPEDGE : Sharp Edge
if sys.version_info[0] >= 3:
    class IMAGETRANSFORM_MODE(enum.Enum):
        IMAGETRANSFORM_ADAPTIVE="adaptive-soft"
        IMAGETRANSFORM_BOX="box"
        IMAGETRANSFORM_CIRCLE="circle"
        IMAGETRANSFORM_COMPOSITE="composite"
        IMAGETRANSFORM_CUBIC="cubic"
        IMAGETRANSFORM_CUBIC_SPLINE="cubic-spline"
        IMAGETRANSFORM_LANCZOS="Lanczos"
        IMAGETRANSFORM_6LANCZOS="6Lanczos"
        IMAGETRANSFORM_6QUINTIC="6quintic"
        IMAGETRANSFORM_GAUSSIAN="Gaussian"
        IMAGETRANSFORM_CATMULL_ROM="Catmull-Rom"
        IMAGETRANSFORM_SIMON="Simon"
        IMAGETRANSFORM_LINEAR="linear"
        IMAGETRANSFORM_NEAREST="nearest"
        IMAGETRANSFORM_SHARPEDGE="sharpEdge"
        def describe(self):
            descs = {
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_ADAPTIVE: "Adaptive",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_BOX: "Square Average (Box filter)",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_CIRCLE: "Circle average",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_COMPOSITE: "Composite",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_CUBIC: "Fixed Cubic",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_CUBIC_SPLINE: "Fixed Cubic Spline",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_LANCZOS: "Fixed Lanczos 4-tap",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_6LANCZOS: "Fixed Lanczos 6-tap",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_6QUINTIC: "Fixed Quintic 6-tap",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_GAUSSIAN: "Fixed Gaussian",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_CATMULL_ROM: "Fixed Catmull-Rom",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_SIMON: "Fixed Simon",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_LINEAR: "Fixed Linear",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_NEAREST: "Fixed Nearest Pixel",
                IMAGETRANSFORM_MODE.IMAGETRANSFORM_SHARPEDGE: "Sharp Edge",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in IMAGETRANSFORM_MODE}

IMAGETRANSFORM_ADAPTIVE="adaptive-soft"
IMAGETRANSFORM_BOX="box"
IMAGETRANSFORM_CIRCLE="circle"
IMAGETRANSFORM_COMPOSITE="composite"
IMAGETRANSFORM_CUBIC="cubic"
IMAGETRANSFORM_CUBIC_SPLINE="cubic-spline"
IMAGETRANSFORM_LANCZOS="Lanczos"
IMAGETRANSFORM_6LANCZOS="6Lanczos"
IMAGETRANSFORM_6QUINTIC="6quintic"
IMAGETRANSFORM_GAUSSIAN="Gaussian"
IMAGETRANSFORM_CATMULL_ROM="Catmull-Rom"
IMAGETRANSFORM_SIMON="Simon"
IMAGETRANSFORM_LINEAR="linear"
IMAGETRANSFORM_NEAREST="nearest"
IMAGETRANSFORM_SHARPEDGE="sharpEdge"
#  INSERT_POSITION : Specify where to insert a sequence in a Scene
#    INSERT_START : Insert sequence at start of scene
#    INSERT_END : Insert sequence at end of scene
#    INSERT_BEFORE : Insert sequence before specified Shot
#    INSERT_AFTER : Insert sequence after specified Shot
#    INSERT_ABOVE : Insert sequence above specified Shot
#    INSERT_BELOW : Insert sequence below specified Shot
if sys.version_info[0] >= 3:
    class INSERT_POSITION(enum.Enum):
        INSERT_START="start"
        INSERT_END="end"
        INSERT_BEFORE="before"
        INSERT_AFTER="after"
        INSERT_ABOVE="above"
        INSERT_BELOW="below"
        def describe(self):
            descs = {
                INSERT_POSITION.INSERT_START: "Insert sequence at start of scene",
                INSERT_POSITION.INSERT_END: "Insert sequence at end of scene",
                INSERT_POSITION.INSERT_BEFORE: "Insert sequence before specified Shot",
                INSERT_POSITION.INSERT_AFTER: "Insert sequence after specified Shot",
                INSERT_POSITION.INSERT_ABOVE: "Insert sequence above specified Shot",
                INSERT_POSITION.INSERT_BELOW: "Insert sequence below specified Shot",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in INSERT_POSITION}

INSERT_START="start"
INSERT_END="end"
INSERT_BEFORE="before"
INSERT_AFTER="after"
INSERT_ABOVE="above"
INSERT_BELOW="below"
#  LOG_SEVERITY : Log Message Severity
#    LOGSEVERITY_HARD : Hard error
#    LOGSEVERITY_SOFT : Soft error
#    LOGSEVERITY_INFO : Information or transient message
if sys.version_info[0] >= 3:
    class LOG_SEVERITY(enum.Enum):
        LOGSEVERITY_HARD="ERR_HARD"
        LOGSEVERITY_SOFT="ERR_SOFT"
        LOGSEVERITY_INFO="ERR_INFO_TRANSIENT"
        def describe(self):
            descs = {
                LOG_SEVERITY.LOGSEVERITY_HARD: "Hard error",
                LOG_SEVERITY.LOGSEVERITY_SOFT: "Soft error",
                LOG_SEVERITY.LOGSEVERITY_INFO: "Information or transient message",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in LOG_SEVERITY}

LOGSEVERITY_HARD="ERR_HARD"
LOGSEVERITY_SOFT="ERR_SOFT"
LOGSEVERITY_INFO="ERR_INFO_TRANSIENT"
#  LUT_LOCATION : Specify where LUT data should be found for a LUT operator
#    LUTLOCATION_FILE : LUT is stored in an external file
#    LUTLOCATION_EMBEDDED : LUT is embedded in source image file
if sys.version_info[0] >= 3:
    class LUT_LOCATION(enum.Enum):
        LUTLOCATION_FILE="file"
        LUTLOCATION_EMBEDDED="embedded"
        def describe(self):
            descs = {
                LUT_LOCATION.LUTLOCATION_FILE: "LUT is stored in an external file",
                LUT_LOCATION.LUTLOCATION_EMBEDDED: "LUT is embedded in source image file",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in LUT_LOCATION}

LUTLOCATION_FILE="file"
LUTLOCATION_EMBEDDED="embedded"
#  MARK_TYPE : Used to distinguish between timeline, shot and strip marks
#    MARKTYPE_TIMELINE : Timeline mark, position stored as time in seconds relative to start of timeline
#    MARKTYPE_SHOT : Shot mark, position stored as source image frame number
#    MARKTYPE_STRIP : Strip mark, position stored as time in seconds relative to start of strip
if sys.version_info[0] >= 3:
    class MARK_TYPE(enum.Enum):
        MARKTYPE_TIMELINE="Timeline"
        MARKTYPE_SHOT="Shot"
        MARKTYPE_STRIP="Strip"
        def describe(self):
            descs = {
                MARK_TYPE.MARKTYPE_TIMELINE: "Timeline mark, position stored as time in seconds relative to start of timeline",
                MARK_TYPE.MARKTYPE_SHOT: "Shot mark, position stored as source image frame number",
                MARK_TYPE.MARKTYPE_STRIP: "Strip mark, position stored as time in seconds relative to start of strip",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MARK_TYPE}

MARKTYPE_TIMELINE="Timeline"
MARKTYPE_SHOT="Shot"
MARKTYPE_STRIP="Strip"
#  MENU_LOCATION : Location within application of new menu or menu item
#    MENULOCATION_APP_MENU : Main application menu, ie Baselight or Daylight
#    MENULOCATION_SCENE_MENU : Scene menu
#    MENULOCATION_EDIT_MENU : Edit menu
#    MENULOCATION_JOB_MANAGER : Job Manager
#    MENULOCATION_SHOT_VIEW : Shots View
if sys.version_info[0] >= 3:
    class MENU_LOCATION(enum.Enum):
        MENULOCATION_APP_MENU="ML_APPMENU"
        MENULOCATION_SCENE_MENU="ML_SCENE"
        MENULOCATION_EDIT_MENU="ML_EDIT"
        MENULOCATION_JOB_MANAGER="ML_JOB_MANAGER"
        MENULOCATION_SHOT_VIEW="ML_SHOTS_VIEW"
        def describe(self):
            descs = {
                MENU_LOCATION.MENULOCATION_APP_MENU: "Main application menu, ie Baselight or Daylight",
                MENU_LOCATION.MENULOCATION_SCENE_MENU: "Scene menu",
                MENU_LOCATION.MENULOCATION_EDIT_MENU: "Edit menu",
                MENU_LOCATION.MENULOCATION_JOB_MANAGER: "Job Manager",
                MENU_LOCATION.MENULOCATION_SHOT_VIEW: "Shots View",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MENU_LOCATION}

MENULOCATION_APP_MENU="ML_APPMENU"
MENULOCATION_SCENE_MENU="ML_SCENE"
MENULOCATION_EDIT_MENU="ML_EDIT"
MENULOCATION_JOB_MANAGER="ML_JOB_MANAGER"
MENULOCATION_SHOT_VIEW="ML_SHOTS_VIEW"
#  MULTIPASTESTATUS : Status info related to Multi-Paste progress
#    MULTIPASTESTATUS_FAIL : Failure during multi-paste operation
#    MULTIPASTESTATUS_WARN : Warning during multi-paste operation
#    MULTIPASTESTATUS_INFO : Info from multi-paste operation
#    MULTIPASTESTATUS_NOTE : Note from multi-paste operation
#    MULTIPASTESTATUS_SCAN : Filesystem scanning progress
if sys.version_info[0] >= 3:
    class MULTIPASTESTATUS(enum.Enum):
        MULTIPASTESTATUS_FAIL="FAIL"
        MULTIPASTESTATUS_WARN="WARN"
        MULTIPASTESTATUS_INFO="INFO"
        MULTIPASTESTATUS_NOTE="NOTE"
        MULTIPASTESTATUS_SCAN="SCAN"
        def describe(self):
            descs = {
                MULTIPASTESTATUS.MULTIPASTESTATUS_FAIL: "Failure during multi-paste operation",
                MULTIPASTESTATUS.MULTIPASTESTATUS_WARN: "Warning during multi-paste operation",
                MULTIPASTESTATUS.MULTIPASTESTATUS_INFO: "Info from multi-paste operation",
                MULTIPASTESTATUS.MULTIPASTESTATUS_NOTE: "Note from multi-paste operation",
                MULTIPASTESTATUS.MULTIPASTESTATUS_SCAN: "Filesystem scanning progress",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTESTATUS}

MULTIPASTESTATUS_FAIL="FAIL"
MULTIPASTESTATUS_WARN="WARN"
MULTIPASTESTATUS_INFO="INFO"
MULTIPASTESTATUS_NOTE="NOTE"
MULTIPASTESTATUS_SCAN="SCAN"
#  MULTIPASTE_BLGRESOURCECONFLICT : Values for MultiPasteSettings BLGResourceConflict
#    MULTIPASTE_BLGRESOURCECONFLICT_REPLACE : Replace Existing Resources with BLG Versions
#    MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL : Use Existing Resources with the Same Name
#    MULTIPASTE_BLGRESOURCECONFLICT_RENAME : Import BLG Resources Under a New Name
if sys.version_info[0] >= 3:
    class MULTIPASTE_BLGRESOURCECONFLICT(enum.Enum):
        MULTIPASTE_BLGRESOURCECONFLICT_REPLACE="Replace"
        MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL="Original"
        MULTIPASTE_BLGRESOURCECONFLICT_RENAME="Rename"
        def describe(self):
            descs = {
                MULTIPASTE_BLGRESOURCECONFLICT.MULTIPASTE_BLGRESOURCECONFLICT_REPLACE: "Replace Existing Resources with BLG Versions",
                MULTIPASTE_BLGRESOURCECONFLICT.MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL: "Use Existing Resources with the Same Name",
                MULTIPASTE_BLGRESOURCECONFLICT.MULTIPASTE_BLGRESOURCECONFLICT_RENAME: "Import BLG Resources Under a New Name",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_BLGRESOURCECONFLICT}

MULTIPASTE_BLGRESOURCECONFLICT_REPLACE="Replace"
MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL="Original"
MULTIPASTE_BLGRESOURCECONFLICT_RENAME="Rename"
#  MULTIPASTE_DESTSELECTION : Values for MultiPasteSettings DestSelection
#    MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS : Timeline Stacks Containing a Selected Strip
#    MULTIPASTE_DESTSELECTION_SELECTEDSHOTS : Selected Shots in Shots View/Cuts View
if sys.version_info[0] >= 3:
    class MULTIPASTE_DESTSELECTION(enum.Enum):
        MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS="SelectedStrips"
        MULTIPASTE_DESTSELECTION_SELECTEDSHOTS="SelectedShots"
        def describe(self):
            descs = {
                MULTIPASTE_DESTSELECTION.MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS: "Timeline Stacks Containing a Selected Strip",
                MULTIPASTE_DESTSELECTION.MULTIPASTE_DESTSELECTION_SELECTEDSHOTS: "Selected Shots in Shots View/Cuts View",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_DESTSELECTION}

MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS="SelectedStrips"
MULTIPASTE_DESTSELECTION_SELECTEDSHOTS="SelectedShots"
#  MULTIPASTE_DESTSHOTS : Values for MultiPasteSettings DestShots
#    MULTIPASTE_DESTSHOTS_OVERWRITEALL : Overwrite All
#    MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS : Overwrite All, Except Layers of Category
#    MULTIPASTE_DESTSHOTS_RETAINALL : Retain All
#    MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS : Retain All, Except Layers of Category
if sys.version_info[0] >= 3:
    class MULTIPASTE_DESTSHOTS(enum.Enum):
        MULTIPASTE_DESTSHOTS_OVERWRITEALL="OverwriteAll"
        MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS="OverwriteAllExceptCats"
        MULTIPASTE_DESTSHOTS_RETAINALL="RetainAll"
        MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS="RetainAllExceptCats"
        def describe(self):
            descs = {
                MULTIPASTE_DESTSHOTS.MULTIPASTE_DESTSHOTS_OVERWRITEALL: "Overwrite All",
                MULTIPASTE_DESTSHOTS.MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS: "Overwrite All, Except Layers of Category",
                MULTIPASTE_DESTSHOTS.MULTIPASTE_DESTSHOTS_RETAINALL: "Retain All",
                MULTIPASTE_DESTSHOTS.MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS: "Retain All, Except Layers of Category",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_DESTSHOTS}

MULTIPASTE_DESTSHOTS_OVERWRITEALL="OverwriteAll"
MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS="OverwriteAllExceptCats"
MULTIPASTE_DESTSHOTS_RETAINALL="RetainAll"
MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS="RetainAllExceptCats"
#  MULTIPASTE_EDLAPPLYASCCDL : Values for MultiPasteSettings EDLApplyASCCDL
#    MULTIPASTE_EDLAPPLYASCCDL_NO : No
#    MULTIPASTE_EDLAPPLYASCCDL_CDL : Yes
if sys.version_info[0] >= 3:
    class MULTIPASTE_EDLAPPLYASCCDL(enum.Enum):
        MULTIPASTE_EDLAPPLYASCCDL_NO="No"
        MULTIPASTE_EDLAPPLYASCCDL_CDL="CDL"
        def describe(self):
            descs = {
                MULTIPASTE_EDLAPPLYASCCDL.MULTIPASTE_EDLAPPLYASCCDL_NO: "No",
                MULTIPASTE_EDLAPPLYASCCDL.MULTIPASTE_EDLAPPLYASCCDL_CDL: "Yes",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_EDLAPPLYASCCDL}

MULTIPASTE_EDLAPPLYASCCDL_NO="No"
MULTIPASTE_EDLAPPLYASCCDL_CDL="CDL"
#  MULTIPASTE_LAYERZEROBEHAVIOUR : Values for MultiPasteSettings LayerZeroBehaviour
#    MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY : All Layers, Except Layer 0
#    MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK : All Layers, Including Layer 0
#    MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY : Layer 0 Only
#    MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS : No Layers
if sys.version_info[0] >= 3:
    class MULTIPASTE_LAYERZEROBEHAVIOUR(enum.Enum):
        MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY="StackOnly"
        MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK="LayerZeroAndStack"
        MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY="LayerZeroOnly"
        MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS="NoLayers"
        def describe(self):
            descs = {
                MULTIPASTE_LAYERZEROBEHAVIOUR.MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY: "All Layers, Except Layer 0",
                MULTIPASTE_LAYERZEROBEHAVIOUR.MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK: "All Layers, Including Layer 0",
                MULTIPASTE_LAYERZEROBEHAVIOUR.MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY: "Layer 0 Only",
                MULTIPASTE_LAYERZEROBEHAVIOUR.MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS: "No Layers",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_LAYERZEROBEHAVIOUR}

MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY="StackOnly"
MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK="LayerZeroAndStack"
MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY="LayerZeroOnly"
MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS="NoLayers"
#  MULTIPASTE_LAYERZEROCATEGORIES : Values for MultiPasteSettings LayerZeroCategories
#    MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE : Append Categories, Except
#    MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE : Replace Categories, Add All Except
#    MULTIPASTE_LAYERZEROCATEGORIES_NO : Do Not Copy Layer 0 Categories
if sys.version_info[0] >= 3:
    class MULTIPASTE_LAYERZEROCATEGORIES(enum.Enum):
        MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE="Include"
        MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE="Overwrite"
        MULTIPASTE_LAYERZEROCATEGORIES_NO="No"
        def describe(self):
            descs = {
                MULTIPASTE_LAYERZEROCATEGORIES.MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE: "Append Categories, Except",
                MULTIPASTE_LAYERZEROCATEGORIES.MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE: "Replace Categories, Add All Except",
                MULTIPASTE_LAYERZEROCATEGORIES.MULTIPASTE_LAYERZEROCATEGORIES_NO: "Do Not Copy Layer 0 Categories",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_LAYERZEROCATEGORIES}

MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE="Include"
MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE="Overwrite"
MULTIPASTE_LAYERZEROCATEGORIES_NO="No"
#  MULTIPASTE_MATCHBY : Values for MultiPasteSettings MatchBy
#    MULTIPASTE_MATCHBY_TAPENAME : Source Tape Name
#    MULTIPASTE_MATCHBY_FILENAME : Source Path+Filename
#    MULTIPASTE_MATCHBY_CLIPNAME : Source Clip Name
#    MULTIPASTE_MATCHBY_AVIDUID : Source Avid UID
#    MULTIPASTE_MATCHBY_CAMERA : Source Camera
#    MULTIPASTE_MATCHBY_BLGNAME : Source BLG Name
#    MULTIPASTE_MATCHBY_BLGID : Source BLG ID
#    MULTIPASTE_MATCHBY_SCENE : Source Scene
#    MULTIPASTE_MATCHBY_SCENETAKE : Source Scene & Take
#    MULTIPASTE_MATCHBY_CAMERAROLL : Source Camera Roll
#    MULTIPASTE_MATCHBY_LABROLL : Source Lab Roll
#    MULTIPASTE_MATCHBY_LUT : Source LUT
#    MULTIPASTE_MATCHBY_LUT2 : Source LUT2
#    MULTIPASTE_MATCHBY_ASC_CC_XML : Source ASC_CC_XML
#    MULTIPASTE_MATCHBY_FRAMENUMBER : Source Frame Number
#    MULTIPASTE_MATCHBY_TIMECODE : Source Timecode
#    MULTIPASTE_MATCHBY_KEYCODE : Source Keycode
#    MULTIPASTE_MATCHBY_RECORDFRAMENUMBER : Record Frame Number
#    MULTIPASTE_MATCHBY_RECORDTIMECODE : Record Timecode
#    MULTIPASTE_MATCHBY_ALWAYSMATCH : Ignore Time Ranges
if sys.version_info[0] >= 3:
    class MULTIPASTE_MATCHBY(enum.Enum):
        MULTIPASTE_MATCHBY_TAPENAME="TapeName"
        MULTIPASTE_MATCHBY_FILENAME="Filename"
        MULTIPASTE_MATCHBY_CLIPNAME="ClipName"
        MULTIPASTE_MATCHBY_AVIDUID="AvidUID"
        MULTIPASTE_MATCHBY_CAMERA="Camera"
        MULTIPASTE_MATCHBY_BLGNAME="BLGName"
        MULTIPASTE_MATCHBY_BLGID="BLGId"
        MULTIPASTE_MATCHBY_SCENE="Scene"
        MULTIPASTE_MATCHBY_SCENETAKE="SceneTake"
        MULTIPASTE_MATCHBY_CAMERAROLL="CameraRoll"
        MULTIPASTE_MATCHBY_LABROLL="LabRoll"
        MULTIPASTE_MATCHBY_LUT="LUT"
        MULTIPASTE_MATCHBY_LUT2="LUT2"
        MULTIPASTE_MATCHBY_ASC_CC_XML="ASC_CC_XML"
        MULTIPASTE_MATCHBY_FRAMENUMBER="FrameNumber"
        MULTIPASTE_MATCHBY_TIMECODE="Timecode"
        MULTIPASTE_MATCHBY_KEYCODE="Keycode"
        MULTIPASTE_MATCHBY_RECORDFRAMENUMBER="RecordFrameNumber"
        MULTIPASTE_MATCHBY_RECORDTIMECODE="RecordTimecode"
        MULTIPASTE_MATCHBY_ALWAYSMATCH="AlwaysMatch"
        def describe(self):
            descs = {
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_TAPENAME: "Source Tape Name",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_FILENAME: "Source Path+Filename",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_CLIPNAME: "Source Clip Name",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_AVIDUID: "Source Avid UID",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_CAMERA: "Source Camera",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_BLGNAME: "Source BLG Name",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_BLGID: "Source BLG ID",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_SCENE: "Source Scene",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_SCENETAKE: "Source Scene & Take",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_CAMERAROLL: "Source Camera Roll",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_LABROLL: "Source Lab Roll",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_LUT: "Source LUT",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_LUT2: "Source LUT2",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_ASC_CC_XML: "Source ASC_CC_XML",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_FRAMENUMBER: "Source Frame Number",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_TIMECODE: "Source Timecode",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_KEYCODE: "Source Keycode",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_RECORDFRAMENUMBER: "Record Frame Number",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_RECORDTIMECODE: "Record Timecode",
                MULTIPASTE_MATCHBY.MULTIPASTE_MATCHBY_ALWAYSMATCH: "Ignore Time Ranges",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_MATCHBY}

MULTIPASTE_MATCHBY_TAPENAME="TapeName"
MULTIPASTE_MATCHBY_FILENAME="Filename"
MULTIPASTE_MATCHBY_CLIPNAME="ClipName"
MULTIPASTE_MATCHBY_AVIDUID="AvidUID"
MULTIPASTE_MATCHBY_CAMERA="Camera"
MULTIPASTE_MATCHBY_BLGNAME="BLGName"
MULTIPASTE_MATCHBY_BLGID="BLGId"
MULTIPASTE_MATCHBY_SCENE="Scene"
MULTIPASTE_MATCHBY_SCENETAKE="SceneTake"
MULTIPASTE_MATCHBY_CAMERAROLL="CameraRoll"
MULTIPASTE_MATCHBY_LABROLL="LabRoll"
MULTIPASTE_MATCHBY_LUT="LUT"
MULTIPASTE_MATCHBY_LUT2="LUT2"
MULTIPASTE_MATCHBY_ASC_CC_XML="ASC_CC_XML"
MULTIPASTE_MATCHBY_FRAMENUMBER="FrameNumber"
MULTIPASTE_MATCHBY_TIMECODE="Timecode"
MULTIPASTE_MATCHBY_KEYCODE="Keycode"
MULTIPASTE_MATCHBY_RECORDFRAMENUMBER="RecordFrameNumber"
MULTIPASTE_MATCHBY_RECORDTIMECODE="RecordTimecode"
MULTIPASTE_MATCHBY_ALWAYSMATCH="AlwaysMatch"
#  MULTIPASTE_MATCHQUALITY : Values for MultiPasteSettings MatchQuality
#    MULTIPASTE_MATCHQUALITY_EXACTMATCH : Exact
#    MULTIPASTE_MATCHQUALITY_FUZZYMATCH : Fuzzy
if sys.version_info[0] >= 3:
    class MULTIPASTE_MATCHQUALITY(enum.Enum):
        MULTIPASTE_MATCHQUALITY_EXACTMATCH="ExactMatch"
        MULTIPASTE_MATCHQUALITY_FUZZYMATCH="FuzzyMatch"
        def describe(self):
            descs = {
                MULTIPASTE_MATCHQUALITY.MULTIPASTE_MATCHQUALITY_EXACTMATCH: "Exact",
                MULTIPASTE_MATCHQUALITY.MULTIPASTE_MATCHQUALITY_FUZZYMATCH: "Fuzzy",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_MATCHQUALITY}

MULTIPASTE_MATCHQUALITY_EXACTMATCH="ExactMatch"
MULTIPASTE_MATCHQUALITY_FUZZYMATCH="FuzzyMatch"
#  MULTIPASTE_PASTELOCATION : Values for MultiPasteSettings PasteLocation
#    MULTIPASTE_PASTELOCATION_ABOVE : Above Remaining Destination Layers
#    MULTIPASTE_PASTELOCATION_BELOW : Below Remaining Destination Layers
if sys.version_info[0] >= 3:
    class MULTIPASTE_PASTELOCATION(enum.Enum):
        MULTIPASTE_PASTELOCATION_ABOVE="Above"
        MULTIPASTE_PASTELOCATION_BELOW="Below"
        def describe(self):
            descs = {
                MULTIPASTE_PASTELOCATION.MULTIPASTE_PASTELOCATION_ABOVE: "Above Remaining Destination Layers",
                MULTIPASTE_PASTELOCATION.MULTIPASTE_PASTELOCATION_BELOW: "Below Remaining Destination Layers",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_PASTELOCATION}

MULTIPASTE_PASTELOCATION_ABOVE="Above"
MULTIPASTE_PASTELOCATION_BELOW="Below"
#  MULTIPASTE_SOURCE : Values for MultiPasteSettings Source
#    MULTIPASTE_SOURCE_COPYBUFFER : Current Copy Buffer
#    MULTIPASTE_SOURCE_MULTIPLESCENES : Multiple Scenes
#    MULTIPASTE_SOURCE_BLG : BLG Files
#    MULTIPASTE_SOURCE_LUT : LUT Files
#    MULTIPASTE_SOURCE_CDL : CDL/CCC XML Files
#    MULTIPASTE_SOURCE_EDL : EDL/ALE files
if sys.version_info[0] >= 3:
    class MULTIPASTE_SOURCE(enum.Enum):
        MULTIPASTE_SOURCE_COPYBUFFER="CopyBuffer"
        MULTIPASTE_SOURCE_MULTIPLESCENES="MultipleScenes"
        MULTIPASTE_SOURCE_BLG="BLG"
        MULTIPASTE_SOURCE_LUT="LUT"
        MULTIPASTE_SOURCE_CDL="CDL"
        MULTIPASTE_SOURCE_EDL="EDL"
        def describe(self):
            descs = {
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_COPYBUFFER: "Current Copy Buffer",
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_MULTIPLESCENES: "Multiple Scenes",
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_BLG: "BLG Files",
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_LUT: "LUT Files",
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_CDL: "CDL/CCC XML Files",
                MULTIPASTE_SOURCE.MULTIPASTE_SOURCE_EDL: "EDL/ALE files",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_SOURCE}

MULTIPASTE_SOURCE_COPYBUFFER="CopyBuffer"
MULTIPASTE_SOURCE_MULTIPLESCENES="MultipleScenes"
MULTIPASTE_SOURCE_BLG="BLG"
MULTIPASTE_SOURCE_LUT="LUT"
MULTIPASTE_SOURCE_CDL="CDL"
MULTIPASTE_SOURCE_EDL="EDL"
#  MULTIPASTE_SOURCESHOTS : Values for MultiPasteSettings SourceShots
#    MULTIPASTE_SOURCESHOTS_COPYALL : Copy All
#    MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS : Copy All, Except Layers of Category
#    MULTIPASTE_SOURCESHOTS_COPYONLYCATS : Copy Only Layers of Category
if sys.version_info[0] >= 3:
    class MULTIPASTE_SOURCESHOTS(enum.Enum):
        MULTIPASTE_SOURCESHOTS_COPYALL="CopyAll"
        MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS="CopyAllExceptCats"
        MULTIPASTE_SOURCESHOTS_COPYONLYCATS="CopyOnlyCats"
        def describe(self):
            descs = {
                MULTIPASTE_SOURCESHOTS.MULTIPASTE_SOURCESHOTS_COPYALL: "Copy All",
                MULTIPASTE_SOURCESHOTS.MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS: "Copy All, Except Layers of Category",
                MULTIPASTE_SOURCESHOTS.MULTIPASTE_SOURCESHOTS_COPYONLYCATS: "Copy Only Layers of Category",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in MULTIPASTE_SOURCESHOTS}

MULTIPASTE_SOURCESHOTS_COPYALL="CopyAll"
MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS="CopyAllExceptCats"
MULTIPASTE_SOURCESHOTS_COPYONLYCATS="CopyOnlyCats"
#  OPENFLAG : Flags used to control opening a scene
#    OPENFLAG_DISCARD : Discard any unsaved changes when opening scene
#    OPENFLAG_RECOVER : Recover any unsaved changes when opening scene
#    OPENFLAG_OLD : Allow opening of old scenes
#    OPENFLAG_IGNORE_REVISION : Ignore data revision number when opening scene
#    OPENFLAG_READ_ONLY : Open scene read-only
#    OPENFLAG_ALLOW_UNKNOWN_OFX : Allow opening scenes that reference unknown OpenFX plugins
#    OPENFLAG_NO_CONTAINER_WARNING : Don't warn if scene uses container that is not known on this machine
if sys.version_info[0] >= 3:
    class OPENFLAG(enum.Enum):
        OPENFLAG_DISCARD="discard"
        OPENFLAG_RECOVER="recover"
        OPENFLAG_OLD="openold"
        OPENFLAG_IGNORE_REVISION="ignorerevision"
        OPENFLAG_READ_ONLY="readonly"
        OPENFLAG_ALLOW_UNKNOWN_OFX="allow_unknown_openfx"
        OPENFLAG_NO_CONTAINER_WARNING="nocontainerwarning"
        def describe(self):
            descs = {
                OPENFLAG.OPENFLAG_DISCARD: "Discard any unsaved changes when opening scene",
                OPENFLAG.OPENFLAG_RECOVER: "Recover any unsaved changes when opening scene",
                OPENFLAG.OPENFLAG_OLD: "Allow opening of old scenes",
                OPENFLAG.OPENFLAG_IGNORE_REVISION: "Ignore data revision number when opening scene",
                OPENFLAG.OPENFLAG_READ_ONLY: "Open scene read-only",
                OPENFLAG.OPENFLAG_ALLOW_UNKNOWN_OFX: "Allow opening scenes that reference unknown OpenFX plugins",
                OPENFLAG.OPENFLAG_NO_CONTAINER_WARNING: "Don't warn if scene uses container that is not known on this machine",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in OPENFLAG}

OPENFLAG_DISCARD="discard"
OPENFLAG_RECOVER="recover"
OPENFLAG_OLD="openold"
OPENFLAG_IGNORE_REVISION="ignorerevision"
OPENFLAG_READ_ONLY="readonly"
OPENFLAG_ALLOW_UNKNOWN_OFX="allow_unknown_openfx"
OPENFLAG_NO_CONTAINER_WARNING="nocontainerwarning"
#  OPERATOR_BARS_TYPE : Define the type of Bars to render
#    OPERATOR_BARS_TYPE_RP219HD_2a3a : SMPTE 75% white
#    OPERATOR_BARS_TYPE_RP219HD_2b3a : SMPTE 100% white
#    OPERATOR_BARS_TYPE_RP219HD_2c3b : SMPTE +I +Q
#    OPERATOR_BARS_TYPE_RP219HD_2d3b : SMPTE -I +Q
#    OPERATOR_BARS_TYPE_GREYS17 : Grey bars
#    OPERATOR_BARS_TYPE_RAMP : Grey ramp
#    OPERATOR_BARS_TYPE_RGBGREY : RGB and greys
#    OPERATOR_BARS_TYPE_B72 : BT.2111/ARIB B72 (HLG)
#    OPERATOR_BARS_TYPE_ITU2111_PQ : BT.2111 (PQ)
#    OPERATOR_BARS_TYPE_B66_4K : ARIB B66 (UHDTV 4K)
#    OPERATOR_BARS_TYPE_B66_8K : ARIB B66 (UHDTV 8K)
if sys.version_info[0] >= 3:
    class OPERATOR_BARS_TYPE(enum.Enum):
        OPERATOR_BARS_TYPE_RP219HD_2a3a="RP219HD_2a3a"
        OPERATOR_BARS_TYPE_RP219HD_2b3a="RP219HD_2b3a"
        OPERATOR_BARS_TYPE_RP219HD_2c3b="RP219HD_2c3b"
        OPERATOR_BARS_TYPE_RP219HD_2d3b="RP219HD_2d3b"
        OPERATOR_BARS_TYPE_GREYS17="GREYS17"
        OPERATOR_BARS_TYPE_RAMP="RAMP"
        OPERATOR_BARS_TYPE_RGBGREY="RGBGREY"
        OPERATOR_BARS_TYPE_B72="B72"
        OPERATOR_BARS_TYPE_ITU2111_PQ="ITU2111_PQ"
        OPERATOR_BARS_TYPE_B66_4K="B66_4K"
        OPERATOR_BARS_TYPE_B66_8K="B66_8K"
        def describe(self):
            descs = {
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RP219HD_2a3a: "SMPTE 75% white",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RP219HD_2b3a: "SMPTE 100% white",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RP219HD_2c3b: "SMPTE +I +Q",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RP219HD_2d3b: "SMPTE -I +Q",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_GREYS17: "Grey bars",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RAMP: "Grey ramp",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_RGBGREY: "RGB and greys",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_B72: "BT.2111/ARIB B72 (HLG)",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_ITU2111_PQ: "BT.2111 (PQ)",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_B66_4K: "ARIB B66 (UHDTV 4K)",
                OPERATOR_BARS_TYPE.OPERATOR_BARS_TYPE_B66_8K: "ARIB B66 (UHDTV 8K)",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in OPERATOR_BARS_TYPE}

OPERATOR_BARS_TYPE_RP219HD_2a3a="RP219HD_2a3a"
OPERATOR_BARS_TYPE_RP219HD_2b3a="RP219HD_2b3a"
OPERATOR_BARS_TYPE_RP219HD_2c3b="RP219HD_2c3b"
OPERATOR_BARS_TYPE_RP219HD_2d3b="RP219HD_2d3b"
OPERATOR_BARS_TYPE_GREYS17="GREYS17"
OPERATOR_BARS_TYPE_RAMP="RAMP"
OPERATOR_BARS_TYPE_RGBGREY="RGBGREY"
OPERATOR_BARS_TYPE_B72="B72"
OPERATOR_BARS_TYPE_ITU2111_PQ="ITU2111_PQ"
OPERATOR_BARS_TYPE_B66_4K="B66_4K"
OPERATOR_BARS_TYPE_B66_8K="B66_8K"
#  OPSTATUS : Status of an operation in Queue or Processor
#    OPSTATUS_CREATING : Operation is being created
#    OPSTATUS_QUEUED : Operation is waiting in the queue
#    OPSTATUS_ACTIVE : Operation is active
#    OPSTATUS_CRASHED : Operation crashed
#    OPSTATUS_STOPPED : Operation has been manually stopped
#    OPSTATUS_TOONEW : Operation was submitted to the queue by a newer version of the software and cannot be processed
#    OPSTATUS_DONE : Operation is complete
if sys.version_info[0] >= 3:
    class OPSTATUS(enum.Enum):
        OPSTATUS_CREATING="Creating"
        OPSTATUS_QUEUED="Queued"
        OPSTATUS_ACTIVE="Active"
        OPSTATUS_CRASHED="Crashed"
        OPSTATUS_STOPPED="Stopped"
        OPSTATUS_TOONEW="Too New"
        OPSTATUS_DONE="Done"
        def describe(self):
            descs = {
                OPSTATUS.OPSTATUS_CREATING: "Operation is being created",
                OPSTATUS.OPSTATUS_QUEUED: "Operation is waiting in the queue",
                OPSTATUS.OPSTATUS_ACTIVE: "Operation is active",
                OPSTATUS.OPSTATUS_CRASHED: "Operation crashed",
                OPSTATUS.OPSTATUS_STOPPED: "Operation has been manually stopped",
                OPSTATUS.OPSTATUS_TOONEW: "Operation was submitted to the queue by a newer version of the software and cannot be processed",
                OPSTATUS.OPSTATUS_DONE: "Operation is complete",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in OPSTATUS}

OPSTATUS_CREATING="Creating"
OPSTATUS_QUEUED="Queued"
OPSTATUS_ACTIVE="Active"
OPSTATUS_CRASHED="Crashed"
OPSTATUS_STOPPED="Stopped"
OPSTATUS_TOONEW="Too New"
OPSTATUS_DONE="Done"
#  OPTICALFLOW_QUALITY : Optical Flow Quality
#    OFLOWQUAL_BEST : Best Quality
#    OFLOWQUAL_HIGH : High Quality
#    OFLOWQUAL_MEDIUM : Medium Quality
if sys.version_info[0] >= 3:
    class OPTICALFLOW_QUALITY(enum.Enum):
        OFLOWQUAL_BEST="Best"
        OFLOWQUAL_HIGH="High"
        OFLOWQUAL_MEDIUM="Medium"
        def describe(self):
            descs = {
                OPTICALFLOW_QUALITY.OFLOWQUAL_BEST: "Best Quality",
                OPTICALFLOW_QUALITY.OFLOWQUAL_HIGH: "High Quality",
                OPTICALFLOW_QUALITY.OFLOWQUAL_MEDIUM: "Medium Quality",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in OPTICALFLOW_QUALITY}

OFLOWQUAL_BEST="Best"
OFLOWQUAL_HIGH="High"
OFLOWQUAL_MEDIUM="Medium"
#  OPTICALFLOW_SMOOTHING : Optical Flow Smoothing
#    OFLOWSMOOTH_NONE : None
#    OFLOWSMOOTH_LOW : Low
#    OFLOWSMOOTH_MEDIUM : Medium
#    OFLOWSMOOTH_HIGH : High
#    OFLOWSMOOTH_MAX : Maximum
if sys.version_info[0] >= 3:
    class OPTICALFLOW_SMOOTHING(enum.Enum):
        OFLOWSMOOTH_NONE=0
        OFLOWSMOOTH_LOW=1
        OFLOWSMOOTH_MEDIUM=2
        OFLOWSMOOTH_HIGH=3
        OFLOWSMOOTH_MAX=4
        def describe(self):
            descs = {
                OPTICALFLOW_SMOOTHING.OFLOWSMOOTH_NONE: "None",
                OPTICALFLOW_SMOOTHING.OFLOWSMOOTH_LOW: "Low",
                OPTICALFLOW_SMOOTHING.OFLOWSMOOTH_MEDIUM: "Medium",
                OPTICALFLOW_SMOOTHING.OFLOWSMOOTH_HIGH: "High",
                OPTICALFLOW_SMOOTHING.OFLOWSMOOTH_MAX: "Maximum",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in OPTICALFLOW_SMOOTHING}

OFLOWSMOOTH_NONE=0
OFLOWSMOOTH_LOW=1
OFLOWSMOOTH_MEDIUM=2
OFLOWSMOOTH_HIGH=3
OFLOWSMOOTH_MAX=4
#  PROXY_RESOLUTION : Proxy Resolution of Render Format
#    RES_HIGH : High (full) resolution
#    RES_MEDIUM : Medium proxy resolution
#    RES_LOW : Low proxy resolution
if sys.version_info[0] >= 3:
    class PROXY_RESOLUTION(enum.Enum):
        RES_HIGH="GMPR_HIGH"
        RES_MEDIUM="GMPR_MEDIUM"
        RES_LOW="GMPR_LOW"
        def describe(self):
            descs = {
                PROXY_RESOLUTION.RES_HIGH: "High (full) resolution",
                PROXY_RESOLUTION.RES_MEDIUM: "Medium proxy resolution",
                PROXY_RESOLUTION.RES_LOW: "Low proxy resolution",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in PROXY_RESOLUTION}

RES_HIGH="GMPR_HIGH"
RES_MEDIUM="GMPR_MEDIUM"
RES_LOW="GMPR_LOW"
#  QUEUE_LOG_TYPE : Message type for log entry queue operation log
#    QUEUELOGTYPE_INFO : Information
#    QUEUELOGTYPE_WARN : Warning
#    QUEUELOGTYPE_FAIL : Error/failure
if sys.version_info[0] >= 3:
    class QUEUE_LOG_TYPE(enum.Enum):
        QUEUELOGTYPE_INFO="info"
        QUEUELOGTYPE_WARN="warn"
        QUEUELOGTYPE_FAIL="fail"
        def describe(self):
            descs = {
                QUEUE_LOG_TYPE.QUEUELOGTYPE_INFO: "Information",
                QUEUE_LOG_TYPE.QUEUELOGTYPE_WARN: "Warning",
                QUEUE_LOG_TYPE.QUEUELOGTYPE_FAIL: "Error/failure",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in QUEUE_LOG_TYPE}

QUEUELOGTYPE_INFO="info"
QUEUELOGTYPE_WARN="warn"
QUEUELOGTYPE_FAIL="fail"
#  RENDER_CLIPNAME_SOURCE : Which clip name to embed into rendered output
#    RENDER_CLIPNAME_FILE : Source File Clip Name
#    RENDER_CLIPNAME_SHOT : Shot Clip Name
#    RENDER_CLIPNAME_STRIP : Clip Name from Strip Name
if sys.version_info[0] >= 3:
    class RENDER_CLIPNAME_SOURCE(enum.Enum):
        RENDER_CLIPNAME_FILE=0
        RENDER_CLIPNAME_SHOT=1
        RENDER_CLIPNAME_STRIP=2
        def describe(self):
            descs = {
                RENDER_CLIPNAME_SOURCE.RENDER_CLIPNAME_FILE: "Source File Clip Name",
                RENDER_CLIPNAME_SOURCE.RENDER_CLIPNAME_SHOT: "Shot Clip Name",
                RENDER_CLIPNAME_SOURCE.RENDER_CLIPNAME_STRIP: "Clip Name from Strip Name",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_CLIPNAME_SOURCE}

RENDER_CLIPNAME_FILE=0
RENDER_CLIPNAME_SHOT=1
RENDER_CLIPNAME_STRIP=2
#  RENDER_COLOURSPACE : Special values to use for RenderColourSpace in RenderDeliverable
#    RENDER_COLOURSPACE_USEINPUT : Use Input Colour Space of Shot
#    RENDER_COLOURSPACE_USESTACKOUTPUT : Use Stack Output Colour Space.This will resolve to the Scene Grade Result Colour Space if specified, otherwise this will resolve to the Scene Working Colour Space.
if sys.version_info[0] >= 3:
    class RENDER_COLOURSPACE(enum.Enum):
        RENDER_COLOURSPACE_USEINPUT="Input"
        RENDER_COLOURSPACE_USESTACKOUTPUT="None"
        def describe(self):
            descs = {
                RENDER_COLOURSPACE.RENDER_COLOURSPACE_USEINPUT: "Use Input Colour Space of Shot",
                RENDER_COLOURSPACE.RENDER_COLOURSPACE_USESTACKOUTPUT: "Use Stack Output Colour Space.This will resolve to the Scene Grade Result Colour Space if specified, otherwise this will resolve to the Scene Working Colour Space.",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_COLOURSPACE}

RENDER_COLOURSPACE_USEINPUT="Input"
RENDER_COLOURSPACE_USESTACKOUTPUT="None"
#  RENDER_EMPTY_BEHAVIOUR : Action to take when encountering frames in timeline with no strips/shots
#    RENDER_EMPTY_FAIL : Fail Render
#    RENDER_EMPTY_BLACK : Render Black Frame
#    RENDER_EMPTY_CHEQUER : Render Chequerboard Frame
if sys.version_info[0] >= 3:
    class RENDER_EMPTY_BEHAVIOUR(enum.Enum):
        RENDER_EMPTY_FAIL="GMREB_FAIL"
        RENDER_EMPTY_BLACK="GMREB_BLACK"
        RENDER_EMPTY_CHEQUER="GMREB_CHEQUER"
        def describe(self):
            descs = {
                RENDER_EMPTY_BEHAVIOUR.RENDER_EMPTY_FAIL: "Fail Render",
                RENDER_EMPTY_BEHAVIOUR.RENDER_EMPTY_BLACK: "Render Black Frame",
                RENDER_EMPTY_BEHAVIOUR.RENDER_EMPTY_CHEQUER: "Render Chequerboard Frame",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_EMPTY_BEHAVIOUR}

RENDER_EMPTY_FAIL="GMREB_FAIL"
RENDER_EMPTY_BLACK="GMREB_BLACK"
RENDER_EMPTY_CHEQUER="GMREB_CHEQUER"
#  RENDER_ERROR_BEHAVIOUR : Action to take when encountering frames in timeline with no strips/shots
#    RENDER_ERROR_FAIL : Fail Render
#    RENDER_ERROR_SKIP : Skip Frame And Continue
#    RENDER_ERROR_BLACK : Render Black Frame
#    RENDER_ERROR_CHEQUER : Render Chequerboard Frame And Continue
if sys.version_info[0] >= 3:
    class RENDER_ERROR_BEHAVIOUR(enum.Enum):
        RENDER_ERROR_FAIL="ABORT"
        RENDER_ERROR_SKIP="SKIP"
        RENDER_ERROR_BLACK="BLACK"
        RENDER_ERROR_CHEQUER="CHEQUER"
        def describe(self):
            descs = {
                RENDER_ERROR_BEHAVIOUR.RENDER_ERROR_FAIL: "Fail Render",
                RENDER_ERROR_BEHAVIOUR.RENDER_ERROR_SKIP: "Skip Frame And Continue",
                RENDER_ERROR_BEHAVIOUR.RENDER_ERROR_BLACK: "Render Black Frame",
                RENDER_ERROR_BEHAVIOUR.RENDER_ERROR_CHEQUER: "Render Chequerboard Frame And Continue",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_ERROR_BEHAVIOUR}

RENDER_ERROR_FAIL="ABORT"
RENDER_ERROR_SKIP="SKIP"
RENDER_ERROR_BLACK="BLACK"
RENDER_ERROR_CHEQUER="CHEQUER"
#  RENDER_FORMAT : Special values to use for RenderFormat in RenderDeliverable
#    RENDER_FORMAT_USEINPUT : Use Shot Input Format
if sys.version_info[0] >= 3:
    class RENDER_FORMAT(enum.Enum):
        RENDER_FORMAT_USEINPUT="0"
        def describe(self):
            descs = {
                RENDER_FORMAT.RENDER_FORMAT_USEINPUT: "Use Shot Input Format",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_FORMAT}

RENDER_FORMAT_USEINPUT="0"
#  RENDER_FRAMENUM : Specify how frame number for sequence should be calculated
#    RENDER_FRAMENUM_SCENE_FRAME : Scene Frame Number
#    RENDER_FRAMENUM_SHOT_FRAME : Shot  Frame Number
#    RENDER_FRAMENUM_SCENE_TIMECODE : Record Timecode as Frame Number
#    RENDER_FRAMENUM_SHOT_TIMECODE : Shot Timecode as Frame Number
if sys.version_info[0] >= 3:
    class RENDER_FRAMENUM(enum.Enum):
        RENDER_FRAMENUM_SCENE_FRAME="F"
        RENDER_FRAMENUM_SHOT_FRAME="G"
        RENDER_FRAMENUM_SCENE_TIMECODE="T"
        RENDER_FRAMENUM_SHOT_TIMECODE="H"
        def describe(self):
            descs = {
                RENDER_FRAMENUM.RENDER_FRAMENUM_SCENE_FRAME: "Scene Frame Number",
                RENDER_FRAMENUM.RENDER_FRAMENUM_SHOT_FRAME: "Shot  Frame Number",
                RENDER_FRAMENUM.RENDER_FRAMENUM_SCENE_TIMECODE: "Record Timecode as Frame Number",
                RENDER_FRAMENUM.RENDER_FRAMENUM_SHOT_TIMECODE: "Shot Timecode as Frame Number",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_FRAMENUM}

RENDER_FRAMENUM_SCENE_FRAME="F"
RENDER_FRAMENUM_SHOT_FRAME="G"
RENDER_FRAMENUM_SCENE_TIMECODE="T"
RENDER_FRAMENUM_SHOT_TIMECODE="H"
#  RENDER_INCOMPLETE_BEHAVIOUR : Action to take when encountering shots with missing strips
#    RENDER_INCOMPLETE_FAIL : Fail Render
#    RENDER_INCOMPLETE_CONTINUE : Render As Baselight (Chequerboard Missing)
#    RENDER_INCOMPLETE_BLACK : Render Black Frame
#    RENDER_INCOMPLETE_CHEQUER : Render Chequerboard Frame
if sys.version_info[0] >= 3:
    class RENDER_INCOMPLETE_BEHAVIOUR(enum.Enum):
        RENDER_INCOMPLETE_FAIL="GMREB_FAIL"
        RENDER_INCOMPLETE_CONTINUE="GMREB_CONTINUE"
        RENDER_INCOMPLETE_BLACK="GMREB_BLACK"
        RENDER_INCOMPLETE_CHEQUER="GMREB_CHEQUER"
        def describe(self):
            descs = {
                RENDER_INCOMPLETE_BEHAVIOUR.RENDER_INCOMPLETE_FAIL: "Fail Render",
                RENDER_INCOMPLETE_BEHAVIOUR.RENDER_INCOMPLETE_CONTINUE: "Render As Baselight (Chequerboard Missing)",
                RENDER_INCOMPLETE_BEHAVIOUR.RENDER_INCOMPLETE_BLACK: "Render Black Frame",
                RENDER_INCOMPLETE_BEHAVIOUR.RENDER_INCOMPLETE_CHEQUER: "Render Chequerboard Frame",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_INCOMPLETE_BEHAVIOUR}

RENDER_INCOMPLETE_FAIL="GMREB_FAIL"
RENDER_INCOMPLETE_CONTINUE="GMREB_CONTINUE"
RENDER_INCOMPLETE_BLACK="GMREB_BLACK"
RENDER_INCOMPLETE_CHEQUER="GMREB_CHEQUER"
#  RENDER_LAYER : Layers to include when rendering. This can be a layer number or one of the following constants.
#    RENDER_LAYER_ALL : Include all grade layers in rendered output
#    RENDER_LAYER_LAYERS_INPUTONLY : Do not include any grade layers or operators in layer 0
#    RENDER_LAYER_LAYER0 : Do not include any grade layers
if sys.version_info[0] >= 3:
    class RENDER_LAYER(enum.Enum):
        RENDER_LAYER_ALL=-1
        RENDER_LAYER_LAYERS_INPUTONLY=-2
        RENDER_LAYER_LAYER0=0
        def describe(self):
            descs = {
                RENDER_LAYER.RENDER_LAYER_ALL: "Include all grade layers in rendered output",
                RENDER_LAYER.RENDER_LAYER_LAYERS_INPUTONLY: "Do not include any grade layers or operators in layer 0",
                RENDER_LAYER.RENDER_LAYER_LAYER0: "Do not include any grade layers",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_LAYER}

RENDER_LAYER_ALL=-1
RENDER_LAYER_LAYERS_INPUTONLY=-2
RENDER_LAYER_LAYER0=0
#  RENDER_MASK : Select whether to crop to the mask, or set the black value for the masked area
#    RENDER_MASK_CROP : Crop image to mask
#    RENDER_MASK_BLACK : Set mask area to absolue black (0)
#    RENDER_MASK_VIDEO : Set mask area to video black (16/255)
#    RENDER_MASK_FILM : Set mask area to film black (95/1023)
if sys.version_info[0] >= 3:
    class RENDER_MASK(enum.Enum):
        RENDER_MASK_CROP=-1
        RENDER_MASK_BLACK=0
        RENDER_MASK_VIDEO=64
        RENDER_MASK_FILM=95
        def describe(self):
            descs = {
                RENDER_MASK.RENDER_MASK_CROP: "Crop image to mask",
                RENDER_MASK.RENDER_MASK_BLACK: "Set mask area to absolue black (0)",
                RENDER_MASK.RENDER_MASK_VIDEO: "Set mask area to video black (16/255)",
                RENDER_MASK.RENDER_MASK_FILM: "Set mask area to film black (95/1023)",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_MASK}

RENDER_MASK_CROP=-1
RENDER_MASK_BLACK=0
RENDER_MASK_VIDEO=64
RENDER_MASK_FILM=95
#  RENDER_NCLC_TAG : Which NCLC tag to use in QuickTime Movie files for colourimetry
#    RENDER_NCLC_LEGACY : Use legacy NCLC tag
#    RENDER_NCLC_AUTOMATIC : Use NCLC tag based on RenderColourSpace
if sys.version_info[0] >= 3:
    class RENDER_NCLC_TAG(enum.Enum):
        RENDER_NCLC_LEGACY=0
        RENDER_NCLC_AUTOMATIC=1
        def describe(self):
            descs = {
                RENDER_NCLC_TAG.RENDER_NCLC_LEGACY: "Use legacy NCLC tag",
                RENDER_NCLC_TAG.RENDER_NCLC_AUTOMATIC: "Use NCLC tag based on RenderColourSpace",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_NCLC_TAG}

RENDER_NCLC_LEGACY=0
RENDER_NCLC_AUTOMATIC=1
#  RENDER_TAPENAME_SOURCE : Which tape name to embed into rendered output
#    RENDER_TAPENAME_FILE : Source File Tape Name
#    RENDER_TAPENAME_SHOT : Shot Tape Name
#    RENDER_TAPENAME_CLIP : Shot Clip Name
#    RENDER_TAPENAME_STRIP : Tape Name from Strip Name
if sys.version_info[0] >= 3:
    class RENDER_TAPENAME_SOURCE(enum.Enum):
        RENDER_TAPENAME_FILE=0
        RENDER_TAPENAME_SHOT=1
        RENDER_TAPENAME_CLIP=3
        RENDER_TAPENAME_STRIP=2
        def describe(self):
            descs = {
                RENDER_TAPENAME_SOURCE.RENDER_TAPENAME_FILE: "Source File Tape Name",
                RENDER_TAPENAME_SOURCE.RENDER_TAPENAME_SHOT: "Shot Tape Name",
                RENDER_TAPENAME_SOURCE.RENDER_TAPENAME_CLIP: "Shot Clip Name",
                RENDER_TAPENAME_SOURCE.RENDER_TAPENAME_STRIP: "Tape Name from Strip Name",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_TAPENAME_SOURCE}

RENDER_TAPENAME_FILE=0
RENDER_TAPENAME_SHOT=1
RENDER_TAPENAME_CLIP=3
RENDER_TAPENAME_STRIP=2
#  RENDER_TIMECODE_SOURCE : Which timecode to embed into rendered output
#    RENDER_TIMECODE_FILETC1 : File Timecode 1
#    RENDER_TIMECODE_FILETC2 : File Timecode 2
#    RENDER_TIMECODE_SHOTTC : Shot Timecode
#    RENDER_TIMECODE_RECTC : Record (Timeline) Timecode
if sys.version_info[0] >= 3:
    class RENDER_TIMECODE_SOURCE(enum.Enum):
        RENDER_TIMECODE_FILETC1=0
        RENDER_TIMECODE_FILETC2=3
        RENDER_TIMECODE_SHOTTC=2
        RENDER_TIMECODE_RECTC=1
        def describe(self):
            descs = {
                RENDER_TIMECODE_SOURCE.RENDER_TIMECODE_FILETC1: "File Timecode 1",
                RENDER_TIMECODE_SOURCE.RENDER_TIMECODE_FILETC2: "File Timecode 2",
                RENDER_TIMECODE_SOURCE.RENDER_TIMECODE_SHOTTC: "Shot Timecode",
                RENDER_TIMECODE_SOURCE.RENDER_TIMECODE_RECTC: "Record (Timeline) Timecode",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in RENDER_TIMECODE_SOURCE}

RENDER_TIMECODE_FILETC1=0
RENDER_TIMECODE_FILETC2=3
RENDER_TIMECODE_SHOTTC=2
RENDER_TIMECODE_RECTC=1
#  ROP_TEXT_ALIGN : Text alignment
#    ROP_TEXT_ALIGN_LEFT : Left
#    ROP_TEXT_ALIGN_CENTER : Center
#    ROP_TEXT_ALIGN_RIGHT : Right
if sys.version_info[0] >= 3:
    class ROP_TEXT_ALIGN(enum.Enum):
        ROP_TEXT_ALIGN_LEFT=0
        ROP_TEXT_ALIGN_CENTER=1
        ROP_TEXT_ALIGN_RIGHT=2
        def describe(self):
            descs = {
                ROP_TEXT_ALIGN.ROP_TEXT_ALIGN_LEFT: "Left",
                ROP_TEXT_ALIGN.ROP_TEXT_ALIGN_CENTER: "Center",
                ROP_TEXT_ALIGN.ROP_TEXT_ALIGN_RIGHT: "Right",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in ROP_TEXT_ALIGN}

ROP_TEXT_ALIGN_LEFT=0
ROP_TEXT_ALIGN_CENTER=1
ROP_TEXT_ALIGN_RIGHT=2
#  SEQRESAMPLE_MODE : Sequence Resample Mode to use when resampling a sequence to a different video frame rate
#    SEQRESAMPLE_SNAP_TO_FRAME : Snap to Frame
#    SEQRESAMPLE_ROLLING_MAX : Mix Nearest Frames
#    SEQRESAMPLE_OPTICAL_FLOW : Optical Flow
if sys.version_info[0] >= 3:
    class SEQRESAMPLE_MODE(enum.Enum):
        SEQRESAMPLE_SNAP_TO_FRAME="SnapToFrame"
        SEQRESAMPLE_ROLLING_MAX="RollingMix"
        SEQRESAMPLE_OPTICAL_FLOW="OpticalFlow"
        def describe(self):
            descs = {
                SEQRESAMPLE_MODE.SEQRESAMPLE_SNAP_TO_FRAME: "Snap to Frame",
                SEQRESAMPLE_MODE.SEQRESAMPLE_ROLLING_MAX: "Mix Nearest Frames",
                SEQRESAMPLE_MODE.SEQRESAMPLE_OPTICAL_FLOW: "Optical Flow",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in SEQRESAMPLE_MODE}

SEQRESAMPLE_SNAP_TO_FRAME="SnapToFrame"
SEQRESAMPLE_ROLLING_MAX="RollingMix"
SEQRESAMPLE_OPTICAL_FLOW="OpticalFlow"
#  STEREO_EYE : Stereo eye
#    STEREOEYE_MONO : Mono (no stereo)
#    STEREOEYE_LEFT : Left eye
#    STEREOEYE_RIGHT : Right eye
if sys.version_info[0] >= 3:
    class STEREO_EYE(enum.Enum):
        STEREOEYE_MONO="GMSE_MONO"
        STEREOEYE_LEFT="GMSE_LEFT"
        STEREOEYE_RIGHT="GMSE_RIGHT"
        def describe(self):
            descs = {
                STEREO_EYE.STEREOEYE_MONO: "Mono (no stereo)",
                STEREO_EYE.STEREOEYE_LEFT: "Left eye",
                STEREO_EYE.STEREOEYE_RIGHT: "Right eye",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STEREO_EYE}

STEREOEYE_MONO="GMSE_MONO"
STEREOEYE_LEFT="GMSE_LEFT"
STEREOEYE_RIGHT="GMSE_RIGHT"
#  STILLEXPORT_BURNIN : Values for StillExportSettings Burnin
if sys.version_info[0] >= 3:
    class STILLEXPORT_BURNIN(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_BURNIN}

#  STILLEXPORT_DECODEQUALITY : Values for StillExportSettings DecodeQuality
#    STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH : Max Quality	Decode at maximum resolution
#    STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED : Optimised	Decode at half resolution where possible, for speed
#    STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT : Draft	Decode at draft quality, for maximum speed
if sys.version_info[0] >= 3:
    class STILLEXPORT_DECODEQUALITY(enum.Enum):
        STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH="GMDQ_OPTIMISED_UNLESS_HIGH"
        STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED="GMDQ_OPTIMISED"
        STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT="GMDQ_DRAFT"
        def describe(self):
            descs = {
                STILLEXPORT_DECODEQUALITY.STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH: "Max Quality	Decode at maximum resolution",
                STILLEXPORT_DECODEQUALITY.STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED: "Optimised	Decode at half resolution where possible, for speed",
                STILLEXPORT_DECODEQUALITY.STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT: "Draft	Decode at draft quality, for maximum speed",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_DECODEQUALITY}

STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH="GMDQ_OPTIMISED_UNLESS_HIGH"
STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED="GMDQ_OPTIMISED"
STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT="GMDQ_DRAFT"
#  STILLEXPORT_FILETYPE : Values for StillExportSettings FileType
if sys.version_info[0] >= 3:
    class STILLEXPORT_FILETYPE(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_FILETYPE}

#  STILLEXPORT_FORMAT : Values for StillExportSettings Format
if sys.version_info[0] >= 3:
    class STILLEXPORT_FORMAT(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_FORMAT}

#  STILLEXPORT_MASK : Values for StillExportSettings Mask
if sys.version_info[0] >= 3:
    class STILLEXPORT_MASK(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_MASK}

#  STILLEXPORT_MASKMODE : Values for StillExportSettings MaskMode
#    STILLEXPORT_MASKMODE_CROP : Crop Image To Mask
#    STILLEXPORT_MASKMODE_HARDBLACK : Hard Black (0) Mask
#    STILLEXPORT_MASKMODE_VIDEOBLACK : Video Black (16/255) Mask
#    STILLEXPORT_MASKMODE_FILMBLACK : Film Black (95/1023) Mask
if sys.version_info[0] >= 3:
    class STILLEXPORT_MASKMODE(enum.Enum):
        STILLEXPORT_MASKMODE_CROP="Crop"
        STILLEXPORT_MASKMODE_HARDBLACK="HardBlack"
        STILLEXPORT_MASKMODE_VIDEOBLACK="VideoBlack"
        STILLEXPORT_MASKMODE_FILMBLACK="FilmBlack"
        def describe(self):
            descs = {
                STILLEXPORT_MASKMODE.STILLEXPORT_MASKMODE_CROP: "Crop Image To Mask",
                STILLEXPORT_MASKMODE.STILLEXPORT_MASKMODE_HARDBLACK: "Hard Black (0) Mask",
                STILLEXPORT_MASKMODE.STILLEXPORT_MASKMODE_VIDEOBLACK: "Video Black (16/255) Mask",
                STILLEXPORT_MASKMODE.STILLEXPORT_MASKMODE_FILMBLACK: "Film Black (95/1023) Mask",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_MASKMODE}

STILLEXPORT_MASKMODE_CROP="Crop"
STILLEXPORT_MASKMODE_HARDBLACK="HardBlack"
STILLEXPORT_MASKMODE_VIDEOBLACK="VideoBlack"
STILLEXPORT_MASKMODE_FILMBLACK="FilmBlack"
#  STILLEXPORT_RESOLUTION : Values for StillExportSettings Resolution
if sys.version_info[0] >= 3:
    class STILLEXPORT_RESOLUTION(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_RESOLUTION}

#  STILLEXPORT_TRUELIGHT : Values for StillExportSettings Truelight
if sys.version_info[0] >= 3:
    class STILLEXPORT_TRUELIGHT(enum.Enum):
        def describe(self):
            descs = {
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in STILLEXPORT_TRUELIGHT}

#  SVGFITMODE : Controls how an SVG is transformed/fitted into a shape strip's 'target area' (the working format area or an optional mask area transformed to the working format).
#    SVGFITMODE_NONE : The SVG is translated to the corner of the target area. No Scaling is applied.
#    SVGFITMODE_BEST : The SVG image is translated to the centre of the target area and pillarboxed or letterboxed to fit the target area's height or width respectively.
#    SVGFITMODE_STRETCH : The SVG is stretched horizontally and vertically to fit the target area.
if sys.version_info[0] >= 3:
    class SVGFITMODE(enum.Enum):
        SVGFITMODE_NONE="None"
        SVGFITMODE_BEST="Best"
        SVGFITMODE_STRETCH="Stretch"
        def describe(self):
            descs = {
                SVGFITMODE.SVGFITMODE_NONE: "The SVG is translated to the corner of the target area. No Scaling is applied.",
                SVGFITMODE.SVGFITMODE_BEST: "The SVG image is translated to the centre of the target area and pillarboxed or letterboxed to fit the target area's height or width respectively.",
                SVGFITMODE.SVGFITMODE_STRETCH: "The SVG is stretched horizontally and vertically to fit the target area.",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in SVGFITMODE}

SVGFITMODE_NONE="None"
SVGFITMODE_BEST="Best"
SVGFITMODE_STRETCH="Stretch"
#  VIDEOLUT : Video Scaling LUT
#    VIDEOLUT_NONE : No video scaling LUT applied
#    VIDEOLUT_SCALE : Full to Legal Scale
#    VIDEOLUT_SCALE_NOCLIP : Full to Legal Scale (Unclipped)
#    VIDEOLUT_UNSCALE : Legal to Full Scale
#    VIDEOLUT_FULLRANGE_SOFTCLIP : Soft Clip to Full Range
#    VIDEOLUT_CLIP : Clip to Legal
#    VIDEOLUT_SOFTCLIP : Soft Clip to Legal
if sys.version_info[0] >= 3:
    class VIDEOLUT(enum.Enum):
        VIDEOLUT_NONE="none"
        VIDEOLUT_SCALE="scale"
        VIDEOLUT_SCALE_NOCLIP="scalenoclip"
        VIDEOLUT_UNSCALE="unscale"
        VIDEOLUT_FULLRANGE_SOFTCLIP="fullrangesoftclip"
        VIDEOLUT_CLIP="clip"
        VIDEOLUT_SOFTCLIP="softclip"
        def describe(self):
            descs = {
                VIDEOLUT.VIDEOLUT_NONE: "No video scaling LUT applied",
                VIDEOLUT.VIDEOLUT_SCALE: "Full to Legal Scale",
                VIDEOLUT.VIDEOLUT_SCALE_NOCLIP: "Full to Legal Scale (Unclipped)",
                VIDEOLUT.VIDEOLUT_UNSCALE: "Legal to Full Scale",
                VIDEOLUT.VIDEOLUT_FULLRANGE_SOFTCLIP: "Soft Clip to Full Range",
                VIDEOLUT.VIDEOLUT_CLIP: "Clip to Legal",
                VIDEOLUT.VIDEOLUT_SOFTCLIP: "Soft Clip to Legal",
            }
            return descs.get(self)

        def as_dict():
            return {x:x.describe() for x in VIDEOLUT}

VIDEOLUT_NONE="none"
VIDEOLUT_SCALE="scale"
VIDEOLUT_SCALE_NOCLIP="scalenoclip"
VIDEOLUT_UNSCALE="unscale"
VIDEOLUT_FULLRANGE_SOFTCLIP="fullrangesoftclip"
VIDEOLUT_CLIP="clip"
VIDEOLUT_SOFTCLIP="softclip"

###############################################################################
# Value Types
from .APIPermissionInfo import APIPermissionInfo
from .APIUserInfo import APIUserInfo
from .AudioSequenceSettings import AudioSequenceSettings
from .AudioSyncProgress import AudioSyncProgress
from .AudioSyncSettings import AudioSyncSettings
from .BLGExportSettings import BLGExportSettings
from .CDLExportSettings import CDLExportSettings
from .CategoryInfo import CategoryInfo
from .ClientViewClientSettings import ClientViewClientSettings
from .ClientViewHostUserSettings import ClientViewHostUserSettings
from .ClientViewStreamSettings import ClientViewStreamSettings
from .ColourSpaceInfo import ColourSpaceInfo
from .ConnectionInfo import ConnectionInfo
from .CubeExportSettings import CubeExportSettings
from .CustomerInfo import CustomerInfo
from .DRTInfo import DRTInfo
from .DecodeParameterChoice import DecodeParameterChoice
from .DecodeParameterDefinition import DecodeParameterDefinition
from .DiagHostResult import DiagHostResult
from .DiagInfo import DiagInfo
from .DiagProgress import DiagProgress
from .DiagResult import DiagResult
from .DialogItem import DialogItem
from .EnumInfo import EnumInfo
from .ExportOpInfo import ExportOpInfo
from .ExportProgress import ExportProgress
from .FormatBurninItem import FormatBurninItem
from .FormatInfo import FormatInfo
from .FormatMapping import FormatMapping
from .FormatMask import FormatMask
from .FrameRange import FrameRange
from .KeyTextItem import KeyTextItem
from .LicenceItem import LicenceItem
from .LookInfo import LookInfo
from .MetadataItem import MetadataItem
from .MetadataProperty import MetadataProperty
from .MultiPasteProgress import MultiPasteProgress
from .MultiPasteSettings import MultiPasteSettings
from .NewSceneOptions import NewSceneOptions
from .OpenSceneStatus import OpenSceneStatus
from .QueueLogItem import QueueLogItem
from .QueueOp import QueueOp
from .QueueOpStatus import QueueOpStatus
from .QueueOpTask import QueueOpTask
from .Rational import Rational
from .RenderCodecInfo import RenderCodecInfo
from .RenderCodecParameterInfo import RenderCodecParameterInfo
from .RenderCodecParameterValue import RenderCodecParameterValue
from .RenderDeliverable import RenderDeliverable
from .RenderFileTypeInfo import RenderFileTypeInfo
from .RenderOpInfo import RenderOpInfo
from .RenderProcessorLogItem import RenderProcessorLogItem
from .RenderStatus import RenderStatus
from .SDKVersion import SDKVersion
from .SceneInfo import SceneInfo
from .ScenePath import ScenePath
from .SceneSettingDefinition import SceneSettingDefinition
from .ShotIndexRange import ShotIndexRange
from .ShotInfo import ShotInfo
from .StillExportSettings import StillExportSettings
from .VolumeInfo import VolumeInfo
###############################################################################
# Classes
from .APITest import APITest
from .Application import Application
from .AudioSync import AudioSync
from .ClientViewManager import ClientViewManager
from .CurrentGrade import CurrentGrade
from .Cursor import Cursor
from .Diagnostics import Diagnostics
from .DynamicDialog import DynamicDialog
from .Export import Export
from .Filesystem import Filesystem
from .Format import Format
from .FormatBurnin import FormatBurnin
from .FormatSet import FormatSet
from .Image import Image
from .ImageSearcher import ImageSearcher
from .JobManager import JobManager
from .Licence import Licence
from .Mark import Mark
from .Menu import Menu
from .MenuItem import MenuItem
from .MultiPaste import MultiPaste
from .ProgressDialog import ProgressDialog
from .QueueManager import QueueManager
from .RenderProcessor import RenderProcessor
from .RenderSetup import RenderSetup
from .Scene import Scene
from .SceneSettings import SceneSettings
from .SequenceDescriptor import SequenceDescriptor
from .Shot import Shot
from .SystemInfo import SystemInfo
from .ThumbnailManager import ThumbnailManager
from .Timer import Timer
from .Utilities import Utilities
from .Volumes import Volumes
from .WebConfig import WebConfig
