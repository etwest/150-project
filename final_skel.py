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
    # Create a switches (each needs a unique numeric component
    floor_1 = self.addSwitch('floor_1')
    floor_2 = self.addSwitch('floor_2')
    floor_3 = self.addSwitch('floor_3')
    core = self.addSwitch('core_4')
    data = self.addSwitch('data_5')

    #link hosts to switches
    #For some reason all hosts require the usage of port 0 in order to work
    self.addLink(h10, floor_1, port1=0, port2=1)
    self.addLink(h20, floor_2, port1=0, port2=1)
    self.addLink(h30, floor_3, port1=0, port2=1)
    self.addLink(untrusth, core, port1=0, port2=4)
    self.addLink(server_1, data, port1=0, port2=2)

    #Link switches
    self.addLink(floor_1, core, port1=100, port2=1)
    self.addLink(floor_2, core, port1=100, port2=2)
    self.addLink(floor_3, core, port1=100, port2=3)
    self.addLink(data, core, port1=100, port2=5)


def configure():
  topo = final_topo()
  net = Mininet(topo=topo, controller=RemoteController)
  net.start()

  CLI(net)
  
  net.stop()


if __name__ == '__main__':
  configure()
