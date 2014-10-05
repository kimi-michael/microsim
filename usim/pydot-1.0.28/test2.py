#!/bin/env python2.7
# author: Michael Kimi
# date  : Tue Jan  7 07:49:22 2014

import pydot
N = pydot.Dot()
N.set_node_defaults(shape='record')

p0 = pydot.Node('node0', label = "<f0> |<f1> G|<f2> ")
p1 = pydot.Node('node1', label = "<f0> |<f1> F|<f2> ")

N.add_node(p0)
N.add_node(p1)

e01 = pydot.Edge('node0:f0', 'node1:f2')

N.add_edge(e01)

N.write_dot('foo.dot')
N.write_png('foo.png')
