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

def main(NAOip=[], NAOport=[], name=[]):
    ###---------- VARIABLE SETUP:
    # first, generate a sequence of tasks questions
    trainingQuestions = taskQuestions.taskQuestions()
    qMax = trainingQuestions.questionsPerTask
    questionsHigh = random.sample(range(1,qMax[0]),qMax[0]-1)
    questionsMed = random.sample(range(1,qMax[1]),qMax[1]-1)
    questionsLow = random.sample(range(1,qMax[2]),qMax[2]-1)
    # number of interactions in a sequence:
    sequenceLength = 20
    # number of tasks:
    nTasks = 3
    tasks = ('H','M','L')
    logFilePath = "log.cvs"
    emotions = ("happy", "hope", "sad", "fear", "anger")
    # Hopeful = interested
    # fearful = worried
    # Angry = stern

    naoMotions = BasicMotions(NAOip, NAOport) # should be able to use this...
    genUtil = GenUtil(naoMotions)

    # get now to stand and test vocals - looks like will work together.
    naoMotions.naoStand()
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
    #---------- Generate emotion list:
    genOk = False
    print 'Generating uniform distribution of emotions questions for sequence...'
    while not genOk:
        genOk = True
        emotionSequence = [np.random.choice(range(0,len(emotions))) for x in range(sequenceLength)]
        emotionCount = np.asarray([len([x for x in range(sequenceLength) if emotionSequence[x]==y]) for y in range(len(emotions))])
        #print taskQCount
        if (np.std(emotionCount) > 0.6) or len([y for y in range(len(emotionCount)) if emotionCount[y]==0])>0:
            genOk = False
    emotionSequenceText = [emotions[emotionSequence[y]] for y in range(len(emotionSequence))]
    print 'Emotion Sequence: ', emotionSequenceText, '\t historgram: ', emotionCount
    # print task names
    taskArray = [tasks[x-1] for x in taskSequence]
    # print taskArray
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

    #DEBUG MOTIONS & Speech:
    if False:
        testingStr = 'This is a test'
        for x in emotions:
            if x == 'happy':
                formattedSentence = naoMotions.naoSayEmotion(testingStr,x, True)
                naoMotions.sayAndPlay(x,formattedSentence,1)
                naoMotions.sayAndPlay(x,formattedSentence,2)
            elif x== 'hope':
                formattedSentence = naoMotions.naoSayEmotion(testingStr,x, True)
                naoMotions.sayAndPlay(x,formattedSentence,1)
            elif x=='sad':
                formattedSentence = naoMotions.naoSayEmotion(testingStr,x, True)
                naoMotions.sayAndPlay(x,formattedSentence,1)
                naoMotions.sayAndPlay(x,formattedSentence,2)
            elif x=='fear':
                formattedSentence = naoMotions.naoSayEmotion(testingStr,x, True)
                naoMotions.sayAndPlay(x,formattedSentence,1)
                naoMotions.sayAndPlay(x,formattedSentence,2)
            elif x=='anger':
                formattedSentence = naoMotions.naoSayEmotion(testingStr,x, True)
                naoMotions.sayAndPlay(x,formattedSentence,1)
                naoMotions.sayAndPlay(x,formattedSentence,2)
        raw_input("DEBUG MOTIONS")

    #DEBUG MOTION ONLY
    if False:
        while 1:
            for x in emotions:
                if x == 'happy':
                    naoMotions.sayAndPlay(x,[],1)
                    naoMotions.sayAndPlay(x,[],2)
                elif x== 'hope':
                    naoMotions.sayAndPlay(x,[]],1)
                elif x=='sad':
                    naoMotions.sayAndPlay(x,[],1)
                    naoMotions.sayAndPlay(x,[],2)
                elif x=='fear':
                    naoMotions.sayAndPlay(x,[],1)
                    naoMotions.sayAndPlay(x,[],2)
                elif x=='anger':
                    naoMotions.sayAndPlay(x,[],1)
                    naoMotions.sayAndPlay(x,[],2)
            raw_input("DEBUG MOTIONS: PRESS ENTER TO REPEAT")

    #DEBUG TEXT
    if False:
        for x in trainingQuestions.questionList:
            sentence = x[2]
            naoMotions.naoSayEmotion(sentence,'happy')
            #naoMotions.naoSayEmotion(sentence,'hope')
            naoMotions.naoSayEmotion(sentence,'sad')
            #naoMotions.naoSayEmotion(sentence,'fear')
            naoMotions.naoSayEmotion(sentence,'anger')
            raw_input("DEBUG MOTIONS")

    #
    # Do the same above task but inline - need lambda!
    #print [qS3[i] = questionsHigh[j[0]] for i in range(sequenceLength) if taskSequence[i]==1]
    #raw_input('')
    #print qS2
    # can do something like this to combine:
    #taskQuestionSequence = [(taskArray[x]+str(qS2[x])) for x in range(0,sequenceLength)]
    # 2xn array of task + question...maybe this should be 3xn with emotion too...
    tqs = []
    tqs.append(taskSequence)
    tqs.append(qS2)
    # print tqs # first row is the task, second row is question
    # open log file:
    # Write Sequence of tasks:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['NEW INTERACTION SEQUENCE','TASK SECQUENCE','QUESTION SEQUENCE','EMOTION SEQUENCE', st])
        writer.writerow(['NEW INTERACTION SEQUENCE',taskSequence,qS2,emotionSequenceText, st])



    for x in range(0,sequenceLength):
        # randomly draw robot emotion:
        interactionInstance(naoMotions,genUtil,logFilePath,emotionSequenceText[x],tqs[0][x],tqs[1][x],trainingQuestions,x)

    # open log file - write end of interaction
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['END OF INTERACTION SEQUENCE',taskSequence,qS2,emotionSequenceText, st])
        writer.writerow(['END OF INTERACTION SEQUENCE','TASK SECQUENCE','QUESTION SEQUENCE','EMOTION SEQUENCE', st])

    # ENDING THANKYOUS
    naoMotions.naoStand()
    formattedSentence = naoMotions.naoSayEmotion('Thank you for participating','happy', True)
    naoMotions.sayAndPlay('happy',formattedSentence)



def interactionInstance(naoMotions,genUtil,logFilePath, emotion, taskNum,questionNum,questionObj, interactionNumber):
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
        writer.writerow([interactionNumber,'PRE',taskNum,questionNum,qStr,emotion, st])

    print 'Robot will ask: ', qStr[0], '\nWith Emotion: ', emotion
    #print 'Question: ' interactionNumber
    loopback = True
    while loopback:
        formattedSentence = naoMotions.naoSayEmotion(qStr[0],emotion, True)
        naoMotions.sayAndPlay(emotion,formattedSentence)

        #naoMotions.setEyeEmotion('hope')
        # POST RECORDING:
        ret = Parser.getChar("To record timestamp for POST use (t,f) for (true/false), q to repeat:", ('t','f','q'))
        if ret != 'q':
            loopback = False
    #naoMotions.naoStand()
    # date-time stamp:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # write log file for initial recording of affect:
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([interactionNumber,'POST',taskNum,questionNum,qStr,emotion,ret,st])

def testNaoConnection(NAOip, NAOport):
    worked = False
    try:
        print NAOip, NAOport
        # naoBehavior = connectToProxy(NAOip, NAOport, "ALBehaviorManager")
        # names = naoBehavior.getInstalledBehaviors()
        # print "Names: ", names

        naoMotions = BasicMotions(NAOip, NAOport)
        print "Made Basic Motions"
        # naoMotions.naoSay("Connected!")
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
