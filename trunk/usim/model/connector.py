#!/bin/env python2.7 
# author: Michael Kimi
# date  : Dec 2012

"""defines connector in micro-Sim project"""

import utils
from interfaces.hostable       import Hostable
from interfaces.simulatable    import Simulatable
from simulation_core.simulator import Event
from model.ports               import Ports
from model.primitives          import Probe
import print_formats as pf


class Connector(Hostable, Simulatable):
    """Define a connector that can connect source port to multiple 
    destination ports. Note: this class is Simulatable"""

    #some static constants:
    DEFAULT_INIT_VAL          = 0
    DEFAULT_PROPAGATION_DELAY = 0

    
    def __init__(self, name, unitRef, enableDump, srcPort, *destPorts):
        """ctor receive variable number of destPorts where # of destPorts must
        be at least 1.
         - unitRef is a pointer to a hosting unit of given connector"""
        
        assert len(destPorts) > 0, \
          "{} must have at least 1 destPorts not {}".format(destPorts,
                                                            len(destPorts))
        self._name = name
        self._hostRef = unitRef
        self._value = Connector.DEFAULT_INIT_VAL
        self._delay = Connector.DEFAULT_PROPAGATION_DELAY
        self._enableDump = enableDump
        self._destPorts = Ports(Ports.storeByFullPath)
        self._srcPort = srcPort
        self._srcPort.connect(self.handleEvent)
        
        #TODO: think of a good reason why do I need to store connectors ref unit?!
        #  it disable the flexibility of connecting any two arbitrate ports 
        #  regardless of their hierarchy locations (cause in that case what unitRef
        #  should point to?!)
        if unitRef is not None: unitRef.addConnector(self)
        
        for port in destPorts: #add destination ports
            self._destPorts.addPort(port)
            #port assumed to be properly connected (using port.connect(x) func)
            
        return
    
    def __str__(self, indent=""):
        srcPortFmt= "\n%ssrc {}"%(indent)
        formatStr = "{}, {:%d} ports, delay {:%d}, value {}, host {}, ports: %s {}"\
          %(pf.FORMAT_PORTS, pf.FORMAT_DELAY, srcPortFmt)
        return formatStr.format( \
            super(Connector, self).__str__(indent),
            len(self._destPorts) + 1, #+1 is for srcPort
            self._delay,
            self._value,
            self._hostRef.fullPath,
            self._srcPort,
            self._destPorts.__str__(indent))

    @property
    def srcPort(self):
        return self._srcPort

    
    def _getSimulationOrderDestPortsList(self):
        """This function returns a list of ports when Probe ports precede any 
        other port. It's needed to call event handler of Probes prior to other
        ports i.e. to resolve rise conditions in favor of probes. Mainly for
        convenience"""
        portsList = []
        
        acceptFunc0 = lambda port: isinstance(port.host, Probe)
        acceptFunc1 = lambda port: not isinstance(port.host, Probe)
        
        for port in self._destPorts._iter(acceptFunc0):
            portsList.append(port)
            
        for port in self._destPorts._iter(acceptFunc1):
            portsList.append(port)

        return portsList
            
    
    def getDestPortIter(self): 
        return self._destPorts.__iter__()

    
    def addConnection(self, destPort):
        assert destPort.direction == Port.Direction.IN, \
          "{} port must be input port".format(destPort.fullPath)
        self._destPorts.addPort(destPort)
        destPort.srcConnector = self

        
    #################################################
    def _set_value(self, newVal):
        self._value = newVal
        return

    
    def _get_value(self):
        return self._value

    
    value = property(_get_value, _set_value)
    
    #################################################
    def _set_delay(self, delay):
        self._delay = delay
        return
    
    def _get_delay(self):
        return self._delay
    
    delay = property(_get_delay, _set_delay)
    
    #################################################
    def handleEvent(self, event):
        newVal = event.state
        newTime = event.time + self._delay
        eventList = []
        portsList = self._getSimulationOrderDestPortsList()
        
        for destPort in portsList:
            eventList.append(Event(newTime, newVal, destPort.handleEvent))
            
        if self._enableDump:
            print "@{:5} {} {}".format(newTime, self.fullPath, repr(newVal))

        self._value = newVal #update self sate
        return eventList
    
