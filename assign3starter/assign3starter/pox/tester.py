
# Importing necessary modules and functions from the POX library
# POX is a networking software platform that provides services and components for creating software-defined networks
# Based on tutorial from POX creator 


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import pox.lib.packet as pkt

# Getting logger instance from the core module for logging purposes
log = core.getLogger()

# Creating a dictionary of IPs
IPS = {
  "h10" : ("10.0.1.10","x"),
  "h20" : ("10.0.2.20", "x"),
  "h30" : ("10.0.3.30", "x"),
  "serv1" : ("10.0.4.10", "x"),
  "hnotrust" : ("172.16.10.100", "x"),
}


# Defining a class for the OpenFlow controller
class Part3Controller (object):
  """
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Printing the Data Path ID (DPID) of the connection
    print (connection.dpid)
  # Storing the connection to the switch
    self.connection = connection

   # Binding the PacketIn event listener
    connection.addListeners(self)
    # Checking the DPID to setup appropriate switch
    if (connection.dpid == 1):
      self.setup_s1()
    elif (connection.dpid == 2):
      self.setup_s2()
    elif (connection.dpid == 3):
      self.setup_s3()
    elif (connection.dpid == 21):
      self.cores21_setup()
    elif (connection.dpid == 31):
      self.dcs31_setup()
    else:
     # If the DPID does not match any of the predefined ones, the switch is unknown and the program exits
      print ("UNKNOWN SWITCH")
      exit(1)
# Methods to setup different switches
  def setup_s1(self):
    self._allow_all()

  def setup_s2(self):
    self._allow_all()

  def setup_s3(self):
    self._allow_all()

  def cores21_setup(self):
    # Block communications with 'hnotrust'
    self._block()                                
    # Guide traffic through switch
    self._allow_IP_traffic()                
     # flood/drop the rest
    self._allow_all()                           

  def dcs31_setup(self):
    self._allow_all()

 # Method to flood all communications going through the network, dropping the rest
  def _allow_all(self, act=of.ofp_action_output(port=of.OFPP_FLOOD)):
    self.connection.send(of.ofp_flow_mod(action=act,
                                         priority=2))     # flood to all ports
    # Send a low priority rule to drop packets if no other rules apply
    self.connection.send(of.ofp_flow_mod(priority=1))
  
  # Method to block ICMP from 'hnotrust' to anyone, and block all IP to 'serv1'
  def _block(self, block=IPS['hnotrust'][0]):
    block_icmp = of.ofp_flow_mod(priority=20,
                                 match=of.ofp_match(dl_type=0x800,
                                                    nw_proto=pkt.ipv4.ICMP_PROTOCOL,
                                                    nw_src=block))
    self.connection.send(block_icmp)
    block_to_serv = of.ofp_flow_mod(priority=19,
                                 match=of.ofp_match(dl_type=0x800,
                                                    nw_src=block,
                                                    nw_dst=IPS['serv1'][0]))
    self.connection.send(block_to_serv)
  
  # allow IP traffic as normal
  def _allow_IP_traffic(self):
    host = {10: (IPS['h10'][0], 1),
            20: (IPS['h20'][0], 2),
            30: (IPS['h30'][0], 3),
            40: (IPS['serv1'][0], 4),
            50: (IPS['hnotrust'][0], 5)}
    
    for i in range(len(host)):
      h = host[(i+1)*10][0]
      p = host[(i+1)*10][1]
      self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=p),
                                           priority=5,
                                           match=of.ofp_match(dl_type=0x800,
                                                              nw_dst=h)))


  def _handle_PacketIn (self, event):
   
    #Packets not caught by router rules will forward to here
 

    packet = event.parsed 
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp 
    print('Unhandled packet from '+str(self.connection.dpid)+':'+packet.dump())

def launch ():
  #initialize component
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part3Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
part3controller.py
Displaying part3controller.py.
