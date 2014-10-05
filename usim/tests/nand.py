#!/bin/env python2.7
# author: Michael Kimi
# date  : Jul 2013

"""a simple DUT to present microSim capabilities"""

from model.connector  import Connector
from model.unit       import Unit
from model.primitives import Not, And, Probe, drive
from model.port       import Port

## create the design, modules
top = Unit("top", None)

# add some ports
top.ports.addPort(Port("pi0", top, Port.Direction.IN))
top.ports.addPort(Port("pi1", top, Port.Direction.IN))
top.ports.addPort(Port("po", top, Port.Direction.OUT))

a1 = And("and1", top)
n1 = Not("not1", top)

dumpEable = True

c0 = Connector("c0", top, dumpEable, top.ports["pi0"], a1.ports["i0"])
c1 = Connector("c1", top, dumpEable, top.ports["pi1"], a1.ports["i1"])
c2 = Connector("c2", top, dumpEable, a1.ports["o"], n1.ports["i"])
c3 = Connector("c3", top, dumpEable, n1.ports["o"], top.ports["po"])


#exercise the design
def main(simControl):
    drive(simControl, top.ports["pi0"], value=1, time=0)
    drive(simControl, top.ports["pi1"], value=1, time=0)


