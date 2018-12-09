import snap
import numpy as np
import datetime
from matplotlib import pyplot as plt
import random
from operator import itemgetter
from matplotlib.ticker import FormatStrFormatter
from scipy.stats.stats import pearsonr
from pylab import polyfit, poly1d

from network_description import load_graph
from utilities import loadTreesFromFile, load_mapping

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


if __name__ == "__main__":

    total_trees = loadTreesFromFile('processed_data/total/trees/')
    total_tree_rootnode_mappping = load_mapping('processed_data/total/dfTree_rootNode_mapping.txt')
    total_node_tree_mapping = load_mapping('processed_data/total/node_dfTree_mapping.txt')

    rt_trees = loadTreesFromFile('processed_data/RT/trees/')
    rt_tree_rootnode_mappping = load_mapping('processed_data/RT/RT_dfTree_rootNode_mapping.txt')
    rt_node_tree_mapping = load_mapping('processed_data/RT/RT_node_dfTree_mapping.txt')






    """G_ret = load_graph("retweet")
    print "Nodes: ", G_ret.GetNodes()
    print "Edges: ", G_ret.GetEdges()

    G_men = load_graph("mention")
    G_reply = load_graph("reply")
    G_social = load_graph("social")
    print "Social Nodes: ", G_social.GetNodes()
    print "Social Edges: ", G_social.GetEdges()"""

    timeD = loadTimeData("RT")
    timeM = getTimeMatrix(timeD,G_ret.GetNodes())
    trees = getTrees(G_ret, timeD, timeM)
    print "Number of trees: ", len(trees)
    cas = [t for t in trees if t[0].GetNodes() >= 5]
    print "Number of k>=5 trees: ", len(cas)

    timeD2 = loadTimeData("MT")
    timeM2 = getTimeMatrix(timeD2,G_men.GetNodes(), False)
    trees2 = getTrees(G_men, timeD2, timeM2)
    print "Number of trees: ", len(trees2)
    cas2 = [t for t in trees2 if t[0].GetNodes() >= 5]
    print "Number of k>=5 trees: ", len(cas2)

    timeD3 = loadTimeData("RE")
    timeM3 = getTimeMatrix(timeD3,G_reply.GetNodes(), False)
    trees3 = getTrees(G_reply, timeD3, timeM3)
    print "Number of trees: ", len(trees3)
    cas3 = [t for t in trees3 if t[0].GetNodes() >= 5]
    print "Number of k>=5 trees: ", len(cas3)

    #plotDepth(cas,"Retweet")
    svArr,ccdf = getSV(cas)
    svArr2,ccdf2 = getSV(cas2)
    svArr3,ccdf3 = getSV(cas3)
    plt.loglog(svArr,ccdf,c='red',label="Retweet")
    plt.loglog(svArr2,ccdf2,c='blue',label="Mention")
    plt.loglog(svArr3,ccdf3,c='green',label="Reply")
    plt.ylabel("CCDF Percentage %")
    plt.xlabel("Structural Viralty")
    plt.title("CCDF of Structural Viralty for Retweet, Mention and Reply")
    plt.ylim([0,100])
    plt.yticks([0,25,50,75,100])
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    ax.set_yscale('symlog')
    ax.set_xscale('symlog')
    plt.legend()
    plt.show()    

    #plot casade size
    x1, y1 = getCascadeSize(cas)
    x2, y2 = getCascadeSize(cas2)
    x3, y3 = getCascadeSize(cas3)
    plt.loglog(x1,y1,c='red',label="Retweet")
    plt.loglog(x2,y2,c='blue',label="Mention")
    plt.loglog(x3,y3,c='green',label="Reply")
    plt.ylabel("CCDF Percentage %")
    plt.xlabel("Size of The Cascade")
    plt.title("CCDF of Information Cascade Size for Retweet, Mention and Reply")
    plt.yticks([0,25,50,75,100])
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    plt.ylim([0,100])
    ax.set_yscale('symlog')
    ax.set_xscale('symlog')
    plt.legend()
    plt.show() 

    # plot average depth
    x1, y1 = getDepth(cas)
    x2, y2 = getDepth(cas2)
    x3, y3 = getDepth(cas3)
    plt.loglog(x1,y1,c='red',label="Retweet")
    plt.loglog(x2,y2,c='blue',label="Mention")
    plt.loglog(x3,y3,c='green',label="Reply")
    plt.ylabel("Average Tree Depth For a Tree of Size x")
    plt.xlabel("Size of The Diffusion Tree")
    plt.title("Diffusion Tree Size v.s. Average Depth for Retweet, Mention and Reply")
    plt.tick_params(axis='y', which='minor')
    ax = plt.gca()
    plt.legend()
    plt.show()  
    plt.autoscale()   

    x,y = getSVandSize(cas)
    x2,y2= getSVandSize(cas2)
    x3,y3 = getSVandSize(cas3)
    c1, p1 =  pearsonr(x,y)
    c2, p2 = pearsonr(x2,y2)
    c3, p3 = pearsonr(x3,y3)
    x = np.array([1,2,3])
    y = np.array([c1,c2,c3])
    my_xticks = ['Retweet','Mention','Reply']
    plt.xticks(x, my_xticks)
    plt.plot(x, y,'-o')
    plt.xlim([0,4])
    plt.ylim([0,1])
    plt.grid()
    plt.title("Correlation Between Structural Viralty and Cascade Size")
    plt.show()

    # plot Root Deg depth
    x1, y1 = getRootDegs(cas)
    x2, y2 = getRootDegs(cas2)
    x3, y3 = getRootDegs(cas3)

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