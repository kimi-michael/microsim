#!/bin/env python2.7
# author: Michael Kimi
# date  : Jul 2013

"""Defines the simulatable interface. Each object that willing to be
simulated by micro-sim should be implement this class"""

class Simulatable(object):
    """defines a mandatory methods of a simulatable object"""

    ## TODO: think if i really have to pass the whole event to the handler?
    ##  the usual steps in the event handler funtion is always to unpack the 
    ##  event using getPorperties. The handler pointer is useless cause it's
    ##  the pointer to the same funciton ...
    ##  may be i would be wiser to change the signature to :
    ##  handleEvent(self, time, state):
    ## TODO:
    ##  why do need state anyway?! whos state it is ?! i can get state of each 
    ##  connection by quering it's value !!!
    ## TODO: rename that funciton to event handler!!!
    def handleEvent(self, event):
        """This method will be callen by the execution engine of the 
        micro-sim upon a dispatch time of an event. This method should
        calculate and update a state of the implementing object and return
        a list of generated events. return list may be empty"""
        raise Exception("un-implemented-methode")

