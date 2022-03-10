"""
MHaddock.py

contains the loop for the iteration 0-8
is only called once by RunHaddock.py
"""
__author__   = "$Author $"
__revision__ = "$Revision $"
__date__     = "$Date $"

import copy, glob, os, re, string, time, sys

from Haddock.Analysis import EnergySorter, ProjectStatus
from Haddock.CNS import CallCns
from Haddock.Main import ParsePath, Messages
from Haddock.Main.QueueSubmit import QueueSubmit, QueueFlush
from Haddock.ThirdParty import task, TextFile
from Haddock.Main.UseLongFileNames import useLongJobFileNames
from Haddock.Analysis.Diagnostic import HaddockError, RunCNSError
from Haddock.Analysis import Diagnostic

#define job concanetation option
jobconcat = {}
#values for running locally in csh (or node) mode
jobconcat["0"] = 1
jobconcat["1"] = 1
jobconcat["2"] = 1
#values for running via a batch system
#jobconcat["0"] = 5
#jobconcat["1"] = 2
#jobconcat["2"] = 2
#values for grid submission
#jobconcat["0"] = 100
#jobconcat["1"] = 20
#jobconcat["2"] = 20

#define the job behavior (using local /tmp or not)
# - for grid submission set to false
# - for local runs, if the network is a bottleneck better set it to true
tmpout=False

def create_queueDic(run,concatfactor):
    #check that for every queue, there is a cpunumber and a cns_exe
    for k in run['queue'].keys():
      if k not in run['cpunumber'].keys():
        raise RunCNSError("""Queue %s has no defined cpunumber""" % (k))
      if k not in run['cns_exe'].keys():
        raise RunCNSError("""Queue %s has no defined CNS exe""" % (k))

              
    #create the queueDic:
    queueDic = {}
    for k in run['cpunumber'].keys():
      nr = int(run['cpunumber'][k])*int(concatfactor)
      com = run['queue'][k]
      if com != '':
          queueDic[com] = [run['cns_exe'][k], nr, []]
    return queueDic   



###############################################################################

def print_status(currit, todoList, todoMap, status, statusroot):
            print 60 * '-'
            for n in todoList:
                currstatus = status[statusroot + str(todoMap[n])]
                if currstatus != 'waiting' and currstatus != 'finished':
                    if currit == '2':
                        print "Structure %4d %4d: %s" % (n, todoMap[n], currstatus)
                    else:
                        print "Structure %4d: %s" % (n, currstatus)
            print 60 * '-'
            print ""
            sys.stdout.flush()


