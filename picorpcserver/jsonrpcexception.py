"""
This object wraps an exception into a valid JSON-RPC exception
From anything to a parse error, or other issues once everything
is set, it can use json_string to retrieve the valid JSON-RPC 
formatted json string to return to the requestor
"""
import json

msgTable = {
    -32700: "Parse Error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid Parameters",
    -32603: "Internal Error"
}

def msgFromId(code):
    if code not in msgTable:
        return "Unknown Exception"
    return msgTable[code]

class JsonRPCException(Exception):
    code = 0
    extradata = None
    id = None

    def __init__(self,code,data,id = None):
        super().__init__()
        self.code = code
        self.extradata = data
        self.id = id

    def __str__(self):
        if self.extradata is not None:
            return str(self.extradata)
        return msgFromId(self.code)

    def json_string(self):
        robj = { "jsonrpc": "2.0" }
        if self.id is not None and len(str(self.id)) > 0:
            robj["id"] = self.id
        errobj = { "code": self.code, "message": msgFromId(self.code) }
        if self.extradata is not None:
            errobj["data"] = self.extradata
        robj["error"] = errobj
        return json.dumps(robj)

class JsonRPCParseException(JsonRPCException):
    def __init__(self,txt):
        super().__init__(-32700,txt)

class JsonRPCInvalidRequest(JsonRPCException):
    def __init__(self,obj):
        super().__init__(-32600,obj)

class JsonRPCSystemError(JsonRPCException):
    def __init__(self,e):
        super().__init__(-32603,str(e))