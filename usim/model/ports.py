#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Oct 30 16:55:09 2013

"""hold representation of port's container object in this project"""

from interfaces.hostable import Hostable
from model.port import Port

class Ports(object):
    """Defines the functionality of port's container object. It implements
    iterators, getters/setters and similar functions. Will be used by objects
    that have multiple ports"""

    def __init__(self, keyFunc):
        """create ports object
         - keyFunc is function that will be applied to every port element 
         in order to store it in ports structure"""
        self._portMap = dict() # map[<portName>] = <portObject>
        self._keyOf = keyFunc

    def __str__(self, indent=""):
        res = ""
        for i, port in enumerate(self._portMap.values()):
            res += "\n" + indent + "{:3} {}".format(i, port)
        return res
    
    def _assertPort(self, port):
        assert isinstance(port, Port), \
          "Error, %s must be instance of Port class" % (port)
        return 
    
    def addPort(self, port):
        """note: function doesn't set port's reference to self"""
        self._assertPort(port)
        key = self._keyOf(port)
        if key in self._portMap:
            print "Warning, %s already exist override %s with %s"\
              %(key, self._portMap[key].fullPath, port.fullPath)
        self._portMap[key] = port

    def getPort(self, portKey):
        return self.__getitem__(portKey)

    ## static variables to define ports storage ###############################

    #will store all ports by name, i.e. ports keys will be a name of the object
    storeByName = Hostable._getName
    
    #will store all ports by full path, i.e. ports keys will be a full path
    # of the port
    storeByFullPath = Hostable._getFullPath

    ## Emulating container types: #############################################
    def __len__(self):
        return len(self._portMap)

    def __getitem__(self, portKey):
        return self._portMap[portKey]

    def __setitem__(self, portKey, portObj):
        self.addPort(portObj)

    def __delitem__(self, portKey):
        del(self._portMap[portKey])

    def __iter__(self):
        return self._portMap.values().__iter__()

    def __contains__(self, port):
        return self._portMap.__contains__(port.name)

    ## some useful iterators: #################################################
    def _iter(self, accecptFunc):
        """will return all ports that obey accecptFunc(port) == True"""
        for port in self._portMap.values():
            if accecptFunc(port): 
                yield port

    def iterInputPorts(self):
        return self._iter(lambda p: p.direction == Port.Direction.IN)

    def iterOutputPorts(self):
        return self._iter(lambda p: p.direction == Port.Direction.OUT)
