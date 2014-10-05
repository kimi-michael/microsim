#!/bin/env python2.7
# author: Michael Kimi
# date  : Mon Sep  2 14:10:27 2013

"""a ring oscillator module to present a gate level simulation 
capabilities of microSim"""

from model.connector  import Connector
from model.unit       import Unit
from model.primitives import Not, And, Probe


def buildDesign():
    """build ring oscillator"""
    #create all units
    top = Unit("top", None)
    n1  = Not("not1", top)
    n2  = Not("not2", top)
    n3  = Not("not3", top)
    
    #connect all units to form a ring
    c1 = Connector("c1", top, False, n1.ports["o"], n2.ports["i"])
    c2 = Connector("c2", top, False, n2.ports["o"], n3.ports["i"])
    c2 = Connector("c3", top, True,  n3.ports["o"], n1.ports["i"])   # enable print state changes 

    #return created unit
    return top


def main(simControl):
    #do nothing here cause ring osc' should start oscillating by itself
    return

######################################################################
top = buildDesign()
