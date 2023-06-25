///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
//
// FilmLight API for NodeJS v6.x +
//
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

'use strict'

const util = require("util");
const events = require("events");
const WebSocketClient = require("websocket").client;
const fs = require("fs");
const path = require("path");

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
//
// Type library
//
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

var Library = class Library
{
    constructor()
    {
        this.Classes = {};
        this.ValueTypes = {};
    }

    register_class( name, cls ) 
    {
        if( name == null )
            throw "Attempt to register class with no name";

        if( cls == null )
            throw "Attempt to register class " + name + " with no class definition";

        this.Classes[name] = cls;
    }

    register_value_type( key, cls )
    {
        this.ValueTypes[key] = cls;
    }

    get_class( name )
    {
        return this.Classes[name];
    }

    get_classes()
    {
        return Object.keys(this.Classes);
    }

    create_instance(clsname, conn, target)
    {
        var cls = this.Classes[clsname];
        if( cls == null )
            throw "Undefined FLAPI class " + clsname;

        return new cls(conn, target);
    }

    create_value_type(key, obj)
    {
        var cls = this.ValueTypes[key];
        if( cls == null )
            throw "Undefined FLAPI class " + clsname;

        return new cls(obj);
    }
};

// Instance of type library
var library = new Library();

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
//
// Basic types
//
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
//
// Interface - base class for all public interfaces

var Interface = class Interface
{
    constructor( conn, target )
    {
        this.conn = conn;
        this.target = target;
        this.sighandlers = {};
    }

    // release()
    //
    // Release resources for this object
    //
    // Call when object is no longer required by client.
    
    release()
    {
        if( this.target == null )
            throw "Attempt to release an object with no instance";
        this.conn.forget( this.target );
        this.target = null;
    }

    // connect( signal, handler )
    // 
    // Register handler for named signal
    //
    // handler will be called with the following arguments:
    //      from - object that emitted the signal
    //      signal - name of signal
    //      args - arguments for emitted signal
    //
    connect( signal, handler )
    {
        if( this.sighandlers[signal] == null )
        {
            this.sighandlers[signal] = new Set();
            this.conn.connect_signal( this.target, signal );
        }

        this.sighandlers[signal].add( handler );
    }

    // disconnect( signal, handler )
    // 
    // Remove handler for named signal
    //
    disconnect( signal, handler )
    {
        var sighandlers = this.sighandlers[signal];
        if( sighandlers == null )
            return;

        sighandlers.delete(handler);
        if( sighandlers.size == 0 )
        {
            this.conn.disconnect_signal( this.target, signal );
            this.sighandlers[ signal ] = null;
        }
    }

    //// Internal

    // dispatch_signal( signal, args )
    //
    // Call all registered handlers for the named signal
    // Pass args to each handler.
    //
    dispatch_signal( signal, args )
    {
        var sighandlers = this.sighandlers[signal];
        if( sighandlers )
            sighandlers.forEach( (handler) => { handler(this, signal, args); } );
    }
};

///////////////////////////////////////////////////////////////////////////////
//
// Timecode

var Timecode = class Timecode 
{
    constructor( obj )
    {
        this.h = obj.h;
        this.m = obj.m;
        this.s = obj.s;
        this.f = obj.f;
        this.phase = obj.phase;
        this.fps = obj.fps;
        this.wrap = obj.wrap;
    }

    toJSON() 
    {
        return {
            "_type": "timecode",
            "h": this.h, 
            "m": this.m, 
            "s": this.s, 
            "f": this.f, 
            "phase": this.phase, 
            "fps": this.fps, 
            "wrap": this.wrap
        };
    }
};

library.register_value_type( "timecode", Timecode );

module.exports.Timecode = Timecode;

///////////////////////////////////////////////////////////////////////////////
//
// Keycode

var Keycode = class Keycode
{
    constructor( obj )
    {
        this.stock = obj.stock;
        this.feet = obj.feet;
        this.frames = obj.frames;
        this.perfs = obj.perfs;
        this.gearing = obj.gearing;
    }

    toJSON() 
    {
        return {
            "_type": "keycode",
            "stock": this.stock,
            "feet": this.feet,
            "frames": this.frames,
            "perfs": this.perfs,
            "gearing": this.gearing
        };
    }
};

library.register_value_type( "keycode", Keycode );

module.exports.Keycode = Keycode;

///////////////////////////////////////////////////////////////////////////////
//
// FrameNumber

var FrameNumber = class FrameNumber
{
    constructor( obj )
    {
        this.frame = obj.frame;
    }

    toJSON() 
    {
        return {
            "_type": "framenumber",
            "frame": this.frame
        };
    }
};

library.register_value_type( "framenumber", FrameNumber );

module.exports.FrameNumber = FrameNumber;

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
//
// Connection
//
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
    
var Connection = class Connection extends events.EventEmitter 
{
    constructor(hostname, port, username, password, token)
    {
        super();
        
        if( hostname != null )
            this.hostname = hostname;
        else
            this.hostname = "localhost";

        if( port )
            this.port = port;
        else
            this.port = 1984;

        if( username == null )
            username = process.env.USER;

        if( token == null )
        {
            /* Try and read token for FLAPI_TOKEN */
            token = process.env.FLAPI_TOKEN;
        }
        if( token == null )
        {
            /* Try and read token from ~/.flapitoken */
            try
            {
                token = fs.readFileSync(path.join(process.env.HOME, ".filmlight", "flapi-token"), {encoding:"utf-8"});
            }
            catch
            {
                token = null;
            }
        }

        this.username = username;
        this.password = password;
        this.token = token;

        this.debug = 0; /* debug flag */
        this.msgid = 0; /* next msg id */
        this.objects = {}; /* dict of interface objects keyed by id */
        this.msgs = {}; /* dict of pending messages keyed by id */
        
        this.ws_client = null; /* WebSocket client */
        this.ws_conn = null; /* WebSocket connection */

        /* create instance of each Class and assign to connection.
         * used for calling static class functions.
         */
        var classes = library.get_classes();
        for( var ix in classes )
        {
            var clsname = classes[ix];
            this[clsname] = library.create_instance( clsname, this, null );
        }
    }

    set_debug(enabled)
    {
        this.debug = enabled;
    }

    connect()
    {
        if( this.ws_client == null )
        {
            return new Promise( (resolve, reject) => {
                this.ws_client = new WebSocketClient();
                this.ws_client.on("connect", 
                    (conn) => { 
                        this.on_connect(conn, resolve); 
                    }
                );
                this.ws_client.on("connectFailed", 
                    (error) => { 
                        this.on_connect_failed(error); 
                        reject(error);
                    } 
                );

                this.ws_client.connect( "ws://" + this.hostname + ":" + this.port + "/" );
            });
        }
        else
        {
            return Promise().resolve( this );
        }
    }

    close()
    {
        if( this.ws_conn )
        {
            this.ws_conn.close();
            this.ws_conn = null;
        }

        this.ws_client = null;
    }

    on_connect(connection, resolve) 
    {
        if( this.debug )
            console.log( "FLAPI connected to " + this.hostname );
        
        this.ws_conn = connection;
        this.ws_conn.on("message", (msg) => { this.read_msg(msg); } );
        this.ws_conn.on("error", (error) => { this.on_conn_error(error); } );
        this.ws_conn.on("close", () => { this.on_conn_close(); } );

        this.send_connect().then( () => {
            this.emit( "connected", this );
            resolve( this );
        });
    }

    on_connect_failed(error)
    {
        if( this.debug )
            console.log( "FLAPI connect failed: " + error.toString() );

        this.emit( "connectFailed", this, error );
    }

    on_conn_error(error) 
    {
        if( this.debug )
            console.log( "FLAPI connect error: " + error.toString() );

        this.emit( "error", this, error );
    }

    on_conn_close()
    {
        this.ws_conn = null;
        this.emit( "close", this );
    }

    read_msg(msg)
    {
        if( this.debug )
            console.log( "FLAPI received: " + msg.utf8Data );

        if( msg.type === "utf8" )
        {
            var reply = JSON.parse( msg.utf8Data, (k,v) => { return this.decode_obj(k,v); } ); 
            
            /* Handle async signal */
            if( reply.method == "signal" )
            {
                if( reply.target == null )
                {
                    this.emit( "error", this, "signal message has no target" );
                    return;
                }

                var obj = this.objects[ reply.target ];
                if( obj == null )
                {
                    this.emit( "error", this, "object for signal target id " + reply.target + " cannot be found" );
                    return;
                }

                obj.dispatch_signal( reply.params.signal, reply.params.args );
                return;
            }
            
            /* Handle method call result */
            var msg = this.msgs[ reply.id ];
            if( msg )
            {
                if( reply.error )
                    msg.reject( reply.error.message );
                else
                    msg.resolve( reply.result );

                delete this.msgs[reply.id];
            }
        }
    }

    encode_obj( k, v )
    {
        if( v instanceof Set )
        {
            var os = { "_type": "set" };
            for( var k of v )
                os[k] = 1;
            return os;
        }
        else
        {
            return v;
        }
    }

    decode_obj( k, v )
    {
        if( v != null && typeof v === 'object' )
        {
            if( v._handle != null )
            {
                /* Find existing handle */
                var o;
                o = this.objects[ v._id ];
                if( o != null )
                    return o;

                /* Create new handle */
                o = library.create_instance( v._handle, this, v._id );
                this.objects[ v._id ] = o;
                return o;
            }
            else if( v._type == "set" )
            {
                let os = new Set();
                for( var k in v )
                {
                    if( k != "_type" )
                        os.add(k);
                }

                return os;
            }
            else if( v._type != null )
            {
                let vto = library.create_value_type( v._type, v );
                if( vto == null )
                    throw "Unknown data type " + v._type;
                return vto;
            }
        }

        return v;
    }

    send_connect()
    {
        /* Send connect handshake */
        return new Promise( (resolve, reject) => {
            /* Send connect message */
            var id = this.msgid++;
            var msg = {
                "jsonrpc": "2.0",
                "id": id,
                "method": "connect",
                "username": this.username,
                "password": this.password,
                "token": this.token
            };
            
            this.msgs[id] = { "resolve": resolve, "reject": reject };
           
            var msgjson = JSON.stringify(msg, this.encode_obj);
            if( this.debug )
                console.log( "FLAPI send: " + msgjson );

            this.ws_conn.sendUTF( msgjson );
        });
    }

    call( target, method, params )
    {
        return new Promise( (resolve, reject) => {
            var id = this.msgid++;
            var msg = {
                "jsonrpc": "2.0",
                "id": id,
                "method": method,
                "target": target,
                "params": params,
            };
            
            this.msgs[id] = { "resolve": resolve, "reject": reject };
            
            var msgjson = JSON.stringify(msg, this.encode_obj );
            if( this.debug )
                console.log( "FLAPI send: " + msgjson );

            this.ws_conn.sendUTF( msgjson );
        });
    }
    
    connect_signal( target, signal )
    {
        var id = this.msgid++;
        var msg = {
            "jsonrpc": "2.0",
            "id": id,
            "method": "connect_signal",
            "target": target,
            "params": { "signal": signal }
        };
       
        var msgjson = JSON.stringify(msg, this.encode_obj);
        if( this.debug )
            console.log( "FLAPI send: " + msgjson );

        this.ws_conn.sendUTF( msgjson );
    }

    disconnect_signal( target, signal )
    {
        var id = this.msgid++;
        var msg = {
            "jsonrpc": "2.0",
            "id": id,
            "method": "disconnect_signal",
            "target": target,
            "params": { "signal": signal }
        };
        
        var msgjson = JSON.stringify(msg, this.encode_obj);
        if( this.debug )
            console.log( "FLAPI send: " + msgjson );
        
        this.ws_conn.sendUTF( msgjson );
    }
    
    forget( target )
    {
        var msg = {
            "jsonrpc": "2.0",
            "method": "forget",
            "target": target,
        };
        
        var msgJson = JSON.stringify(msg, this.encode_obj);
        if( this.debug )    
            console.log( "FLAPI send: " + msgJson );
        
        this.ws_conn.sendUTF( msgJson );
    }
};

module.exports.Connection = Connection;

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
//
// Interfaces
//
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// APITest
//
// Test API fundamentals
//

var APITest = class APITest extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "APITest", "_id": this.target };
    }

    // APITest.create
    //
    // Create an instance of the APITest object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (APITest): APITest object
    //
    create()
    {
        return this.conn.call(
            null,
            "APITest.create",
            {
            }
        );
    }

    // APITest.get
    //
    // Return client-specific instance of APITest 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (APITest): APITest object
    //
    get()
    {
        return this.conn.call(
            null,
            "APITest.get",
            {
            }
        );
    }

    // APITest.send_test_signal
    //
    // Emit TestSignal 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    No result
    //
    send_test_signal()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "APITest.send_test_signal",
            {
            }
        );
    }

    // APITest.defer_test_signal
    //
    // Emit TestSignal asynchronously after a delay 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    No result
    //
    defer_test_signal()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "APITest.defer_test_signal",
            {
            }
        );
    }

    // APITest.promise_test
    //
    // This function will do something time-consuming by returning a promise, making it asynchronous 
    //
    // Arguments:
    //    'value' (string): Value to return via promise
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Result
    //
    promise_test(value)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "APITest.promise_test",
            {
                'value': value,
            }
        );
    }

    // APITest.fail
    //
    // This method is expected to fail with an error message 'FAIL' 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    fail()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "APITest.fail",
            {
            }
        );
    }

};
library.register_class( 'APITest', APITest )
module.exports.APITest = APITest;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Application
//
// Access information about the target application
//

var Application = class Application extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Application", "_id": this.target };
    }

    // Application.get_application_info
    //
    // Information describing the application exposed via the FilmLight API 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Application Info
    //        'Build' (string): Build number i.e. 10000
    //        'Major' (string): Major version number, i.e. 5
    //        'Minor' (string): Minor version number, i.e. 0
    //        'Name' (string): Application Name, i.e. 'flapi'
    //        'Path' (string): Path to the application
    //        'Product' (string): Product Name, i.e. 'Baselight'
    //
    get_application_info()
    {
        return this.conn.call(
            null,
            "Application.get_application_info",
            {
            }
        );
    }

    // Application.get_sdk_versions
    //
    // Get SDK version information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of SDKVersion objects
    //        '<n>' (SDKVersion): 
    //
    get_sdk_versions()
    {
        return this.conn.call(
            null,
            "Application.get_sdk_versions",
            {
            }
        );
    }

    // Application.get_connections_info
    //
    // Get array of current connections. Each entry in the array will be a ConnectionInfo object describing that connection. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of connection info objects
    //        '<n>' (ConnectionInfo): 
    //
    get_connections_info()
    {
        return this.conn.call(
            null,
            "Application.get_connections_info",
            {
            }
        );
    }

    // Application.get_video_streaming_supported
    //
    // Is video streaming supported (hardware, setup & licensed) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if streaming supported, 0 if not
    //
    get_video_streaming_supported()
    {
        return this.conn.call(
            null,
            "Application.get_video_streaming_supported",
            {
            }
        );
    }

    // Application.get_video_streaming_enabled
    //
    // Is video streaming currently enabled 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if streaming enabled, 0 if not
    //
    get_video_streaming_enabled()
    {
        return this.conn.call(
            null,
            "Application.get_video_streaming_enabled",
            {
            }
        );
    }

    // Application.get_video_stream_address
    //
    // Return address for video stream 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Address for video stream access. Used by Client View.
    //
    get_video_stream_address()
    {
        return this.conn.call(
            null,
            "Application.get_video_stream_address",
            {
            }
        );
    }

    // Application.is_playing
    //
    // Is playback currently in progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if playback in progress, 0 if not
    //
    is_playing()
    {
        return this.conn.call(
            null,
            "Application.is_playing",
            {
            }
        );
    }

    // Application.get
    //
    // Return instance of the Application object (typically for signal connection) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Application): Returns Application object
    //
    get()
    {
        return this.conn.call(
            null,
            "Application.get",
            {
            }
        );
    }

    // Application.get_current_scene
    //
    // Return the currently active Scene within the application 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): Current Scene
    //
    get_current_scene()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_current_scene",
            {
            }
        );
    }

    // Application.get_current_scene_name
    //
    // Return the name of the currently active Scene within the application 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Current Scene name
    //
    get_current_scene_name()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_current_scene_name",
            {
            }
        );
    }

    // Application.get_open_scene_names
    //
    // Return array of names of scenes currently open in the application. 
    // You can get the Scene object for a given name by calling get_scene_by_name(). 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Scene Names
    //        '<n>' (string): Scene Name
    //
    get_open_scene_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_open_scene_names",
            {
            }
        );
    }

    // Application.get_scene_by_name
    //
    // Return the Scene object for the scene with the given name. 
    // If no matching scene can be found, NULL is returned. 
    //
    // Arguments:
    //    'name' (string): Name of Scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): Scene object for given scene name
    //
    get_scene_by_name(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_scene_by_name",
            {
                'name': name,
            }
        );
    }

    // Application.get_current_cursor
    //
    // Return the currently active Cursor within the application 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Cursor): Current Cursor
    //
    get_current_cursor()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_current_cursor",
            {
            }
        );
    }

    // Application.get_cursors
    //
    // Return active Cursor objects within the application 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Cursor objects
    //        '<n>' (Cursor): Cursor object representing active cursor in application
    //
    get_cursors()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_cursors",
            {
            }
        );
    }

    // Application.log
    //
    // Log message in application Log view 
    //
    // Arguments:
    //    'category' (string): Category of message
    //    'severity' (string): Severity of message, Hard, Soft or Transient
    //    'message' (string): Message to log
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    log(category, severity, message)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.log",
            {
                'category': category,
                'severity': severity,
                'message': message,
            }
        );
    }

    // Application.message_dialog
    //
    // Present a message box in the Application for the user to interact with 
    //
    // Arguments:
    //    'title' (string): Title of message box
    //    'message' (string): Contents of message box
    //    'buttons' (array): Array of buttons to show in dialog box
    //        '<n>' (string): Button label
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Label of button selected by user
    //
    message_dialog(title, message, buttons)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.message_dialog",
            {
                'title': title,
                'message': message,
                'buttons': buttons,
            }
        );
    }

    // Application.list_dialog
    //
    // Present a dialog to the user containing a list of items that the user can select from 
    //
    // Arguments:
    //    'title' (string): Title of list dialog
    //    'message' (string): Message to show in list dialog
    //    'items' (array): Array of items to show in list
    //        '<n>' (KeyTextItem): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (any): Key of selected object, or NULL if no selection
    //
    list_dialog(title, message, items)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.list_dialog",
            {
                'title': title,
                'message': message,
                'items': items,
            }
        );
    }

    // Application.set_custom_data
    //
    // Set a custom data value in the application with the supplied (string) key. Existing custom 
    // data values can be deleted from the application by supplying NULL/None/null as the data value 
    // (for an existing key). 
    //
    // Arguments:
    //    'data_key' (string): Custom data value key
    //    'data_value' (any): New data value for the given key (or NULL/None/null to delete) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_custom_data(data_key, data_value = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.set_custom_data",
            {
                'data_key': data_key,
                'data_value': data_value,
            }
        );
    }

    // Application.get_custom_data
    //
    // Get a custom data value from the application previously set using set_custom_data. 
    //
    // Arguments:
    //    'data_key' (string): Custom data value key
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (any): Custom data value found
    //
    get_custom_data(data_key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_custom_data",
            {
                'data_key': data_key,
            }
        );
    }

    // Application.get_custom_data_keys
    //
    // Return sorted array of (string) keys that can be used to fetch application 
    // custom data values via get_custom_data. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (string): Key string
    //
    get_custom_data_keys()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Application.get_custom_data_keys",
            {
            }
        );
    }

};
library.register_class( 'Application', Application )
module.exports.Application = Application;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// AudioSync
//
// audio sync operation
//

var AudioSync = class AudioSync extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "AudioSync", "_id": this.target };
    }

    // AudioSync.create
    //
    // Create a new audio sync operation object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (AudioSync): AudioSync object
    //
    create()
    {
        return this.conn.call(
            null,
            "AudioSync.create",
            {
            }
        );
    }

    // AudioSync.audio_sync
    //
    // Perform audio sync operation using the given audio sync settings 
    //
    // Arguments:
    //    'scene' (Scene): Target scene to AudioSync into
    //    'settings' (AudioSyncSettings): 
    //    'shot_ids' (array): Array of Shot IDs to apply audio sync operation to [Optional]
    //        '<n>' (number): Shot ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of shots updated by audio sync operation
    //
    audio_sync(scene, settings, shot_ids = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "AudioSync.audio_sync",
            {
                'scene': scene,
                'settings': settings,
                'shot_ids': shot_ids,
            }
        );
    }

    // AudioSync.get_log
    //
    // Return log of progress information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of audio sync progress information
    //        '<n>' (AudioSyncProgress): 
    //
    get_log()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "AudioSync.get_log",
            {
            }
        );
    }

};
library.register_class( 'AudioSync', AudioSync )
module.exports.AudioSync = AudioSync;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ClientViewManager
//
// Manages settings for connected Client Views.
//

var ClientViewManager = class ClientViewManager extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "ClientViewManager", "_id": this.target };
    }

    // ClientViewManager.get
    //
    // Get reference to the (singleton) ClientViewManager object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ClientViewManager): 
    //
    get()
    {
        return this.conn.call(
            null,
            "ClientViewManager.get",
            {
            }
        );
    }

    // ClientViewManager.get_host_user_settings
    //
    // Get object containing Settings for the Client View's host user 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ClientViewHostUserSettings): 
    //
    get_host_user_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_host_user_settings",
            {
            }
        );
    }

    // ClientViewManager.get_client_settings
    //
    // Get the connected Client View's config/settings object. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ClientViewClientSettings): 
    //
    get_client_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_client_settings",
            {
            }
        );
    }

    // ClientViewManager.get_stream_settings
    //
    // Get array of stream settings objects. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (ClientViewStreamSettings): 
    //
    get_stream_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_stream_settings",
            {
            }
        );
    }

    // ClientViewManager.get_streaming_enabled
    //
    // Is streaming currently enabled. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if streaming enabled, otherwise 0
    //
    get_streaming_enabled()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_streaming_enabled",
            {
            }
        );
    }

    // ClientViewManager.get_session_name
    //
    // Get the current Client View session name. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Current session name
    //
    get_session_name()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_session_name",
            {
            }
        );
    }

    // ClientViewManager.get_session_clients
    //
    // Get array of current session clients. Each entry in the array will be a ConnectionInfo object describing that connection. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of current session clients
    //        '<n>' (ConnectionInfo): 
    //
    get_session_clients()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.get_session_clients",
            {
            }
        );
    }

    // ClientViewManager.log
    //
    // Private routine used to log client view messages for debugging 
    //
    // Arguments:
    //    'category' (string): Category of message
    //    'message' (string): Message to log
    //    'severity' (string): Severity of message, Hard, Soft (warning) or Transient (info) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    log(category, message, severity = "ERR_INFO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.log",
            {
                'category': category,
                'message': message,
                'severity': severity,
            }
        );
    }

    // ClientViewManager.set_available_simad_actions
    //
    // Set debug actions availble to SimAd 
    //
    // Arguments:
    //    'actions' (object): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_available_simad_actions(actions)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ClientViewManager.set_available_simad_actions",
            {
                'actions': actions,
            }
        );
    }

};
library.register_class( 'ClientViewManager', ClientViewManager )
module.exports.ClientViewManager = ClientViewManager;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// CurrentGrade
//
//

var CurrentGrade = class CurrentGrade extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "CurrentGrade", "_id": this.target };
    }

    // CurrentGrade.get
    //
    // Get (singleton) current grade interface for the connected client 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (CurrentGrade): CurrentGrade object
    //
    get()
    {
        return this.conn.call(
            null,
            "CurrentGrade.get",
            {
            }
        );
    }

    // CurrentGrade.request_update_current_shot_signal
    //
    // Explicitly request an 'UpdateCurrentShot' signal. This can be useful, for example, when first connecting to the current grade module for initialising a client's internal state. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    No result
    //
    request_update_current_shot_signal()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "CurrentGrade.request_update_current_shot_signal",
            {
            }
        );
    }

    // CurrentGrade.get_current_cursor
    //
    // Get an interface to the cursor currently in use by Baselight for grading. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Cursor): Current cursor interface
    //
    get_current_cursor()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "CurrentGrade.get_current_cursor",
            {
            }
        );
    }

    // CurrentGrade.is_enabled
    //
    // Is this interface currently enabled. Note: The current grade interface may be arbitrarily enabled/disabled from the host application itself. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating whether the interface is currently enabled
    //
    is_enabled()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "CurrentGrade.is_enabled",
            {
            }
        );
    }

};
library.register_class( 'CurrentGrade', CurrentGrade )
module.exports.CurrentGrade = CurrentGrade;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Cursor
//
// Interface for accessing cursors within a scene.
//

var Cursor = class Cursor extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Cursor", "_id": this.target };
    }

    // Cursor.get_time
    //
    // Get cursor's position in the timeline in seconds 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Timeline time
    //
    get_time()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_time",
            {
            }
        );
    }

    // Cursor.get_frame
    //
    // Get cursor's position in the timeline as a frame number 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Timeline frame number
    //
    get_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_frame",
            {
            }
        );
    }

    // Cursor.get_record_timecode
    //
    // Get cursor's position in the timeline as a timecode 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Record timecode
    //
    get_record_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_record_timecode",
            {
            }
        );
    }

    // Cursor.get_viewing_format_name
    //
    // Get the name of the cursor's current viewing format. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Viewing format name
    //
    get_viewing_format_name()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_viewing_format_name",
            {
            }
        );
    }

    // Cursor.get_viewing_format_dims
    //
    // Get basic geometry (width, height and aspect ratio) of the cursor's current viewing format 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Viewing format dimensions
    //        'AspectRatio' (number): Viewing format pixel aspect ratio (for anamorphic formats)
    //        'Height' (number): Viewing format height
    //        'Width' (number): Viewing format width
    //
    get_viewing_format_dims()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_viewing_format_dims",
            {
            }
        );
    }

    // Cursor.get_viewing_format_mask_name
    //
    // Get current viewing format mask name 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatMask):  [Optional]
    //
    get_viewing_format_mask_name()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_viewing_format_mask_name",
            {
            }
        );
    }

    // Cursor.get_viewing_format_mask
    //
    // Get current viewing format mask rectangle 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatMask):  [Optional]
    //
    get_viewing_format_mask()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_viewing_format_mask",
            {
            }
        );
    }

    // Cursor.get_age
    //
    // Get the cursor's 'age'. The age is an integer, incremented whenever an attribute which could result in a visual change to the image display has been modfied. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Cursor age value
    //
    get_age()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.get_age",
            {
            }
        );
    }

    // Cursor.is_using_truelight
    //
    // Is Truelight currently in use (ie. a profile has been selected & Truelight is enabled) in this cursor. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating if Truelight is in use
    //
    is_using_truelight()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Cursor.is_using_truelight",
            {
            }
        );
    }

};
library.register_class( 'Cursor', Cursor )
module.exports.Cursor = Cursor;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Diagnostics
//
// Run diagnostics and query results
//

var Diagnostics = class Diagnostics extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Diagnostics", "_id": this.target };
    }

    // Diagnostics.get
    //
    // Create an instance of the Diagnostics module 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Diagnostics): 
    //
    get()
    {
        return this.conn.call(
            null,
            "Diagnostics.get",
            {
            }
        );
    }

    // Diagnostics.get_hosts
    //
    // Return list of hosts that diags will be run on 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of hostnames
    //        '<n>' (string): Hostname
    //
    get_hosts()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.get_hosts",
            {
            }
        );
    }

    // Diagnostics.get_groups
    //
    // Return list of diagnostic test groups 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of group names
    //        '<n>' (string): Group name
    //
    get_groups()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.get_groups",
            {
            }
        );
    }

    // Diagnostics.get_tests
    //
    // Return list of diagnostic test information 
    //
    // Arguments:
    //    'group' (string): Optional group name. Only return tests matching this group. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of diagnostics
    //        '<n>' (DiagInfo): 
    //
    get_tests(group = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.get_tests",
            {
                'group': group,
            }
        );
    }

    // Diagnostics.can_start
    //
    // Check to see if it is possible to start diagnostic tests 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating whether it is possible to start diagnostics tests
    //
    can_start()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.can_start",
            {
            }
        );
    }

    // Diagnostics.start
    //
    // Start diagnostic tests 
    //
    // Arguments:
    //    'weight' (string): Weight of tests to run [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    start(weight = "DIAGWEIGHT_MEDIUM")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.start",
            {
                'weight': weight,
            }
        );
    }

    // Diagnostics.start_specific
    //
    // Start a specific diagnostic test and any of its pre-requisites 
    //
    // Arguments:
    //    'test' (string): Name of diagnostic test
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    start_specific(test)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.start_specific",
            {
                'test': test,
            }
        );
    }

    // Diagnostics.cancel
    //
    // Cancel diagnostic test in progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    cancel()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.cancel",
            {
            }
        );
    }

    // Diagnostics.get_progress
    //
    // Return overall progress of diagnostic operation 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (DiagProgress): 
    //
    get_progress()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.get_progress",
            {
            }
        );
    }

    // Diagnostics.get_results
    //
    // Return results for all tests 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (DiagResult): 
    //
    get_results()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Diagnostics.get_results",
            {
            }
        );
    }

};
library.register_class( 'Diagnostics', Diagnostics )
module.exports.Diagnostics = Diagnostics;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DynamicDialog
//
// This class can be used to show a complex dialog box to the user
//

var DynamicDialog = class DynamicDialog extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "DynamicDialog", "_id": this.target };
    }

    // DynamicDialog.create
    //
    // Create a Dialog object 
    //
    // Arguments:
    //    'title' (string): Title of dialog
    //    'defns' (array): Array of items to show in dialog
    //        '<n>' (DialogItem): Definition for an individual item in the DynamicDialog
    //    'settings' (object): Dictionary of initial settings for dialog items
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (DynamicDialog): 
    //
    create(title, defns, settings)
    {
        return this.conn.call(
            null,
            "DynamicDialog.create",
            {
                'title': title,
                'defns': defns,
                'settings': settings,
            }
        );
    }

    // DynamicDialog.modal
    //
    // Display a Dialog object and return the settings 
    //
    // Arguments:
    //    'title' (string): Title of dialog
    //    'defns' (array): Array of items to show in dialog
    //        '<n>' (DialogItem): 
    //    'settings' (object): Dictionary of initial settings for dialog items
    //    'width' (number): Desired width of dialog box [Optional]
    //    'height' (number): Desired height of dialog box [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Settings chosen by user, or NULL if dialog was cancelled
    //
    modal(title, defns, settings, width = null, height = null)
    {
        return this.conn.call(
            null,
            "DynamicDialog.modal",
            {
                'title': title,
                'defns': defns,
                'settings': settings,
                'width': width,
                'height': height,
            }
        );
    }

    // DynamicDialog.show_modal
    //
    // Show dialog to user 
    //
    // Arguments:
    //    'width' (number): Desired width of dialog box [Optional]
    //    'height' (number): Desired height of dialog box [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Settings chosen by user, or NULL if dialog was cancelled
    //
    show_modal(width = null, height = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "DynamicDialog.show_modal",
            {
                'width': width,
                'height': height,
            }
        );
    }

    // DynamicDialog.get_settings
    //
    // Return current dialog settings 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): 
    //
    get_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "DynamicDialog.get_settings",
            {
            }
        );
    }

    // DynamicDialog.set_settings
    //
    // Set current dialog settings 
    //
    // Arguments:
    //    'settings' (object): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_settings(settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "DynamicDialog.set_settings",
            {
                'settings': settings,
            }
        );
    }

    // DynamicDialog.set_timer_callback
    //
    // Set time until callback signal TimerCallback will be sent 
    //
    // Arguments:
    //    'delay' (number): Time until signal in milliseconds
    //    'repeat' (number): Flag indicating signal should repeat until cancel_timer_callback is called [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_timer_callback(delay, repeat = 1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "DynamicDialog.set_timer_callback",
            {
                'delay': delay,
                'repeat': repeat,
            }
        );
    }

    // DynamicDialog.cancel_timer_callback
    //
    // Cancel any pending timer callback 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    cancel_timer_callback()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "DynamicDialog.cancel_timer_callback",
            {
            }
        );
    }

};
library.register_class( 'DynamicDialog', DynamicDialog )
module.exports.DynamicDialog = DynamicDialog;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Export
//
// Export operation
//

var Export = class Export extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Export", "_id": this.target };
    }

    // Export.create
    //
    // Create a new Export operation object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Export): Export object
    //
    create()
    {
        return this.conn.call(
            null,
            "Export.create",
            {
            }
        );
    }

    // Export.select_all
    //
    // Select all snots in Scene to export 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_all()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.select_all",
            {
            }
        );
    }

    // Export.clear_selection
    //
    // Clear selection of shots in Scene to export 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    clear_selection()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.clear_selection",
            {
            }
        );
    }

    // Export.select_shots
    //
    // Set the selection to the given Shots for rendering 
    //
    // Arguments:
    //    'shots' (array): Array of Shot objects to select
    //        '<n>' (Shot): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shots(shots)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.select_shots",
            {
                'shots': shots,
            }
        );
    }

    // Export.select_shot
    //
    // Add the given shot to the selection to be exported. 
    //
    // Arguments:
    //    'shot' (array): Shot to add to selection
    //        '<n>' (Shot): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shot(shot)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.select_shot",
            {
                'shot': shot,
            }
        );
    }

    // Export.do_export_BLG
    //
    // Perform export BLG operation using the given Export settings 
    //
    // Arguments:
    //    'queue' (QueueManager): QueueManager object for machine running render queue
    //    'scene' (Scene): Target scene to Export From
    //    'settings' (BLGExportSettings): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ExportOpInfo): Operation info for job added to export queue
    //
    do_export_BLG(queue, scene, settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.do_export_BLG",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        );
    }

    // Export.do_export_CDL
    //
    // Perform export CDL operation using the given Export settings 
    //
    // Arguments:
    //    'queue' (QueueManager): QueueManager object for machine running render queue
    //    'scene' (Scene): Target scene to Export From
    //    'settings' (CDLExportSettings): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ExportOpInfo): Operation info for job added to export queue
    //
    do_export_CDL(queue, scene, settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.do_export_CDL",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        );
    }

    // Export.do_export_cube
    //
    // Perform export LUT operation using the given Export settings 
    //
    // Arguments:
    //    'queue' (QueueManager): QueueManager object for machine running render queue
    //    'scene' (Scene): Target scene to Export From
    //    'settings' (CubeExportSettings): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ExportOpInfo): Operation info for job added to export queue
    //
    do_export_cube(queue, scene, settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.do_export_cube",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        );
    }

    // Export.do_export_still
    //
    // Perform export still operation using the given Export settings 
    //
    // Arguments:
    //    'queue' (QueueManager): QueueManager object for machine running render queue
    //    'scene' (Scene): Target scene to Export From
    //    'settings' (StillExportSettings): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ExportOpInfo): Operation info for job added to export queue
    //
    do_export_still(queue, scene, settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.do_export_still",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        );
    }

    // Export.get_log
    //
    // Return log of progress information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Export progress information
    //        '<n>' (ExportProgress): 
    //
    get_log()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.get_log",
            {
            }
        );
    }

    // Export.get_presets
    //
    // Return array of presets.   
    // Note:  this function is provided to make it easier to discover what settings are required when you want a particular export format (in particular for stills where it may not be obvious how to choose quality / compression settings etc).  It is not, currently, intended to be a full-fledged interface to the Baselight presets. 
    //
    // Arguments:
    //    'scene' (Scene): Scene to read presets from
    //    'export_type' (string): Type of Export to request presets from
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (object): 
    //
    get_presets(scene, export_type)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Export.get_presets",
            {
                'scene': scene,
                'export_type': export_type,
            }
        );
    }

};
library.register_class( 'Export', Export )
module.exports.Export = Export;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Filesystem
//
// Access host filesystem
//

var Filesystem = class Filesystem extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Filesystem", "_id": this.target };
    }

    // Filesystem.get_items
    //
    // Return array of items in given directory 
    //
    // Arguments:
    //    'dir' (string): Path to directory
    //    'filter' (Set):  [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (object): name
    //            'type' (string): Type of item
    //
    get_items(dir, filter = null)
    {
        return this.conn.call(
            null,
            "Filesystem.get_items",
            {
                'dir': dir,
                'filter': filter,
            }
        );
    }

};
library.register_class( 'Filesystem', Filesystem )
module.exports.Filesystem = Filesystem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Format
//
// Format defines an image resolution and pixel aspect ratio with associated masks and burnins
//

