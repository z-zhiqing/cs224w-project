import snap
import community
import networkx as nx
import numpy as np
from scipy import stats
import datetime

# Louvain algorithm, networkx community api
def compute_community():
    global G
    G = nx.read_edgelist(path="raw_data/higgs-social_network.edgelist", nodetype=int)
    print "Loading graph completed: " + str(datetime.datetime.now())

    partition = community.best_partition(G)
    print "Community partition completed: " + str(datetime.datetime.now())

    with open('processed_data/social_communities.txt', 'w') as f:
        for key, value in partition.items():
            f.write('%s:%s\n' % (key, value))
    print "Saving social communities completed: " + str(datetime.datetime.now())

def load_communities():
    node_community_mapping = dict()
    communities = dict()

    with open('processed_data/social_communities.txt') as data:
        for item in data:
            if ':' in item:
                key, value = map(int, item.rstrip().split(':', 1))
                node_community_mapping[key] = value
                if value in communities.keys():
                    communities[value] += 1
                else:
                    communities[value] = 1
            else:
                pass
	return node_community_mapping, communities

def get_community_stats():
    G = nx.read_edgelist(path="raw_data/higgs-social_network.edgelist", nodetype=int)
    node_community_mapping, communities = load_communities()

    # Get stats
    modularity = community.modularity(node_community_mapping, G)
    sizes = list(communities.values())
    count = len(sizes)
    min_size = min(sizes)
    max_size = max(sizes)
    mean_size = np.mean(sizes)
    median_size = np.median(sizes)
    mode_size = stats.mode(sizes)
    print "Total number of communities: {}, min: {}, max: {}, mean: {}, median: {}, mode: {}, modularity: {}".format(count, min_size, max_size, mean_size, median_size, mode_size, modularity)

def get_friends():
    friends = set()
    G = snap.LoadEdgeList(snap.PNGraph, "raw_data/higgs-social_network.edgelist", 0, 1)
    print "Done loading social graph: {}".format(str(datetime.datetime.now()))

    for node in G.Nodes():
        nid = node.GetId()
        num_nbr = node.GetOutDeg()
        for i in xrange(num_nbr):
            nbr_nid = node.GetOutNId(i)
            pair = frozenset({nid, nbr_nid})
            if nid != nbr_nid and pair not in friends and G.GetNI(nbr_nid).IsOutNId(nid):
                friends.add(pair)
    print "Done creating friendship: {}".format(str(datetime.datetime.now()))

    with open('processed_data/friends.txt', 'w') as f:
        for friend in friends:
            friend = list(friend)
            print friend
            f.write('{} {}\n'.format(friend[0], friend[1]))
    print "Saving friendship completed: " + str(datetime.datetime.now())

if __name__ == "__main__":
    get_community_stats()
    #get_friends()
    print "Done with processing social communities.\n"