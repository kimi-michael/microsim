# Introduction #

When developing a complex hardware system an architect has many ways to define system’s components and each system’s arrangement will derive a different system’s performance. It’s necessary to be able to simulate the performance of a given system’s arrangement and refine it until certain performance goals are reached.
A simulator has to provide flexible abstractions to allow rapid development & modification of the simulated model (system’s arrangement). Additionally the simulator has to be fast in order to support real life scenarios (i.e. simulate many of millions of clock cycles).
uSim (pronounced: “micro sim”) is a hi-level general purpose simulator that allows rapid performance modeling.

# Details #

## uSim abstractions : ##

### a. Black box (BB): ###
> A BB is an abstraction commonly used in engineering to reduce the complexity of systems. It is a basic simulatable unit in uSim. A BB is defined by its inputs, outputs and the transfer characteristics.

### b. Ports: ###
> Each BB may have multiple input and output ports.

### c. Connectors: ###
> A connector connects between ports. It must have 1 source port (driver) and any number of destination ports. A connector may have 0 or positive propagation delay.

### d. Event: ###
> It holds a time when an event should be dispatched, a state that should be applied to a given object (targeted by this event) and event\_hadler function pointer that changes the internal state of a targeted object and generates series of following events as a result (series may be empty)

Black boxes, Ports and Connectors all are simulatable objects. They have an event handler function pointer that is called each time there’s event on a given object for current simulation time.

**Example:**

Let’s take an example of CAM (content addressable memory) one may think of it as some sort of hash table.
CAM with `N` elements of type `T` will usually have the following interface:
  1. `hit_index_vector[N] lookup(T data);`
> > `hit_index_vector[i] == True` only if data equals `CAM_DATA_ARRAY[i]`, for `i` from `0` to `N-1`. i.e. `hit_index_vector` tells us which entries in `CAM_DATA_ARRAY` are holding the given data.
  1. `void update(int index, T data);`
> > Write the data into `CAM_DATA_ARRAY[index]`

