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

# This class is custom written to parse input text.
class Parser:
    import sys
    def __init__(self):
        pass

    '''
    A @staticmethod means that this function can be called without initializing
    a class object, i.e. you can call this function in another piece of code as:
    Parser.getChat(string,charaterList)
    the string is the prompt string that will show up during runtime, the
    charaterList is a list of charaters that the user can choose from. If none
    of the available charatecters are input, the method rethrows the question.
    '''
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
    # first, generate a sequence of tasks questions using taskQuestions.py:
    trainingQuestions = taskQuestions.taskQuestions()
    # get list of questions / task
    qMax = trainingQuestions.questionsPerTask
    # Create a random integer array of pointers to unique questions for each task:
    questionsHigh = random.sample(range(1,qMax[0]),qMax[0]-1)
    questionsMed = random.sample(range(1,qMax[1]),qMax[1]-1)
    questionsLow = random.sample(range(1,qMax[2]),qMax[2]-1)
    # number of interactions in a sequence:
    sequenceLength = 20
    # number of tasks - this should all be returned from taskQuestions.py:
    nTasks = 3
    tasks = ('H','M','L')
    logFilePath = "log.cvs"
    emotions = ("happy", "hope", "sad", "fear", "anger")
    # Hopeful = interested
    # fearful = worried
    # Angry = stern

    # initialize Nao class objects for motion, etc!
    naoMotions = BasicMotions(NAOip, NAOport) # should be able to use this...
    genUtil = GenUtil(naoMotions)

    # get now to stand and test vocals - looks like will work together.
    naoMotions.naoStand()
    ###-----------End VARIABLE SETUP


    # Randomly Generated task sequence (must regen until there is good distribution of each task):
    # this part of the code should really ensure that the total sequence length is not more than the sum for all the questions for each task type
    genOk = False
    print 'Generating uniform distribution of task questions for sequence...'
    # WARNING: THIS CAN GET STUCK IN INIFNITE LOOP IF THE NUMBER OF TASKS IS TOO LARGE AND THE NUMBER OF QUESTIONS ITS TOO SMALL!
    while not genOk:
        genOk = True
        # this line generates a sequence of tasks by rangdomly sampling the tasks for the total number of interactions in the sequeunce:
        taskSequence = [np.random.choice(range(1,nTasks+1)) for x in range(sequenceLength)]
        # this line counts how many of each task there is in the task sequence
        taskQCount = np.asarray([len([x for x in range(sequenceLength) if taskSequence[x]==y]) for y in range(1,nTasks+1)])
        # Check the standard deviation of the taskQCount, a high std.div means the task distribution is not uniform
        if np.std(taskQCount) > 0.6:
            genOk = False # this is false until the task distribution is uniform
            # NOTE: in certain cases, this condition may endlessly fail if the sequence length is too short or there are too many different tasks
    print 'Sequence: ', taskSequence, '\t historgram: ', taskQCount
    #---------- Generate emotion list:
    genOk = False
    print 'Generating uniform distribution of emotions questions for sequence...'
    # This part of the code does the same thing as above, for for randomly distrubted emotions
    # WARNING: THIS CAN GET STUCK IN INIFNITE LOOP IF THE NUMBER OF EMOTIONS IS TOO LARGE AND THE NUMBER OF QUESTIONS ITS TOO SMALL!
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
    # basically, for each question of a task, this process samples the randomly ordered questions from the task question list per task. This could be made more efficient/robust.
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
                    naoMotions.sayAndPlay(x,[],1)
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

    # Initialize a sequence list of tasks and questions.
    tqs = []
    tqs.append(taskSequence)
    tqs.append(qS2)
    # print tqs # first row is the task, second row is question
    # open log file:
    # Write Sequence of tasks for beginning of interaction
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    with open(logFilePath, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['NEW INTERACTION SEQUENCE','TASK SECQUENCE','QUESTION SEQUENCE','EMOTION SEQUENCE', st])
        writer.writerow(['NEW INTERACTION SEQUENCE',taskSequence,qS2,emotionSequenceText, st])


    # For each question in the sequence, run interaction instance with NAO:
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

    # ENDING THANK YOUS
    naoMotions.naoStand()
    formattedSentence = naoMotions.naoSayEmotion('Thank you for participating','happy', True)
    naoMotions.sayAndPlay('happy',formattedSentence)



def interactionInstance(naoMotions,genUtil,logFilePath, emotion, taskNum,questionNum,questionObj, interactionNumber):
    # get question string:
    qStr = questionObj.getQuestion(taskNum,questionNum)
    # Get operator to press record to log the time for the users initial affect, this will act as a code stop until the teleoperated presses 'r':
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
    loopback = True # this is a repeat loop-back that will allow the nao to repeat questions
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

# test connection method from old code:
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

# from old code
def connectToProxy(NAOip, NAOport, proxyName):
        try:
            proxy = ALProxy(proxyName, NAOip, NAOport)
        except Exception, e:
            print "Could not create Proxy to ", proxyName
            print "Error was: ", e
            proxy = ""

        return proxy

# from old code
def getNAOIP():
    fileName = "ProgramDataFiles\_FSM_INPUT.json"
    jsInput = FileUtilitiy.readFileToJSON(fileName)
    naoIP = str(jsInput['naoIP'])
    return naoIP

#from old code
def exitingProgram():
    print "Program Exiting..."

# Main Function, mostly from old code
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
            #NAOIP = "192.168.1.37"
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