def ForAllIterations(runDir, protocolsDir, newit_tail, tempTrashDir, currit,\
                     fileRoot, previt_tail, templatefile,\
                     structures, HaddockDir, run):
    """
    includes all the stuff for each iteration:
    """

    #get some integer values:
    structures = int(structures)
    currit = str(currit)
    
    newItDir = run['newit']
    previtDir = run['previt']
   
    if run['waterdock'] == 'true': jobconcat[currit] = min(jobconcat[currit], 5)

    allfix = False  # This will be only true if all failed structures have been ordered to be copied
    queueDic = create_queueDic(run,jobconcat[currit])
    
    #get the runPlusNumber as string (e.g. 'run12'):
    runPlusNumber = ParsePath.GetTail(runDir)

    firstpass = True
    
    if currit == '0':
        outDir = runDir + '/begin'
        genfiles = 'false'
        if os.path.exists(outDir + '/file.list'):
            fileList = open (outDir + '/file.list', 'r')
            lenlist = 0
            lenlist = len(fileList.readlines())
            if not lenlist >= structures: genfiles = 'true'
            print "increased number of structures requested for it0"
            print "  ==> regenerating file.nam file.list and file.cns in begin directory"
            fileList.close()
        if not os.path.exists(outDir + '/file.cns'): genfiles = 'true'
        if genfiles == 'true':
            #get a list of all the pdb files:
            pdbNames = outDir + '/' + fileRoot + '_[1-9]*.pdb'
            pdbFiles = glob.glob(pdbNames)
            if len(pdbFiles) == 0:
                print '    no pdb files found => file.list, file.nam and file.cns not created'
                return
            #open file.list , file.nam and file.cns filehandles:
            try:
                fileListHandle = open (outDir + '/file.list', 'w')
            except IOError:
                print "couldn't create file.list in directory", outDir
            try:
                namHandle = open (outDir + '/file.nam', 'w')
            except IOError:
                print "couldn't create file.nam in directory", outDir
            try:
                cnsHandle = open (outDir + '/file.cns', 'w')
            except IOError:
                print "couldn't create file.cns in directory", outDir
                
            #write the header of the file.cns file:
            startCnsFile="""module(filenames;)
set message off echo off end
evaluate ($count = 1)
while ($count le 2000) loop main
   evaluate (&filenames.bestfile_$count = "")
   evaluate ($count = $count + 1)
end loop main
set message on echo on end
"""
            cnsHandle.write(startCnsFile)

            #output:
            zzz = 0
            xxx = structures
            while zzz < xxx:
                for x in pdbFiles:
                    zzz = zzz + 1
                    if zzz > xxx: break
                    pdbout = os.path.split(x)[1]
                    fileListHandle.write('"PREVIT:' + pdbout + '"\n')
                    namHandle.write(pdbout + '\n')
                    cnsHandle.write('evaluate (&filenames.bestfile_' +\
                                str(zzz) + '="PREVIT:' + pdbout + '")\n')
            cnsHandle.write('\n\n') #important for CNS!!!
    
            #close the file handles:
            fileListHandle.close()
            namHandle.write('\n\n')
            namHandle.close()
            cnsHandle.write('\n\n')
            cnsHandle.close()

    elif currit == '2':
        print '    starting water refinement for the', structures, \
          'best structures regarding energy'
        solvent = run['solvent']
        
    lastit = int(currit) - 1
 
    #starting molecular dynamics in parallel:
    print 'starting DOCKING protocol '
    whichMD = 'torsion'
    if currit == '2':
        protocolFile = 're_h2o.inp'
        if solvent == 'dmso':
            protocolFile = 're_dmso.inp'    
    else:
        protocolFile = 'refine.inp'


    #for substituting the count and the output filename:
    parseEval = re.compile('!The next line will be changed automatically.*?\n\s*?evaluate.*?\)')


    #get the status of the whole project, e.g. the calculated structures:
    status = ProjectStatus.GetStatus(run)
        
    #read the file.list file and create a list of filenames:
    insideQuotes = re.compile('"(.*?)"')
    fileList = {}
    fileListCounter = 0
    fileListHandle = open(os.path.join(previtDir, 'file.list'))
    fileListLines = fileListHandle.readlines()
    for eachLine in fileListLines:
        fileListCounter += 1
        searched = insideQuotes.search(eachLine)
        fileList[fileListCounter] = searched.group(1)
    fileListHandle.close()                    
    
    rotate_1 = run['rotate180_it1']
    solvdock = run['waterdock']
    if rotate_1 == 'true' and currit == '2' and solvdock == 'false':
        nstruc = structures * 2
    else:
        nstruc = structures
                
    #create a list of structures that still need to be calculated       
    
    todoList = range(1, nstruc + 1) 
    if currit == '2':
        todoStructures = []
        wStrucNumber = re.compile('\S+_(\S+)\.pdb')
        for eachLine in fileListLines:
            wStrucSearched = wStrucNumber.search(eachLine)
            todoStructures.append(int(wStrucSearched.group(1)))
        todoStructures = todoStructures[:nstruc]
    else:
        todoStructures = range(1, nstruc + 1)

    todoMap = {}
    for n in range(0, len(todoList)):
      todoMap[todoList[n]] = todoStructures[n] 
        
        
    #where to look for statuses
    if currit == '0' or currit == '1':
        statusroot = 'pdb_' + currit + '_'
    else: statusroot = 'wpdb_'
    
    different = False  #This will become true if a status changes
    last_submitted = False
    #dcounter = 0
    check = []
    while len(todoList):
    
        #check for possible failure
        failfile = runDir + '/FAILED'
        if os.path.exists(failfile):
            print "HADDOCK has detected an error"
            print "Check the FAILED file in ",runDir
            print "Stopping..."
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean'
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()

        #check for possible cancellation
        failfile = runDir + '/CANCEL'
        if os.path.exists(failfile):
            print "Your HADDOCK run has been cancelled"
            print "Stopping..."
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean'
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()

        waitgrid = False 
        for k in run['queue'].keys():
            if 'dirac' in run['queue'][k]: waitgrid = True

        #check for results archives - grid mode
        for package in glob.glob("packages/*-result.tar.gz"):
            packageroot = package[len("packages/"):-len("-result.tar.gz")]
            extractfile = packageroot+"-extract-results.csh"
            packagetar = "packages/"+packageroot+".tar.gz"
            time.sleep(5)      
            if os.path.isfile(extractfile):
                os.system("csh " + extractfile)
                os.remove(extractfile)
                if os.path.isfile(package): os.remove(package)
                if os.path.isfile(packagetar): os.remove(packagetar)
            else:
                if os.path.isfile(package): os.remove(package)
                if os.path.isfile(packagetar): os.remove(packagetar)

        #start at begin of structureList
        todoListPointer = 0
        allfailed = True #This will remain true if all remaining structures have failed
        printout = True #Set this to False when a queue is not free immediately
        while todoListPointer < len(todoList):

            #read the current todo structure
            strucNumber = todoList[todoListPointer] #basically the rank
            strucID = todoStructures[todoListPointer] #basically the number suffix of the resulting structure
            
            if last_submitted == False and todoListPointer == len(todoList) -1:
               last_submitted = True
               different = True
        
            if currit == '2': 
                jobroot = tempTrashDir + '/' + fileRoot + '_' + ParsePath.GetTail(run['run_dir']) + '_'\
                + str(strucID) + 'w'
            else: 
                jobroot = tempTrashDir + '/' + fileRoot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
                + currit + '_refine_' + str(strucID)            
            
            #check the status of the current structure  
            currstatus = status[statusroot + str(strucID)]
            #if currstatus != 'finished': print  strucNumber, currstatus
            if currstatus == 'running' or currstatus == 'waiting':
                #re-check status
                newcurrstatus = Diagnostic.GetDiagnose(strucID, currit, run, status)
                if newcurrstatus == 'pending':
                    currstatus = newcurrstatus
                    status[statusroot + str(strucID)] = currstatus
                    print_status(currit, todoList, todoMap, status, statusroot)
                if newcurrstatus != 'waiting':
                    currstatus = newcurrstatus
                    status[statusroot + str(strucID)] = currstatus
                if newcurrstatus == 'running':
                    #check for a time-out
                    timeout = Diagnostic.CheckTimeOut(run, strucID, currit, jobroot)
                    if timeout == False:
                        allfailed = False
                        todoListPointer += 1
                        continue
                    else:
                        print "Time-out of structure %s" % strucID
                        currstatus = 'crashed'
                        status[statusroot + str(strucID)] = currstatus
                        different = True
                else:
                    different = True
            if currstatus == 'pending':
                currstatus = Diagnostic.GetDiagnose(strucID, currit, run, status)
                if currstatus == 'pending':
                    currstatus = Diagnostic.CheckForLateArrival(run,strucID, currit)
                    allfailed = False
                    todoListPointer += 1
                    continue
                else:
                    different = True
            if currstatus == 'finished':
                if statusroot + str(strucID) in check:
                     QueueFlush(finished=True)
                allfailed = False
                todoList.remove(todoList[todoListPointer])
                todoStructures.remove(todoStructures[todoListPointer])
                continue
            if currstatus == 'crashed':
                if statusroot + str(strucID) in check:
                    QueueFlush(finished=True)
                if Diagnostic.Fix(run, strucID, currit, jobroot) == False:
                    status[statusroot + str(strucID)] = 'failed'
                    todoListPointer += 1
                    continue
                else:
                    print "Waiting to restart job..."
                    status[statusroot + str(strucID)] = 'crashed'
                    #job is equivalent to 'waiting' now, and will be changed into 'running'
                print_status(currit, todoList, todoMap, status, statusroot)
            if currstatus == 'failed':
                todoListPointer += 1
                continue
                        
            different = True
            allfailed = False
            #wait for a free queue
            queueIndex = 0
            while 1:

                #check for results archives - grid mode
                for package in glob.glob("packages/*-result.tar.gz"):
                    packageroot = package[len("packages/"):-len("-result.tar.gz")]
                    extractfile = packageroot+"-extract-results.csh"
                    packagetar = "packages/"+packageroot+".tar.gz"
                    time.sleep(5)
                    if os.path.isfile(extractfile):
                        os.system("csh " + extractfile)
                        os.remove(extractfile)
                        if os.path.isfile(package): os.remove(package)
                        if os.path.isfile(packagetar): os.remove(packagetar)
                    else:
                        if os.path.isfile(package): os.remove(package)
                        if os.path.isfile(packagetar): os.remove(packagetar)

                printout = False #only printout when the queue is initially full  
                queueList = queueDic.keys()
                eachQueue = queueList[queueIndex]
                #1. if empty, take it directly:
                if queueDic[eachQueue][1] > len(queueDic[eachQueue][2]):
                    if queueDic[eachQueue][1] == len(queueDic[eachQueue][2]) + 1:
                        printout = True
                    break
                #2. if fileNames exist, check if the structures already exist:
                else:
                    breakOut = False
                    for eachF in queueDic[eachQueue][2]:
                        if os.path.exists(eachF[1]):
                            print eachF[1]
                            queueDic[eachQueue][2].remove(eachF)
                            breakOut = True
                            printout = True
                        else:
                            strucID_F = eachF[0]
                            currstatus_F  = status[statusroot + str(strucID_F)]
                            if currstatus_F == "pending":
                              currstatus_F = Diagnostic.CheckForLateArrival(run,strucID_F, currit)
                            elif currstatus_F  == "running":
                              currstatus_F = Diagnostic.GetDiagnose(strucID_F, currit, run, status)
                              if currstatus_F != "running": printout = True
                            if currstatus_F == "running":
                              if currit == '2': 
                                jobroot_F = tempTrashDir + '/' + fileRoot + '_' + ParsePath.GetTail(run['run_dir']) + '_'\
                                + str(strucID_F) + 'w'
                              else: 
                                jobroot_F = tempTrashDir + '/' + fileRoot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
                                + currit + '_refine_' + str(strucID_F)          
                              timeout = Diagnostic.CheckTimeOut(run, strucID_F, currit, jobroot_F) 
                              if timeout == True:
                                  print "Time-out of structure %s" % strucID_F
                                  if statusroot + str(strucID) in check:
                                      QueueFlush(finished=True)
                                  currstatus_F = "crashed"
                            status[statusroot + str(strucID_F)] = currstatus_F
                            if currstatus_F == "crashed":
                                queueDic[eachQueue][2].remove(eachF)
                                breakOut = True
                                printout = True                                             
                    if breakOut: break
                if queueIndex == (len(queueList) - 1):
                    queueIndex = 0
                    time.sleep(1) 
                else:
                    queueIndex = queueIndex + 1
                
            
            print '    calculating structure', strucNumber
            startFrom = fileList[strucNumber]
            
            #create a temporary protocol file in the tempTrashDir:
            if currit == '2':
                outputFileName = os.path.join(tempTrashDir, fileRoot + '_' + runPlusNumber +\
                                      '_' + str(strucID) + 'w.inp')
            else:
                outputFileName = os.path.join(tempTrashDir, fileRoot + '_' +\
                                      runPlusNumber + '_it' + currit +\
                                      '_refine_' + str(strucID) + '.inp')           

            if currit == '2':
                if not os.path.exists(outputFileName):
                    inputHandle = open(os.path.join(protocolsDir, protocolFile))
                    outputHandle = open(outputFileName, 'w')
                    wholeProtocol = string.join(inputHandle.readlines(), '')
                    wholeProtocol = parseEval.sub('evaluate ($count=' +\
                            str(strucNumber) + ')', wholeProtocol, 1)
                    wholeProtocol = parseEval.sub('evaluate ($file="' +\
                             startFrom + '")', wholeProtocol, 1)
                    outputHandle.write(wholeProtocol)
                    outputHandle.close()                             
                stdoutFN = tempTrashDir + '/' + fileRoot + '_' + runPlusNumber + '_' +\
                   str(strucID) + 'w.out'
                jobFN = os.path.join(tempTrashDir, fileRoot + '_' +\
                             runPlusNumber +\
                             '_' + str(strucID) + 'w.job')
                   
                            
            else:
                if not os.path.exists(outputFileName):
                    inputHandle = open(os.path.join(protocolsDir, protocolFile))
                    outputHandle = open(outputFileName, 'w')
                    wholeProtocol = string.join(inputHandle.readlines(), '')
                    #replace $whichMD, $count, $file and $filename:
                    wholeProtocol = parseEval.sub('evaluate ($whichMD="' +\
                                            whichMD + '")', wholeProtocol, 1)
                    wholeProtocol = parseEval.sub('evaluate ($count=' +\
                                            str(strucNumber) + ')', wholeProtocol, 1)
                    wholeProtocol = parseEval.sub('evaluate ($file="' +\
                                            startFrom + '")', wholeProtocol, 1)
                    wholeProtocol = parseEval.sub('evaluate ($filename="' +\
                                            os.path.join(newItDir, fileRoot + '_' +\
                                                    str(strucNumber)+ '.pdb")'),\
                                            wholeProtocol, 1)
                    outputHandle.write(wholeProtocol)
                    outputHandle.close()
                stdoutFN = jobroot + '.out'
                jobFN = os.path.join(tempTrashDir, fileRoot + '_' +\
                             runPlusNumber +\
                             '_it' + currit +\
                             '_refine_' + str(strucNumber) + '.job')


            #write the temporary job files in the tempTrashDir:
            cnslink = "protocols/cns%d" % (queueIndex+1,)
            if not os.path.exists(cnslink): os.system("ln -s %s %s" % (queueDic[eachQueue][0],cnslink))     

            rotstrucNumber = strucNumber + structures

            if currit == '2':
                pdb_struc = newit_tail + '/water/' + fileRoot + '_' + str(strucID) + 'w.pdb'
                pdb_strucrot = newit_tail + '/NONE'
            else:
                pdb_struc = newit_tail + '/' + fileRoot + '_' + str(strucNumber) + '.pdb'
                pdb_strucrot = newit_tail + '/' + fileRoot + '_' + str(rotstrucNumber) + '.pdb'
		
