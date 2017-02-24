from naoqi import ALBroker
from naoqi  import ALProxy

import FileUtilitiy
#from BasicMotions import BasicMotions
from BasicMotions2 import BasicMotions
from DietFitnessFSM import DietFitnessFSM
from GenUtil import GenUtil
import NAOReactionChecker
from ThreadedCheckers import ThreadedChecker
from UserAffectGenerator import UserAffectGenerator
import taskQuestions
import json
import atexit
import time
import numpy as np
import random
import datetime
import csv


def main(NAOip=[], NAOport=[], name=[]):
    ###---------- VARIABLE SETUP:
    # first, generate a sequence of tasks questions
    trainingQuestions = taskQuestions.taskQuestions()
    qMax = trainingQuestions.questionsPerTask
    questionsHigh = random.sample(range(1,qMax[0]),qMax[0]-1)
    questionsMed = random.sample(range(1,qMax[1]),qMax[1]-1)
    questionsLow = random.sample(range(1,qMax[2]),qMax[2]-1)
    # number of interactions in a sequence:
    sequenceLength = 10
    # number of tasks:
    nTasks = 3
    tasks = ('H','M','L')
    logFilePath = "log.cvs"
    emotions = ("Happy", "Hopeful", "Sad", "Fearful", "Angry")
    # Hopeful = interested
    # fearful = worried
    # Angry = stern

    naoMotions = BasicMotions(NAOip, NAOport) # should be able to use this...
    genUtil = GenUtil(naoMotions)

    # get now to stand and test vocals - looks like will work together.
   
    naoMotions.naoStand()
    naoMotions.naoSay("the quick brown fox did something.")
    naoMotions.naoShakeHead()
    #naoMotions.happyEmotion()
    raw_input("BREAK")

    ###-----------End VARIABLE SETUP


    # Randomly Generated task sequence (must regen until there is good distribution of each task):
    # this part of the code should really ensure that the total sequence length is not more than the sum for all the questions for each task type
    genOk = False
    print 'Generating uniform distribution of task questions for sequence...'
    while not genOk:
        genOk = True
        taskSequence = [np.random.choice(range(1,nTasks+1)) for x in range(sequenceLength)]
        taskQCount = np.asarray([len([x for x in range(sequenceLength) if taskSequence[x]==y]) for y in range(1,nTasks+1)])
        #print taskQCount
        if np.std(taskQCount) > 0.6:
            genOk = False
    print 'Sequence: ', taskSequence, '\t historgram: ', taskQCount
    # print task names
    taskArray = [tasks[x-1] for x in taskSequence]
    print taskArray
    # now need to sample the questions based for each task with no repeats:
    qS2 = range(sequenceLength)
    qS3 = range(sequenceLength)
    j = np.array([0,0,0])
    for i in range(sequenceLength):
        if taskSequence[i] == 1:
            qS2[i] = questionsHigh[j[0]]
            j[0] = j[0]+1
        elif taskSequence[i] == 2:
            qS2[i] = questionsMed[j[1]]
            j[1] = j[1]+1
        elif taskSequence[i] == 3:
            qS2[i] = questionsLow[j[2]]
            j[2] = j[2]+1
    # Do the same above task but inline - need lambda!
    #print [qS3[i] = questionsHigh[j[0]] for i in range(sequenceLength) if taskSequence[i]==1]
    #raw_input('')
    print qS2
    # can do something like this to combine:
    taskQuestionSequence = [(taskArray[x]+str(qS2[x])) for x in range(0,sequenceLength)]
    tqs = []
    tqs.append(taskSequence)
    tqs.append(qS2)
    print tqs # first row is the task, second row is question

    # open log file:
    # Write Sequence of tasks:
    # []
    for x in range(0,sequenceLength):
        # randomly draw robot emotion:
        emotion = 1
        interactionInstance(logFilePath,emotion,tqs[0][x],tqs[1][x],trainingQuestions)

    # open log file - write end of interaction


def interactionInstance(logFilePath, emotion, taskNum,questionNum,questionObj):
    # get question string:
    qStr = questionObj.getQuestion(taskNum,questionNum)
    # Get operator to press record to log the time for the users initial affect:
    Parser.getChar("press 'r' to record timestamp for initial affect:", 'r')
    # date-time stamp:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # write log file for initial recording of affect:
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['PRE',taskNum,questionNum,qStr,emotion, st])

    print 'Robot will ask: ', qStr
    # get speech string:
    speechSentence = []
    # Robot plays Question and emotion:
    ROBOT_PLAY_QUESTIONEMOTION = 0

	#self.genUtil.naoEmotionalSay(sayText, self.getOENumber())

    # POST RECORDING:
    ret = Parser.getChar("press 'T' to record timestamp for POST affect with success, or 'F' for false:", ('t','f'))
    # date-time stamp:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # write log file for initial recording of affect:
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['POST',taskNum,questionNum,qStr,emotion,ret,st])

def testNaoConnection(NAOip, NAOport):
    worked = False
    try:
        print NAOip, NAOport
        # naoBehavior = connectToProxy(NAOip, NAOport, "ALBehaviorManager")
        # names = naoBehavior.getInstalledBehaviors()
        # print "Names: ", names

        naoMotions = BasicMotions(NAOip, NAOport)
        print "Made Basic Motions"
        naoMotions.naoSay("Connected!")
        # naoMotions.naoSit()
        # naoMotions.naoShadeHeadSay("Hello, the connection worked!")

        testExpressions = False
        if testExpressions:
            genUtil = GenUtil(naoMotions)
            genUtil.testExpressions()

        worked = True
    except Exception as e:
        print "Connection Failed, maybe wrong IP and/or Port"
        print e

    print "Connection Test Finished"
    return worked


def connectToProxy(NAOip, NAOport, proxyName):
        try:
            proxy = ALProxy(proxyName, NAOip, NAOport)
        except Exception, e:
            print "Could not create Proxy to ", proxyName
            print "Error was: ", e
            proxy = ""

        return proxy

def getNAOIP():
    fileName = "ProgramDataFiles\_FSM_INPUT.json"
    jsInput = FileUtilitiy.readFileToJSON(fileName)
    naoIP = str(jsInput['naoIP'])
    return naoIP

def exitingProgram():
    print "Program Exiting..."

if __name__ == '__main__':
    simulated = False
    name = "NAO"
    if simulated:
        #simulated NAO
        NAOIP = "127.0.0.1"
        NAOPort = 61753
    else:
        useLuke = True
        #real NAO
        if useLuke:
            NAOIP = "luke.local"
            NAOIP = "192.168.1.37"
            name = "Luke"
        else:
            NAOIP = "leia.local"
            name = "Leia"
        #NAOIP = getNAOIP()
        #name = NAOIP[0:4]
        print "Robot Name: ", name
        NAOPort = 9559

    print("Initiated Values")

    connWorks = testNaoConnection(NAOIP, NAOPort)
    print "Connection Worked: ",connWorks
    atexit.register(exitingProgram)
    if connWorks:
        main(NAOIP, NAOPort, name)
