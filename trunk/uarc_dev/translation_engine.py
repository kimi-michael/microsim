#!/bin/env python2.7
# author: Michael Kimi
# date  : Aug 2013

"""holds all constructs for implementing Translation TBL"""

from model.unit                import Unit
from model.primitives          import Probe
from model.port                import Port
from model.connector           import Connector

from launched_transactions import LaunchedTransactions
from translation_tlb       import TranslationTlb
from two_port_merge        import TwoPortMerge

class TranslationEngine(Unit):
    """
    implements TranslationEngine. It is a HW unit that can handle
    a single caching level. Units of this type will be cascade
    one after another to handle all caching levels. (l0, ..., l4 etc)
    """
    def __init__(self, name , hostUnitRef, tlbSize, launchedTransSize):
        super(TranslationEngine, self).__init__(name, hostUnitRef)

        #TODO: put all these units into sub unit map
        # instantiate all sub units:
        self._tlb = TranslationTlb("tlb", self, 2,  tlbSize)
        self._trk = LaunchedTransactions("trk", self, 2, size=launchedTransSize)
        self._mrg = TwoPortMerge("mrg", self, propagationDelay = 1)
        
        #add ports
        self.ports.addPort(Port("hit",    self, Port.Direction.OUT))
        self.ports.addPort(Port("miss",   self, Port.Direction.OUT))
        self.ports.addPort(Port("lookup", self, Port.Direction.IN))
        self.ports.addPort(Port("update", self, Port.Direction.IN))

        enableDump = True
        # connect unit's ports and internal connections 
        Connector("cLookup",    self, enableDump, self.ports["lookup"],      self._tlb.ports["lookup"])
        Connector("cUpdate",    self, enableDump, self.ports["update"],      self._trk.ports["dealloc"])
        Connector("cHit",       self, enableDump, self._mrg.ports["o"],      self.ports["hit"])
        Connector("cMiss",      self, enableDump, self._trk.ports["miss"],   self.ports["miss"])
        Connector("cTlbHit",    self, enableDump, self._tlb.ports["hit"],    self._mrg.ports["i0"])
        Connector("cTlbMiss",   self, enableDump, self._tlb.ports["miss"],   self._trk.ports["lookup"])
        Connector("cTrkUpdate", self, enableDump, self._trk.ports["update"], self._tlb.ports["update"])
        Connector("cTrkGenHit", self, enableDump, self._trk.ports["genHits"], self._mrg.ports["i1"])
        
    
    def lookup(self, request):
        """Does a lookup in internal data structures. 

        Returns a tuple of the form (isHit, result).
        isHit is Boolean that is True in case of hit, False otherwise.
        
        In case of hit:
         - result is a Request-Object that holds translated address and 
           request.id

        In case of miss: 
         - On 1st miss result will hold the address of provided request.
         - On non 1st miss None will be returned. Cause there is at least
           one translation request for the same address and this request
           will be en-queued in launched transactions queue"""

        resRequest = None
        resLookup  = False
        
        isHit, translatedAddress = self._tlb.lookup(request)

        if isHit: 
            resLookup = True
            resRequest = Request(translatedAddress, request.id)

        else: #miss flow bellow:
            
            resLookup  = False
            isHit, resId = self._trk.lookup(request)
            
            if isHit : #we've already flying transaction to same address
                resRequest = None
            else: # this is a first miss on that address => send miss
                resRequest = request

        return resLookup, resRequest

    
    def update(self, translatedReq):
        """Updates internal tlbs to hold the translated address. 

        Returns: tuple of 2 elements (isHit, hitsList)
         - isHit is true if translatedReq is being trucked by this engine.
         - hitsList is non-empty list when isHit==True. This list of generated
           hits i.e. request-objects. This list will have at least one element
           (the one with same id as update.id).
           In case when additional transaction have arrived to translate the
           address that's already in-flight, additional request-objects will be
           added to returned list.
        """

        isHit, update, hitsList = self._trk.dealloc(translatedReq)

        if isHit == True:
            self._tlb.update(update) #send the update to tlb
            
        return isHit, hitsList

    
