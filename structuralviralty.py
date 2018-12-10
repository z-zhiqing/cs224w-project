import snap
import numpy as np
import datetime
from matplotlib import pyplot as plt
import random
from operator import itemgetter
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
from scipy.stats.stats import pearsonr
from pylab import polyfit, poly1d

from network_description import load_graph
from utilities import loadTreesFromFile, load_mapping, getStructuralVirality

random.seed(datetime.datetime.now())

def neighbors(G,src):
    deg = src.GetDeg()
    res = []
    for e in range(0, deg):
        nb = src.GetNbrNId(e)
        res.append(nb)
    return res

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

def getDepth(trees, mapping):
    d = {}
    depCnt = []
    for key, value in trees.items():
        depth = snap.GetSubTreeSz(value[0], mapping[key], True, False)  
        depCnt.append(depth)
        size = value[0].GetNodes()  
        if size in d:
            d[size].append(depth)
        else:
            d[size] = [depth]
    
    tps = []
    for k, v in d.items():
        tps.append((k, np.mean(v)))

    sorted(tps)
    x = [i[0] for i in tps]
    y = [i[1] for i in tps]
    return x,y

# important
def getCascadeSize(trees):
    sizes = [value[0].GetNodes() for key, value in trees.items()]
    sizes.sort()
    cumulative = np.cumsum(sizes)
    cdf = cumulative/float(cumulative[-1])
    ccdf = [float(1-i) *100 for i in cdf]
    return sizes, ccdf

# important
def getSV(trees):
    svArr = [getStructuralVirality(value[1]) for key, value in trees.items()]
    svArr.sort()
    cumulative = np.cumsum(svArr)
    cdf = cumulative/float(cumulative[-1])
    ccdf = [float(1-i) *100 for i in cdf]
    return svArr, ccdf

def getRootDegs(trees, mapping):
    tps = []
    for key, value in trees.items():
        src = mapping[key]
        deg = value[0].GetNI(src).GetDeg()
        size = value[0].GetNodes()  
        tps.append((size,deg))

    sorted(tps)
    x = [i[0] for i in tps]
    y = [i[1] for i in tps]
    return x,y

def getSVandSize(trees):
    arr = []
    for key, value in trees.items():
        sv = getStructuralVirality(value[1])
        size = value[0].GetNodes()
        arr.append((sv, size))
    sorted(arr, key=itemgetter(0))
    svArr, sizeArr = zip(*arr)
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

