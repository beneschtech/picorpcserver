from .netmgr import NetMgr
from .httprequest import HTTPRequest
from .httpresponse import HTTPResponse
from .jsonrpcexception import JsonRPCException,JsonRPCParseException,JsonRPCInvalidRequest,JsonRPCSystemError
from .jsonrpcrequest import JSONRpcRequest
from .jsonrpcresponse import JSONRPCResponse

_gNetMgr = None
_gVerboseFlag = False
_gFuncMap = {}
_gListenPort = 80
_gKeepListening = True

def init(nwid,nwpass,ifc=None):
    global _gNetMgr
    _gNetMgr = NetMgr(nwid,nwpass,ifc,_gVerboseFlag)
    return _gNetMgr.wait_for_connected()

def stop():
    global _gNetMgr
    _gNetMgr.close()
    _gNetMgr = None
    
def stop_listening():
    global _gKeepListening
    _gKeepListening = False
    
def set_verbose(v):
    global _gVerboseFlag
    _gVerboseFlag = v
    
def map_function(method,func):
    global _gFuncMap
    _gFuncMap[method] = func
    
def set_listen_port(l):
    global _gListenPort
    _gListenPort = int(l)
    
def _listenForMessages():
    global _gKeepListening
    global _gNetMgr
    if _gNetMgr is None:
        return false
    if not _gNetMgr.is_connected():
        return false
    return _gKeepListening

def run():
    global _gNetMgr
    global _gFuncMap
    global _gListenPort
    global _gVerboseFlag
    
    try:
        _gNetMgr.bind_to_port(_gListenPort)
    except Exception as e:
        print(e)
        _gNetMgr.close()
        return
    
    while _listenForMessages():
        hreq = HTTPRequest(_gNetMgr,_gNetMgr.next_request())
        jreq=None
        try:
            jreq = JSONRpcRequest(hreq,_gVerboseFlag)
            jreq.validate()
        except JsonRPCException as je:
            resp = JSONRPCResponse(jreq)
            resp.fromException(je)
            resp.send(hreq)
            continue
        method = jreq.method
        if method not in _gFuncMap:
            jex = JsonRpcException(-32601,method,jreq.id)
            resp = JSONRPCResponse(jreq)
            resp.fromException(je)
            resp.send(hreq)
            continue
        try:
            rval = _gFuncMap[method](jreq.data)
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
            resp.fromException(je)
            resp.send(hreq)
            continue
        
            