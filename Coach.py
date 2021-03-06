''' 
=====================================================================
TO CHANGE
=====================================================================
- Constant in Probability function (PBase and const)
- Constant in keepCoach '''

#####################################################################
# Name: Yash Patel                                                  #
# File: Coach.py                                                    #
# Description: Contains all the methods pertinent to the wellness   #
# coaches present in the simulation. Behaviors include maintaining  #
# self-efficacy levels and exercise in the network of agents        #
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

#####################################################################
# Given a particular agent, determines their probability of         #
# getting a coach (based on connected agents in network and SE)     #
#####################################################################
def Coach_getCoachProbability(agent):
    pBase = .25
    const = .25
    return (1 - agent.SE) * const + pBase

#####################################################################
# Given a particular agent, determines their probability of         #
# keeping a coach (based on changes in SE due to the presence of    #
# an agent and current SE)                                          #
#####################################################################
def Coach_keepCoachProbability(agent):
    pBase = .75
    delta = agent.Agent_getSEChange()
    return agent.SE * delta + pBase

#####################################################################
# Given a particular agent, acquires a coach with probability       #
# determined by SE and network                                      #
#####################################################################
def Coach_acquireCoachWithProb(agent):
    # print("Current: {}".format(agent.network.coachCount))
    # print("Max: {}".format(agent.network.maxCoachCount))

    # Accounts for the case where all of the coaches have been taken
    if agent.network.coachCount >= agent.network.maxCoachCount:
        return

    if agent.hasCoach:
        return
    prob = Coach_getCoachProbability(agent)
    rand = random.random()
    if rand < prob:
        agent.Agent_addCoach()

#####################################################################
# Given a particular agent, keep a coach with probability           #
# determined by SE and changes caused by coach                      #
#####################################################################
def Coach_keepCoachWithProb(agent):
    if not agent.hasCoach:
        return
    prob = Coach_keepCoachProbability(agent)
    rand = random.random()
    if rand > prob:
        agent.Agent_removeCoach()