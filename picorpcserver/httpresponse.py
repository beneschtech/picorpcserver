"""
This class is a one shot class that wraps raw data and a code
and special headers if set into a valid HTTP response
"""
class HTTPResponse:
    net = None
    sock = None
    code = 200
    _hlines = {
        200: "OK",
        403: "Unauthorized",
        404: "Not Found",
        500: "Internal Error"
    }
    headers = {
        "Content-Type": "text/html",
        "Server": "RP2040/MicroPython"
    }
    def __init__(self,htreq):
        self.net = htreq.nmgr
        self.sock = htreq.hsock

    def send(self,code,payload):
        """
        This sends the request on the socket obtained from the constructor
        it closes the connection at the end because we cant support requests
        that are based on saved connections without signifacantly more
        code. We are running on a microcontroller after all...
        """
        rv = f"HTTP/1.1 {code} {self._hlines[code]}\r\n"
        for k in self.headers:
            if k.lower() == "content-length".lower():
                continue
            rv += f"{k}: {self.headers[k]}\r\n"
        rv += f"Content-Length: {len(payload)}\r\n"
        rv += "\r\n"
        rv += payload
        self.net.write(self.sock,rv.encode())
        self.sock.close()