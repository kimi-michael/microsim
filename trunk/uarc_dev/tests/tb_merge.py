#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Dec 11 09:35:46 2013

"""Implements unit test to merge unit"""

import unittest
from merge import Merge
from simulation_core.simulator import Event

######################################################################
class MergeDriver(object):
    """implement merge input driver"""

    def __init__(self, simControl , mergeDut, informFunc):
        """ctor. informFunc will be called each drive() call with same
        arguments that were sent to drive(...) function"""
        
        self._merge = mergeDut
        self._simControl = simControl
        self._informFunc = informFunc
        
        assert mergeDut is not None, "dut can't be None"
        assert simControl is not None, "simulation control can't be None"

    def drive(self, portIdx, data):
        """drives the data into a DUT.port[portIdx]"""
        time = self._simControl.getSimulationTime()
        inputPort = self._merge.ports["i%d" % portIdx]
        e = Event(time, data, inputPort.handleEvent)
        self._simControl.addEvent(e)
        self._informFunc((time, portIdx, data))
        

######################################################################
class MergeListener(object):
    """ implements a listener to a merge dut unit"""

    def __init__(self, simControl, mergeDut, informFunc):
        self._merge = mergeDut
        self._simControl = simControl
        self._informFunc = informFunc
        
        assert mergeDut is not None, "dut can't be None"
        assert simControl is not None, "simulation control can't be None"

        mergeDut.ports["o"].connect(self.listener)

    def listener(self, event):
        """listener is sort of event handler, thus it should return a
        list of events"""
        print "TB:@%s arrived event %s" % (event.time, event) 
        informFunction = self._informFunc
        informFunction((event.time, event.state))
        return []


######################################################################
class MergeScoreBoard(object):
    """merge's dut score board. Receives transactions (messages) from
    merge driver and merge listener and implement the testing logic"""

    def __init__(self):
        self._driveDataList = []
        self._listenDataList = []
        return

    def driverInform(self, data):
        """will be passed to a listener so he'll call it every time 
        he wanna inform score board about something"""
        return self._driveDataList.append(data)

    def listenerInform(self, data):
        """same as above but for listener class"""
        return self._listenDataList.append(data)

    def getDriveDataList(self): 
        return self._driveDataList

    def getListenDataList(self): 
        return self._listenDataList
    
######################################################################
class TestMerge(unittest.TestCase):

    def setUp(self):
        global simControl, dut
        self.stageDelay = 1
        self.nofInputPorts = 5
        self.scoreBoard = MergeScoreBoard()
        self.driver = MergeDriver(simControl, dut, self.scoreBoard.driverInform)
        self.listener = MergeListener(simControl, dut, self.scoreBoard.listenerInform)
        self.timeOutFunc = None
        dut = getDut("dut", self.stageDelay, self.nofInputPorts)
        return

    def testOnePortAtATime(self):
        """drive a single message into one port of merge mux"""
        global simControl
        self.driver.drive(0, "data")
        # add timeout event to run checker after 1000 time units 
        timeout_event = Event(1000, "", self.checkerOnePortAtATime)
        simControl.addEvent(timeout_event)
        return

    def checkerOnePortAtATime(self, event):
        """verify that a single message has been received on output port.
        it's an event handler function"""
        driveData = self.scoreBoard.getDriveDataList()
        listeneData = self.scoreBoard.getListenDataList()

        self.assertTrue( len(listeneData) == 1, "expect to get one result")
        dTime, dPort, dData = driveData[0]
        lTime, lData = listeneData[0]

        self.assertEqual( dData, lData, "data expected to be the same"\
                          " send %s != received %s" % (dData, lData))

        self.assertTrue( dTime < lTime, "expect send time %d is prior"\
                         " to accept time %d" % ( dTime, lTime ))
        return []
                          
######################################################################


def getDut(name = "dut", stageDelay=1, nofInputPorts=5):
    return Merge(name, None, stageDelay, nofInputPorts)

def main(simulationControl):
    global simControl
    simControl = simulationControl
    import sys
    sys.argv[1:] = [] # remove all program args so unit test wont confuse
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMerge)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main(verbosity=2)

    
dut = getDut()
