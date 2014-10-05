#!/bin/env python2.7 
# author: Michael Kimi
# date  : Nov 2012

"""this module contains all useful utilities, taken from DfxBuilder"""

import os


class Enum(set):
    """implementation of enum type"""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError("[%s] isn't one of elements, expecting: %s"\
                             % (name , self))

                             
def fullpath(path):
    return os.path.abspath(path)


def getTerminalSize():
    """helping function to retrieve the size of console window,
    copied from somewhere else :) """
    height, width = 70, 40
    readData = os.popen('stty size', 'r').read()
    if len(readData) > 0:
        height, width = readData.split()
    return int(height), int(width)

