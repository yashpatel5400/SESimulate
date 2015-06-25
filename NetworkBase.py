#####################################################################
# Name: Yash Patel                                                  #
# File: NetworkBase.py                                              #
# Description: Contains all the methods pertinent to the network    #
# base model, used to produce the other graphs desired to simulate  #
#####################################################################

import sys
import os
import random
from numpy import array, zeros, std, mean, sqrt

from Agent import *

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

class NetworkBase:
    #################################################################
    # Initializes the base of the network with the type it is to be #
    # i.e. SW, ER, etc... and number of coaches                     #
    #################################################################
    def __init__(self, networkType, maxCoachCount):
        if not self.NetworkBase_verifyBase(networkType, maxCoachCount):
            return None
        self.networkType = networkType
        self.maxCoachCount = maxCoachCount
        self.coachCount = 0

    #################################################################
    # Given parameters for initializing the network base, ensures   #
    # it is legal                                                   #  
    #################################################################
    def NetworkBase_verifyBase(self, networkType, maxCoachCount):
        if not isinstance(networkType, str):
            sys.stderr.write("networkType level must be of type " +
                "string (word)")
            return False

        if not isinstance(maxCoachCount, int):
            sys.stderr.write("maxCoachCount level must be of type int")
            return False
        return True

    #################################################################
    # Given a graph G, assigns it to be the graph for this network  #
    #################################################################
    def NetworkBase_setGraph(self, G):
        self.G = G

    #################################################################
    # Given dictionary of agents, assigns them for this network     #
    #################################################################
    def NetworkBase_setAgents(self, agents):
        self.Agents = agents

    #################################################################
    # Simulates updating all agents in network over a single time   #
    # step: includes updating coach presence/retention and SE. Each #
    # of the impact parameters passed in allow for sensitivity      #
    # analysis on each of the factors (i.e. coach impact helps look #
    # at, if the "effectiveness" of the coaches is different, how   #
    # would the final results vary) with default values given       #
    #################################################################
    def NetworkBase_updateAgents(self, time, timeImpact = .005, 
            coachImpact = .225, pastImpact = .025, 
            socialImpact = .015): 
        # Since we wished for update to happen synchronously, the
        # first loop determines and stores all the values to which 
        # the SE will change and the second then updates all agents

        for agentID in self.Agents:
            self.Agents[agentID].Agent_timeStep(timeImpact, coachImpact,\
                pastImpact, socialImpact, time)
        for agentID in self.Agents:
            self.Agents[agentID].SE = self.Agents[agentID].toUpdateSE

    #################################################################
    # Given a list of nodes, adds edges between all of them         #
    #################################################################
    def addEdges(self, nodeList):
        self.G.add_edges_from(nodeList)

    #################################################################
    # Given two agents in the graph, respectively with IDs agentID1 #
    # and agentID2, removes the edge between them                   #
    #################################################################
    def NetworkBase_removeEdge(self, agentID1, agentID2):
        self.G.remove_edge(agentID1, agentID2)

    #################################################################
    # Returns all the edges present in the graph associated with the#
    # network base                                                  #
    #################################################################
    def NetworkBase_getEdges(self):
        return self.G.edges()

    #################################################################
    # Returns the agent associated with the agentID specified       #
    #################################################################
    def NetworkBase_getAgent(self, agentID):
        return self.Agents[agentID]

    #################################################################
    # Returns the total number of agents in the graph associated w/ #
    # the network base                                              #
    #################################################################
    def NetworkBase_getNumAgents(self):
        return len(self.Agents)

    #################################################################
    # Returns an array of the neighbors of a given agent in graph   #
    #################################################################
    def NetworkBase_getNeighbors(self, agent):
        agentID = agent.agentID
        return nx.neighbors(self.G, agentID)

    #################################################################
    # Returns an array comprised of the exercising levels for all   #
    # the neighbors of a given agent                                #
    #################################################################
    def NetworkBase_getNeighborsExercise(self, agent):
        neighbors = self.NetworkBase_getNeighbors(agent)
        exerNeighbors = []
        for neighbor in neighbors:
            curNeighbor = self.Agents[neighbor]
            exerNeighbors.append(curNeighbor.\
                Agent_getExercisePts(curNeighbor))
        return exerNeighbors

    #################################################################
    # Returns an array comprised of the exercising levels for all   #
    # the agents in the network                                     #
    ################################################################# 
    def NetworkBase_getPopExercise(self, isOld = False):
        exerPop = []
        if not isOld:
            for agent in self.Agents:
                curAgent = self.Agents[agent]
                exerPop.append(curAgent.Agent_getExercisePts\
                    (curAgent.Agent_getHours()))
        else:
            for agent in self.Agents:
                curAgent = self.Agents[agent]
                exerPop.append(curAgent.Agent_getOldExercisePts\
                    (curAgent.Agent_getHours()))
        return exerPop

    #################################################################
    # Determines the number of nodes with coaches present in the    #
    # graph associated with this network base                       #
    #################################################################
    def NetworkBase_getNumCoaches(self):
        return len(getCoachAgents(self))

    #################################################################
    # Returns an array of all the agents with coaches in the network#
    #################################################################
    def NetworkBase_getCoachAgents(self):
        coachAgents = []
        for agent in self.Agents:
            if self.Agents[agent].hasCoach:
                coachAgents.append(self.Agents[agent])
        return coachAgents

    #################################################################
    # Returns an array of all agents without coaches in the network #
    #################################################################
    def NetworkBase_getNonCoachAgents(self):
        coachAgents = []
        for agent in self.Agents:
            if not self.Agents[agent].hasCoach:
                coachAgents.append(self.Agents[agent])
        return coachAgents

    #################################################################
    # Returns the mean exercise level for the local network, having #
    # all those directly connected (neighbors) to a given agent     #
    #################################################################
    def NetworkBase_getMeanLocalExercise(self, agent):
        exerNeighbors = self.NetworkBase_getNeighborsExercise(agent)
        return mean(exerNeighbors)

    #################################################################
    # Returns the mean exercise level for entire network. If want   #
    # for previous time tick (old), pass in True for isOld (default #
    # value is False)                                               #
    #################################################################
    def NetworkBase_getMeanPopExercise(self, isOld = False):
        exerPop = self.NetworkBase_getPopExercise()
        return mean(exerPop)

    #################################################################
    # Returns the standard deviation for the exercise level of the  #
    # entire network. If want for previous time tick (old), pass in #
    # True for isOld (default value is False)                       #
    #################################################################
    def NetworkBase_getStdPopExercise(self, isOld = False):
        exerPop = self.NetworkBase_getPopExercise()
        return std(exerPop)

    #################################################################
    # Returns the mean SE level for the population network          #
    #################################################################
    def NetworkBase_getMeanPopSE(self):
        agentsSE = []
        for agentID in self.Agents:
            agent = self.NetworkBase_getAgent(agentID)
            agentsSE.append(agent.SE)
        return mean(agentsSE)

    #################################################################
    # Assigns to each nodes the appropriate visual attributes, with #
    # those nodes with wellness coaches given a color of red and    #
    # those without blue along with an opacity corresponding to SE  #
    #################################################################
    def NetworkBase_addVisualAttributes(self):
        # Iterate through each of the nodes present in the graph and
        # finds respective agent
        for agentID in self.G.nodes():
            curAgent = self.Agents[agentID]
            if not curAgent.hasCoach:
                self.G.node[agentID]['color'] = 'red'
            else:
                self.G.node[agentID]['color'] = 'blue'
            self.G.node[agentID]['opacity'] = curAgent.SE

    #################################################################
    # Provides graphical display of the population, color coded to  #
    # illustrate who does and doesn't have the wellness coaches and #
    # sized proportional to the level of exercise. Pass in True for #
    # toShow to display directly and False to save for later view   #
    # with the fileName indicating the current timestep simulated.  #
    # pos provides the initial layout for the visual display        #
    #################################################################
    def NetworkBase_visualizeNetwork(self, toShow, time, pos):
        self.NetworkBase_addVisualAttributes()

        plt.figure(figsize=(12,12))
        for node in self.G.nodes():
            nx.draw_networkx_nodes(self.G,pos, nodelist=[node], 
                node_color=self.G.node[node]['color'],
                node_size=500, alpha=self.G.node[node]['opacity'])
        nx.draw_networkx_edges(self.G,pos,width=1.0,alpha=.5)

        plt.title("SE Network at Time {}".format(time))
        plt.savefig("Results\\TimeResults\\timestep{}.png".format(time))
        if toShow: 
            plt.show()
        plt.close()