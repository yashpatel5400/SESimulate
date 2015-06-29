#####################################################################
# Name: Yash Patel                                                  #
# File: SESimulation.py                                             #
# Description: Contains all the methods pertinent to producing the  #
# simulation for modelling the relation between SE and exercise     #
# levels in the form of an ABM (agent-based model)                  #
#####################################################################

import sys
import os
import csv
import random,itertools
from copy import deepcopy
import numpy as np

from NetworkBase import NetworkBase
from ERNetwork import ERNetwork
from SWNetwork import SWNetwork
from ASFNetwork import ASFNetwork

from SensitivitySimulations import *

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

class SEModel:
    #################################################################
    # Given a network type (defaults to ASF network), the timespan  #
    # in years, and sensitivity to the different update methods,    #
    # produces an SE simulation object. The default values for the  #
    # impact parameters are as follow: timeImpact = .005,           #
    # coachImpact = .225, pastImpact = .025, socialImpact = .015    #
    #################################################################
    def __init__(self, timeImpact=.005, coachImpact=.225, 
            pastImpact=.025, socialImpact=.015, networkType='ASF', \
            timeSpan=10, numAgents=10, numCoaches = 10):
        if not self.SEModel_verifySE(timeImpact, coachImpact, 
            pastImpact, socialImpact, networkType, timeSpan, \
            numAgents, numCoaches):
            return None

        self.timeImpact = timeImpact
        self.coachImpact = coachImpact
        self.pastImpact = pastImpact
        self.socialImpact = socialImpact

        self.networkType = networkType
        self.timeSpan = timeSpan
        self.numAgents = numAgents
        self.numCoaches = numCoaches

        self.SEModel_setNetwork()
        
    #################################################################
    # Based on the specified value of the network type, generates   #
    # and sets the network accordingly                              #
    #################################################################
    def SEModel_setNetwork(self):
        if self.networkType == 'ER':
            self.network = ERNetwork(self.numAgents, self.numCoaches, \
                10.0/self.numAgents, )
        elif self.networkType == 'SW':
            self.network = SWNetwork(self.numAgents, self.numCoaches, \
                10, 0.0)
        else:
            self.network = ASFNetwork(self.numAgents, self.numCoaches,\
                9, 7)

    #################################################################
    # Given parameters for initializing the simulation, ensures they#
    # are legal                                                     # 
    #################################################################
    def SEModel_verifySE(self, timeImpact, coachImpact, 
            pastImpact, socialImpact, networkType, timeSpan, \
            numAgents, numCoaches):
        if not isinstance(networkType, str):
            sys.stderr.write("Network type must be of type string")
            return False

        if networkType != 'SW' and networkType != 'ASF'\
            and networkType != 'ER':
            sys.stderr.write("Network type must either SW, ASF, or ER")
            return False

        if not isinstance(timeSpan, int): 
            sys.stderr.write("Time span must be of type int")
            return False
            
        if not isinstance(numAgents, int): 
            sys.stderr.write("Number of agents must be of type int")
            return False

        if not isinstance(numCoaches, int): 
            sys.stderr.write("Number of coaches must be of type int")
            return False

        if not isinstance(timeImpact, float): 
            sys.stderr.write("timeImpact must be of type float")
            return False

        if not isinstance(coachImpact, float): 
            sys.stderr.write("coachImpact must be of type float")
            return False

        if not isinstance(pastImpact, float): 
            sys.stderr.write("pastImpact must be of type float")
            return False

        if not isinstance(socialImpact, float): 
            sys.stderr.write("socialImpact must be of type float")
            return False

        return True

    #################################################################
    # Writes the header of the CSV file to be given as output in the#
    # specified file                                                #
    #################################################################
    def SEModel_writeSimulationHeader(self, resultsFile):
        if resultsFile is not None:
            columns = ['time', 'agent_id','has_coach', 'lowLevel', \
                'medLevel', 'highLevel', 'exercise_pts', 'SE']
            with open(resultsFile, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
    
    #################################################################
    # Writes the current data/parameters corresponding to each agent#
    # in the network at the current time step, given the current    #
    # time in the simulation and the file to be written to          #
    #################################################################
    def SEModel_writeSimulationData(self, time, resultsFile):
        if resultsFile is not None:
            with open(resultsFile, 'a') as f:
                writer = csv.writer(f)
                Agents = self.network.networkBase.Agents
                for agent in Agents:
                    curAgent = Agents[agent]
                    exLevels = curAgent.Agent_getExerciseLevels()
                    row = [time, curAgent.agentID,                  \
                    	curAgent.hasCoach, exLevels[0],             \
                    	exLevels[1], exLevels[2],                   \
                        curAgent.Agent_getExercisePts(), curAgent.SE]
                    writer.writerow(row)

    #################################################################
    # Creates a bar graph comparing two specified values (val1,val2)#
    # outputting result into file with fileName. Uses label, title  #
    # for producing the graph                                       #
    #################################################################
    def SEModel_createBarResults(self, val1, val2, fileName, label, 
            title):
        N = len(val1)

        ind = np.arange(N)  # the x locations for the groups
        width = 0.25        # the width of the bars
        fig, ax = plt.subplots()

        rects1 = ax.bar(ind, val1, width, color='r')
        rects2 = ax.bar(ind+width, val2, width, color='b')

        # add some text for labels, title and axes ticks
        ax.set_ylabel("Agent ID")
        ax.set_ylabel(label)
        ax.set_title(title)
        ax.set_xticks(ind+width)

        labels = []
        for i in range(0, N):
            curWord = str(i + 1)
            labels.append(curWord)

        ax.set_xticklabels(labels)
        ax.legend( (rects1[0], rects2[0]), ('Before', 'After') )
        plt.savefig("Results\\TimeResults\\" + fileName + ".png")
        plt.close()

    #################################################################
    # Runs simulation over the desired timespan and produces/outputs#
    # results in CSV file specified along with displaying graphics  #
    #################################################################
    def SEModel_runSimulation(self, resultsFile):
        self.SEModel_writeSimulationHeader(resultsFile)

        # Converts from years to "ticks" (represent 2 week span)
        numTicks = self.timeSpan * 26
        pos = nx.random_layout(self.network.G)
        
        SEBefore = []
        ExBefore = []
        for curAgent in self.network.Agents:
            agent = self.network.networkBase.\
                NetworkBase_getAgent(curAgent)
            SEBefore.append(agent.SE)
            ExBefore.append(agent.Agent_getExercisePts())

        for i in range(0, numTicks):
            if i % 10 == 0:
                print("Plotting time step " + str(i))
                self.network.networkBase.\
                    NetworkBase_visualizeNetwork(False, i, pos)

            # Updates the agents in the network base and copies those
            # to the network
            self.network.networkBase.NetworkBase_updateAgents(i, \
                self.timeImpact, self.coachImpact, self.pastImpact, \
                self.socialImpact)
            self.network.Agents = self.network.networkBase.Agents

            self.SEModel_writeSimulationData(i, resultsFile)    

        SEAfter = []
        ExAfter = []
        for curAgent in self.network.Agents:
            agent = self.network.networkBase.\
                NetworkBase_getAgent(curAgent)
            SEAfter.append(agent.SE)
            ExAfter.append(agent.Agent_getExercisePts())

        # Creates bar graphs of change in SE, exercise for individuals
        self.SEModel_createBarResults(SEBefore, SEAfter, \
            "BarSEResults", "SE", "SE Before/After")
        self.SEModel_createBarResults(ExBefore, ExAfter, \
            "BarExResults", "Exercise Pts", "Exercise Pts Before/After")

    #################################################################
    # Runs simulation over the desired timespan without producing   #
    # visible output: used for sensitivity analysis                 #
    #################################################################
    def SEModel_runStreamlineSimulation(self):
        numTicks = self.timeSpan * 26

        for i in range(0, numTicks):
            # Updates the agents in the network base and copies those
            # to the network
            self.network.networkBase.NetworkBase_updateAgents(i, \
                self.timeImpact, self.coachImpact, self.pastImpact, \
                self.socialImpact)
            self.network.Agents = self.network.networkBase.Agents

#####################################################################
# Given the paramters of the simulation (upon being prompted on)    #
# command line, runs simulation, outputting a CSV with each time    #
# step and a graphical display corresponding to the final iteration #
#####################################################################
if __name__ == "__main__":
    # Get all input for initializing simulation

    # ER, SW, or ASF
    networkType = "ER"
    timeSpan = 10
    numAgents = 25
    numCoaches = 10

    # Defaults for the impact values are as follow: 
    # timeImpact = .005, coachImpact = .225, pastImpact = .025
    # socialImpact = .015. Feel free to change as desired below
    # for sensitivity analysis (automated by displaySensitive below)
    
    timeImpact = 0.005 
    coachImpact = 0.225
    pastImpact = 0.025
    socialImpact = 0.015

    displaySensitive = True

    resultsFile = "Results\\TimeResults\\results.csv"
    simulationModel = SEModel(timeImpact, coachImpact, pastImpact, \
       socialImpact, networkType, timeSpan, numAgents, numCoaches)
    simulationModel.SEModel_runSimulation(resultsFile)

    # Runs alternative simulations for depicting effect of changing
    # parameters on overall results -- Done before actual simulation
    # due to bug in graphical display
    if displaySensitive:
        Sensitivity_sensitivitySimulation(networkType, timeSpan, \
            numAgents, numCoaches, timeImpact, coachImpact, \
            pastImpact, socialImpact)

    print("Terminating simulation...")