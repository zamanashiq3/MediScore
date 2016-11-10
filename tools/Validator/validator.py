#TODO: try __version__
"""
* File: validate.py
* Date: 09/23/2016
* Translation by: Daniel Zhou
* Original Author: Yooyoung Lee
* Status: Complete 

* Description: This object validates the format of the input of the 
  system output along with the index file. It empirically verifies the 

* Requirements: This code requires the following packages:
    - cv2
    - numpy
    - pandas
  
  The rest should be available on your system.

* Inputs
    * -x, inIndex: index file name
    * -s, inSys: system output file name
    * -vt, valType: validator type: SSD or DSD
    * -v, verbose: Control printed output. -v 0 suppresss all printed output except argument parsng errors, -v 1 to print all output.

* Outputs
    * 0 if the files are validly formatted, 1 if the files are not.

* Disclaimer: 
This software was developed at the National Institute of Standards 
and Technology (NIST) by employees of the Federal Government in the
course of their official duties. Pursuant to Title 17 Section 105 
of the United States Code, this software is not subject to copyright 
protection and is in the public domain. NIST assumes no responsibility 
whatsoever for use by other parties of its source code or open source 
server, and makes no guarantees, expressed or implied, about its quality, 
reliability, or any other characteristic."
"""

import sys
import os
import cv2
import numpy as np
import pandas as pd
import unittest as ut
import contextlib
from abc import ABCMeta, abstractmethod

verbose=None
if verbose==1:
    def printq(mystring,iserr=False):
        print(mystring)
elif verbose==0:
    printq = lambda *x : None
else:
    def printq(mystring,iserr=False):
        if iserr:
            print(mystring)

class validator:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self,sysfname,idxfname): pass
    @abstractmethod
    def nameCheck(self): pass
    @abstractmethod
    def contentCheck(self): pass
    def fullCheck(self):
        if self.nameCheck() == 1:
            return 1

        printq("Checking if index file is a pipe-separated csv...")
        idx_pieces = self.idxname.split('.')
        idx_ext = idx_pieces[-1]

        if idx_ext != 'csv':
            printq("ERROR: Your index file should have csv as an extension! (It is separated by '|', I know...)",True)
            return 1

        printq("Your index file appears to be a pipe-separated csv, for now. Hope it isn't separated by commas.")

        if self.contentCheck() == 1:
            return 1
        return 0


