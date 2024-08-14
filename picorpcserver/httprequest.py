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
        self.hsock = sock
        self.nmgr = nm
        self.verbose = nm.verbose
        if self.verbose:
            print("HTTPRequest::__init__")
        self.raw_msg = nm.read_all(sock)
        self._parse()
        
    def socket(self):
        return self.hsock
    
    def net_manager(self):
        return self.nmgr
    
    def raw_message(self):
        return self.raw_msg
    
    def _parse(self):
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
        return self.method
    def url(self):
        return self.uri
    def protocol(self):
        return self.protocol
    def payload(self):
        return self.payload
    
    def headerval(self,key):
        if self.verbose:
            print(f"HTTPRequest::headerval ({key})")
        
        cmpkey = key.lower()
        for k in self.headers:
            if k.lower() == cmpkey:
                return self.headers[k]
        if self.verbose:
            print(f"HTTPRequest::headerval {key} not found")    
        return None
