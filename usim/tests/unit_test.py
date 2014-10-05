#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Nov  6 07:48:31 2013

from datastructures.skiplist.skiplist import SkipList

from simulation_core.simulator import Event
from simulation_core.simulator import EventQueue

######################################################################
def isEqualEvents(e0, e1):
    return e0.time == e1.time and e0.state == e1.state \
      and e0.handler == e1.handler
    

def testSeq(eq, cmpFunc, inSeq, expectedSeq, finalLen=-1, isDebug = False):
    errors = 0
    for elem in inSeq:
        eq.enque(elem) #to skip time checking

    if isDebug: 
        print "DBG print EQ after enque"
        print str(eq)
    
    resultSeq = []
    for i in range(len(expectedSeq)):
        resultSeq.append(eq.deque())

    if isDebug:
        print "DBG print results"
        for r in resultSeq:
            print " %s"%(r)
            
    for result, expected in zip(resultSeq, expectedSeq):
        if cmpFunc(result, expected) == False:
            print " Error: expected [%s] got [%s]"%(expected, result)
            errors += 1

    if finalLen != -1 and finalLen != len(eq):
        errors += 1
        print " Error: len mismatch expected %d got %d"%(finalLen,len(eq))
        print "        event q %s" % eq
    return errors



######################################################################
def testDuplicates(eq):
    errors = 0
    totalErrors = 0

    print "Testing Duplicated events"
    ev0 = Event(1, "a", "a handler")
    ev1 = Event(1, "a", "a handler")

    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev1], [ev0], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev1, ev0], [ev0], 0)

    ev2 = Event(1, "b", "b handler")#set time of the event to be equal to others
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev1, ev2], [ev0, ev2], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev2, ev0, ev1], [ev2, ev0], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev2, ev1], [ev2, ev0], 0)

    ev2 = Event(2, "b", "b handler") #change the time of the event to be bigger
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev1, ev2], [ev0, ev2], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev2, ev0, ev1], [ev0, ev2], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev2, ev1], [ev0, ev2], 0)

    ev2 = Event(0, "b", "b handler") #change the time of the event to be smaller
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev1, ev2], [ev2, ev0], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev2, ev0, ev1], [ev2, ev0], 0)
    errors += testSeq(EventQueue(), isEqualEvents, [ev0, ev2, ev1], [ev2, ev0], 0)
    
    if errors == 0: 
        print " Ok"
        
    return errors
    
    
    
    


######################################################################
def testOrdering(eq):
    errors = 0
    totalErrors = 0
    
    ev0 = Event(1, "a", "a handler")
    ev1 = Event(1, "b", "b handler")

    print "Testing events for the same time"
    errors += testSeq(eq, isEqualEvents, [ev0, ev1], [ev0, ev1])
    errors += testSeq(eq, isEqualEvents, [ev1, ev0], [ev1, ev0])

    if errors == 0:
        print " OK"
        
    print "Testing different times"
    totalErrors += errors
    errors = 0
    
    ev0 = Event(0, "a", "a handler")
    ev1 = Event(1, "b", "b handler")
    ev2 = Event(2, "c", "c handler")

    expevtedSeq = [ev0, ev1, ev2]
    errors += testSeq(eq, isEqualEvents, [ev0, ev1, ev2], expevtedSeq)
    errors += testSeq(eq, isEqualEvents, [ev1, ev0, ev2], expevtedSeq)
    errors += testSeq(eq, isEqualEvents, [ev0, ev2, ev1], expevtedSeq)
    errors += testSeq(eq, isEqualEvents, [ev2, ev1, ev0], expevtedSeq)
    errors += testSeq(eq, isEqualEvents, [ev2, ev0, ev1], expevtedSeq)
    errors += testSeq(eq, isEqualEvents, [ev1, ev2, ev0], expevtedSeq)

    if errors == 0: 
        print " Ok"

    totalErrors += errors
    
    return totalErrors    
    
    

def testEventQ():
    errors = 0

    errors += testOrdering(EventQueue())
    errors += testDuplicates(EventQueue())
    
    
    if errors == 0:
        print "\n All tests passed :]"
    else:
        print "\n Failed %d errors :["%errors
        

#this is the main function:
testEventQ()
