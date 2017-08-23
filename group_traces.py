import re
import numpy as np
from make_dag import *
from decimal import *

# groups of traces based on structure
categories = {}
anomaly_types = {'anomalous_groups': {}, 'anomalous_edges': {}, 'high_covar_edges': {}}

def add_to_dict(dic, key, add_val):
    if dic.get(key) is not None:
        dic[key].append(add_val)
    else:
        dic[key] = [add_val]

def depth_first_traversal(trace):
    """
    the DFT traverses DAG dict starting with 
    root node; returns a list indicating all
    nodes seen in order. no duplicates are
    kept in case of sync and full paths are 
    not kept.
    """
    from timer import Timer
    nodes = []
    stack = [trace.dag]
    while stack:
	with Timer() as t:
	    cur_node = stack[0]
	    stack = stack[1:]
	    if cur_node.id not in nodes: #do not duplicate in case of sync
		nodes.append(cur_node.id)
	    for child in cur_node.get_rev_children():
		stack.insert(0, child)
	    #print "=> time of start: %s" % t.start
    return nodes 

def hashval(trace):
    """
    hashval takes the list generated by DFT and 
    creates a string for the hash value
    of each trace (stored in trace object).
    """
    lst = depth_first_traversal(trace)
    trunc = [re.search(r'....$', x).group(0) if len(x) > 3 else x for x in lst]
        
    hashval = "".join(trunc)
    return hashval

def group_traces(trace):
    """
    traces with the same hash value (determined by
    hashval function) are in the same group. keys are
    hashvalues, values are lists of trace ids in that
    group.
    """
    add_to_dict(categories, trace.hashval, trace.traceId)

def trace_lookup(tid, tlist):
    for trace in tlist:
        if trace.traceId == tid:
            return trace
    return none

def process_groups(d, tlist):
    """
    calculates the average completion time of
    traces within a group, as well as variance 
    of each group.
    """
    group_info = {}

    for hashv, traceids in d.items():
        psum = 0
        lst = []
        numvals = len(traceids)

        # count edges (uses first trace in group as representative)
        t = trace_lookup(traceids[0], tlist)
        num_edges = len(t.fullEdges)

        # calculate average
        for tid in traceids:
            t = trace_lookup(tid, tlist)
            psum += float(t.response)
        if numvals != 0:
            avg = psum / numvals
        else:
            #throw an error
            pass
 
        # calculate variance
        psum = 0
        if numvals < 2:
            var = 0
        else: 
	    for tid in traceids:
       	        t = trace_lookup(tid, tlist)
        	curr = (float(t.response) - avg) ** 2
		psum += curr
            if numvals != 1:
                var = (1 / float(numvals - 1)) * psum
            else:
                #throw an error
                pass
        # random value, can be changed
        if var > 5:
            add_to_dict(anomaly_types[anomalous_groups], "Groups:", group)
            
        group_info[hashv] = {'Number of edges': num_edges, 'Trace total time average' : avg, 'Trace total time variance': var}
    return group_info
