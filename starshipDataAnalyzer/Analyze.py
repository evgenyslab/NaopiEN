import csv
import time as t
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os.path




def importCSVFile(fileName):
    csvList = []
    try:
        with open(fileName, 'rb') as f:
            reader = csv.reader(f)
            csvList = list(reader)
    except Exception as e:
        print "Something went wrong reading the file: ", fileName
        print e

    return csvList

def printCSVList(csvList):
    for row in csvList:
        print row

def makeNewList(csvList, cols):
    newList = []
    colNums = getColNumsFromNames(cols)
    # print colNums
    for row in csvList:
        newRow = [row[i] for i in colNums]
        newList.append(newRow)
    return newList

def formatAffectList(csvList):
    affectLogTitles = {'feature1':0, 'feature2':1,'feature3':2,'feature4':3,'feature5':4,'feature6':5,'feature7':6,'feature8':7,
                       'BV':8, 'BA':9, 'vV':10, 'vA':11, 'MV':12, 'MA':13, 'absTime':14, 'usedV':15}
    affectLogTitles.update({'time':16, 'VV':17, 'VA':18})

    newRow = []
    timeStart = t.mktime(dt.datetime.strptime(csvList[0][affectLogTitles['absTime']], "%Y-%m-%d %H:%M:%S.%f").timetuple())
    for row in csvList:
        vV = row[affectLogTitles['vV']]
        vA = row[affectLogTitles['vA']]
        usedV = row[affectLogTitles['usedV']]
        VV = "_"
        VA = "_"
        if usedV == '1':
            VV = vV
            VA = vA
        absTime = row[affectLogTitles['absTime']]
        time = t.mktime(dt.datetime.strptime(absTime, "%Y-%m-%d %H:%M:%S.%f").timetuple()) - timeStart
        newRow.append(row + [time, VV, VA])

    return newRow, timeStart

def getColNumsFromNames(colNames):
    affectLogTitles = {'feature1':0, 'feature2':1,'feature3':2,'feature4':3,'feature5':4,'feature6':5,'feature7':6,'feature8':7,
                       'BV':8, 'BA':9, 'vV':10, 'vA':11, 'MV':12, 'MA':13, 'absTime':14, 'usedV':15,
                       'time':16, 'VV':17, 'VA':18}
    colNums = [affectLogTitles[i] for i in colNames]
    return colNums

def formatRobotLog(csvList, timeStart, offsetHours = 5):
    timeStart -= (dt.timedelta(hours = offsetHours)).total_seconds()
    # print "timeStart: ", timeStart
    robotLogTitles = {'State TimeStamp': 0, 'State Date Time': 1, 'FSM State': 2,
                      'FSM State Name': 3,'Robot Emotion': 4, 'Observable Expression': 5, 'Drive Statuses': 6}
    csvData = csvList[5:]
    newRows = []
    for row in csvData:
        # print row
        RE = row[robotLogTitles['Robot Emotion']]
        OE = row[robotLogTitles['Observable Expression']]
        state = row[robotLogTitles['FSM State']]
        stateN = row[robotLogTitles['FSM State Name']][1:]
        absTime = row[robotLogTitles['State Date Time']].replace(" ", "")
        time = t.mktime(dt.datetime.strptime(absTime, "%Y-%m-%d_%H-%M-%S").timetuple()) - timeStart
        newRows.append([time, state, RE, OE, stateN])

    interactionType = csvList[1][2][len(' Daily Companion '):]
    # print '"' + interactionType + '"'
    return newRows, interactionType

