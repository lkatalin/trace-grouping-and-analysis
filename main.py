import sys
from def_color import *
from make_dag import *
from extract_traces import *
from print_stuff import *
from group_traces import *
from edge_data import *

# open file from arg or use piped input from stdin
# to be used if piping from json_parser
try:
    filename = sys.argv[1]
    with open(filename) as infile:
        tracelist = extract_traces(infile)
except IndexError:
    tracelist = extract_traces(sys.stdin.readlines())

# uncomment below to get verbose dump of all trace-object data per trace
#print_trace(tracelist)

# group traces based on hashvalue (structure)
for trace in tracelist:
    group_traces(trace)

#analyze groups for avg latency and variance
group_data = process_groups(categories, tracelist)

# print human-meaningful info
print "\n----------------------------SUMMARY OF TRACE DATA------------------------------ \n"

key_counter = 0
for key in categories.keys():
    key_counter += 1

print "Number of traces: %d" % len(tracelist)
print "Number of categories: %d \n" % key_counter

print "INFO BY CATEGORY: \n"
for key, values in categories.items():
    print "Category hashval: " + str(key)
    print "Number of traces: " + str(len(values))
    print "The traces are: " + str (values) 
    for val in group_data[key]:
        print (val + ': ' + str(group_data[key][val]))
    print "\n"

for key in categories.keys():
    latencies = edge_latencies(key, tracelist)
    if len(categories[key]) > 1:
        cov_matrix(key, latencies[0], tracelist)


print "VARIANCE RESULTS:\n"
if len(anomalous_groups) == 0:
    print "{}---> No anomalous groups found (var > 20).{}\n".format(G, W)
else:
    print "{}---> Anomalous groups found (var > 20):{} ".format(R, W) + str(anomalous_groups) + "\n"
if len(anomalous_edges) == 0:
    print "\n{}---> No anomalous edges found (var > 5).{}\n".format(G, W)
else:
    print "\n{}---> Anomalous edges found (var > 5):{}\n".format(R, W)
    for group, edges in anomalous_edges.iteritems():
        print "     Group: " + str(group)
        print "     Edges: "
        for edge in edges:
            print "            " + str(edge)
if len(high_covar_edges) == 0:
    print "\n{}---> No high covariance edges found (var > 3000000000).{}\n".format(G, W)
else:
    print "\n{}---> High covariance edges found (var > 3000000000):{}\n".format(R, W)
    for group, var in high_covar_edges.iteritems():
        print "     Group: " + str(group)
        print "     Edges: "
        for v in var:
            print "            " + str(v)
