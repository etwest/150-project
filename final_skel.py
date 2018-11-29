#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController

class final_topo(Topo):
  def build(self):
    h10 = self.addHost('h10',mac='00:00:00:00:00:01',ip='10.0.1.10/24', defaultRoute="h10-eth0")
    h20 = self.addHost('h20',mac='00:00:00:00:00:02',ip='10.0.1.20/24', defaultRoute="h20-eth0")
    h30 = self.addHost('h30',mac='00:00:00:00:00:03',ip='10.0.1.30/24', defaultRoute="h30-eth0")
    server_1 = self.addHost('server_1',mac='00:00:00:00:00:04',ip='10.0.4.10/24', defaultRoute="server_1-eth0")
    untrusth = self.addHost('untrusth',mac='00:00:00:00:00:05',ip='172.16.10.100/24', defaultRoute="untrusth-eth0")
    # Create a switches
    floor_1 = self.addSwitch('floor_1')
    floor_2 = self.addSwitch('floor_2')
    floor_3 = self.addSwitch('floor_3')
    core_1 = self.addSwitch('core_1')
    data_1 = self.addSwitch('data_1')

    #For communication from host to switch use host number for host port and floor number for switch port
    self.addLink(h10, floor_1, port1=10, port2=1)
    self.addLink(h20, floor_2, port1=20, port2=2)
    self.addLink(h30, floor_3, port1=30, port2=3)
    # Use port 100 to connect to the core switch and use port equal to floor num for core to switch
    self.addLink(floor_1, core_1, port1=100, port2=1)
    self.addLink(floor_2, core_1, port1=100, port2=2)
    self.addLink(floor_3, core_1, port1=100, port2=3)
    # port 100 to connect to core port 666 to connect to untrusted
    self.addLink(untrusth, core_1, port1=100, port2=666)
    # use port 101 to connect to data center and 100 to connect to core switch
    self.addLink(data_1, core_1, port1=100, port2=101)
    # use port 1 to connect to server 1 and port 101 to connect to data center switch
    self.addLink(server_1, data_1, port1=101, port2=1)

def configure():
  topo = final_topo()
  # net = Mininet(topo=topo, controller=RemoteController)
  net = Mininet(topo=topo)
  net.start()

  CLI(net)
  
  net.stop()


if __name__ == '__main__':
  configure()