var Format = class Format extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Format", "_id": this.target };
    }

    // Format.get_description
    //
    // Return description of format 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Description
    //
    get_description()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_description",
            {
            }
        );
    }

    // Format.get_resolution
    //
    // Return FormatInfo for given resolution of Format 
    //
    // Arguments:
    //    'res' (string): Constant identify which resolution to fetch [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatInfo): 
    //
    get_resolution(res = "GMPR_HIGH")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_resolution",
            {
                'res': res,
            }
        );
    }

    // Format.get_mapping_names
    //
    // Return names of mapping from this format to other formats 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of names of format mapping
    //        '<n>' (string): Format name
    //
    get_mapping_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_mapping_names",
            {
            }
        );
    }

    // Format.get_mapping
    //
    // Return definition of mapping from this format to named format 
    //
    // Arguments:
    //    'name' (string): Name of target format
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatMapping): 
    //
    get_mapping(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_mapping",
            {
                'name': name,
            }
        );
    }

    // Format.get_masks
    //
    // Return array of FormatMasks defined for this format 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of masks
    //        '<n>' (FormatMask): 
    //
    get_masks()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_masks",
            {
            }
        );
    }

    // Format.get_burnin_names
    //
    // Return array of names of burnins defined for this format 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of burnin names
    //        '<n>' (string): Burnin name
    //
    get_burnin_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_burnin_names",
            {
            }
        );
    }

    // Format.add_burnin
    //
    // Create a new burnin with the given name, and return a FormatBurnin object for it 
    //
    // Arguments:
    //    'name' (string): Burnin name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatBurnin): 
    //
    add_burnin(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.add_burnin",
            {
                'name': name,
            }
        );
    }

    // Format.get_burnin
    //
    // Return FormatBurnin object for the named burnin 
    //
    // Arguments:
    //    'name' (string): Burnin name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatBurnin): 
    //
    get_burnin(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.get_burnin",
            {
                'name': name,
            }
        );
    }

    // Format.delete_burnin
    //
    // Delete the burnin with the given name 
    //
    // Arguments:
    //    'name' (string): Burnin name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_burnin(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Format.delete_burnin",
            {
                'name': name,
            }
        );
    }

};
library.register_class( 'Format', Format )
module.exports.Format = Format;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatBurnin
//
// Definition of a burn-in for a Format
//

var FormatBurnin = class FormatBurnin extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "FormatBurnin", "_id": this.target };
    }

    // FormatBurnin.get_opacity
    //
    // Get burnin opacity 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Opacity
    //
    get_opacity()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.get_opacity",
            {
            }
        );
    }

    // FormatBurnin.set_opacity
    //
    // Set burnin opacity 
    //
    // Arguments:
    //    'opacity' (number): Opacity
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_opacity(opacity)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.set_opacity",
            {
                'opacity': opacity,
            }
        );
    }

    // FormatBurnin.get_box_colour
    //
    // Set colour of box around text items 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): RGBA box colour
    //        '<n>' (number): 
    //
    get_box_colour()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.get_box_colour",
            {
            }
        );
    }

    // FormatBurnin.set_box_colour
    //
    // Set colour of box around text items 
    //
    // Arguments:
    //    'colour' (array): RGBA box colour
    //        '<n>' (number): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_box_colour(colour)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.set_box_colour",
            {
                'colour': colour,
            }
        );
    }

    // FormatBurnin.get_font
    //
    // Get font name for this burnin 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Font name
    //
    get_font()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.get_font",
            {
            }
        );
    }

    // FormatBurnin.set_font
    //
    // Get font name for this burnin 
    //
    // Arguments:
    //    'name' (string): Font name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_font(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.set_font",
            {
                'name': name,
            }
        );
    }

    // FormatBurnin.add_item
    //
    // Add new item to the burnin 
    //
    // Arguments:
    //    'item' (FormatBurninItem): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_item(item)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.add_item",
            {
                'item': item,
            }
        );
    }

    // FormatBurnin.get_num_items
    //
    // Return number of items defined within this burnin 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of burnin items
    //
    get_num_items()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.get_num_items",
            {
            }
        );
    }

    // FormatBurnin.get_item
    //
    // Return definition for the burnin item at the given index 
    //
    // Arguments:
    //    'index' (number): Index of burnin item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatBurninItem): 
    //
    get_item(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.get_item",
            {
                'index': index,
            }
        );
    }

    // FormatBurnin.set_item
    //
    // Return definition for the burnin item at the given index 
    //
    // Arguments:
    //    'index' (number): Index of burnin item
    //    'item' (FormatBurninItem): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_item(index, item)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.set_item",
            {
                'index': index,
                'item': item,
            }
        );
    }

    // FormatBurnin.delete_item
    //
    // Delete the burnin item at the given index 
    //
    // Arguments:
    //    'index' (number): Index of burnin item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_item(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatBurnin.delete_item",
            {
                'index': index,
            }
        );
    }

};
library.register_class( 'FormatBurnin', FormatBurnin )
module.exports.FormatBurnin = FormatBurnin;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatSet
//
// The FormatSet interface allows enumeration of available resources on the FilmLight system such as formats, colour spaces, display render transforms, LUTs, etc.
//

var FormatSet = class FormatSet extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "FormatSet", "_id": this.target };
    }

    // FormatSet.factory_formats
    //
    // Return factory FormatSet object for factory (built-in) formats 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatSet): 
    //
    factory_formats()
    {
        return this.conn.call(
            null,
            "FormatSet.factory_formats",
            {
            }
        );
    }

    // FormatSet.global_formats
    //
    // Return global FormatSet object for formats defined in formats database 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatSet): 
    //
    global_formats()
    {
        return this.conn.call(
            null,
            "FormatSet.global_formats",
            {
            }
        );
    }

    // FormatSet.job_formats
    //
    // Return FormatSet object for formats defined in the given Job database 
    //
    // Arguments:
    //    'hostname' (string): Database host
    //    'jobname' (string): Job name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatSet): 
    //
    job_formats(hostname, jobname)
    {
        return this.conn.call(
            null,
            "FormatSet.job_formats",
            {
                'hostname': hostname,
                'jobname': jobname,
            }
        );
    }

    // FormatSet.get_drt_names
    //
    // Return array of Display Rendering Transform names 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of DRT names
    //        '<n>' (string): DRT Name
    //
    get_drt_names()
    {
        return this.conn.call(
            null,
            "FormatSet.get_drt_names",
            {
            }
        );
    }

    // FormatSet.get_drt_info
    //
    // Return information for the given Display Rendering Transform name 
    //
    // Arguments:
    //    'name' (string): Name of Display Rendering Transform
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (DRTInfo): 
    //
    get_drt_info(name)
    {
        return this.conn.call(
            null,
            "FormatSet.get_drt_info",
            {
                'name': name,
            }
        );
    }

    // FormatSet.get_scope
    //
    // Return scope this is FormatSet represents 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string)
    //
    get_scope()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_scope",
            {
            }
        );
    }

    // FormatSet.get_scope_path
    //
    // Return the path for FormatSets representing a job/scene scope 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Scope path
    //
    get_scope_path()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_scope_path",
            {
            }
        );
    }

    // FormatSet.get_format_names
    //
    // Return array of format names 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Format names
    //        '<n>' (string): 
    //
    get_format_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_format_names",
            {
            }
        );
    }

    // FormatSet.get_basic_format_name
    //
    // Return name for a basic (auto-generated) format 
    //
    // Arguments:
    //    'width' (number): Width of format
    //    'height' (number): Height of format
    //    'pixelAspectRatio' (number): Pixel aspect ratio [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Format name
    //
    get_basic_format_name(width, height, pixelAspectRatio = 1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_basic_format_name",
            {
                'width': width,
                'height': height,
                'pixelAspectRatio': pixelAspectRatio,
            }
        );
    }

    // FormatSet.get_format
    //
    // Return Format object for the named format 
    //
    // Arguments:
    //    'name' (string): Format name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Format): 
    //
    get_format(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_format",
            {
                'name': name,
            }
        );
    }

    // FormatSet.get_colour_space_names
    //
    // Return array of colour space names 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of colour space names
    //        '<n>' (string): Colour space name
    //
    get_colour_space_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_colour_space_names",
            {
            }
        );
    }

    // FormatSet.get_colour_space_info
    //
    // Return information on the given colour space 
    //
    // Arguments:
    //    'name' (string): Name of colour space
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ColourSpaceInfo): 
    //
    get_colour_space_info(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.get_colour_space_info",
            {
                'name': name,
            }
        );
    }

    // FormatSet.add_format
    //
    // Add a new format to this FormatSet 
    //
    // Arguments:
    //    'name' (string): Name of format
    //    'description' (string): Description of format
    //    'width' (number): Width of format in pixels
    //    'height' (number): Height of format in pixels
    //    'pixelAspectRatio' (number): Pixel aspect ratio [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Format): Object representing the newly created format
    //
    add_format(name, description, width, height, pixelAspectRatio = 1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.add_format",
            {
                'name': name,
                'description': description,
                'width': width,
                'height': height,
                'pixelAspectRatio': pixelAspectRatio,
            }
        );
    }

    // FormatSet.delete_format
    //
    // Delete a format from the FormatSet 
    //
    // Arguments:
    //    'name' (string): Name of format to delete
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_format(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "FormatSet.delete_format",
            {
                'name': name,
            }
        );
    }

};
library.register_class( 'FormatSet', FormatSet )
module.exports.FormatSet = FormatSet;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Image
//
//

var Image = class Image extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Image", "_id": this.target };
    }

    // Image.get_raw_metadata
    //
    // Returns raw metadata for the image or movie at the supplied path 
    //
    // Arguments:
    //    'filename' (string): Filename of image/movie to examine
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Dictionary of metadata
    //
    get_raw_metadata(filename)
    {
        return this.conn.call(
            null,
            "Image.get_raw_metadata",
            {
                'filename': filename,
            }
        );
    }

};
library.register_class( 'Image', Image )
module.exports.Image = Image;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ImageSearcher
//
// Search for image sequences on disk
//

var ImageSearcher = class ImageSearcher extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "ImageSearcher", "_id": this.target };
    }

    // ImageSearcher.create
    //
    // Create a new Image Searcher object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ImageSearcher): New ImageSearcher object
    //
    create()
    {
        return this.conn.call(
            null,
            "ImageSearcher.create",
            {
            }
        );
    }

    // ImageSearcher.add_root_directory
    //
    // Add a root directory to search to the image searcher 
    //
    // Arguments:
    //    'dir' (string): Path to directory
    //    'recurse' (number): Flag indicating whether to recursively search this directory
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Returns 1 if directory as successfully added, or 0 if directory cannot be added.
    //
    add_root_directory(dir, recurse)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.add_root_directory",
            {
                'dir': dir,
                'recurse': recurse,
            }
        );
    }

    // ImageSearcher.scan
    //
    // Begin search for image sequences and movies. 
    // The scan will run asynchronously. 
    // You can check for scan completion by calling is_scan_in_progress(). 
    // Alternatively you can cancel the scan by calling cancel(). 
    // You can poll the ImageSearcher object for progress by calling get_num_images() or get_num_sequences(). 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Returns 1 if scan is started successfully, or 0 if scan cannot be started.
    //
    scan()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.scan",
            {
            }
        );
    }

    // ImageSearcher.is_scan_in_progress
    //
    // Check whether scan is in progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Returns 1 if scan is in progress, 0 if scan is not in progress
    //
    is_scan_in_progress()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.is_scan_in_progress",
            {
            }
        );
    }

    // ImageSearcher.cancel
    //
    // Cancel scan in progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    cancel()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.cancel",
            {
            }
        );
    }

    // ImageSearcher.is_cancelled
    //
    // Check if scan was cancelled 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Returns 1 if scan was cancelled, 0 if scan was not cancelled.
    //
    is_cancelled()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.is_cancelled",
            {
            }
        );
    }

    // ImageSearcher.get_num_images
    //
    // Return number of image files found 
    //
    // Arguments:
    //    'rootDir' (string): Directory to get statistics for
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of image files found
    //
    get_num_images(rootDir)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.get_num_images",
            {
                'rootDir': rootDir,
            }
        );
    }

    // ImageSearcher.get_num_movies
    //
    // Return number of movie files found 
    //
    // Arguments:
    //    'rootDir' (string): Directory to get statistics for
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of image files found
    //
    get_num_movies(rootDir)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.get_num_movies",
            {
                'rootDir': rootDir,
            }
        );
    }

    // ImageSearcher.get_sequences
    //
    // Get array of sequences found by the ImageSearcher 
    //
    // Arguments:
    //    'track' (string): Choose which metadata 'track' to use to separate sequences.
    //        A range of files may be grouped into sequences based frame number, timecode (track 1 or 2), or keycode.
    //        For example, a single sequence with contiguous frame numbers could result in multiple distinct
    //        sub-sequences when separated by timecode or keycode.
    //    'limit' (number): Limit the number of sequences returned by this call
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of SequenceDescriptor objects
    //        '<n>' (SequenceDescriptor): 
    //
    get_sequences(track, limit)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ImageSearcher.get_sequences",
            {
                'track': track,
                'limit': limit,
            }
        );
    }

};
library.register_class( 'ImageSearcher', ImageSearcher )
module.exports.ImageSearcher = ImageSearcher;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// JobManager
//
// Query and manipulate the FilmLight job database
//

var JobManager = class JobManager extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "JobManager", "_id": this.target };
    }

    // JobManager.get_jobs
    //
    // Fetch list of jobs in job database 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of job name strings
    //        '<n>' (string): Job name
    //
    get_jobs(host)
    {
        return this.conn.call(
            null,
            "JobManager.get_jobs",
            {
                'host': host,
            }
        );
    }

    // JobManager.get_folders
    //
    // Fetch list of folder names within job/folder in job database 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'job' (string): Job name within job database
    //    'folder' (string): Folder within job [Optional]
    //    'recursive' (number): Return all folders contained within the given job/folder [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of folder names
    //        '<n>' (string): Folder name
    //
    get_folders(host, job, folder = null, recursive = 1)
    {
        return this.conn.call(
            null,
            "JobManager.get_folders",
            {
                'host': host,
                'job': job,
                'folder': folder,
                'recursive': recursive,
            }
        );
    }

    // JobManager.get_scenes
    //
    // Fetch list of scene names within job/folder in job database 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'job' (string): Job name within job database
    //    'folder' (string): Folder within job [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of scene names
    //        '<n>' (string): Scene name
    //
    get_scenes(host, job, folder = null)
    {
        return this.conn.call(
            null,
            "JobManager.get_scenes",
            {
                'host': host,
                'job': job,
                'folder': folder,
            }
        );
    }

    // JobManager.create_job
    //
    // Create a new job 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    create_job(host, jobname)
    {
        return this.conn.call(
            null,
            "JobManager.create_job",
            {
                'host': host,
                'jobname': jobname,
            }
        );
    }

    // JobManager.rename_job
    //
    // Rename job 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'new_jobname' (string): New job name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    rename_job(host, jobname, new_jobname)
    {
        return this.conn.call(
            null,
            "JobManager.rename_job",
            {
                'host': host,
                'jobname': jobname,
                'new_jobname': new_jobname,
            }
        );
    }

    // JobManager.delete_job
    //
    // Delete job 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'force' (number): Force deletion of job [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_job(host, jobname, force = 0)
    {
        return this.conn.call(
            null,
            "JobManager.delete_job",
            {
                'host': host,
                'jobname': jobname,
                'force': force,
            }
        );
    }

    // JobManager.job_exists
    //
    // Check if job exists 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating whether job exists
    //
    job_exists(host, jobname)
    {
        return this.conn.call(
            null,
            "JobManager.job_exists",
            {
                'host': host,
                'jobname': jobname,
            }
        );
    }

    // JobManager.create_folder
    //
    // Create a folder within job 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'foldername' (string): Folder name within job
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    create_folder(host, jobname, foldername)
    {
        return this.conn.call(
            null,
            "JobManager.create_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
            }
        );
    }

    // JobManager.rename_folder
    //
    // Rename folder 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'foldername' (string): Folder name within job
    //    'new_foldername' (string): New folder name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    rename_folder(host, jobname, foldername, new_foldername)
    {
        return this.conn.call(
            null,
            "JobManager.rename_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
                'new_foldername': new_foldername,
            }
        );
    }

    // JobManager.delete_folder
    //
    // Delete folder 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'foldername' (string): Folder name within job
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_folder(host, jobname, foldername)
    {
        return this.conn.call(
            null,
            "JobManager.delete_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
            }
        );
    }

    // JobManager.get_scene_info
    //
    // Return information about scene 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'scenename' (string): Scene name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (SceneInfo): An object containing properties of the Scene
    //
    get_scene_info(host, jobname, scenename)
    {
        return this.conn.call(
            null,
            "JobManager.get_scene_info",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
            }
        );
    }

    // JobManager.scene_exists
    //
    // Check if scene exists 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'scenename' (string): Scene name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating whether scene exists
    //
    scene_exists(host, jobname, scenename)
    {
        return this.conn.call(
            null,
            "JobManager.scene_exists",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
            }
        );
    }

    // JobManager.delete_scene
    //
    // Delete scene 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'scenename' (string): Scene name
    //    'ignoreLocks' (number): Flag indicating any existing locks on scene should be ignored [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_scene(host, jobname, scenename, ignoreLocks = 0)
    {
        return this.conn.call(
            null,
            "JobManager.delete_scene",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
                'ignoreLocks': ignoreLocks,
            }
        );
    }

    // JobManager.rename_scene
    //
    // Rename scene 
    //
    // Arguments:
    //    'host' (string): Hostname of job database
    //    'jobname' (string): Job name
    //    'scenename' (string): Scene name
    //    'newname' (string): New Scene name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    rename_scene(host, jobname, scenename, newname)
    {
        return this.conn.call(
            null,
            "JobManager.rename_scene",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
                'newname': newname,
            }
        );
    }

};
library.register_class( 'JobManager', JobManager )
module.exports.JobManager = JobManager;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Licence
//
// Licence management
//

var Licence = class Licence extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Licence", "_id": this.target };
    }

    // Licence.get_system_id
    //
    // Return the system ID used to identify this system for licensing 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): System ID string
    //
    get_system_id()
    {
        return this.conn.call(
            null,
            "Licence.get_system_id",
            {
            }
        );
    }

    // Licence.get_licence_info
    //
    // Return licence information 
    //
    // Arguments:
    //    'include_expired' (number): Flag indicating whether to include expired licenses in the list [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of installed licence items
    //        '<n>' (LicenceItem): 
    //
    get_licence_info(include_expired = 0)
    {
        return this.conn.call(
            null,
            "Licence.get_licence_info",
            {
                'include_expired': include_expired,
            }
        );
    }

    // Licence.install_licence
    //
    // Install the given licence data 
    //
    // Arguments:
    //    'licenceData' (string): String containing Base-64 encoded licence data
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    install_licence(licenceData)
    {
        return this.conn.call(
            null,
            "Licence.install_licence",
            {
                'licenceData': licenceData,
            }
        );
    }

};
library.register_class( 'Licence', Licence )
module.exports.Licence = Licence;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Mark
//
// Mark defined in a Shot or Scene
//

var Mark = class Mark extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Mark", "_id": this.target };
    }

    // Mark.get_id
    //
    // Return Mark object ID 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Mark ID
    //
    get_id()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_id",
            {
            }
        );
    }

    // Mark.get_type
    //
    // Return Mark type 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Value indicating type of mark
    //
    get_type()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_type",
            {
            }
        );
    }

    // Mark.get_position
    //
    // Return Mark position 
    // For Shot marks, this value is a frame number relative to the start of the image sequence. 
    // For Strip marks, this value is a time in seconds relative to the start of the strip. 
    // For Timeline marks, this value is a time in seconds relative to the start of the timeline. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Position in seconds or frames
    //
    get_position()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_position",
            {
            }
        );
    }

    // Mark.get_time
    //
    // Return Mark position in seconds 
    // For Shot and Strip marks, this returns the time relative to the start of the shot 
    // For Timeline marks, this returns the time relative to the start of the timeline 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Position in seconds
    //
    get_time()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_time",
            {
            }
        );
    }

    // Mark.get_note_text
    //
    // Return Mark note text 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Note text
    //
    get_note_text()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_note_text",
            {
            }
        );
    }

    // Mark.get_colour
    //
    // Return Mark colour 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): RGBA colour
    //        '<n>' (number): 
    //
    get_colour()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_colour",
            {
            }
        );
    }

    // Mark.get_category
    //
    // Return Mark category 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Mark category
    //
    get_category()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_category",
            {
            }
        );
    }

    // Mark.get_source_frame
    //
    // Return the source image frame number for this mark 
    // Only applicable for Shot/Strip marks. Will fail for Timeline marks 
    //
    // Arguments:
    //    'eye' (string): Which eye for stereo sequences [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Source frame number
    //
    get_source_frame(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_source_frame",
            {
                'eye': eye,
            }
        );
    }

    // Mark.get_source_timecode
    //
    // Return the source image timecode for this mark 
    // Only applicable for Shot/Strip marks. Will fail for Timeline marks 
    //
    // Arguments:
    //    'eye' (string): Which eye for stereo sequences [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Source timecode
    //
    get_source_timecode(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_source_timecode",
            {
                'eye': eye,
            }
        );
    }

    // Mark.get_record_frame
    //
    // Return the source image frame number for this mark 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Record frame number
    //
    get_record_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_record_frame",
            {
            }
        );
    }

    // Mark.get_record_timecode
    //
    // Return the source image timecode for this mark 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Record timecode
    //
    get_record_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_record_timecode",
            {
            }
        );
    }

    // Mark.get_properties
    //
    // Return dictionary of properties for this Mark object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Dictionary containing property keys and values
    //
    get_properties()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.get_properties",
            {
            }
        );
    }

    // Mark.set_properties
    //
    // Set the property values for the given dictionary of keys & values. 
    // Setting a value to NULL will remove it from the property set. 
    //
    // Arguments:
    //    'props' (object): Dictionary of property keys & values
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_properties(props)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Mark.set_properties",
            {
                'props': props,
            }
        );
    }

};
library.register_class( 'Mark', Mark )
module.exports.Mark = Mark;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Menu
//
// A menu in the application user interface, which contains MenuItems
//

var Menu = class Menu extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Menu", "_id": this.target };
    }

    // Menu.create
    //
    // Create new Menu object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Menu): Menu object
    //
    create()
    {
        return this.conn.call(
            null,
            "Menu.create",
            {
            }
        );
    }

    // Menu.add_item
    //
    // Add MenuItem to menu 
    //
    // Arguments:
    //    'item' (MenuItem): Item to add to menu
    //    'index' (number): Index to insert item at. Use 0 to append to front. Use -1 to append to end. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_item(item, index = -1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.add_item",
            {
                'item': item,
                'index': index,
            }
        );
    }

    // Menu.get_num_items
    //
    // Get number of items in menu 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of items in menu
    //
    get_num_items()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.get_num_items",
            {
            }
        );
    }

    // Menu.get_item_at
    //
    // Get MenuItem at given index within menu 
    //
    // Arguments:
    //    'index' (number): Index of menu item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (MenuItem): 
    //
    get_item_at(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.get_item_at",
            {
                'index': index,
            }
        );
    }

    // Menu.get_index_of_item
    //
    // Return the index of the given MenuItem within this Menu 
    //
    // Arguments:
    //    'item' (MenuItem): Item to find index for
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Index of MenuItem, -1 if not found
    //
    get_index_of_item(item)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.get_index_of_item",
            {
                'item': item,
            }
        );
    }

    // Menu.remove_item_at
    //
    // Remove menu item at the given index 
    //
    // Arguments:
    //    'index' (number): Index of menu item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    remove_item_at(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.remove_item_at",
            {
                'index': index,
            }
        );
    }

    // Menu.remove_item
    //
    // Remove menu item from menu 
    //
    // Arguments:
    //    'item' (MenuItem): MenuItem to remove
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    remove_item(item)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.remove_item",
            {
                'item': item,
            }
        );
    }

    // Menu.remove_all_items
    //
    // Remove all menu items from menu 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    remove_all_items()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Menu.remove_all_items",
            {
            }
        );
    }

};
library.register_class( 'Menu', Menu )
module.exports.Menu = Menu;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MenuItem
//
// A menu item in the application user interface, which can trigger actions
//

var MenuItem = class MenuItem extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "MenuItem", "_id": this.target };
    }

    // MenuItem.create
    //
    // Create a new MenuItem object 
    //
    // Arguments:
    //    'title' (string): Title of MenuItem
    //    'key' (any): A value which can be used as a key to identify this menu item [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (MenuItem): 
    //
    create(title, key = null)
    {
        return this.conn.call(
            null,
            "MenuItem.create",
            {
                'title': title,
                'key': key,
            }
        );
    }

    // MenuItem.register
    //
    // Register this menu item to insert it into the application's UI 
    //
    // Arguments:
    //    'location' (string): Where to register menu item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    register(location)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.register",
            {
                'location': location,
            }
        );
    }

    // MenuItem.get_title
    //
    // Get menu item title 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Menu item title
    //
    get_title()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.get_title",
            {
            }
        );
    }

    // MenuItem.set_title
    //
    // Set menu item title 
    //
    // Arguments:
    //    'title' (string): New menu item title
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_title(title)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.set_title",
            {
                'title': title,
            }
        );
    }

    // MenuItem.get_enabled
    //
    // Get menu item enabled state 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Enabled state
    //
    get_enabled()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.get_enabled",
            {
            }
        );
    }

    // MenuItem.set_enabled
    //
    // Set menu item enabled state 
    //
    // Arguments:
    //    'enabled' (number): Enabled state
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_enabled(enabled)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.set_enabled",
            {
                'enabled': enabled,
            }
        );
    }

    // MenuItem.get_hidden
    //
    // Get menu item hidden state 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Hidden state
    //
    get_hidden()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.get_hidden",
            {
            }
        );
    }

    // MenuItem.set_hidden
    //
    // Set menu item hidden state 
    //
    // Arguments:
    //    'hidden' (number): Hidden state
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_hidden(hidden)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.set_hidden",
            {
                'hidden': hidden,
            }
        );
    }

    // MenuItem.get_sub_menu
    //
    // Get sub-menu for this menu item 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Menu): 
    //
    get_sub_menu()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.get_sub_menu",
            {
            }
        );
    }

    // MenuItem.set_sub_menu
    //
    // Set sub-menu for this menu item 
    //
    // Arguments:
    //    'submenu' (Menu): Menu object containing sub-menu items
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_sub_menu(submenu)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MenuItem.set_sub_menu",
            {
                'submenu': submenu,
            }
        );
    }

};
library.register_class( 'MenuItem', MenuItem )
module.exports.MenuItem = MenuItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MultiPaste
//
// Multi-Paste operation
//

var MultiPaste = class MultiPaste extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "MultiPaste", "_id": this.target };
    }

    // MultiPaste.create
    //
    // Create a new Multi-Paste operation object 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (MultiPaste): MultiPaste object
    //
    create()
    {
        return this.conn.call(
            null,
            "MultiPaste.create",
            {
            }
        );
    }

    // MultiPaste.multi_paste
    //
    // Perform multi-paste operation using the given Multi-Paste settings 
    //
    // Arguments:
    //    'scene' (Scene): Target scene to MultiPaste into
    //    'settings' (MultiPasteSettings): 
    //    'shot_ids' (array): Array of Shot IDs to apply multi-paste operation to [Optional]
    //        '<n>' (number): Shot ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of shots updated by Multi-Paste operation
    //
    multi_paste(scene, settings, shot_ids = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MultiPaste.multi_paste",
            {
                'scene': scene,
                'settings': settings,
                'shot_ids': shot_ids,
            }
        );
    }

    // MultiPaste.get_log
    //
    // Return log of progress information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of multi-paste progress information
    //        '<n>' (MultiPasteProgress): 
    //
    get_log()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "MultiPaste.get_log",
            {
            }
        );
    }

};
library.register_class( 'MultiPaste', MultiPaste )
module.exports.MultiPaste = MultiPaste;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ProgressDialog
//
// Display a progress dialog within the application
//

var ProgressDialog = class ProgressDialog extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "ProgressDialog", "_id": this.target };
    }

    // ProgressDialog.create
    //
    // Create a new ProgressDialog 
    //
    // Arguments:
    //    'title' (string): Title of progress dialog
    //    'msg' (string): Message to display in progress dialog
    //    'cancellable' (number): Flag indicating that progress dialog has cancel button [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ProgressDialog): 
    //
    create(title, msg, cancellable = 0)
    {
        return this.conn.call(
            null,
            "ProgressDialog.create",
            {
                'title': title,
                'msg': msg,
                'cancellable': cancellable,
            }
        );
    }

    // ProgressDialog.show
    //
    // Show the progress dialog 
    //
    // Arguments:
    //    'delay' (number): Only show progress dialog after a delay, in seconds [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    show(delay = 0)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ProgressDialog.show",
            {
                'delay': delay,
            }
        );
    }

    // ProgressDialog.set_title
    //
    // Set the title of the progress dialog 
    //
    // Arguments:
    //    'title' (string): New title for dialog
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_title(title)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ProgressDialog.set_title",
            {
                'title': title,
            }
        );
    }

    // ProgressDialog.set_progress
    //
    // Update the progress & message displayed in dialog 
    //
    // Arguments:
    //    'progress' (number): Progress value between 0.0 and 1.0
    //    'message' (string): Progress message to display
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_progress(progress, message)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ProgressDialog.set_progress",
            {
                'progress': progress,
                'message': message,
            }
        );
    }

    // ProgressDialog.hide
    //
    // Hide the progress dialog 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    hide()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "ProgressDialog.hide",
            {
            }
        );
    }

};
library.register_class( 'ProgressDialog', ProgressDialog )
module.exports.ProgressDialog = ProgressDialog;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// QueueManager
//
// Interface for managing the Queue on a Baselight/Daylight system
//

var QueueManager = class QueueManager extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "QueueManager", "_id": this.target };
    }

    // QueueManager.create
    //
    // Create a QueueManager object to examine and manipulate the queue on the given zone 
    //
    // Arguments:
    //    'zone' (string): Zone name of machine running queue
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueManager): 
    //
    create(zone)
    {
        return this.conn.call(
            null,
            "QueueManager.create",
            {
                'zone': zone,
            }
        );
    }

    // QueueManager.create_local
    //
    // Create a QueueManager object to examine and manipulate the queue on the local zone 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueManager): 
    //
    create_local()
    {
        return this.conn.call(
            null,
            "QueueManager.create_local",
            {
            }
        );
    }

    // QueueManager.create_no_database
    //
    // Create a QueueManager object to examine and manipulate a non-database queue in the FLAPI process. In addition, the QueueManager object will process any operations added to the queue within the FLAPI process. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueManager): 
    //
    create_no_database()
    {
        return this.conn.call(
            null,
            "QueueManager.create_no_database",
            {
            }
        );
    }

    // QueueManager.get_queue_zones
    //
    // Return list of available zones running queue services 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of strings identifying zones available for rendering
    //        '<n>' (string): Zone name
    //
    get_queue_zones()
    {
        return this.conn.call(
            null,
            "QueueManager.get_queue_zones",
            {
            }
        );
    }

    // QueueManager.get_operation_ids
    //
    // Return list operation IDs in queue 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Operation IDs
    //        '<n>' (number): Operation ID
    //
    get_operation_ids()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_operation_ids",
            {
            }
        );
    }

    // QueueManager.get_operation
    //
    // Return definition of given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueOp): 
    //
    get_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.get_operation_status
    //
    // Return status of given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueOpStatus): 
    //
    get_operation_status(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_operation_status",
            {
                'id': id,
            }
        );
    }

    // QueueManager.get_operation_log
    //
    // Return log for given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Log Entries
    //        '<n>' (QueueLogItem): 
    //
    get_operation_log(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_operation_log",
            {
                'id': id,
            }
        );
    }

    // QueueManager.pause_operation
    //
    // Pause operation with given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    pause_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.pause_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.resume_operation
    //
    // Resume operation with given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    resume_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.resume_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.restart_operation
    //
    // Restart operation with given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    restart_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.restart_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.delete_operation
    //
    // Delete operation with given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.delete_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.archive_operation
    //
    // Archive operation with given operation ID 
    //
    // Arguments:
    //    'id' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    archive_operation(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.archive_operation",
            {
                'id': id,
            }
        );
    }

    // QueueManager.enable_updates
    //
    // Enable status update signals 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    enable_updates()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.enable_updates",
            {
            }
        );
    }

    // QueueManager.disable_updates
    //
    // Disable status update signals 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    disable_updates()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.disable_updates",
            {
            }
        );
    }

    // QueueManager.new_operation
    //
    // Create a new custom operation and return its ID 
    //
    // Arguments:
    //    'opType' (string): Key identifying the operation type
    //    'desc' (string): Description of operation to present in queue
    //    'params' (object): Parameters for operation. May contain any simple key/value parameters.
    //    'tasks' (array): Array of tasks for this operation. If you wish to add more tasks to the operation, leave this parameter empty and use add_tasks_to_operation() instead, followed by set_operation_ready(). [Optional]
    //        '<n>' (QueueOpTask): 
    //    'dependsOn' (Set): Set of operation IDs that this operation depends on [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Operation ID
    //
    new_operation(opType, desc, params, tasks = null, dependsOn = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.new_operation",
            {
                'opType': opType,
                'desc': desc,
                'params': params,
                'tasks': tasks,
                'dependsOn': dependsOn,
            }
        );
    }

    // QueueManager.add_tasks_to_operation
    //
    // Add more tasks to the given operation 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'tasks' (array): Array of tasks for this operation
    //        '<n>' (QueueOpTask): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_tasks_to_operation(opid, tasks)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.add_tasks_to_operation",
            {
                'opid': opid,
                'tasks': tasks,
            }
        );
    }

    // QueueManager.set_operation_ready
    //
    // Mark operation as ready to process. Should be called after calling add_tasks_to_operation(). 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_operation_ready(opid)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.set_operation_ready",
            {
                'opid': opid,
            }
        );
    }

    // QueueManager.get_next_operation_of_type
    //
    // Find the next operation for the given operation type that is ready to execute 
    //
    // Arguments:
    //    'opType' (string): Key identifying operation type
    //    'wait' (number): Flag indicating whether the method should block until a task is available
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Operation ID
    //
    get_next_operation_of_type(opType, wait)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_next_operation_of_type",
            {
                'opType': opType,
                'wait': wait,
            }
        );
    }

    // QueueManager.get_operation_params
    //
    // Get params for given operation ID 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): 
    //
    get_operation_params(opid)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_operation_params",
            {
                'opid': opid,
            }
        );
    }

    // QueueManager.get_next_task
    //
    // Get the next task ready to execute for the given operation ID 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (QueueOpTask): Description of task to execute
    //
    get_next_task(opid)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.get_next_task",
            {
                'opid': opid,
            }
        );
    }

    // QueueManager.set_task_progress
    //
    // Set task progress 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'taskseq' (number): Task Sequence Number
    //    'progress' (number): Task progress between 0.0 and 1.0
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_task_progress(opid, taskseq, progress)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.set_task_progress",
            {
                'opid': opid,
                'taskseq': taskseq,
                'progress': progress,
            }
        );
    }

    // QueueManager.set_task_done
    //
    // Mark task as completed 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'taskseq' (number): Task Sequence ID
    //    'msg' (string): Task Message
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_task_done(opid, taskseq, msg)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.set_task_done",
            {
                'opid': opid,
                'taskseq': taskseq,
                'msg': msg,
            }
        );
    }

    // QueueManager.set_task_failed
    //
    // Mark task as failed 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'taskseq' (number): Task Sequence ID
    //    'msg' (string): Task Message
    //    'detail' (string): Detailed information on failure
    //    'frame' (number): Frame number of failure [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_task_failed(opid, taskseq, msg, detail, frame = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.set_task_failed",
            {
                'opid': opid,
                'taskseq': taskseq,
                'msg': msg,
                'detail': detail,
                'frame': frame,
            }
        );
    }

    // QueueManager.add_operation_log
    //
    // Add log entry for operation 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'type' (string): Type of log entry
    //    'msg' (string): Log Message
    //    'detail' (string): Detailed information on failure
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_operation_log(opid, type, msg, detail)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.add_operation_log",
            {
                'opid': opid,
                'type': type,
                'msg': msg,
                'detail': detail,
            }
        );
    }

    // QueueManager.add_task_log
    //
    // Add log entry for operation 
    //
    // Arguments:
    //    'opid' (number): Operation ID
    //    'taskseq' (number): Task Sequence ID
    //    'type' (string): Type of log entry
    //    'msg' (string): Log Message
    //    'detail' (string): Detailed information on failure
    //    'frame' (number): Frame number within task for log entry [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_task_log(opid, taskseq, type, msg, detail, frame = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "QueueManager.add_task_log",
            {
                'opid': opid,
                'taskseq': taskseq,
                'type': type,
                'msg': msg,
                'detail': detail,
                'frame': frame,
            }
        );
    }

};
library.register_class( 'QueueManager', QueueManager )
module.exports.QueueManager = QueueManager;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderProcessor
//
// A RenderProcessor will execute a RenderSetup and produce deliverable data
//

