''' 
=====================================================================
TO CHANGE
=====================================================================
- Constant in time decay function
- Constant in Agent_pastUpdate
- Constant in Agent_socialUpdate
- Gamma in Coach_update
- Normalization '''

#####################################################################
# Name: Yash Patel                                                  #
# File: Agent.py                                                    #
# Description: Object file containing all the methods modelling the #
# agents present in the simulation. Agents comprise the individuals #
# of the simulation, of which the self-efficacy and exercise were   #
# the main takeaways                                                #
#####################################################################

import sys
import os
import random
import numpy as np

from Coach import *
from NetworkBase import *

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

#####################################################################
# Used to create several agents to produce the agents en masse for  #
# the setup of the simulation                                       #
#####################################################################
class AgentFactory(object):
    def AgentFactory_createAgent(network, agentID):
        oldSE = np.random.normal(.5, .15)
        SE = np.random.normal(.5, .15)
        hasCoach = int(random.random() * 2)

        oldLowLevel = int(10.0 * oldSE)
        lowLevel = int(10.0 * SE)
        
        oldMedLevel = int(10.0 * oldSE ** 2)
        medLevel = int(10.0 * SE ** 2)
        
        oldHighLevel = int(10.0 * oldSE ** 3)
        highLevel = int(10.0 * SE ** 3)

        agent = Agent(SE, network, agentID, hasCoach, lowLevel, \
            medLevel, highLevel, oldLowLevel, oldMedLevel, oldHighLevel)
        return agent