class SSD_Validator(validator):
    def __init__(self,sysfname,idxfname):
        self.sysname=sysfname
        self.idxname=idxfname

    def nameCheck(self):
        printq('Validating the name of the system file...')

        eflag = False
        if not os.path.isfile(self.sysname):
            printq("ERROR: I can't find your system output " + self.sysname + "! Where is it?",True)
            eflag = True
        if not os.path.isfile(self.idxname):
            printq("ERROR: I can't find your index file " + self.idxname + "! Where is it?",True)
            eflag = True
        if eflag:
            return 1

        sys_pieces = self.sysname.split('.')
        sys_ext = sys_pieces[-1]
        if sys_ext != 'csv':
            printq('ERROR: Your system output is not a csv!',True)
            return 1
    
        fileExpid = sys_pieces[-2].split('/')
        dirExpid = fileExpid[-2]
        fileExpid = fileExpid[-1]
        if fileExpid != dirExpid:
            printq("ERROR: Please follow the naming convention. The system output should follow the naming <EXPID>/<EXPID>.csv.",True)
            return 1
    
        taskFlag = 0
        teamFlag = 0
        sysPath = os.path.dirname(self.sysname)
        sysfName = os.path.basename(self.sysname)
        arrSplit = sysfName.split('_')
        #team,ncid,task,condition,sys,version = sysfName.split('_')
        team = arrSplit[0]
        ncid = arrSplit[1]
        task = arrSplit[2]
        condition = arrSplit[3]
        sys = arrSplit[4]
        version = arrSplit[5] 
    
        if ('+' in team) or (team == ''):
            printq("ERROR: The team name must not include characters + or _",True)
            teamFlag = 1
    
        if (task != 'Manipulation') and (task != 'Removal') and (task != 'Clone'):
            printq('ERROR: What kind of task is ' + task + '? It should be Manipulation, Removal, or Clone!',True)
            taskFlag = 1
    
        if (taskFlag == 0) and (teamFlag == 0):
            printq('The name of this file is valid!')
        else:
            printq('The name of the file is not valid. Please review the requirements.',True)
            return 1 

    def contentCheck(self):
        printq('Validating the syntactic content of the system output.')
        idxfile = pd.read_csv(self.idxname,sep='|')
        sysfile = pd.read_csv(self.sysname,sep='|')
    
        dupFlag = 0
        xrowFlag = 0
        scoreFlag = 0
        maskFlag = 0
        
        if sysfile.shape[1] != 3:
            printq("ERROR: The number of columns of the system output file must be equal to 3. Are you using '|' to separate your columns?",True)
            return 1

        sysHeads = list(sysfile.columns)
        allClear = True
        truelist = ["ProbeFileID","ConfidenceScore","ProbeOutputMaskFileName"]

        for i in range(0,len(truelist)):
            allClear = allClear and (truelist[i] == sysHeads[i])

        if not allClear:
            headlist = []
            properhl = []
            for i in range(0,len(truelist)):
                if sysHeads[i] != truelist[i]:
                    headlist.append(sysHeads[i])
                    properhl.append(truelist[i]) 
            printq("ERROR: Your header(s) " + ', '.join(headlist) + " should be " + ', '.join(properhl) + " respectively.",True)
            return 1
        
        if sysfile.shape[0] != sysfile.drop_duplicates().shape[0]:
            rowlist = range(0,sysfile.shape[0])
            printq("ERROR: Your system output contains duplicate rows for ProbeFileID's: "
                    + ' ,'.join(list(map(str,sysfile['ProbeFileID'][sysfile.duplicated()])))    + " at row(s): "
                    + ' ,'.join(list(map(str,[i for i in rowlist if sysfile.duplicated()[i]]))) + " after the header. I recommended you delete these row(s).",True)
            dupFlag = 1
        
        if sysfile.shape[0] != idxfile.shape[0]:
            printq("ERROR: The number of rows in the system output does not match the number of rows in the index file.",True)
            xrowFlag = 1
        
        if not ((dupFlag == 0) and (xrowFlag == 0)):
            printq("The contents of your file are not valid!",True)
            return 1
        
        sysfile['ProbeFileID'] = sysfile['ProbeFileID'].astype(str)
        sysfile['ConfidenceScore'] = sysfile['ConfidenceScore'].astype(np.float64)
        sysfile['ProbeOutputMaskFileName'] = sysfile['ProbeOutputMaskFileName'].astype(str) 

        idxfile['ProbeFileID'] = idxfile['ProbeFileID'].astype(str) 
        idxfile['ProbeHeight'] = idxfile['ProbeHeight'].astype(np.float64) 
        idxfile['ProbeWidth'] = idxfile['ProbeWidth'].astype(np.float64) 

        sysPath = os.path.dirname(self.sysname)
    
        for i in range(0,sysfile.shape[0]):
            if not (sysfile['ProbeFileID'][i] in idxfile['ProbeFileID'].unique()):
                printq("ERROR: " + sysfile['ProbeFileID'][i] + " does not exist in the index file.",True)
                printq("The contents of your file are not valid!",True)
                return 1

            #check mask validation
            probeOutputMaskFileName = sysfile['ProbeOutputMaskFileName'][i]
            if probeOutputMaskFileName in [None,'',np.nan,'nan']:
                printq("The mask for file " + sysfile['ProbeFileID'][i] + " appears to be absent. Skipping it.")
                continue
            maskFlag = maskFlag | maskCheck1(sysPath + "/" + sysfile['ProbeOutputMaskFileName'][i],sysfile['ProbeFileID'][i],idxfile)
        
        #final validation
        if (scoreFlag == 0) and (maskFlag == 0):
            printq("The contents of your file are valid!")
        else:
            printq("The contents of your file are not valid!",True)
            return 1