var RenderProcessor = class RenderProcessor extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "RenderProcessor", "_id": this.target };
    }

    // RenderProcessor.get
    //
    // Get RenderProcessor instance 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderProcessor): 
    //
    get()
    {
        return this.conn.call(
            null,
            "RenderProcessor.get",
            {
            }
        );
    }

    // RenderProcessor.start
    //
    // Start render operation for the given RenderSetup 
    //
    // Arguments:
    //    'renderSetup' (RenderSetup): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    start(renderSetup)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderProcessor.start",
            {
                'renderSetup': renderSetup,
            }
        );
    }

    // RenderProcessor.get_progress
    //
    // Returns current render progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderStatus): 
    //
    get_progress()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderProcessor.get_progress",
            {
            }
        );
    }

    // RenderProcessor.get_log
    //
    // Get log of operation progress 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of log entries from this render operation
    //        '<n>' (RenderProcessorLogItem): 
    //
    get_log()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderProcessor.get_log",
            {
            }
        );
    }

    // RenderProcessor.shutdown
    //
    // Shutdown the RenderProcessor instance. This releases any resources in use by the RenderProcessor. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    shutdown()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderProcessor.shutdown",
            {
            }
        );
    }

};
library.register_class( 'RenderProcessor', RenderProcessor )
module.exports.RenderProcessor = RenderProcessor;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderSetup
//
// Setup Baselight/Daylight scene for rendering
//

var RenderSetup = class RenderSetup extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "RenderSetup", "_id": this.target };
    }

    // RenderSetup.get_image_types
    //
    // Return array of supported image types for rendering 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (RenderFileTypeInfo): 
    //
    get_image_types()
    {
        return this.conn.call(
            null,
            "RenderSetup.get_image_types",
            {
            }
        );
    }

    // RenderSetup.get_movie_types
    //
    // Return array of movie types for rendering 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (RenderFileTypeInfo): 
    //
    get_movie_types()
    {
        return this.conn.call(
            null,
            "RenderSetup.get_movie_types",
            {
            }
        );
    }

    // RenderSetup.get_movie_codecs
    //
    // Return array of video codecs available for the given movie type 
    //
    // Arguments:
    //    'movieType' (string): Movie type key
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (RenderCodecInfo): 
    //
    get_movie_codecs(movieType)
    {
        return this.conn.call(
            null,
            "RenderSetup.get_movie_codecs",
            {
                'movieType': movieType,
            }
        );
    }

    // RenderSetup.get_movie_audio_codecs
    //
    // Return array of audio codecs available for the given movie type 
    //
    // Arguments:
    //    'movieType' (string): Movie type key
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (RenderCodecInfo): 
    //
    get_movie_audio_codecs(movieType)
    {
        return this.conn.call(
            null,
            "RenderSetup.get_movie_audio_codecs",
            {
                'movieType': movieType,
            }
        );
    }

    // RenderSetup.create
    //
    // Create a new RenderSetup instance 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderSetup): New RenderSetup object
    //
    create()
    {
        return this.conn.call(
            null,
            "RenderSetup.create",
            {
            }
        );
    }

    // RenderSetup.create_from_scene
    //
    // Create a new RenderSetup instance configured to render the given Scene using its default deliverables 
    //
    // Arguments:
    //    'scene' (Scene): Scene to render and take deliverable configuration from
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderSetup): 
    //
    create_from_scene(scene)
    {
        return this.conn.call(
            null,
            "RenderSetup.create_from_scene",
            {
                'scene': scene,
            }
        );
    }

    // RenderSetup.get_scene
    //
    // Return Scene object for RenderSetup 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): 
    //
    get_scene()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_scene",
            {
            }
        );
    }

    // RenderSetup.set_scene
    //
    // Set Scene to Render 
    //
    // Arguments:
    //    'scene' (Scene): Scene object
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_scene(scene)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_scene",
            {
                'scene': scene,
            }
        );
    }

    // RenderSetup.save_into_scene
    //
    // Save the deliverables from this RenderSetup into the Scene. If a delta is not in progress on the Scene, a new delta will be created for the save operation. 
    //
    // Arguments:
    //    'scene' (Scene): Scene to save deliverables into. If not specified, the deliverables will be saved into the scene currently associated with the RenderSetup. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    save_into_scene(scene = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.save_into_scene",
            {
                'scene': scene,
            }
        );
    }

    // RenderSetup.set_deliverables_from_scene
    //
    // Load Deliverables from Scene object assigned to this RenderSetup object 
    //
    // Arguments:
    //    'scene' (Scene): If specified, load deliverables from the specified Scene instead of scene associated with RenderSetup [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_deliverables_from_scene(scene = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_deliverables_from_scene",
            {
                'scene': scene,
            }
        );
    }

    // RenderSetup.get_num_deliverables
    //
    // Render number of deliverables defined for this Scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of deliverables
    //
    get_num_deliverables()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_num_deliverables",
            {
            }
        );
    }

    // RenderSetup.get_deliverable_names
    //
    // Return array of deliverable names 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of deliverable names
    //        '<n>' (string): Deliverable name
    //
    get_deliverable_names()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_deliverable_names",
            {
            }
        );
    }

    // RenderSetup.get_deliverable
    //
    // Return the RenderDeliverable definition at the given index 
    //
    // Arguments:
    //    'index' (number): Index of RenderDeliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderDeliverable): 
    //
    get_deliverable(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_deliverable",
            {
                'index': index,
            }
        );
    }

    // RenderSetup.set_deliverable
    //
    // Set the settings for the deliverable at the given index 
    //
    // Arguments:
    //    'index' (number): Index  of deliverable to  update
    //    'deliverable' (RenderDeliverable): Settings to use for this deliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_deliverable(index, deliverable)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_deliverable",
            {
                'index': index,
                'deliverable': deliverable,
            }
        );
    }

    // RenderSetup.get_deliverable_by_name
    //
    // Get the settings for the RenderDeliverable definition with the given name. 
    // Returns NULL if not matching deliverable can be found. 
    //
    // Arguments:
    //    'name' (string): Name of RenderDeliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderDeliverable): 
    //
    get_deliverable_by_name(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_deliverable_by_name",
            {
                'name': name,
            }
        );
    }

    // RenderSetup.set_deliverable_by_name
    //
    // Set the settings for the RenderDeliverable definition with the given name 
    //
    // Arguments:
    //    'name' (string): Name of RenderDeliverable to update
    //    'deliverable' (RenderDeliverable): Settings to use for this deliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_deliverable_by_name(name, deliverable)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_deliverable_by_name",
            {
                'name': name,
                'deliverable': deliverable,
            }
        );
    }

    // RenderSetup.add_deliverable
    //
    // Add a new deliverable to be generated as part of this render operation 
    //
    // Arguments:
    //    'deliverable' (RenderDeliverable): Settings for render deliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_deliverable(deliverable)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.add_deliverable",
            {
                'deliverable': deliverable,
            }
        );
    }

    // RenderSetup.delete_deliverable
    //
    // Delete the deliverable at the given index 
    //
    // Arguments:
    //    'index' (number): Index of deliverable to delete
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_deliverable(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.delete_deliverable",
            {
                'index': index,
            }
        );
    }

    // RenderSetup.delete_all_deliverables
    //
    // Delete all deliverables defined in the RenderSetup 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_all_deliverables()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.delete_all_deliverables",
            {
            }
        );
    }

    // RenderSetup.get_deliverable_enabled
    //
    // Get enabled state of deliverable at given index 
    //
    // Arguments:
    //    'index' (number): Index of deliverable
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    get_deliverable_enabled(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_deliverable_enabled",
            {
                'index': index,
            }
        );
    }

    // RenderSetup.set_deliverable_enabled
    //
    // Set enabled state of deliverable at given index 
    //
    // Arguments:
    //    'index' (number): Index of deliverable
    //    'enabled' (number): Flag indicating whether deliverable is enabled for rendering
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_deliverable_enabled(index, enabled)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_deliverable_enabled",
            {
                'index': index,
                'enabled': enabled,
            }
        );
    }

    // RenderSetup.get_output_filename_for_deliverable
    //
    // Return the full filename for the given frame number of a deliverable 
    //
    // Arguments:
    //    'index' (number): Index of deliverable
    //    'leave_container' (number): Leave %C container variable in returned path [Optional]
    //    'frame' (number): Frame number to generate filename for.
    //        Default is -1 to indicate the first frame of the render operation. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Full filename for rendered file/frame
    //
    get_output_filename_for_deliverable(index, leave_container = 0, frame = -1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_output_filename_for_deliverable",
            {
                'index': index,
                'leave_container': leave_container,
                'frame': frame,
            }
        );
    }

    // RenderSetup.set_container
    //
    // Set the output container directory for all deliverables 
    //
    // Arguments:
    //    'container' (string): Container path
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_container(container)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_container",
            {
                'container': container,
            }
        );
    }

    // RenderSetup.get_frames
    //
    // Get list of frame ranges to render 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): List of frame ranges
    //        '<n>' (FrameRange): 
    //
    get_frames()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.get_frames",
            {
            }
        );
    }

    // RenderSetup.set_frames
    //
    // Set list of frame ranges to render 
    //
    // Arguments:
    //    'frames' (array): List of frame ranges
    //        '<n>' (FrameRange): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_frames(frames)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.set_frames",
            {
                'frames': frames,
            }
        );
    }

    // RenderSetup.select_all
    //
    // Select all frames in Scene to render 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_all()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_all",
            {
            }
        );
    }

    // RenderSetup.select_shots
    //
    // Select the given Shots for rendering 
    //
    // Arguments:
    //    'shots' (array): Array of Shot objects to select
    //        '<n>' (Shot): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shots(shots)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_shots",
            {
                'shots': shots,
            }
        );
    }

    // RenderSetup.select_shot_ids
    //
    // Select the given Shots identified by their ID for rendering 
    //
    // Arguments:
    //    'shotids' (array): Array of Shot IDs to select
    //        '<n>' (number): Shot ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shot_ids(shotids)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_shot_ids",
            {
                'shotids': shotids,
            }
        );
    }

    // RenderSetup.select_graded_shots
    //
    // Select all graded shots to render 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_graded_shots()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_graded_shots",
            {
            }
        );
    }

    // RenderSetup.select_timeline_marks
    //
    // Select timeline marks matching the categories in the given category set 
    //
    // Arguments:
    //    'categories' (Set): Set of categories to match against [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_timeline_marks(categories = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_timeline_marks",
            {
                'categories': categories,
            }
        );
    }

    // RenderSetup.select_shot_marks
    //
    // Select shot marks matching the categories in the given category set 
    //
    // Arguments:
    //    'categories' (Set): Set of categories to match against
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shot_marks(categories)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_shot_marks",
            {
                'categories': categories,
            }
        );
    }

    // RenderSetup.select_poster_frames
    //
    // Select all shot poster frames to render 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_poster_frames()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_poster_frames",
            {
            }
        );
    }

    // RenderSetup.select_shots_of_category
    //
    // Select shots marked with one of the categories in the given category set 
    //
    // Arguments:
    //    'categories' (Set): Set of categories to match against
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    select_shots_of_category(categories)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.select_shots_of_category",
            {
                'categories': categories,
            }
        );
    }

    // RenderSetup.submit_to_queue
    //
    // Submit the current Render operation to a Queue for processing 
    //
    // Arguments:
    //    'queue' (QueueManager): QueueManager object for machine running render queue
    //    'opname' (string): Operation name to use for queue job
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (RenderOpInfo): Operation info for job added to render queue
    //
    submit_to_queue(queue, opname)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "RenderSetup.submit_to_queue",
            {
                'queue': queue,
                'opname': opname,
            }
        );
    }

};
library.register_class( 'RenderSetup', RenderSetup )
module.exports.RenderSetup = RenderSetup;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Scene
//
// Now in Scene.md
//

var Scene = class Scene extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Scene", "_id": this.target };
    }

    // Scene.parse_path
    //
    // Convert the given string into a ScenePath object contaning Host, Job, Scene components, or raise an error if the path is invalid 
    //
    // Arguments:
    //    'str' (string): Path string containing host, job, folder and scene elements
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ScenePath): A ScenePath object containing the elements of the path
    //
    parse_path(str)
    {
        return this.conn.call(
            null,
            "Scene.parse_path",
            {
                'str': str,
            }
        );
    }

    // Scene.path_to_string
    //
    // Convert the given ScenePath object into a string 
    //
    // Arguments:
    //    'scenepath' (ScenePath): ScenePath object containing Host, Job, Scene fields
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): String form of ScenePath
    //
    path_to_string(scenepath)
    {
        return this.conn.call(
            null,
            "Scene.path_to_string",
            {
                'scenepath': scenepath,
            }
        );
    }

    // Scene.create
    //
    // Create an empty Scene object, which can then be used to create a temporary scene, a new scene, or load an existing scene. 
    // After creating an empty Scene object, you must call ::temporary_scene_nonblock::, ::new_scene_nonblock:: or ::open_scene_nonblock::. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): Scene object
    //
    create()
    {
        return this.conn.call(
            null,
            "Scene.create",
            {
            }
        );
    }

    // Scene.new_scene
    //
    // Create a new scene stored in a database. This function will block until the new scene has been created in the database. If the new scene cannot be created, this function will raise an exception containing an error message. 
    //
    // Arguments:
    //    'scenepath' (ScenePath): 
    //    'options' (NewSceneOptions): Options to use for new scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): 
    //
    new_scene(scenepath, options)
    {
        return this.conn.call(
            null,
            "Scene.new_scene",
            {
                'scenepath': scenepath,
                'options': options,
            }
        );
    }

    // Scene.open_scene
    //
    // Open a scene. This function will block until the scene has been opened. If the scene cannot be opened, this function will raise an exception containing an error message. 
    //
    // Arguments:
    //    'scenepath' (ScenePath): ScenePath identifying scene to open
    //    'flags' (Set):  [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): 
    //
    open_scene(scenepath, flags = null)
    {
        return this.conn.call(
            null,
            "Scene.open_scene",
            {
                'scenepath': scenepath,
                'flags': flags,
            }
        );
    }

    // Scene.temporary_scene
    //
    // Create a temporary scene that is not stored in a database. This function will block until the temporary scene has been created. If the temporary scene cannot be created, this function will raise an exception containing an error message. 
    //
    // Arguments:
    //    'options' (NewSceneOptions): Options to use for new scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): 
    //
    temporary_scene(options)
    {
        return this.conn.call(
            null,
            "Scene.temporary_scene",
            {
                'options': options,
            }
        );
    }

    // Scene.new_scene_nonblock
    //
    // Create a new scene 
    //
    // Arguments:
    //    'scenepath' (ScenePath): 
    //    'options' (NewSceneOptions): Options to use for new scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    new_scene_nonblock(scenepath, options)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.new_scene_nonblock",
            {
                'scenepath': scenepath,
                'options': options,
            }
        );
    }

    // Scene.open_scene_nonblock
    //
    // Open a scene 
    //
    // Arguments:
    //    'scenepath' (ScenePath): ScenePath identifying scene to open
    //    'flags' (Set):  [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    open_scene_nonblock(scenepath, flags = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.open_scene_nonblock",
            {
                'scenepath': scenepath,
                'flags': flags,
            }
        );
    }

    // Scene.temporary_scene_nonblock
    //
    // Create a temporary scene that is not stored in a database 
    //
    // Arguments:
    //    'options' (NewSceneOptions): Options to use for new scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    temporary_scene_nonblock(options)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.temporary_scene_nonblock",
            {
                'options': options,
            }
        );
    }

    // Scene.save_scene
    //
    // Save changes to scene into database 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    save_scene()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.save_scene",
            {
            }
        );
    }

    // Scene.get_open_status
    //
    // Fetch status of scene open operation 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (OpenSceneStatus): 
    //
    get_open_status()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_open_status",
            {
            }
        );
    }

    // Scene.wait_until_open
    //
    // Wait for any scene opening/creation operations to complete, and return the status 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (OpenSceneStatus): 
    //
    wait_until_open()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.wait_until_open",
            {
            }
        );
    }

    // Scene.close_scene
    //
    // Close scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 on success, 0 if no scene is open.
    //
    close_scene()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.close_scene",
            {
            }
        );
    }

    // Scene.get_scene_pathname
    //
    // Get current scene's 'pathname' string (typically 'host:job:scene') 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Scene's pathname string
    //
    get_scene_pathname()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_scene_pathname",
            {
            }
        );
    }

    // Scene.get_scene_container
    //
    // Get the current container for the scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Container path for the scene
    //
    get_scene_container()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_scene_container",
            {
            }
        );
    }

    // Scene.set_scene_container
    //
    // Set the current container for the scene 
    //
    // Arguments:
    //    'container' (string): New container path for the scene
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_scene_container(container)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_scene_container",
            {
                'container': container,
            }
        );
    }

    // Scene.start_delta
    //
    // Start a 'delta' on a scene that has been opened read/write. A delta is a set of modifcations/edits on a scene that together constitute a single, logical operation/transaction. Each start_delta call must have a matching end_delta call (with one or more editing operations in between). Every delta has a user visible name (eg. 'Change Film Grade Exposure'). Once a delta has been completed/ended it becomes an atomic, undoable operation. 
    //
    // Arguments:
    //    'name' (string): Name of delta to start
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    start_delta(name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.start_delta",
            {
                'name': name,
            }
        );
    }

    // Scene.cancel_delta
    //
    // Cancel a 'delta' (a set of scene modifications/edits) previously started via 
    // the start_delta() method, reverting the Scene back to the state it was in before start_delta(). 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    cancel_delta()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.cancel_delta",
            {
            }
        );
    }

    // Scene.end_delta
    //
    // End a 'delta' (a set of scene modifications/edits) previously started via 
    // the start_delta() method. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    end_delta()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.end_delta",
            {
            }
        );
    }

    // Scene.is_read_only
    //
    // Has this scene interface been opened 'read only'. Interfaces opened read only cannot modify their scene using the standard start_delta, make changes, end_delta paradigm. At any given time, multiple interfaces may reference/open the same scene in read only mode. However, at most only a single interface may reference a scene in read/write mode  
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if the interface is read only, 0 if not (read/write)
    //
    is_read_only()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.is_read_only",
            {
            }
        );
    }

    // Scene.is_read_only_for_host
    //
    // Is the scene opened 'read only' for the host application. Note: This will be false if any interface has opened the scene in read/write mode (or the host has explicitly opened the scene read/write itself) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if the scene is read only for the host, 0 if not
    //
    is_read_only_for_host()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.is_read_only_for_host",
            {
            }
        );
    }

    // Scene.get_formats
    //
    // Return FormatSet for formats defined within this Scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (FormatSet): 
    //
    get_formats()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_formats",
            {
            }
        );
    }

    // Scene.get_scene_settings
    //
    // Return SceneSettings object for this Scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (SceneSettings): 
    //
    get_scene_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_scene_settings",
            {
            }
        );
    }

    // Scene.get_category
    //
    // Return category definition 
    //
    // Arguments:
    //    'key' (string): Key used to identify category
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (CategoryInfo): 
    //
    get_category(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_category",
            {
                'key': key,
            }
        );
    }

    // Scene.set_category
    //
    // Overwrites an existing category in the scene, or adds a new category if a category of that name doesn't exist. Will fail if an attempt is made to overwrite an built-in, read-only category. 
    //
    // Arguments:
    //    'name' (string): User-visible name for this category. This value will also act as the key identifying the category when adding categories to strips and marks.
    //    'colour' (array): Colour associated with this category
    //        '<n>' (number): RGBA components
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_category(name, colour)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_category",
            {
                'name': name,
                'colour': colour,
            }
        );
    }

    // Scene.get_mark_categories
    //
    // Return array of mark category keys 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of mark category keys
    //        '<n>' (string): Category
    //
    get_mark_categories()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_mark_categories",
            {
            }
        );
    }

    // Scene.get_strip_categories
    //
    // Return array of strip category keys 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of strip category keys
    //        '<n>' (string): Category
    //
    get_strip_categories()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_strip_categories",
            {
            }
        );
    }

    // Scene.get_start_frame
    //
    // Get frame number of start of first shot in scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_start_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_start_frame",
            {
            }
        );
    }

    // Scene.get_end_frame
    //
    // Get frame number of end of last shot in scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_end_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_end_frame",
            {
            }
        );
    }

    // Scene.get_working_frame_rate
    //
    // Get the working frame rate of the current scene (in FPS) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): The scene's frame rate (in FPS).
    //
    get_working_frame_rate()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_working_frame_rate",
            {
            }
        );
    }

    // Scene.get_record_timecode_for_frame
    //
    // Get record timecode for a given (timeline) frame number 
    //
    // Arguments:
    //    'frame_num' (number): Timeline frame number
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Record timecode
    //
    get_record_timecode_for_frame(frame_num)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_record_timecode_for_frame",
            {
                'frame_num': frame_num,
            }
        );
    }

    // Scene.get_shot_index_range
    //
    // Get index range of shots intersecting the (end exclusive) timeline frame range supplied 
    //
    // Arguments:
    //    'startFrame' (number): timeline frame range start
    //    'endFrame' (number): timeline frame range end
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (ShotIndexRange): shot index range
    //
    get_shot_index_range(startFrame, endFrame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_shot_index_range",
            {
                'startFrame': startFrame,
                'endFrame': endFrame,
            }
        );
    }

    // Scene.get_num_shots
    //
    // Get number of Shots within scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of Shots
    //
    get_num_shots()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_num_shots",
            {
            }
        );
    }

    // Scene.get_shot_id_at
    //
    // Return the ID of the shot at the timeline frame number supplied 
    //
    // Arguments:
    //    'frame' (number): Timeline frame number
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): ID of shot at frame, or -1 if none found
    //
    get_shot_id_at(frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_shot_id_at",
            {
                'frame': frame,
            }
        );
    }

    // Scene.get_shot_id
    //
    // Return the ID for the shot at the given index within the Scene 
    //
    // Arguments:
    //    'index' (number): Index of shot within scene (relative to get_num_shots)
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Shot ID
    //
    get_shot_id(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_shot_id",
            {
                'index': index,
            }
        );
    }

    // Scene.get_shot_ids
    //
    // Get an array of shots in the supplied indexed range. Each array entry 
    // is an object containing basic information for that shot. Explicitly, 
    // each shot entry will contain the following keys: 
    // * ShotId - A shot idenfifier (which can be used to obtain a Shot object via get_shot() if required). 
    // * StartFrame - The shot's timeline start frame 
    // * EndFrame - The shot's timeline end frame 
    // * PosterFrame - The shot's timeline poster frame 
    // Returns new array shot list on success, NULL on error. 
    //
    // Arguments:
    //    'firstIndex' (number): Index of first shot [Optional]
    //    'lastIndex' (number): Index of last shot [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of shot info objects
    //        '<n>' (ShotInfo): 
    //
    get_shot_ids(firstIndex = 0, lastIndex = -1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_shot_ids",
            {
                'firstIndex': firstIndex,
                'lastIndex': lastIndex,
            }
        );
    }

    // Scene.get_shot
    //
    // Create a new Shot object for the given shot ID 
    //
    // Arguments:
    //    'shot_id' (number): Identifier of shot
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Shot): Shot object
    //
    get_shot(shot_id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_shot",
            {
                'shot_id': shot_id,
            }
        );
    }

    // Scene.delete_shot
    //
    // Delete the given shot and its associated layers from the Scene 
    //
    // Arguments:
    //    'shot_id' (number): ID of Shot to be deleted. Note this is *not* an index
    //    'cleanup' (number): Flag indicating whether vertical space left by shot should be reclaimed
    //    'closeGap' (number): Flag indicating whether horizontal gap left by shot should be closed
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_shot(shot_id, cleanup, closeGap)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.delete_shot",
            {
                'shot_id': shot_id,
                'cleanup': cleanup,
                'closeGap': closeGap,
            }
        );
    }

    // Scene.insert_bars
    //
    // Insert a Bars strip into the Scene 
    //
    // Arguments:
    //    'barType' (string): The type of Bars to insert.
    //    'duration' (number): Duration for strip in frames
    //    'where' (string): Where in the scene the sequence should be inserted.
    //    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    //    'barsColourSpace' (string): Name of desired Bars colour space, or NULL
    //        to use the default Bars colour space for the barType [Optional]
    //    'stackColourSpace' (string): Name of desired Stack colour space, or NULL
    //        to use the default Stack colour space for the barType [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Shot): Shot created by inserting Blank into Scene
    //
    insert_bars(barType, duration, where, relativeTo = null, barsColourSpace = null, stackColourSpace = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.insert_bars",
            {
                'barType': barType,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'barsColourSpace': barsColourSpace,
                'stackColourSpace': stackColourSpace,
            }
        );
    }

    // Scene.insert_blank
    //
    // Insert a Blank strip into the Scene 
    //
    // Arguments:
    //    'red' (string): Red component of colour for blank
    //    'green' (string): Green component of colour for blank
    //    'blue' (string): Blue component of colour for blank
    //    'duration' (number): Duration for strip in frames
    //    'where' (string): Where in the scene the sequence should be inserted.
    //    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    //    'colourSpace' (string): Name of desired output colour space, or NULL
    //        to use the working colour space [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Shot): Shot created by inserting Blank into Scene
    //
    insert_blank(red, green, blue, duration, where, relativeTo = null, colourSpace = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.insert_blank",
            {
                'red': red,
                'green': green,
                'blue': blue,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'colourSpace': colourSpace,
            }
        );
    }

    // Scene.insert_sequence
    //
    // Insert an image/movie sequence into the Scene 
    //
    // Arguments:
    //    'sequence' (SequenceDescriptor): SequenceDescriptor for sequence to insert
    //    'where' (string): Where in the scene the sequence should be inserted.
    //    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    //    'colourSpace' (string): Input Colour Space to use for sequence. Leave NULL to determine automatically [Optional]
    //    'format' (string): Input Format to use for sequence. Leave NULL to use basic format [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Shot): Shot created by inserting SequenceDescriptor into Scene
    //
    insert_sequence(sequence, where, relativeTo = null, colourSpace = null, format = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.insert_sequence",
            {
                'sequence': sequence,
                'where': where,
                'relativeTo': relativeTo,
                'colourSpace': colourSpace,
                'format': format,
            }
        );
    }

    // Scene.insert_text
    //
    // Insert a Text strip into the Scene 
    //
    // Arguments:
    //    'text' (string): The text to rendered in the Rop.
    //    'duration' (number): Duration for strip in frames
    //    'where' (string): Where in the scene the sequence should be inserted
    //    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    //    'alignment' (string): Alignment for the text [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Shot): Shot created by inserting Text into Scene
    //
    insert_text(text, duration, where, relativeTo = null, alignment = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.insert_text",
            {
                'text': text,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'alignment': alignment,
            }
        );
    }

    // Scene.get_num_marks
    //
    // Return number of Timeline Marks in Scene 
    //
    // Arguments:
    //    'type' (string): If specified, return number of marks of this type [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of marks
    //
    get_num_marks(type = "")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_num_marks",
            {
                'type': type,
            }
        );
    }

    // Scene.get_mark_ids
    //
    // Return array of mark ids 
    //
    // Arguments:
    //    'offset' (number): Offset within list of marks to fetch from [Optional]
    //    'count' (number): Number of Mark objects to fetch, use -1 to fetch all marks [Optional]
    //    'type' (string): If specified, only return marks of this type [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Mark IDs
    //        '<n>' (number): Mark ID
    //
    get_mark_ids(offset = 0, count = -1, type = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_mark_ids",
            {
                'offset': offset,
                'count': count,
                'type': type,
            }
        );
    }

    // Scene.get_mark_ids_in_range
    //
    // Return array of mark ids within the given frame range in the Scene 
    //
    // Arguments:
    //    'startF' (number): Start frame in Scene timeline
    //    'endF' (number): End frame in Scene timeline (exclusive)
    //    'type' (string): Mark type/category [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Mark IDs
    //        '<n>' (number): Mark ID
    //
    get_mark_ids_in_range(startF, endF, type = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_mark_ids_in_range",
            {
                'startF': startF,
                'endF': endF,
                'type': type,
            }
        );
    }

    // Scene.get_mark
    //
    // Return Mark object for the given mark ID 
    //
    // Arguments:
    //    'id' (number): Mark ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Mark): Mark object matching the given mark ID
    //
    get_mark(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_mark",
            {
                'id': id,
            }
        );
    }

    // Scene.add_mark
    //
    // Add new Mark to the Scene at the given frame number 
    //
    // Arguments:
    //    'frame' (number): Frame number
    //    'category' (string): Key identifying Mark Category
    //    'note' (string): Note text for mark [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): ID of new mark object
    //
    add_mark(frame, category, note = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.add_mark",
            {
                'frame': frame,
                'category': category,
                'note': note,
            }
        );
    }

    // Scene.delete_mark
    //
    // Remove Mark object with the given ID 
    //
    // Arguments:
    //    'id' (number): Mark ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_mark(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.delete_mark",
            {
                'id': id,
            }
        );
    }

    // Scene.get_metadata_definitions
    //
    // Return array of metadata item definitions 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of MetadataItems define metadata types defined in scene
    //        '<n>' (MetadataItem): 
    //
    get_metadata_definitions()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_metadata_definitions",
            {
            }
        );
    }

    // Scene.add_metadata_defn
    //
    // Add a new Metadata Item field to the Scene 
    //
    // Arguments:
    //    'name' (string): User-visible name for Metadata Item
    //    'type' (string): Data type for Metadata Item
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (MetadataItem): Definition of new Metadata Item, including internal Key created for it
    //
    add_metadata_defn(name, type)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.add_metadata_defn",
            {
                'name': name,
                'type': type,
            }
        );
    }

    // Scene.delete_metadata_defn
    //
    // Delete a Metadata Item field from the Scene 
    //
    // Arguments:
    //    'key' (string): Key identifying metadata item to delete
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_metadata_defn(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.delete_metadata_defn",
            {
                'key': key,
            }
        );
    }

    // Scene.get_metadata_property_types
    //
    // Return list of properties that can be defined for each MetadataItem 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of MetadataProperty objects
    //        '<n>' (MetadataProperty): 
    //
    get_metadata_property_types()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_metadata_property_types",
            {
            }
        );
    }

    // Scene.get_metadata_defn_property
    //
    // Set the value for the given property for the given metadata item key 
    //
    // Arguments:
    //    'key' (string): Key identifying metadata item to modify
    //    'property' (string): Key identifying which property of the metadata item to get
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Current value for metadata item property
    //
    get_metadata_defn_property(key, property)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_metadata_defn_property",
            {
                'key': key,
                'property': property,
            }
        );
    }

    // Scene.set_metadata_defn_property
    //
    // Set the value for the given property for the given metadata item key 
    //
    // Arguments:
    //    'key' (string): Key identifying metadata item to modify
    //    'property' (string): Key identifying which property of the metadata item to set
    //    'value' (string): New property value
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_metadata_defn_property(key, property, value)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_metadata_defn_property",
            {
                'key': key,
                'property': property,
                'value': value,
            }
        );
    }

    // Scene.get_look_names
    //
    // Return names of available Looks 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of names of looks
    //        '<n>' (string): Look name
    //
    get_look_names()
    {
        return this.conn.call(
            null,
            "Scene.get_look_names",
            {
            }
        );
    }

    // Scene.get_look_infos
    //
    // Get an array of available Looks.  Each array entry 
    // is a LookInfo object containing the Name and Group 
    // for each Look. Explicitly, each entry will contain 
    // the following keys: 
    // * Name - The name of the look.   This is unique and used as an identifier 
    // * Group - The look group for the look 
    // Returns new array of LookInfo objects on success, NULL on error. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of shot info objects
    //        '<n>' (LookInfo): 
    //
    get_look_infos()
    {
        return this.conn.call(
            null,
            "Scene.get_look_infos",
            {
            }
        );
    }

    // Scene.set_transient_write_lock_deltas
    //
    // Use to enable (or disable) creation of deltas in a scene where FLAPI does not have the write lock.  In particular, this is needed for FLAPI scripts running inside the main application that wish to modify the current scene. 
    //  When you open such a delta, you are preventing anything else from being able to make normal scene modifications.  You should therefore ensure you hold it open for as short a time as possible.  
    // Note also that you should not disable transient deltas while a transient delta is in progress. 
    //
    // Arguments:
    //    'enable' (number): If non-zero, creation of deltas when FLAPI does not have the write lock will be enabled
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_transient_write_lock_deltas(enable)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_transient_write_lock_deltas",
            {
                'enable': enable,
            }
        );
    }

    // Scene.set_custom_data
    //
    // Set a custom data value in the scene with the supplied (string) key. Setting a 
    // custom data value does not require a delta. Also custom data values are unaffected 
    // by undo/redo. Existing custom data values can be deleted from a scene by supplying 
    // NULL/None/null as the data value (for an existing key). 
    //
    // Arguments:
    //    'data_key' (string): Custom data value key
    //    'data_value' (any): New data value for the given key (or NULL/None/null to delete) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_custom_data(data_key, data_value = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_custom_data",
            {
                'data_key': data_key,
                'data_value': data_value,
            }
        );
    }

    // Scene.get_custom_data
    //
    // Get a custom data value from the scene previously set using set_custom_data. 
    //
    // Arguments:
    //    'data_key' (string): Custom data value key
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (any): Custom data value found
    //
    get_custom_data(data_key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_custom_data",
            {
                'data_key': data_key,
            }
        );
    }

    // Scene.get_custom_data_keys
    //
    // Return sorted array of (string) keys that can be used to fetch scene 
    // custom data values via get_custom_data. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (string): Key string
    //
    get_custom_data_keys()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_custom_data_keys",
            {
            }
        );
    }

    // Scene.get_groups
    //
    // Return list of groups in the scene 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of group keys
    //        '<n>' (string): Groups
    //
    get_groups()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_groups",
            {
            }
        );
    }

    // Scene.get_group
    //
    // Return array of shot IDs for shots in group, or NULL if the group doesn't exist 
    //
    // Arguments:
    //    'key' (string): Key used to identify group
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Set of shot IDs [Optional]
    //        '<n>' (number): ShotId
    //
    get_group(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.get_group",
            {
                'key': key,
            }
        );
    }

    // Scene.set_group
    //
    // Create or update a group of shot IDs 
    //
    // Arguments:
    //    'key' (string): Key used to identify group
    //    'shotIDs' (array): Array of shot IDs [Optional]
    //        '<n>' (number): ShotId
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_group(key, shotIDs = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.set_group",
            {
                'key': key,
                'shotIDs': shotIDs,
            }
        );
    }

    // Scene.delete_group
    //
    // Delete Group 
    //
    // Arguments:
    //    'key' (string): Key used to identify group
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_group(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Scene.delete_group",
            {
                'key': key,
            }
        );
    }

};
library.register_class( 'Scene', Scene )
module.exports.Scene = Scene;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SceneSettings
//
// This class provides an interface to get/set scene settings, which affect all Shots in a Scene.
//

