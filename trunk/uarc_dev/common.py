#!/bin/env python2.7 
# author: Michael Kimi
# date  : Aug 2013

"""will hold all common types of developed uarch"""

from bitarray import bitarray
import print_formats as pf

FORMAT_ADDR      = 6
FORMAT_FILED     = 8
FORMAT_ID        = 3

FORMAT5_STR = "{:%d} {:%d} {:%d}, {:%d} {:%d}" %(pf.FORMAT_TYPE, FORMAT_FILED,
                                                FORMAT_ID, FORMAT_FILED,
                                                FORMAT_ADDR)

class TranslationRequest(object):
    """defines the translation request issued by a IO device"""
    def __init__(self, addressToTranslate, metadata ):
        self._addtToTrans = addressToTranslate
        self._metadata = metadata 

    def __str__(self):
        return FORMAT5_STR.format("TranReq","addrToTran", self._addtToTrans,
                                  "metaData", self._metadata)

###############################################################################
class Request(object):
    """represent the internal request"""

    
    def __init__(self, reqAddr, reqId):
        self._reqAddr = reqAddr
        self._reqId = reqId
        return


    def __str__(self):
        return FORMAT5_STR.format(self.__class__.__name__, 
                                  "id", self.id,
                                  "addr", self.addr)

    def __repr__(self):
        return "<Request: %d, %s>" % (self._reqId, self._reqAddr)


    def __eq__(self, other):
        if other is None: 
            return False
        return self._reqAddr == other._reqAddr and self._reqId == other._reqId


    def __ne__(self, other):
        return not self.__eq__(other)

    
    @property
    def id(self) :   return self._reqId

    @property
    def addr(self) : return self._reqAddr

###############################################################################
class Update(object):
    """represent update command data, internal to Translation Engine"""
    def __init__(self, reqAddr, tranAddr):
        self._reqAddr = reqAddr
        self._tranAddr= tranAddr

    def __str__(self):
        return FORMAT5_STR.format(self.__class__.__name__,
                                  "reqAddr", self.requestAddr,
                                  "tranAddr", self.translatedAddr)
    
    @property
    def requestAddr(self): 
        return self._reqAddr


    @property
    def translatedAddr(self): 
        return self._tranAddr
