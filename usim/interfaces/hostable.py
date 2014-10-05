#!/bin/env python2.7
# author: Michael Kimi
# date  : Aug 2013

"""Pure abstract class of a unit that has a name and may be a subunit
of some other unit"""

import print_formats as pf

class Hostable(object):
    """defines all methods of unit that my be hosted by some other unit"""

    @property
    def name(self): 
        """return a name of a unit"""
        return self._name
    
    def _getName(self): 
        """to be used when need to extract key of some hostable"""
        return self._name
    
    def _set_host(self, hostRef):
        """In general case this functionality is problematic and isn't 
        needed thus I will disable it. If it's needed one should remove a 
        hostable element from current hosing unit list and add in to a new
        host unit list. """
        raise Exception("un supported operation")
    
    def _get_host(self):
        """returns a pointer to a hosting unit (parent if you want)"""
        return self._hostRef
    
    host = property(_get_host, _set_host)

    @property
    def fullPath(self):
        """return the full path string of a unit"""
        unit, nameStack, delim = self, [], "/"
        while unit: 
            nameStack.append(unit._name)
            unit = unit._hostRef
        path = delim + nameStack.pop()
        while nameStack:
            path += delim + nameStack.pop()
        return path

    def _getFullPath(self):
        """has the same functionality as _getName"""
        return self.fullPath
    
    @property
    def typeName(self):
        """return class name of self object"""
        return type(self).__name__ 

    def __str__(self, indent=""):
        formatStr = "{:%d}, type {:%d}" % (pf.FORMAT_FULLPATH, pf.FORMAT_TYPE)
        return formatStr.format(self.fullPath, self.typeName)