#####################################################################
# Agents are the constituent objects that comprise the simulation:  #
# model the individuals (people) involved in the exercise/housing   #
#####################################################################
class Agent:

    #################################################################
    # Given the SE (self-efficacy), a boolean determining whether or#
    # not an agent has a wellness coach, and the levels of exercise #
    # (for low, medium, and high), creates an agent with properties #
    #################################################################
    def __init__(self, SE, network, agentID, hasCoach, lowLevel, \
            medLevel, highLevel, oldLowLevel, oldMedLevel, oldHighLevel):
        if not self.Agent_verifyAgent(SE, hasCoach, lowLevel, \
            medLevel, highLevel, agentID, oldLowLevel, oldMedLevel, \
            oldHighLevel):
            return None

        self.SE = SE
        self.oldSE = 0.0

        self.hasCoach = hasCoach

        self.lowLevel = lowLevel
        self.oldLowLevel = oldLowLevel

        self.medLevel = medLevel
        self.oldMedLevel = oldMedLevel

        self.highLevel = highLevel
        self.oldHighLevel = oldHighLevel    

        self.agentID = agentID
        self.network = network.networkBase

        if self.hasCoach:
            self.network.coachCount += 1

    #################################################################
    # Given the parameters for initializing the agent, determines   #
    # whether or not they are legal.                                #  
    #################################################################
    def Agent_verifyAgent(self, SE, hasCoach, lowLevel, medLevel, \
        highLevel, agentID, oldLowLevel, oldMedLevel, oldHighLevel):
        if not isinstance(SE, float):
            sys.stderr.write("Self-efficacy level must be of type " +
                "double/float")
            return False

        if not isinstance(hasCoach, int):
            sys.stderr.write("hasCoach must be of type boolean " +
                "(True/False)")
            return False

        if  not isinstance(lowLevel, int) or \
            not isinstance(medLevel, int) or \
            not isinstance(highLevel, int):
            sys.stderr.write("Exercise levels must be of type int")
            return False

        if  not isinstance(oldLowLevel, int) or \
            not isinstance(oldMedLevel, int) or \
            not isinstance(oldHighLevel, int):
            sys.stderr.write("Old exercise levels must be of type int")
            return False

        if not isinstance(agentID, int):
            sys.stderr.write("Agent ID must be of type int")
            return False

        # Self-efficacy must be scaled to a 1.0 scale
        if SE < 0.0 or SE > 1.0:
            sys.stderr.write("Self-efficacy level must be in the " +
                "range of 0.0-1.0")
            return False
        return True

    #################################################################
    # Used for initialization of ASF network: determines to which   #
    # nodes a given agent will attach (based on connection density).#
    # Please note: the following function was taken from Steve      #
    # Mooney's Obesagent ASFNetwork.py program                      #
    #################################################################
    def Agent_preferentiallyAttach(self, network, nConnections):
        candidate_nodes = network.G.nodes()
        
        # Reorder candidates to ensure randomness
        random.shuffle(candidate_nodes)
        target_nodes = []

        # Double edge count to get per-node edge count.
        edge_count = len(network.G.edges(candidate_nodes))*2

        # Pick a random number
        rand = random.random()
        p_sum = 0.0
        
        # To add edges per the B-A algorithm, we compute probabilities
        # for each node multiplying by nConnections, then partition the
        # probability space per the probabilities.  Every time we find a
        # match, we add one to the random number.  So, for example, suppose we
        # have four nodes with p1=0.5, p2=0.75, p3=0.5 and p4=0.25.  If our
        # random number is 0.38, we'll first pick node 1, since 0 < .38 < .5,
        # then skip node 2, since 1.38 > 1.25 (=0.5+0.75), then pick node 3,
        # since 1.25 < 1.38 < 1.75, then skip node 4, since 2.38 > 2.0

        # Note that because we randomized candidates above, the selection is
        # truly random.

        for i in range(len(candidate_nodes)):
            candidate_node = candidate_nodes[i]
            candidate_edges = network.G.edges(candidate_node)
            p_edge = nConnections*1.0*len(candidate_edges)/edge_count
            low = p_sum
            high = p_sum+p_edge
            test = rand + len(target_nodes)
            if (test > low and test <= high):
                target_nodes.append(candidate_node)
            p_sum += p_edge

        node_list = [self.agentID]*len(target_nodes)
        edges_to_add = zip(node_list, target_nodes)
        network.networkBase.addEdges(edges_to_add)

    #################################################################
    # Normalizes the SE level onto a 1.0 scale                      #
    #################################################################
    def Agent_normalizeSE(self):
        if self.toUpdateSE > 1.0:
            self.toUpdateSE = 1.0

    #################################################################
    # Provides change over one time tick of the SE for a given agent#
    #################################################################
    def Agent_getSEChange(self):
        return self.SE - self.oldSE

    #################################################################
    # Determines and returns the expected number of hours (in one   #
    # time tick) to be exercised based on the SE level of agent     #
    #################################################################
    def Agent_getHours(self):
        # 36 hours was assumed to correspond to an SE of 1.0 (as
        # such corresponds to 3 hrs/day, unlikely for seniors)
        MAX_HOURS = 36
        return self.SE * MAX_HOURS

    #################################################################
    # Determines the number of exercise points for a given agent,   #
    # based on the determined formula of 2 pt/hrs for low exercise, #
    # 3 pts/hr for medium, and 5 pts/hr for high.                   #
    #################################################################
    def Agent_getExercisePts(self, hrs):
        return 2 * self.lowLevel \
            + 3 * self.medLevel + 5 * self.highLevel

    #################################################################
    # Similarly determines exercise pts for previous week (old)     #
    #################################################################
    def Agent_getOldExercisePts(self, hrs):
        return 2 * self.oldLowLevel \
            + 3 * self.oldMedLevel + 5 * self.oldHighLevel

    #################################################################
    # Returns array of exercise levels (format: [low, medium, high])#
    #################################################################
    def Agent_getExerciseLevels(self):
        return [self.lowLevel, self.medLevel, self.highLevel]

    #################################################################
    # Used to update the values for the exercise levels (low, med,  #
    # and high) to correspond to the new SE value determined        #
    #################################################################
    def Agent_updateExerciseLevels(self):
        # Updated by, Ex_t = floor(10.0 * SE^t), where t = 1 is low,
        # 2 is medium, and 3 is high
        self.oldLowLevel = self.lowLevel
        self.lowLevel = int(10.0 * self.SE)
        
        self.oldMedLevel = self.medLevel
        self.medLevel = int(10.0 * self.SE ** 2)
        
        self.oldHighLevel = self.highLevel
        self.highLevel = int(10.0 * self.SE ** 3)
        
    #################################################################
    # Makes the agent acquire a coach (if not already present).     #
    #################################################################
    def Agent_addCoach(self):
        self.hasCoach = True
        self.network.coachCount += 1

    #################################################################
    # Makes the agent release its coach (if already present).       #
    #################################################################
    def Agent_removeCoach(self):
        self.hasCoach = False
        self.network.coachCount -= 1

    #################################################################
    # Determines whether, for a given agent, there is a coach in the#
    # network.                                                      #
    #################################################################
    def Agent_netHasCoach(self):
        neighbors = self.network.NetworkBase_getNeighbors(self)
        for neighbor in neighbors:
            if self.network.NetworkBase_getAgent(neighbor).hasCoach:
                return True
        return False

    #################################################################
    # Given an agent and the current time in ticks of the simulation#
    # decays the self-efficacy extent depending on whether or not   #
    # agent has a wellness coach.                                   #
    #################################################################
    def Agent_timeUpdate(self, time):
        const = .005
        if not self.hasCoach: 
            const *= 2.0
        self.toUpdateSE = self.toUpdateSE * (1 + time) ** (-const)
        return

    #################################################################
    # Given a particular agent, updates its SE based resulting from #
    # the presence (or lack thereof) of a coach                     #
    #################################################################
    def Agent_coachUpdate(agent):
        SE = agent.toUpdateSE
        gamma = .225

        agentHasCoach = agent.hasCoach
        if SE >= .5 and agentHasCoach:
            newSE = SE + (1 - SE) * gamma 
        elif SE < .5 and agentHasCoach:
            newSE = SE * (1 + gamma)
        else:
            newSE = SE

        agent.toUpdateSE = newSE

    #################################################################
    # Given a particular agent, changes its SE based on whether or  #
    # not his given exercise level was above or below (by >= 1/2 std#
    # dev) the population avg                                       #
    #################################################################
    def Agent_pastUpdate(self):
        meanOld = self.network.NetworkBase_getMeanPopExercise(True)
        stdOld = self.network.NetworkBase_getStdPopExercise(True)

        # Determines the number of hours expected to have exercised
        # in the two-week span and finds corresponding pts for #hrs
        curPt = self.Agent_getOldExercisePts(self.Agent_getHours())
        self.Agent_updateExerciseLevels()

        const = .025

        if (curPt - meanOld)/stdOld >= .25:
            self.toUpdateSE = (1 + const) * self.toUpdateSE
        else: 
            self.toUpdateSE = (1 - const) * self.toUpdateSE

    #################################################################
    # Given a particular agent, changes its SE based on whether or  #
    # not the average exercise level of his connected network was   #
    # above or below (by >= 1/2 std dev) the population avg         #
    #################################################################
    def Agent_socialUpdate(self):
        meanLocal = self.network.NetworkBase_getMeanLocalExercise(self)
        meanPop = self.network.NetworkBase_getMeanPopExercise()
        stdPop = self.network.NetworkBase_getStdPopExercise()
        
        const = .015

        if (meanLocal - meanPop)/stdPop >= .25:
            self.toUpdateSE = (1 + const) * self.toUpdateSE
        else: 
            self.toUpdateSE = (1 - const) * self.toUpdateSE

    #################################################################
    # From the proposal, "functions will be applied in the          # 
    # following "order: decay, coaching, past-exercise, social      #
    # network." Given an agent and current time (in ticks), new SE  #
    # is determined.                                                #
    #################################################################
    def Agent_updateSE(self, time):
        self.oldSE = self.SE

        # toUpdateSE will be used for all the calculations and then
        # (after ALL agents toUpdates have been calculated) will be
        # used to update SE: simulates "simultaneous change"
        self.toUpdateSE = self.SE

        self.Agent_timeUpdate(time)
        self.Agent_coachUpdate()
        self.Agent_pastUpdate()
        self.Agent_socialUpdate()

    #################################################################
    # Simulates change in the agent over a single time step given   #
    # the current time (in ticks) of simulation: includes updating  #
    # coach presence/retention and SE                               #
    #################################################################
    def Agent_timeStep(self, time):
        Coach_acquireCoachWithProb(self)
        Coach_keepCoachWithProb(self)
        self.Agent_updateSE(time)
        self.Agent_normalizeSE()