# Final Skeleton
#
# Hints/Reminders from Lab 4:
# 
# To send an OpenFlow Message telling a switch to send packets out a
# port, do the following, replacing <PORT> with the port number the 
# switch should send the packets out:
#
#    msg = of.ofp_flow_mod()
#    msg.match = of.ofp_match.from_packet(packet)
#    msg.idle_timeout = 30
#    msg.hard_timeout = 30
#
#    msg.actions.append(of.ofp_action_output(port = <PORT>))
#    msg.data = packet_in
#    self.connection.send(msg)
#
# To drop packets, simply omit the action.
#

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Final (object):
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
  
  def send_packet (self, packet_in, port_out):
    msg = of.ofp_packet_out()
    msg.data = packet_in

    action = of.ofp_action_output(port=port_out)
    msg.actions.append(action)
    self.connection.send(msg) 

  def do_final (self, packet, packet_in, port_on_switch, switch_id):
    # This is where you'll put your code. The following modifications have 
    # been made from Lab 4:
    #   - port_on_switch represents the port that the packet was received on.
    #   - switch_id represents the id of the switch that received the packet
    #      (for example, s1 would have switch_id == 1, s2 would have switch_id == 2, etc...)
    
    #Put the relevant flow tables into the switch depending on it's type
    #do something with floor switches
    if switch_id <= 3:
      #If comes in on port 100 use port 1 to send or other way around
      if( port_on_switch == 100):
        print "Floor switch_"+str(switch_id)+" got packet on port: 100. Sending out on port 1"
        self.send_packet(packet_in, 1)
      else:
        print "Floor switch_"+str(switch_id)+" got packet on port: "+str(port_on_switch)+". Sending out on port 100"
        self.send_packet(packet_in, 100)
    
    #do something with core switch
    elif switch_id == 4:
      print('core')
      #This time it depends on the destination ip address
      if packet.find('ip'):
        if str(packet.dst) == '00:00:00:00:00:01':
          self.send_packet(packet_in, 1)
        elif str(packet.dst) == '00:00:00:00:00:02':
          self.send_packet(packet_in, 2)
        elif str(packet.dst) == '00:00:00:00:00:03':
          self.send_packet(packet_in, 3)
        elif str(packet.dst) == '00:00:00:00:00:04':
          self.send_packet(packet_in, 4)
        elif str(packet.dst) == '00:00:00:00:00:05':
          self.send_packet(packet_in, 5)
        else:
          print('error, bad IP packet') 
      else:
        self.send_packet(packet_in, of.OFPP_FLOOD)
    #do something with data center switch
    else:
      #if comes in on port 100 send out port 1 and other way around
      if( port_on_switch == 100):
        print "Data Center got packet on port: 100. Sending out on port 1"
        self.send_packet(packet_in, 1)
      else:
        print "Data Center got packet on port: "+str(port_on_switch)+". Sending out on port 100"
        self.send_packet(packet_in, 100)

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_final(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Final(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
