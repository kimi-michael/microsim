#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Sep 11 08:40:32 2013

"""a test module for a translation engine unit"""

from simulation_core.simulator import Event

from translation_engine        import TranslationEngine
from common                    import Request
from bitarray                  import bitarray

def timeOutHandler(event):
    """this is event handler thus it has to return list of events 
    (may be empty)"""
    global testNofAcceptedEvents, testErrorCnt
    
    if testNofAcceptedEvents > 0 and testErrorCnt == 0:
        print "TB: OK"
    else: 
        pass #print "TB: Error, err cnt %d"%(testErrorCnt) # todo check 

    return []
    
######################################################################
## drive & listen sequences : ########################################
######################################################################

"""This is a unit test module of translation engine (TE). 
It has the following tests:
 - test0 : cold tlbs miss on any address
 - test1 : merging multiple translation requests for same address
 - test2 : a TE.hit is generated when TE.update has arrived for a former 
    TE.miss request
 - test3 : multiple TE.hit-s are generated when we have a 
 """

## test 0 :###########################################################
def drive0(simControl):
    global dut
    address = bitarray("1111")
    req0 = Request(address, 1)
    simControl.addEvent(Event(0, req0, dut.ports["lookup"].handleEvent))
    simControl.addEvent(Event(500, "TIMEOUT", timeOutHandler))
    return 

def listen0MissPortHandler(event):
    global runningTestIndex, testErrorCnt, testNofAcceptedEvents
    time, request = event.time, event.state

    if isinstance(request, Request) and request.addr == bitarray("1111") \
      and request.id == 1:
        print "TB: @%d listener0missport got %s"%(time, repr(request))
        testNofAcceptedEvents += 1
    else: 
        testErrorCnt += 1

    runningTestIndex +=1
    controller()
    return []

def test0Preset(dut): 
    #connect tb listener funciton
    dut.ports["miss"].connect(listen0MissPortHandler)
    
## test 1 :###########################################################
# TODO implement




######################################################################
######################################################################
def main(simulationControl):
    """test main function that exercise the DUT"""
    global simControl, dut
    simControl = simulationControl #init the global var

    controller() 
    return

def controller():
    global simControl, runningTestIndex

    if runningTestIndex > 0:
        reportStatistics()

    prepareForTest()
        
    if runningTestIndex == 0:
        test0Preset(dut)
        drive0(simControl)
    elif runningTestIndex == 1:
        pass #drive1(simControl)
    else:
        print "TB: Done with the tests"

    #TODO: put into other test
    #req1 = Request(address, 2)
    #simControl.addEvent(Event(5, req1, dut.ports["lookup"].handleEvent))
    return 

def prepareForTest():
    """reset all global variables before running the next sequence"""
    global globalErrorCount, testErrorCnt, testNofAcceptedEvents
    globalErrorCount += testErrorCnt
    testErrorCnt = 0
    testNofAcceptedEvents = 0
    print "TB: in prepareForTest() function"

def reportStatistics():
    """report test's statistics after execution"""
    pass


######################################################################
######################################################################
def build():
    top = TranslationEngine("dut", hostUnitRef = None, tlbSize = 20, 
                            launchedTransSize = 10)
    
    return top


dut = build()
testErrorCnt          = 0 #
testNofAcceptedEvents = 0 #count all accepted events from DUT
runningTestIndex      = 0 #index of a runnig test
globalErrorCount      = 0
simControl = None #simulation control object, will be set by main test function