class DSD_Validator(validator):
    def __init__(self,sysfname,idxfname):
        self.sysname=sysfname
        self.idxname=idxfname

    def nameCheck(self):
        printq('Validating the name of the system file...')

        eflag = False
        if not os.path.isfile(self.sysname):
            printq("ERROR: I can't find your system output " + self.sysname + "! Where is it?",True)
            eflag = True
        if not os.path.isfile(self.idxname):
            printq("ERROR: I can't find your index file " + self.idxname + "! Where is it?",True)
            eflag = True
        if eflag:
            return 1

        sys_pieces = self.sysname.split('.')
        sys_ext = sys_pieces[-1]
        if sys_ext != 'csv':
            printq('ERROR: Your system output is not a csv!',True)
            return 1
    
        fileExpid = sys_pieces[-2].split('/')
        dirExpid = fileExpid[-2]
        fileExpid = fileExpid[-1]
        if fileExpid != dirExpid:
            printq("ERROR: Please follow the naming convention. The system output should follow the naming <EXPID>/<EXPID>.csv.",True)
            return 1
    
        taskFlag = 0
        teamFlag = 0
        sysPath = os.path.dirname(self.sysname)
        sysfName = os.path.basename(self.sysname)
        arrSplit = sysfName.split('_')
        team = arrSplit[0]
        ncid = arrSplit[1]
        task = arrSplit[2]
        condition = arrSplit[3]
        sys = arrSplit[4]
        version = arrSplit[5] 
    
        if '+' in team or team == '':
            printq("ERROR: The team name must not include characters + or _",True)
            teamFlag = 1
    
        if task != 'Splice':
            printq('ERROR: What kind of task is ' + task + '? It should be Splice!',True)
            taskFlag = 1
    
        if (taskFlag == 0) and (teamFlag == 0):
            printq('The name of this file is valid!')
        else:
            printq('The name of the file is not valid. Please review the requirements.',True)
            return 1 

    def contentCheck(self):
        printq('Validating the syntactic content of the system output.')
        idxfile = pd.read_csv(self.idxname,sep='|')
        sysfile = pd.read_csv(self.sysname,sep='|')

        dupFlag = 0
        xrowFlag = 0
        scoreFlag = 0
        maskFlag = 0
        
        if sysfile.shape[1] != 5:
            printq("ERROR: The number of columns of the system output file must be equal to 5. Are you using '|' to separate your columns?",True)
            return 1

        sysHeads = list(sysfile.columns)
        allClear = True
        truelist = ["ProbeFileID","DonorFileID","ConfidenceScore","ProbeOutputMaskFileName","DonorOutputMaskFileName"]

        for i in range(0,len(truelist)):
            allClear = allClear and (truelist[i] == sysHeads[i])

        if not allClear:
            headlist = []
            properhl = []
            for i in range(0,len(truelist)):
                if (sysHeads[i] != truelist[i]):
                    headlist.append(sysHeads[i])
                    properhl.append(truelist[i]) 
            printq("ERROR: Your header(s) " + ', '.join(headlist) + " should be " + ', '.join(properhl) + " respectively.",True)
            return 1
        
        if sysfile.shape[0] != sysfile.drop_duplicates().shape[0]:
            rowlist = range(0,sysfile.shape[0])
            printq("ERROR: Your system output contains duplicate rows for ProbeFileID's: " + ' ,'.join(list(sysfile['ProbeFileID'][sysfile.duplicated()])) + " at row(s): " +\
                                     ' ,'.join(list(map(str,[i for i in rowlist if sysfile.duplicated()[i]]))) + " after the header. I recommended you delete these row(s).",True)
            dupFlag = 1
        
        if sysfile.shape[0] != idxfile.shape[0]:
            printq("ERROR: The number of rows in the system output does not match the number of rows in the index file.",True)
            xrowFlag = 1
        
        if not ((dupFlag == 0) and (xrowFlag == 0)):
            printq("The contents of your file are not valid!",True)
            return 1
        
        sysfile['ProbeFileID'] = sysfile['ProbeFileID'].astype(str) 
        sysfile['ConfidenceScore'] = sysfile['ConfidenceScore'].astype(np.float64) 
        sysfile['ProbeOutputMaskFileName'] = sysfile['ProbeOutputMaskFileName'].astype(str) 

        idxfile['ProbeFileID'] = idxfile['ProbeFileID'].astype(str) 
        idxfile['ProbeHeight'] = idxfile['ProbeHeight'].astype(np.uint32) 
        idxfile['ProbeWidth'] = idxfile['ProbeWidth'].astype(np.uint32) 

        sysfile['DonorFileID'] = sysfile['DonorFileID'].astype(str) 
        sysfile['DonorOutputMaskFileName'] = sysfile['DonorOutputMaskFileName'].astype(str) 

        idxfile['DonorFileID'] = idxfile['DonorFileID'].astype(str) 
        idxfile['DonorHeight'] = idxfile['DonorHeight'].astype(np.uint32) 
        idxfile['DonorWidth'] = idxfile['DonorWidth'].astype(np.uint32) 
        
        sysPath = os.path.dirname(self.sysname)
    
        for i in range(0,sysfile.shape[0]):
            if not (sysfile['ProbeFileID'][i] in idxfile['ProbeFileID'].unique()):
                printq("ERROR: " + sysfile['ProbeFileID'][i] + " does not exist in the index file.",True)
                printq("The contents of your file are not valid!",True)
                return 1

            #First get all the matching probe rows
            rowset = idxfile[idxfile['ProbeFileID'] == sysfile['ProbeFileID'][i]].copy()
            #search in these rows for DonorFileID matches. If empty, pair does not exist. Quit status 1
            if not (sysfile['DonorFileID'][i] in rowset['DonorFileID'].unique()):
                printq("ERROR: The pair (" + sysfile['ProbeFileID'][i] + "," + sysfile['DonorFileID'][i] + ") does not exist in the index file.",True)
                printq("The contents of your file are not valid!",True)
                return 1

            #check mask validation
            probeOutputMaskFileName = sysfile['ProbeOutputMaskFileName'][i]
            donorOutputMaskFileName = sysfile['DonorOutputMaskFileName'][i]

            if (probeOutputMaskFileName in [None,'',np.nan,'nan']) or (donorOutputMaskFileName in [None,'',np.nan,'nan']):
                printq("At least one mask for the pair (" + sysfile['ProbeFileID'][i] + "," + sysfile['DonorFileID'][i] + ") appears to be absent. Skipping it.")
                continue
            maskFlag = maskFlag | maskCheck2(sysPath + "/" + probeOutputMaskFileName,sysPath + "/" + donorOutputMaskFileName,sysfile['ProbeFileID'][i],sysfile['DonorFileID'][i],idxfile,i)
        
        #final validation
        if (scoreFlag == 0) and (maskFlag == 0):
            printq("The contents of your file are valid!")
        else:
            printq("The contents of your file are not valid!",True)
            return 1

