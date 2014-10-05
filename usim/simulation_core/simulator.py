#!/bin/env python2.7
# author: Michael Kimi
# date  : Jul 2013

###############################################################################
from datastructures.skiplist.skiplist import SkipList
from datastructures.frame import Frame

class EventQueue(object):
    """define the event Q. It can store event and get them by popping from 
    the top"""

    def __init__(self):
        self._eventSortFunc = lambda e : e.eventType == Event.EventType.Now
        self._queue = SkipList(keyFun = Frame.getTime, allowDups = 0)

        
    def enque(self, event):
        """put the given event into the event Q. Throws exception if event has
        negative time"""

        #if e exit in Q in some frame f
        # append e to f
        #else
        # create new frame f with e and add f to Q
        if event.time in self._queue:
            #print "Appending event %s" % event
            self._queue[event.time].append(event)
        else: 
            f = Frame(event.time, self._eventSortFunc)
            f.append(event)
            #print "Adding frame %s" % f
            self._queue.insert(f)
        return
            

    def deque(self):
        """remove the topmost event from the event Q. throws exception if the
        Q is empty"""
        
        if self.isEmpty:
            raise Exception("Error, can't deque cause Q is empty")
        
        currentFrame = self._queue.first()
        resultEvent = currentFrame.pop()
        
        if currentFrame.isEmpty(): #this frame is empty, bring the next one
            self._queue.delete(currentFrame.getTime())

        return resultEvent

    
    @property
    def time(self):
        """returns the time of the top most event in event Q. 
        Returns 0 if Q is empty"""
        if self.isEmpty:
            return 0
        return self._queue.first().peek().time

    
    @property
    def top(self):
        if self.isEmpty:
            raise Exception("Error, can't get top cause event Q is empty")
        return self._queue.first().peek()

    
    @property
    def isEmpty(self):
        return len(self._queue) == 0


    def __len__(self):
        #have to count all events cause sometimes events are merged
        eventCount = 0
        for frame in self._queue:
            eventCount += len(frame)
        return eventCount

    
    def __iter__(self): 
        for frame in self._queue:
            for event in frame:
                yield event

                
    def __str__(self):
        res = "EventQ len: {:3}".format(len(self))
        for i , ev in enumerate(self._queue):
            res += "\n {:3}) {}".format(i, ev)
        return res
    
###############################################################################
import print_formats as pf
from utils import Enum

class Event(object):
    """defined the event object"""

    EventType = Enum(["Now", "Late"])
    """
    Defines a simulation event. It has:
     1. Dispatch time
     2. State that will be updated when the event will be dispatched
     3. Handler function that will update the state of a component
        (for which this event is targeted to). It also will generate new
        events based the state
     3. eventType is defines the scheduling policy. 
        Now - will enque the event into higher priority events in given time slot
        Late - will enque the event into lower priority events in given time slot"""
    def __init__(self, time, state, handler, eventType = EventType.Now):
        self._time = time
        self._state = state
        self._handler = handler
        self._eventType = eventType

    @property 
    def time(self):     
        return self._time
        
    @property 
    def state(self):      
        return self._state
        
    @property 
    def handler(self):    
        return self._handler

    @property
    def eventType(self):
        return self._eventType
        

    def __cmp__(self, other):
        """events are considered equal if they are scheduled for the same time
        and handled with the same handler (sate is ignored in a comparison)"""
        if self._time == other._time and self._handler == other._handler:
            return 0
        elif self._time < other._time:
            return -1
        else:
            return 1

        
    def __str__(self):
        if hasattr(self._handler, '__self__') \
          and hasattr(self._handler.__self__, 'fullPath'):
            handlerFmt = self._handler.__self__.fullPath
        else:
            handlerFmt = str(self._handler)
            
        fStr = "Event time: {:%d} state: {:4} handler: {}"%(pf.FORMAT_TIME)
        return fStr.format(self._time, self._state, handlerFmt)

    
    def getKeyIndex(self):
        return self._time
          
###############################################################################
class ExecutionEngine(object):

    def __init__(self, eventQ, control):
        self._eventQ = eventQ
        self._control = control
        #print "Info: create execution engine object"

    def setControl(self, control):
        """set the control object of the execution engine"""
        self._control = control
        
    def run(self):
        #print "Info: start running the simulation"
        while (not self._eventQ.isEmpty) and \
          self._control.canRun(self._eventQ.top):
            event       = self._eventQ.deque()
            handlerFunc = event.handler
            eventList   = handlerFunc(event) # evaluate the event
            for ev in eventList:
                self._eventQ.enque(ev)
        #print "Info: finish running the simulation"
                
###############################################################################
class ExecutionControl(object):
    """Implements a control logic of the execution engine i.e. It defined
    functionality similar to standard debuggers:
    run-forever,
    run-number-of-ticks,
    step-single-tick,
    stop, stop-at-tick etc
    """
    def __init__(self):
        self._canRun = lambda e: False #default policy is: disable running
        self._stepsCounter = 0 #TODO encapsulate this into some class
        #print "Info: create execution control object"

    def canRun(self, event):
        return self._canRun(event)

    def runUntilTick(self, maxTick):
        self._canRun = lambda event: event.time <= maxTick

    def runForever(self):
        self._canRun = lambda event: True # return always True

    def runNumberOfSteps(self, steps):
        assert steps > 0, "Steps must be positive int not [%d]" % steps
        self._stepsCounter = steps
        self._canRun = self._runSteps

    def _runSteps(self, event):
        if self._stepsCounter > 0:
            self._stepsCounter -= 1
            return True
        else:
            return False

###############################################################################
