import os
import snap
import numpy as np
import datetime
import networkx as nx

def split_activity_file(activityType):
    with open('raw_data/higgs-activity_time.txt') as data:
        with open('processed_data/higgs-activity_time_{}.txt'.format(activityType), 'w') as f:
            for item in data:
                start_id, end_id, timestamp, activity = item.split()
                if activity == activityType:
                    f.write('%s %s %s %s\n' % (start_id, end_id, timestamp, activity))

def read_and_plot_tree(filepath, outfilename):
    G = nx.read_edgelist(filepath, nodetype=int)
    nx.write_gexf(G, "{}.gexf".format(outfilename))

def loadTreesFromFile(dir):
    trees = {}
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            path = dir + filename
            if "_" in filename:
                treeId = int(filename.split("_")[1].split(".")[0])
            else:
                treeId = int(filename.split(".")[0])
            G_snap = snap.LoadEdgeList(snap.PNGraph, path, 0, 1)
            G_networkx = nx.read_edgelist(path, nodetype=int)
            if (G_snap.GetNodes() > 1):
                trees[treeId] = (G_snap,G_networkx)
    return trees

def getStructuralVirality(tree):
    return nx.average_shortest_path_length(tree)

def loadMapping(fileName):
    result = []
    with open (fileName,"r") as myfile:
            for line in myfile:
                temp = line.split()
                result.append(temp)
    return result

def load_mapping(filepath):
    result = dict()
    with open(filepath, 'r') as data:
        for item in data:
            key, value = item.split()
            key = int(key)
            value = int(value)
            result[key] = value
    return result