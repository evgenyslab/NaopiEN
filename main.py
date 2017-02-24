from naoqi import ALBroker
from naoqi  import ALProxy

import FileUtilitiy
from BasicMotions import BasicMotions
from DietFitnessFSM import DietFitnessFSM
from GenUtil import GenUtil
import NAOReactionChecker
from ThreadedCheckers import ThreadedChecker
from UserAffectGenerator import UserAffectGenerator
import json
import atexit
import time
import numpy as np
import random
import datetime
import csv


class Parser:
    import sys
    def __init__(self):
        pass

    @staticmethod
    def getChar(str="Please enter char: ", cRange = ('a','b','c')):
        ask = True
        while ask:
            ret = raw_input(str)
            if len(ret) == 1 and ret in cRange:
                ask = False
            else:
                print "Input is not single char, or not in range: ", cRange
        return ret

def main():
    ###---------- VARIABLE SETUP:
    # first, generate a sequence of tasks questions
    qMax = (16,14,15)
    questionsHigh = random.sample(range(1,qMax[0]),qMax[0]-1)
    questionsMed = random.sample(range(1,qMax[1]),qMax[1]-1)
    questionsLow = random.sample(range(1,qMax[2]),qMax[2]-1)
    # number of interactions in a sequence:
    sequenceLength = 10
    # number of tasks:
    nTasks = 3
    tasks = ('H','M','L')
    logFilePath = "log.cvs"
    emotions = range(1,6)

    ###-----------End VARIABLE SETUP


    # Randomly Generated task sequence (must regen until there is good distribution of each task):
    # this part of the code should really ensure that the total sequence length is not more than the sum for all the questions for each task type
    genOk = False
    while not genOk:
        genOk = True
        taskSequence = [np.random.choice(range(1,nTasks+1)) for x in range(0,sequenceLength)]
        for x in range(1,nTasks+1):
            if taskSequence.count(x) == 0:
                genOk = False
    print taskSequence
    # print task names
    taskArray = [tasks[x-1] for x in taskSequence]
    print taskArray
    # now need to sample the questions based for each task with no repeats:
    qS2 = range(sequenceLength)
    j = np.array([0,0,0])
    for i in range(0,sequenceLength):
        if taskSequence[i] == 1:
            qS2[i] = questionsHigh[j[0]]
            j[0] = j[0]+1
        elif taskSequence[i] == 2:
            qS2[i] = questionsMed[j[1]]
            j[1] = j[1]+1
        elif taskSequence[i] == 3:
            qS2[i] = questionsLow[j[2]]
            j[2] = j[2]+1

    print qS2
    # can do something like this to combine:
    taskQuestionSequence = [(taskArray[x]+str(qS2[x])+', ') for x in range(0,sequenceLength)]
    print taskQuestionSequence

    # open log file:
    # Write Sequence of tasks:
    # []
    for x in range(0,sequenceLength):
        # randomly draw robot emotion:
        emotion = 1
        #interactionInstance(logFilePath,emotion,taskQuestionSequence[x])

    # open log file - write end of interaction


def interactionInstance(logFilePath, emotion, question):
    # Get operator to press record to log the time for the users initial affect:
    Parser.getChar("press 'r' to record timestamp for initial affect:", 'r')
    # date-time stamp:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # write log file for initial recording of affect:
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['PRE',question,emotion, st])

    # Robot plays Question and emotion:
    ROBOT_PLAY_QUESTIONEMOTION = 0

		self.genUtil.naoEmotionalSay(sayText, self.getOENumber())

    # POST RECORDING:
    ret = Parser.getChar("press 'T' to record timestamp for POST affect with success, or 'F' for false:", ('t','f'))
    # date-time stamp:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # write log file for initial recording of affect:
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['POST',question,ret,st])


if __name__ == '__main__':
    main()