######### Functions that don't depend on validator ####################################################

def maskCheck1(maskname,fileid,indexfile):
    #check to see if index file input image files are consistent with system output
    flag = 0
    printq("Validating {} for file {}...".format(maskname,fileid))
    mask_pieces = maskname.split('.')
    mask_ext = mask_pieces[-1]
    if mask_ext != 'png':
        printq('ERROR: Mask image {} for FileID {} is not a png. Make it into a png!'.format(maskname,fileid),True)
        return 1
    if not os.path.isfile(maskname):
        printq("ERROR: " + maskname + " does not exist! Did you name it wrong?",True)
        return 1
    baseHeight = list(map(int,indexfile['ProbeHeight'][indexfile['ProbeFileID'] == fileid]))[0] 
    baseWidth = list(map(int,indexfile['ProbeWidth'][indexfile['ProbeFileID'] == fileid]))[0]
    dims = cv2.imread(maskname,cv2.IMREAD_UNCHANGED).shape

    if len(dims)>2:
        printq("ERROR: {} is not single-channel. Make it single-channel.".format(maskname),True)
        flag = 1

    if (baseHeight != dims[0]) or (baseWidth != dims[1]):
        printq("Dimensions for ProbeImg of ProbeFileID {}: {},{}".format(fileid,baseHeight,baseWidth),True)
        printq("Dimensions of mask {}: {},{}".format(maskname,dims[0],dims[1]),True)
        printq("ERROR: The mask image's length and width do not seem to be the same as the base image's.",True)
        flag = 1
        
    #maskImg <- readPNG(maskname) #EDIT: expensive for only getting the number of channels. Find cheaper option
    #note: No need to check for third channel. The imread option automatically reads as grayscale.

    if flag == 0:
        printq(maskname + " is valid.")

    return flag

