#!/bin/env python2.7
# author: Michael Kimi
# date  : Tue Aug 27 15:13:52 2013

import importlib, os, time, sys
import optparse as opts
import utils
import visualize as viz
import Queue as que
from model.unit                import Unit
from simulation_core.simulator import EventQueue,       \
                                      ExecutionControl, \
                                      ExecutionEngine,  \
                                      Event

__author__ = 'Michael Kimi'
__email__  = 'kimi.michael@gmail.com'
__version__= '0.3'

"""
It's an executable module of the microSim simulator, user should run it
from shell.

Global TODOs:
 1. add logger object. All prints from microSim should be handled only thru
 this object.
 2. add VCD capability to the simulator. i.e. after a simulations user could
 view the VCD file (cause HW guys understand only waves)
 3. split this file to two separate classes
"""

DESIGN_PIC_FILE_NAME = 'top'

class SimulationControl(object):
    """
    It's a controller of the simulation. It will be passed to a 
    test bench and will expose the needed functionality like:
     1. get simulation time. 
     2. set event 
     3. set break point etc.
     
    Note: User should never create this object, it will get an instance of 
    it from microSim
    """    
    def __init__(self, eventQ, execContol):
        self._eventQ = eventQ
        self._execControl = execContol
        return
    
    def getSimulationTime(self):
        """returns the (absolute) current simulation time"""
        return self._eventQ.time
    
    def addEvent(self, event):
        """Add the event to be executed when it's time will arrive. 
        The time in the passed event object is a ABSOLUTE simulation
        time, it must be greater that current simulation time.
        
        Arguments:
         - `event`: should be an Event object
        """
        self._assertEvent(event)
        self._eventQ.enque(event)
        return
    
    def addEventRelativeTime(self, event):
        """Like addEvent but here the event will be scheduled to :
        current_simulation_time + event.time
        
        Arguments:
         - `event`: instance of event object
        """
        self._assertEvent(event)
        time = event.time
        if not self._eventQ.isEmpty:
            time += self._eventQ.time
        self._eventQ.enque(Event(time, event.state, event.handler))
        return 
    
    # helper methods
    def _assertEvent(self, event):
        assert isinstance(event, Event), \
          "Error, %s must be of Event type"% (event)
        assert event.time >= 0, \
          "Error, %d must be non negative" % ( event.time )
        return


