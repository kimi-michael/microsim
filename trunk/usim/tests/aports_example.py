#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Jul 16 20:45:02 2014

"""
Here i will show how to implement 'A Port' based model on top of uSim.
Below I will model an ALU with ports as shown in example Fig5 in
'A-Port Networks: Preserving the Timed Behavior of Synchronous Systems for
Modeling on FPGAs' paper
"""

from simulation_core.simulator import Event
from model.unit import Unit
from model.port import Port
from model.connector  import Connector
from model.primitives import Probe, drive
from utils import Enum

OPCODE = Enum(['ARITH', 'MUL', 'DIV'])
FUNCT  = Enum(['ADD', 'SUB'])

class Alu(Unit):
    """integer ALU unit model"""

    def __init__(self, name, hostUnitRef):
        super(Alu, self).__init__(name, hostUnitRef)
        # internal state tracking
        self._opStartTime = 0
        self._opDuration = 0
        #create the ports:
        self.ports.addPort(Port("in_port",    self, Port.Direction.IN))
        self.ports.addPort(Port("arith_port", self, Port.Direction.OUT))
        self.ports.addPort(Port("mul_port",   self, Port.Direction.OUT))
        self.ports.addPort(Port("div_port",   self, Port.Direction.OUT))
        #connect in_port to event handler
        self.ports["in_port"].connect(self._handleAluOperations)


    def _handleAluOperations(self, event):
        time, aluInst = event.time, event.state
        assert self.notBusy(time), "Error, alu is still working on last request" 

        self._opStartTime = time
        res = aluInst.calcRes()
        outEvent = None
        
        if aluInst.opcode == OPCODE.ARITH:
            outEvent = Event(time + 2, res, self.ports["arith_port"].handleEvent)
            self._opDuration = 2
        elif aluInst.opcode == OPCODE.MUL: 
            outEvent = Event(time + 4, res, self.ports["mul_port"].handleEvent)
            self._opDuration = 4
        elif aluInst.opcode == OPCODE.DIV:
            duration = aluInst.divTime()
            self._opDuration = duration
            outEvent = Event(time + duration, res, self.ports["div_port"].handleEvent)
        else:
            raise Exception ("non supported instruction %s" % aluInst)
        
        return [outEvent]

    def notBusy(self, time):
        return (time >= self._opStartTime + self._opDuration)
    
class AluInst(object):
    """ALU MIPS style instruction """

    def __init__(self, opcode, operandA, operandB, funct):
        self.opcode = opcode
        self._operandA = operandA
        self._operandB = operandB
        self._funct = funct
       
    def calcRes(self):
        if self.opcode == OPCODE.ARITH:
            if self._funct == FUNCT.ADD:
                return self._operandA + self._operandB
            else:
                return self._operandA - self._operandB
        elif self.opcode == OPCODE.MUL:
            return self._operandA * self._operandB
        else:
            return int(self._operandA) / int(self._operandB)            
           
    def divTime(self):
        assert self.opcode == OPCODE.DIV
        return int(self._operandA) / int(self._operandB)

    def __str__(self):
        return "AluInst: %s %s %s %s" % (self.opcode, self._operandA, 
                                         self._operandB, self._funct)
   
def buildAluDesign():
    top = Unit("top", None)
    alu = Alu("alu", top)
    # probes are for printing the values on alu's output ports 
    Connector("c0", top, False, alu.ports["arith_port"], Probe("arith_probe", top).ports["i"]);
    Connector("c1", top, False, alu.ports["mul_port"],   Probe("mul_probe", top).ports["i"]);
    Connector("c2", top, False, alu.ports["div_port"],   Probe("div_probe", top).ports["i"]);
    return top

def main(simControl):
    global dut
    inPort = dut.subUnit['alu'].ports['in_port']
    
    # schedule arith instruction @ time = 0
    inst = AluInst(OPCODE.ARITH, 2, 2, FUNCT.ADD)
    drive(simControl, inPort, inst, 0)
    
    # schedule mult instruction @ time = 10
    inst = AluInst(OPCODE.MUL, 2, 3, None)
    drive(simControl, inPort, inst, 10)

    # schedule div instruction @ time = 20
    inst = AluInst(OPCODE.DIV, 9, 3, None)
    drive(simControl, inPort, inst, 20)
    
dut = buildAluDesign()
