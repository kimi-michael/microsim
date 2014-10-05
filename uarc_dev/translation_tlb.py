#!/bin/env python2.7 
# author: Michael Kimi
# date  : Aug 2013

"""holds all constructs for translation tlb"""

from collections               import deque

from simulation_core.simulator import Event
from model.unit                import Unit
from model.port                import Port

class TranslationTlb(Unit):
    """
    Implements the a translation tlb unit in developed uarch. It holds translations
    of addresses request address -> translated address. It can perform lookup
    of an entry that may generate hit or miss. It also supports update
    (tlb write if you want) that writes a translation entry.
    NOTE: this class doesn't implement handle-Event func cause it has a separate
    event handler for each input port. This func shouldn't be called in anyway
    """
    
    def __init__(self, name, hostUnitRef, propagationDelay, size):
        super(TranslationTlb, self).__init__(name, hostUnitRef)
        self._addressMap = dict() # map[<guest phys addr>] = <host phys addr>
        self._allocatedQ = deque() #manage De/allocation RR policy
        self._maxSize    = size
        self._delay      = propagationDelay
        # create all ports
        self.ports.addPort(Port("update", self, Port.Direction.IN))
        self.ports.addPort(Port("lookup", self, Port.Direction.IN))
        self.ports.addPort(Port("hit",    self, Port.Direction.OUT))
        self.ports.addPort(Port("miss",   self, Port.Direction.OUT))
        # set event handlers for all input ports
        self.ports["update"].connect(self._handleUpdate)
        self.ports["lookup"].connect(self._handleLookup)

    def __str__(self, indent=""):
        return super(TranslationTlb, self).__str__() + \
          ", tlb size: {:3}".format(self._maxSize)
          
    def lookup(self, request):
        """return a tuple of (isHit, hitResult). 
        isHit is a Boolean with is true in case of hit and false in case of 
        miss.
        in case of hit hitResult is HPA if request.addr is cached in the tlb, 
        otherwise hitResult is None"""
        
        if request.addr in self._addressMap:
            return (True, self._addressMap[request.addr])
        else: 
            return (False, None)

        
    def update(self, updateObj):
        """update the tlb with the translation address from update-Obj"""
        #if we've allocated all free entries in tlb
        if len(self._allocatedQ) == self._maxSize:
            #remove the old entries from the tlb (fifo order)
            oldUpdateObj = self._allocatedQ.popleft()
            del self._addressMap[oldUpdateObj.requestAddr]

        reqAddr,tranAddr = updateObj.requestAddr, updateObj.translatedAddr
        
        self._addressMap[reqAddr] = tranAddr
        self._allocatedQ.append(updateObj)

        
    def _handleUpdate( self, event):
        self.update(event.state)
        return []

    def _handleLookup(self, event):
        time, reqObj = event.time, event.state
        isHit, hostPhysAddr = self.lookup(reqObj)
        if isHit : 
            outEvent = Event(time + self._delay, 
                             Request(hostPhysAddr, reqObj.id),
                             self.ports["hit"].handleEvent)
        else: # we have miss, i.e. forward the request to miss port as is
            outEvent = Event(time + self._delay, 
                             reqObj,
                             self.ports["miss"].handleEvent)
        return [outEvent]


