#!/bin/env python2.7
# author: Michael Kimi
# date  : Tue Dec 10 14:21:13 2013

"""generic merge unit, based on two_port_merge"""

from two_port_merge import TwoPortMerge
from model.port import Port
from model.unit import Unit


class Merge(Unit):
    """implements multi input port to 1 output port merge unit. this unit is
    based on two_port_merge unit. two_port_merge units are pipelined 
    one after another, when each stage is a single two_port_merge unit"""

    # a ctor will instantiate two_port_merge (denoted by M) in this order
    #
    #      i1   i2   i3        iN
    #      |    |    |         |
    #      V    V    V         V
    # i0-> M -> M -> M -> ...  M -> o
    # 
    def __init__(self, name, hostUnitRef, stageDelay, nofInputPorts):
        super(Merge, self).__init__(name, hostUnitRef)

        assert nofInputPorts > 1,\
            "Number of input ports must be more than 1 not %s" % nofInputPorts

        assert stageDelay >= 0, "Stage delay must be non negative not %s" % stageDelay
          
        self._nofStages = nofInputPorts - 1
        self._mergeStages = []

        #create ports of Merge unit
        self.ports.addPort(Port("o", self, Port.Direction.OUT))
        
        for i in range(nofInputPorts):
            self.ports.addPort(Port("i%d" % i, self, Port.Direction.IN))

        #create and connect all two-port-merge units in pipeline and connect 
        # them to Merge-unit input ports
        for i in range(self._nofStages):
            mergeUnit = TwoPortMerge("mergeStage%d"%i, self, stageDelay)
            self._mergeStages.append(mergeUnit)

            if i == 0:  # connect 1st stage
                self.ports["i0"].connect(mergeUnit.ports["i0"])
                self.ports["i1"].connect(mergeUnit.ports["i1"])
            else:       # connect non 1st stage
                prevUnit = self._mergeStages[i-1]
                
                prevUnit.ports["o"].connect(mergeUnit.ports["i0"])
                self.ports["i%d"%(i+1)].connect(mergeUnit.ports["i1"])

        # connect last stage
        self._mergeStages[-1].ports["o"].connect(self.ports["o"])