var SceneSettings = class SceneSettings extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "SceneSettings", "_id": this.target };
    }

    // SceneSettings.get_setting_keys
    //
    // Return array of keys that can be used to get/set Scene Settings parameters 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (string): Key string
    //
    get_setting_keys()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.get_setting_keys",
            {
            }
        );
    }

    // SceneSettings.get_setting_definition
    //
    // Return SceneSettings parameter type definition for the given key 
    //
    // Arguments:
    //    'key' (string): Key for SceneSettings parameter
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (SceneSettingDefinition): 
    //
    get_setting_definition(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.get_setting_definition",
            {
                'key': key,
            }
        );
    }

    // SceneSettings.get
    //
    // Return values for given SceneSettings keys 
    //
    // Arguments:
    //    'keys' (array): Array of keys
    //        '<n>' (string): Key for parameter
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): 
    //
    get(keys)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.get",
            {
                'keys': keys,
            }
        );
    }

    // SceneSettings.get_single
    //
    // Return value for given SceneSettings key 
    //
    // Arguments:
    //    'key' (string): SceneSettings Key for value wanted
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (any): 
    //
    get_single(key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.get_single",
            {
                'key': key,
            }
        );
    }

    // SceneSettings.set
    //
    // Set values for the given SceneSettings keys 
    //
    // Arguments:
    //    'values' (object): A dictionary containing new values for the given SceneSettings keys
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set(values)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.set",
            {
                'values': values,
            }
        );
    }

    // SceneSettings.set_single
    //
    // Set value for the given SceneSettings key 
    //
    // Arguments:
    //    'key' (string): SceneSettings key for value to set
    //    'value' (any): New value for the given SceneSettings key [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_single(key, value = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SceneSettings.set_single",
            {
                'key': key,
                'value': value,
            }
        );
    }

};
library.register_class( 'SceneSettings', SceneSettings )
module.exports.SceneSettings = SceneSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SequenceDescriptor
//
// A SequenceDescriptor represents a movie file (e.g. `/vol/bl000-images/myjob/media/A001_C001_00000A_001.R3D`) or a sequence of image files (e.g. `/vol/bl000-images/myjob/renders/day1_%.7F.exr`) on disk.
// It has a frame range (which does not have to cover the full length of the media on disk) and associated metadata.
// Audio-only media (e.g. OpAtom MXF audio, or .wav files) is also described using a SequenceDescriptor.
//

var SequenceDescriptor = class SequenceDescriptor extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "SequenceDescriptor", "_id": this.target };
    }

    // SequenceDescriptor.get_for_template
    //
    // Search the filesystem and return zero or more SequenceDescriptors which match the given filename template (e.g. "/vol/images/A001B002.mov" or "/vol/san/folder/%.6F.dpx", and optionally intersecting the given start and end frame numbers. 
    //
    // Arguments:
    //    'template' (string): Path to the file, using FilmLight %.#F syntax for frame numbering
    //    'start' (number): Start frame number [Optional]
    //    'end' (number): End frame number (inclusive) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of SequenceDescriptor objects
    //        '<n>' (SequenceDescriptor): 
    //
    get_for_template(template, start = null, end = null)
    {
        return this.conn.call(
            null,
            "SequenceDescriptor.get_for_template",
            {
                'template': template,
                'start': start,
                'end': end,
            }
        );
    }

    // SequenceDescriptor.get_for_template_with_timecode
    //
    // Search the filesystem and return zero or more SequenceDescriptors which match the given filename template (e.g. "/vol/images/A001B002.mov" or "/vol/san/folder/%.6F.dpx", and optionally intersecting the given start and end timecodes. 
    //
    // Arguments:
    //    'template' (string): Path to the file, using FilmLight %.#F syntax for frame numbering
    //    'startTC' (timecode): Start timecode [Optional]
    //    'endTC' (timecode): End timecode (inclusive) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of SequenceDescriptor objects
    //        '<n>' (SequenceDescriptor): 
    //
    get_for_template_with_timecode(template, startTC = null, endTC = null)
    {
        return this.conn.call(
            null,
            "SequenceDescriptor.get_for_template_with_timecode",
            {
                'template': template,
                'startTC': startTC,
                'endTC': endTC,
            }
        );
    }

    // SequenceDescriptor.get_for_file
    //
    // Create a SequenceDescriptor for a single file 
    //
    // Arguments:
    //    'filepath' (string): Path to file
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (SequenceDescriptor): SequenceDescriptor for given path
    //
    get_for_file(filepath)
    {
        return this.conn.call(
            null,
            "SequenceDescriptor.get_for_file",
            {
                'filepath': filepath,
            }
        );
    }

    // SequenceDescriptor.get_start_frame
    //
    // Return the first frame number, which does not necessarily correspond with the first frame of the files on disk. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_start_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_start_frame",
            {
            }
        );
    }

    // SequenceDescriptor.get_end_frame
    //
    // Return the last frame number, which does not necessarily correspond with the last frame of the files on disk. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_end_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_end_frame",
            {
            }
        );
    }

    // SequenceDescriptor.get_start_timecode
    //
    // Return the timecode at the first frame of the sequence. Some media can support two timecode tracks, so you must specify which one you want (0 or 1). 
    //
    // Arguments:
    //    'index' (number): Index of timecode track
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Start timecode
    //
    get_start_timecode(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_start_timecode",
            {
                'index': index,
            }
        );
    }

    // SequenceDescriptor.get_end_timecode
    //
    // Return the timecode at the last frame of the sequence. Some media can support two timecode tracks, so you must specify which one you want (0 or 1). 
    //
    // Arguments:
    //    'index' (number): Index of timecode track
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): End timecode
    //
    get_end_timecode(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_end_timecode",
            {
                'index': index,
            }
        );
    }

    // SequenceDescriptor.get_start_keycode
    //
    // Return the keycode at the first frame of the sequence. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (keycode): Start keycode
    //
    get_start_keycode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_start_keycode",
            {
            }
        );
    }

    // SequenceDescriptor.get_end_keycode
    //
    // Return the keycode at the last frame of the sequence. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (keycode): End keycode
    //
    get_end_keycode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_end_keycode",
            {
            }
        );
    }

    // SequenceDescriptor.get_start_handle
    //
    // Return the first frame number on disk (0 for movie files). 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_start_handle()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_start_handle",
            {
            }
        );
    }

    // SequenceDescriptor.get_end_handle
    //
    // Return the last frame number on disk (inclusive). 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_end_handle()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_end_handle",
            {
            }
        );
    }

    // SequenceDescriptor.get_width
    //
    // Return the width (in pixels) of the images in this sequence. Returns 0 for audio-only media. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Width
    //
    get_width()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_width",
            {
            }
        );
    }

    // SequenceDescriptor.get_height
    //
    // Return the height (in pixels) of the images in this sequence. Returns 0 for audio-only media. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Height
    //
    get_height()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_height",
            {
            }
        );
    }

    // SequenceDescriptor.get_pixel_aspect_ratio
    //
    // Return the pixel aspect ratio (width/height) of the images in this sequence. Returns 1.0 if unknown. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Aspect ratio
    //
    get_pixel_aspect_ratio()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_pixel_aspect_ratio",
            {
            }
        );
    }

    // SequenceDescriptor.get_path
    //
    // Return the path to the folder containing this sequence. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Folder path
    //
    get_path()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_path",
            {
            }
        );
    }

    // SequenceDescriptor.get_name
    //
    // Return the filename (for a movie) or the filename template (for an image sequence, using FilmLight %.#F syntax for frame numbering), excluding the folder path. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Name of sequence
    //
    get_name()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_name",
            {
            }
        );
    }

    // SequenceDescriptor.get_ext
    //
    // Return the filename extension (including the leading '.') for this sequence. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Extension
    //
    get_ext()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_ext",
            {
            }
        );
    }

    // SequenceDescriptor.get_prefix
    //
    // Return filename prefix before numeric component 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Prefix
    //
    get_prefix()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_prefix",
            {
            }
        );
    }

    // SequenceDescriptor.get_postfix
    //
    // Return filename postfix after numeric component 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Postfix
    //
    get_postfix()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_postfix",
            {
            }
        );
    }

    // SequenceDescriptor.get_format_len
    //
    // Return number of digits in numerical component of filename 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of digits
    //
    get_format_len()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_format_len",
            {
            }
        );
    }

    // SequenceDescriptor.get_base_filename_with_F
    //
    // Return filename (without path) using FilmLight %.#F syntax for the frame number pattern 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename template
    //
    get_base_filename_with_F()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_base_filename_with_F",
            {
            }
        );
    }

    // SequenceDescriptor.get_base_filename_with_d
    //
    // Return filename (without path) using printf %0#d syntax for the frame number pattern 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename template
    //
    get_base_filename_with_d()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_base_filename_with_d",
            {
            }
        );
    }

    // SequenceDescriptor.get_full_filename_with_F
    //
    // Return filename (with path) using FilmLight %.#F syntax for the frame number pattern 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename
    //
    get_full_filename_with_F()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_full_filename_with_F",
            {
            }
        );
    }

    // SequenceDescriptor.get_full_filename_with_d
    //
    // Return filename (with path) using printf %0#d syntax for the frame number pattern 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename
    //
    get_full_filename_with_d()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_full_filename_with_d",
            {
            }
        );
    }

    // SequenceDescriptor.get_base_filename
    //
    // Return filename (without path) for the given frame number 
    //
    // Arguments:
    //    'frame' (number): Frame number
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename
    //
    get_base_filename(frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_base_filename",
            {
                'frame': frame,
            }
        );
    }

    // SequenceDescriptor.get_filename_for_frame
    //
    // Return filename (with path) for the given frame number 
    //
    // Arguments:
    //    'frame' (number): Frame number
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Filename
    //
    get_filename_for_frame(frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_filename_for_frame",
            {
                'frame': frame,
            }
        );
    }

    // SequenceDescriptor.get_tape
    //
    // Return the tape name. Some media can support two tracks, so you must specify which one you want (0 or 1). 
    //
    // Arguments:
    //    'index' (number): Index of timecode track
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Tape name
    //
    get_tape(index)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_tape",
            {
                'index': index,
            }
        );
    }

    // SequenceDescriptor.get_metadata
    //
    // Return the metadata read when the sequence was scanned on disk, in human-readable form. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Metadata
    //
    get_metadata()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_metadata",
            {
            }
        );
    }

    // SequenceDescriptor.is_movie
    //
    // Return whether sequence is a movie file 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag
    //
    is_movie()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.is_movie",
            {
            }
        );
    }

    // SequenceDescriptor.has_blg
    //
    // Return whether sequence has BLG (Baselight Linked Grade) information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag
    //
    has_blg()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.has_blg",
            {
            }
        );
    }

    // SequenceDescriptor.is_blg
    //
    // Return whether sequence is a BLG (Baselight Linked Grade) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag
    //
    is_blg()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.is_blg",
            {
            }
        );
    }

    // SequenceDescriptor.has_audio
    //
    // Return whether movie file has audio 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag
    //
    has_audio()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.has_audio",
            {
            }
        );
    }

    // SequenceDescriptor.get_audio_channels
    //
    // Return number of audio channels in movie 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of channels
    //
    get_audio_channels()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_audio_channels",
            {
            }
        );
    }

    // SequenceDescriptor.get_audio_sample_rate
    //
    // Return audio sample rate (in Hz) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Sample rate
    //
    get_audio_sample_rate()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_audio_sample_rate",
            {
            }
        );
    }

    // SequenceDescriptor.get_audio_length_in_samples
    //
    // Return total number of audio samples in file 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Length
    //
    get_audio_length_in_samples()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.get_audio_length_in_samples",
            {
            }
        );
    }

    // SequenceDescriptor.trim_movie
    //
    // Create (if possible) a trimmed copy of the movie specified by this descriptor 
    //
    // Arguments:
    //    'output' (string): Output movie file name
    //    'start' (number): Start frame of output movie
    //    'length' (number): Number of frames to write to output movie
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    No result
    //
    trim_movie(output, start, length)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "SequenceDescriptor.trim_movie",
            {
                'output': output,
                'start': start,
                'length': length,
            }
        );
    }

};
library.register_class( 'SequenceDescriptor', SequenceDescriptor )
module.exports.SequenceDescriptor = SequenceDescriptor;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Shot
//
// A shot in Baselight is a set of strips comprising a top strip (typically containing a Sequence operator referencing input media) and the strips lying directly underneath it. These strips apply image-processing and other operations to the top strip.
//

var Shot = class Shot extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Shot", "_id": this.target };
    }

    // Shot.is_valid
    //
    //  Called to determine if the shot object references a valid top strip an open scene. A shot object may become invalid in a couple of ways: 
    //   * The scene which it is in is closed. 
    //   * The shot's top strip is removed from the scene's timeline. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if this shot interface is valid, 0 if not.
    //
    is_valid()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.is_valid",
            {
            }
        );
    }

    // Shot.get_scene
    //
    // Get the scene object which this shot is a part of. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Scene): The shot's scene.
    //
    get_scene()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_scene",
            {
            }
        );
    }

    // Shot.get_id
    //
    // Get the shot's identifier, an integer which uniquely identifies the shot within the timeline. The id is persistent, remaining constant even if the scene containing the shot is closed and reopened.  
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): The shot's unique identifier.
    //
    get_id()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_id",
            {
            }
        );
    }

    // Shot.get_start_frame
    //
    // Get the start frame of the shot within the scene which contains it. Because the time extent of a shot is actually defined by the shot's top strip, the start frame is actually the start frame of the top strip. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Start frame of the shot (inclusive).
    //
    get_start_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_start_frame",
            {
            }
        );
    }

    // Shot.get_end_frame
    //
    // Get the end frame of the shot within the scene which contains it. Because the time extent of a shot is defined by the shot's top strip, the end frame is actually the end frame of the top strip. In Baselight, shot extents are defined in floating-point frames and are start-inclusive and end-exclusive. This means that the shot goes all the way up to the beginning of the end frame, but doesn't include it.  
    // So a 5-frame shot  starting at frame 100.0 would have an end frame 105.0 and 104.75, 104.9 and 104.99999 would all lie within the shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): End frame of the shot (exclusive).
    //
    get_end_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_end_frame",
            {
            }
        );
    }

    // Shot.get_poster_frame
    //
    // Get the poster frame of the shot within the scene that contains it.  
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Poster frame number of the shot.
    //
    get_poster_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_poster_frame",
            {
            }
        );
    }

    // Shot.get_start_timecode
    //
    // Get the start record timecode of the shot 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Start record timecode of the shot
    //
    get_start_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_start_timecode",
            {
            }
        );
    }

    // Shot.get_end_timecode
    //
    // Get the end record timecode of the shot 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): End record timecode of the shot (exclusive)
    //
    get_end_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_end_timecode",
            {
            }
        );
    }

    // Shot.get_timecode_at_frame
    //
    // Get the record timecode at the given frame within the shot 
    //
    // Arguments:
    //    'frame' (number): Frame relative to start of shot
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Record timecode for frame
    //
    get_timecode_at_frame(frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_timecode_at_frame",
            {
                'frame': frame,
            }
        );
    }

    // Shot.get_src_start_frame
    //
    // Return start frame number within source sequence/movie 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_src_start_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_start_frame",
            {
            }
        );
    }

    // Shot.get_src_end_frame
    //
    // Return end frame number within source sequence/movie (exclusive) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Frame number
    //
    get_src_end_frame()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_end_frame",
            {
            }
        );
    }

    // Shot.get_src_start_timecode
    //
    // Return start timecode within source sequence/movie 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Start source timecode
    //
    get_src_start_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_start_timecode",
            {
            }
        );
    }

    // Shot.get_src_end_timecode
    //
    // Return end timecode within source sequence/movie (exclusive) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): End source timecode
    //
    get_src_end_timecode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_end_timecode",
            {
            }
        );
    }

    // Shot.get_src_timecode_at_frame
    //
    // Return source timecode at the given frame within the shot 
    //
    // Arguments:
    //    'frame' (number): Frame number relative to start of shot
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Timecode for given frame
    //
    get_src_timecode_at_frame(frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_timecode_at_frame",
            {
                'frame': frame,
            }
        );
    }

    // Shot.get_src_start_keycode
    //
    // Return start keycode within source sequence/movie 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (keycode): Start source keycode
    //
    get_src_start_keycode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_start_keycode",
            {
            }
        );
    }

    // Shot.get_src_end_keycode
    //
    // Return end keycode within source sequence/movie (exclusive) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (keycode): End source keycode
    //
    get_src_end_keycode()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_src_end_keycode",
            {
            }
        );
    }

    // Shot.get_input_colour_space
    //
    // Return the input colour space defined for this shot. Can be 'None', indicating no specific colour space defined. For RAW codecs, this may be 'auto' indicating that the input colour space will be determined by the SDK used to decode to the image data. In either case the actual input colour space can be determined by call get_actual_input_colour_space(). 
    //
    // Arguments:
    //    'eye' (string): Find input colour space for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Colour space name, or 'auto'
    //
    get_input_colour_space(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_input_colour_space",
            {
                'eye': eye,
            }
        );
    }

    // Shot.set_input_colour_space
    //
    // Set the input colour space 
    //
    // Arguments:
    //    'name' (string): Input colour space name, or 'Auto'
    //    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_input_colour_space(name, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_input_colour_space",
            {
                'name': name,
                'eye': eye,
            }
        );
    }

    // Shot.get_actual_input_colour_space
    //
    // Return the input colour space for this shot. 
    // If the input colour space is set to 'Auto', the actual colour space name will be returned. 
    //
    // Arguments:
    //    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Colour space name
    //
    get_actual_input_colour_space(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_actual_input_colour_space",
            {
                'eye': eye,
            }
        );
    }

    // Shot.get_input_format
    //
    // Return the input format name for this shot 
    //
    // Arguments:
    //    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Format name
    //
    get_input_format(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_input_format",
            {
                'eye': eye,
            }
        );
    }

    // Shot.set_input_format
    //
    // Set the input format name for this shot 
    //
    // Arguments:
    //    'name' (string): Format name
    //    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_input_format(name, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_input_format",
            {
                'name': name,
                'eye': eye,
            }
        );
    }

    // Shot.get_input_video_lut
    //
    // Return the input video lut value for this shot 
    //
    // Arguments:
    //    'eye' (string): Input video LUT for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Input Video LUT (either VIDEOLUT_NONE or VIDEOLUT_UNSCALE) or NULL/None/null if an input video LUT is inappropriate for the shot's current media type and input colour space settings (indicated by the "Legal to Full Scale" button not being present in the Baselight Sequence operator UI.
    //
    get_input_video_lut(eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_input_video_lut",
            {
                'eye': eye,
            }
        );
    }

    // Shot.set_input_video_lut
    //
    // Set the input video LUT for this shot 
    //
    // Arguments:
    //    'video_lut' (string): Video LUT to be applied to the input sequence. The only permitted values for this method are VIDEOLUT_UNSCALE and VIDEOLUT_NONE.
    //    'eye' (string): Input video LUT for the given eye in a stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_input_video_lut(video_lut, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_input_video_lut",
            {
                'video_lut': video_lut,
                'eye': eye,
            }
        );
    }

    // Shot.get_metadata
    //
    // Get metadata values for the keys provided. The possible keys and the value type for each key are obtained using the Scene.get_metadata_definitions method. 
    //
    // Arguments:
    //    'md_keys' (Set): Set of metadata keys whose values are required.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Key/value pairs containing the metadata obtained.
    //
    get_metadata(md_keys)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_metadata",
            {
                'md_keys': md_keys,
            }
        );
    }

    // Shot.get_metadata_strings
    //
    // Get metadata values expressed as strings for the keys provided. The possible keys are obtained using the Scene.get_metadata_definitions method. 
    //
    // Arguments:
    //    'md_keys' (Set): Set of metadata keys whose values are required.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Key/value pairs containing the metadata obtained. All the values will have been converted to strings.
    //
    get_metadata_strings(md_keys)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_metadata_strings",
            {
                'md_keys': md_keys,
            }
        );
    }

    // Shot.set_metadata
    //
    // Set metadata values for the keys provided. The possible keys and the value type for each key are obtained using the Scene.get_metadata_definitions method. 
    //
    // Arguments:
    //    'metadata' (object): Key/value pairs of metadata to assign in the shot.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_metadata(metadata)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_metadata",
            {
                'metadata': metadata,
            }
        );
    }

    // Shot.get_sequence_descriptor
    //
    // Get a SequenceDescriptor object that represents the input media for this shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (SequenceDescriptor): Object containing information about the shot's input media.
    //
    get_sequence_descriptor()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_sequence_descriptor",
            {
            }
        );
    }

    // Shot.supports_client_event_data
    //
    // Does this shot support client event lists/data. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 if the shot supports client event data, otherwise 0.
    //
    supports_client_event_data()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.supports_client_event_data",
            {
            }
        );
    }

    // Shot.get_client_event_list
    //
    // Get array of client events (notes/flags) for either an entire shot, or a specific frame of a shot. When querying the event list at a specific frame, NULL/None/null will be returned if no event list exists at that frame or the shot. The events array returned will be chronologically sorted (oldest first). Each event entry is itself a dictionary describing that event. 
    //
    // Arguments:
    //    'list_frame' (number): Identifies which event list to return; either for the entire shot (if no list_frame supplied), or for a specific, shot start relative frame number [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of client events for the shot.
    //        '<n>' (object): Client event entry.
    //            'ClientName' (string): The name of the client that added the entry.
    //            'EventId' (number): Identifier used to modify/delete this event.
    //            'EventType' (string): The event type. Currently either "Note" or "Flag".
    //            'NoteText' (string): Only valid when "EventType" value is "Note". The note text. [Optional]
    //            'RelativeTimeString' (string): Time the entry was created as a formatted as a user friendly string (eg. "Tuesday 17:25").
    //            'Source' (string): Source of the event. Either "FLAPI" if event was added from an external source, or "Application" if added from the Filmlight host application.
    //            'Time' (number): Time the entry was created (in seconds since 1/1/70 UTC).
    //
    get_client_event_list(list_frame = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_client_event_list",
            {
                'list_frame': list_frame,
            }
        );
    }

    // Shot.add_client_note
    //
    // Add a client note to either the client event list for an entire shot, or to the client event list at a specific frame number. 
    //
    // Arguments:
    //    'client_name' (string): Name of client adding the note.
    //    'note_text' (string): Note text.
    //    'event_list_frame' (number): Client event list frame number, or NULL/None/null for the entire shot's client event list [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Event identifier which can be used to edit/delete the note later.
    //
    add_client_note(client_name, note_text, event_list_frame = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.add_client_note",
            {
                'client_name': client_name,
                'note_text': note_text,
                'event_list_frame': event_list_frame,
            }
        );
    }

    // Shot.add_client_flag
    //
    // Add a new client flag entry to either the client event list for an entire shot, or to the client event list at a specific frame number. A client event list only supports a single flag event for a given client name; If one already exists, a call to this method will replace it with a new one.  
    //
    // Arguments:
    //    'client_name' (string): Name of client flagging the shot.
    //    'event_list_frame' (number): Client event list frame number, or NULL/None/null for the entire shot's client event list [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Event identifier which can be used to remove the flag later.
    //
    add_client_flag(client_name, event_list_frame = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.add_client_flag",
            {
                'client_name': client_name,
                'event_list_frame': event_list_frame,
            }
        );
    }

    // Shot.delete_client_event
    //
    // Delete the (note or flag) event with the supplied id from the shot's client event list. 
    //
    // Arguments:
    //    'event_id' (string): Event list identifier of event to delete.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): 1 on success, 0 if no event found.
    //
    delete_client_event(event_id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.delete_client_event",
            {
                'event_id': event_id,
            }
        );
    }

    // Shot.set_client_event_metadata
    //
    // Set custom metadata key/value pairs for the client event with the supplied ID. 
    //
    // Arguments:
    //    'client_event_id' (number): ID of client event
    //    'metadata' (object): Key/value pairs containing the metadata for the client event.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_client_event_metadata(client_event_id, metadata)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'metadata': metadata,
            }
        );
    }

    // Shot.get_client_event_metadata
    //
    // Get custom metadata key/value pairs for the client event with the supplied ID. 
    //
    // Arguments:
    //    'client_event_id' (number): ID of client event
    //    'md_keys' (Set): Set of metadata keys whose values are required, or NULL/None/null for all metadata. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Key/value pairs containing the metadata for the client event.
    //
    get_client_event_metadata(client_event_id, md_keys = null)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'md_keys': md_keys,
            }
        );
    }

    // Shot.delete_client_event_metadata
    //
    // Delete a single metadata key/value item from the client event with the supplied ID. 
    //
    // Arguments:
    //    'client_event_id' (number): ID of client event
    //    'metadata_key' (any): Key of metadata item to remove from client event.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_client_event_metadata(client_event_id, metadata_key)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.delete_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'metadata_key': metadata_key,
            }
        );
    }

    // Shot.get_client_event_list_frames
    //
    // Get array of (shot start relative) frame numbers of frames with client event lists 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of frames with client event lists
    //        '<n>' (number): frame number
    //
    get_client_event_list_frames()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_client_event_list_frames",
            {
            }
        );
    }

    // Shot.delete_frame_client_event_list
    //
    // Delete the entire client event list at the given shot frame (if any). 
    //
    // Arguments:
    //    'list_frame' (number): Frame number of frame containing the event list
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_frame_client_event_list(list_frame)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.delete_frame_client_event_list",
            {
                'list_frame': list_frame,
            }
        );
    }

    // Shot.get_client_data_summary
    //
    // Get summary info on any client data associated with this shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Client summary info
    //        'Clients' (object): Dictionary containing client name keys/entries for all clients who have added data to this shot. The value associated with each key is a set containing all the types of data that client has added ("Note" and/or "Flag").
    //
    get_client_data_summary()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_client_data_summary",
            {
            }
        );
    }

    // Shot.get_num_marks
    //
    // Get number of marks within shot. 
    // If type is supplied, only return number of marks of the given type 
    //
    // Arguments:
    //    'type' (string): Mark type
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Number of marks
    //
    get_num_marks(type)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_num_marks",
            {
                'type': type,
            }
        );
    }

    // Shot.get_mark_ids
    //
    // Get shot mark ids within the shot. 
    // Shot marks are marks which are attached to the shot's top strip. 
    // If type is specified, only return marks of matching type. 
    //
    // Arguments:
    //    'offset' (number): Offset into array of marks [Optional]
    //    'count' (number): Number of marks to fetch, pass -1 to fetch all [Optional]
    //    'type' (string): Mark type, which is a category name. Only shot marks of this type will be returned. If not provided, all marks within the shot will be returned. Possible categories for marks can be obtained using the Scene.get_mark_categories method. [Optional]
    //    'eye' (string): Which eye to get marks for stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of Mark IDs
    //        '<n>' (number): Mark ID
    //
    get_mark_ids(offset = 0, count = -1, type = null, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_mark_ids",
            {
                'offset': offset,
                'count': count,
                'type': type,
                'eye': eye,
            }
        );
    }

    // Shot.get_mark
    //
    // Get Mark object for given ID 
    //
    // Arguments:
    //    'id' (number): Mark ID
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Mark): Mark object
    //
    get_mark(id)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_mark",
            {
                'id': id,
            }
        );
    }

    // Shot.add_mark
    //
    // Add new Mark to the shot at the given source frame 
    //
    // Arguments:
    //    'frame' (number): Source frame number
    //    'category' (string): Mark category
    //    'note' (string): Mark note text [Optional]
    //    'eye' (string): Which eye to add mark for in stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Mark ID
    //
    add_mark(frame, category, note = null, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.add_mark",
            {
                'frame': frame,
                'category': category,
                'note': note,
                'eye': eye,
            }
        );
    }

    // Shot.delete_mark
    //
    // Delete the Mark object with the given mark ID 
    //
    // Arguments:
    //    'id' (number): Mark ID
    //    'eye' (string): Which eye to delete mark for in stereo sequence [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_mark(id, eye = "GMSE_MONO")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.delete_mark",
            {
                'id': id,
                'eye': eye,
            }
        );
    }

    // Shot.get_categories
    //
    // Get the set of categories assigned to this shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Set): Set of category keys. The Scene.get_category method can be used to obtain information (such as the UI colour and user-readable name) about a given category key.
    //
    get_categories()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_categories",
            {
            }
        );
    }

    // Shot.set_categories
    //
    // Set the categories assigned to this shot 
    //
    // Arguments:
    //    'categories' (Set): Set of category keys to be assigned to the shot.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_categories(categories)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_categories",
            {
                'categories': categories,
            }
        );
    }

    // Shot.insert_blg_stack
    //
    // Insert a BLG stack at the bottom of the shot. 
    //
    // Arguments:
    //    'blg_path' (string): Path to the BLG to be applied to the shot.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_blg_stack(blg_path)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_blg_stack",
            {
                'blg_path': blg_path,
            }
        );
    }

    // Shot.get_blg_payload
    //
    // Returns the BLG payload for this shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): String containing the payload.
    //
    get_blg_payload()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_blg_payload",
            {
            }
        );
    }

    // Shot.apply_blg_payload
    //
    // Insert a BLG stack at the bottom of the shot. 
    //
    // Arguments:
    //    'blg_payload' (string): A BLG payload as returned by get_blg_payload().
    //    'blg_resources' (string): BLG resources as returned by get_blg_resources().
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    apply_blg_payload(blg_payload, blg_resources)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.apply_blg_payload",
            {
                'blg_payload': blg_payload,
                'blg_resources': blg_resources,
            }
        );
    }

    // Shot.get_blg_resources
    //
    // Returns the BLG resources for this shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): String containing the resources.
    //
    get_blg_resources()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_blg_resources",
            {
            }
        );
    }

    // Shot.insert_basegrade_layer
    //
    // Insert a BaseGrade layer at the bottom of the stack. 
    //
    // Arguments:
    //    'values' (object): A dictionary containing new values for the given 
    //        BaseGrade parameters.  Valid keys are 
    //        BalanceExposure, BalanceA, BalanceB, 
    //        Flare, 
    //        Saturation, 
    //        Contrast, 
    //        LightExposure, LightA, LightB, 
    //        DimExposure, DimA, DimB, 
    //        BrightExposure, BrightA, BrightB, 
    //        DarkExposure, DarkA, DarkB, 
    //        ContrastPivot, 
    //        LightPivot, LightFalloff, 
    //        DimPivot, DimFalloff, 
    //        BrightPivot, BrightFalloff, 
    //        DarkPivot, DarkFalloff, 
    //        LightSaturation, 
    //        DimSaturation, 
    //        BrightSaturation, 
    //        DarkSaturation
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_basegrade_layer(values)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_basegrade_layer",
            {
                'values': values,
            }
        );
    }

    // Shot.insert_cdl_layer
    //
    // Insert a CDLGrade layer at the bottom of the shot. 
    //
    // Arguments:
    //    'cdl_values' (array): CDL values (Slope R, Slope G, Slope B, Offset R, Offset G, Offset B, Power R, Power G, Power B, Saturation).
    //        '<n>' (number): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_cdl_layer(cdl_values)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_cdl_layer",
            {
                'cdl_values': cdl_values,
            }
        );
    }

    // Shot.insert_cdl_layer_above
    //
    // Insert a CDLGrade layer at the top of the shot. 
    //
    // Arguments:
    //    'cdl_values' (array): CDL values (Slope R, Slope G, Slope B, Offset R, Offset G, Offset B, Power R, Power G, Power B, Saturation).
    //        '<n>' (number): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_cdl_layer_above(cdl_values)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_cdl_layer_above",
            {
                'cdl_values': cdl_values,
            }
        );
    }

    // Shot.insert_look_layer
    //
    // Insert a Look kayer at the bottom of the shot. 
    //
    // Arguments:
    //    'look_name' (string): Name of the Look to be inserted.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_look_layer(look_name)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_look_layer",
            {
                'look_name': look_name,
            }
        );
    }

    // Shot.insert_truelight_layer
    //
    // Insert a Truelight layer at the bottom of the shot. The Truelight operator is used for applying 1D and 3D LUTs to an image. 
    //
    // Arguments:
    //    'lut_path' (string): Path to the LUT file to be set in the newly created Truelight operator.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_truelight_layer(lut_path)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_truelight_layer",
            {
                'lut_path': lut_path,
            }
        );
    }

    // Shot.insert_shape_layer_from_svg
    //
    // Insert a layer with a shape strip populated from an SVG file at the bottom of the shot. 
    //
    // Arguments:
    //    'svg_path' (string): Path to the SVG file used to populate the layer's shape strip.
    //    'fit_mode' (string): Controls how an SVG is transformed/fitted into the shape strip.
    //    'mask_format' (string): Fit to this format and mask (supplied in 'mask_name' parameter). If set, the SVG will be transformed/fitted to this format's mask area mapped to the working format area. If none supplied, the SVG will be transformed/fitted to the entire working format area. [Optional]
    //    'mask_name' (string): Mask name (from the 'mask_format'). This may be used to further constrain fitting of the SVG to the working format area (see above). [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_shape_layer_from_svg(svg_path, fit_mode, mask_format = "", mask_name = "")
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_shape_layer_from_svg",
            {
                'svg_path': svg_path,
                'fit_mode': fit_mode,
                'mask_format': mask_format,
                'mask_name': mask_name,
            }
        );
    }

    // Shot.insert_colour_space_layer
    //
    // Insert a ColourSpace operator at the bottom of the stack for this shot 
    //
    // Arguments:
    //    'toColourSpace' (string): Name of Output Colour Space
    //    'drt' (string): Name of DRT to use when converting between scene-referred and display-referred colour spaces.
    //        Default is 'scene' which uses Scene's current Display Render Transform. [Optional]
    //    'identify' (number): Set to 1 to indicate the Colour Space operator is being used to tag/identify the colour space at this point in the stack, without any colour conversions.
    //        This would be applicable when using the Colour Space operator after a Truelight operator. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_colour_space_layer(toColourSpace, drt = "scene", identify = 0)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_colour_space_layer",
            {
                'toColourSpace': toColourSpace,
                'drt': drt,
                'identify': identify,
            }
        );
    }

    // Shot.insert_lut_layer
    //
    // Insert a LUT operator at the bottom of the stack for this shot 
    //
    // Arguments:
    //    'location' (string): Specify where LUT data is stored.
    //    'file' (string): Path to LUT file. You can use %C/ to use a path relative to the Scene's container. [Optional]
    //    'inputColourSpace' (string): Name of Input Colour Space for this LUT.
    //    'outputColourSpace' (string): Name of Output Colour Space for this LUT
    //    'inputLegalRange' (number): Flag indicating that input to LUT is expected to be video-legal range. Defautls to 0 to indicate full-range. [Optional]
    //    'outputLegalRange' (number): Flag indicating that output of LUT is video-legal range. Defaults to 0 to indicate full-range. [Optional]
    //    'tetrahedral' (number): Flag indicating that high-quality tetrahedral interpolation should be used. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    insert_lut_layer(location, file = null, inputColourSpace, outputColourSpace, inputLegalRange = 0, outputLegalRange = 0, tetrahedral = 1)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.insert_lut_layer",
            {
                'location': location,
                'file': file,
                'inputColourSpace': inputColourSpace,
                'outputColourSpace': outputColourSpace,
                'inputLegalRange': inputLegalRange,
                'outputLegalRange': outputLegalRange,
                'tetrahedral': tetrahedral,
            }
        );
    }

    // Shot.delete_all_layers
    //
    // Remove all layers from the shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_all_layers()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.delete_all_layers",
            {
            }
        );
    }

    // Shot.get_codec
    //
    // Method to obtain the codec of the input media of the shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): A short string containing the codec name, or NULL if the codec couldn't be determined.
    //
    get_codec()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_codec",
            {
            }
        );
    }

    // Shot.get_decode_parameter_types
    //
    // Return list of supported decode parameter codec keys 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of supported decode parameter codec keys
    //        '<n>' (string): Decode Parameter codec key
    //
    get_decode_parameter_types()
    {
        return this.conn.call(
            null,
            "Shot.get_decode_parameter_types",
            {
            }
        );
    }

    // Shot.get_decode_parameter_type_for_codec
    //
    // Return the key identifying the decode parameters type to use for the given video codec 
    //
    // Arguments:
    //    'codec' (string): Name of codec
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Decode Parameter type key
    //
    get_decode_parameter_type_for_codec(codec)
    {
        return this.conn.call(
            null,
            "Shot.get_decode_parameter_type_for_codec",
            {
                'codec': codec,
            }
        );
    }

    // Shot.get_decode_parameter_definitions
    //
    // Static method called to obtain the image decode parameter definitions for a given codec. The decode parameters are used to control how an RGBA image is generated from RAW formats like ARRIRAW, R3D etc. 
    //  This method returns an array of image decode parameter definitions for a given decode parameter type, one per parameter. Each parameter definition is a collection of key/value pairs, with different entries dependent on the type of parameter. 
    //
    // Arguments:
    //    'decode_type' (string): Type of decode parameter definitions to be obtained
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): An array containing parameter definitions as defined above.
    //        '<n>' (DecodeParameterDefinition): 
    //
    get_decode_parameter_definitions(decode_type)
    {
        return this.conn.call(
            null,
            "Shot.get_decode_parameter_definitions",
            {
                'decode_type': decode_type,
            }
        );
    }

    // Shot.get_decode_parameters
    //
    // This method returns the image decode parameters for the shot. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Key/value pairs containing the current decode parameters. The meaning of the various keys can be discovered using the Shot.get_decode_parameter_definitions static method.
    //
    get_decode_parameters()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_decode_parameters",
            {
            }
        );
    }

    // Shot.set_decode_parameters
    //
    // Set some or all of the image decode parameters for the shot. 
    //
    // Arguments:
    //    'decode_params' (object): Key/value pairs containing new decode parameter values. The allowable keys and valid values for those keys can be discovered using the get_decode_parameter_definitions static method. It is not necessary to specify all the parameters - any parameters not set will remain untouched.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_decode_parameters(decode_params)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_decode_parameters",
            {
                'decode_params': decode_params,
            }
        );
    }

    // Shot.get_audio_settings
    //
    // Return the audio settings defined for this shot. Returns NULL if the shot has no audio defined. 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (AudioSequenceSettings): Audio settings for shot
    //
    get_audio_settings()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.get_audio_settings",
            {
            }
        );
    }

    // Shot.set_audio_settings
    //
    // Set the audio settings for this shot.  
    //
    // Arguments:
    //    'audio_settings' (AudioSequenceSettings): New audio settings for shot
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_audio_settings(audio_settings)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.set_audio_settings",
            {
                'audio_settings': audio_settings,
            }
        );
    }

    // Shot.bypass_all_layers
    //
    // Bypass/unbypass all layers in the shot. 
    //
    // Arguments:
    //    'bypass' (number): Whether to bypass or unbypass the shot's layers.
    //    'ignore_top_layer' (number): Whether to ignore the top-most layer, flag indicating true or false.
    //    'ignore_bottom_layer' (number): Whether to ignore the bottom-most layer, flag indicating true or false.
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    bypass_all_layers(bypass, ignore_top_layer, ignore_bottom_layer)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Shot.bypass_all_layers",
            {
                'bypass': bypass,
                'ignore_top_layer': ignore_top_layer,
                'ignore_bottom_layer': ignore_bottom_layer,
            }
        );
    }

};
library.register_class( 'Shot', Shot )
module.exports.Shot = Shot;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SystemInfo
//
// Provides information about hardware, OS and software
//