def plotAffect(affectCSVList, robotCSVList, interactionType = "Morning", task=1):
    BVs = []
    BAs = []
    VVs = []
    VAs = []
    MVs = []
    MAs = []
    times = []
    timesV = []
    for row in affectCSVList:
        [bv, ba, vv, va, mv, ma, ts] = row[0:7]
        BVs += [int(bv)]
        BAs += [int(ba)]
        if vv != "_":
            VVs += [int(vv)]
            VAs += [int(va)]
            timesV += [float(ts)]
        MVs += [int(mv)]
        MAs += [int(ma)]
        times += [float(ts)]
    # print times
    AvgV = [np.mean(MVs)] * len(MVs)
    AvgA = [np.mean(MAs)] * len(MAs)
    maxTime = max(times)

    # fig = plt.figure(1)
    r = 4
    c = 1

    #
    morningAppraisals = [2,3,5,7,8,9,11,12,13,14,18,19,20,21,24,25,28,29,32,33,37,38,39,45,46,47]
    morningAppraisals = ["morningGood","morningBad","askWeatherGood","askWeatherGoodYesTravel","askWeatherGoodNoTravel",
                         "askWeatherBad","askWeatherBadSameHome","askWeatherBadDiffHome","askWeatherBadDiffHomeYesTake",
                         "askWeatherBadDiffHomeNoTake","askBreakfastAte","askDietGluten","askDietGlutenYesEat",
                         "askDietGlutenNoEat","askDietPoultryYesEat","askDietPoultryNoEat","meal2FeedbackYesDelici",
                         "meal2FeedbackNoDelici","askDietFishYesEat","askDietFishNoEat","meal3FeedbackDinner",
                         "meal3FeedbackYesGood","meal3FeedbackNoGood","exerciseFeedbackGood","exerciseFeedbackBad",
                         "exerciseFeedbackEasy"]
    endDayAppraisals = [2,3,5,6,9,10,11,12,13,14,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,39,40,41,42,43,44,45,46,47,48,49]
    endDayAppraisals = ["dayEndGood","dayEndBad","askWeekendYes","askWeekendNo","meal1CheckinYesAte",
                        "meal1CheckinYesAteYesReg","meal1CheckinYesAteNoReg","meal1CheckinNoAte",
                        "meal1CheckinNoAteYesHad","meal1CheckinNoAteNoHad","meal2CheckinYesAte","meal2CheckinYesAteGood",
                        "meal2CheckinYesAteBad","meal2CheckinNoAte","meal2CheckinNoAteYesComp",
                        "meal2CheckinNoAteYesCompYesResp","meal2CheckinNoAteDontknowComp","meal2CheckinNoAteNoComp",
                        "meal3CheckinYesHad","meal3CheckinYesAte","meal3CheckinYesAteGood","meal3CheckinYesAteBad",
                        "meal3CheckinNoAte","meal3CheckinNoAteYesComp","meal3CheckinNoAteDontknowComp",
                        "meal3CheckinNoAteNoComp","meal3CheckinNoHad","exerciseCheckinYesDid",
                        "exerciseCheckinYesDidGoodDiff","exerciseCheckinYesDidHardDiff","exerciseCheckinYesDidEasyDiff",
                        "exerciseCheckinNoDid","exerciseCheckinNoDidYesComp","exerciseCheckinNoDidYesCompGotResp",
                        "exerciseCheckinNoDidNoComp","exerciseCheckinNoDidNoCompCouldnt",
                        "exerciseCheckinNoDidNoCompDidntWant","exerciseCheckinDontknowDid"]

    REs = []
    OEs = []
    times = []
    aREs = []
    aOEs = []
    atimes = []
    last_stn = ""
    last_re = 0
    last_oe = 0
    for row in robotCSVList:
        [ts, st, re, oe, stn] = row
        if (interactionType == "Morning" and stn in morningAppraisals) or (
            interactionType == "End of Day" and stn in endDayAppraisals) or (
            stn == last_stn):
            aREs += [int(re)]
            aOEs += [int(oe)]
            atimes += [float(ts)]
            REs += [int(last_re)]
            OEs += [int(last_oe)]
            times += [float(ts)-0.1]
        REs += [int(re)]
        OEs += [int(oe)]
        times += [float(ts)]
        last_stn = stn
        last_re = re
        last_oe = oe

    ###### make new plots

    #fig2 = plt.figure(2,figsize=(8.5,5.6))
    timeStart = times[0]
    timeEnd = times[-1]
    # print timeStart, ' ', timeEnd
    want_Square = False
    MVs = []
    MAs = []
    last_v = 0
    last_a = 0
    aff_times = []
    for row in affectCSVList:
        [bv, ba, vv, va, mv, ma, ts] = row[0:7]
        if float(ts) >= timeStart and float(ts) <= timeEnd:
            if want_Square:
                MVs += [last_v]
                MAs += [last_a]
                aff_times += [float(ts) - timeStart - 0.1]
            MVs += [int(mv)]
            MAs += [int(ma)]
            aff_times += [float(ts) - timeStart]
            last_v = int(mv)
            last_a = int(ma)
    AvgV = [np.mean(MVs)] * len(MVs)
    AvgA = [np.mean(MAs)] * len(MAs)

    AvgV = [0.911764705882] * len(MVs)
    AvgA = [0.161764705882] * len(MAs)


    for t in range(len(times)):
        times[t] -= timeStart
    for t in range(len(atimes)):
        atimes[t] -= timeStart
    # print times
    # print REs
    # print OEs
    REOEs, ts = colourREplotData(times, REs, OEs)
    # need to trim REOEs that are <0
    eTimePoints = [ts[x] for x in range(len(ts)) if ts[x]>=0]
    R2 =  [[REOEs[y][x] for x in range(len(ts)) if ts[x] in eTimePoints] for y in range(10)]
    # raw_input("PAUSE")
    emotionsShort = ['happy','interested','sad','worried','stern']
    emotions =emotionsShort*2


    h, i, s, w, a, h2, i2, s2, w2, a2, sc1, sc2, sc3 = REOEs

    # so TS is the time step for REOEs
    # outputArray = [V,A,prevEmotion,V',A',currentEmotion]
    if (len(eTimePoints)>len(aff_times)):
        print "less affect measurments ADD CODE"
        pass
        # raw_input("NEED TO ADD CODE HERE")
        # there are more emotion measurements than affect measurements
        numMeasure = len(aff_times)-2
        outputArray = []

        for x in range(1,numMeasure):
            # first should reduce MAs and MVs to same length as numMeasure by
            # making sure time stamps are closest
            timeCurrent = aff_times[x]
            timeMatch = min(eTimePoints, key=lambda y:abs(y-timeCurrent))
            timeIdx = [y for y in range(len(eTimePoints)) if eTimePoints[y]==timeMatch]
            # first, find the emotion at the time,
            currentEmotions = [emotions[y] for y in range(10) if REOEs[y][x] != None]
            # now get previous emotion:
            previousEmotions = [emotions[y] for y in range(10) if REOEs[y][x-1] != None]
            var = [timeCurrent,timeMatch,MVs[timeIdx[0]],MAs[timeIdx[0]],currentEmotions[0],previousEmotions[0],MVs[timeIdx[0]+1],MAs[timeIdx[0]+1]]
            # check if delta affect is >=0
            if (var[6]-var[2])>=0 and (var[7]-var[3])>=0:
                if not outputArray:
                    outputArray.append(var)
                else:
                    # check if any current values in var[2:] are different from last outputArray[prev][2:], if yes, then append
                    prevIdx = len(outputArray)-1
                    # print outputArray[prevIdx],'\n',var
                    if [True for y in range(2,8) if var[y]!=outputArray[prevIdx][y]]:
                        outputArray.append(var)
                    # outputArray[prevIdx]
                    # print len(outputArray),'\n'
        outData = []
        for x in outputArray:
            # this is csv formatted
            # print x
            # print [[y for y in range(0,5) if x[5]==emotionsShort[y]][0]+1]
            outData.append([[y for y in range(0,5) if x[5]==emotionsShort[y]][0]+1,x[2]+2,x[3]+2,x[4]])

        # print outData

        with open('elog.csv', 'a') as csvfile:
            for x in outData:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(x)

    else:
        print "less emotion measurements"
        #there are more affect measurements then emotion measurements, USE
        # EMOTION MEASUREMENTS
        numMeasure = len(eTimePoints)-2
        outputArray = []
        # print aff_times
        # print eTimePoints
        for x in range(1,numMeasure):
            # first should reduce MAs and MVs to same length as numMeasure by
            # making sure time stamps are closest
            timeCurrent = eTimePoints[x]
            timeMatch = min(aff_times, key=lambda y:abs(y-timeCurrent))
            timeIdx = [y for y in range(len(aff_times)) if aff_times[y]==timeMatch]
            # first, find the emotion at the time,
            currentEmotions = [emotions[y] for y in range(10) if REOEs[y][x] != None]
            # now get previous emotion:
            previousEmotions = [emotions[y] for y in range(10) if REOEs[y][x-1] != None]
            var = [timeCurrent,timeMatch,MVs[timeIdx[0]],MAs[timeIdx[0]],currentEmotions[0],previousEmotions[0],MVs[timeIdx[0]+1],MAs[timeIdx[0]+1]]
            # check if delta affect is >=0
            if (var[6]-var[2])>=0 and (var[7]-var[3])>=0:
                if not outputArray:
                    outputArray.append(var)
                else:
                    # check if any current values in var[2:] are different from last outputArray[prev][2:], if yes, then append
                    prevIdx = len(outputArray)-1
                    # print outputArray[prevIdx],'\n',var
                    if [True for y in range(2,8) if var[y]!=outputArray[prevIdx][y]]:
                        outputArray.append(var)
                    # outputArray[prevIdx]
                    # print len(outputArray),'\n'
        outData = []
        for x in outputArray:
            # this is csv formatted
            # print x
            # print [[y for y in range(0,5) if x[5]==emotionsShort[y]][0]+1]
            outData.append([task,[y for y in range(0,5) if x[5]==emotionsShort[y]][0]+1,x[2]+2,x[3]+2,x[4]])

        # print outData

        with open('elog.csv', 'a') as csvfile:
            for x in outData:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(x)





