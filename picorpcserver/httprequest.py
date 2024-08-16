"""
Implements basic HTTP request parsing. This does not support SSL or anything like that
but can be used to serve a simple web server if needed. The underlying process to jsonrpc
It can verifiably stand on its own if needed.
"""
import socket
from .netmgr import NetMgr
class HTTPRequest:
    
    raw_msg = ""
    hsock = None
    nmgr = None
    verbose = False
    payload = ""
    headers = {}
    method = ""
    uri = ""
    protocol = ""
    
    def __init__(self,nm,sock):
        """
        Initializes the http server, it requires the following parameters
        nm: A connected NetMgr object
        sock: A socket that is successfully listening
        """
        self.hsock = sock
        self.nmgr = nm
        self.verbose = nm.verbose
        if self.verbose:
            print("HTTPRequest::__init__")
        self.raw_msg = nm.read_all(sock)
        self._parse()
        
    def socket(self):
        """
        Returns the listening socket used to create this object
        """
        return self.hsock
    
    def net_manager(self):
        """
        Returns the connected NetMgr object used to construct the object
        """
        return self.nmgr
    
    def raw_message(self):
        """
        Returns the raw message read from the socket to process
        """
        return self.raw_msg
    
    def _parse(self):
        """
        Parses the message filling in the method, url, headers, and raw message sent.
        """
        if self.verbose:
            print("HTTPRequest::parse")
        try:
            offst = self.raw_msg.find("\r\n\r\n")
            hdr = self.raw_msg[:offst]
            self.payload = self.raw_msg[offst+4:]
            hdrs = hdr.split("\r\n")        
            protocolh = hdrs[0]        
            for hdrt in hdrs[1:]:
                hdrta = hdrt.split(':')
                key = hdrta[0].strip()
                val = hdrta[1].strip()            
                self.headers[key.lower()] = val
            parr = protocolh.split()
            if len(parr) != 3:
                return false
            self.method = parr[0]
            self.uri = parr[1]
            self.protocol = parr[2]
        except e as Exception:
            if self.verbose:
                print(f"HTTPRequest::parse exception: {e}")
            return false
        if self.verbose:
            print(self.headers)
        return True
        
    def method(self):
        """
        The method used for this request, usually POST or GET
        """
        return self.method

    def url(self):
        """
        The URL being requested
        """
        return self.uri

    def protocol(self):
        """
        The request protocol, usually HTTP/1.1
        """
        return self.protocol

    def payload(self):
        """
        The raw data sent after the headers. Will be blank if its a get request
        """
        return self.payload
    
    def headerval(self,key):
        """
        Returns a case insensitive match for a header and retrieve its value
        """
        if self.verbose:
            print(f"HTTPRequest::headerval ({key})")
        
        cmpkey = key.lower()
        for k in self.headers:
            if k.lower() == cmpkey:
                return self.headers[k]
        if self.verbose:
            print(f"HTTPRequest::headerval {key} not found")    
        return None
