#!/bin/env python2.7 
# author: Michael Kimi
# date  : Aug 2013

"""holds all constructs for id manager"""

from collections                 import deque
from simulation_core.simulator   import Event
from model.unit                  import Unit
from model.port                  import Port

class IndexPool(Unit):
    """Implements a pool of unique ids. Single id is retrieved upon 
    allocation. This id will be inserted back to the manager upon 
    deallocation"""

    def __init__(self, name, hostUnitRef, numberOfIndexs, propagationDelay):
        super(IndexPool, self).__init__(name, hostUnitRef)
        assert numberOfIndexs > 0, "%d must be positive integer"
        self._fifo = deque(range(0, numberOfIndexs))
        self._delay= propagationDelay
        self.ports.addPort(Port("allocReq",    self, Port.Direction.IN))
        self.ports.addPort(Port("allocatedId", self, Port.Direction.OUT))
        self.ports.addPort(Port("deallocId",   self, Port.Direction.IN))
        #set correct handler for deallocation-id event
        self.ports["deallocId"].connect(self._handleDealloc) 
        return

    def allocate( self ):
        """returns allocated index from the pool"""
        return self._fifo.popleft()

    def dealloc( self, index ):
        """deallocate the given index, i.e. put it back to index pool"""
        self._fifo.append(index)
        return 
    
    def __str__(self): 
        return super(IndexPool, self).__str__() + \
          ", free ids: " + str(self._fifo)

    def _handleDealloc(self, event):
        """separate handler for deallocation flow """
        self.dealloc(event.state)
        
    ## override of Simlatable methods #########################################
    def handleEvent(self, event): 
        """it will called to handle events on allocReq port"""
        return [Event(event.time + self._delay, 
                      self.allocate(), 
                      self.ports["allocatedId"].handleEvent)]
    