if __name__ == "__main__":

    total_trees = loadTreesFromFile('processed_data/total/trees/')
    print "1"
    total_tree_rootnode_mappping = load_mapping('processed_data/total/dfTree_rootNode_mapping.txt')
    #total_node_tree_mapping = load_mapping('processed_data/total/node_dfTree_mapping.txt')

    rt_trees = loadTreesFromFile('processed_data/RT/trees/')
    print "1"
    rt_tree_rootnode_mappping = load_mapping('processed_data/RT/RT_dfTree_rootNode_mapping.txt')
    #rt_node_tree_mapping = load_mapping('processed_data/RT/RT_node_dfTree_mapping.txt')

    mt_trees = loadTreesFromFile('processed_data/MT/trees/')
    print "1"
    mt_tree_rootnode_mappping = load_mapping('processed_data/MT/MT_dfTree_rootNode_mapping.txt')
    #mt_node_tree_mapping = load_mapping('processed_data/MT/MT_node_dfTree_mapping.txt')

    re_trees = loadTreesFromFile('processed_data/RE/trees/')
    print "1"
    re_tree_rootnode_mappping = load_mapping('processed_data/RE/RE_dfTree_rootNode_mapping.txt')
    #re_node_tree_mapping = load_mapping('processed_data/RE/RE_node_dfTree_mapping.txt')

    # Plot Cascade Size
    """x1, y1 = getCascadeSize(rt_trees)
    x2, y2 = getCascadeSize(mt_trees)
    x3, y3= getCascadeSize(re_trees)
    x4, y4 = getCascadeSize(total_trees)
    plt.loglog(x1,y1,c='red',label="Retweet")
    plt.loglog(x2,y2,c='blue',label="Mention")
    plt.loglog(x3,y3,c='green',label="Reply")
    plt.loglog(x4,y4,c='orange',label="All Activities")
    plt.ylabel("CCDF Percentage %")
    plt.xlabel("Cascade Size")
    plt.title("CCDF of Cascade Size for Retweet, Mention, Reply, and All Activities")
    plt.yticks([0,25,50,75,100])
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    plt.ylim([0,100])
    ax.set_yscale('symlog')
    ax.set_xscale('symlog')
    plt.legend()
    plt.show() """

    # Plot Structural Virality
    """x1, y1 = getSV(rt_trees)
    x2, y2 = getSV(mt_trees)
    x3, y3 = getSV(re_trees)
    x4, y4 = getSV(total_trees)
    plt.loglog(x1,y1,c='red',label="Retweet")
    plt.loglog(x2,y2,c='blue',label="Mention")
    plt.loglog(x3,y3,c='green',label="Reply")
    plt.loglog(x4,y4,c='orange',label="All Activities")
    plt.ylabel("CCDF Percentage %")
    plt.xlabel("Cascade Structural Viralty")
    plt.title("CCDF of Structural Viralty for Retweet, Mention, Reply, and All Activities")
    plt.ylim([0,100])
    plt.yticks([0,25,50,75,100])
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    ax.set_yscale('symlog')
    ax.set_xscale('symlog')
    ax.set_xticks([0,1,5])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.legend()
    plt.show()""" 

    # Plot correlation between SV and Cascade Size
    """x1,y1 = getSVandSize(rt_trees)
    print "1"
    x2,y2 = getSVandSize(mt_trees)
    print "1"
    x3,y3 = getSVandSize(re_trees)
    print "1"
    x4,y4 = getSVandSize(total_trees)
    print "1"
    c1, p1 = pearsonr(x1,y1)
    c2, p2 = pearsonr(x2,y2)
    c3, p3 = pearsonr(x3,y3)
    c4, p4 = pearsonr(x4,y4)
    x = np.array([1,2,3,4])
    y = np.array([c1,c2,c3,c4])
    my_xticks = ['Retweet','Mention','Reply','All Activities']
    plt.xticks(x, my_xticks)
    plt.plot(x, y,'-o')
    plt.xlim([0,5])
    plt.ylim([0,1])
    plt.grid()
    plt.title("Correlation Between Structural Viralty and Cascade Size")
    plt.show()"""


    # plot average depth
    x1, y1 = getDepth(rt_trees, rt_tree_rootnode_mappping)
    x2, y2 = getDepth(mt_trees, mt_tree_rootnode_mappping)
    x3, y3 = getDepth(re_trees, re_tree_rootnode_mappping)
    x4, y4 = getDepth(total_trees, total_tree_rootnode_mappping)
    plt.loglog(x1,y1,c='red',label="Retweet")
    plt.loglog(x2,y2,c='blue',label="Mention")
    plt.loglog(x3,y3,c='green',label="Reply")
    plt.loglog(x4,y4,c='orange',label="All Activities")
    plt.ylabel("Average Tree Depth For a Tree of Size x")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Average Tree Depth")
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    plt.legend()
    plt.show()  
    plt.autoscale()   

    # Plot Root Deg depth
    x1, y1 = getRootDegs(rt_trees, rt_tree_rootnode_mappping)
    x2, y2 = getRootDegs(mt_trees, mt_tree_rootnode_mappping)
    x3, y3 = getRootDegs(re_trees, re_tree_rootnode_mappping)
    x4, y4 = getRootDegs(total_trees, total_tree_rootnode_mappping)

    fit = polyfit(x1, y1, 1)
    fit_fn = poly1d(fit)
    plt.plot(x1, y1, '*', x1, fit_fn(x1), 'k',c='red')
    plt.ylabel("Root Degree")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Root Degree for Retweet")
    plt.tick_params(axis='y', which='minor')
    plt.legend()
    plt.show()  
    plt.autoscale()   

    fit = polyfit(x2, y2, 1)
    fit_fn = poly1d(fit)
    plt.plot(x2, y2, '*', x2, fit_fn(x2), 'k',c='blue')
    plt.ylabel("Root Degree")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Root Degree for Mention")
    plt.tick_params(axis='y', which='minor')
    plt.legend()
    plt.show()  
    plt.autoscale()   

    fit = polyfit(x3, y3, 1)
    fit_fn = poly1d(fit)
    plt.plot(x3, y3, '*', x3, fit_fn(x3), 'k',c='green')
    plt.ylabel("Root Degree")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Root Degree for Reply")
    plt.tick_params(axis='y', which='minor')
    plt.legend()
    plt.show()  
    plt.autoscale()

    fit = polyfit(x4, y4, 1)
    fit_fn = poly1d(fit)
    plt.plot(x4, y4, '*', x4, fit_fn(x4), 'k',c='orange')
    plt.ylabel("Root Degree")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Root Degree for All Activities")
    plt.tick_params(axis='y', which='minor')
    plt.legend()
    plt.show()  
    plt.autoscale()