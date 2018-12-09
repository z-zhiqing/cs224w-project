import snap
import numpy as np
import datetime
from matplotlib import pyplot as plt
import random
from operator import itemgetter
from matplotlib.ticker import FormatStrFormatter
from scipy.stats.stats import pearsonr
from pylab import polyfit, poly1d

random.seed(datetime.datetime.now())

def neighbors(G,src):
    deg = src.GetDeg()
    res = []
    for e in range(0, deg):
        nb = src.GetNbrNId(e)
        res.append(nb)
    return res

def load_graph(name):
    '''
    Helper function to load undirected graphs.
    Check that the respective .txt files are in the same folder as this script;
    if not, change the paths below as required.
    '''
    if name == "retweet":
        G = snap.LoadEdgeList(snap.PNGraph, "/Users/zilongwang/Desktop/CS224/Project/higgs-retweet_reversed.edgelist", 0, 1)
    elif name == 'mention':
        G = snap.LoadEdgeList(snap.PNGraph, "/Users/zilongwang/Desktop/CS224/Project/higgs-mention_network.edgelist", 0, 1)
    elif name == 'reply':
        G = snap.LoadEdgeList(snap.PNGraph, "/Users/zilongwang/Desktop/CS224/Project/higgs-reply_network.edgelist", 0, 1)
    elif name == 'social':
        G = snap.LoadEdgeList(snap.PNGraph, "/Users/zilongwang/Desktop/CS224/Project/higgs-social_network.edgelist", 0, 1)
    else:
        raise ValueError("Invalid graph: please use 'normal', 'rewired' or 'sample'.")
    return G

def revertG():
    with open ("/Users/zilongwang/Desktop/CS224/Project/higgs-retweet_network.edgelist", "r") as myfile:
        with open ("/Users/zilongwang/Desktop/CS224/Project/higgs-retweet_reversed.edgelist", "a") as outfile: 
            for line in myfile:
                temp = line.split()
                outfile.write(temp[1]+" "+temp[0]+" "+temp[2]+"\n")

def loadTimeData(delim):
    res = []
    with open ("//Users/zilongwang/Desktop/CS224/Project/higgs-activity_time.txt", "r") as myfile: 
        for line in myfile:
            if line.split()[3] == delim:
                res.append(tuple(line.split()))
            #print len(res)

    sorted(res,key=itemgetter(2))
    return res
def getTimeMatrix(timeD,n,ifRet=True):
    res = {}
    for i in timeD:
        if ifRet:
            res[(int(i[1]),int(i[0]))] = int(i[2])
        else:
            res[(int(i[0]),int(i[1]))] = int(i[2])
    return res

def getDepth(trees):
    d = {}
    depCnt = []
    for t in trees:
        src = t[1]
        depth = snap.GetSubTreeSz(t[0],src,True,False)  
        depCnt.append(depth)
        size = t[0].GetNodes()  
        if size in d:
            d[size].append(depth)
        else:
            d[size] = [depth]
    
    tps = []
    for k, v in d.iteritems():
        tps.append((k,np.mean(v)))

    sorted(tps)
    x = [i[0] for i in tps]
    y = [i[1] for i in tps]
    return x,y


def getCascadeSize(trees):
    sizes = [i[0].GetNodes() for i in trees]
    sizes.sort()
    cumulative = np.cumsum(sizes)
    cdf = cumulative/float(cumulative[-1])
    ccdf = [float(1-i) *100 for i in cdf]
    return sizes, ccdf



def getSV(trees):
    sizeArr = []
    svArr = []
    #s = sorted(s, key = itemgetter(1))
    trees.sort(key = itemgetter(2))
    for t in trees:
        size = t[0].GetNodes()  
        sizeArr.append(size)
        svArr.append(t[2])
    
    cumulative = np.cumsum(svArr)
    cdf = cumulative/float(cumulative[-1])
    ccdf = [float(1-i) *100 for i in cdf]
    return svArr, ccdf

def getRootDegs(trees):
    tps = []
    degs = []
    for t in trees:
        src = t[1]
        deg = t[0].GetNI(src).GetDeg()
        degs.append(deg)
        size = t[0].GetNodes()  
        tps.append((size,deg))

    sorted(tps)
    x = [i[0] for i in tps]
    y = [i[1] for i in tps]
    return x,y

def getSVandSize(trees):
    sizeArr = []
    svArr = []
    #s = sorted(s, key = itemgetter(1))
    trees.sort(key = itemgetter(2))
    for t in trees:
        size = t[0].GetNodes()  
        sizeArr.append(size)
        svArr.append(t[2])

    return svArr, sizeArr

def bfs(G,n,rootTime, timeM):
    res = snap.TNGraph.New()
    s = set()
    q = []
    sumSize = 0
    sumSizeSqr = 0
    q.append((n,rootTime,0))
    
    while (q):
        cur = q.pop()
        curNode = cur[0]
        curTime = cur[1]
        curD = cur[2]
        sumSize += curD
        sumSizeSqr+=curD*curD
        if curNode not in s:
            s.add(curNode)
            res.AddNode(curNode)
        for nbr in neighbors(G,G.GetNI(curNode)):
            if G.IsEdge(curNode,nbr):
                edgeTime = timeM[(curNode,nbr)]
                if nbr not in s and edgeTime > curTime:
                    q.append((nbr,edgeTime, curD+1))
                    s.add(nbr)
                    res.AddNode(nbr)
                    res.AddEdge(curNode,nbr)

    n = res.GetNodes()
    sv = 0 if n==1 else float(2*n/(n-1)) * (float(sumSize)/n - sumSizeSqr/float(n*n))
    return res, sv