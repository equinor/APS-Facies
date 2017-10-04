#!/bin/env python
from xml.etree.ElementTree import Element

import copy

from src.xmlFunctions import getIntCommand, getKeyword


class APSGaussFieldJobs:
    """
    Class APSGaussFieldJobs
    Description: Keep the name of RMS petro jobs and  associated 3D property
                 parameter these jobs will create
    Public member functions:
    Constructor:     def __init__(self,ET_Tree = None, modelFileName = None,printInfo=0)

     -- Get functions ---
       def getNumberOfGFJobs(self)
       def getNumberOfGFNames(self)
       def getClassName(self)
       def getGaussFieldNames(self)
       def getGaussFieldJobNames(self)
       def getGaussFieldNamesPerJobs(self)
       def getGaussFieldIndx(self,jobName,gfName)

     -- Set functions (add/remove) --
       def addGaussFieldJob(self,jobName,gaussFieldParamNames)
       def removeGaussFieldJob(self,jobName)

     -- Check functions --
       def checkGaussFieldNameInJob(self,jobName,gfName)
       def checkGaussFieldName(self,gfName)

     -- Write xml tree functions
       def XMLAddElement(self,root)

     Private member functions:
       def __checkUniqueGaussFieldNames(self)
       def __interpretXMLTree(self,ET_Tree)

    -----------------------------------------------------------------------------------
    """

    def __init__(self, ET_Tree=None, modelFileName=None, printInfo=0):
        self.__modelFileName = modelFileName
        self.__className = 'APSGaussFieldJobs'
        self.__printInfo = printInfo
        self.__nGFNames = 0
        self.__gaussFieldNames = []
        self.__nJobs = 0
        self.__jobNames = []
        self.__gaussFieldNamesPerJob = []

        if ET_Tree is not None:
            # Search xml tree 
            self.__interpretXMLTree(ET_Tree)
            if self.__printInfo >= 3:
                print('Debug output: Call APSGaussFieldJobs init')

    # End __init__

    def __class_name(self):
        return self.__class__.__name__

    def __interpretXMLTree(self, ET_Tree):
        root = ET_Tree.getroot()

        self.__printInfo = getIntCommand(root, 'PrintInfo', 'Root',
                                         defaultValue=1,
                                         modelFile=self.__modelFileName,
                                         required=False)

        obj = getKeyword(root, 'GaussFieldJobNames', 'Root', modelFile=self.__modelFileName)

        gfJobs = obj
        gfJobList = []
        gfJobNames = []
        for jobs in gfJobs.findall('Job'):
            name = jobs.get('name')
            # Check if job name is specified previously
            if name in gfJobNames:
                raise ValueError(
                    'Error: In {}\n'
                    'Error: Gauss field RMS job name: {} is specified multiple times'
                    ''.format(self.__class_name(), name)
                )
            else:
                gfJobNames.append(name)

            gfList = []
            for gf in jobs.findall('GFParam'):
                text = gf.text
                gfName = text.strip()
                gfList.append(gfName)
            if gfList is None:
                raise ValueError(
                    'Error reading Job keyword in model file: {}\n'
                    'Error missing keyword GFParam.'
                    ''.format(self.__modelFileName)
                )
            gfJobList.append(gfList)

        if gfJobList is None:
            raise ValueError(
                'Error reading GaussFieldJobNames in model file: {}\n'
                'Error missing keyword Job.'
                ''.format(self.__modelFileName)
            )

        # List of job names
        self.__jobNames = gfJobNames

        # List of list of gauss field names (one list per job)
        self.__gaussFieldNamesPerJob = gfJobList

        for i in range(self.getNumberOfGFJobs()):
            gfList = self.__gaussFieldNamesPerJob[i]
            for j in range(len(gfList)):
                name = gfList[j]
                self.__gaussFieldNames.append(name)
        self.__nGFNames = len(self.__gaussFieldNames)
        self.__nJobs = len(self.__jobNames)
        # Check that gauss field param names are unique
        if not self.__checkUniqueGaussFieldNames():
            raise ValueError('In model file {} in command GaussFieldJobNames.\n'
                             'Specified Gaussian field names are not unique'.format(self.__modelFileName)
                             )
        if self.__printInfo >= 3:
            print('Debug output: Number of gauss field jobs: ' + str(self.__nJobs))
            print('Debug output: Number of gauss field names: ' + str(self.__nGFNames))
            print('Debug output: Job names:')
            print(repr(self.__jobNames))
            print('Debug output: Gauss field names per job: ')
            print(repr(self.__gaussFieldNamesPerJob))

    def initialize(self, gfJobNames, gfNamesPerJob, printInfo=0):
        if printInfo >= 3:
            print('Debug output: Call the initialize function in ' + self.__className)

        self.__jobNames = copy.copy(gfJobNames)
        self.__gaussFieldNamesPerJob = copy.deepcopy(gfNamesPerJob)
        if self.getNumberOfGFJobs() != len(gfNamesPerJob):
            raise ValueError(
                'Error in {}\n'
                'Error: Mismatch in input data for initialize.'
                ''.format(self.__class_name())
            )
        for i in range(self.getNumberOfGFJobs()):
            for j in range(len(self.__gaussFieldNamesPerJob[i])):
                gfName = self.__gaussFieldNamesPerJob[i][j]
                self.__gaussFieldNames.append(gfName)
        self.__nGFNames = len(self.__gaussFieldNames)
        self.__nJobs = len(self.__jobNames)

    def getNumberOfGFJobs(self):
        return len(self.__jobNames)

    def getNumberOfGFNames(self):
        return self.__nGFNames

    def getClassName(self):
        return copy.copy(self.__class_name())

    def getGaussFieldNames(self):
        return copy.copy(self.__gaussFieldNames)

    def getGaussFieldJobNames(self):
        return copy.copy(self.__jobNames)

    def getGaussFieldNamesPerJobs(self):
        return copy.deepcopy(self.__gaussFieldNamesPerJob)

    def checkGaussFieldNameInJob(self, jobName, gfName):
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

    def checkGaussFieldName(self, gfName):
        if gfName in self.__gaussFieldNames:
            return True
        else:
            return False

    def getGaussFieldIndx(self, jobName, gfName):
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

    def addGaussFieldJob(self, jobName, gaussFieldParamNames):
        # Check that the job name does not exist
        if self.__nJobs > 0:
            if jobName in self.__jobNames:
                raise ValueError(
                    'Error in {}\n'
                    'Error: Cannot add new job name with the same name as existing jobs.'
                    ''.format(self.__class_name())
                )
        # Check that the gauss field parameter names are unique not equal to existing gauss field names
        for gfName in gaussFieldParamNames:
            if gfName in self.__gaussFieldNames:
                raise ValueError(
                    'Error in {}\n'
                    'Error: There already exist a parameter with name: {} in a previously defined job.'
                    ''.format(self.__class_name(), gfName)
                )
        # If data is ok, add to data structure
        self.__jobNames.append(copy.copy(jobName))
        gfList = copy.deepcopy(gaussFieldParamNames)
        self.__gaussFieldNamesPerJob.append(gfList)
        for gfName in gaussFieldParamNames:
            self.__gaussFieldNames.append(gfName)
        self.__nJobs += 1

    def removeGaussFieldJob(self, jobName):
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

    def XMLAddElement(self, root):
        if self.__printInfo >= 3:
            print('Debug output: call XMLADDElement from ' + self.__className)

        tag = 'GaussFieldJobNames'
        elem = Element(tag)
        root.append(elem)
        gfJobListElement = elem
        for i in range(self.__nJobs):
            jobName = self.__jobNames[i]
            tag = 'Job'
            attribute = {'name': jobName}
            elem = Element(tag, attribute)
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
            for j in range(i + 1, self.__nGFNames):
                s2 = self.__gaussFieldNames[j]
                if s1 == s2:
                    found = 1
                    print('Error: In ' + self.__class_name())
                    print('Error: Gauss field name: ' + s1 + ' is specified multiple times')
                    break
        if found == 1:
            return False
        else:
            return True
            # -- End of function checkUniqueGaussFieldNames

# End class APSGaussFieldJobs
