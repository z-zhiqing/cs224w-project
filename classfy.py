#import scikit-learn dataset library
from sklearn import datasets
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import snap
import numpy as np
import datetime
import networkx
import collections
from sklearn import metrics
from utilities import loadTreesFromFile
from utilities import loadMapping
from utilities import getStructuralVirality
from process_social_communities import load_communities


def classify(features,labels):
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.1) # 90% training and 10% test

    clf=RandomForestClassifier(n_estimators=100)

    #Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(X_train,y_train)

    y_pred=clf.predict(X_test)
    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

def getLargestComm(tree,node_community_mapping, communities ):
    comms = []
    for i in tree.Nodes():
        comms.append(node_community_mapping[i.GetId()])
    ctr = collections.Counter(comms)
    largestCnt = sorted(ctr)[-1]
    return float(largestCnt * largestCnt / tree.GetNodes())

def getFeatures(trees):
    # Root Node degree:
    rootNodes = loadMapping("processed_data/half/half_dfTree_rootNode_mapping.txt")
    G = snap.LoadEdgeList(snap.PNGraph, "raw_data/higgs-social_network.edgelist", 0, 1)
    node_community_mapping, communities = load_communities()

    rootDegs = []
    rootSocialDegs = []
    strVirals = []
    dfNodeCnt = []
    dfEdgeCnt = []
    coeffs = []

    # Community features
    rootComm = []
    largestComm = []

    for i in rootNodes:
        index = int(i[0])
        if index in trees:
            t = trees[index][0]
            nodeId = int(i[1])
            nd = t.GetNI(nodeId)
            deg = nd.GetDeg()
            rootDegs.append(deg)
            rootSocialDegs.append(G.GetNI(nodeId).GetDeg())
            strVirals.append(getStructuralVirality(trees[index][1]))
            dfNodeCnt.append(t.GetNodes())
            dfEdgeCnt.append(t.GetEdges())
            coeffs.append(snap.GetClustCf(t,-1))
            rootComm.append(communities[node_community_mapping[nodeId]])
            largestComm.append(getLargestComm(t, node_community_mapping, communities))
            # print index

    ft = pd.DataFrame(np.transpose([rootDegs,rootSocialDegs, strVirals, dfNodeCnt, dfEdgeCnt]), columns=["Root Degree", "Root Degree in Social Graph", "Structural Virality", "DF Node Count", "DF Edge Count"])
    ftWithComm = pd.DataFrame(np.transpose([rootDegs,rootSocialDegs, strVirals, dfNodeCnt, dfEdgeCnt, rootComm, largestComm]), columns=["Root Degree", "Root Degree in Social Graph", "Structural Virality", "DF Node Count", "DF Edge Count", "Root Node Community", "Largest Community Index"])
    return ft, ftWithComm

def getYs(h,f):
    keys = sorted(h.keys())
    labels = []

    for i in keys:
        hSize = h[i][0].GetNodes()
        fSize = f[i][0].GetNodes()
        if hSize *2 > fSize:
            labels.append(0)
        else:
            labels.append(1)
    return labels

if __name__ == "__main__":
    halfTrees = loadTreesFromFile("/Users/zilongwang/Documents/GitHub/cs224w-project/processed_data/half/trees/")
    finalTrees = loadTreesFromFile("/Users/zilongwang/Documents/GitHub/cs224w-project/processed_data/total/trees/")

    labels = getYs(halfTrees,finalTrees)
    ft, ftWithComm = getFeatures(halfTrees)

    # Examine feature set without community features:
    print ft.head()
    # Examine feature set with community features:
    print ftWithComm.head()

    classify(ft,labels)
    classify(ftWithComm,labels)
