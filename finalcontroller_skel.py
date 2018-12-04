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
import pox.lib.packet as pkt

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
    
    #route or drop packets depending on which switch they are arriving at
    #do something with floor switches
    if switch_id <= 3:
      #If comes in on port 100 use port 1 to send or other way around
      if( port_on_switch == 100):
        self.send_packet(packet_in, 1)
      else:
        self.send_packet(packet_in, 100)
      # push the flow table for this information to the floor switch
      fm = of.ofp_flow_mod()
      fm.priority = 5
      fm.hard_timeout = 45
      fm.match.in_port = 100
      fm.actions.append(of.ofp_action_output(port=1))
      self.connection.send(fm)
      fm = of.ofp_flow_mod()
      fm.priority = 5
      fm.hard_timeout = 45
      fm.match.in_port = 1
      fm.actions.append(of.ofp_action_output(port=100))
      self.connection.send(fm)
    
    ####################### core switch #########################
    elif switch_id == 4:
      #ip packets need to be occasionally blocked and are routed to specific ports
      if packet.find('ipv4'):
        skip = False
        if str(packet.src) == '00:00:00:00:00:05':
          #This originated from the untrusted host so we block some traffic
          if str(packet.dst) == '00:00:00:00:00:04': #cannot send any ip to server
            msg = of.ofp_packet_out()
            self.connection.send(msg)
            skip = True
          if packet.find('icmp'): #untrusted cannot send icmp so block that
            msg = of.ofp_packet_out()
            self.connection.send(msg)
            skip = True
        if skip == False:
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
      # rule for dropping all traffic from untrusted to server
      fm = of.ofp_flow_mod()
      fm.priority = 10
      fm.hard_timeout = 45
      fm.match.dl_type = pkt.ethernet.IP_TYPE
      fm.match.nw_src = '172.16.10.100'
      fm.match.nw_dst = '10.0.4.0/24'
      self.connection.send(fm)
      # rule for blocking all icmp traffic from untrusted to anyone
      fm = of.ofp_flow_mod()
      fm.priority = 8
      fm.hard_timeout = 45
      fm.match.dl_type = pkt.ethernet.IP_TYPE
      fm.match.nw_proto = 1
      fm.match.nw_src = '172.16.10.100'
      self.connection.send(fm)
      # rule for various destinations
      for i in range(1,5):
        fm = of.ofp_flow_mod()
        fm.priority = 5
        fm.hard_timeout = 45
        fm.match.dl_type = pkt.ethernet.IP_TYPE
        fm.match.nw_dst = '10.0.'+str(i)+'.0/24'
        fm.actions.append(of.ofp_action_output(port=i))
        self.connection.send(fm)
      fm = of.ofp_flow_mod()
      fm.hard_timeout = 45
      fm.match.dl_type = pkt.ethernet.IP_TYPE
      fm.match.nw_dst = '172.16.10.100'
      fm.actions.append(of.ofp_action_output(port=5))
      self.connection.send(fm)
      fm = of.ofp_flow_mod()
      fm.priority = 1
      fm.hard_timeout = 40
      fm.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
      self.connection.send(fm)

    #do something with data center switch
    else:
      #if comes in on port 100 send out port 1 and other way around
      if( port_on_switch == 100):
        self.send_packet(packet_in, 1)
      else:
        self.send_packet(packet_in, 100)
      #install flow tables to data center switch that deal with this information
      fm = of.ofp_flow_mod()
      fm.priority = 5
      fm.hard_timeout = 45
      fm.match.in_port = 100
      fm.actions.append(of.ofp_action_output(port=1))
      self.connection.send(fm)
      fm = of.ofp_flow_mod()
      fm.priority = 5
      fm.hard_timeout = 45
      fm.match.in_port = 1
      fm.actions.append(of.ofp_action_output(port=100))
      self.connection.send(fm)

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