# Duplication of the RemoveBadPDB.py call below is required to handle the case where rotate_it1 = true
# In that case one job will generate two PDB files and both need to be checked

            if tmpout == False:
                jobString = """#!/bin/csh
setenv CURRIT %s
setenv RUN ./
setenv NEWIT $RUN/%s
setenv PREVIT $RUN/%s
setenv TEMPTRASH $RUN
%s < %s >! %s
./tools/check-error-messages.csh %s
if ( -e ./%s0 ) then
  python protocols/RemoveBadPDB.py ./%s
endif
if ( -e ./%s0 ) then
  python protocols/RemoveBadPDB.py ./%s
endif
gzip -f %s
""" %           (currit,\
                 newit_tail,\
                 previt_tail,\
                 cnslink,\
                 ParsePath.GetTail(outputFileName),\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 pdb_struc,\
                 pdb_struc,\
                 pdb_strucrot,\
                 pdb_strucrot,\
                 ParsePath.GetTail(stdoutFN))
            else:
                 jobString = """#!/bin/csh
setenv CURRIT %s
setenv RUN ./
setenv NEWIT $RUN/%s
setenv PREVIT $RUN/%s
setenv TEMPTRASH $RUN
python protocols/KeepAlive.py %s &
if (-e /tmp) then
  setenv TMPDIR /tmp/`uuidgen`
else
  setenv TMPDIR ./`uuidgen`
endif
mkdir $TMPDIR
echo STARTED >>%s
%s < %s >! $TMPDIR/%s
set jobid=`ps -afU $USER | grep %s |grep -v grep | awk '{print $2}'` >&/dev/null
./tools/check-error-messages.csh $TMPDIR/%s
gzip -f $TMPDIR/%s
if ( -e ./%s0 ) then
  python protocols/RemoveBadPDB.py ./%s
endif
if ( -e ./%s0 ) then
  python protocols/RemoveBadPDB.py ./%s
endif
kill -9 $jobid >&/dev/null
rm -f %s
mv -f $TMPDIR/%s.gz %s.gz
rm -rf $TMPDIR
""" %           (currit,\
                 newit_tail,\
                 previt_tail,\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 cnslink,\
                 ParsePath.GetTail(outputFileName),\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 pdb_struc,\
                 pdb_struc,\
                 pdb_strucrot,\
                 pdb_strucrot,\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN),\
                 ParsePath.GetTail(stdoutFN))

            if not useLongJobFileNames:
                jobFN = ParsePath.GetTail(jobFN)
            cwd = os.getcwd()
            os.chdir(tempTrashDir)
            if os.path.exists(stdoutFN + '.gz'):
                os.remove(stdoutFN + '.gz')
            open(stdoutFN, 'w')
            check.append(statusroot + str(strucID))
            QueueSubmit(eachQueue, jobFN, jobString, run, jobconcat[currit], fileRoot)
            os.chdir(cwd)


            #add the file to the queueDic:
            
            queueDic[eachQueue][2].append((strucID, pdb_struc))
            status[statusroot + str(strucID)] = 'running'
            break
        
        #if we didn't submit a structure this cycle, wait a bit before moving back to the front of the todo list
        if allfailed == True:  
            if allfix:
                maxfail = int(0.2 * nstruc) #maximum 20 % of the structures may fail...
                if len(todoStructures) > maxfail:
                    repstr = "HADDOCK cannot continue due to too many (>20%) failed structures in it" + currit
                    raise HaddockError("\n"+repstr+"\nThe following structures could not be docked: \n    " + str(todoStructures) )
            else:
                if currit == "0": 
                    print "Restarting failed structures..."
                    for strucID in todoStructures:
                        Diagnostic.RestartStructure(strucID, currit, run)
                        status[statusroot+str(strucID)] = "waiting"
