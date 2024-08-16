"""
This module represents a reply to request, it can be initialized
"""
import json
from .jsonrpcrequest import JSONRpcRequest
from .jsonrpcexception import JsonRPCException
from .httpresponse import HTTPResponse

class JSONRPCResponse:
    id = None
    req = None
    retVal = ""

    def __init__(self,req):
        self.req = req
        # A notification
        if req.id is None:
          resp = HTTPResponse(req.http_req)
          resp.headers["Content-Type"] = "application/json"
          resp.send(200,'')
        else:
          self.id = req.id

    def fromValue(self,val):
        print(f"JSONRPCResponse::fromValue({str(val)})")
        self.retVal = json.dumps({ "jsonrpc": "2.0", "id": self.id, "result": val })

    def fromException(self,ex):
        self.retVal = ex.json_string()

    def response_text(self):
        return self.retVal

    def send(self,hreq):
        print(f"JSONRPCResponse::send({str(self.retVal)})")
        resp = HTTPResponse(hreq)
        resp.headers["Content-Type"] = "application/json"
        resp.send(200,self.retVal)
