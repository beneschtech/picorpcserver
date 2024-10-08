"""
This object takes a raw string and determines the value to pass to a function,
the method name, and the id if able to be determined which is the key to map a
request to a response
"""
import json
from .jsonrpcexception import JsonRPCParseException,JsonRPCInvalidRequest
_GVERBOSEFLAG = False

class JSONRpcRequest:
    http_req = None
    method = ""
    data = {}
    id = ""
    raw_msg = ""

    def __init__(self,httpReq,verbose=False):
        global _GVERBOSEFLAG
        _GVERBOSEFLAG = verbose
        self.http_req = httpReq
        self.raw_msg = httpReq.payload
        if _GVERBOSEFLAG:
            print(f"JSONRpcRequest: Init with payload size of {len(self.raw_msg)}");

    def validate(self):
        global _GVERBOSEFLAG
        ctstr = self.http_req.headerval("content-type")
        payld = self.raw_msg
        if ctstr != "application/json":
            raise JsonRPCParseException('Content-Type is not application/json')
        msgobj = {}
        try:
          msgobj = json.loads(payld)
        except ValueError as ve:
          print(ve)
          raise JsonRPCParseException(str(ve))

        if "params" in msgobj:
            self.data = msgobj["params"]
        else:
            self.data = []

        if "id" in msgobj:
            self.id = msgobj["id"]
        else:
            self.id = None

        self.method = msgobj["method"]
        if msgobj["jsonrpc"] != "2.0":
            raise JsonRPCInvalidRequest("jsonrpc key is not '2.0'")
        if len(self.method) == 0:
            raise JsonRPCInvalidRequest("No method specified")

        if _GVERBOSEFLAG:
            print(f"JSONRpcRequest: id:{self.id}, method:{self.method}")