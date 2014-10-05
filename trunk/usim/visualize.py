#!/bin/env python2.7
# author: Michael Kimi
# date  : Jan 2014

"""this module handles design visualization, i.e. print to graph"""

import os
from model.connector import Connector
from model.port import Port
from model.unit import Unit
import pydot as dot


def to_gif(file_name, top_unit):
    """write a graph of a top_unit into file_name"""
    g = dot.Dot(graph_type='digraph', rankdir='LR')
    add_nodes(g, top_unit)
    add_edges(g, top_unit)

    g.write_dot(file_name)
    g.write_gif(file_name)
    return os.path.join(os.getcwd(), file_name)


def add_edges(graph, top_unit):
    """add all connections (edges) in top_unit into the graph"""
    add_edges_input_port_to_all(graph, top_unit)
    add_edges_output_port_to_all(graph, top_unit)
    return


def add_edges_output_port_to_all(graph, top_unit):
    """add edges for all subunit's output ports to their destinations"""
    for sub_unit in top_unit:
        for out_port in sub_unit.ports.iterOutputPorts():
            if not out_port.isConnected():
                continue
            destinations = destination_units_of_port(out_port)
            for dest in destinations:
                dest_name = get_destination_name(dest, top_unit, out_port)
                source_name = "%s:%s" % (sub_unit.name, out_port.name)
                graph.add_edge(dot.Edge(source_name, dest_name))
    return


def add_edges_input_port_to_all(graph, top_unit):
    """add edges from input ports of top_unit to all destinations"""
    for input_port in top_unit.ports.iterInputPorts():
        destinations = destination_units_of_port(input_port)
        for dest in destinations:
            dest_name = get_destination_name(dest, top_unit, input_port)
            graph.add_edge(dot.Edge(input_port.name, dest_name))
    return


def get_destination_name(destination, top_unit, port):
    """return a name of a destination that will be used to create an edge in 
    a graph"""
    if isinstance(destination, Port):     # destination is a port
        if destination.host != top_unit:  # port belongs to some unit
            dest_name = '%s:%s' % (destination.host.name, destination.name)
        else:  # port belongs to top_unit
            dest_name = '%s' % destination.name
    elif isinstance(destination, Unit):   # destination is a unit
        if destination == top_unit:       # destination is the hosting unit
            dest_name = '%s' % port.name 
        else:                             # destination is some other unit
            dest_name = '%s' % destination.name
    else:
        print "WARNING: [%s] is unknown instance" % destination
    return dest_name


def add_nodes(graph, top_unit):
    """add dot nodes of a given unit to a graph"""
    add_port_nodes(graph, top_unit, "IN")
    add_port_nodes(graph, top_unit, "OUT")
    add_sub_units_nodes(graph, top_unit)
    return


def add_port_nodes(graph, top_unit, ports_type):
    """add all I/O ports for top_unit to a graph as nodes. ports_type defines
    if adding input or output nodes"""
    
    shape = "house"
    if ports_type == "IN":
        ports_iter = top_unit.ports.iterInputPorts
        orientation = 270
    elif ports_type == "OUT":
        ports_iter = top_unit.ports.iterOutputPorts
        orientation = 90
    else:
        raise ValueError("Error, unsupported type '%s'" % ports_type)

    sub_graph = dot.Subgraph('', rank='same') 
    
    for port in ports_iter():
        name = port.name
        node = dot.Node(name, label=name, shape=shape, orientation=orientation)
        sub_graph.add_node(node)
        
    graph.add_subgraph(sub_graph)
    return


def add_sub_units_nodes(graph, top_unit):
    """add all sub units of top_unit as nodes to the graph"""
    shape = 'record'
    for sub_unit in top_unit:
        name = sub_unit.name
        label = get_unit_label(sub_unit)
        node = dot.Node(name, label=label, shape=shape)
        graph.add_node(node)
    return


def get_unit_label(unit):
    """returns a label of a given unit, based on its ports"""
    input_ports_label = get_ports_label(unit.ports.iterInputPorts)
    output_ports_label = get_ports_label(unit.ports.iterOutputPorts)
    unit_label = "%s" % unit.name

    label = "{"

    if input_ports_label != '':  # add input ports' label
        label += "%s |" % input_ports_label
        
    label += " %s " % unit_label
    
    if output_ports_label != '':  # add output ports' label
        label += "| %s" % output_ports_label
        
    label += "}"
        
    return label


def get_ports_label(ports_iterator):
    """returns port's label using all ports returned by ports_iterator"""
    ports_label = ""
    for i, port in enumerate(ports_iterator()):
        if i == 0:
            ports_label += "<%s>%s " % (port.name, port.name)
        else:
            ports_label += "| <%s>%s " % (port.name, port.name)
            
    if ports_label is not "":
        ports_label = "{ %s }" % ports_label

    return ports_label


def destination_units_of_port(port):
        """return a list of destination units of a given port, if it's connected"""

        if not port.isConnected():
            return []

        dest = port._destEventHandler.__self__

        destination_units_list = []
        if isinstance(dest, Connector):  # dest is a connector
            for destination_port in dest.getDestPortIter():
                destination_units_list.append(destination_port)

        elif isinstance(dest, Port):  # dest is a port
            destination_units_list.append(dest.host)
        else:
            print "WARNING: skipping [%s], it destination [%s] "\
              "is not a port or connection" % (port, dest)

        return destination_units_list
