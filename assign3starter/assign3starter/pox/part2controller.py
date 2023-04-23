from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr,EthAddr

log = core.getLogger()

class Firewall (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)
    
    
    #add switch rules here only
    # arp = 0x806 
    
  def _handle_ConnectionUp(self, event):
    msg = of.ofp_flow_mod()
    msg.match.dl_dst = None
    msg.match.dl_type = 0x806
   
    msg.match.nw_proto = None
    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
    event.connection.send(msg)
    
    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr('00:00:00:00:00:01')
    msg.match.dl_type = 0x800
   
    msg.match.nw_proto = 1
    msg.actions.append(of.ofp_action_output(port = 1))
    event.connection.send(msg)

    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr('00:00:00:00:00:02')
    msg.match.dl_type = 0x800
   
    msg.match.nw_proto = 1
    msg.actions.append(of.ofp_action_output(port = 2))
    event.connection.send(msg)

    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr('00:00:00:00:00:03')
    msg.match.dl_type = 0x800
    msg.match.nw_proto = 1
    msg.actions.append(of.ofp_action_output(port = 3))
    event.connection.send(msg)

    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr('00:00:00:00:00:04')
    msg.match.dl_type = 0x800
    msg.match.nw_proto = 1
    msg.actions.append(of.ofp_action_output(port = 4))
    event.connection.send(msg)



  def _handle_PacketIn (self, event):
    """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    print ("Unhandled packet :" + str(packet.dump()))

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Firewall(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