![http://microsim.googlecode.com/svn/trunk/docs/pics/cam-example.jpg](http://microsim.googlecode.com/svn/trunk/docs/pics/cam-example.jpg)

When there is an incoming event time=t<sub>0</sub> on lookup port handle\_lookup function will be called. It will search the `CAM_DATA_ARRAY` for a given data and construct the hit vector signal. Then it will schedule an event on `hit_index_vector` port (with the constructed hit vector as a state) for time t<sub>0</sub> + t<sub>lookup</sub>. When t<sub>lookup</sub> is the time takes to CAM to perform a lookup that affects system’s performance.

# uSim structure: #
## uSim consist of the following parts: ##

![http://microsim.googlecode.com/svn/trunk/docs/pics/structure.png](http://microsim.googlecode.com/svn/trunk/docs/pics/structure.png)

### 1. An arbitrary simulated model ###

> It’s written by the developer/architect and usually include a test bench that is driving model’s inputs and monitor its outputs.

### 2. Event Queue (EQ) ###
> EQ stores all events that aren't dispatched yet, sorted by dispatch time. Event with the smallest time value will be located at the top of the queue. EQ is further internally divided into time frames (frames). A frame is holding all events scheduled for the same simulation time. There are two event pools in each frame ‘now’, ‘later’.  Fetched events from a frame are always pulled from the ‘now’ queue. When ‘now’ queue is empty, we swap ‘now’ and ‘later’ queues and continue to drain ‘now’ queue. When both queues are empty the frame is released and the next frame become active. At this point simulator’s time is (implicitly) advanced (from t<sub>j</sub> to t<sub>j+1</sub>). Events may arrive in arbitrary order, they are inserted into appropriate frames into ‘now’ or ‘later’ queues according to event’s type. Using ‘now’ and ‘later’ queues developer can implement “non-blocking-assignment” (`<=`) behavior or postpone the evaluation of some output port until all inputs are valid (has arrived).

![http://microsim.googlecode.com/svn/trunk/docs/pics/event-queue.png](http://microsim.googlecode.com/svn/trunk/docs/pics/event-queue.png)

The event queue is implemented using skip-list, which is a probabilistic data structure implemented by multi-level linked list. Skip list shows good performance as event queue data structure in simulators, cause fetch of topmost element is done at O(1) complexity. While search, insertion and deletion of an event has O(log(n)) complexity. When n is the number of elements in the list.

### 3. Execution engine (simulation engine) ###
> It implements the following algorithm:

```
while event_queue not empty:
  e = event_queue.get_topmost_event()
  events_list = e.event_handler(e) //call event handler with event e as argument
  event_queue.enque(events_list)
```
### 4.Simulation speedup (future extension). ###
> It is vital for a simulator to be able to run the simulation fast when model become big (more detailed) e.g. simulating a real workloads that last seconds in simulated clock domain. uSim was designed to enable “opportunistic parallelism” [1](1.md) acceleration approach straight forward. The approach’s main assumption is: in large models there are enough independent tasks that can be executed in parallel, to keep models consistency it’s necessary to check for dependencies only when model’s state is changed (at a commit stage). If a dependency was discover (non-common case) one of the tasks should be recomputed based on the outcome of the other task. This approach resembles out of order execution of instructions in modern CPUs when instruction’s commit happens in-order manner to keep consistency.

# Results: #
## A. Basic ring oscillator example (hello world equivalent): ##
Ring oscillator consist of odd number of inverters (not logic gate) connected in a loop. It’s easy to see that this loop will start oscillating forever.

The code of describing ring oscillator is:
```
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

```

uSim GUI:
![http://microsim.googlecode.com/svn/trunk/docs/pics/ring-osc-gui.png](http://microsim.googlecode.com/svn/trunk/docs/pics/ring-osc-gui.png)

In uSim’s GUI a picture of ring oscillator appear on the right side, each output port (o) of an inverter connected to input port (i) of next one. We set the simulation to run 20 ticks. The output:

```
> ./micro_sim_gui.py
Couldn't import dot_parser, loading of dot files will not be possible.
Info: invocation command: microSim --module ring_osc --top top --test main -u 20 --resolveZeroTime
Options  : {'runForever': False, 'runSteps': -1, 'topRefName': 'top', 'runUntilTick': 20.0, 'moduleList': ['ring_osc'], 'testFuncName': 'main', 'enableResolveZero': True}
Arguments: ['microSim']
#################################################################################################################
## Importing Design 
#################################################################################################################
Info: python search path $PYTHONPATH:
        /<some_full_path>/tools/pydot-1.0.28
        /<some_full_path>/projects/uarc_dev/tests
        /<some_full_path>/projects/uarc_dev/bitarray_0_8_1
        /<some_full_path>/projects/uarc_dev
        /<some_full_path>/projects/usim/tests
        /<some_full_path>/projects/usim
Info: importing [ring_osc] module
Info: [top] found in [<module 'ring_osc' from '/<some_full_path>/projects/usim/tests/ring_osc.py'>] module
Info: [main] found in [<module 'ring_osc' from '/<some_full_path>/projects/usim/tests/ring_osc.py'>] module
##################################################################################################################
## Loaded Design 
##################################################################################################################
/top                          , type Unit                ,  0 ports,  3 sub units,  3 connectors
/top/c3                       , type Connector           ,  2 ports, delay  0, value 0, host /top, ports:
 src /top/not3.o                   , type Port                , direction OUT
   0 /top/not1.i                   , type Port                , direction IN
/top/c2                       , type Connector           ,  2 ports, delay  0, value 0, host /top, ports:
 src /top/not2.o                   , type Port                , direction OUT
   0 /top/not3.i                   , type Port                , direction IN
/top/c1                       , type Connector           ,  2 ports, delay  0, value 0, host /top, ports:
 src /top/not1.o                   , type Port                , direction OUT
   0 /top/not2.i                   , type Port                , direction IN
/top/not1                     , type Not                 ,  2 ports,  0 sub units,  0 connectors  delay  1
/top/not2                     , type Not                 ,  2 ports,  0 sub units,  0 connectors  delay  1
/top/not3                     , type Not                 ,  2 ports,  0 sub units,  0 connectors  delay  1
##################################################################################################################
## Starting simulation 
##################################################################################################################
Info: resolve 0 time
  Unit - top
   Not - not1
    /top/not1.i                   , type Port                , direction IN
   Not - not2
    /top/not2.i                   , type Port                , direction IN
   Not - not3
    /top/not3.i                   , type Port                , direction IN
Info: invoke design test function
@    1 /top/c3 1
@    2 /top/c3 0
@    3 /top/c3 1
@    4 /top/c3 0
@    5 /top/c3 1
.
.
.
@   19 /top/c3 1
@   20 /top/c3 0
Info: Done
```

## B. Real example “Translation engine module”: ##
Translation engine is commonly used element in the developed some micro-arch. It caches commonly used addresses and their translation. It has two methods:
### 1. Lookup(address) ###
Lookup return translated address if there is one in a cache. Otherwise it will generate a MISS to be fetched from the memory. If there is already one outstanding MISS for the same address this request will be blocked and nothing will be sent.
### 2. Update(lookup\_address, translated\_address, idx) ###
When the outstanding request returns its translated address will be cashed. Then all waiting transactions for same address will be unblock by generating HIT for each of them. Following diagram present the translation engine module.

![http://microsim.googlecode.com/svn/trunk/docs/pics/translation-engine-gui.png](http://microsim.googlecode.com/svn/trunk/docs/pics/translation-engine-gui.png)

A simple test that sends lookup request on a cold cache and expects a miss presented below:

```
Info: invocation command: microSim --module tb_translation_engine --top dut --test main -f
Options  : {'runForever': True, 'runSteps': -1, 'topRefName': 'dut', 'runUntilTick': -1, 'moduleList': ['tb_translation_engine'], 'testFuncName': 'main', 'enableResolveZero': False}
Arguments: ['microSim']
#################################################################################################################
## Importing Design 
#################################################################################################################
Info: python search path $PYTHONPATH:
        /<some_full_path>/tools/pydot-1.0.28
        /<some_full_path>/projects/uarc_dev/tests
        /<some_full_path>/projects/uarc_dev/bitarray_0_8_1
        /<some_full_path>/projects/uarc_dev
        /<some_full_path>/projects/usim/tests
        /<some_full_path>/projects/usim
Info: importing [tb_translation_engine] module
Info: [dut] found in [<module 'tb_translation_engine' from '/<some_full_path>/projects/uarc_dev/tests/tb_translation_engine.pyc'>] module
Info: [main] found in [<module 'tb_translation_engine' from '/<some_full_path>/projects/uarc_dev/tests/tb_translation_engine.pyc'>] module
#################################################################################################################
## Loaded Design
#################################################################################################################
/dut                          , type TranslationEngine   ,  4 ports,  3 sub units,  8 connectors
/dut/cLookup                  , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut.lookup                   , type Port                , direction IN
   0 /dut/tlb.lookup               , type Port                , direction IN
/dut/cTrkUpdate               , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/trk.update               , type Port                , direction OUT
   0 /dut/tlb.update               , type Port                , direction IN
/dut/cMiss                    , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/trk.miss                 , type Port                , direction OUT
   0 /dut.miss                     , type Port                , direction OUT
/dut/cHit                     , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/mrg.o                    , type Port                , direction OUT
   0 /dut.hit                      , type Port                , direction OUT
/dut/cTrkGenHit               , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/trk.genHits              , type Port                , direction OUT
   0 /dut/mrg.i1                   , type Port                , direction IN
/dut/cUpdate                  , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut.update                   , type Port                , direction IN
   0 /dut/trk.dealloc              , type Port                , direction IN
/dut/cTlbHit                  , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/tlb.hit                  , type Port                , direction OUT
   0 /dut/mrg.i0                   , type Port                , direction IN
/dut/cTlbMiss                 , type Connector           ,  2 ports, delay  0, value 0, host /dut, ports:
 src /dut/tlb.miss                 , type Port                , direction OUT
   0 /dut/trk.lookup               , type Port                , direction IN
/dut/trk                      , type LaunchedTransactions,  5 ports,  0 sub units,  0 connectors , num of entries:  10
/dut/tlb                      , type TranslationTlb      ,  4 ports,  0 sub units,  0 connectors , tlb size:  20
#################################################################################################################
## Starting simulation 
#################################################################################################################
Info: invoke design test function
TB: in prepareForTest() function
@    0 /dut/cLookup <Request: 1, bitarray('1111')>
@    2 /dut/cTlbMiss <Request: 1, bitarray('1111')>
@    4 /dut/cMiss <Request: 1, bitarray('1111')>
TB: @4 listener0missport got <Request: 1, bitarray('1111')>
TB: in prepareForTest() function
Info: Done
```

Additional important result is when the developer writes the model in a certain way (not explained in this doc) he can run the model in 2 ways.
  1. Using uSim simulator to get cycle accurate simulation
  1. Run the code in a traditional way directly on CPU (w/o the simulator). In that case functional equivalent of model will be executed.

To motivate this method I would like to describe, as an example, development flow of HW accelerator for image compression algorithm. Initially programmer develop the codec algorithm in pure software (modelSW) until he obtains desired result. Usually there are multiple ways to map this algorithm to hardware, hence performance accurate model is written (modelPEF). However both models (modelSW and modelPEF) implement the same algorithm and hence they may share the same code. Eventually if you have modelSW you can get modelPEF with less effort than writing it from scratch.




---

author: Michael Kimi