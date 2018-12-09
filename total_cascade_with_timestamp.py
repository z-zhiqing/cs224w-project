import snap
#import community
import networkx as nx
import numpy as np
import datetime

from scipy import stats
#from process_social_communities import load_communities
from utilities import split_activity_file
from utilities import read_and_plot_tree

def main():
    global node_community_mapping, node_dfTree_mapping, dfTree_rootNode_mapping, dfTree_timestamp_mapping, dfTrees

    #split_activity_file('RT')
    #split_activity_file('MT')

    node_dfTree_mapping, dfTree_rootNode_mapping, dfTree_timestamp_mapping, dfTrees = construct_diffusion_trees('half')

    read_and_plot_tree('processed_data/total/trees/928.txt', '928')

def construct_diffusion_trees(activityType):
    node_dfTree_mapping = dict()
    dfTree_rootNode_mapping = dict()
    dfTree_timestamp_mapping = dict()
    dfTrees = dict()

    # counters
    next_dfTree_Id = 0
    counter = 0
    with open('processed_data/higgs-activity_time_{}.txt'.format(activityType)) as data:
        for item in data:
            # Process nodes and timestamp
            start_id, end_id, timestamp, activity = item.split()
            if activity != 'RT':
                start_id = int(start_id)
                end_id = int(end_id)
            else:
                tmp = start_id
                start_id = int(end_id)
                end_id = int(tmp)
            timestamp = int(timestamp)

            # Construct cascades
            # if start node is not in df tree, ADD IT.
            if start_id not in node_dfTree_mapping.keys():
                # add node to node_dfTree_mapping with new df tree index
                treeId = next_dfTree_Id
                next_dfTree_Id += 1
                node_dfTree_mapping[start_id] = treeId

                # add new dftree
                dfTree_rootNode_mapping[treeId] = start_id
                dfTree_timestamp_mapping[treeId] = [timestamp, 0]
                G = snap.TNGraph.New()
                G.AddNode(start_id)
                dfTrees[treeId] = G

            # if end node is not in df tree
            if start_id != end_id and end_id not in node_dfTree_mapping.keys():
                # set end node to start node's df tree
                treeId = node_dfTree_mapping[start_id]
                node_dfTree_mapping[end_id] = treeId

                # add end node to df Tree
                G = dfTrees[treeId]
                G.AddEdge2(start_id, end_id)
                dfTrees[treeId] = G
            # else if end node is already in df tree - do nothing (1st activity determines df tree)
            # update df tree latest timestamp
            dfTree_timestamp_mapping[node_dfTree_mapping[end_id]][1] = timestamp
            print "{}: {}".format(activityType, counter)
            counter += 1

    with open('processed_data/{}/{}_node_dfTree_mapping.txt'.format(activityType, activityType), 'w') as f:
        for key, value in node_dfTree_mapping.items():
            f.write('%s %s\n' % (key, value))
    print "Saving node to dfTree mapping completed: " + str(datetime.datetime.now()) 

    with open('processed_data/{}/{}_dfTree_rootNode_mapping.txt'.format(activityType, activityType), 'w') as f:
        for key, value in dfTree_rootNode_mapping.items():
            f.write('%s %s\n' % (key, value))
    print "Saving dfTree to root node mapping completed: " + str(datetime.datetime.now())

    with open('processed_data/{}/{}_dfTree_timestamp_mapping.txt'.format(activityType, activityType), 'w') as f:
        for key, value in dfTree_timestamp_mapping.items():
            f.write('%s %s\n' % (key, value))
    print "Saving dfTreeId to timestamps mapping completed: " + str(datetime.datetime.now()) 

    for key, value in dfTrees.items():
        snap.SaveEdgeList(value, 'processed_data/{}/trees/{}_{}.txt'.format(activityType, activityType, key))
    print "Saving dfTrees completed: " + str(datetime.datetime.now()) 

    return node_dfTree_mapping, dfTree_rootNode_mapping, dfTree_timestamp_mapping, dfTrees

if __name__ == "__main__":
    INITIALTIMESTAMP = 0
    LATESTTIMESTAMP = 1
    main()
    print "Done with processing total cascade with timestamp.\n"