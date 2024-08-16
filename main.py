# We have a sleep later on, so we need time
import time

# In addition to the classes inside here, you can use the picorpcserver
# import itself as a wrapper around the classes inside, the end goal
# is set up network, map functions to method names and run
import picorpcserver

# Your Wifi parameters go here
WIFI_SSID = "MyWifiSSID"
WIFI_PASSWD = "MyWifiPassword"

# In addition to implement a statis address, specify this array
# Desired address, netmask, gateway, and nameserver in that order.
WIFI_IFCONFIG = ("172.16.5.2","255.255.0.0","172.16.0.1","172.16.2.1")

# The classic ping function which represents the template for rpc calls
# The value passed in will be directly json.loads from the wire, and the
# single parameter is the params attribute, it should return a single
# value which will be json encoded as a response.  I didnt work out
# supplying the request as well to check for headers, and other things
# after all this is a little microcontroller running python, if you need
# security and tokens and all that, get a full fledged pi and do this in C++
def rpc_ping(v):
    return f"Pong {v}!!"

# This function actually stops the netowrk loop, and shows one of the functions
# exposed by the back end.
def rpc_exit(v):
    picorpcserver.stop_listening()
    return "Stopping"

# This makes sure that the value passed in is a list of numbers
# and adds them all up, otherwise returns 0
def rpc_add(v):    
    if str(type(v)) != "<class 'list'>":
      return 0
    rv = 0
    for val in v:
      rv += val
    return rv

# By setting verbose, you see most of the internals of the communication
# and object layers. Very useful for debugging.
picorpcserver.set_verbose(True)

# Initial startup, which connects to your wifi. Passing in something like
# the ifconfig list above as a 3rd parameter will give you a static IP
# otherwise, it uses DHCP after authenticating with your network
if not picorpcserver.init(WIFI_SSID,WIFI_PASSWD):
    print("Network init failed!")
    exit(1)

# Bind a few of our functions, the format is "method",function
# there is no reason these cant be functions inside a package
# you create as well.
picorpcserver.map_function("ping",rpc_ping)
picorpcserver.map_function("add",rpc_add)
picorpcserver.map_function("exit",rpc_exit)

# This tells it to start listening and which port you want.
picorpcserver.set_listen_port(80)

# Initiates the run loop, it will continue until either
# it is explicitly stopped as above, or some kind of major
# exception occurs that it cant deal with.  Hopefully not
# the latter, but if it does, please let me know so we can 
# adress it
picorpcserver.run()

# Wait for any pending reads/writes and shut down the network
# stack
time.sleep(1)
picorpcserver.stop()

print("RPC Server stopped")
