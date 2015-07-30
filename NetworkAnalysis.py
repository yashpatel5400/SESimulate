#####################################################################
# Name: Yash Patel                                                  #
# File: NetworkAnalysis.py                                          #
# Description: Given data (formatted as Pajek .net and .clu files)  #
# obtains network metrics (i.e. degree distribution, density, etc..)#
#####################################################################

from __future__ import division
from __future__ import absolute_import
import networkx as nx
import matplotlib.pyplot as plt
import Tkinter
import FileDialog

from numpy import mean
from io import open
from itertools import imap
from itertools import izip

#####################################################################
# Given the filename (MUST be .clu format), determines the degree   #
# distribution and outputs a graphical representation of it         #
#####################################################################
def getDegreeDistribution(filename):
	f = open(filename, u'r')
	f.readline()
	degrees = [int(line) for line in f]

	degree_sequence=sorted(degrees,reverse=True)
	dmax=max(degree_sequence)

	plt.loglog(degree_sequence,u'b-',marker=u'o')
	plt.title(u"Degree rank plot")
	plt.ylabel(u"degree")
	plt.xlabel(u"rank")

	plt.savefig(u"{}Degree.png".format(filename[0:-4]))

#####################################################################
# Given the filename (MUST be .net format), determines the density  #
# of the graph and returns it                                       #
#####################################################################
def getDensity(filename):
	ID_LENGTH = 10
	f = open(filename, u'r')
	numVertices = int(f.readline()[ID_LENGTH:])
	for i in xrange(numVertices): 
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
	reaches = list(imap(lambda node: len(nx.descendants(G, 
		node))/numNodes, G.nodes()))
	avgReach = mean(reaches)
	indReache = dict(izip(G.nodes(), reaches))
	return avgReach

#####################################################################
# Given a graph G, determines the average eccentricity of its nodes #
#####################################################################
def getEccentricity(G):
	paths = nx.shortest_path(G)

	# Obtains all the eccentricities for nodes in the graph. Note: the
	# -1 in the calculation accounts for not including the starting 
	# node when calculating the distance of paths
	ecc = [max(list(imap(lambda x: len(paths[node][x]) - 1, paths[node]))) \
		for node in paths]
	eccentricities = dict(izip(paths, ecc))
	avgEccentricity = sum(imap(lambda x: eccentricities[x], 
		eccentricities))/len(eccentricities)
	return avgEccentricity

#####################################################################
# Given a graph G, determines the average geodesic distance of its  #
# nodes                                                             #
#####################################################################
def getGeodesic(G):
	geoDist = nx.average_shortest_path_length(G1)
	return geoDist

if __name__ == u"__main__":
	# Adjusts for the counting of months naturally starting from 1 
	# as opposed to 0
	ADJUST = 1

	# Accounts for month 3 (skipped in data collection process)
	SKIPPED_MONTH = 3 

	months = int(raw_input(u"Please number of months: "))
	f = open("networkAnalysis.txt", u'w')
	for month in range(months):
		if month != SKIPPED_MONTH - ADJUST:
			for typeStr in [u"Close", u"Talk"]:
				degreeDist = u"{}Month_{}.clu".format(typeStr, month + ADJUST)
				network = u"{}Results_Month{}.net".format(typeStr, month + ADJUST)

				G = nx.read_pajek(network)
				G1 = nx.Graph(G)

				getDegreeDistribution(degreeDist)
				f.write(u"{}: Month {}\n".format(typeStr, month))
				f.write(u"------------------------------------------------\n")
				f.write(u"Degree density: {}\n".format(getDensity(network)))
				f.write(u"Eccentricity: {}\n".format(getEccentricity(G1)))
				f.write(u"Geodesic Distance: {}\n".format(getGeodesic(G1)))
				f.write(u"Reachability: {}\n\n".format(getReachability(G1)))