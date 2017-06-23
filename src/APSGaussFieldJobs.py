#!/bin/env python
import sys
import copy
import xml.etree.ElementTree as ET
from  xml.etree.ElementTree import Element, SubElement, dump

# Class APSGaussFieldJobs
# Description: Keep the name of RMS petro jobs and  associated 3D property 
#              parameter these jobs will create
#
# Public member functions:
# Constructor:     def __init__(self,ET_Tree = None, modelFileName = None,printInfo=0)
#
#  -- Get functions ---
#    def getNumberOfGFJobs(self)
#    def getNumberOfGFNames(self)
#    def getClassName(self)
#    def getGaussFieldNames(self)
#    def getGaussFieldJobNames(self)
#    def getGaussFieldNamesPerJobs(self)
#    def getGaussFieldIndx(self,jobName,gfName)
#
#  -- Set functions (add/remove) --
#    def addGaussFieldJob(self,jobName,gaussFieldParamNames)
#    def removeGaussFieldJob(self,jobName)
#
#  -- Check functions --
#    def checkGaussFieldNameInJob(self,jobName,gfName)
#    def checkGaussFieldName(self,gfName)
#
#  -- Write xml tree functions
#    def XMLAddElement(self,root)
#
#  Private member functions:
#    def __checkUniqueGaussFieldNames(self)
#    def __interpretXMLTree(self,ET_Tree)
#
# -----------------------------------------------------------------------------------

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class APSGaussFieldJobs:

    def __init__(self,ET_Tree = None, modelFileName = None,printInfo=0):
        self.__className = 'APSGaussFieldJobs'
        self.__printInfo = printInfo
        self.__nGFNames = 0
        self.__gaussFieldNames = []
        self.__nJobs = 0
        self.__jobNames = []
        self.__gaussFieldNamesPerJob = []


        if ET_Tree == None:
            return

        # Search xml tree for model file to find the specified zone and mainLevelFacies
        self.__interpretXMLTree(ET_Tree)
        if self.__printInfo >= 3:
            print('Debug output: Call APSGaussFieldJobs init')
        return
    # End __init__


    def __interpretXMLTree(self,ET_Tree):
        root = ET_Tree.getroot()

        kw = 'PrintInfo'
        obj =  root.find(kw)
        if obj == None:
            # Default value is set
            self.__printInfo = 1
        else:
            text = obj.text
            self.__printInfo = int(text.strip())

        kw = 'GaussFieldJobNames'
        obj = root.find(kw)
        if obj == None:
            print('Error reading ' + modelFileName)
            print('Error missing command: ' + kw)
            sys.exit()

        gfJobs = obj
        gfJobList = []
        gfJobNames = []
        for jobs in gfJobs.findall('Job'):
            name = jobs.get('name')
            # Check if job name is specified previously
            if name in gfJobNames:
                print('Error: In ' + self.__className)
                print('Error: Gauss field RMS job name: ' + name + ' is specified multiple times')
                sys.exit()
            else:
                gfJobNames.append(name)

            gfList = []
            for gf in jobs.findall('GFParam'):
                text = gf.text
                gfName = text.strip()
                gfList.append(gfName)
            if gfList == None:
                print('Error reading Job keyword in model file: ' + modelFileName)
                print('Error missing keyword GFParam')
                sys.exit()
            gfJobList.append(gfList)

        if gfJobList == None:
            print('Error reading ' + 'GaussFieldJobNames' + ' in model file: ' + modelFileName)
            print('Error missing keyword Job')
            sys.exit()

        
        # List of job names
        self.__jobNames = gfJobNames
        self.__nJobs = len(self.__jobNames)

        # List of list of gauss field names (one list per job)
        self.__gaussFieldNamesPerJob = gfJobList

        for i in range(self.__nJobs):
            gfList = self.__gaussFieldNamesPerJob[i]
            for j in range(len(gfList)):
                name = gfList[j]
                self.__gaussFieldNames.append(name)
        self.__nGFNames = len(self.__gaussFieldNames)

        # Check that gauss field param names are unique
        if not self.__checkUniqueGaussFieldNames():
            sys.exit()

        return


    def initialize(self,gfJobNames,gfNamesPerJob):
        self.__nJobs = len(gfJobNames)
        self.__jobNames = copy.copy(gfJobNames)
        self.__gaussFieldNamesPerJob = copy.deepcopy(gfNamesPerJob)
        if self.__nJobs != len(gfNamesPerJob):
            print('Error in ' + self.__className)
            print('Error: Mismatch in input data for initialize')
            sys.exit()
        for i in range(self.__nJobs):
            for j in range(len(self.__gaussFieldNamesPerJob[i])):
                gfName = self.__gaussFieldNamesPerJob[i][j]
                self.__gaussFieldNames.append(gfName)
        self.__nGFNames =  len(self.__gaussFieldNames)
        return

    def getNumberOfGFJobs(self):
        return self.__nJobs

    def getNumberOfGFNames(self):
        return self.__nGFNames

    def getClassName(self):
        return copy.copy(self.__className)

    def getGaussFieldNames(self):
        return copy.copy(self.__gaussFieldNames)

    def getGaussFieldJobNames(self):
        return copy.copy(self.__jobNames)

    def getGaussFieldNamesPerJobs(self):
        return copy.deepcopy(self.__gaussFieldNamesPerJob)

    def checkGaussFieldNameInJob(self,jobName,gfName):
        found = 0
        for i in range(len(self.__jobNames)):
            jName = self.__jobNames[i]
            if jName == jobName:
                for j in range(len(self.__gaussFieldNamesPerJob[i])):
                    gName = self.__gaussFieldNamesPerJob[i][j]
                    if gName == gfName:
                        found = 1
                        break
                if found == 1:
                    break
        if found == 1:
            return True
        else:
            return False

    def checkGaussFieldName(self,gfName):
        if gfName in self.__gaussFieldNames:
            return True
        else:
            return False

    def getGaussFieldIndx(self,jobName,gfName):
        found = 0
        for i in range(len(self.__jobNames)):
            jName = self.__jobNames[i]
            if jName == jobName:
                for j in range(len(self.__gaussFieldNamesPerJob[i])):
                    gName = self.__gaussFieldNamesPerJob[i][j]
                    if gName == gfName:
                        found = 1
                        indx = j
                        break
                if found == 1:
                    break
        if found == 1:
            return indx
        else:
            print('Error: Cannot find specified gauss field name for specified job name.')
            return -999


    def addGaussFieldJob(self,jobName,gaussFieldParamNames):
        # Check that the job name does not exist
        err = 0
        if self.__nJobs > 0:
            if jobName in self.__jobNames:
                print('Error in ' + self.__className)
                print('Error: Cannot add new job name with the same name as existing jobs')
                err = 1
        if err == 0:
            # Check that the gauss field parameter names are unique not equal to existing gauss field names
            for gfName in gaussFieldParamNames:
                if gfName in self.__gaussFieldNames:
                    print('Error in ' + self.__className)
                    print('Error: There already exist a parameter with name: ' + gfName + ' in a previously defined job')
                    err = 1
                    break
            # If data is ok, add to data structure
            if err == 0:
                self.__jobNames.append(copy.copy(jobName))
                gfList = copy.deepcopy(gaussFieldParamNames)
                self.__gaussFieldNamesPerJob.append(gfList)
                for gfName in gaussFieldParamNames:
                    self.__gaussFieldNames.append(gfName)
                self.__nJobs += 1

        return err

    def removeGaussFieldJob(self,jobName):
        for i in range(len(self.__jobNames)):
            jobN = self.__jobNames[i]
            if jobN == jobName:
                # Remove from list
                gfNames = self.__gaussFieldNamesPerJob[i]
                for name in gfNames:
                    for j in range(len(self.__gaussFieldNames)):
                        name2 = self.__gaussFieldNames[j]
                        if name2 == name:
                            # Remove
                            self.__gaussFieldNames.pop(j)
                            break
                # Remove
                self.__gaussFieldNamesPerJob.pop(i)
                self.__jobNames.pop(i)
                self.__nJobs -= 1
                break
        return

    def XMLAddElement(self,root):
            
        tag = 'GaussFieldJobNames'
        elem = Element(tag)
        root.append(elem)
        gfJobListElement = elem
        for i in range(self.__nJobs):
            jobName = self.__jobNames[i]
            tag = 'Job'
            attribute = {'name':jobName}
            elem = Element(tag,attribute)
            gfJobListElement.append(elem)
            jobElement = elem
            for j in range(len(self.__gaussFieldNamesPerJob[i])):
                gfName = self.__gaussFieldNamesPerJob[i][j]
                tag = 'GFParam'
                elem = Element(tag)
                elem.text = ' ' + gfName.strip() + ' '
                jobElement.append(elem)
        return
        

    def __checkUniqueGaussFieldNames(self):
        found = 0
        for i in range(self.__nGFNames):
            s1 = self.__gaussFieldNames[i]
            for j in range(i+1,self.__nGFNames):
                s2 = self.__gaussFieldNames[j]
                if s1 == s2:
                    found = 1
                    print('Error: In ' + self.__className)
                    print('Error: Gauss field name: ' + s1 + ' is specified multiple times')
                    break
        if found == 1:
            return False
        else:
            return True
    # -- End of function checkUniqueGaussFieldNames


# End class APSGaussFieldJobs
