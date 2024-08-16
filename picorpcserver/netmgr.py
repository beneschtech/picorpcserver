"""
The network manager class, manages reads/writes/connections, etc..
It supports static addresses and dhcp, but only supports ipv4
That is due to the underlying micropython methods
"""
import socket
from time import sleep
import machine
import network

WIFI_TIMEOUT = 10

class NetMgr:
    led = None
    wlan = None
    ssid = ""
    passw = ""
    ifcfg = None
    connection = None
    PAGE_SIZE = 4096
    verbose = False

    def __init__(self,ssid,passwd,ifconfig=None,verbose=False):
        self.ssid = ssid
        self.passw = passwd
        self.ifcfg = ifconfig
        self.verbose = verbose
        self.led = machine.Pin("LED",machine.Pin.OUT)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.led.off()
        if ifconfig is not None:
            self.wlan.ifconfig(ifconfig)
        self.wlan.connect(ssid,passwd)
        if verbose:
            print("NetMgr::__init__")

    def __del__(self):
        if verbose:
            print("NetMgr::__del__")
        self.connection.close()
        self.wlan.disconnect()
        self.led.off()

    def is_connected(self):
        return self.wlan.isconnected()

    def if_config(self):
        return self.wlan.ifconfig()

    def wait_for_connected(self):
        for i in range(WIFI_TIMEOUT*2):
            if self.wlan.isconnected():
                self.led.on()
                break
            sleep(0.5)
            self.led.toggle()
        if self.verbose:
            if self.wlan.isconnected():
                print("NetMgr::wait_for_connected Connected To Network")
                ic = self.wlan.ifconfig()
                print(f"  IP Address: {ic[0]}")
                print(f"  Netmask: {ic[1]}")
                print(f"  Gateway: {ic[2]}")
                print(f"  Nameserver(s): {ic[3]}")
            else:
                print("NetMgr::wait_for_connected Connection failed "+str(self.wlan.status()))
                self.net_fail()
 
        return self.wlan.isconnected()

    def bind_to_port(self,port):
        if self.verbose:
            print(f"NetMgr::bind_to_port({port})")

        address = ('', port)
        self.connection = socket.socket()
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        for attempt in range(10):
            try:
                self.connection.bind(address)
            except Exception as e:
                if self.verbose:
                    print(f"NetMgr::bind_to_port({port}) failed with {str(e)}, retry attempt {attempt}/10")
                sleep(1)
                continue
            else:
                break
        if attempt >= 9:
            self.net_fail()
        self.connection.listen(1)
        return self.connection

    def next_request(self):
        if self.verbose:
            print(f"NetMgr::next_request Listening")
        acc = self.connection.accept()
        if self.verbose:
            print(f"NetMgr::next_request Connection from {acc[1]}")
        return acc[0]

    def read_all(self,sock):
        rv = ""
        inbytes = sock.recv(NetMgr.PAGE_SIZE)
        while len(inbytes) == NetMgr.PAGE_SIZE:
            rv += inbytes.decode()
            inbytes = sock.recv(NetMgr.PAGE_SIZE)
        rv += inbytes.decode()
        if self.verbose:
            print(f"NetMgr::read_all Read {len(rv)} bytes")
        return rv

    def read(self,sock,sz):
        if sz == -1:
            return self.read_all(sock)
        rv = ""
        inbytes = sock.recv(sz)
        while len(inbytes) < sz:
            rv += inbytes.decode()
            inbytes = sock.recv(sz - len(inbytes))
        rv += inbytes.decode()
        if self.verbose:
            print(f"NetMgr::read Read {len(rv)} bytes")
        return rv

    def write(self,sock: socket.socket,data: bytes):
        sz = len(data)
        sent = sock.write(data)
        if (sent < sz):
            raise OSError("Short write")
        if self.verbose:
            print(f"NetMgr::write Wrote {sent} bytes")
        return sent

    def close(self):
        if self.verbose:
            print("NetMgr::close")
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.wlan.disconnect()
        self.led.off()

    def net_fail(self):
      while ( True ):
        sleep(0.25)
        self.led.toggle()
