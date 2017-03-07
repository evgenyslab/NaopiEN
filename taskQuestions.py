import numpy as np
import re

'''
Evgeny Nuger

This function reads a text file that has a task number, tab, and a question per line. If there is no tab,
then the reader will incorrectly read the line.
The questions' must be ordered by task! otherwise, the method here must change, which would be ideal for robustness

'''

class taskQuestions:
    def __init__(self,filePath = 'taskQuestions.txt'):
        #open file and read each line
        #each line needs the following format:
        # [#] question
        file = open(filePath, 'r')
        # read all lines into a list:
        lines = file.readlines()
        file.close()
        # split each line into a sublist by a tab and new line character:
        lArr =  [re.split(r'[\t\n]+',lines[x]) for x in range(0,len(lines))]
        # empty list of questions
        self.questionList = []
        taskLast = -1
        # loop over each line read
        for x in range(0,len(lArr)):
            try: # this will skip over lines with wrong formatting!
                # get the first iten in the row, should be task number
                task = int(lArr[x][0])
                if task != taskLast:
                    # this is a task counter, it increments for every question read from the same task
                    count = 1
                self.questionList.append((int(lArr[x][0]),count,lArr[x][1]))
                taskLast = task
                count +=1
            except:
                print "In parsing input Questions, line ", x, ' skipped!'

        self.nlines = len(self.questionList)
        self.nTasks = list(np.unique([self.questionList[x][0] for x in range(0,self.nlines)]))
        #print self.nTasks
        # this gets the number of questions for each task:
        self.questionsPerTask = [len([self.questionList[x][0] for x in range(0,self.nlines) if self.questionList[x][0]==y]) for y in range(1,len(self.nTasks)+1)]

        #print self.questionList
        #print self.questionsPerTask

    def getQuestion(self,taskNum=1,questionNum=1):
        # this line searchs the list of questions for a specific question number under a given task number.
        # this is used since all the questions are stored as a single list. A hash might be better to implement.
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
