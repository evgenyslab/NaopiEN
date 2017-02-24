import taskQuestions
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
    emotions = ("happy", "hope", "sad", "fear", "angry")
    # Hopeful = interested
    # fearful = worried
    # Angry = stern

    #naoMotions = BasicMotions(NAOip, NAOport) # should be able to use this...
    #genUtil = GenUtil(naoMotions)


    ###-----------End VARIABLE SETUP
    if True:
        for x in trainingQuestions.questionList:
            print x[2]
        raw_input("STOP HERE")
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
    print 'Task Sequence: ', taskSequence, '\t historgram: ', taskQCount
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
    raw_input("BREAK")
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


if __name__ == '__main__':
    main()
