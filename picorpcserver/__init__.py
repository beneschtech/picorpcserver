"""
This is the main module for the rpc server, it includes the necessary
objects and some exported functions to assist in running the server
successfully

You can use these objects directly to implement a simple http server
or in this case a jsonrpc server. It relies heavily on exception
catching, so make sure in your code that things are cleaned up 
correctly if an exception is thrown
"""
from .netmgr import NetMgr
from .httprequest import HTTPRequest
from .httpresponse import HTTPResponse
from .jsonrpcexception import JsonRPCException,JsonRPCParseException
from .jsonrpcexception import JsonRPCInvalidRequest,JsonRPCSystemError
from .jsonrpcrequest import JSONRpcRequest
from .jsonrpcresponse import JSONRPCResponse

_GNETMGR = None
_GVERBOSEFLAG = False
_GFUNCMAP = {}
_GLISTENPORT = 80
_GKEEPLISTENING = True

def init(nwid,nwpass,ifc=None):
    """
    Starts the network subsystem, connecting to the wifi, and setting up network
    params.

    nwid is a required parameter and denotes the wifi network name
    nwpass is a required password to connect to that network

    ifc is an optional parameter and can be used if you want to use a static ip
    address.  The format is ('ip.add.re.ss','ne.t.ma.sk','ga.te.wa.y','na.me.ser.ver')
    Please note that the underlying Micropython network stack does not seem to include
    support for IPv6.

    It uses the onboard LED to show status: 
      Blinking 1/2 second: connecting in progress
      On solid: Running, connected, operational
      Blinking fast (1/4 second): Uncaught exception, system down
    """
    global _GNETMGR
    _GNETMGR = NetMgr(nwid,nwpass,ifc,_GVERBOSEFLAG)
    return _GNETMGR.wait_for_connected()

def stop():
    """
    Stops the network and disconnects cleanly, the LED will now go off
    """
    global _GNETMGR
    _GNETMGR.close()
    _GNETMGR = None

def stop_listening():
    """
    Stops the listening loop ands returns from the run() function after
    the next loop (request), or tldr, this is the last request.
    """
    global _GKEEPLISTENING
    _GKEEPLISTENING = False

def set_verbose(v):
    """
    Sets the verbose flag and allows you to see internals of the program
    as it runs. This must be set before init() is called to operate correctly
    """
    global _GVERBOSEFLAG
    _GVERBOSEFLAG = v

def map_function(method,func):
    """
    Maps a method string to a function written to accept and return
    JSON-RPC functions. The function template is as follows:

    def func(Any val):
        retval = do_something()
        return retval
    """
    global _GFUNCMAP
    if _GFUNCMAP is None:
        _GFUNCMAP = {method: func}
    else:
        _GFUNCMAP[method] = func

def set_listen_port(l):
    """
    Sets the TCP port to listen on must be called before run()
    and after init()
    """
    global _GLISTENPORT
    _GLISTENPORT = int(l)

def __listen_for_messages():
    """
    Private function that determines whether to keep running the listen
    loop. It checks whether the application has requested to stop
    and also that the network is still connected
    """
    global _GKEEPLISTENING
    global _GNETMGR
    if _GNETMGR is None:
        return False
    if not _GNETMGR.is_connected():
        return False
    return _GKEEPLISTENING

def run():
    """
    This is the heart of the jsonrpc function
    Once your functions are mapped and connected to the
    network, this one will listen on a port and process it
    accordingly. It does all of this inside of a single
    thread, if you want to support long running operations
    you will need to start another thread inside of your
    code. Beware there are only 2 threads available on the
    pico RP2040, so you either need a job manager or to only do
    quick operations with this
    """
    global _GNETMGR
    global _GFUNCMAP
    global _GLISTENPORT
    global _GVERBOSEFLAG

    try:
        _GNETMGR.bind_to_port(_GLISTENPORT)
    except Exception as e:
        print(e)
        _GNETMGR.close()
        return

    while __listen_for_messages():
        try:
            hreq = HTTPRequest(_GNETMGR,_GNETMGR.next_request())
        except Exception as e:
            print(f"Exception occured while getting next request! {str(e)}")
            _GKEEPLISTENING = False
            continue

        jreq=None
        try:
            jreq = JSONRpcRequest(hreq,_GVERBOSEFLAG)
            jreq.validate()
        except JsonRPCException as je:
            resp = JSONRPCResponse(jreq)
            resp.fromException(je)
            resp.send(hreq)
            continue
        method = jreq.method
        if method not in _GFUNCMAP:
            jex = JsonRPCException(-32601,method,jreq.id)
            resp = JSONRPCResponse(jreq)
            resp.fromException(jex)
            resp.send(hreq)
            continue
        try:
            rval = _GFUNCMAP[method](jreq.data)
            resp = JSONRPCResponse(jreq)
            resp.fromValue(rval)
            if jreq.id is not None:
                resp.send(hreq)
        except JsonRPCException as je:
            resp = JSONRPCResponse(jreq)
            resp.fromException(je)
            resp.send(hreq)
            continue
        except Exception as e:
            print(f"Exception caught! {str(e)}")
            ex = JsonRPCSystemError(e)
            resp = JSONRPCResponse(jreq)
            resp.fromException(ex)
            resp.send(hreq)
            continue
