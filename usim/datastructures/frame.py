#!/bin/env python2.7
# author: Michael Kimi
# date  : Tue Nov 26 10:01:12 2013

"""implements a frame that's used by the event Q in microSim project"""

from collections import deque

class Deque(deque):
    """extends the deque and implement some special functionality"""

    def append(self, item):
        """if item exit, it will be removed and new item will be inserted
        to the end. Otherwise item will be appended"""

        foundIndex = -1
        for i, elem in enumerate(self):
            if elem == item:
                foundIndex = i
                break

        if foundIndex >= 0: # item found -> remove it
            del self[foundIndex]

        super(Deque, self).append(item) #add the item to the end

        
################################################################################
################################################################################
################################################################################
class Frame:
    """this is a single element of event-Q"""

    def __init__(self, time, sortFunc = lambda item : True):
        """Ctor:
         - time:     is the frame's time.
         - sortFunc: is a function that will be applied for each item to decide
                     into what Q it will be assigned.
                     sortFunc(item) -> {True, False}
                     True if item should be paced into now Q, False otherwise."""
        self._time = time
        self._nowQue = Deque()
        self._lateQue = Deque()
        self._itemSortFunc = sortFunc


    def append(self, item):
        """will add the item to the frame. In case item is already exist in
        the frame, it will be overwritten"""
        if self._itemSortFunc(item) == True:
            self._nowQue.append(item)
        else:
            self._lateQue.append(item)


    def pop(self):
        """will return the topmost item in the frame"""
        if len(self._nowQue) > 0:
            return self._nowQue.popleft()
        elif len(self._lateQue) > 0:
            #move all items from late-Q to now-Q
            self._reloadNowQue()
            return self._nowQue.popleft()
        raise Exception("Error, cant pop frame %s is empty"%(self))
        pass


    def peek(self):
        """return the topmost event if frame isn't empty. Otherwise will throw
        an exception"""
        if self.isEmpty():
            raise Exception("Error, frame %s is empty" % (self))
        elif len(self._nowQue) > 0:
            return self._nowQue[0]
        else: #late Q isn't empty
            return self._lateQue[0]
        

    def _reloadNowQue(self):
        """when now-Queue is empty and late-Queue isn't this function will
        move all element from late-Queue into now-Queue"""
        self._nowQue = self._lateQue
        self._lateQue = Deque()
        return


    def isEmpty(self):
        """return true if the frame doesn't hold any items"""
        return len(self._nowQue) + len(self._lateQue) == 0 


    def __cmp__(self, other):
        """default compare function. make time based comparison"""
        return cmp(self._time, other._time)


    def getTime(self):
        return self._time


    def __str__(self):
        nowQueItems = Frame._listToString(self._nowQue)
        lateQueItems = Frame._listToString(self._lateQue)
        return "time {} nowQ {} lateQ {}".format(self._time,
                                                  nowQueItems,
                                                  lateQueItems)
    

    def __len__(self):
        return len(self._nowQue) + len(self._lateQue)


    def __iter__(self):
        """iterate all items in a frame"""
        for item in self._nowQue:
            yield item
            
        for item in self._lateQue:
            yield item

        
            
    @staticmethod
    def _listToString(itemsList):
        res = ""
        for item in itemsList:
            res += " %s" %(item)
            
        return "[%s]" % res

