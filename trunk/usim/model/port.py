#!/bin/env python2.7 
# author: Michael Kimi
# date  : Dec 2012

"""a module that holds port representation"""

from interfaces.hostable    import Hostable
from interfaces.simulatable import Simulatable
from simulation_core.simulator import Event
import utils, types
import print_formats as pf

# Description: port hold a pointer to dest-event-handler function
# that will be called when ports event handler functions will be called
# ports-evnt-handler-flow upon reception of event e:
#   1. update the self-port-value to be e.value
#   2. return new event with params:  dest-event-handler and e.value
class Port(Hostable, Simulatable):
    """
    Represent a single port of simulated object, port may be connected to
    some connectors. There are several port's types: IN, OUT. A single port
    may be connected up to two connectors.
    Note: Port is an instance of Simulatable class i.e. it must implement
    eventHandler function. Port is needed for correct modeling of HW elements.
    
    Using this class in future one may implement connection-rules to 
    automatically connect units one to another.
    
    Expected Usage: 
    Each port have to be connected to some destination-event-handler in order
    to operate correctly.

    Default behavior:
    destination-event-handler will point to hosting unit handleEvent function
    if port's direction is IN (input port).
    """
    
    #static class member
    Direction = utils.Enum(["IN", "OUT"])
    DEFAULT_PORT_VALUE = 0
    
    def __init__(self, name , unitRef, direction):
        """ctor, unitRef is the reference name of unit that has this port"""
        self._name      = name
        self._direction = direction
        self._hostRef   = unitRef #pointer to a unit
        self._value     = Port.DEFAULT_PORT_VALUE
        #will hold ptr to ev_handler of entity connected to this port
        if direction == Port.Direction.IN and unitRef is not None:
            self._destEventHandler = unitRef.handleEvent
        else:
            self._destEventHandler = None

    def __str__(self):
        formatStr = ', direction {:%d}' % (pf.FORMAT_DIRECTION)
        return super(Port, self).__str__() + formatStr.format(self._direction)

    def connect(self, entity):
        """This function set the destination-event-handler of this port
        
        Arguments:
         - `entity`: may be an event-handler-function or Simulatable-object
        """

        destEventHandler = None
        if hasattr(entity, '__call__') : #entity is function
            destEventHandler = entity
        elif isinstance(entity, Simulatable):
            destEventHandler = entity.handleEvent
        else:
            raise Exception("Supported types are 'function' or 'Simulatable' "\
                            "type %s of %s isn't supported"%(type(entity), 
                                                              entity))
        self._destEventHandler = destEventHandler
        return

    def isConnected(self):
        """return True iff the port is driving a destination-event-handler
        """
        return self._destEventHandler is not None


    @property
    def direction(self): 
        return self._direction
    
    @property
    def value(self):
        return self._value
    
    @property
    def fullPath(self):
        """override fullPath for Port class to separate port by '.' (dot)
        in a full path"""
        unit, nameStack, delim = self, [], "/"

        while unit: 
            nameStack.append(unit._name)
            unit = unit._hostRef
            
        path = delim + nameStack.pop()

        while nameStack:
            if len(nameStack) == 1:
                delim = '.'
                
            path += delim + nameStack.pop()
            
        return path


    ## Simulatable methods implementation #####################################
    def handleEvent(self, event):
        """Update the value of this port and return an event on a 
        destination-event-handler function for correct propagation of this event
        """
        self._value = event.state
        
        if self._destEventHandler is None:
            #print "Warning: port %s isn't driving any eventHandler function "\
            #  "event [%s] will be lost" % (self, event)
            return []
        
        return [Event(event.time, event.state, self._destEventHandler)]
    