def maskCheck2(pmaskname,dmaskname,probeid,donorid,indexfile,rownum):
    #check to see if index file input image files are consistent with system output
    flag = 0
    printq("Validating probe and donor mask pair({},{}) for ({},{}) pair at row {}...".format(pmaskname,dmaskname,probeid,donorid,rownum))

    #check to see if index file input image files are consistent with system output
    pmask_pieces = pmaskname.split('.')
    pmask_ext = pmask_pieces[-1]
    if pmask_ext != 'png':
        printq('ERROR: Probe mask image {} for pair ({},{}) at row {} is not a png. Make it into a png!'.format(pmaskname,probeid,donorid,rownum),True)
        return 1

    dmask_pieces = dmaskname.split('.')
    dmask_ext = dmask_pieces[-1]
    if dmask_ext != 'png':
        printq('ERROR: Donor mask image {} for pair ({},{}) at row {} is not a png. Make it into a png!'.format(dmaskname,probeid,donorid,rownum),True)
        return 1
    #TODO: revise all strings to format notation

    #check to see if png files exist before doing anything with them.
    eflag = False
    if not os.path.isfile(pmaskname):
        printq("ERROR: " + pmaskname + " does not exist! Did you name it wrong?",True)
        eflag = True
    if not os.path.isfile(dmaskname):
        printq("ERROR: " + dmaskname + " does not exist! Did you name it wrong?",True)
        eflag = True
    if eflag:
        return 1

    pbaseHeight = list(map(int,indexfile['ProbeHeight'][(indexfile['ProbeFileID'] == probeid) & (indexfile['DonorFileID'] == donorid)]))[0] 
    pbaseWidth = list(map(int,indexfile['ProbeWidth'][(indexfile['ProbeFileID'] == probeid) & (indexfile['DonorFileID'] == donorid)]))[0]
    pdims = cv2.imread(pmaskname,cv2.IMREAD_UNCHANGED).shape

    if len(pdims)>2:
        printq("ERROR: {} is not single-channel. Make it single-channel.".format(pmaskname),True)
        flag = 1

    if (pbaseHeight != pdims[0]) or (pbaseWidth != pdims[1]):
        printq("Dimensions for ProbeImg of pair ({},{}): {},{}".format(probeid,donorid,pbaseHeight,pbaseWidth),True)
        printq("Dimensions of probe mask {}: {},{}".format(pmaskname,pdims[0],pdims[1]),True)
        printq("ERROR: The mask image's length and width do not seem to be the same as the base image's.",True)
        flag = 1
     
    dbaseHeight = list(map(int,indexfile['DonorHeight'][(indexfile['ProbeFileID'] == probeid) & (indexfile['DonorFileID'] == donorid)]))[0] 
    dbaseWidth = list(indexfile['DonorWidth'][(indexfile['ProbeFileID'] == probeid) & (indexfile['DonorFileID'] == donorid)])[0]
    ddims = cv2.imread(dmaskname,cv2.IMREAD_UNCHANGED).shape

    if len(ddims)>2:
        printq("ERROR: {} is not single-channel. Make it single-channel.".format(dmaskname),True)
        flag = 1

    if (dbaseHeight != ddims[0]) or (dbaseWidth != ddims[1]):
        printq("Dimensions for DonorImg of pair ({},{}): {},{}".format(probeid,donorid,dbaseHeight,dbaseWidth),True)
        printq("Dimensions of probe mask {}: {},{}".format(dmaskname,ddims[0],ddims[1]),True)
        printq("ERROR: The mask image's length and width do not seem to be the same as the base image's.",True)
        flag = 1
 
    if (flag == 0):
        printq("Your masks {} and {} are valid.".format(pmaskname,dmaskname))
    return flag