class MicroSim(object):
    """
    It exposes simulator's relevant functionality to the user. i.e. load 
    relevant files, set topmost unit names, set test bench main function.
    """
    
    def __init__(self):
        """build the simulator object"""
        self._importedModulesList  = [] 
        self._designTop   = None #: pointer to top unit of the design
        self._designTest  = None #: pointer to main test function
        self._execControl = None
        self._eventQ      = None
        self._execEngine  = None
        self._simControl  = None #: will be passed to designTest function
        self._designPicFileName = DESIGN_PIC_FILE_NAME
        self._outQue = que.Queue()  #: store messages from microSim to any listener
        #TODO: add input queue in future to control the simulation loop
        
    def importModules(self, moduleNameList):
        """Accept a list of modules to be imported into the simulator. Then the
        simulator may access (call) any classes / functions in these modules

        Arguments:
         - `moduleNameList`: list of all module names that should be loaded
        """
        
        print "Info: python search path $PYTHONPATH:"
        for path in os.environ['PYTHONPATH'].split(":"):
            print "\t%s" % path

        for moduleName in moduleNameList:
            print "Info: importing [%s] module" %(moduleName)
            self._importedModulesList.append(importlib.import_module(moduleName))

    
    def setTopTest(self, functionName):
        """A name of a function withing an imported modules. This function 
        is the main test bench function that will be invoked by the simulator

        Arguments:
         - `functionName`: name of function that drives the design
        """
        self._assertImportedModules()
        isFound = False
        for module in self._importedModulesList:
            try :
                self._designTest =  getattr(module, functionName)
                isFound = True 
                print 'Info: [%s] found in [%s] module' %(functionName, module)
                break
            except AttributeError: 
                pass
        assert isFound , "Error, function %s was not found" % (functionName)
        self._assertDesignTest()
        return
    
    def setTopDesign(self, unitReferenceName):
        """A name of a reference to a topmost unit that's defined in one of the
        loaded files. Note: it's not unit's Name!!!

        Arguments:
         - `unitReferenceName`: name of a reference to a topmost unit. This 
        ref must be of Unit type
        """
        
        self._assertImportedModules()
        isFound = False
        
        for module in self._importedModulesList: #search in all modules
            try :
                self._designTop = getattr(module, unitReferenceName)
                isFound = True 
                print 'Info: [%s] found in [%s] module'%( unitReferenceName, 
                                                          module)
                break 
            except AttributeError: 
                pass
            
        assert isFound , "Error, unit [%s] was not found" % (unitReferenceName)
        self._assertDesignTop()
        return 

    def run(self, opts, controlObj):
        """this function run the simulation by invoking design test function.
        controlObj is ExecutionControl object that specify how to run the 
        simulation
        """
        assert isinstance(controlObj, ExecutionControl) , \
          "Error, [%s] must be instance of ExecutionControl object"%(controlObj)

        # assembling simulator from its components:
        self._execControl = controlObj
        self._eventQ      = EventQueue()
        self._execEngine  = ExecutionEngine(self._eventQ, self._execControl)
        
        self._simControl  = SimulationControl(self._eventQ, self._execControl)

        if (opts.enableResolveZero) :
            print "Info: resolve 0 time"
            self._resolveZeroTime()
            
        #print "Info: Event Q debug print\n %s" % (self._eventQ)
        print "Info: invoke design test function"
        self._designTest(self._simControl)
        self._execEngine.run()
        print "Info: Done"
        return 

    
    def prettyPrintDesign(self):

        header = ["full path", "type", "num ports", "delay", "value", "host unit"]
        spacing = " "
        stack = [self._designTop, 0]
        
        while stack:
            level, unit = stack.pop(), stack.pop()
            
            print unit.__str__(spacing*1)

            # iterate all subunits
            for subUnit in sorted(unit, reverse=True) : 
                stack.append(subUnit)
                stack.append(level+1)
        return


    def dumpHierachies(self, fileName):
        fileFullPath = viz.to_gif(fileName, self._designTop)
        self._outQue.put(("design_pic_update", fileFullPath))

    def getMessage(self, block=True, timeout=None):
        return self._outQue.get(block, timeout)

    def isEmpty(self):
        return self._outQue.empty()

    ############################################################################
    def _resolveZeroTime(self):
        """It traverses all units in the design, starting from the top and
        invoke the event handler at time 0 to resolve all outputs of these
        units"""
        spacing = " "
        stack = [self._designTop, 0]
        while stack:
            level, unit = (stack.pop(), stack.pop())
            res = spacing + level*spacing + " {} - {}".format(unit.typeName,
                                                              unit.name)
            #skip all non units objects
            if not isinstance(unit, Unit): continue
            
            #create event @ time=0 for all input ports of a unit
            for port in unit.ports.iterInputPorts():
                res += "\n" + spacing + level*spacing + "  {}".format(port)
                e = Event(0, port.value, port.handleEvent)
                self._eventQ.enque(e)

            # iterate all subunits
            for subUnit in sorted(unit, reverse=True) : 
                stack.append(subUnit)
                stack.append(level+1)
                
            print res
        return

    ## assertion methods #######################################################
    def _assertImportedModules(self):
        """check if imported modules are set"""
        assert self._importedModulesList is not None , \
          "Error, 'imported modules' must be not None"

        assert len(self._importedModulesList) > 0 , \
            "Error, list of imported modules is empty, " \
            "consider checking invocation command"
        
    def _assertDesignTop(self):
        assert self._designTop is not None, \
          "Error, 'design top' must be not None" %( self._designTop )
        
        assert isinstance(self._designTop, Unit), \
          "Error, [%s] must be instance of Unit" %( self._designTop )
          
    def _assertDesignTest(self):
        assert self._designTest is not None, \
          "Error, 'design test' must be not None" %( self._designTop )
        assert hasattr(self._designTest, '__call__'), \
          "Error, %s must be callable function" %( self._designTest )


###############################################################################
###############################################################################
###############################################################################

def _getFooter():
    return "\nThanks for flying with microSim %s\n\tfor any issues contact %s"%\
        (__version__, __email__)

