import time
import picorpcserver

WIFI_SSID = "MyWifiSSID"
WIFI_PASSWD = "MyWifiPassword"
WIFI_IFCONFIG = ("172.16.5.2","255.255.0.0","172.16.0.1","172.16.2.1")


def rpc_ping(v):
    return f"Pong {v}!!"

def rpc_exit(v):
    picorpcserver.stop_listening()
    return "Stopping"

def rpc_add(v):    
    if str(type(v)) != "<class 'list'>":
      return 0
    rv = 0
    for val in v:
      rv += val
    return rv

picorpcserver.set_verbose(True)
if not picorpcserver.init(WIFI_SSID,WIFI_PASSWD):
    print("Network init failed!")
    exit(1)

picorpcserver.map_function("ping",rpc_ping)
picorpcserver.map_function("add",rpc_add)
picorpcserver.map_function("exit",rpc_exit)
picorpcserver.set_listen_port(80)
picorpcserver.run()
time.sleep(1)
picorpcserver.stop()

print("RPC Server stopped")
