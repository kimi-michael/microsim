#!/bin/env python2.7
# author: Michael Kimi
# date  : Mon Nov 18 09:25:22 2013

"""Implements the functional unit test to translation engine unit"""
import unittest
from translation_engine import TranslationEngine
from bitarray import bitarray
from common import Request, Update


def decimalToBinaryString(integer):
    return bin(integer)[2:]

class TestTranslationEngine(unittest.TestCase):

    def setUp(self):
        """creates the DUT, so all test could run tests on it"""
        self.tlbSize = 20
        self.launchedTransactionsSize = 10
        self.dut = TranslationEngine("dut", None, self.tlbSize, 
                                     self.launchedTransactionsSize)


    ######################################################################
    ## test cases ########################################################
    ######################################################################
    def testLookupOnColdTlb(self):
        """For any lookup request on cold TLB a miss will be generated"""

        for i in range(self.launchedTransactionsSize):
            address = bitarray(decimalToBinaryString(i))
            req     = Request(address, i)
            isHit, result = self.dut.lookup(req)

            #we expect only misses
            self.assertFalse(isHit, "hit reported for %s on clod tlbs"\
                             %( repr(req)))

            self.assertIsNotNone(result, "res #%d is None when expected %s"\
                                 %(i, repr(req)))
            
            self.assertEqual(result.addr, req.addr, 
                "res #%d address doesn't match request address %s!=%s"\
                %(i, result.addr, req.addr))
            


    def testManyLookupsForSameAddress(self):
        """When we have multiple lookups (translation requests) for the same
        address we will obtain translation request only for the 1st request"""
    
    	address = bitarray('1111')
    	req = Request(address, 0)
    	isHit, result = self.dut.lookup(req) #1st req should result in a miss
    	
    	self.assertFalse(isHit, "hit reported for %s" %( repr(req)) )
    	self.assertIsNotNone(result, "expected result 1st lookup is None, "\
                             "not %s" % result)
        self.assertEqual(result.addr, req.addr, "res address doesn't match"\
                         " request address %s!=%s" %(result.addr, req.addr))
    	   
    	for i in range(1, self.launchedTransactionsSize):
    	    req = Request(address, i) 
            # should result in miss, w\ result=None
    	    isHit, result = self.dut.lookup(req)
    	    self.assertFalse(isHit, "hit reported for %d %s" % (i, repr(req)))
    	    self.assertIsNone(result, "request %d %s isn't None as expected"\
                              % (i, repr(result)))

                              
    def testUpdateArrivialToOneReq(self):
        """Arrival of an update on a former lookup request will generate
        only one hit"""

        for i in range(self.tlbSize):
            #create request
            address = bitarray(decimalToBinaryString(i))
            req     = Request(address, i)

            #create update for the request
            transltedAddress = bitarray(address)
            transltedAddress.invert()
            updateReq = Request(transltedAddress, i)
	
            #send a lookup request
            self.dut.lookup(req)
            #send update request w\ translated address
            isHit, hitsList = self.dut.update(updateReq)
            
            self.assertTrue(isHit, "expecting a Hit for a request #%d %s" \
                            %(i, repr(req)))
            self.assertEqual( len(hitsList),  1, "hit list length is %d " \
                              "when 1 is expected" % ( len(hitsList)))
            genHit = hitsList[0]
            self.assertEqual(genHit, updateReq, "reported hit %s differs "\
                             "from update %s" % ( repr(genHit), repr(req)))
                             
	
    def testUpdateArrivialToNonTrackedReq(self):
        """Arrival of an update request on non-tracked request will result
        in a miss"""

        #test on clean dut
        for i in range(40): #can be any random number
            address = bitarray(decimalToBinaryString(i))
            updateReq = Request(address, i)
            isHit, hitsList = self.dut.update(updateReq)

            self.assertFalse(isHit, "expecting miss in req #%d %s" \
                            %(i, repr(updateReq)))

            self.assertEqual( len(hitsList), 0, "hit list for req #%d %s "\
                              "isn't empty, but: %s" %(i, repr(updateReq), 
                                                       hitsList))

        #test: put some req into self.dut and do the same test:
        for i in range(self.launchedTransactionsSize):
            address = bitarray(decimalToBinaryString(i))
            req = Request(address, i)
            self.dut.lookup(req)

        #can be any random number there's nothing special in 40
        for i in range(self.launchedTransactionsSize + 1, 
                       self.launchedTransactionsSize + 40): 
            address = bitarray(decimalToBinaryString(i))
            updateReq = Request(address, i)
            isHit, hitsList = self.dut.update(updateReq)

            self.assertFalse(isHit, "expecting miss in req #%d %s" \
                             %(i, repr(updateReq)))

            self.assertEqual( len(hitsList), 0, "hit list for req #%d %s "\
                              "isn't empty, but: %s" % (i, repr(updateReq), 
                                                        hitsList))


    def testMultipleHitsGeneration(self):
        """check that arrival of an update on a former lookup, that has many
        other pending request to the same address, will generate hits for
        each of pending requests"""

        address = bitarray('1111')
        reqList = []
        expectedResList = []
        translatedAddr  = "translated address"

        #create list of different trans' req for the same address
        for i in range(self.launchedTransactionsSize):
            reqList.append(Request(address, i))
            expectedResList.append(Request(translatedAddr, i))

        #put lookup requests to translate the same address
        for req in reqList:
            self.dut.lookup(req)
            
        #send update for the 1st request:
        updateReq = Request(translatedAddr, 0)
        isHit, hitsList = self.dut.update(updateReq)

        self.assertTrue( isHit, "expecting Hit for update request %s" \
                         %( repr(updateReq) ))
        
        self.assertEqual( len(hitsList), self.launchedTransactionsSize, 
                          "Error, hit list length is %d when %d is expected" \
                          % ( len(hitsList), self.launchedTransactionsSize ))

        for hit, res in zip(hitsList, expectedResList):
            self.assertEqual(hit, res, "hit request %s is different than "\
                             "expected res %s" % ( repr(hit), repr(res)))
    
  
######################################################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