def _parseCommandLine(argsList):
    parser = opts.OptionParser(usage="%prog DESIGN_OPITONS"\
                                   " [EXECUTION_CONTORL_OPTIONS]",
                                   version="%prog " + "%s" % (__version__))
    #designGroup
    designGroup = opts.OptionGroup(
        parser, 
        title = "Design option group - MANDATORY", 
        description='All options related to design files')
    
    parser.add_option_group(designGroup)
    
    designGroup.add_option(
        "--module",
        dest="moduleList",
        action="append",
        default=[],
        metavar="MODULE_NAME",
        help='a name of module to import. This opt may appear more than ones.'\
             ' Note: MANDATORY OPTION')

    designGroup.add_option(
        "--top",
        dest="topRefName",
        default='top',
        metavar="TOP_REFERENCE_NAME",
        help='a name of top unit in one the imported modules')
    
    designGroup.add_option(
        "--test",
        dest="testFuncName",
        default='test',
        metavar="TEST_FUNCTION_NAME",
        help='a name of test function to invoke must be in one '
             'the imported modules')

    # execGroup
    execGroup = opts.OptionGroup(
        parser, 
        title = "Execution control option group - optional", 
        description='All options related to execution control')

    parser.add_option_group(execGroup)

    execGroup.add_option(
        "-f", "--runForever",
        dest="runForever",
        action="store_true",
        default=False,
        help="simulator will run forever or until simulaiton's end. "
        "This is SET by default")

    execGroup.add_option(
        "-u", "--runUntilTick",
        dest="runUntilTick",
        type='float',
        default=-1,
        metavar="TICK",
        help='simulator will run until TICK time. '
        'TICK is non negative int or float')

    execGroup.add_option(
        "-n", "--runNumberOfSteps",
        dest="runSteps",
        type='int',
        default=-1,
        metavar="NUMBER",
        help='simulator will process NUMBER steps and then stop. '
        'NUMBER is non negative int')

    execGroup.add_option(
        "--resolveZeroTime",
        dest="enableResolveZero",
        action="store_true",
        default=False,
        help='Simulator will perform zero time resolution. i.e. simulator will '
        'invoke the event-handler of each input port of every unit before '
        'invoking the TEST_FUNCTION_NAME function')

    #TODO: add interactive debug mode. i.e. let the user choose how he wanna
    # run the simulations and then wait for input from user
    
    options, arguments = parser.parse_args(argsList)
    if len(argsList) == 1: 
        parser.print_usage()
        print "For more help invoke with -h or --help flag"
        sys.exit()
        
    return options, arguments


def _execContorlFromInput(opts):
    """will create and return execution control object from user's options"""

    assert opts.runSteps < 0 or opts.runUntilTick < 0,\
      "Error: runUntilTick & runNumberOfSteps must be mutual exclusive"

    if opts.runForever == True and opts.runSteps >= 0:
        raise ValueError("Error, runForever & runNumberOfSteps "
                         "opts must be mutual exclusive")

    if opts.runForever == True and opts.runUntilTick >= 0:
        raise ValueError("Error, runForever & runUntilTick "
                         "opts must be mutual exclusive")
    
    execObj = ExecutionControl()
    if (opts.runUntilTick < 0 and opts.runSteps < 0):
        #if user didn't choose run (steps or until) => run forever
        execObj.runForever()
    elif opts.runUntilTick >= 0 and opts.runSteps < 0: 
        execObj.runUntilTick(opts.runUntilTick)
    elif opts.runUntilTick < 0 and opts.runSteps >= 0:
        execObj.runNumberOfSteps(opts.runSteps)
    else:
        raise ValueError("Error unsupported combination of execution "
                         "control flags")
    return execObj


def _printOptsArgs(opts, args):
    print "Options  : %s"%(opts)
    print "Arguments: %s"%(args)


def report(line):
    """write the line enclosed in comment box"""

    height, width = utils.getTerminalSize()
    separatorStr = width*"#"
    formatStr = "## %s %s"%(line, (width - len(line) - 4)*"#")
    print "%s\n%s\n%s"%(separatorStr, formatStr, separatorStr)
    return


def getMessage(block=True, timeout=None):
    global uSim
    if uSim is None:
        return None
    return uSim.getMessage(block, timeout)


def isEmpty():
    global uSim
    if uSim is None:
        return True
    return uSim.empty()


def main(argsList):
    global uSim
    opts, args = _parseCommandLine(argsList)
    _printOptsArgs(opts,args)
    uSim = MicroSim()
    
    report("Importing Design")
    uSim.importModules(opts.moduleList)
    uSim.setTopDesign(opts.topRefName)
    uSim.setTopTest(opts.testFuncName)
    
    report("Loaded Design")
    uSim.prettyPrintDesign()
    uSim.dumpHierachies(DESIGN_PIC_FILE_NAME)
    #TODO: enque here a message into communication queue

    report("Starting simulation")
    uSim.run(opts, _execContorlFromInput(opts))

uSim = None

if __name__ == '__main__':
    t0 = time.time()
    main(sys.argv)
    t1 = time.time()
    print _getFooter()
    print "\nTotal execution time: %ss" % ( int(t1-t0) )