class TestValidator(ut.TestCase):
    def testSSDName(self):
        import StringIO
        #This code taken from the following site: http://stackoverflow.com/questions/14197009/how-can-i-redirect-print-output-of-a-function-in-python
        @contextlib.contextmanager
        def stdout_redirect(where):
            sys.stdout = where
            try:
                yield where
            finally:
                sys.stdout = sys.__stdout__
        validatorRoot = '../../data/test_suite/validatorTests/'
        global verbose
        verbose = 1

        print("BASIC FUNCTIONALITY validation of SSDValidator.r beginning...")
        myval = SSD_Validator(validatorRoot + 'foo_NC2016_Manipulation_ImgOnly_p-baseline_1/foo_NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        self.assertEqual(myval.fullCheck(),0)
        print("BASIC FUNCTIONALITY validated.")
        
        print("\nBeginning experiment ID naming error validations. Expect ERROR printouts for the next couple of cases. This is normal here.")
        print("CASE 0: Validating behavior when files don't exist.")
        
        myval = SSD_Validator(validatorRoot + 'emptydir_NC2016_Splice_ImgOnly_p-baseline_1/foo__NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index0.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck() 
            
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read() #NOTE: len(errmsg.read())==0, but when you set it equal, you get the entire string. What gives?
        self.assertTrue("ERROR: I can't find your system output" in errstr)
        errmsg.close()
        
        print("CASE 0 validated.")
        
        print("\nCASE 1: Validating behavior when detecting consecutive underscores ('_') in name...")
        myval = SSD_Validator(validatorRoot + 'foo__NC2016_Manipulation_ImgOnly_p-baseline_1/foo__NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 1 validated.")
        
        print("\nCASE 2: Validating behavior when detecting excessive underscores elsewhere...")
        myval = SSD_Validator(validatorRoot + 'fo_o_NC2016_Manipulation_ImgOnly_p-baseline_1/fo_o_NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 2 validated.")
        
        print("\nCASE 3: Validating behavior when detecting '+' in file name and an unrecognized task...")
        myval = SSD_Validator(validatorRoot + 'foo+_NC2016_Manip_ImgOnly_p-baseline_1/foo+_NC2016_Manip_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: The team name must not include characters" in errstr)
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 3 validated.")
        
    def testSSDContent(self):
        import StringIO
        @contextlib.contextmanager
        def stdout_redirect(where):
            sys.stdout = where
            try:
                yield where
            finally:
                sys.stdout = sys.__stdout__
        validatorRoot = '../../data/test_suite/validatorTests/'
        global verbose
        verbose = None
        print("Validating syntactic content of system output.\nCASE 4: Validating behavior for incorrect headers, duplicate rows, and different number of rows than in index file...")
        print("CASE 4a: Validating behavior for incorrect headers")
        myval = SSD_Validator(validatorRoot + 'foo_NC2016_Manipulation_ImgOnly_p-baseline_2/foo_NC2016_Manipulation_ImgOnly_p-baseline_2.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv') 
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: Your header(s)" in errstr)

        print("CASE 4b: Validating behavior for duplicate rows and different number of rows than in index file...")
        myval = SSD_Validator(validatorRoot + 'foob_NC2016_Manipulation_ImgOnly_p-baseline_2/foob_NC2016_Manipulation_ImgOnly_p-baseline_2.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: Your system output contains duplicate rows" in errstr)
        self.assertTrue("ERROR: The number of rows in the system output does not match the number of rows in the index file." in errstr)
        print("CASE 4 validated.")
        
        print("\nCASE 5: Validating behavior when mask is not a png...")
        myval = SSD_Validator(validatorRoot + 'bar_NC2016_Removal_ImgOnly_p-baseline_1/bar_NC2016_Removal_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("is not a png. Make it into a png!" in errstr)
        print("CASE 5 validated.")
        
        print("\nCASE 6: Validating behavior when mask is not single channel and when mask does not have the same dimensions.")
        myval = SSD_Validator(validatorRoot + 'baz_NC2016_Manipulation_ImgOnly_p-baseline_1/baz_NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertEqual(errstr.count("Dimensions"),2)
        self.assertTrue("ERROR: The mask image's length and width do not seem to be the same as the base image's." in errstr)
        self.assertTrue("is not single-channel. Make it single-channel." in errstr)
        print("CASE 6 validated.")
        
        print("\nCASE 7: Validating behavior when system output column number is not equal to 3.") 
        myval = SSD_Validator(validatorRoot + 'foo_NC2016_Manipulation_ImgOnly_p-baseline_3/foo_NC2016_Manipulation_ImgOnly_p-baseline_3.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: The number of columns of the system output file must be equal to 3. Are you using '|' to separate your columns?" in errstr)
        print("CASE 7 validated.")
        
        print("\nCASE 8: Validating behavior when mask file is not present.") 
        myval = SSD_Validator(validatorRoot + 'foo_NC2016_Manipulation_ImgOnly_p-baseline_4/foo_NC2016_Manipulation_ImgOnly_p-baseline_4.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-manipulation-index.csv')
        
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("does not exist! Did you name it wrong?" in errstr)
        
        print("CASE 8 validated.")
        
        print("\nALL SSD VALIDATION TESTS SUCCESSFULLY PASSED.")
                

    def testDSDName(self):
        import StringIO
        @contextlib.contextmanager
        def stdout_redirect(where):
            sys.stdout = where
            try:
                yield where
            finally:
                sys.stdout = sys.__stdout__
        validatorRoot = '../../data/test_suite/validatorTests/'
        global verbose
        verbose = None
        
        print("BASIC FUNCTIONALITY validation of DSDValidator.py beginning...")
        myval = DSD_Validator(validatorRoot + 'lorem_NC2016_Splice_ImgOnly_p-baseline_1/lorem_NC2016_Splice_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        self.assertEqual(myval.fullCheck(),0)
        print("BASIC FUNCTIONALITY validated.")
        
        errmsg = ""
        #Same checks as Validate SSD, but applied to different files
        print("\nBeginning experiment ID naming error validations. Expect ERROR printouts for the next couple of cases. This is normal here.")
        print("\nCASE 0: Validating behavior when files don't exist.") 
        myval = DSD_Validator(validatorRoot + 'emptydir_NC2016_Splice_ImgOnly_p-baseline_1/emptydir_NC2016_Splice_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index0.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: I can't find your system output" in errstr)
        self.assertTrue("ERROR: I can't find your index file" in errstr)
        print("CASE 0 validated.")
        
        print("\nCASE 1: Validating behavior when detecting consecutive underscores ('_') in name...")
        myval = DSD_Validator(validatorRoot + 'lorem__NC2016_Spl_ImgOnly_p-baseline_1/lorem__NC2016_Spl_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 1 validated.")
        
        print("\nCASE 2: Validating behavior when detecting excessive underscores elsewhere...")
        myval = DSD_Validator(validatorRoot + 'lor_em_NC2016_Manipulation_ImgOnly_p-baseline_1/lor_em_NC2016_Manipulation_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 2 validated.")
        
        print("\nCASE 3: Validating behavior when detecting '+' in file name and an unrecogized task...\n")
        myval = DSD_Validator(validatorRoot + 'lorem+_NC2016_Removal_ImgOnly_p-baseline_1/lorem+_NC2016_Removal_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: The team name must not include characters" in errstr)
        self.assertTrue("ERROR: What kind of task is" in errstr)
        print("CASE 3 validated.")
        
    def testDSDContent(self):
        import StringIO
        @contextlib.contextmanager
        def stdout_redirect(where):
            sys.stdout = where
            try:
                yield where
            finally:
                sys.stdout = sys.__stdout__
        validatorRoot = '../../data/test_suite/validatorTests/'
        global verbose
        verbose = None
        print("Validating syntactic content of system output.\nCASE 4: Validating behavior for incorrect headers, duplicate rows, and different number of rows than in index file...")
        print("CASE 4a: Validating behavior for incorrect headers, duplicate rows, and different number of rows than in index file...")
        myval = DSD_Validator(validatorRoot + 'lorem_NC2016_Splice_ImgOnly_p-baseline_2/lorem_NC2016_Splice_ImgOnly_p-baseline_2.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: Your header(s)" in errstr)
        print("CASE 4b: Validating behavior for duplicate rows and different number of rows than in index file...")
        myval = DSD_Validator(validatorRoot + 'loremb_NC2016_Splice_ImgOnly_p-baseline_2/loremb_NC2016_Splice_ImgOnly_p-baseline_2.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: Your system output contains duplicate rows" in errstr)
        self.assertTrue("ERROR: The number of rows in the system output does not match the number of rows in the index file." in errstr)
        print("CASE 4 validated.")
        
        print("\nCase 5: Validating behavior when the number of columns in the system output is not equal to 5.")
        myval = DSD_Validator(validatorRoot + 'lorem_NC2016_Splice_ImgOnly_p-baseline_4/lorem_NC2016_Splice_ImgOnly_p-baseline_4.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("ERROR: The number of columns of the system output file must be equal to 5. Are you using '|' to separate your columns?" in errstr)
        print("CASE 5 validated.")
        
        print("\nCASE 6: Validating behavior for mask semantic deviations. NC2016-1893.jpg and NC2016_6847-mask.jpg are (marked as) jpg's. NC2016_1993-mask.png is not single-channel. NC2016_4281-mask.png doesn't have the same dimensions...")
        myval = DSD_Validator(validatorRoot + 'ipsum_NC2016_Splice_ImgOnly_p-baseline_1/ipsum_NC2016_Splice_ImgOnly_p-baseline_1.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        self.assertTrue("is not a png. Make it into a png!" in errstr)
        idx=0
        count=0
        while idx < len(errstr):
            idx = errstr.find("Dimensions",idx)
            if idx == -1:
                self.assertEqual(count,2)
                break
            else:
                count += 1
                idx += len("Dimensions")
        self.assertTrue("ERROR: The mask image's length and width do not seem to be the same as the base image's." in errstr)
        self.assertTrue("is not single-channel. Make it single-channel." in errstr)
        self.assertTrue("is not a png. Make it into a png!" in errstr)
        print("CASE 6 validated.")
        
        print("\nCASE 7: Validating behavior when at least one mask file is not present...") 
        myval = DSD_Validator(validatorRoot + 'lorem_NC2016_Splice_ImgOnly_p-baseline_3/lorem_NC2016_Splice_ImgOnly_p-baseline_3.csv',validatorRoot + 'NC2016_Test0516_dfz/indexes/NC2016-splice-index.csv')
        with stdout_redirect(StringIO.StringIO()) as errmsg:
            result=myval.fullCheck()
        errmsg.seek(0)
        self.assertEqual(result,1)
        errstr = errmsg.read()
        idx=0
        count=0
        while idx < len(errstr):
            idx = errstr.find("does not exist! Did you name it wrong?",idx)
            if idx == -1:
                self.assertEqual(count,3)
                break
            else:
                count += 1
                idx += len("does not exist! Did you name it wrong?")
        print("CASE 7 validated.")
        
        print("\nALL DSD VALIDATION TESTS SUCCESSFULLY PASSED.")
        


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Validate the file and data format of the Single-Source Detection (SSD) or Double-Source Detection (DSD) files.')
    parser.add_argument('-x','--inIndex',type=str,default=None,\
    help='required index file',metavar='character')
    parser.add_argument('-s','--inSys',type=str,default=None,\
    help='required system output file',metavar='character')
    parser.add_argument('-vt','--valtype',type=str,default=None,\
    help='required validator type',metavar='character')
    parser.add_argument('-v','--verbose',type=int,default=None,\
    help='Control print output. Select 1 to print all non-error print output and 0 to suppress all printed output (bar argument-parsing errors).',metavar='0 or 1')

    if (len(sys.argv) > 1):

        args = parser.parse_args()
        verbose = args.verbose

        if (args.valtype == 'SSD'):
            ssd_validation = SSD_Validator(args.inSys,args.inIndex)
            ssd_validation.fullCheck()

        elif (args.valtype == 'DSD'):
            dsd_validation = DSD_Validator(args.inSys,args.inIndex)
            dsd_validation.fullCheck()

        else:
            print("Validation type must be 'SSD' or 'DSD'.")
    else:
        parser.print_help()