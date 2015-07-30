#####################################################################
# Name: Yash Patel                                                  #
# File: NetworkAnalysis.py                                          #
# Description: Given data (formatted as Pajek .net and .clu files)  #
# obtains network metrics (i.e. degree distribution, density, etc..)#
#####################################################################

import networkx as nx
import matplotlib.pyplot as plt
from numpy import mean

#####################################################################
# Given the filename (MUST be .clu format), determines the degree   #
# distribution and outputs a graphical representation of it         #
#####################################################################
def getDegreeDistribution(filename):
	f = open(filename, 'r')
	f.readline()
	degrees = [int(line) for line in f]

	degree_sequence=sorted(degrees,reverse=True)
	dmax=max(degree_sequence)

	plt.loglog(degree_sequence,'b-',marker='o')
	plt.title("Degree rank plot")
	plt.ylabel("degree")
	plt.xlabel("rank")

	plt.savefig("{}Degree.png".format(filename[0:-4]))
	plt.show()

#####################################################################
# Given the filename (MUST be .net format), determines the density  #
# of the graph and returns it                                       #
#####################################################################
def getDensity(filename):
	ID_LENGTH = 10
	f = open(filename, 'r')
	numVertices = int(f.readline()[ID_LENGTH:])
	for i in range(numVertices): 
		f.readline()
	f.readline()
	numEdges = len([line for line in f])
	return numEdges/(numVertices * (numVertices - 1))

#####################################################################
# Given a graph G, determines the average reachability of its nodes #
#####################################################################
def getReachability(G):
	numNodes = len(G.nodes())
	# Obtains all the reability values for the nodes in the graph
	reaches = list(map(lambda node: len(nx.descendants(G, 
		node))/numNodes, G.nodes()))
	avgReach = mean(reaches)
	indReache = dict(zip(G.nodes(), reaches))
	return avgReach

#####################################################################
# Given a graph G, determines the average eccentricity of its nodes #
#####################################################################
def getEccentricity(G):
	paths = nx.shortest_path(G)

	# Obtains all the eccentricities for nodes in the graph. Note: the
	# -1 in the calculation accounts for not including the starting 
	# node when calculating the distance of paths
	ecc = [max(list(map(lambda x: len(paths[node][x]) - 1, paths[node]))) \
		for node in paths]
	eccentricities = dict(zip(paths, ecc))
	avgEccentricity = sum(map(lambda x: eccentricities[x], 
		eccentricities))/len(eccentricities)
	return avgEccentricity

#####################################################################
# Given a graph G, determines the average geodesic distance of its  #
# nodes                                                             #
#####################################################################
def getGeodesic(G):
	geoDist = nx.average_shortest_path_length(G1)
	return geoDist

if __name__ == "__main__":
	resultType = input("Please enter (c) for closeness and "\
		"(t) for talking: ")

	isCloseness = (resultType == 'c')
	if isCloseness: typeStr = "Close"
	else: typeStr = "Talk"

	month = input("Please enter in month: ")
	degreeDist = "{}Month_{}.clu".format(typeStr, month)
	network = "{}Results_Month{}.net".format(typeStr, month)

	G = nx.read_pajek(network)
	G1 = nx.Graph(G)

	getDegreeDistribution(degreeDist)
	print("Degree density: {}".format(getDensity(network)))
	print("Eccentricity: {}".format(getEccentricity(G1)))
	print("Geodesic Distance: {}".format(getGeodesic(G1)))
	print("Reachability: {}".format(getReachability(G1)))