def colourREplotData(times, REs, OEs):
    REOEs = [[],[],[],[],[],[],[],[],[],[],[],[],[]]
    ts = []
    last_re = 0
    for t in range(len(times)):
        re = REs[t]
        oe = OEs[t]
        REOEs[oe].append(last_re)
        REOEs[oe].append(re)
        for r in range(13):
            if r != oe:
                REOEs[r].append(None)
                REOEs[r].append(None)
        ts += [times[t]-0.1,times[t]]
        last_re = re

    return REOEs, ts

if __name__ == '__main__':
    offsetHours = 5
    for x in range(1,32):
        affectFileNameM = "%02d_u_m.csv" %(x,)
        robotFileNameM = "%02d_r_m.csv" %(x,)
        affectFileNameE = "%02d_u_e.csv" %(x,)
        robotFileNameE = "%02d_r_e.csv" %(x,)

        if os.path.isfile(affectFileNameM) and os.path.isfile(robotFileNameM):
            task = 1
            affectFileName = affectFileNameM
            robotFileName = robotFileNameM
        elif os.path.isfile(affectFileNameE) and os.path.isfile(robotFileNameE):
            task = 2
            affectFileName = affectFileNameE
            robotFileName = robotFileNameE
        print task, affectFileName, robotFileName
        try:
            affectLog = importCSVFile(affectFileName)
            colsWant = ['BV', 'BA', 'vV', 'vA', 'MV', 'MA', 'absTime', 'usedV']
            affectLogAV = makeNewList(affectLog, colsWant)
            colsWant = ['BV', 'BA', 'VV', 'VA', 'MV', 'MA', 'time', 'usedV']
            affectLog, startTime = formatAffectList(affectLog)
            affectLogAV = makeNewList(affectLog, colsWant)
            robotLog = importCSVFile(robotFileName)
            robotLog, interactionType = formatRobotLog(robotLog, startTime, offsetHours)
            plotAffect(affectLogAV, robotLog, interactionType, task)
        except:
            print "something went wrong with user: ", x
    print "Done"