var SystemInfo = class SystemInfo extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "SystemInfo", "_id": this.target };
    }

    // SystemInfo.get_hardware_info
    //
    // Return base hardware information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Hardware information
    //        'Manufacturer' (string): Hardware manufacturer
    //        'Model' (string): Hardware model
    //        'Motherboard' (string): Motherboard model
    //
    get_hardware_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_hardware_info",
            {
            }
        );
    }

    // SystemInfo.get_os_info
    //
    // Return information about the OS installed in this system 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): OS version info
    //        'OSPlatform' (string): Platform is this software running on
    //        'OSVersion' (string): Version of operating system
    //
    get_os_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_os_info",
            {
            }
        );
    }

    // SystemInfo.get_cpu_info
    //
    // Return CPU hardware information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): CPU Info
    //        'Model' (string): CPU Model
    //        'NumCores' (number): Total number of CPU cores
    //        'NumSockets' (number): Number of CPU sockets
    //        'Speed' (string): CPU Speed
    //
    get_cpu_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_cpu_info",
            {
            }
        );
    }

    // SystemInfo.get_memory_info
    //
    // Return memory hardware information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): Memory information
    //        'Total' (number): Total memory in megabytes
    //
    get_memory_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_memory_info",
            {
            }
        );
    }

    // SystemInfo.get_gpu_info
    //
    // Return GPU hardware information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of GPU information
    //        '<n>' (object): GPU Information
    //            'Memory' (number): Memory size
    //            'Model' (string): Model name
    //
    get_gpu_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_gpu_info",
            {
            }
        );
    }

    // SystemInfo.get_sdi_info
    //
    // Return SDI hardware information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (object): SDI device information
    //            'Driver' (string): SDI driver version
    //            'Firmware' (string): SDI firmware version
    //            'ID' (string): SDI hardware model
    //            'Serial' (string): SDI hardware serial number
    //            'Type' (string): SDI hardware type
    //
    get_sdi_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_sdi_info",
            {
            }
        );
    }

    // SystemInfo.get_network_info
    //
    // Return network interface information 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (object): General network information
    //        'Hostname' (string): Network hostname
    //        'Interfaces' (array): Array of network interfaces
    //            '<n>' (object): Interface information
    //                'Device' (string): Device name
    //                'IPv4Address' (array): Array of IPv4 addresses
    //                    '<n>' (string): IPv4 address
    //                'IPv4Mode' (string): Address mode: Manual, DHCP
    //                'Link' (number): Flag indicating that interface has a link
    //                'LinkSpeed' (string): Current link speed in MBbit/sec
    //                'MACAddress' (string): Ethernet MAC Address
    //                'Name' (string): Interface name
    //                'Running' (number): Flag indicating that interface is enabled
    //                'Speed' (string): Maximum link speed in Mbit/sec
    //        'ZCHostname' (string): Zeroconf hostname
    //
    get_network_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_network_info",
            {
            }
        );
    }

    // SystemInfo.get_software_info
    //
    // Return array of installed applications 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): 
    //        '<n>' (object): Installed software information
    //            'Current' (number): Flag indicating that this is the currently active software version
    //            'Path' (string): Path to installed product
    //            'Product' (string): Product name
    //            'Version' (string): Product version
    //
    get_software_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_software_info",
            {
            }
        );
    }

    // SystemInfo.switch_software_version
    //
    // Switch active software version 
    //
    // Arguments:
    //    'product' (string): Product name
    //    'version' (string): Product version
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    switch_software_version(product, version)
    {
        return this.conn.call(
            null,
            "SystemInfo.switch_software_version",
            {
                'product': product,
                'version': version,
            }
        );
    }

    // SystemInfo.get_customer_info
    //
    // Return customer info dictionary (populated from preferences) 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (CustomerInfo): 
    //
    get_customer_info()
    {
        return this.conn.call(
            null,
            "SystemInfo.get_customer_info",
            {
            }
        );
    }

};
library.register_class( 'SystemInfo', SystemInfo )
module.exports.SystemInfo = SystemInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ThumbnailManager
//
// Interface used to generate shot thumbnails
//

var ThumbnailManager = class ThumbnailManager extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "ThumbnailManager", "_id": this.target };
    }

    // ThumbnailManager.get_poster_uri
    //
    // Get a poster (or specific) frame thumbnail URI for a shot 
    //
    // Arguments:
    //    'shot_if' (Shot): Shot interface object
    //    'options' (object): Stucture containing optional settings used to control the type of thumbnail image rendered.
    //        'DCSpace' (string): Display colourspace (sRGB or P3) [Optional]
    //        'Graded' (number): Graded/ungraded flag [Optional]
    //        'HiRes' (string): Flag indicating hi-res image preferable [Optional]
    //        'ShotFrame' (number): Optional timeline frame number (constrained to shot range) [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (string): Thumbnail URI
    //
    get_poster_uri(shot_if, options)
    {
        return this.conn.call(
            null,
            "ThumbnailManager.get_poster_uri",
            {
                'shot_if': shot_if,
                'options': options,
            }
        );
    }

    // ThumbnailManager.get_scrub_uri_template
    //
    // Get a scrub image URI template (prefix & suffix strings). This can be used while scrubbing to generate image URIs without additional roundtrips/calls to the server. 
    //
    // Arguments:
    //    'scene_if' (Scene): Scene interface object
    //    'shot_id' (Shot): ID of shot in scene
    //    'options' (object): Stucture containing optional settings used to control the type of scrub image rendered.
    //        'DCSpace' (string): Display colourspace (sRGB or P3) [Optional]
    //        'Graded' (number): Graded/ungraded flag [Optional]
    //        'HiRes' (string): Flag indicating hi-res image preferable [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Template array containing 2 strings; a URI prefix & suffix. To form a completeURI, the scrub frame number required should be inserted between these 2 strings.
    //        '<n>' (string): 
    //
    get_scrub_uri_template(scene_if, shot_id, options)
    {
        return this.conn.call(
            null,
            "ThumbnailManager.get_scrub_uri_template",
            {
                'scene_if': scene_if,
                'shot_id': shot_id,
                'options': options,
            }
        );
    }

};
library.register_class( 'ThumbnailManager', ThumbnailManager )
module.exports.ThumbnailManager = ThumbnailManager;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Timer
//
// A Timer allows your script to be triggered periodically to perform processing
//

var Timer = class Timer extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Timer", "_id": this.target };
    }

    // Timer.create
    //
    // Create a new Timer object 
    //
    // Arguments:
    //    'interval' (number): Number of milliseconds between timer ticks firing
    //    'repeat' (number): Flag indicating whether timer should repeat after interval elapses [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (Timer): 
    //
    create(interval, repeat = 1)
    {
        return this.conn.call(
            null,
            "Timer.create",
            {
                'interval': interval,
                'repeat': repeat,
            }
        );
    }

    // Timer.start
    //
    // Start timer running 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    start()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Timer.start",
            {
            }
        );
    }

    // Timer.is_started
    //
    // Inquire if timer is started 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Flag indicating whether timer is started
    //
    is_started()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Timer.is_started",
            {
            }
        );
    }

    // Timer.stop
    //
    // Stop timer firing 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    stop()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Timer.stop",
            {
            }
        );
    }

    // Timer.get_interval
    //
    // Return interval between timer ticks firing 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (number): Interval in milliseconds
    //
    get_interval()
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Timer.get_interval",
            {
            }
        );
    }

    // Timer.set_interval
    //
    // Set interval between timer ticks firing 
    //
    // Arguments:
    //    'interval' (number): Interval in milliseconds
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_interval(interval)
    {
        if( this.target == null )
            throw "Instance method called on object with no instance";
        return this.conn.call(
            this.target,
            "Timer.set_interval",
            {
                'interval': interval,
            }
        );
    }

};
library.register_class( 'Timer', Timer )
module.exports.Timer = Timer;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Utilities
//
// Utility functions
//

var Utilities = class Utilities extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Utilities", "_id": this.target };
    }

    // Utilities.timecode_from_string
    //
    // Convert string to Timecode 
    //
    // Arguments:
    //    'str' (string): Timecode in string form
    //    'fps' (number): FPS [Optional]
    //    'wraphour' (number): Hour at which timecode is considered to wrap around, defaults to 24. Set this to 0 to disable timecode wrapping. [Optional]
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (timecode): Timecode parsed from string
    //
    timecode_from_string(str, fps = null, wraphour = 24)
    {
        return this.conn.call(
            null,
            "Utilities.timecode_from_string",
            {
                'str': str,
                'fps': fps,
                'wraphour': wraphour,
            }
        );
    }

    // Utilities.get_allowed_enum_values
    //
    // Returns an array of EnumInfo objects representing the allowed 
    // values for a given enumeration type.  Explictly, each returned entry 
    // has two fields: 
    // * Value - The (unique) internal value. 
    // * Desc - The user-friendly description for the value 
    // (so that you would typically present Desc to the user 
    // and use Value in calls to FLAPI functions). 
    //
    // Arguments:
    //    'enumType' (string): The name of the enumerated type.  e.g. CUBEEXPORT_LUTFORMAT
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of EnumInfo objects
    //        '<n>' (EnumInfo): 
    //
    get_allowed_enum_values(enumType)
    {
        return this.conn.call(
            null,
            "Utilities.get_allowed_enum_values",
            {
                'enumType': enumType,
            }
        );
    }

};
library.register_class( 'Utilities', Utilities )
module.exports.Utilities = Utilities;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Volumes
//
// Query and configure storage for this system
//

var Volumes = class Volumes extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "Volumes", "_id": this.target };
    }

    // Volumes.get_volume_keys
    //
    // Return keys for volumes accessible from this system 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of volume keys
    //        '<n>' (string): Key
    //
    get_volume_keys()
    {
        return this.conn.call(
            null,
            "Volumes.get_volume_keys",
            {
            }
        );
    }

    // Volumes.get_local_volume_keys
    //
    // Return volumes defined locally on this system 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of volume keys
    //        '<n>' (string): Key
    //
    get_local_volume_keys()
    {
        return this.conn.call(
            null,
            "Volumes.get_local_volume_keys",
            {
            }
        );
    }

    // Volumes.get_volume_info
    //
    // Return VolumeInfo describing the volume with the given key 
    //
    // Arguments:
    //    'keys' (array): Array of volume keys
    //        '<n>' (string): Key identifying volume
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (VolumeInfo): 
    //
    get_volume_info(keys)
    {
        return this.conn.call(
            null,
            "Volumes.get_volume_info",
            {
                'keys': keys,
            }
        );
    }

};
library.register_class( 'Volumes', Volumes )
module.exports.Volumes = Volumes;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// WebConfig
//
// WebConfig interface used by Web Management UI to configure users/passwords for web interface access
//

var WebConfig = class WebConfig extends Interface {

    constructor( conn, target )
    {
        super( conn, target );
    }

    toJSON()
    {
        return { "_handle": "WebConfig", "_id": this.target };
    }

    // WebConfig.get_permissions
    //
    // Return list of available permissions 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of permission definitions
    //        '<n>' (APIPermissionInfo): 
    //
    get_permissions()
    {
        return this.conn.call(
            null,
            "WebConfig.get_permissions",
            {
            }
        );
    }

    // WebConfig.get_users
    //
    // Return list of web users 
    //
    // Arguments:
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (array): Array of users
    //        '<n>' (APIUserInfo): 
    //
    get_users()
    {
        return this.conn.call(
            null,
            "WebConfig.get_users",
            {
            }
        );
    }

    // WebConfig.add_user
    //
    // Add new user 
    //
    // Arguments:
    //    'info' (APIUserInfo): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    add_user(info)
    {
        return this.conn.call(
            null,
            "WebConfig.add_user",
            {
                'info': info,
            }
        );
    }

    // WebConfig.update_user
    //
    // Update user config 
    //
    // Arguments:
    //    'name' (string): User login name
    //    'info' (APIUserInfo): 
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    update_user(name, info)
    {
        return this.conn.call(
            null,
            "WebConfig.update_user",
            {
                'name': name,
                'info': info,
            }
        );
    }

    // WebConfig.delete_user
    //
    // Delete user 
    //
    // Arguments:
    //    'name' (string): User login name
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    delete_user(name)
    {
        return this.conn.call(
            null,
            "WebConfig.delete_user",
            {
                'name': name,
            }
        );
    }

    // WebConfig.set_password
    //
    // Set user password 
    //
    // Arguments:
    //    'name' (string): User login name
    //    'password' (string): New password
    //
    // Result:
    //    Promise, which is resolved when the method call completes.
    //    Result type:
    //    (none)
    //
    set_password(name, password)
    {
        return this.conn.call(
            null,
            "WebConfig.set_password",
            {
                'name': name,
                'password': password,
            }
        );
    }

};
library.register_class( 'WebConfig', WebConfig )
module.exports.WebConfig = WebConfig;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// APIPermissionInfo
//
// Definition of an API permission
//

var APIPermissionInfo = class APIPermissionInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Label = obj.Label;
             this.Desc = obj.Desc;
        }
        else
        {
             this.Key = null;
             this.Label = null;
             this.Desc = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "APIPermissionInfo",
            "Key": this.Key,
            "Label": this.Label,
            "Desc": this.Desc,
        }
    }

}
library.register_value_type( 'APIPermissionInfo', APIPermissionInfo )
module.exports.APIPermissionInfo = APIPermissionInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// APIUserInfo
//
// Settings for an API user
//

var APIUserInfo = class APIUserInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Login = obj.Login;
             this.Name = obj.Name;
             this.Permissions = obj.Permissions;
             this.Enabled = obj.Enabled;
        }
        else
        {
             this.Login = null;
             this.Name = null;
             this.Permissions = null;
             this.Enabled = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "APIUserInfo",
            "Login": this.Login,
            "Name": this.Name,
            "Permissions": this.Permissions,
            "Enabled": this.Enabled,
        }
    }

}
library.register_value_type( 'APIUserInfo', APIUserInfo )
module.exports.APIUserInfo = APIUserInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// AudioSequenceSettings
//
// Settings defining the behaviour of an Audio Sequence
//

var AudioSequenceSettings = class AudioSequenceSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Type = obj.Type;
             this.Filename = obj.Filename;
             this.Stems = obj.Stems;
             this.Offset = obj.Offset;
             this.Ratio = obj.Ratio;
        }
        else
        {
             this.Type = null;
             this.Filename = null;
             this.Stems = null;
             this.Offset = null;
             this.Ratio = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "AudioSequenceSettings",
            "Type": this.Type,
            "Filename": this.Filename,
            "Stems": this.Stems,
            "Offset": this.Offset,
            "Ratio": this.Ratio,
        }
    }

}
library.register_value_type( 'AudioSequenceSettings', AudioSequenceSettings )
module.exports.AudioSequenceSettings = AudioSequenceSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// AudioSyncProgress
//
// Progress information from audio sync operation
//

var AudioSyncProgress = class AudioSyncProgress {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Status = obj.Status;
             this.Summary = obj.Summary;
             this.ShotID = obj.ShotID;
             this.Frame = obj.Frame;
        }
        else
        {
             this.Status = null;
             this.Summary = null;
             this.ShotID = null;
             this.Frame = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "AudioSyncProgress",
            "Status": this.Status,
            "Summary": this.Summary,
            "ShotID": this.ShotID,
            "Frame": this.Frame,
        }
    }

}
library.register_value_type( 'AudioSyncProgress', AudioSyncProgress )
module.exports.AudioSyncProgress = AudioSyncProgress;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// AudioSyncSettings
//
// Settings to use for AudioSync operation
//

var AudioSyncSettings = class AudioSyncSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Criteria = obj.Criteria;
             this.Timecode = obj.Timecode;
             this.Scene = obj.Scene;
             this.Take = obj.Take;
             this.Directory = obj.Directory;
             this.SubSearch = obj.SubSearch;
             this.Subdirs = obj.Subdirs;
             this.FPS = obj.FPS;
             this.Offset = obj.Offset;
             this.Metadata = obj.Metadata;
             this.ClapDetect = obj.ClapDetect;
             this.ClapDetectThreshold = obj.ClapDetectThreshold;
             this.Ratio = obj.Ratio;
             this.ReadLTC = obj.ReadLTC;
             this.LTCIndex = obj.LTCIndex;
             this.LTCColumn = obj.LTCColumn;
             this.AutoSync = obj.AutoSync;
        }
        else
        {
             this.Criteria = null;
             this.Timecode = null;
             this.Scene = null;
             this.Take = null;
             this.Directory = null;
             this.SubSearch = null;
             this.Subdirs = null;
             this.FPS = null;
             this.Offset = null;
             this.Metadata = null;
             this.ClapDetect = null;
             this.ClapDetectThreshold = null;
             this.Ratio = null;
             this.ReadLTC = null;
             this.LTCIndex = null;
             this.LTCColumn = null;
             this.AutoSync = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "AudioSyncSettings",
            "Criteria": this.Criteria,
            "Timecode": this.Timecode,
            "Scene": this.Scene,
            "Take": this.Take,
            "Directory": this.Directory,
            "SubSearch": this.SubSearch,
            "Subdirs": this.Subdirs,
            "FPS": this.FPS,
            "Offset": this.Offset,
            "Metadata": this.Metadata,
            "ClapDetect": this.ClapDetect,
            "ClapDetectThreshold": this.ClapDetectThreshold,
            "Ratio": this.Ratio,
            "ReadLTC": this.ReadLTC,
            "LTCIndex": this.LTCIndex,
            "LTCColumn": this.LTCColumn,
            "AutoSync": this.AutoSync,
        }
    }

}
library.register_value_type( 'AudioSyncSettings', AudioSyncSettings )
module.exports.AudioSyncSettings = AudioSyncSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// BLGExportSettings
//
// Settings to use for BLG exports
//

var BLGExportSettings = class BLGExportSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Source = obj.Source;
             this.Filter = obj.Filter;
             this.Category = obj.Category;
             this.CategoryMatch = obj.CategoryMatch;
             this.Frames = obj.Frames;
             this.MarkCategory = obj.MarkCategory;
             this.Stereo = obj.Stereo;
             this.Directory = obj.Directory;
             this.Overwrite = obj.Overwrite;
             this.Path = obj.Path;
             this.Template = obj.Template;
             this.Scale = obj.Scale;
             this.AllowMultiInput = obj.AllowMultiInput;
             this.GenerateNukeScripts = obj.GenerateNukeScripts;
             this.GenerateWriteNode = obj.GenerateWriteNode;
             this.Keyframes = obj.Keyframes;
             this.LockGrade = obj.LockGrade;
             this.ViewingColourSpace = obj.ViewingColourSpace;
             this.ViewingFormat = obj.ViewingFormat;
        }
        else
        {
             this.Source = null;
             this.Filter = null;
             this.Category = null;
             this.CategoryMatch = null;
             this.Frames = null;
             this.MarkCategory = null;
             this.Stereo = null;
             this.Directory = null;
             this.Overwrite = null;
             this.Path = null;
             this.Template = null;
             this.Scale = null;
             this.AllowMultiInput = null;
             this.GenerateNukeScripts = null;
             this.GenerateWriteNode = null;
             this.Keyframes = null;
             this.LockGrade = null;
             this.ViewingColourSpace = null;
             this.ViewingFormat = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "BLGExportSettings",
            "Source": this.Source,
            "Filter": this.Filter,
            "Category": this.Category,
            "CategoryMatch": this.CategoryMatch,
            "Frames": this.Frames,
            "MarkCategory": this.MarkCategory,
            "Stereo": this.Stereo,
            "Directory": this.Directory,
            "Overwrite": this.Overwrite,
            "Path": this.Path,
            "Template": this.Template,
            "Scale": this.Scale,
            "AllowMultiInput": this.AllowMultiInput,
            "GenerateNukeScripts": this.GenerateNukeScripts,
            "GenerateWriteNode": this.GenerateWriteNode,
            "Keyframes": this.Keyframes,
            "LockGrade": this.LockGrade,
            "ViewingColourSpace": this.ViewingColourSpace,
            "ViewingFormat": this.ViewingFormat,
        }
    }

}
library.register_value_type( 'BLGExportSettings', BLGExportSettings )
module.exports.BLGExportSettings = BLGExportSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// CDLExportSettings
//
// Settings to use for CDL exports
//

var CDLExportSettings = class CDLExportSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Source = obj.Source;
             this.Filter = obj.Filter;
             this.Category = obj.Category;
             this.CategoryMatch = obj.CategoryMatch;
             this.Frames = obj.Frames;
             this.MarkCategory = obj.MarkCategory;
             this.Stereo = obj.Stereo;
             this.Directory = obj.Directory;
             this.Overwrite = obj.Overwrite;
             this.Format = obj.Format;
             this.PathExample = obj.PathExample;
             this.Template = obj.Template;
             this.LookNameExample = obj.LookNameExample;
             this.LookName = obj.LookName;
             this.CDLLayer = obj.CDLLayer;
             this.CDLLayerCustom = obj.CDLLayerCustom;
        }
        else
        {
             this.Source = null;
             this.Filter = null;
             this.Category = null;
             this.CategoryMatch = null;
             this.Frames = null;
             this.MarkCategory = null;
             this.Stereo = null;
             this.Directory = null;
             this.Overwrite = null;
             this.Format = null;
             this.PathExample = null;
             this.Template = null;
             this.LookNameExample = null;
             this.LookName = null;
             this.CDLLayer = null;
             this.CDLLayerCustom = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "CDLExportSettings",
            "Source": this.Source,
            "Filter": this.Filter,
            "Category": this.Category,
            "CategoryMatch": this.CategoryMatch,
            "Frames": this.Frames,
            "MarkCategory": this.MarkCategory,
            "Stereo": this.Stereo,
            "Directory": this.Directory,
            "Overwrite": this.Overwrite,
            "Format": this.Format,
            "PathExample": this.PathExample,
            "Template": this.Template,
            "LookNameExample": this.LookNameExample,
            "LookName": this.LookName,
            "CDLLayer": this.CDLLayer,
            "CDLLayerCustom": this.CDLLayerCustom,
        }
    }

}
library.register_value_type( 'CDLExportSettings', CDLExportSettings )
module.exports.CDLExportSettings = CDLExportSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// CategoryInfo
//
// Definition of a Category used to annotate marks, shots or strips
//

var CategoryInfo = class CategoryInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
             this.ReadOnly = obj.ReadOnly;
             this.Colour = obj.Colour;
        }
        else
        {
             this.Key = null;
             this.Name = null;
             this.ReadOnly = null;
             this.Colour = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "CategoryInfo",
            "Key": this.Key,
            "Name": this.Name,
            "ReadOnly": this.ReadOnly,
            "Colour": this.Colour,
        }
    }

}
library.register_value_type( 'CategoryInfo', CategoryInfo )
module.exports.CategoryInfo = CategoryInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ClientViewClientSettings
//
// Settings for a connected Client View
//

var ClientViewClientSettings = class ClientViewClientSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.StreamIndex = obj.StreamIndex;
             this.StreamConfigsAge = obj.StreamConfigsAge;
             this.NotesEnabled = obj.NotesEnabled;
             this.LaserEnabled = obj.LaserEnabled;
             this.Debug = obj.Debug;
        }
        else
        {
             this.StreamIndex = null;
             this.StreamConfigsAge = null;
             this.NotesEnabled = null;
             this.LaserEnabled = null;
             this.Debug = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ClientViewClientSettings",
            "StreamIndex": this.StreamIndex,
            "StreamConfigsAge": this.StreamConfigsAge,
            "NotesEnabled": this.NotesEnabled,
            "LaserEnabled": this.LaserEnabled,
            "Debug": this.Debug,
        }
    }

}
library.register_value_type( 'ClientViewClientSettings', ClientViewClientSettings )
module.exports.ClientViewClientSettings = ClientViewClientSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ClientViewHostUserSettings
//
// Settings for user hosting the Client View
//

var ClientViewHostUserSettings = class ClientViewHostUserSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.UserName = obj.UserName;
             this.LaserColour = obj.LaserColour;
        }
        else
        {
             this.UserName = null;
             this.LaserColour = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ClientViewHostUserSettings",
            "UserName": this.UserName,
            "LaserColour": this.LaserColour,
        }
    }

}
library.register_value_type( 'ClientViewHostUserSettings', ClientViewHostUserSettings )
module.exports.ClientViewHostUserSettings = ClientViewHostUserSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ClientViewStreamSettings
//
// Settings for a Client View stream
//

var ClientViewStreamSettings = class ClientViewStreamSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Resolution = obj.Resolution;
             this.Bitrate = obj.Bitrate;
             this.ColourSpace = obj.ColourSpace;
        }
        else
        {
             this.Resolution = null;
             this.Bitrate = null;
             this.ColourSpace = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ClientViewStreamSettings",
            "Resolution": this.Resolution,
            "Bitrate": this.Bitrate,
            "ColourSpace": this.ColourSpace,
        }
    }

}
library.register_value_type( 'ClientViewStreamSettings', ClientViewStreamSettings )
module.exports.ClientViewStreamSettings = ClientViewStreamSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ColourSpaceInfo
//
// Description of a Truelight Colour Space
//

var ColourSpaceInfo = class ColourSpaceInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.DisplayName = obj.DisplayName;
             this.Type = obj.Type;
        }
        else
        {
             this.Name = null;
             this.DisplayName = null;
             this.Type = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ColourSpaceInfo",
            "Name": this.Name,
            "DisplayName": this.DisplayName,
            "Type": this.Type,
        }
    }

}
library.register_value_type( 'ColourSpaceInfo', ColourSpaceInfo )
module.exports.ColourSpaceInfo = ColourSpaceInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ConnectionInfo
//
// Dictionary describing a single connection.
//

var ConnectionInfo = class ConnectionInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ConnectionID = obj.ConnectionID;
             this.UserName = obj.UserName;
             this.UsageType = obj.UsageType;
        }
        else
        {
             this.ConnectionID = null;
             this.UserName = null;
             this.UsageType = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ConnectionInfo",
            "ConnectionID": this.ConnectionID,
            "UserName": this.UserName,
            "UsageType": this.UsageType,
        }
    }

}
library.register_value_type( 'ConnectionInfo', ConnectionInfo )
module.exports.ConnectionInfo = ConnectionInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// CubeExportSettings
//
// Settings to use for Cube exports
//

var CubeExportSettings = class CubeExportSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Source = obj.Source;
             this.Filter = obj.Filter;
             this.Category = obj.Category;
             this.CategoryMatch = obj.CategoryMatch;
             this.Frames = obj.Frames;
             this.MarkCategory = obj.MarkCategory;
             this.Stereo = obj.Stereo;
             this.Directory = obj.Directory;
             this.Overwrite = obj.Overwrite;
             this.NumLUTs = obj.NumLUTs;
             this.LUT1Options = obj.LUT1Options;
             this.LUT1Path = obj.LUT1Path;
             this.LUT1Name = obj.LUT1Name;
             this.LUT2Options = obj.LUT2Options;
             this.LUT2Path = obj.LUT2Path;
             this.LUT2Name = obj.LUT2Name;
             this.LUT3Options = obj.LUT3Options;
             this.LUT3Path = obj.LUT3Path;
             this.LUT3Name = obj.LUT3Name;
             this.InputColourSpace = obj.InputColourSpace;
             this.InputDRT = obj.InputDRT;
             this.LUTFormat = obj.LUTFormat;
             this.ExtendedRanges = obj.ExtendedRanges;
             this.InputMin = obj.InputMin;
             this.InputMaxLog = obj.InputMaxLog;
             this.InputMaxLin = obj.InputMaxLin;
             this.InputLogOffset = obj.InputLogOffset;
             this.OutputColourSpace = obj.OutputColourSpace;
             this.CubeResolution = obj.CubeResolution;
             this.LUTResolution = obj.LUTResolution;
             this.GradeReplace = obj.GradeReplace;
        }
        else
        {
             this.Source = null;
             this.Filter = null;
             this.Category = null;
             this.CategoryMatch = null;
             this.Frames = null;
             this.MarkCategory = null;
             this.Stereo = null;
             this.Directory = null;
             this.Overwrite = null;
             this.NumLUTs = null;
             this.LUT1Options = null;
             this.LUT1Path = null;
             this.LUT1Name = null;
             this.LUT2Options = null;
             this.LUT2Path = null;
             this.LUT2Name = null;
             this.LUT3Options = null;
             this.LUT3Path = null;
             this.LUT3Name = null;
             this.InputColourSpace = null;
             this.InputDRT = null;
             this.LUTFormat = null;
             this.ExtendedRanges = null;
             this.InputMin = null;
             this.InputMaxLog = null;
             this.InputMaxLin = null;
             this.InputLogOffset = null;
             this.OutputColourSpace = null;
             this.CubeResolution = null;
             this.LUTResolution = null;
             this.GradeReplace = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "CubeExportSettings",
            "Source": this.Source,
            "Filter": this.Filter,
            "Category": this.Category,
            "CategoryMatch": this.CategoryMatch,
            "Frames": this.Frames,
            "MarkCategory": this.MarkCategory,
            "Stereo": this.Stereo,
            "Directory": this.Directory,
            "Overwrite": this.Overwrite,
            "NumLUTs": this.NumLUTs,
            "LUT1Options": this.LUT1Options,
            "LUT1Path": this.LUT1Path,
            "LUT1Name": this.LUT1Name,
            "LUT2Options": this.LUT2Options,
            "LUT2Path": this.LUT2Path,
            "LUT2Name": this.LUT2Name,
            "LUT3Options": this.LUT3Options,
            "LUT3Path": this.LUT3Path,
            "LUT3Name": this.LUT3Name,
            "InputColourSpace": this.InputColourSpace,
            "InputDRT": this.InputDRT,
            "LUTFormat": this.LUTFormat,
            "ExtendedRanges": this.ExtendedRanges,
            "InputMin": this.InputMin,
            "InputMaxLog": this.InputMaxLog,
            "InputMaxLin": this.InputMaxLin,
            "InputLogOffset": this.InputLogOffset,
            "OutputColourSpace": this.OutputColourSpace,
            "CubeResolution": this.CubeResolution,
            "LUTResolution": this.LUTResolution,
            "GradeReplace": this.GradeReplace,
        }
    }

}
library.register_value_type( 'CubeExportSettings', CubeExportSettings )
module.exports.CubeExportSettings = CubeExportSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// CustomerInfo
//
// Dictionary containing customer related settings/preferences.
//

var CustomerInfo = class CustomerInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.LogoURI = obj.LogoURI;
             this.WebsiteURL = obj.WebsiteURL;
        }
        else
        {
             this.Name = null;
             this.LogoURI = null;
             this.WebsiteURL = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "CustomerInfo",
            "Name": this.Name,
            "LogoURI": this.LogoURI,
            "WebsiteURL": this.WebsiteURL,
        }
    }

}
library.register_value_type( 'CustomerInfo', CustomerInfo )
module.exports.CustomerInfo = CustomerInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DRTInfo
//
// Description of a Truelight Display Rendering Transform
//

var DRTInfo = class DRTInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.InputSpace = obj.InputSpace;
             this.OutputSpace = obj.OutputSpace;
             this.ViewingConditions = obj.ViewingConditions;
        }
        else
        {
             this.Name = null;
             this.InputSpace = null;
             this.OutputSpace = null;
             this.ViewingConditions = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DRTInfo",
            "Name": this.Name,
            "InputSpace": this.InputSpace,
            "OutputSpace": this.OutputSpace,
            "ViewingConditions": this.ViewingConditions,
        }
    }

}
library.register_value_type( 'DRTInfo', DRTInfo )
module.exports.DRTInfo = DRTInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DecodeParameterChoice
//
//

var DecodeParameterChoice = class DecodeParameterChoice {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Value = obj.Value;
             this.Label = obj.Label;
        }
        else
        {
             this.Value = null;
             this.Label = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DecodeParameterChoice",
            "Value": this.Value,
            "Label": this.Label,
        }
    }

}
library.register_value_type( 'DecodeParameterChoice', DecodeParameterChoice )
module.exports.DecodeParameterChoice = DecodeParameterChoice;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DecodeParameterDefinition
//
// This type is returned by get_decode_parameter_definitions to define the data type, label, ranges and values for each decode parameter that can be get or set for a Shot.
//

var DecodeParameterDefinition = class DecodeParameterDefinition {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Parameter = obj.Parameter;
             this.Type = obj.Type;
             this.Default = obj.Default;
             this.Label = obj.Label;
             this.Min = obj.Min;
             this.Max = obj.Max;
             this.Choices = obj.Choices;
        }
        else
        {
             this.Parameter = null;
             this.Type = null;
             this.Default = null;
             this.Label = null;
             this.Min = null;
             this.Max = null;
             this.Choices = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DecodeParameterDefinition",
            "Parameter": this.Parameter,
            "Type": this.Type,
            "Default": this.Default,
            "Label": this.Label,
            "Min": this.Min,
            "Max": this.Max,
            "Choices": this.Choices,
        }
    }

}
library.register_value_type( 'DecodeParameterDefinition', DecodeParameterDefinition )
module.exports.DecodeParameterDefinition = DecodeParameterDefinition;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DiagHostResult
//
// Result information for diagnostic tests run on a specific host
//

var DiagHostResult = class DiagHostResult {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Host = obj.Host;
             this.Messages = obj.Messages;
             this.Status = obj.Status;
        }
        else
        {
             this.Host = null;
             this.Messages = null;
             this.Status = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DiagHostResult",
            "Host": this.Host,
            "Messages": this.Messages,
            "Status": this.Status,
        }
    }

}
library.register_value_type( 'DiagHostResult', DiagHostResult )
module.exports.DiagHostResult = DiagHostResult;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DiagInfo
//
// Information about a particular diagnostic test
//

var DiagInfo = class DiagInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
             this.Group = obj.Group;
             this.Hosts = obj.Hosts;
             this.Weight = obj.Weight;
        }
        else
        {
             this.Key = null;
             this.Name = null;
             this.Group = null;
             this.Hosts = null;
             this.Weight = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DiagInfo",
            "Key": this.Key,
            "Name": this.Name,
            "Group": this.Group,
            "Hosts": this.Hosts,
            "Weight": this.Weight,
        }
    }

}
library.register_value_type( 'DiagInfo', DiagInfo )
module.exports.DiagInfo = DiagInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DiagProgress
//
// Overall process of diagnostic test operation
//

var DiagProgress = class DiagProgress {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Running = obj.Running;
             this.Total = obj.Total;
             this.NumComplete = obj.NumComplete;
             this.NumInProgress = obj.NumInProgress;
             this.NumWaiting = obj.NumWaiting;
             this.NumSkipped = obj.NumSkipped;
        }
        else
        {
             this.Running = null;
             this.Total = null;
             this.NumComplete = null;
             this.NumInProgress = null;
             this.NumWaiting = null;
             this.NumSkipped = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DiagProgress",
            "Running": this.Running,
            "Total": this.Total,
            "NumComplete": this.NumComplete,
            "NumInProgress": this.NumInProgress,
            "NumWaiting": this.NumWaiting,
            "NumSkipped": this.NumSkipped,
        }
    }

}
library.register_value_type( 'DiagProgress', DiagProgress )
module.exports.DiagProgress = DiagProgress;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DiagResult
//
// Result information for an individual diagnostic test across all hosts running this test
//

