#!/bin/env python2.7
# author: Michael Kimi
# date  : Jul 2013

"""this module holds a unit which is a base class for every unit that 
microSim can simulate"""

from interfaces.hostable    import Hostable
from interfaces.simulatable import Simulatable

from simulation_core.simulator import Event
from model.port                import Port
from model.ports               import Ports
import print_formats as pf

class Unit( Hostable, Simulatable ):
    """This is a base class for every (RTL) unit. Defines common behavior for
    such a unit"""

    
    def __init__(self, name, hostUnitRef):
        super(Unit, self).__init__() # call the super classes
        self._name = name
        self._hostRef = hostUnitRef
        self._ports = Ports(Ports.storeByName)
        self._subUnitMap = dict() # map[ <unitName> ] = <unitObj>
        self._connectorMap = dict() # map[<connectorName>] = <connetorObj>
        
        if hostUnitRef is not None:
            hostUnitRef.addSubUnit(self)
        return

    
    def __iter__(self):
        """iterate over all sub units"""
        for unit in self._subUnitMap.values(): 
            yield unit

            
    def __str__(self, indent=""):
        formatStr = ", {:%d} ports, {:%d} sub units, {:%d} connectors {}"\
          %(pf.FORMAT_PORTS, pf.FORMAT_SUB_UNITS, pf.FORMAT_CONNECTORS)
        return super(Unit, self).__str__(indent) + \
            formatStr.format( len(self._ports), 
                              len(self._subUnitMap.keys()),
                              len(self._connectorMap.keys()), 
                              self._connectionsToString(indent))

    
    def _connectionsToString(self, indent):
        res = ""
        for connector in self._connectorMap.values():
            res += "\n{}".format(connector.__str__(indent))
        return res

    
    @property
    def ports(self): 
        """return all ports of current unit, mainly for making connections"""
        return self._ports

    @property
    def subUnit(self):
        """returns all sub units map"""
        return self._subUnitMap
        
    def addConnector(self, connector):
        if connector is None:
            raise Exception("Error can't add null connector to %s"\
                            % (self.fullPath))
        if connector.name in self._connectorMap:
            print "Warning: connector with name %s already exist in %s"\
                %(connector.name, self)
            print " overwrite %s with %s" %( self._connectorMap[connector.name],
                                             connector)
        self._connectorMap[connector.name] = connector
        return

    
    def iterConnectors(self):
        for connector in self._connectorMap.values():
            yield connector
            

    def addSubUnit(self, unit):
        if unit is None:
            raise Exception("Can't add None sub unit to %s"%(self))
        
        if unit._name in self._subUnitMap:
            print "Warning: subunit %s exist in %s unit, override with %s"\
              %(unit._name, self, unit)
              
        self._subUnitMap[unit._name] = unit
        unit._hostRef = self
        return

    
    ## override of Simulatable methods #########################################
    def handleEvent(self, event):
        raise Exception("unimplemented method")

