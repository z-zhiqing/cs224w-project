import snap
from matplotlib import pyplot as plt

def load_graph(name):
    if name == "retweet":
        G = snap.LoadEdgeList(snap.PNGraph, "higgs-retweet_network.edgelist", 1, 0)
    elif name == 'mention':
        G = snap.LoadEdgeList(snap.PNGraph, "higgs-mention_network.edgelist", 0, 1)
    elif name == 'reply':
        G = snap.LoadEdgeList(snap.PNGraph, "higgs-reply_network.edgelist", 0, 1)
    elif name == 'social':
        G = snap.LoadEdgeList(snap.PNGraph, "higgs-social_network.edgelist", 0, 1)
    else:
        raise ValueError("Invalid graph: please use 'retweet', 'mention', 'reply', or 'social'.")
    return G

def getDataPointsToPlot(Graph, degType):
    """
    return values:
    X: list of degrees
    Y: list of frequencies: Y[i] = fraction of nodes with degree X[i]
    """
    ############################################################################
    DegToCntV = snap.TIntPrV()

    if degType == "In":
        snap.GetInDegCnt(Graph, DegToCntV)
    elif degType == "Out":
        snap.GetOutDegCnt(Graph, DegToCntV)
    elif degType == "Total":
        snap.GetDegCnt(Graph, DegToCntV)
    else:
        raise ValueError("Invalid degree type: please use 'In', 'Out' or 'Total'.")

    NumNodes = Graph.GetNodes()
    DegToFrqV = { item.GetVal1() : float(item.GetVal2())/NumNodes for item in DegToCntV }
    DegToFrqV = sorted(DegToFrqV.items())
    X, Y = zip(*DegToFrqV)
    ############################################################################
    return X, Y

    def plot_graph(name):
        G = load_graph(name)
        print "{} graph nodes: {}".format(name, G.GetNodes()) 
        print "{} graph edges: {}".format(name, G.GetEdges()) 

        x_in, y_in = getDataPointsToPlot(G, 'In')
        plt.loglog(x_in, y_in, marker=',', color = 'y', label = 'In Degree')

        x_out, yout = getDataPointsToPlot(G, 'Out')
        plt.loglog(x_out, y_out, marker=',', color = 'r', label = 'Out Degree')

        x_total, y_total = getDataPointsToPlot(G, 'Total')
        plt.loglog(x_total, y_total, marker=',', color = 'b', label = 'Total Degree')  #linestyle = 'dotted'

        plt.xlabel('Node Degree (log)')
        plt.ylabel('Proportion of Nodes with a Given Degree (log)')
        plt.title('Degree Distribution of In, Out, and Total degree for {} network'.format(name))
        plt.legend()
        plt.show()


    if __name__ == "__main__":
        # Plot distribution graphs for RT, MT, RE, Social networks
        plot_graph("retweet")
        plot_graph("mention")
        plot_graph("reply")
        plot_graph("social")