# added this flush to sort our the job resubmission problem
                    QueueFlush(force=True)
                else:
                    print "The following structures have failed: %s" % str(todoStructures)
                    print "Only a flexible energy minimization will be performed."
                    print "Restarting structures..."
                    for strucID in todoStructures:
                        Diagnostic.MiniStructure(strucID, currit, run)
                        status[statusroot+str(strucID)] = "waiting"
# added this flush to sort our the job resubmission problem
                    QueueFlush(force=True)
                allfix = True
                allfailed = False
            allcopy = True

        if todoListPointer >= len(todoList):
            if firstpass == True:
              QueueFlush(force=True)
              firstpass = False
            else: 
              QueueFlush()

            if waitgrid:
               time.sleep(60)
            else:
               time.sleep(5)

        if different and printout:
            different = False
            print_status(currit, todoList, todoMap, status, statusroot)

            if waitgrid:
               time.sleep(60)
            else:
               time.sleep(5)
            
      
    if run['skip_struc']:
        nstskip = int(run['skip_struc'])
    else:
        nstskip = 0     
    if currit != '0': nstskip = 0
    filelistdir = newItDir
    if currit == '2': filelistdir += '/water'
    time.sleep(10)
    EnergySorter.WriteFileList(directory=filelistdir,outDir=filelistdir,\
                               howMany=100000, message=1, fileNam=1,\
                               fileCns=1, nstskip=nstskip, iteration=int(currit))
    #last line must change when merged with water refinement
