#!/bin/env python2.7 
# author: Michael Kimi
# date  : Aug 2013

"""holds all related constructs for implementing launched transaction unit"""
from collections               import deque

from simulation_core.simulator import Event
from model.unit                import Unit
from model.port                import Port
from common                    import Request, Update

class LaunchedTransactions(Unit):
    """
    This unit is tracking all transactions that are sent to the memory and
    yet returned. It's needed in order to prevent sending multiple translation
    requests for the same address.
    NOTE: This class doesn't implement handleEvent func cause it has separate 
    event handler function of each port
    """
    def __init__(self, name, hostUnitRef, propagationDelay, size):
        super(LaunchedTransactions, self).__init__(name, hostUnitRef)
        self._reqAddrMap = dict() # map[<reqAddr>] = <reqId>
        self._reqIdMap   = dict() # map[<reqId>]   = <reqAddr> (inverse table)
        self._mergeIdMap = dict() # map[<reqId>]   = <list of reqIds>
        self._maxSize    = size
        self._delay      = propagationDelay #TODO think carefully about the delays and update 
                                            # all the delays in event handler funcitons!!!

        # create all ports of the unit
        self.ports.addPort(Port("lookup",  self, Port.Direction.IN))
        self.ports.addPort(Port("dealloc", self, Port.Direction.IN))
        self.ports.addPort(Port("genHits", self, Port.Direction.OUT))
        self.ports.addPort(Port("update",  self, Port.Direction.OUT))
        self.ports.addPort(Port("miss",    self, Port.Direction.OUT))
        # set ev-handlers for ports
        self.ports["lookup"].connect(self._handleLookup)
        self.ports["dealloc"].connect(self._handleDealloc)
        return 

    def lookup(self, request):
        """
        Check if there is a request transaction already in-flight for the same
        address (lookup hit). 
        If hit it will bind request.id to in-flight.id so when in-flight
        transaction return we could report 2 hits.
        If miss it will store request.id and request.addr so to filter further 
        requests to translate the same address.
        
        Returns a tuple of (isHit, id):
         - in case of hit isHit = True, id = id-of-former-flying-transaction
         - in case of miss isHit = False, id = request.id
        """
        reqAddr, reqId = request.addr , request.id
        isFound = False
        returnId = reqId
        formatStr = "%s.lookup(%s): {}"%(self.name, request)
        
        if reqAddr in self._reqAddrMap:#we have tran' transaction in-flight

            formerId = self._reqAddrMap[reqAddr]

            #TODO extract as mergeQ en-queue function
            if formerId in self._mergeIdMap: #append reqId to former id's list
                self._mergeIdMap[formerId].append(reqId)
            else: #allocate new entry
                self._mergeIdMap[formerId] = [reqId]
            
            isFound = True
            returnId = formerId
            
            #print formatStr.format("hit, former id: %s" %(formerId))
            
        else: #no in-flight transactions, allocate new entry in all tlbs
            self._reqAddrMap[reqAddr] = reqId
            self._reqIdMap[reqId]     = reqAddr
            #print formatStr.format("miss, alloc new entry")
            
        return isFound, returnId

    
    def dealloc(self, translatedReq):
        """Upon deallocation the following things happen:
        1. Update is generated to update the tlb (reqAddr, tranAddr)
        2. At least one hit (tranAddr, id) is generated to continue translation
           flow.
           
        Multiple hits may be generated when additional trans' request 
        (for same reqAddr) arrived while the 1st one was sent to memory
        Return update event (reqAddr, tranAddr) and list of generated hits
        [(tranAddr, id),...]

        Returns tuple of 3:
         - isHit True if translatedReq.id exist in launched_transactions data 
           structures. False otherwise.
         - Update-Object for updating the translation TLB in case of Hit. None 
           otherwise.
         - List of Request-Objects for hits generation in case of Hit, empty 
           list otherwise.
        """
        
        isHit = False
        resUpdate = None
        tranAddr, tranId = translatedReq.addr, translatedReq.id
        resGeneratedHitList = []

        if tranId in self._reqIdMap:
            isHit = True
            reqAddr = self._reqIdMap[tranId]
            resGeneratedHitList.append(Request(tranAddr, tranId))
        
            #dealloc entries from dicts
            del self._reqIdMap[tranId]
            del self._reqAddrMap[reqAddr]

            #TODO: make a mergeQ deque function from the following 2 steps
            if tranId in self._mergeIdMap:
                #1 generate hits:
                for reqId in self._mergeIdMap[tranId]:
                    resGeneratedHitList.append(Request(tranAddr, reqId))

                #2 remove the entry from mergeQ
                del self._mergeIdMap[tranId]
            
            resUpdate = Update(reqAddr, tranAddr)
        
        return isHit, resUpdate, resGeneratedHitList

    
    def __str__(self, indent=""):
        return super(LaunchedTransactions, self).__str__() + \
          ", num of entries: {:3}".format(self._maxSize)

          
    def _handleLookup(self, event):
        time, reqObj = event.time, event.state
        res = []
        #print "Time : %s %s._handleLookup event: %r"%(event.time, self.name, event)
        if self.lookup(reqObj) == True: #hit
            pass #all data stucts were updated by lookup method
        else: #miss, criate event on a miss port of this unit
            res.append(Event(time + self._delay, 
                             reqObj, 
                             self.ports["miss"].handleEvent))
        return res

    
    def _handleDealloc(self, event):
        time, reqObj = event.time, event.state
        netTime = time + self._delay
        res = []
        isHit, update, generateHitsList = self.dealloc(reqObj)

        if isHit:
            res.append(Event(netTime, update, self.ports["update"].handleEvent))
            #sched generated events one in a cycle 
            for i, reqObj in enumerate(generateHitsList) :
                res.append(Event(newTime + i + 1, reqObj,
                                 self.ports["genHits"].handleEvent))
            
        return res
