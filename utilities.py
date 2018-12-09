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

def read_and_plot_tree(filepath):
    G = nx.read_edgelist(filepath, create_using=nx.DiGraph())
    nx.write_gexf(G, "928.gexf")

def loadTreesFromFile(dir):
    trees = []

    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            path = dir + filename
            G_snap = snap.LoadEdgeList(snap.PNGraph, path, 0, 1)
            G_networkx = nx.read_edgelist(path)
            trees.append((G_snap,G_networkx))

    return trees

def getStructuralVirality(tree):
    return nx.average_shortest_path_length(tree)
