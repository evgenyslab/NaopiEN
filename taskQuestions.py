import numpy as np
import re


class taskQuestions:
    def __init__(self,filePath = 'taskQuestions.txt'):
        #open file and read each line
        #each line needs the following format:
        # [#] question
        file = open(filePath, 'r')
        lines = file.readlines()
        file.close()
        lArr =  [re.split(r'[\t\n]+',lines[x]) for x in range(0,len(lines))]
        #print len(lArr)
        self.questionList = []
        for x in range(0,len(lArr)):
            self.questionList.append((int(lArr[x][0]),x+1,lArr[x][1]))

        self.nlines = len(lArr)
        self.nTasks = list(np.unique([self.questionList[x][0] for x in range(0,self.nlines)]))
        #print self.nTasks
        # this gets the number of questions for each task:
        self.questionsPerTask = [len([self.questionList[x][0] for x in range(0,self.nlines) if self.questionList[x][0]==y]) for y in range(1,len(self.nTasks)+1)]

        #print self.questionsPerTask

    def getQuestion(self,taskNum=1,questionNum=1):
        str = [ self.questionList[x][2] for x in range(0,self.nlines) if self.questionList[x][0]==taskNum and self.questionList[x][1]==questionNum]
        if not str:
            print 'Question does not exits'
            return -1
        else:
            return str


'''
if __name__ == '__main__':
    obj = taskQuestions('taskQuestions.txt')
    obj.getQuestion(1,20)
'''
