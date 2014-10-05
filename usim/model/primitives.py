#!/bin/env python2.7
# author: Michael Kimi
# date  : Mon Sep  2 13:48:25 2013

"""holds the representation of all common primitives like gates, probes etc"""

from simulation_core.simulator import Event
from model.port                import Port
from model.ports               import Ports
from model.unit                import Unit


###############################################################################
class And(Unit):
    """a class that defines AND gate"""

    def __init__(self, name, hostUnitRef, propagationDelay=2):
        """AND gate ctor. creates AND gate with 2 inputs 1 output pins"""
        super(And, self).__init__(name, hostUnitRef)
        self.ports.addPort(Port("o",  self, Port.Direction.OUT))
        self.ports.addPort(Port("i0", self, Port.Direction.IN))
        self.ports.addPort(Port("i1", self, Port.Direction.IN))
        self._delay = propagationDelay

    def __str__(self, indent=""):
        return super(And, self).__str__(indent) + \
          " delay {:2}".format(self._delay)
    
    def handleEvent(self, event):
        """implement the logic of and gate"""
        newTime = event.time + self._delay
        outVal = 1

        for inPort in self.ports.iterInputPorts():
            outVal = outVal and inPort.value

        if outVal != self.ports["o"].value:
            return [Event(newTime, outVal, self.ports["o"].handleEvent)]
        
        return []


###############################################################################
class Not(Unit):
    """a class that implements not gate"""
    def __init__(self, name, hostUnitRef, propagationDelay = 1 ):
        super(Not, self).__init__(name, hostUnitRef)
        self._delay = propagationDelay
        self.ports.addPort(Port("i", self, Port.Direction.IN))
        self.ports.addPort(Port("o", self, Port.Direction.OUT))

    def __str__(self, indent=""):
        return super(Not, self).__str__(indent) + \
          " delay {:2}".format(self._delay)

    def handleEvent(self, event):
        newTime = event.time + self._delay
        outVal = 1

        if self.ports["i"].value == 1:
            outVal = 0

        if outVal != self.ports["o"].value:
            return [Event(newTime, outVal, self.ports["o"].handleEvent)]
        
        return []


###############################################################################
class Probe(Unit):
    """implement a probe functionality. It's attached to a connector
    and print any changes in connector's values during the simulation"""
    
    def __init__(self, name, hostUnitRef ):
        super(Probe, self).__init__(name, hostUnitRef)
        self.ports.addPort(Port("i", self, Port.Direction.IN))

    def handleEvent(self, event): 
        print "Time [{:5}] Probe [{:30}] Val[{:10}]".format(event.time, 
                                                            self.fullPath, 
                                                            event.state)
        return []


def drive(simControl, port, value, time):
        """force the value of a port to be value at time:
        <current_simulation_time> + time. It drives the simulation.
        simControl is a SimulationControl object"""
        print "Schedule [%s] value [%s] time %s" % (port.name, value, time)
        assert port.isConnected(), "port %s of unit %s isn't connected" \
                                                   %(port, port.fullPath)
        simControl.addEventRelativeTime(Event(time, value, port.handleEvent))
        return