var DiagResult = class DiagResult {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.Hosts = obj.Hosts;
        }
        else
        {
             this.Name = null;
             this.Hosts = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "DiagResult",
            "Name": this.Name,
            "Hosts": this.Hosts,
        }
    }

}
library.register_value_type( 'DiagResult', DiagResult )
module.exports.DiagResult = DiagResult;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// DialogItem
//
// Definition of an item to be shown in a DynamicDialog
//

var DialogItem = class DialogItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Label = obj.Label;
             this.Type = obj.Type;
             this.Help = obj.Help;
             this.Default = obj.Default;
             this.Options = obj.Options;
             this.RegExp = obj.RegExp;
             this.Password = obj.Password;
             this.IntMin = obj.IntMin;
             this.IntMax = obj.IntMax;
             this.FloatMin = obj.FloatMin;
             this.FloatMax = obj.FloatMax;
             this.FloatSnap = obj.FloatSnap;
             this.Style = obj.Style;
             this.Height = obj.Height;
        }
        else
        {
             this.Key = null;
             this.Label = null;
             this.Type = null;
             this.Help = null;
             this.Default = null;
             this.Options = null;
             this.RegExp = null;
             this.Password = null;
             this.IntMin = null;
             this.IntMax = null;
             this.FloatMin = null;
             this.FloatMax = null;
             this.FloatSnap = null;
             this.Style = null;
             this.Height = 0;
        }
    }

    toJSON()
    {
        return {
            "_type": "DialogItem",
            "Key": this.Key,
            "Label": this.Label,
            "Type": this.Type,
            "Help": this.Help,
            "Default": this.Default,
            "Options": this.Options,
            "RegExp": this.RegExp,
            "Password": this.Password,
            "IntMin": this.IntMin,
            "IntMax": this.IntMax,
            "FloatMin": this.FloatMin,
            "FloatMax": this.FloatMax,
            "FloatSnap": this.FloatSnap,
            "Style": this.Style,
            "Height": this.Height,
        }
    }

}
library.register_value_type( 'DialogItem', DialogItem )
module.exports.DialogItem = DialogItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// EnumInfo
//
// Information about a defined enumerated value
//

var EnumInfo = class EnumInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Value = obj.Value;
             this.Desc = obj.Desc;
        }
        else
        {
             this.Value = null;
             this.Desc = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "EnumInfo",
            "Value": this.Value,
            "Desc": this.Desc,
        }
    }

}
library.register_value_type( 'EnumInfo', EnumInfo )
module.exports.EnumInfo = EnumInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ExportOpInfo
//
// This type is returned to return information about export operations queued via QueueManager
//

var ExportOpInfo = class ExportOpInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ID = obj.ID;
             this.Log = obj.Log;
        }
        else
        {
             this.ID = null;
             this.Log = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ExportOpInfo",
            "ID": this.ID,
            "Log": this.Log,
        }
    }

}
library.register_value_type( 'ExportOpInfo', ExportOpInfo )
module.exports.ExportOpInfo = ExportOpInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ExportProgress
//
// Progress information from Export operation
//

var ExportProgress = class ExportProgress {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Status = obj.Status;
             this.Summary = obj.Summary;
             this.ShotID = obj.ShotID;
             this.Frame = obj.Frame;
        }
        else
        {
             this.Status = null;
             this.Summary = null;
             this.ShotID = null;
             this.Frame = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ExportProgress",
            "Status": this.Status,
            "Summary": this.Summary,
            "ShotID": this.ShotID,
            "Frame": this.Frame,
        }
    }

}
library.register_value_type( 'ExportProgress', ExportProgress )
module.exports.ExportProgress = ExportProgress;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatBurninItem
//
// Definition of a text element within a FormatBurnin
//

var FormatBurninItem = class FormatBurninItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Type = obj.Type;
             this.X = obj.X;
             this.Y = obj.Y;
             this.XAlign = obj.XAlign;
             this.YAlign = obj.YAlign;
             this.Box = obj.Box;
             this.Height = obj.Height;
             this.Text = obj.Text;
             this.XScale = obj.XScale;
             this.YScale = obj.YScale;
             this.ResX = obj.ResX;
             this.ResY = obj.ResY;
             this.Opacity = obj.Opacity;
             this.File = obj.File;
        }
        else
        {
             this.Type = null;
             this.X = null;
             this.Y = null;
             this.XAlign = null;
             this.YAlign = null;
             this.Box = null;
             this.Height = null;
             this.Text = null;
             this.XScale = null;
             this.YScale = null;
             this.ResX = null;
             this.ResY = null;
             this.Opacity = null;
             this.File = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "FormatBurninItem",
            "Type": this.Type,
            "X": this.X,
            "Y": this.Y,
            "XAlign": this.XAlign,
            "YAlign": this.YAlign,
            "Box": this.Box,
            "Height": this.Height,
            "Text": this.Text,
            "XScale": this.XScale,
            "YScale": this.YScale,
            "ResX": this.ResX,
            "ResY": this.ResY,
            "Opacity": this.Opacity,
            "File": this.File,
        }
    }

}
library.register_value_type( 'FormatBurninItem', FormatBurninItem )
module.exports.FormatBurninItem = FormatBurninItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatInfo
//
// Specifies the width, height, pixel aspect ratio
//

var FormatInfo = class FormatInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Width = obj.Width;
             this.Height = obj.Height;
             this.PixelAspectRatio = obj.PixelAspectRatio;
        }
        else
        {
             this.Width = null;
             this.Height = null;
             this.PixelAspectRatio = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "FormatInfo",
            "Width": this.Width,
            "Height": this.Height,
            "PixelAspectRatio": this.PixelAspectRatio,
        }
    }

}
library.register_value_type( 'FormatInfo', FormatInfo )
module.exports.FormatInfo = FormatInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatMapping
//
// Defines the mapping from one Format to another Format
//

var FormatMapping = class FormatMapping {

    constructor( obj )
    {
        if( obj != null )
        {
             this.sx = obj.sx;
             this.sy = obj.sy;
             this.tx = obj.tx;
             this.ty = obj.ty;
             this.inside = obj.inside;
             this.src_mask = obj.src_mask;
             this.dst_mask = obj.dst_mask;
        }
        else
        {
             this.sx = null;
             this.sy = null;
             this.tx = null;
             this.ty = null;
             this.inside = null;
             this.src_mask = null;
             this.dst_mask = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "FormatMapping",
            "sx": this.sx,
            "sy": this.sy,
            "tx": this.tx,
            "ty": this.ty,
            "inside": this.inside,
            "src_mask": this.src_mask,
            "dst_mask": this.dst_mask,
        }
    }

}
library.register_value_type( 'FormatMapping', FormatMapping )
module.exports.FormatMapping = FormatMapping;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FormatMask
//
// Specifies the area of Mark defined with a Format
//

var FormatMask = class FormatMask {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.XMin = obj.XMin;
             this.XMax = obj.XMax;
             this.YMin = obj.YMin;
             this.YMax = obj.YMax;
        }
        else
        {
             this.Name = null;
             this.XMin = null;
             this.XMax = null;
             this.YMin = null;
             this.YMax = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "FormatMask",
            "Name": this.Name,
            "XMin": this.XMin,
            "XMax": this.XMax,
            "YMin": this.YMin,
            "YMax": this.YMax,
        }
    }

}
library.register_value_type( 'FormatMask', FormatMask )
module.exports.FormatMask = FormatMask;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// FrameRange
//
// Defines a range of frames
//

var FrameRange = class FrameRange {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Start = obj.Start;
             this.End = obj.End;
        }
        else
        {
             this.Start = null;
             this.End = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "FrameRange",
            "Start": this.Start,
            "End": this.End,
        }
    }

}
library.register_value_type( 'FrameRange', FrameRange )
module.exports.FrameRange = FrameRange;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// KeyTextItem
//
// A mapping for a key object to a user-readable string describing that key
//

var KeyTextItem = class KeyTextItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Text = obj.Text;
        }
        else
        {
             this.Key = null;
             this.Text = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "KeyTextItem",
            "Key": this.Key,
            "Text": this.Text,
        }
    }

}
library.register_value_type( 'KeyTextItem', KeyTextItem )
module.exports.KeyTextItem = KeyTextItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// LicenceItem
//
// Description of a installed licence option
//

var LicenceItem = class LicenceItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Product = obj.Product;
             this.Version = obj.Version;
             this.Options = obj.Options;
             this.Permanent = obj.Permanent;
             this.Start = obj.Start;
             this.Duration = obj.Duration;
             this.DaysLeft = obj.DaysLeft;
        }
        else
        {
             this.Product = null;
             this.Version = null;
             this.Options = null;
             this.Permanent = null;
             this.Start = null;
             this.Duration = null;
             this.DaysLeft = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "LicenceItem",
            "Product": this.Product,
            "Version": this.Version,
            "Options": this.Options,
            "Permanent": this.Permanent,
            "Start": this.Start,
            "Duration": this.Duration,
            "DaysLeft": this.DaysLeft,
        }
    }

}
library.register_value_type( 'LicenceItem', LicenceItem )
module.exports.LicenceItem = LicenceItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// LookInfo
//
// Information for a Look
//

var LookInfo = class LookInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.Group = obj.Group;
        }
        else
        {
             this.Name = null;
             this.Group = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "LookInfo",
            "Name": this.Name,
            "Group": this.Group,
        }
    }

}
library.register_value_type( 'LookInfo', LookInfo )
module.exports.LookInfo = LookInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MetadataItem
//
// Definition of a Metadata field that exists across all shots in a Scene
//

var MetadataItem = class MetadataItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
             this.Type = obj.Type;
             this.NumElements = obj.NumElements;
             this.IsReadOnly = obj.IsReadOnly;
             this.IsUserDefined = obj.IsUserDefined;
             this.Properties = obj.Properties;
        }
        else
        {
             this.Key = null;
             this.Name = null;
             this.Type = null;
             this.NumElements = null;
             this.IsReadOnly = null;
             this.IsUserDefined = null;
             this.Properties = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "MetadataItem",
            "Key": this.Key,
            "Name": this.Name,
            "Type": this.Type,
            "NumElements": this.NumElements,
            "IsReadOnly": this.IsReadOnly,
            "IsUserDefined": this.IsUserDefined,
            "Properties": this.Properties,
        }
    }

}
library.register_value_type( 'MetadataItem', MetadataItem )
module.exports.MetadataItem = MetadataItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MetadataProperty
//
// Definition of a Property that can specified for each MetadataItem defined in a Scene
//

var MetadataProperty = class MetadataProperty {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
        }
        else
        {
             this.Key = null;
             this.Name = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "MetadataProperty",
            "Key": this.Key,
            "Name": this.Name,
        }
    }

}
library.register_value_type( 'MetadataProperty', MetadataProperty )
module.exports.MetadataProperty = MetadataProperty;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MultiPasteProgress
//
// Progress information from Multi-Paste operation
//

var MultiPasteProgress = class MultiPasteProgress {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Status = obj.Status;
             this.Summary = obj.Summary;
             this.ShotID = obj.ShotID;
             this.Frame = obj.Frame;
        }
        else
        {
             this.Status = null;
             this.Summary = null;
             this.ShotID = null;
             this.Frame = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "MultiPasteProgress",
            "Status": this.Status,
            "Summary": this.Summary,
            "ShotID": this.ShotID,
            "Frame": this.Frame,
        }
    }

}
library.register_value_type( 'MultiPasteProgress', MultiPasteProgress )
module.exports.MultiPasteProgress = MultiPasteProgress;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// MultiPasteSettings
//
// Settings to use for MultiPaste operation
//

var MultiPasteSettings = class MultiPasteSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Source = obj.Source;
             this.SourceScenes = obj.SourceScenes;
             this.SourceDirectory = obj.SourceDirectory;
             this.SourceEDL = obj.SourceEDL;
             this.EDLApplyASCCDL = obj.EDLApplyASCCDL;
             this.ASCCDLLayerNumber = obj.ASCCDLLayerNumber;
             this.ASCCDLColour = obj.ASCCDLColour;
             this.ASCCDLCategories = obj.ASCCDLCategories;
             this.BLGResourceConflict = obj.BLGResourceConflict;
             this.DestSelection = obj.DestSelection;
             this.LUTDirectory = obj.LUTDirectory;
             this.LUTLayerNum = obj.LUTLayerNum;
             this.LUTLayerColour = obj.LUTLayerColour;
             this.LUTCategories = obj.LUTCategories;
             this.CDLDirectory = obj.CDLDirectory;
             this.CDLLayerNum = obj.CDLLayerNum;
             this.CDLLayerColour = obj.CDLLayerColour;
             this.CDLCategories = obj.CDLCategories;
             this.MatchBy = obj.MatchBy;
             this.MatchQuality = obj.MatchQuality;
             this.PasteGrades = obj.PasteGrades;
             this.LayerZeroBehaviour = obj.LayerZeroBehaviour;
             this.LayerZeroOverwrite = obj.LayerZeroOverwrite;
             this.LayerZeroAudio = obj.LayerZeroAudio;
             this.InputColourSpace = obj.InputColourSpace;
             this.SourceShots = obj.SourceShots;
             this.SourceShotCategories = obj.SourceShotCategories;
             this.DestShots = obj.DestShots;
             this.DestShotCategories = obj.DestShotCategories;
             this.DetectGradeChanges = obj.DetectGradeChanges;
             this.GradeChangedCategory = obj.GradeChangedCategory;
             this.ClearUnchangedGrades = obj.ClearUnchangedGrades;
             this.PasteLocation = obj.PasteLocation;
             this.LayerZeroCategories = obj.LayerZeroCategories;
             this.LayerZeroExcludeCategories = obj.LayerZeroExcludeCategories;
             this.PasteMetadata = obj.PasteMetadata;
             this.MetadataColumns = obj.MetadataColumns;
             this.AddExtraMetadata = obj.AddExtraMetadata;
             this.OverwriteMetadata = obj.OverwriteMetadata;
             this.PasteGroups = obj.PasteGroups;
             this.ShredComps = obj.ShredComps;
             this.ShredProtectCategories = obj.ShredProtectCategories;
             this.ShredExternalMattes = obj.ShredExternalMattes;
        }
        else
        {
             this.Source = null;
             this.SourceScenes = null;
             this.SourceDirectory = null;
             this.SourceEDL = null;
             this.EDLApplyASCCDL = null;
             this.ASCCDLLayerNumber = null;
             this.ASCCDLColour = null;
             this.ASCCDLCategories = null;
             this.BLGResourceConflict = null;
             this.DestSelection = null;
             this.LUTDirectory = null;
             this.LUTLayerNum = null;
             this.LUTLayerColour = null;
             this.LUTCategories = null;
             this.CDLDirectory = null;
             this.CDLLayerNum = null;
             this.CDLLayerColour = null;
             this.CDLCategories = null;
             this.MatchBy = null;
             this.MatchQuality = null;
             this.PasteGrades = null;
             this.LayerZeroBehaviour = null;
             this.LayerZeroOverwrite = null;
             this.LayerZeroAudio = null;
             this.InputColourSpace = null;
             this.SourceShots = null;
             this.SourceShotCategories = null;
             this.DestShots = null;
             this.DestShotCategories = null;
             this.DetectGradeChanges = null;
             this.GradeChangedCategory = null;
             this.ClearUnchangedGrades = null;
             this.PasteLocation = null;
             this.LayerZeroCategories = null;
             this.LayerZeroExcludeCategories = null;
             this.PasteMetadata = null;
             this.MetadataColumns = null;
             this.AddExtraMetadata = null;
             this.OverwriteMetadata = null;
             this.PasteGroups = null;
             this.ShredComps = null;
             this.ShredProtectCategories = null;
             this.ShredExternalMattes = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "MultiPasteSettings",
            "Source": this.Source,
            "SourceScenes": this.SourceScenes,
            "SourceDirectory": this.SourceDirectory,
            "SourceEDL": this.SourceEDL,
            "EDLApplyASCCDL": this.EDLApplyASCCDL,
            "ASCCDLLayerNumber": this.ASCCDLLayerNumber,
            "ASCCDLColour": this.ASCCDLColour,
            "ASCCDLCategories": this.ASCCDLCategories,
            "BLGResourceConflict": this.BLGResourceConflict,
            "DestSelection": this.DestSelection,
            "LUTDirectory": this.LUTDirectory,
            "LUTLayerNum": this.LUTLayerNum,
            "LUTLayerColour": this.LUTLayerColour,
            "LUTCategories": this.LUTCategories,
            "CDLDirectory": this.CDLDirectory,
            "CDLLayerNum": this.CDLLayerNum,
            "CDLLayerColour": this.CDLLayerColour,
            "CDLCategories": this.CDLCategories,
            "MatchBy": this.MatchBy,
            "MatchQuality": this.MatchQuality,
            "PasteGrades": this.PasteGrades,
            "LayerZeroBehaviour": this.LayerZeroBehaviour,
            "LayerZeroOverwrite": this.LayerZeroOverwrite,
            "LayerZeroAudio": this.LayerZeroAudio,
            "InputColourSpace": this.InputColourSpace,
            "SourceShots": this.SourceShots,
            "SourceShotCategories": this.SourceShotCategories,
            "DestShots": this.DestShots,
            "DestShotCategories": this.DestShotCategories,
            "DetectGradeChanges": this.DetectGradeChanges,
            "GradeChangedCategory": this.GradeChangedCategory,
            "ClearUnchangedGrades": this.ClearUnchangedGrades,
            "PasteLocation": this.PasteLocation,
            "LayerZeroCategories": this.LayerZeroCategories,
            "LayerZeroExcludeCategories": this.LayerZeroExcludeCategories,
            "PasteMetadata": this.PasteMetadata,
            "MetadataColumns": this.MetadataColumns,
            "AddExtraMetadata": this.AddExtraMetadata,
            "OverwriteMetadata": this.OverwriteMetadata,
            "PasteGroups": this.PasteGroups,
            "ShredComps": this.ShredComps,
            "ShredProtectCategories": this.ShredProtectCategories,
            "ShredExternalMattes": this.ShredExternalMattes,
        }
    }

}
library.register_value_type( 'MultiPasteSettings', MultiPasteSettings )
module.exports.MultiPasteSettings = MultiPasteSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// NewSceneOptions
//
// Options for create a new database or temporary scene
//

var NewSceneOptions = class NewSceneOptions {

    constructor( obj )
    {
        if( obj != null )
        {
             this.format = obj.format;
             this.colourspace = obj.colourspace;
             this.frame_rate = obj.frame_rate;
             this.field_order = obj.field_order;
             this.template = obj.template;
             this.blg_template = obj.blg_template;
        }
        else
        {
             this.format = null;
             this.colourspace = null;
             this.frame_rate = null;
             this.field_order = "None";
             this.template = null;
             this.blg_template = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "NewSceneOptions",
            "format": this.format,
            "colourspace": this.colourspace,
            "frame_rate": this.frame_rate,
            "field_order": this.field_order,
            "template": this.template,
            "blg_template": this.blg_template,
        }
    }

}
library.register_value_type( 'NewSceneOptions', NewSceneOptions )
module.exports.NewSceneOptions = NewSceneOptions;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// OpenSceneStatus
//
// Status of scene opening or creation operation
//

var OpenSceneStatus = class OpenSceneStatus {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Done = obj.Done;
             this.Error = obj.Error;
             this.Progress = obj.Progress;
             this.Message = obj.Message;
        }
        else
        {
             this.Done = null;
             this.Error = null;
             this.Progress = null;
             this.Message = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "OpenSceneStatus",
            "Done": this.Done,
            "Error": this.Error,
            "Progress": this.Progress,
            "Message": this.Message,
        }
    }

}
library.register_value_type( 'OpenSceneStatus', OpenSceneStatus )
module.exports.OpenSceneStatus = OpenSceneStatus;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// QueueLogItem
//
// Log Item from Queue Operation
//

var QueueLogItem = class QueueLogItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Time = obj.Time;
             this.Type = obj.Type;
             this.Task = obj.Task;
             this.Frame = obj.Frame;
             this.Message = obj.Message;
             this.Detail = obj.Detail;
        }
        else
        {
             this.Time = null;
             this.Type = null;
             this.Task = null;
             this.Frame = null;
             this.Message = null;
             this.Detail = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "QueueLogItem",
            "Time": this.Time,
            "Type": this.Type,
            "Task": this.Task,
            "Frame": this.Frame,
            "Message": this.Message,
            "Detail": this.Detail,
        }
    }

}
library.register_value_type( 'QueueLogItem', QueueLogItem )
module.exports.QueueLogItem = QueueLogItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// QueueOp
//
// Description of an Operation in a Queue
//

var QueueOp = class QueueOp {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ID = obj.ID;
             this.Description = obj.Description;
             this.SubmitUser = obj.SubmitUser;
             this.SubmitHost = obj.SubmitHost;
        }
        else
        {
             this.ID = null;
             this.Description = null;
             this.SubmitUser = null;
             this.SubmitHost = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "QueueOp",
            "ID": this.ID,
            "Description": this.Description,
            "SubmitUser": this.SubmitUser,
            "SubmitHost": this.SubmitHost,
        }
    }

}
library.register_value_type( 'QueueOp', QueueOp )
module.exports.QueueOp = QueueOp;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// QueueOpStatus
//
// Status of an Operation in a Queue
//

var QueueOpStatus = class QueueOpStatus {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ID = obj.ID;
             this.Status = obj.Status;
             this.Progress = obj.Progress;
             this.ProgressText = obj.ProgressText;
             this.TimeElapsed = obj.TimeElapsed;
             this.TimeRemaining = obj.TimeRemaining;
             this.Warnings = obj.Warnings;
             this.Errors = obj.Errors;
        }
        else
        {
             this.ID = null;
             this.Status = null;
             this.Progress = null;
             this.ProgressText = null;
             this.TimeElapsed = null;
             this.TimeRemaining = null;
             this.Warnings = null;
             this.Errors = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "QueueOpStatus",
            "ID": this.ID,
            "Status": this.Status,
            "Progress": this.Progress,
            "ProgressText": this.ProgressText,
            "TimeElapsed": this.TimeElapsed,
            "TimeRemaining": this.TimeRemaining,
            "Warnings": this.Warnings,
            "Errors": this.Errors,
        }
    }

}
library.register_value_type( 'QueueOpStatus', QueueOpStatus )
module.exports.QueueOpStatus = QueueOpStatus;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// QueueOpTask
//
// Task information for FLAPI queue operation
//

var QueueOpTask = class QueueOpTask {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ID = obj.ID;
             this.Seq = obj.Seq;
             this.Type = obj.Type;
             this.Desc = obj.Desc;
             this.Skip = obj.Skip;
             this.Params = obj.Params;
             this.Weight = obj.Weight;
        }
        else
        {
             this.ID = null;
             this.Seq = null;
             this.Type = null;
             this.Desc = null;
             this.Skip = 0;
             this.Params = null;
             this.Weight = 1.000000;
        }
    }

    toJSON()
    {
        return {
            "_type": "QueueOpTask",
            "ID": this.ID,
            "Seq": this.Seq,
            "Type": this.Type,
            "Desc": this.Desc,
            "Skip": this.Skip,
            "Params": this.Params,
            "Weight": this.Weight,
        }
    }

}
library.register_value_type( 'QueueOpTask', QueueOpTask )
module.exports.QueueOpTask = QueueOpTask;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// Rational
//
// Holds a rational number.  Used in situations where exact ratios are required.
//

var Rational = class Rational {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Numerator = obj.Numerator;
             this.Denominator = obj.Denominator;
        }
        else
        {
             this.Numerator = null;
             this.Denominator = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "Rational",
            "Numerator": this.Numerator,
            "Denominator": this.Denominator,
        }
    }

}
library.register_value_type( 'Rational', Rational )
module.exports.Rational = Rational;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderCodecInfo
//
// Definition of a Codec that is supported for an image or movie file type
//

var RenderCodecInfo = class RenderCodecInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Text = obj.Text;
             this.Params = obj.Params;
        }
        else
        {
             this.Key = null;
             this.Text = null;
             this.Params = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderCodecInfo",
            "Key": this.Key,
            "Text": this.Text,
            "Params": this.Params,
        }
    }

}
library.register_value_type( 'RenderCodecInfo', RenderCodecInfo )
module.exports.RenderCodecInfo = RenderCodecInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderCodecParameterInfo
//
// Definition of a parameter to an image or movie codec
//

var RenderCodecParameterInfo = class RenderCodecParameterInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Text = obj.Text;
             this.Type = obj.Type;
             this.Choices = obj.Choices;
        }
        else
        {
             this.Key = null;
             this.Text = null;
             this.Type = null;
             this.Choices = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderCodecParameterInfo",
            "Key": this.Key,
            "Text": this.Text,
            "Type": this.Type,
            "Choices": this.Choices,
        }
    }

}
library.register_value_type( 'RenderCodecParameterInfo', RenderCodecParameterInfo )
module.exports.RenderCodecParameterInfo = RenderCodecParameterInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderCodecParameterValue
//
// Definition of a valid value for a codec parameter
//

var RenderCodecParameterValue = class RenderCodecParameterValue {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Text = obj.Text;
        }
        else
        {
             this.Key = null;
             this.Text = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderCodecParameterValue",
            "Key": this.Key,
            "Text": this.Text,
        }
    }

}
library.register_value_type( 'RenderCodecParameterValue', RenderCodecParameterValue )
module.exports.RenderCodecParameterValue = RenderCodecParameterValue;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderDeliverable
//
// This type is used to specify the render settings for an individual deliverable defined within a RenderSetup
//

var RenderDeliverable = class RenderDeliverable {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Name = obj.Name;
             this.Disabled = obj.Disabled;
             this.IsMovie = obj.IsMovie;
             this.FileType = obj.FileType;
             this.MovieCodec = obj.MovieCodec;
             this.AudioCodec = obj.AudioCodec;
             this.ImageOptions = obj.ImageOptions;
             this.FastStart = obj.FastStart;
             this.AudioSampleRate = obj.AudioSampleRate;
             this.AudioNumChannels = obj.AudioNumChannels;
             this.Container = obj.Container;
             this.OutputDirectory = obj.OutputDirectory;
             this.FileNamePrefix = obj.FileNamePrefix;
             this.FileNamePostfix = obj.FileNamePostfix;
             this.FileNameNumDigits = obj.FileNameNumDigits;
             this.FileNameNumber = obj.FileNameNumber;
             this.FileNameExtension = obj.FileNameExtension;
             this.ColourSpaceTag = obj.ColourSpaceTag;
             this.RenderFormat = obj.RenderFormat;
             this.RenderResolution = obj.RenderResolution;
             this.RenderFrameRate = obj.RenderFrameRate;
             this.RenderFieldOrder = obj.RenderFieldOrder;
             this.RenderDecodeQuality = obj.RenderDecodeQuality;
             this.RenderColourSpace = obj.RenderColourSpace;
             this.RenderVideoLUT = obj.RenderVideoLUT;
             this.RenderLayer = obj.RenderLayer;
             this.RenderTrack = obj.RenderTrack;
             this.RenderMask = obj.RenderMask;
             this.RenderMaskMode = obj.RenderMaskMode;
             this.RenderBurnin = obj.RenderBurnin;
             this.RenderFlashBurnin = obj.RenderFlashBurnin;
             this.RenderDisableCache = obj.RenderDisableCache;
             this.HandleIncompleteStacks = obj.HandleIncompleteStacks;
             this.HandleEmptyFrames = obj.HandleEmptyFrames;
             this.HandleError = obj.HandleError;
             this.EmbedTimecode = obj.EmbedTimecode;
             this.EmbedTape = obj.EmbedTape;
             this.EmbedClip = obj.EmbedClip;
        }
        else
        {
             this.Name = null;
             this.Disabled = 0;
             this.IsMovie = 0;
             this.FileType = null;
             this.MovieCodec = null;
             this.AudioCodec = null;
             this.ImageOptions = null;
             this.FastStart = 0;
             this.AudioSampleRate = 48000;
             this.AudioNumChannels = 0;
             this.Container = null;
             this.OutputDirectory = null;
             this.FileNamePrefix = "";
             this.FileNamePostfix = "";
             this.FileNameNumDigits = 7;
             this.FileNameNumber = "F";
             this.FileNameExtension = null;
             this.ColourSpaceTag = 1;
             this.RenderFormat = null;
             this.RenderResolution = "GMPR_HIGH";
             this.RenderFrameRate = null;
             this.RenderFieldOrder = "None";
             this.RenderDecodeQuality = "GMDQ_OPTIMISED_UNLESS_HIGH";
             this.RenderColourSpace = null;
             this.RenderVideoLUT = "none";
             this.RenderLayer = -1;
             this.RenderTrack = 0;
             this.RenderMask = "None";
             this.RenderMaskMode = 0;
             this.RenderBurnin = null;
             this.RenderFlashBurnin = 0;
             this.RenderDisableCache = 0;
             this.HandleIncompleteStacks = "GMREB_FAIL";
             this.HandleEmptyFrames = "GMREB_BLACK";
             this.HandleError = "ABORT";
             this.EmbedTimecode = 1;
             this.EmbedTape = 1;
             this.EmbedClip = 1;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderDeliverable",
            "Name": this.Name,
            "Disabled": this.Disabled,
            "IsMovie": this.IsMovie,
            "FileType": this.FileType,
            "MovieCodec": this.MovieCodec,
            "AudioCodec": this.AudioCodec,
            "ImageOptions": this.ImageOptions,
            "FastStart": this.FastStart,
            "AudioSampleRate": this.AudioSampleRate,
            "AudioNumChannels": this.AudioNumChannels,
            "Container": this.Container,
            "OutputDirectory": this.OutputDirectory,
            "FileNamePrefix": this.FileNamePrefix,
            "FileNamePostfix": this.FileNamePostfix,
            "FileNameNumDigits": this.FileNameNumDigits,
            "FileNameNumber": this.FileNameNumber,
            "FileNameExtension": this.FileNameExtension,
            "ColourSpaceTag": this.ColourSpaceTag,
            "RenderFormat": this.RenderFormat,
            "RenderResolution": this.RenderResolution,
            "RenderFrameRate": this.RenderFrameRate,
            "RenderFieldOrder": this.RenderFieldOrder,
            "RenderDecodeQuality": this.RenderDecodeQuality,
            "RenderColourSpace": this.RenderColourSpace,
            "RenderVideoLUT": this.RenderVideoLUT,
            "RenderLayer": this.RenderLayer,
            "RenderTrack": this.RenderTrack,
            "RenderMask": this.RenderMask,
            "RenderMaskMode": this.RenderMaskMode,
            "RenderBurnin": this.RenderBurnin,
            "RenderFlashBurnin": this.RenderFlashBurnin,
            "RenderDisableCache": this.RenderDisableCache,
            "HandleIncompleteStacks": this.HandleIncompleteStacks,
            "HandleEmptyFrames": this.HandleEmptyFrames,
            "HandleError": this.HandleError,
            "EmbedTimecode": this.EmbedTimecode,
            "EmbedTape": this.EmbedTape,
            "EmbedClip": this.EmbedClip,
        }
    }

}
library.register_value_type( 'RenderDeliverable', RenderDeliverable )
module.exports.RenderDeliverable = RenderDeliverable;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderFileTypeInfo
//
// Definition of an image or movie type
//

var RenderFileTypeInfo = class RenderFileTypeInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Text = obj.Text;
             this.Extensions = obj.Extensions;
             this.Params = obj.Params;
        }
        else
        {
             this.Key = null;
             this.Text = null;
             this.Extensions = null;
             this.Params = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderFileTypeInfo",
            "Key": this.Key,
            "Text": this.Text,
            "Extensions": this.Extensions,
            "Params": this.Params,
        }
    }

}
library.register_value_type( 'RenderFileTypeInfo', RenderFileTypeInfo )
module.exports.RenderFileTypeInfo = RenderFileTypeInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderOpInfo
//
// This type is returned to return information about render operations queued via QueueManager
//

var RenderOpInfo = class RenderOpInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ID = obj.ID;
             this.Warning = obj.Warning;
        }
        else
        {
             this.ID = null;
             this.Warning = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderOpInfo",
            "ID": this.ID,
            "Warning": this.Warning,
        }
    }

}
library.register_value_type( 'RenderOpInfo', RenderOpInfo )
module.exports.RenderOpInfo = RenderOpInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderProcessorLogItem
//
// Log Item from RenderProcessor
//

var RenderProcessorLogItem = class RenderProcessorLogItem {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Time = obj.Time;
             this.Type = obj.Type;
             this.Task = obj.Task;
             this.Frame = obj.Frame;
             this.Message = obj.Message;
             this.Detail = obj.Detail;
        }
        else
        {
             this.Time = null;
             this.Type = null;
             this.Task = null;
             this.Frame = null;
             this.Message = null;
             this.Detail = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderProcessorLogItem",
            "Time": this.Time,
            "Type": this.Type,
            "Task": this.Task,
            "Frame": this.Frame,
            "Message": this.Message,
            "Detail": this.Detail,
        }
    }

}
library.register_value_type( 'RenderProcessorLogItem', RenderProcessorLogItem )
module.exports.RenderProcessorLogItem = RenderProcessorLogItem;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// RenderStatus
//
// Status of render operation
//

var RenderStatus = class RenderStatus {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Status = obj.Status;
             this.Error = obj.Error;
             this.Total = obj.Total;
             this.Complete = obj.Complete;
             this.Remaining = obj.Remaining;
             this.Failed = obj.Failed;
             this.Progress = obj.Progress;
             this.ProgressMessage = obj.ProgressMessage;
        }
        else
        {
             this.Status = null;
             this.Error = null;
             this.Total = null;
             this.Complete = null;
             this.Remaining = null;
             this.Failed = null;
             this.Progress = null;
             this.ProgressMessage = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "RenderStatus",
            "Status": this.Status,
            "Error": this.Error,
            "Total": this.Total,
            "Complete": this.Complete,
            "Remaining": this.Remaining,
            "Failed": this.Failed,
            "Progress": this.Progress,
            "ProgressMessage": this.ProgressMessage,
        }
    }

}
library.register_value_type( 'RenderStatus', RenderStatus )
module.exports.RenderStatus = RenderStatus;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SDKVersion
//
// Version information for 3rd-party SDKs used in the application
//

var SDKVersion = class SDKVersion {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
             this.Description = obj.Description;
             this.Version = obj.Version;
        }
        else
        {
             this.Key = null;
             this.Name = null;
             this.Description = null;
             this.Version = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "SDKVersion",
            "Key": this.Key,
            "Name": this.Name,
            "Description": this.Description,
            "Version": this.Version,
        }
    }

}
library.register_value_type( 'SDKVersion', SDKVersion )
module.exports.SDKVersion = SDKVersion;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SceneInfo
//
// Return general information about the state of a scene
//

var SceneInfo = class SceneInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.CreatedDate = obj.CreatedDate;
             this.CreatedBy = obj.CreatedBy;
             this.CreatedVersion = obj.CreatedVersion;
             this.OpenedDate = obj.OpenedDate;
             this.OpenedBy = obj.OpenedBy;
             this.OpenedVersion = obj.OpenedVersion;
             this.ModifiedDate = obj.ModifiedDate;
             this.ModifiedBy = obj.ModifiedBy;
             this.ModifiedVersion = obj.ModifiedVersion;
             this.WorkingFormat = obj.WorkingFormat;
             this.Notes = obj.Notes;
             this.LastEDL = obj.LastEDL;
        }
        else
        {
             this.CreatedDate = null;
             this.CreatedBy = null;
             this.CreatedVersion = null;
             this.OpenedDate = null;
             this.OpenedBy = null;
             this.OpenedVersion = null;
             this.ModifiedDate = null;
             this.ModifiedBy = null;
             this.ModifiedVersion = null;
             this.WorkingFormat = null;
             this.Notes = null;
             this.LastEDL = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "SceneInfo",
            "CreatedDate": this.CreatedDate,
            "CreatedBy": this.CreatedBy,
            "CreatedVersion": this.CreatedVersion,
            "OpenedDate": this.OpenedDate,
            "OpenedBy": this.OpenedBy,
            "OpenedVersion": this.OpenedVersion,
            "ModifiedDate": this.ModifiedDate,
            "ModifiedBy": this.ModifiedBy,
            "ModifiedVersion": this.ModifiedVersion,
            "WorkingFormat": this.WorkingFormat,
            "Notes": this.Notes,
            "LastEDL": this.LastEDL,
        }
    }

}
library.register_value_type( 'SceneInfo', SceneInfo )
module.exports.SceneInfo = SceneInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ScenePath
//
// A ScenePath defines the host, job, folder and scene names required to create or open a FilmLight scene
//

