# picorpcserver
JsonRPC Server infrastructure for a Pi Pico microcontroller

This is a more or less (less) implementation of the jsonrpc protocol written in MicroPython for the Raspberry Pi Pico microcontroller.
See the main.py file for detailed and commented usage examples. You would need to transfer the entire picorpcserver directory to your Pico. I developed this in Thonny, and the best advice for debugging is to set the verbose flag to True and use CTRL-D in the shell window to reset it and try again.

Usage is fairly simple, more detail in the main.py file:

```
import picorpcserver

WIFI_SSID = "MyWifiSSID"
WIFI_PASSWD = "MyWifiPassword"

def rpc_ping(v):
    return f"Pong {v}!!"

if not picorpcserver.init(WIFI_SSID,WIFI_PASSWD):
    print("Network init failed!")
    exit(1)

picorpcserver.map_function("ping",rpc_ping)
picorpcserver.set_listen_port(80)
picorpcserver.run()
time.sleep(1)
picorpcserver.stop()

print("RPC Server stopped")
```
