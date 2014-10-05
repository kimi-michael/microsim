#!/bin/env python2.7
# author: Michael Kimi
# date  : Aug 2013

"""two ports merge unit"""

from simulation_core.simulator import Event
from model.unit                import Unit
from model.port                import Port

class TwoPortMerge(Unit):
    """
    implement a basic 2 ports merge unit that has the following properties:
     - It has 2 inputs and 1 output. 
     - If only one input is active it's data will be sent to output 
       at time "now" + "unit's delay"
     - If more than one inputs are active in a given cycle the one that wins 
       the arbitration will be forwarded to output and then the 2nd input will
       be forwarded to output.
     - Arbitration is based on round robin policy"""
    def __init__(self, name, hostUnitRef, propagationDelay):
        super(TwoPortMerge, self).__init__(name, hostUnitRef)
        self._delay = propagationDelay
        
        self._lastOutEventTime = 0 #time of last event occurred output port
        self._inPortWin = 0 #points what input port wins arbitration if both valid
        self._i0Event = None #event's arrived to port i0 at this sim cycle
        self._i1Event = None # -------------''------- i1 ----------''------
        
        # create all ports, all with default event handlers
        self.ports.addPort(Port("i0",  self, Port.Direction.IN))
        self.ports.addPort(Port("i1",  self, Port.Direction.IN))
        self.ports.addPort(Port("o",   self, Port.Direction.OUT))

        # set event handlers in input ports:
        self.ports["i0"].connect(self._handleInputPort0Event)
        self.ports["i1"].connect(self._handleInputPort1Event)

    
    def _handleInputPort0Event(self, event):
        """store the incoming event and schedule output update at the end of 
        simulation cycle"""
        self._i0Event = event
        return [Event(event.time, event.state, self._handleEventAtEndOfSimCycle,
                      Event.EventType.Late)]

    def _handleInputPort1Event(self, event):
        """same as for input port0, but for input port1"""
        self._i1Event = event
        return [Event(event.time, event.state, self._handleEventAtEndOfSimCycle,
                      Event.EventType.Late)]


    def _handleEventAtEndOfSimCycle(self, event):
        """it will be called at the end of a simulation cycle. At that time 
        it's guaranteed that both input port events has arrived and updated
        merge's internal members"""
        
        eventsList = []
        outEventTime = 0
        
        #choose output event time based on last output event time, to mimic 
        # 2 to 1 serialization 
        if event.time > self._lastOutEventTime:
            outEventTime = event.time + self._delay
        else:
            outEventTime = self._lastOutEventTime + self._delay

        #create list of events based on number of input valid events
        if self._i0Event is not None and self._i1Event is None :
            eventsList.append(Event(outEventTime, 
                                    self._i0Event.state, 
                                    self.ports["o"].handleEvent))
            
        elif self._i0Event is None and self._i1Event is not None :
            eventsList.append(Event(outEventTime, 
                                    self._i1Event.state, 
                                    self.ports["o"].handleEvent))
            
        elif self._i0Event is not None and self._i1Event is None :
            inPort0Time , inPort1Time = 0, 0

            #both ports have events to output, arb is based on _inPortWin
            if self._inPortWin == 0:
                inPort0Time = outEventTime
                inPort1Time = outEventTime + self._delay
            else:
                inPort0Time = outEventTime + self._delay
                inPort1Time = outEventTime

            # swap the winner to model "round robin" arbitration
            self._inPortWin = 1 - self._inPortWin 
                
            #add both event's 
            eventsList.append(Event(inPort0Time, self._i0Event.state, 
                                    self.ports["o"].handleEvent))
            eventsList.append(Event(inPort1Time, self._i1Event.state, 
                                    self.ports["o"].handleEvent))
        else:
            raise Exception("Error, at least one of the input events should "\
                            "be set")
                            
        return eventsList