var ScenePath = class ScenePath {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Type = obj.Type;
             this.Host = obj.Host;
             this.Job = obj.Job;
             this.Scene = obj.Scene;
             this.Tag = obj.Tag;
             this.Filename = obj.Filename;
        }
        else
        {
             this.Type = "psql";
             this.Host = null;
             this.Job = null;
             this.Scene = null;
             this.Tag = "Main";
             this.Filename = "";
        }
    }

    toJSON()
    {
        return {
            "_type": "ScenePath",
            "Type": this.Type,
            "Host": this.Host,
            "Job": this.Job,
            "Scene": this.Scene,
            "Tag": this.Tag,
            "Filename": this.Filename,
        }
    }

}
library.register_value_type( 'ScenePath', ScenePath )
module.exports.ScenePath = ScenePath;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// SceneSettingDefinition
//
// Type information for an SceneSettings parameter
//

var SceneSettingDefinition = class SceneSettingDefinition {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Type = obj.Type;
             this.Desc = obj.Desc;
             this.Values = obj.Values;
        }
        else
        {
             this.Type = null;
             this.Desc = null;
             this.Values = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "SceneSettingDefinition",
            "Type": this.Type,
            "Desc": this.Desc,
            "Values": this.Values,
        }
    }

}
library.register_value_type( 'SceneSettingDefinition', SceneSettingDefinition )
module.exports.SceneSettingDefinition = SceneSettingDefinition;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ShotIndexRange
//
// shot index range
//

var ShotIndexRange = class ShotIndexRange {

    constructor( obj )
    {
        if( obj != null )
        {
             this.FirstIndex = obj.FirstIndex;
             this.LastIndex = obj.LastIndex;
        }
        else
        {
             this.FirstIndex = null;
             this.LastIndex = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ShotIndexRange",
            "FirstIndex": this.FirstIndex,
            "LastIndex": this.LastIndex,
        }
    }

}
library.register_value_type( 'ShotIndexRange', ShotIndexRange )
module.exports.ShotIndexRange = ShotIndexRange;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// ShotInfo
//
// Shot info object
//

var ShotInfo = class ShotInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.ShotId = obj.ShotId;
             this.StartFrame = obj.StartFrame;
             this.EndFrame = obj.EndFrame;
             this.PosterFrame = obj.PosterFrame;
        }
        else
        {
             this.ShotId = null;
             this.StartFrame = null;
             this.EndFrame = null;
             this.PosterFrame = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "ShotInfo",
            "ShotId": this.ShotId,
            "StartFrame": this.StartFrame,
            "EndFrame": this.EndFrame,
            "PosterFrame": this.PosterFrame,
        }
    }

}
library.register_value_type( 'ShotInfo', ShotInfo )
module.exports.ShotInfo = ShotInfo;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// StillExportSettings
//
// Settings to use for Still exports
//

var StillExportSettings = class StillExportSettings {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Source = obj.Source;
             this.Filter = obj.Filter;
             this.Category = obj.Category;
             this.CategoryMatch = obj.CategoryMatch;
             this.Frames = obj.Frames;
             this.MarkCategory = obj.MarkCategory;
             this.Stereo = obj.Stereo;
             this.Directory = obj.Directory;
             this.Overwrite = obj.Overwrite;
             this.FileType = obj.FileType;
             this.ImageOptions = obj.ImageOptions;
             this.Path = obj.Path;
             this.Filename = obj.Filename;
             this.ColourSpace = obj.ColourSpace;
             this.Format = obj.Format;
             this.Resolution = obj.Resolution;
             this.DecodeQuality = obj.DecodeQuality;
             this.Mask = obj.Mask;
             this.MaskMode = obj.MaskMode;
             this.Burnin = obj.Burnin;
             this.Truelight = obj.Truelight;
        }
        else
        {
             this.Source = null;
             this.Filter = null;
             this.Category = null;
             this.CategoryMatch = null;
             this.Frames = null;
             this.MarkCategory = null;
             this.Stereo = null;
             this.Directory = null;
             this.Overwrite = null;
             this.FileType = null;
             this.ImageOptions = null;
             this.Path = null;
             this.Filename = null;
             this.ColourSpace = null;
             this.Format = null;
             this.Resolution = null;
             this.DecodeQuality = null;
             this.Mask = null;
             this.MaskMode = null;
             this.Burnin = null;
             this.Truelight = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "StillExportSettings",
            "Source": this.Source,
            "Filter": this.Filter,
            "Category": this.Category,
            "CategoryMatch": this.CategoryMatch,
            "Frames": this.Frames,
            "MarkCategory": this.MarkCategory,
            "Stereo": this.Stereo,
            "Directory": this.Directory,
            "Overwrite": this.Overwrite,
            "FileType": this.FileType,
            "ImageOptions": this.ImageOptions,
            "Path": this.Path,
            "Filename": this.Filename,
            "ColourSpace": this.ColourSpace,
            "Format": this.Format,
            "Resolution": this.Resolution,
            "DecodeQuality": this.DecodeQuality,
            "Mask": this.Mask,
            "MaskMode": this.MaskMode,
            "Burnin": this.Burnin,
            "Truelight": this.Truelight,
        }
    }

}
library.register_value_type( 'StillExportSettings', StillExportSettings )
module.exports.StillExportSettings = StillExportSettings;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//
// VolumeInfo
//
// Definition of a volume attached to, or accessible from, a FilmLight system
//

var VolumeInfo = class VolumeInfo {

    constructor( obj )
    {
        if( obj != null )
        {
             this.Key = obj.Key;
             this.Name = obj.Name;
             this.Label = obj.Label;
             this.Zone = obj.Zone;
             this.Path = obj.Path;
        }
        else
        {
             this.Key = null;
             this.Name = null;
             this.Label = null;
             this.Zone = null;
             this.Path = null;
        }
    }

    toJSON()
    {
        return {
            "_type": "VolumeInfo",
            "Key": this.Key,
            "Name": this.Name,
            "Label": this.Label,
            "Zone": this.Zone,
            "Path": this.Path,
        }
    }

}
library.register_value_type( 'VolumeInfo', VolumeInfo )
module.exports.VolumeInfo = VolumeInfo;

//////////////////////////////////////////////////////////////////
// Constants

// AUDIOSEQ_TYPE : Type of Audio in an Audio Sequence
//    AUDIOSEQTYPE_NONE : No Audio
//    AUDIOSEQTYPE_FILE : Audio File
//    AUDIOSEQTYPE_STEMS : Audio Stems
//    AUDIOSEQTYPE_MOVIE : Audio from Movie
//    AUDIOSEQTYPE_TONE : Audio is generated Tone
module.exports.AUDIOSEQTYPE_NONE = "AST_NONE";
module.exports.AUDIOSEQTYPE_FILE = "AST_FILE";
module.exports.AUDIOSEQTYPE_STEMS = "AST_STEMS";
module.exports.AUDIOSEQTYPE_MOVIE = "AST_MOVIE";
module.exports.AUDIOSEQTYPE_TONE = "AST_TONE";

// AUDIOSYNCSTATUS : Status info related to audio sync progress
//    AUDIOSYNCSTATUS_FAIL : Failure during audio sync operation
//    AUDIOSYNCSTATUS_WARN : Warning during audio sync operation
//    AUDIOSYNCSTATUS_INFO : Info from audio sync operation
//    AUDIOSYNCSTATUS_NOTE : Note from audio sync operation
//    AUDIOSYNCSTATUS_SCAN : Filesystem scanning progress
module.exports.AUDIOSYNCSTATUS_FAIL = "FAIL";
module.exports.AUDIOSYNCSTATUS_WARN = "WARN";
module.exports.AUDIOSYNCSTATUS_INFO = "INFO";
module.exports.AUDIOSYNCSTATUS_NOTE = "NOTE";
module.exports.AUDIOSYNCSTATUS_SCAN = "SCAN";

// AUDIOSYNC_CRITERIA : Values for AudioSyncSettings Criteria
//    AUDIOSYNC_CRITERIA_TIMECODE : Timecode
//    AUDIOSYNC_CRITERIA_SRCTIMECODE : Source Timecode
//    AUDIOSYNC_CRITERIA_DATESRCTIMECODE : Date & Source Timecode
//    AUDIOSYNC_CRITERIA_SCENETAKE : Scene & Take
//    AUDIOSYNC_CRITERIA_SHOTSCENETAKE : Shot Scene & Take
module.exports.AUDIOSYNC_CRITERIA_TIMECODE = "Timecode";
module.exports.AUDIOSYNC_CRITERIA_SRCTIMECODE = "SrcTimecode";
module.exports.AUDIOSYNC_CRITERIA_DATESRCTIMECODE = "DateSrcTimecode";
module.exports.AUDIOSYNC_CRITERIA_SCENETAKE = "SceneTake";
module.exports.AUDIOSYNC_CRITERIA_SHOTSCENETAKE = "ShotSceneTake";

// AUDIOSYNC_FPS : Values for AudioSyncSettings FPS
//    AUDIOSYNC_FPS_23976 : 23.976 fps
//    AUDIOSYNC_FPS_24000 : 24 fps
//    AUDIOSYNC_FPS_25000 : 25 fps
//    AUDIOSYNC_FPS_29970 : 29.97 fps
//    AUDIOSYNC_FPS_2997DF : 29.97 fps DF
//    AUDIOSYNC_FPS_30000 : 30 fps
//    AUDIOSYNC_FPS_48000 : 48 fps
//    AUDIOSYNC_FPS_50000 : 50 fps
//    AUDIOSYNC_FPS_59940 : 59.94 fps
//    AUDIOSYNC_FPS_60000 : 60 fps
module.exports.AUDIOSYNC_FPS_23976 = "23976";
module.exports.AUDIOSYNC_FPS_24000 = "24000";
module.exports.AUDIOSYNC_FPS_25000 = "25000";
module.exports.AUDIOSYNC_FPS_29970 = "29970";
module.exports.AUDIOSYNC_FPS_2997DF = "2997DF";
module.exports.AUDIOSYNC_FPS_30000 = "30000";
module.exports.AUDIOSYNC_FPS_48000 = "48000";
module.exports.AUDIOSYNC_FPS_50000 = "50000";
module.exports.AUDIOSYNC_FPS_59940 = "59940";
module.exports.AUDIOSYNC_FPS_60000 = "60000";

// AUDIOSYNC_METADATA : Values for AudioSyncSettings Metadata
//    AUDIOSYNC_METADATA_SCENETAKE : Scene & Take
//    AUDIOSYNC_METADATA_DATE : Date
module.exports.AUDIOSYNC_METADATA_SCENETAKE = "SceneTake";
module.exports.AUDIOSYNC_METADATA_DATE = "Date";

// AUDIOSYNC_RATIO : Values for AudioSyncSettings Ratio
//    AUDIOSYNC_RATIO_1_TO_1 : 1:1
//    AUDIOSYNC_RATIO_1001_TO_1000 : 1001:1000
//    AUDIOSYNC_RATIO_1000_TO_1001 : 1000:1001
//    AUDIOSYNC_RATIO_25_TO_24 : 25:24
//    AUDIOSYNC_RATIO_24_TO_25 : 24:25
module.exports.AUDIOSYNC_RATIO_1_TO_1 = "1:1";
module.exports.AUDIOSYNC_RATIO_1001_TO_1000 = "1001:1000";
module.exports.AUDIOSYNC_RATIO_1000_TO_1001 = "1000:1001";
module.exports.AUDIOSYNC_RATIO_25_TO_24 = "25:24";
module.exports.AUDIOSYNC_RATIO_24_TO_25 = "24:25";

// AUDIOSYNC_READLTC : Values for AudioSyncSettings ReadLTC
//    AUDIOSYNC_READLTC_NO : No
//    AUDIOSYNC_READLTC_CHANNEL : From Channel
//    AUDIOSYNC_READLTC_TRACK : From Track
module.exports.AUDIOSYNC_READLTC_NO = "No";
module.exports.AUDIOSYNC_READLTC_CHANNEL = "Channel";
module.exports.AUDIOSYNC_READLTC_TRACK = "Track";

// AUDIOSYNC_SUBSEARCH : Values for AudioSyncSettings SubSearch
//    AUDIOSYNC_SUBSEARCH_ALL : All Sub-Directories
//    AUDIOSYNC_SUBSEARCH_NAMED : Sub-Directories Named
//    AUDIOSYNC_SUBSEARCH_NEAREST : Nearest Sub-Directory Named
module.exports.AUDIOSYNC_SUBSEARCH_ALL = "All";
module.exports.AUDIOSYNC_SUBSEARCH_NAMED = "Named";
module.exports.AUDIOSYNC_SUBSEARCH_NEAREST = "Nearest";

// AUDIO_RATE : Audio Sample Rate
//    AUDIO_RATE_44100 : 44.1 kHz
//    AUDIO_RATE_48000 : 48 kHz
//    AUDIO_RATE_96000 : 96 kHz
module.exports.AUDIO_RATE_44100 = 44100;
module.exports.AUDIO_RATE_48000 = 48000;
module.exports.AUDIO_RATE_96000 = 96000;

// BLGEXPORT_LOCKGRADE : Values for BLGExportSettings LockGrade
//    BLGEXPORT_LOCKGRADE_READWRITE : No
//    BLGEXPORT_LOCKGRADE_LOCKED : Yes
module.exports.BLGEXPORT_LOCKGRADE_READWRITE = "ReadWrite";
module.exports.BLGEXPORT_LOCKGRADE_LOCKED = "Locked";

// BLGEXPORT_SCALE : Values for BLGExportSettings Scale
//    BLGEXPORT_SCALE_1 : Full
//    BLGEXPORT_SCALE_2 : Half
//    BLGEXPORT_SCALE_4 : Quarter
//    BLGEXPORT_SCALE_16 : Sixteenth
module.exports.BLGEXPORT_SCALE_1 = 1;
module.exports.BLGEXPORT_SCALE_2 = 2;
module.exports.BLGEXPORT_SCALE_4 = 4;
module.exports.BLGEXPORT_SCALE_16 = 16;

// BURNIN_BORDER : Define border type for burnin text item
//    BURNIN_BORDER_NONE : No border
//    BURNIN_BORDER_RECTANGLE : Rectangle
//    BURNIN_BORDER_LOZENGE : Lozenge
module.exports.BURNIN_BORDER_NONE = "none";
module.exports.BURNIN_BORDER_RECTANGLE = "rect";
module.exports.BURNIN_BORDER_LOZENGE = "loz";

// BURNIN_HALIGN : Define horizontal alignment of burnin text item
//    BURNIN_HALIGN_LEFT : Left aligned
//    BURNIN_HALIGN_CENTER : Center aligned
//    BURNIN_HALIGN_RIGHT : Right aligned
module.exports.BURNIN_HALIGN_LEFT = 0;
module.exports.BURNIN_HALIGN_CENTER = 1;
module.exports.BURNIN_HALIGN_RIGHT = 2;

// BURNIN_ITEM_TYPE : Specify burnin item type
//    BURNIN_ITEM_TEXT : Text item
//    BURNIN_ITEM_IMAGE : Image item
module.exports.BURNIN_ITEM_TEXT = "text";
module.exports.BURNIN_ITEM_IMAGE = "image";

// BURNIN_VALIGN : Define vertical alignment of burnin text item
//    BURNIN_VALIGN_TOP : Top aligned
//    BURNIN_VALIGN_MIDDLE : Middle aligned
//    BURNIN_VALIGN_BOTTOM : Bottom aligned
module.exports.BURNIN_VALIGN_TOP = 0;
module.exports.BURNIN_VALIGN_MIDDLE = 1;
module.exports.BURNIN_VALIGN_BOTTOM = 2;

// CDLEXPORT_CDLLAYER : Values for CDLExportSettings CDLLayer
//    CDLEXPORT_CDLLAYER_TOP : Top
//    CDLEXPORT_CDLLAYER_BOTTOM : Bottom
//    CDLEXPORT_CDLLAYER_CUSTOM : Layer n
module.exports.CDLEXPORT_CDLLAYER_TOP = "top";
module.exports.CDLEXPORT_CDLLAYER_BOTTOM = "bottom";
module.exports.CDLEXPORT_CDLLAYER_CUSTOM = "custom";

// CDLEXPORT_FORMAT : Values for CDLExportSettings Format
//    CDLEXPORT_FORMAT_CC : .cc file	Color Correction, one correction per file
//    CDLEXPORT_FORMAT_CCC : .ccc file	Color Correction Collection, all corrections in one file
module.exports.CDLEXPORT_FORMAT_CC = "CC";
module.exports.CDLEXPORT_FORMAT_CCC = "CCC";

// CUBEEXPORT_CUBERESOLUTION : Values for CubeExportSettings CubeResolution
//    CUBEEXPORT_CUBERESOLUTION_DEFAULT : Default
//    CUBEEXPORT_CUBERESOLUTION_16 : 16x16x16
//    CUBEEXPORT_CUBERESOLUTION_17 : 17x17x17
//    CUBEEXPORT_CUBERESOLUTION_32 : 32x32x32
//    CUBEEXPORT_CUBERESOLUTION_33 : 33x33x33
//    CUBEEXPORT_CUBERESOLUTION_64 : 64x64x64
module.exports.CUBEEXPORT_CUBERESOLUTION_DEFAULT = -1;
module.exports.CUBEEXPORT_CUBERESOLUTION_16 = 16;
module.exports.CUBEEXPORT_CUBERESOLUTION_17 = 17;
module.exports.CUBEEXPORT_CUBERESOLUTION_32 = 32;
module.exports.CUBEEXPORT_CUBERESOLUTION_33 = 33;
module.exports.CUBEEXPORT_CUBERESOLUTION_64 = 64;

// CUBEEXPORT_EXTENDEDRANGES : Values for CubeExportSettings ExtendedRanges
//    CUBEEXPORT_EXTENDEDRANGES_NO : No
//    CUBEEXPORT_EXTENDEDRANGES_LINEAR : Linear
//    CUBEEXPORT_EXTENDEDRANGES_LOG : Log
module.exports.CUBEEXPORT_EXTENDEDRANGES_NO = "No";
module.exports.CUBEEXPORT_EXTENDEDRANGES_LINEAR = "Linear";
module.exports.CUBEEXPORT_EXTENDEDRANGES_LOG = "Log";

// CUBEEXPORT_LUT1OPTIONS : Values for CubeExportSettings LUT1Options
//    CUBEEXPORT_LUT1OPTIONS_INPUT : Input Transform
//    CUBEEXPORT_LUT1OPTIONS_GRADE : Grade
//    CUBEEXPORT_LUT1OPTIONS_OUTPUT : Output Transform
module.exports.CUBEEXPORT_LUT1OPTIONS_INPUT = "Input";
module.exports.CUBEEXPORT_LUT1OPTIONS_GRADE = "Grade";
module.exports.CUBEEXPORT_LUT1OPTIONS_OUTPUT = "Output";

// CUBEEXPORT_LUT2OPTIONS : Values for CubeExportSettings LUT2Options
//    CUBEEXPORT_LUT2OPTIONS_INPUT : Input Transform
//    CUBEEXPORT_LUT2OPTIONS_GRADE : Grade
//    CUBEEXPORT_LUT2OPTIONS_OUTPUT : Output Transform
module.exports.CUBEEXPORT_LUT2OPTIONS_INPUT = "Input";
module.exports.CUBEEXPORT_LUT2OPTIONS_GRADE = "Grade";
module.exports.CUBEEXPORT_LUT2OPTIONS_OUTPUT = "Output";

// CUBEEXPORT_LUT3OPTIONS : Values for CubeExportSettings LUT3Options
//    CUBEEXPORT_LUT3OPTIONS_INPUT : Input Transform
//    CUBEEXPORT_LUT3OPTIONS_GRADE : Grade
//    CUBEEXPORT_LUT3OPTIONS_OUTPUT : Output Transform
module.exports.CUBEEXPORT_LUT3OPTIONS_INPUT = "Input";
module.exports.CUBEEXPORT_LUT3OPTIONS_GRADE = "Grade";
module.exports.CUBEEXPORT_LUT3OPTIONS_OUTPUT = "Output";

// CUBEEXPORT_LUTFORMAT : Values for CubeExportSettings LUTFormat
//    CUBEEXPORT_LUTFORMAT_TRUELIGHT : Truelight cube
//    CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D : Truelight 1D
//    CUBEEXPORT_LUTFORMAT_AMIRA : AMIRA
//    CUBEEXPORT_LUTFORMAT_ARRI : Arri
//    CUBEEXPORT_LUTFORMAT_AUTODESK : Autodesk
//    CUBEEXPORT_LUTFORMAT_AUTODESK_1D : Autodesk 1D
//    CUBEEXPORT_LUTFORMAT_AUTODESK_1DF : Autodesk 1D half float
//    CUBEEXPORT_LUTFORMAT_AUTODESK_MESH : Autodesk Lustre (Mesh)
//    CUBEEXPORT_LUTFORMAT_AUTODESK_CTF : Autodesk CTF
//    CUBEEXPORT_LUTFORMAT_BMD : BMD
//    CUBEEXPORT_LUTFORMAT_BARCO : Barco
//    CUBEEXPORT_LUTFORMAT_BLACKMAGIC : BlackMagic
//    CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D : BlackMagic 1D
//    CUBEEXPORT_LUTFORMAT_CANON_1D : Canon gamma 1D
//    CUBEEXPORT_LUTFORMAT_CANON_3D : Canon gamut 3D
//    CUBEEXPORT_LUTFORMAT_CINESPACE : CineSpace
//    CUBEEXPORT_LUTFORMAT_COLORFRONT_1D : Colorfront 1D
//    CUBEEXPORT_LUTFORMAT_COLORFRONT_3D : Colorfront 3D
//    CUBEEXPORT_LUTFORMAT_DVS : DVS
//    CUBEEXPORT_LUTFORMAT_DVS_1D : DVS 1D
//    CUBEEXPORT_LUTFORMAT_DAVINCI : DaVinci
//    CUBEEXPORT_LUTFORMAT_EVERTZ : Evertz
//    CUBEEXPORT_LUTFORMAT_ICC : ICC
//    CUBEEXPORT_LUTFORMAT_IRIDAS : IRIDAS
//    CUBEEXPORT_LUTFORMAT_IRIDAS_1D : IRIDAS 1D
//    CUBEEXPORT_LUTFORMAT_LUTHER : LUTher
//    CUBEEXPORT_LUTFORMAT_NUCODA : Nucoda
//    CUBEEXPORT_LUTFORMAT_PANASONIC : Panasonic
//    CUBEEXPORT_LUTFORMAT_PANDORA : Pandora
//    CUBEEXPORT_LUTFORMAT_QUANTEL : Quantel
//    CUBEEXPORT_LUTFORMAT_QUANTEL_65 : Quantel 65x65x65
//    CUBEEXPORT_LUTFORMAT_SCRATCH : Scratch
//    CUBEEXPORT_LUTFORMAT_SONY : Sony
//    CUBEEXPORT_LUTFORMAT_SONY_BVME : Sony BVME
module.exports.CUBEEXPORT_LUTFORMAT_TRUELIGHT = "Truelight";
module.exports.CUBEEXPORT_LUTFORMAT_TRUELIGHT_1D = "Truelight_1D";
module.exports.CUBEEXPORT_LUTFORMAT_AMIRA = "AMIRA";
module.exports.CUBEEXPORT_LUTFORMAT_ARRI = "Arri";
module.exports.CUBEEXPORT_LUTFORMAT_AUTODESK = "Autodesk";
module.exports.CUBEEXPORT_LUTFORMAT_AUTODESK_1D = "Autodesk_1D";
module.exports.CUBEEXPORT_LUTFORMAT_AUTODESK_1DF = "Autodesk_1Df";
module.exports.CUBEEXPORT_LUTFORMAT_AUTODESK_MESH = "Autodesk_Mesh";
module.exports.CUBEEXPORT_LUTFORMAT_AUTODESK_CTF = "Autodesk_ctf";
module.exports.CUBEEXPORT_LUTFORMAT_BMD = "BMD";
module.exports.CUBEEXPORT_LUTFORMAT_BARCO = "Barco";
module.exports.CUBEEXPORT_LUTFORMAT_BLACKMAGIC = "BlackMagic";
module.exports.CUBEEXPORT_LUTFORMAT_BLACKMAGIC_1D = "BlackMagic_1D";
module.exports.CUBEEXPORT_LUTFORMAT_CANON_1D = "Canon_1D";
module.exports.CUBEEXPORT_LUTFORMAT_CANON_3D = "Canon_3D";
module.exports.CUBEEXPORT_LUTFORMAT_CINESPACE = "CineSpace";
module.exports.CUBEEXPORT_LUTFORMAT_COLORFRONT_1D = "Colorfront_1D";
module.exports.CUBEEXPORT_LUTFORMAT_COLORFRONT_3D = "Colorfront_3D";
module.exports.CUBEEXPORT_LUTFORMAT_DVS = "DVS";
module.exports.CUBEEXPORT_LUTFORMAT_DVS_1D = "DVS_1D";
module.exports.CUBEEXPORT_LUTFORMAT_DAVINCI = "DaVinci";
module.exports.CUBEEXPORT_LUTFORMAT_EVERTZ = "Evertz";
module.exports.CUBEEXPORT_LUTFORMAT_ICC = "ICC";
module.exports.CUBEEXPORT_LUTFORMAT_IRIDAS = "IRIDAS";
module.exports.CUBEEXPORT_LUTFORMAT_IRIDAS_1D = "IRIDAS_1D";
module.exports.CUBEEXPORT_LUTFORMAT_LUTHER = "LUTher";
module.exports.CUBEEXPORT_LUTFORMAT_NUCODA = "Nucoda";
module.exports.CUBEEXPORT_LUTFORMAT_PANASONIC = "Panasonic";
module.exports.CUBEEXPORT_LUTFORMAT_PANDORA = "Pandora";
module.exports.CUBEEXPORT_LUTFORMAT_QUANTEL = "Quantel";
module.exports.CUBEEXPORT_LUTFORMAT_QUANTEL_65 = "Quantel_65";
module.exports.CUBEEXPORT_LUTFORMAT_SCRATCH = "Scratch";
module.exports.CUBEEXPORT_LUTFORMAT_SONY = "Sony";
module.exports.CUBEEXPORT_LUTFORMAT_SONY_BVME = "Sony_BVME";

// CUBEEXPORT_LUTRESOLUTION : Values for CubeExportSettings LUTResolution
//    CUBEEXPORT_LUTRESOLUTION_DEFAULT : Default
//    CUBEEXPORT_LUTRESOLUTION_1024 : 1024
//    CUBEEXPORT_LUTRESOLUTION_4096 : 4096
//    CUBEEXPORT_LUTRESOLUTION_16384 : 16384
module.exports.CUBEEXPORT_LUTRESOLUTION_DEFAULT = -1;
module.exports.CUBEEXPORT_LUTRESOLUTION_1024 = 1024;
module.exports.CUBEEXPORT_LUTRESOLUTION_4096 = 4096;
module.exports.CUBEEXPORT_LUTRESOLUTION_16384 = 16384;

// CUBEEXPORT_NUMLUTS : Values for CubeExportSettings NumLUTs
//    CUBEEXPORT_NUMLUTS_1 : 1
//    CUBEEXPORT_NUMLUTS_2 : 2
//    CUBEEXPORT_NUMLUTS_3 : 3
module.exports.CUBEEXPORT_NUMLUTS_1 = 1;
module.exports.CUBEEXPORT_NUMLUTS_2 = 2;
module.exports.CUBEEXPORT_NUMLUTS_3 = 3;

// DECODEPARAM_TYPE : Data type for a DecodeParameterDefinition
//    DECODEPARAMTYPE_INTEGER : Integer value
//    DECODEPARAMTYPE_FLOAT : Floating-point value
//    DECODEPARAMTYPE_BOOLEAN : Boolean value, represented as 1 or 0
//    DECODEPARAMTYPE_CHOICE : A choice for a set of discrete values
//    DECODEPARAMTYPE_FILE : Filename or path to a file
module.exports.DECODEPARAMTYPE_INTEGER = "Integer";
module.exports.DECODEPARAMTYPE_FLOAT = "Float";
module.exports.DECODEPARAMTYPE_BOOLEAN = "Boolean";
module.exports.DECODEPARAMTYPE_CHOICE = "Choice";
module.exports.DECODEPARAMTYPE_FILE = "File";

// DECODEQUALITY : Decode Qulity to use for decoding source images for RAW codecs
//    DECODEQUALITY_HIGH : Use highest quality RAW decode
//    DECODEQUALITY_OPTIMISED : Use nearest decode quality for render format/resolution
//    DECODEQUALITY_DRAFT : Use fastest decode quality
module.exports.DECODEQUALITY_HIGH = "GMDQ_OPTIMISED_UNLESS_HIGH";
module.exports.DECODEQUALITY_OPTIMISED = "GMDQ_OPTIMISED";
module.exports.DECODEQUALITY_DRAFT = "GMDQ_DRAFT";

// DIAGSTATUS : Status of diagnostic test
//    DIAG_READY : Ready to run
//    DIAG_WAITING : Waiting on pre-requisite test to complete
//    DIAG_RUNNING : Test is running
//    DIAG_PASS : Diagnostic passed
//    DIAG_WARNING : Diagnostic completed with warnings
//    DIAG_FAILED : Diagnostiic test failed
//    DIAG_SKIP : Skipped
module.exports.DIAG_READY = "ready";
module.exports.DIAG_WAITING = "waiting";
module.exports.DIAG_RUNNING = "running";
module.exports.DIAG_PASS = "pass";
module.exports.DIAG_WARNING = "warning";
module.exports.DIAG_FAILED = "failed";
module.exports.DIAG_SKIP = "skipped";

// DIAGWEIGHT : Weight of test
//    DIAGWEIGHT_LIGHT : Light tests
//    DIAGWEIGHT_MEDIUM : Medium tests
//    DIAGWEIGHT_HEAVY : Heavy tests
module.exports.DIAGWEIGHT_LIGHT = "DM_LIGHT";
module.exports.DIAGWEIGHT_MEDIUM = "DM_MEDIUM";
module.exports.DIAGWEIGHT_HEAVY = "DM_HEAVY";

// DIALOG_ITEM_TYPE : Type for a DynamicDialogItem used in a DynamicDialog
//    DIT_STRING : String
//    DIT_INTEGER : Integer
//    DIT_FLOAT : Floating-point number
//    DIT_TIMECODE : Timecode
//    DIT_DROPDOWN : Dropdown
//    DIT_LIST : List of items
//    DIT_TOGGLE : Toggle Button
//    DIT_TOGGLE_SET : Set of Toggle buttons
//    DIT_TOGGLE_DROPDOWN : Dropdown menu to allow toggling multiple items
//    DIT_TOGGLE_LIST : List of toggle items
//    DIT_RADIO_GROUP : Set of radio buttons
//    DIT_FILEPATH : File Path
//    DIT_IMAGEPATH : Image Path
//    DIT_DIRECTORY : Directory Path
//    DIT_SHOT_SELECTION : Shot Selection
//    DIT_STATIC_TEXT : Static Text
//    DIT_SHOT_CATEGORY : Shot Category
//    DIT_SHOT_CATEGORY_SET : Shot Category Set
//    DIT_MARK_CATEGORY : Shot Category
//    DIT_MARK_CATEGORY_SET : Mark Category Set
module.exports.DIT_STRING = "String";
module.exports.DIT_INTEGER = "Integer";
module.exports.DIT_FLOAT = "Float";
module.exports.DIT_TIMECODE = "Timecode";
module.exports.DIT_DROPDOWN = "Dropdown";
module.exports.DIT_LIST = "List";
module.exports.DIT_TOGGLE = "Toggle";
module.exports.DIT_TOGGLE_SET = "ToggleSet";
module.exports.DIT_TOGGLE_DROPDOWN = "ToggleDropdown";
module.exports.DIT_TOGGLE_LIST = "ToggleList";
module.exports.DIT_RADIO_GROUP = "RadioGroup";
module.exports.DIT_FILEPATH = "File";
module.exports.DIT_IMAGEPATH = "Image";
module.exports.DIT_DIRECTORY = "Directory";
module.exports.DIT_SHOT_SELECTION = "ShotSelection";
module.exports.DIT_STATIC_TEXT = "StaticText";
module.exports.DIT_SHOT_CATEGORY = "ShotCategory";
module.exports.DIT_SHOT_CATEGORY_SET = "CategorySet";
module.exports.DIT_MARK_CATEGORY = "MarkCategory";
module.exports.DIT_MARK_CATEGORY_SET = "MarkCategorySet";

// EXPORTSTATUS : Status info related to Export progress
//    EXPORTSTATUS_FAIL : Failure during export operation
//    EXPORTSTATUS_WARN : Warning during export operation
//    EXPORTSTATUS_INFO : Info from export operation
//    EXPORTSTATUS_NOTE : Note from export operation
//    EXPORTSTATUS_SCAN : Filesystem scanning progress
module.exports.EXPORTSTATUS_FAIL = "FAIL";
module.exports.EXPORTSTATUS_WARN = "WARN";
module.exports.EXPORTSTATUS_INFO = "INFO";
module.exports.EXPORTSTATUS_NOTE = "NOTE";
module.exports.EXPORTSTATUS_SCAN = "SCAN";

// EXPORTTYPE : Type of Exporter
//    EXPORTTYPE_STILL : Stills Exporter
//    EXPORTTYPE_BLG : BLG Exporter
//    EXPORTTYPE_CUBE : Cube Exporter
//    EXPORTTYPE_CDL : CDL Exporter
module.exports.EXPORTTYPE_STILL = "Still";
module.exports.EXPORTTYPE_BLG = "BLG";
module.exports.EXPORTTYPE_CUBE = "Cube";
module.exports.EXPORTTYPE_CDL = "CDL";

// EXPORT_CATEGORYMATCH : Values for Exporter CategoryMatch field
//    EXPORT_CATEGORYMATCH_ALL : All Categories
//    EXPORT_CATEGORYMATCH_ANY : Any Category
module.exports.EXPORT_CATEGORYMATCH_ALL = "all";
module.exports.EXPORT_CATEGORYMATCH_ANY = "any";

// EXPORT_FRAMES : Values for Exporter Frames field
//    EXPORT_FRAMES_FIRST : First Frame
//    EXPORT_FRAMES_POSTER : Poster Frame
//    EXPORT_FRAMES_MARKED : Marked Frames
//    EXPORT_FRAMES_CURRENT : Current Frame
module.exports.EXPORT_FRAMES_FIRST = "First";
module.exports.EXPORT_FRAMES_POSTER = "Poster";
module.exports.EXPORT_FRAMES_MARKED = "Marked";
module.exports.EXPORT_FRAMES_CURRENT = "Current";

// EXPORT_OVERWRITE : Values for Exporter Overwrite field
//    EXPORT_OVERWRITE_SKIP : Skip
//    EXPORT_OVERWRITE_REPLACE : Replace
module.exports.EXPORT_OVERWRITE_SKIP = "Skip";
module.exports.EXPORT_OVERWRITE_REPLACE = "Replace";

// EXPORT_SOURCE : Values for Exporter Source field
//    EXPORT_SOURCE_ALLSHOTS : All Shots
//    EXPORT_SOURCE_SELECTEDSHOTS : Selected Shots
//    EXPORT_SOURCE_CURRENTSHOT : Current Shot
//    EXPORT_SOURCE_SHOTSINFILTER : Shots in Filter
//    EXPORT_SOURCE_SHOTSOFCATEGORY : Shots of Category
module.exports.EXPORT_SOURCE_ALLSHOTS = "AllShots";
module.exports.EXPORT_SOURCE_SELECTEDSHOTS = "SelectedShots";
module.exports.EXPORT_SOURCE_CURRENTSHOT = "CurrentShot";
module.exports.EXPORT_SOURCE_SHOTSINFILTER = "ShotsInFilter";
module.exports.EXPORT_SOURCE_SHOTSOFCATEGORY = "ShotsOfCategory";

// EXPORT_STEREO : Values for Exporter Stereo field
//    EXPORT_STEREO_CURRENT : Current Eye
//    EXPORT_STEREO_LEFT : Left Eye
//    EXPORT_STEREO_RIGHT : Right Eye
//    EXPORT_STEREO_BOTH : Left & Right Eyes
//    EXPORT_STEREO_SINGLESTACKSTEREO : Single Stack Stereo (BLG exports only)
module.exports.EXPORT_STEREO_CURRENT = "Current";
module.exports.EXPORT_STEREO_LEFT = "Left";
module.exports.EXPORT_STEREO_RIGHT = "Right";
module.exports.EXPORT_STEREO_BOTH = "Both";
module.exports.EXPORT_STEREO_SINGLESTACKSTEREO = "SingleStackStereo";

// FIELDORDER : Field order behaviour
//    FIELDORDER_PROGRESSIVE : Progressive
//    FIELDORDER_UPPER : Upper-field first (PAL/SECAM)
//    FIELDORDER_LOWER : Lower-field first (NTSC)
module.exports.FIELDORDER_PROGRESSIVE = "None";
module.exports.FIELDORDER_UPPER = "upper";
module.exports.FIELDORDER_LOWER = "lower";

// FORMATSET_SCOPE : Defines the scope that a FormatSet is defined in
//    FORMATSET_SCOPE_FACTORY : Factory formats built-in to the software
//    FORMATSET_SCOPE_GLOBAL : Global Formats from the global formats database
//    FORMATSET_SCOPE_JOB : Formats defined for a given job in a database
//    FORMATSET_SCOPE_SCENE : Formats defined for a given scene
module.exports.FORMATSET_SCOPE_FACTORY = "factory";
module.exports.FORMATSET_SCOPE_GLOBAL = "global";
module.exports.FORMATSET_SCOPE_JOB = "job";
module.exports.FORMATSET_SCOPE_SCENE = "scene";

// FSFILTER : Type of items to return from Filesystem get_items method
//    FSFILTER_FILE : Return files
//    FSFILTER_DIR : Return directories
module.exports.FSFILTER_FILE = "file";
module.exports.FSFILTER_DIR = "directory";

// IMAGESEARCHER_METADATA_TRACK : Metadata track to use to group image files together into sequences
//    ISMT_FRAME_NUMBER : Collate frames into sequences based on frame number
//    ISMT_TIMECODE_1 : Collate frames into sequences based on Timecode 1
//    ISMT_TIMECODE_2 : Collate frames into sequences based on Timecode 2
//    ISMT_KEYCODE_1 : Collate frames into sequences based on Keycode
module.exports.ISMT_FRAME_NUMBER = "FSMT_FRAME_NUMBER";
module.exports.ISMT_TIMECODE_1 = "FSMT_TIMECODE_1";
module.exports.ISMT_TIMECODE_2 = "FSMT_TIMECODE_2";
module.exports.ISMT_KEYCODE_1 = "FSMT_KEYCODE_1";

// IMAGETRANSFORM_MODE : Specify filtering kernel to use for image resampling/transform operations
//    IMAGETRANSFORM_ADAPTIVE : Adaptive
//    IMAGETRANSFORM_BOX : Square Average (Box filter)
//    IMAGETRANSFORM_CIRCLE : Circle average
//    IMAGETRANSFORM_COMPOSITE : Composite
//    IMAGETRANSFORM_CUBIC : Fixed Cubic
//    IMAGETRANSFORM_CUBIC_SPLINE : Fixed Cubic Spline
//    IMAGETRANSFORM_LANCZOS : Fixed Lanczos 4-tap
//    IMAGETRANSFORM_6LANCZOS : Fixed Lanczos 6-tap
//    IMAGETRANSFORM_6QUINTIC : Fixed Quintic 6-tap
//    IMAGETRANSFORM_GAUSSIAN : Fixed Gaussian
//    IMAGETRANSFORM_CATMULL_ROM : Fixed Catmull-Rom
//    IMAGETRANSFORM_SIMON : Fixed Simon
//    IMAGETRANSFORM_LINEAR : Fixed Linear
//    IMAGETRANSFORM_NEAREST : Fixed Nearest Pixel
//    IMAGETRANSFORM_SHARPEDGE : Sharp Edge
module.exports.IMAGETRANSFORM_ADAPTIVE = "adaptive-soft";
module.exports.IMAGETRANSFORM_BOX = "box";
module.exports.IMAGETRANSFORM_CIRCLE = "circle";
module.exports.IMAGETRANSFORM_COMPOSITE = "composite";
module.exports.IMAGETRANSFORM_CUBIC = "cubic";
module.exports.IMAGETRANSFORM_CUBIC_SPLINE = "cubic-spline";
module.exports.IMAGETRANSFORM_LANCZOS = "Lanczos";
module.exports.IMAGETRANSFORM_6LANCZOS = "6Lanczos";
module.exports.IMAGETRANSFORM_6QUINTIC = "6quintic";
module.exports.IMAGETRANSFORM_GAUSSIAN = "Gaussian";
module.exports.IMAGETRANSFORM_CATMULL_ROM = "Catmull-Rom";
module.exports.IMAGETRANSFORM_SIMON = "Simon";
module.exports.IMAGETRANSFORM_LINEAR = "linear";
module.exports.IMAGETRANSFORM_NEAREST = "nearest";
module.exports.IMAGETRANSFORM_SHARPEDGE = "sharpEdge";

// INSERT_POSITION : Specify where to insert a sequence in a Scene
//    INSERT_START : Insert sequence at start of scene
//    INSERT_END : Insert sequence at end of scene
//    INSERT_BEFORE : Insert sequence before specified Shot
//    INSERT_AFTER : Insert sequence after specified Shot
//    INSERT_ABOVE : Insert sequence above specified Shot
//    INSERT_BELOW : Insert sequence below specified Shot
module.exports.INSERT_START = "start";
module.exports.INSERT_END = "end";
module.exports.INSERT_BEFORE = "before";
module.exports.INSERT_AFTER = "after";
module.exports.INSERT_ABOVE = "above";
module.exports.INSERT_BELOW = "below";

// LOG_SEVERITY : Log Message Severity
//    LOGSEVERITY_HARD : Hard error
//    LOGSEVERITY_SOFT : Soft error
//    LOGSEVERITY_INFO : Information or transient message
module.exports.LOGSEVERITY_HARD = "ERR_HARD";
module.exports.LOGSEVERITY_SOFT = "ERR_SOFT";
module.exports.LOGSEVERITY_INFO = "ERR_INFO_TRANSIENT";

// LUT_LOCATION : Specify where LUT data should be found for a LUT operator
//    LUTLOCATION_FILE : LUT is stored in an external file
//    LUTLOCATION_EMBEDDED : LUT is embedded in source image file
module.exports.LUTLOCATION_FILE = "file";
module.exports.LUTLOCATION_EMBEDDED = "embedded";

// MARK_TYPE : Used to distinguish between timeline, shot and strip marks
//    MARKTYPE_TIMELINE : Timeline mark, position stored as time in seconds relative to start of timeline
//    MARKTYPE_SHOT : Shot mark, position stored as source image frame number
//    MARKTYPE_STRIP : Strip mark, position stored as time in seconds relative to start of strip
module.exports.MARKTYPE_TIMELINE = "Timeline";
module.exports.MARKTYPE_SHOT = "Shot";
module.exports.MARKTYPE_STRIP = "Strip";

// MENU_LOCATION : Location within application of new menu or menu item
//    MENULOCATION_APP_MENU : Main application menu, ie Baselight or Daylight
//    MENULOCATION_SCENE_MENU : Scene menu
//    MENULOCATION_EDIT_MENU : Edit menu
//    MENULOCATION_JOB_MANAGER : Job Manager
//    MENULOCATION_SHOT_VIEW : Shots View
module.exports.MENULOCATION_APP_MENU = "ML_APPMENU";
module.exports.MENULOCATION_SCENE_MENU = "ML_SCENE";
module.exports.MENULOCATION_EDIT_MENU = "ML_EDIT";
module.exports.MENULOCATION_JOB_MANAGER = "ML_JOB_MANAGER";
module.exports.MENULOCATION_SHOT_VIEW = "ML_SHOTS_VIEW";

// MULTIPASTESTATUS : Status info related to Multi-Paste progress
//    MULTIPASTESTATUS_FAIL : Failure during multi-paste operation
//    MULTIPASTESTATUS_WARN : Warning during multi-paste operation
//    MULTIPASTESTATUS_INFO : Info from multi-paste operation
//    MULTIPASTESTATUS_NOTE : Note from multi-paste operation
//    MULTIPASTESTATUS_SCAN : Filesystem scanning progress
module.exports.MULTIPASTESTATUS_FAIL = "FAIL";
module.exports.MULTIPASTESTATUS_WARN = "WARN";
module.exports.MULTIPASTESTATUS_INFO = "INFO";
module.exports.MULTIPASTESTATUS_NOTE = "NOTE";
module.exports.MULTIPASTESTATUS_SCAN = "SCAN";

// MULTIPASTE_BLGRESOURCECONFLICT : Values for MultiPasteSettings BLGResourceConflict
//    MULTIPASTE_BLGRESOURCECONFLICT_REPLACE : Replace Existing Resources with BLG Versions
//    MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL : Use Existing Resources with the Same Name
//    MULTIPASTE_BLGRESOURCECONFLICT_RENAME : Import BLG Resources Under a New Name
module.exports.MULTIPASTE_BLGRESOURCECONFLICT_REPLACE = "Replace";
module.exports.MULTIPASTE_BLGRESOURCECONFLICT_ORIGINAL = "Original";
module.exports.MULTIPASTE_BLGRESOURCECONFLICT_RENAME = "Rename";

// MULTIPASTE_DESTSELECTION : Values for MultiPasteSettings DestSelection
//    MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS : Timeline Stacks Containing a Selected Strip
//    MULTIPASTE_DESTSELECTION_SELECTEDSHOTS : Selected Shots in Shots View/Cuts View
module.exports.MULTIPASTE_DESTSELECTION_SELECTEDSTRIPS = "SelectedStrips";
module.exports.MULTIPASTE_DESTSELECTION_SELECTEDSHOTS = "SelectedShots";

// MULTIPASTE_DESTSHOTS : Values for MultiPasteSettings DestShots
//    MULTIPASTE_DESTSHOTS_OVERWRITEALL : Overwrite All
//    MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS : Overwrite All, Except Layers of Category
//    MULTIPASTE_DESTSHOTS_RETAINALL : Retain All
//    MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS : Retain All, Except Layers of Category
module.exports.MULTIPASTE_DESTSHOTS_OVERWRITEALL = "OverwriteAll";
module.exports.MULTIPASTE_DESTSHOTS_OVERWRITEALLEXCEPTCATS = "OverwriteAllExceptCats";
module.exports.MULTIPASTE_DESTSHOTS_RETAINALL = "RetainAll";
module.exports.MULTIPASTE_DESTSHOTS_RETAINALLEXCEPTCATS = "RetainAllExceptCats";

// MULTIPASTE_EDLAPPLYASCCDL : Values for MultiPasteSettings EDLApplyASCCDL
//    MULTIPASTE_EDLAPPLYASCCDL_NO : No
//    MULTIPASTE_EDLAPPLYASCCDL_CDL : Yes
module.exports.MULTIPASTE_EDLAPPLYASCCDL_NO = "No";
module.exports.MULTIPASTE_EDLAPPLYASCCDL_CDL = "CDL";

// MULTIPASTE_LAYERZEROBEHAVIOUR : Values for MultiPasteSettings LayerZeroBehaviour
//    MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY : All Layers, Except Layer 0
//    MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK : All Layers, Including Layer 0
//    MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY : Layer 0 Only
//    MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS : No Layers
module.exports.MULTIPASTE_LAYERZEROBEHAVIOUR_STACKONLY = "StackOnly";
module.exports.MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROANDSTACK = "LayerZeroAndStack";
module.exports.MULTIPASTE_LAYERZEROBEHAVIOUR_LAYERZEROONLY = "LayerZeroOnly";
module.exports.MULTIPASTE_LAYERZEROBEHAVIOUR_NOLAYERS = "NoLayers";

// MULTIPASTE_LAYERZEROCATEGORIES : Values for MultiPasteSettings LayerZeroCategories
//    MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE : Append Categories, Except
//    MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE : Replace Categories, Add All Except
//    MULTIPASTE_LAYERZEROCATEGORIES_NO : Do Not Copy Layer 0 Categories
module.exports.MULTIPASTE_LAYERZEROCATEGORIES_INCLUDE = "Include";
module.exports.MULTIPASTE_LAYERZEROCATEGORIES_OVERWRITE = "Overwrite";
module.exports.MULTIPASTE_LAYERZEROCATEGORIES_NO = "No";

// MULTIPASTE_MATCHBY : Values for MultiPasteSettings MatchBy
//    MULTIPASTE_MATCHBY_TAPENAME : Source Tape Name
//    MULTIPASTE_MATCHBY_FILENAME : Source Path+Filename
//    MULTIPASTE_MATCHBY_CLIPNAME : Source Clip Name
//    MULTIPASTE_MATCHBY_AVIDUID : Source Avid UID
//    MULTIPASTE_MATCHBY_CAMERA : Source Camera
//    MULTIPASTE_MATCHBY_BLGNAME : Source BLG Name
//    MULTIPASTE_MATCHBY_BLGID : Source BLG ID
//    MULTIPASTE_MATCHBY_SCENE : Source Scene
//    MULTIPASTE_MATCHBY_SCENETAKE : Source Scene & Take
//    MULTIPASTE_MATCHBY_CAMERAROLL : Source Camera Roll
//    MULTIPASTE_MATCHBY_LABROLL : Source Lab Roll
//    MULTIPASTE_MATCHBY_LUT : Source LUT
//    MULTIPASTE_MATCHBY_LUT2 : Source LUT2
//    MULTIPASTE_MATCHBY_ASC_CC_XML : Source ASC_CC_XML
//    MULTIPASTE_MATCHBY_FRAMENUMBER : Source Frame Number
//    MULTIPASTE_MATCHBY_TIMECODE : Source Timecode
//    MULTIPASTE_MATCHBY_KEYCODE : Source Keycode
//    MULTIPASTE_MATCHBY_RECORDFRAMENUMBER : Record Frame Number
//    MULTIPASTE_MATCHBY_RECORDTIMECODE : Record Timecode
//    MULTIPASTE_MATCHBY_ALWAYSMATCH : Ignore Time Ranges
module.exports.MULTIPASTE_MATCHBY_TAPENAME = "TapeName";
module.exports.MULTIPASTE_MATCHBY_FILENAME = "Filename";
module.exports.MULTIPASTE_MATCHBY_CLIPNAME = "ClipName";
module.exports.MULTIPASTE_MATCHBY_AVIDUID = "AvidUID";
module.exports.MULTIPASTE_MATCHBY_CAMERA = "Camera";
module.exports.MULTIPASTE_MATCHBY_BLGNAME = "BLGName";
module.exports.MULTIPASTE_MATCHBY_BLGID = "BLGId";
module.exports.MULTIPASTE_MATCHBY_SCENE = "Scene";
module.exports.MULTIPASTE_MATCHBY_SCENETAKE = "SceneTake";
module.exports.MULTIPASTE_MATCHBY_CAMERAROLL = "CameraRoll";
module.exports.MULTIPASTE_MATCHBY_LABROLL = "LabRoll";
module.exports.MULTIPASTE_MATCHBY_LUT = "LUT";
module.exports.MULTIPASTE_MATCHBY_LUT2 = "LUT2";
module.exports.MULTIPASTE_MATCHBY_ASC_CC_XML = "ASC_CC_XML";
module.exports.MULTIPASTE_MATCHBY_FRAMENUMBER = "FrameNumber";
module.exports.MULTIPASTE_MATCHBY_TIMECODE = "Timecode";
module.exports.MULTIPASTE_MATCHBY_KEYCODE = "Keycode";
module.exports.MULTIPASTE_MATCHBY_RECORDFRAMENUMBER = "RecordFrameNumber";
module.exports.MULTIPASTE_MATCHBY_RECORDTIMECODE = "RecordTimecode";
module.exports.MULTIPASTE_MATCHBY_ALWAYSMATCH = "AlwaysMatch";

// MULTIPASTE_MATCHQUALITY : Values for MultiPasteSettings MatchQuality
//    MULTIPASTE_MATCHQUALITY_EXACTMATCH : Exact
//    MULTIPASTE_MATCHQUALITY_FUZZYMATCH : Fuzzy
module.exports.MULTIPASTE_MATCHQUALITY_EXACTMATCH = "ExactMatch";
module.exports.MULTIPASTE_MATCHQUALITY_FUZZYMATCH = "FuzzyMatch";

// MULTIPASTE_PASTELOCATION : Values for MultiPasteSettings PasteLocation
//    MULTIPASTE_PASTELOCATION_ABOVE : Above Remaining Destination Layers
//    MULTIPASTE_PASTELOCATION_BELOW : Below Remaining Destination Layers
module.exports.MULTIPASTE_PASTELOCATION_ABOVE = "Above";
module.exports.MULTIPASTE_PASTELOCATION_BELOW = "Below";

// MULTIPASTE_SOURCE : Values for MultiPasteSettings Source
//    MULTIPASTE_SOURCE_COPYBUFFER : Current Copy Buffer
//    MULTIPASTE_SOURCE_MULTIPLESCENES : Multiple Scenes
//    MULTIPASTE_SOURCE_BLG : BLG Files
//    MULTIPASTE_SOURCE_LUT : LUT Files
//    MULTIPASTE_SOURCE_CDL : CDL/CCC XML Files
//    MULTIPASTE_SOURCE_EDL : EDL/ALE files
module.exports.MULTIPASTE_SOURCE_COPYBUFFER = "CopyBuffer";
module.exports.MULTIPASTE_SOURCE_MULTIPLESCENES = "MultipleScenes";
module.exports.MULTIPASTE_SOURCE_BLG = "BLG";
module.exports.MULTIPASTE_SOURCE_LUT = "LUT";
module.exports.MULTIPASTE_SOURCE_CDL = "CDL";
module.exports.MULTIPASTE_SOURCE_EDL = "EDL";

// MULTIPASTE_SOURCESHOTS : Values for MultiPasteSettings SourceShots
//    MULTIPASTE_SOURCESHOTS_COPYALL : Copy All
//    MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS : Copy All, Except Layers of Category
//    MULTIPASTE_SOURCESHOTS_COPYONLYCATS : Copy Only Layers of Category
module.exports.MULTIPASTE_SOURCESHOTS_COPYALL = "CopyAll";
module.exports.MULTIPASTE_SOURCESHOTS_COPYALLEXCEPTCATS = "CopyAllExceptCats";
module.exports.MULTIPASTE_SOURCESHOTS_COPYONLYCATS = "CopyOnlyCats";

// OPENFLAG : Flags used to control opening a scene
//    OPENFLAG_DISCARD : Discard any unsaved changes when opening scene
//    OPENFLAG_RECOVER : Recover any unsaved changes when opening scene
//    OPENFLAG_OLD : Allow opening of old scenes
//    OPENFLAG_IGNORE_REVISION : Ignore data revision number when opening scene
//    OPENFLAG_READ_ONLY : Open scene read-only
//    OPENFLAG_ALLOW_UNKNOWN_OFX : Allow opening scenes that reference unknown OpenFX plugins
//    OPENFLAG_NO_CONTAINER_WARNING : Don't warn if scene uses container that is not known on this machine
module.exports.OPENFLAG_DISCARD = "discard";
module.exports.OPENFLAG_RECOVER = "recover";
module.exports.OPENFLAG_OLD = "openold";
module.exports.OPENFLAG_IGNORE_REVISION = "ignorerevision";
module.exports.OPENFLAG_READ_ONLY = "readonly";
module.exports.OPENFLAG_ALLOW_UNKNOWN_OFX = "allow_unknown_openfx";
module.exports.OPENFLAG_NO_CONTAINER_WARNING = "nocontainerwarning";

// OPERATOR_BARS_TYPE : Define the type of Bars to render
//    OPERATOR_BARS_TYPE_RP219HD_2a3a : SMPTE 75% white
//    OPERATOR_BARS_TYPE_RP219HD_2b3a : SMPTE 100% white
//    OPERATOR_BARS_TYPE_RP219HD_2c3b : SMPTE +I +Q
//    OPERATOR_BARS_TYPE_RP219HD_2d3b : SMPTE -I +Q
//    OPERATOR_BARS_TYPE_GREYS17 : Grey bars
//    OPERATOR_BARS_TYPE_RAMP : Grey ramp
//    OPERATOR_BARS_TYPE_RGBGREY : RGB and greys
//    OPERATOR_BARS_TYPE_B72 : BT.2111/ARIB B72 (HLG)
//    OPERATOR_BARS_TYPE_ITU2111_PQ : BT.2111 (PQ)
//    OPERATOR_BARS_TYPE_B66_4K : ARIB B66 (UHDTV 4K)
//    OPERATOR_BARS_TYPE_B66_8K : ARIB B66 (UHDTV 8K)
module.exports.OPERATOR_BARS_TYPE_RP219HD_2a3a = "RP219HD_2a3a";
module.exports.OPERATOR_BARS_TYPE_RP219HD_2b3a = "RP219HD_2b3a";
module.exports.OPERATOR_BARS_TYPE_RP219HD_2c3b = "RP219HD_2c3b";
module.exports.OPERATOR_BARS_TYPE_RP219HD_2d3b = "RP219HD_2d3b";
module.exports.OPERATOR_BARS_TYPE_GREYS17 = "GREYS17";
module.exports.OPERATOR_BARS_TYPE_RAMP = "RAMP";
module.exports.OPERATOR_BARS_TYPE_RGBGREY = "RGBGREY";
module.exports.OPERATOR_BARS_TYPE_B72 = "B72";
module.exports.OPERATOR_BARS_TYPE_ITU2111_PQ = "ITU2111_PQ";
module.exports.OPERATOR_BARS_TYPE_B66_4K = "B66_4K";
module.exports.OPERATOR_BARS_TYPE_B66_8K = "B66_8K";

// OPSTATUS : Status of an operation in Queue or Processor
//    OPSTATUS_CREATING : Operation is being created
//    OPSTATUS_QUEUED : Operation is waiting in the queue
//    OPSTATUS_ACTIVE : Operation is active
//    OPSTATUS_CRASHED : Operation crashed
//    OPSTATUS_STOPPED : Operation has been manually stopped
//    OPSTATUS_TOONEW : Operation was submitted to the queue by a newer version of the software and cannot be processed
//    OPSTATUS_DONE : Operation is complete
module.exports.OPSTATUS_CREATING = "Creating";
module.exports.OPSTATUS_QUEUED = "Queued";
module.exports.OPSTATUS_ACTIVE = "Active";
module.exports.OPSTATUS_CRASHED = "Crashed";
module.exports.OPSTATUS_STOPPED = "Stopped";
module.exports.OPSTATUS_TOONEW = "Too New";
module.exports.OPSTATUS_DONE = "Done";

// OPTICALFLOW_QUALITY : Optical Flow Quality
//    OFLOWQUAL_BEST : Best Quality
//    OFLOWQUAL_HIGH : High Quality
//    OFLOWQUAL_MEDIUM : Medium Quality
module.exports.OFLOWQUAL_BEST = "Best";
module.exports.OFLOWQUAL_HIGH = "High";
module.exports.OFLOWQUAL_MEDIUM = "Medium";

// OPTICALFLOW_SMOOTHING : Optical Flow Smoothing
//    OFLOWSMOOTH_NONE : None
//    OFLOWSMOOTH_LOW : Low
//    OFLOWSMOOTH_MEDIUM : Medium
//    OFLOWSMOOTH_HIGH : High
//    OFLOWSMOOTH_MAX : Maximum
module.exports.OFLOWSMOOTH_NONE = 0;
module.exports.OFLOWSMOOTH_LOW = 1;
module.exports.OFLOWSMOOTH_MEDIUM = 2;
module.exports.OFLOWSMOOTH_HIGH = 3;
module.exports.OFLOWSMOOTH_MAX = 4;

// PROXY_RESOLUTION : Proxy Resolution of Render Format
//    RES_HIGH : High (full) resolution
//    RES_MEDIUM : Medium proxy resolution
//    RES_LOW : Low proxy resolution
module.exports.RES_HIGH = "GMPR_HIGH";
module.exports.RES_MEDIUM = "GMPR_MEDIUM";
module.exports.RES_LOW = "GMPR_LOW";

// QUEUE_LOG_TYPE : Message type for log entry queue operation log
//    QUEUELOGTYPE_INFO : Information
//    QUEUELOGTYPE_WARN : Warning
//    QUEUELOGTYPE_FAIL : Error/failure
module.exports.QUEUELOGTYPE_INFO = "info";
module.exports.QUEUELOGTYPE_WARN = "warn";
module.exports.QUEUELOGTYPE_FAIL = "fail";

// RENDER_CLIPNAME_SOURCE : Which clip name to embed into rendered output
//    RENDER_CLIPNAME_FILE : Source File Clip Name
//    RENDER_CLIPNAME_SHOT : Shot Clip Name
//    RENDER_CLIPNAME_STRIP : Clip Name from Strip Name
module.exports.RENDER_CLIPNAME_FILE = 0;
module.exports.RENDER_CLIPNAME_SHOT = 1;
module.exports.RENDER_CLIPNAME_STRIP = 2;

// RENDER_COLOURSPACE : Special values to use for RenderColourSpace in RenderDeliverable
//    RENDER_COLOURSPACE_USEINPUT : Use Input Colour Space of Shot
//    RENDER_COLOURSPACE_USESTACKOUTPUT : Use Stack Output Colour Space.This will resolve to the Scene Grade Result Colour Space if specified, otherwise this will resolve to the Scene Working Colour Space.
module.exports.RENDER_COLOURSPACE_USEINPUT = "Input";
module.exports.RENDER_COLOURSPACE_USESTACKOUTPUT = "None";

// RENDER_EMPTY_BEHAVIOUR : Action to take when encountering frames in timeline with no strips/shots
//    RENDER_EMPTY_FAIL : Fail Render
//    RENDER_EMPTY_BLACK : Render Black Frame
//    RENDER_EMPTY_CHEQUER : Render Chequerboard Frame
module.exports.RENDER_EMPTY_FAIL = "GMREB_FAIL";
module.exports.RENDER_EMPTY_BLACK = "GMREB_BLACK";
module.exports.RENDER_EMPTY_CHEQUER = "GMREB_CHEQUER";

// RENDER_ERROR_BEHAVIOUR : Action to take when encountering frames in timeline with no strips/shots
//    RENDER_ERROR_FAIL : Fail Render
//    RENDER_ERROR_SKIP : Skip Frame And Continue
//    RENDER_ERROR_BLACK : Render Black Frame
//    RENDER_ERROR_CHEQUER : Render Chequerboard Frame And Continue
module.exports.RENDER_ERROR_FAIL = "ABORT";
module.exports.RENDER_ERROR_SKIP = "SKIP";
module.exports.RENDER_ERROR_BLACK = "BLACK";
module.exports.RENDER_ERROR_CHEQUER = "CHEQUER";

// RENDER_FORMAT : Special values to use for RenderFormat in RenderDeliverable
//    RENDER_FORMAT_USEINPUT : Use Shot Input Format
module.exports.RENDER_FORMAT_USEINPUT = "0";

// RENDER_FRAMENUM : Specify how frame number for sequence should be calculated
//    RENDER_FRAMENUM_SCENE_FRAME : Scene Frame Number
//    RENDER_FRAMENUM_SHOT_FRAME : Shot  Frame Number
//    RENDER_FRAMENUM_SCENE_TIMECODE : Record Timecode as Frame Number
//    RENDER_FRAMENUM_SHOT_TIMECODE : Shot Timecode as Frame Number
module.exports.RENDER_FRAMENUM_SCENE_FRAME = "F";
module.exports.RENDER_FRAMENUM_SHOT_FRAME = "G";
module.exports.RENDER_FRAMENUM_SCENE_TIMECODE = "T";
module.exports.RENDER_FRAMENUM_SHOT_TIMECODE = "H";

// RENDER_INCOMPLETE_BEHAVIOUR : Action to take when encountering shots with missing strips
//    RENDER_INCOMPLETE_FAIL : Fail Render
//    RENDER_INCOMPLETE_CONTINUE : Render As Baselight (Chequerboard Missing)
//    RENDER_INCOMPLETE_BLACK : Render Black Frame
//    RENDER_INCOMPLETE_CHEQUER : Render Chequerboard Frame
module.exports.RENDER_INCOMPLETE_FAIL = "GMREB_FAIL";
module.exports.RENDER_INCOMPLETE_CONTINUE = "GMREB_CONTINUE";
module.exports.RENDER_INCOMPLETE_BLACK = "GMREB_BLACK";
module.exports.RENDER_INCOMPLETE_CHEQUER = "GMREB_CHEQUER";

// RENDER_LAYER : Layers to include when rendering. This can be a layer number or one of the following constants.
//    RENDER_LAYER_ALL : Include all grade layers in rendered output
//    RENDER_LAYER_LAYERS_INPUTONLY : Do not include any grade layers or operators in layer 0
//    RENDER_LAYER_LAYER0 : Do not include any grade layers
module.exports.RENDER_LAYER_ALL = -1;
module.exports.RENDER_LAYER_LAYERS_INPUTONLY = -2;
module.exports.RENDER_LAYER_LAYER0 = 0;

// RENDER_MASK : Select whether to crop to the mask, or set the black value for the masked area
//    RENDER_MASK_CROP : Crop image to mask
//    RENDER_MASK_BLACK : Set mask area to absolue black (0)
//    RENDER_MASK_VIDEO : Set mask area to video black (16/255)
//    RENDER_MASK_FILM : Set mask area to film black (95/1023)
module.exports.RENDER_MASK_CROP = -1;
module.exports.RENDER_MASK_BLACK = 0;
module.exports.RENDER_MASK_VIDEO = 64;
module.exports.RENDER_MASK_FILM = 95;

// RENDER_NCLC_TAG : Which NCLC tag to use in QuickTime Movie files for colourimetry
//    RENDER_NCLC_LEGACY : Use legacy NCLC tag
//    RENDER_NCLC_AUTOMATIC : Use NCLC tag based on RenderColourSpace
module.exports.RENDER_NCLC_LEGACY = 0;
module.exports.RENDER_NCLC_AUTOMATIC = 1;

// RENDER_TAPENAME_SOURCE : Which tape name to embed into rendered output
//    RENDER_TAPENAME_FILE : Source File Tape Name
//    RENDER_TAPENAME_SHOT : Shot Tape Name
//    RENDER_TAPENAME_CLIP : Shot Clip Name
//    RENDER_TAPENAME_STRIP : Tape Name from Strip Name
module.exports.RENDER_TAPENAME_FILE = 0;
module.exports.RENDER_TAPENAME_SHOT = 1;
module.exports.RENDER_TAPENAME_CLIP = 3;
module.exports.RENDER_TAPENAME_STRIP = 2;

// RENDER_TIMECODE_SOURCE : Which timecode to embed into rendered output
//    RENDER_TIMECODE_FILETC1 : File Timecode 1
//    RENDER_TIMECODE_FILETC2 : File Timecode 2
//    RENDER_TIMECODE_SHOTTC : Shot Timecode
//    RENDER_TIMECODE_RECTC : Record (Timeline) Timecode
module.exports.RENDER_TIMECODE_FILETC1 = 0;
module.exports.RENDER_TIMECODE_FILETC2 = 3;
module.exports.RENDER_TIMECODE_SHOTTC = 2;
module.exports.RENDER_TIMECODE_RECTC = 1;

// ROP_TEXT_ALIGN : Text alignment
//    ROP_TEXT_ALIGN_LEFT : Left
//    ROP_TEXT_ALIGN_CENTER : Center
//    ROP_TEXT_ALIGN_RIGHT : Right
module.exports.ROP_TEXT_ALIGN_LEFT = 0;
module.exports.ROP_TEXT_ALIGN_CENTER = 1;
module.exports.ROP_TEXT_ALIGN_RIGHT = 2;

// SEQRESAMPLE_MODE : Sequence Resample Mode to use when resampling a sequence to a different video frame rate
//    SEQRESAMPLE_SNAP_TO_FRAME : Snap to Frame
//    SEQRESAMPLE_ROLLING_MAX : Mix Nearest Frames
//    SEQRESAMPLE_OPTICAL_FLOW : Optical Flow
module.exports.SEQRESAMPLE_SNAP_TO_FRAME = "SnapToFrame";
module.exports.SEQRESAMPLE_ROLLING_MAX = "RollingMix";
module.exports.SEQRESAMPLE_OPTICAL_FLOW = "OpticalFlow";

// STEREO_EYE : Stereo eye
//    STEREOEYE_MONO : Mono (no stereo)
//    STEREOEYE_LEFT : Left eye
//    STEREOEYE_RIGHT : Right eye
module.exports.STEREOEYE_MONO = "GMSE_MONO";
module.exports.STEREOEYE_LEFT = "GMSE_LEFT";
module.exports.STEREOEYE_RIGHT = "GMSE_RIGHT";

// STILLEXPORT_BURNIN : Values for StillExportSettings Burnin

// STILLEXPORT_DECODEQUALITY : Values for StillExportSettings DecodeQuality
//    STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH : Max Quality	Decode at maximum resolution
//    STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED : Optimised	Decode at half resolution where possible, for speed
//    STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT : Draft	Decode at draft quality, for maximum speed
module.exports.STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED_UNLESS_HIGH = "GMDQ_OPTIMISED_UNLESS_HIGH";
module.exports.STILLEXPORT_DECODEQUALITY_GMDQ_OPTIMISED = "GMDQ_OPTIMISED";
module.exports.STILLEXPORT_DECODEQUALITY_GMDQ_DRAFT = "GMDQ_DRAFT";

// STILLEXPORT_FILETYPE : Values for StillExportSettings FileType

// STILLEXPORT_FORMAT : Values for StillExportSettings Format

// STILLEXPORT_MASK : Values for StillExportSettings Mask

// STILLEXPORT_MASKMODE : Values for StillExportSettings MaskMode
//    STILLEXPORT_MASKMODE_CROP : Crop Image To Mask
//    STILLEXPORT_MASKMODE_HARDBLACK : Hard Black (0) Mask
//    STILLEXPORT_MASKMODE_VIDEOBLACK : Video Black (16/255) Mask
//    STILLEXPORT_MASKMODE_FILMBLACK : Film Black (95/1023) Mask
module.exports.STILLEXPORT_MASKMODE_CROP = "Crop";
module.exports.STILLEXPORT_MASKMODE_HARDBLACK = "HardBlack";
module.exports.STILLEXPORT_MASKMODE_VIDEOBLACK = "VideoBlack";
module.exports.STILLEXPORT_MASKMODE_FILMBLACK = "FilmBlack";

// STILLEXPORT_RESOLUTION : Values for StillExportSettings Resolution

// STILLEXPORT_TRUELIGHT : Values for StillExportSettings Truelight

// SVGFITMODE : Controls how an SVG is transformed/fitted into a shape strip's 'target area' (the working format area or an optional mask area transformed to the working format).
//    SVGFITMODE_NONE : The SVG is translated to the corner of the target area. No Scaling is applied.
//    SVGFITMODE_BEST : The SVG image is translated to the centre of the target area and pillarboxed or letterboxed to fit the target area's height or width respectively.
//    SVGFITMODE_STRETCH : The SVG is stretched horizontally and vertically to fit the target area.
module.exports.SVGFITMODE_NONE = "None";
module.exports.SVGFITMODE_BEST = "Best";
module.exports.SVGFITMODE_STRETCH = "Stretch";

// VIDEOLUT : Video Scaling LUT
//    VIDEOLUT_NONE : No video scaling LUT applied
//    VIDEOLUT_SCALE : Full to Legal Scale
//    VIDEOLUT_SCALE_NOCLIP : Full to Legal Scale (Unclipped)
//    VIDEOLUT_UNSCALE : Legal to Full Scale
//    VIDEOLUT_FULLRANGE_SOFTCLIP : Soft Clip to Full Range
//    VIDEOLUT_CLIP : Clip to Legal
//    VIDEOLUT_SOFTCLIP : Soft Clip to Legal
module.exports.VIDEOLUT_NONE = "none";
module.exports.VIDEOLUT_SCALE = "scale";
module.exports.VIDEOLUT_SCALE_NOCLIP = "scalenoclip";
module.exports.VIDEOLUT_UNSCALE = "unscale";
module.exports.VIDEOLUT_FULLRANGE_SOFTCLIP = "fullrangesoftclip";
module.exports.VIDEOLUT_CLIP = "clip";
module.exports.VIDEOLUT_SOFTCLIP = "softclip";

