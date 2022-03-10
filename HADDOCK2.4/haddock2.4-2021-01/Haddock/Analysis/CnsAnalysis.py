"""
CnsAnalysis.py
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:21 $"

import os, time, glob, string, sys, traceback, stat
from Haddock.Main import ParsePath
from Haddock.DataIO import ParseDihedrals, InputFileParser
from Haddock.Main.UseLongFileNames import useLongJobFileNames
from Haddock.Main.QueueSubmit import QueueSubmit, QueueFlush
    
def Analysis(runDir, HaddockDir, protocolsDir, newit_tail, tempTrashDir, currit, queueDic, fileRoot):
    """
    a method to call all the CNS analysis scripts

    added some protocols from Alexandre Bonvin 25-6-2001
    """
    run = InputFileParser.ParseRunCns()
    newItDir = runDir + '/' + newit_tail
    
    print 'starting analysis scripts for', newItDir
    queueList = queueDic.keys()

    #get the runPlusNumber as string (e.g. 'run12'):
    runPlusNumber = ParsePath.GetTail(runDir)
            
    #1. calculating average structure (get_average.inp):
    print '  calculating average structure and similarity matrices'
    cnslink = "protocols/cns1" 
    if not os.path.exists(cnslink): os.system("ln -s %s %s" % (queueDic[queueList[0]][0],cnslink))
    jobDIR=run['temptrash_dir']
    if not useLongJobFileNames:
        jobDIR = "./"
    jobString = """#!/bin/csh
    cd %s
    setenv CURRIT %s
    setenv RUN ./
    setenv NEWIT $RUN/%s
    setenv PREVIT $RUN/%s
    setenv TEMPTRASH $RUN
    %s < %s >! $NEWIT/%s
    gzip $NEWIT/%s
    rm -rf $NEWIT/%s
    """ %       (jobDIR,currit,\
             newit_tail,\
             newit_tail,\
             cnslink,\
             'protocols/get_average.inp',\
             '/analysis/get_average.out',\
             '/analysis/get_average.out',\
             '/analysis/' + fileRoot + '.crd')

    cwd = os.getcwd()
    os.chdir(tempTrashDir)                   
    jobFN = os.path.join(tempTrashDir, fileRoot + '_' + runPlusNumber + '_get_average.job')    
    if not useLongJobFileNames:
        jobFN = ParsePath.GetTail(jobFN)
    if not os.path.exists(newItDir + '/analysis/' + fileRoot + '_ave.pdb'):     
      calc_ave = True
      QueueSubmit(queueList[0], jobFN, jobString, run, 1, fileRoot)
      QueueFlush(force=True)
    else: calc_ave = False
    
    #waiting:
    print '  waiting for the average structure...'
    while 1:
        if os.path.exists(newItDir + '/analysis/AVE_DONE'):
            break
        time.sleep(10)
    if calc_ave: QueueFlush(finished=True)
    time.sleep(20) #wait for slow networks
   
    #2. Run FCC clustering if chosen as so
    fcc_options = ["-H"]
    if run['fcc_ignc'] == 'true':
      fcc_options.append('-i')

    if run['clust_meth'] == 'FCC':
        outputFN = fileRoot+'_fcc.disp'
        jobString = """#!/bin/csh
cd %s
setenv RUN ./
setenv NEWIT $RUN/%s
python2 ./tools/make_contacts.py $NEWIT/analysis/*fit_*pdb
foreach i ($NEWIT/analysis/*fit_*.contacts)
  grep -v "-" $i >$i.tmp
  \mv $i.tmp $i
end
python2 ./tools/calc_fcc_matrix.py $NEWIT/analysis/*fit_*contacts -o $NEWIT/analysis/%s %s >& $NEWIT/analysis/fcc.out
gzip -f $NEWIT/analysis/fcc.out
""" %       (jobDIR, newit_tail, outputFN, ' '.join(fcc_options))

        cwd = os.getcwd()
        os.chdir(tempTrashDir)
        if currit == 2: 
            jobFN = os.path.join(tempTrashDir, fileRoot + '_' + runPlusNumber + '_fcc_matrix-water.job')
        else:
            jobFN = os.path.join(tempTrashDir, fileRoot + '_' + runPlusNumber + '_fcc_matrix.job')
        if not useLongJobFileNames:
            jobFN = ParsePath.GetTail(jobFN)
        if not os.path.exists(newItDir + '/analysis/' + outputFN):
          calc_fcc_matrix = True
          QueueSubmit(queueList[0], jobFN, jobString, run, 1, fileRoot)
          QueueFlush(force=True)
        else: calc_fcc_matrix = False

##        #waiting:
##        print '  waiting for the fcc matrix...'
##        while 1:
##            if os.path.exists(newItDir + '/analysis/' + outputFN):
##                break
##            time.sleep(20)
##        if calc_fcc_matrix: QueueFlush(finished=True)
##        time.sleep(5) #wait for slow networks

    #3. all the other analysis scripts:
    print '  running analysis scripts:'
    toDoList = []
    if run['runana'] == 'full':
        toDoList = [['analyzing NOEs', 'print_noes.inp'],\
                    ['calculating residue-based intermolecular energies', 'ene-residue.inp'],\
                    ['calculating energies', 'energy.inp'],\
                    ['calculating desolvation energy', 'edesolv.inp'],\
                    ['analyzing geometry', 'print_geom.inp'],\
                    ['analyzing dihedrals', 'print_dih.inp'],\
                    ['analyzing radius of gyration', 'print_rg.inp'],\
                    ['analyzing residual dipolar coupling (SANI)', 'print_sani.inp'],\
                    ['analyzing residual dipolar coupling (VEAN)', 'print_vean.inp'],\
                    ['analyzing residual dipolar coupling (XRDC)', 'print_xrdc.inp'],\
                    ['analyzing pseudo contact shifts (XPCS)', 'print_xpcs.inp'],\
                    ['analyzing diffusion anisotropy restraints (DANI)', 'print_dani.inp'],\
                    ['analyzing intermolecular hydrogen bonds', 'print_hbonds.inp'],\
                    ['analyzing intermolecular hydrophobic contacts', 'print_nb.inp']]

    if run['clust_meth'] == 'RMSD': 
#        toDoList.insert(0,['calculating pairwise rmsd matrix', 'rmsd.inp'])
        toDoList.append(['calculating pairwise rmsd matrix', 'rmsd.inp'])

    donefile = {}
    check = []
    for eachPro in toDoList:
        donefile[eachPro[0]] = newItDir + '/analysis/' + eachPro[1][:-4] + ".out.gz"
    for eachPro in toDoList:
        currdonefile = donefile[eachPro[0]]
        if os.path.exists(currdonefile): 
          continue
          
        queueIndex = 0
        while 1:
            queueList = queueDic.keys()
            eachQueue = queueList[queueIndex]
            if queueDic[eachQueue][1] > len(queueDic[eachQueue][2]):
                break
            if queueIndex == (len(queueList) - 1):
                queueIndex = 0
                break 
                #push jobs into the 1st queue even if it is full; 
                #we cannot determine when a job is finished, so we have to submit everything
            else:
                queueIndex = queueIndex + 1
            time.sleep(1)
        time.sleep(5) #submit a job no faster than every 5 sec

        print '   ', eachPro[0]
        inputFN = runDir + '/protocols/' + eachPro[1]
        outputFN = newItDir + '/analysis/' + eachPro[1][:-4] + '.out'
        if currit == 2: 
            jobFN = os.path.join(tempTrashDir, fileRoot  + '_' + runPlusNumber + '_' +\
                             eachPro[1][:-4] + '-water.job')
        else:
            jobFN = os.path.join(tempTrashDir, fileRoot  + '_' + runPlusNumber + '_' +\
                             eachPro[1][:-4] + '.job')
        cnslink = "protocols/cns%d" % (queueIndex+1,)
        if not os.path.exists(cnslink): os.system("ln -s %s %s" % (queueDic[eachQueue][0],cnslink))
        jobDIR=run['temptrash_dir']
        if not useLongJobFileNames:
            jobDIR = "./"

# Following added to avoid issues with ene-residue not ending properly and hanging a run
# added creating of ENE_DONE file outside the CNS script

        if eachPro[1] == 'ene-residue.inp':
            jobString = """#!/bin/csh
cd %s
setenv CURRIT %s
setenv RUN ./
setenv NEWIT $RUN/%s
setenv PREVIT $RUN/%s
setenv TEMPTRASH $RUN
%s < protocols/%s >! $NEWIT/analysis/%s
gzip -f $NEWIT/analysis/%s
touch $NEWIT/analysis/ENE_DONE
""" %       (jobDIR,currit,\
             newit_tail,\
             newit_tail,\
             cnslink,\
             ParsePath.GetTail(inputFN),\
             ParsePath.GetTail(outputFN),\
             ParsePath.GetTail(outputFN))

        else:

            jobString = """#!/bin/csh
cd %s
setenv CURRIT %s
setenv RUN ./
setenv NEWIT $RUN/%s
setenv PREVIT $RUN/%s
setenv TEMPTRASH $RUN
%s < protocols/%s >! $NEWIT/analysis/%s
gzip -f $NEWIT/analysis/%s
""" %       (jobDIR,currit,\
             newit_tail,\
             newit_tail,\
             cnslink,\
             ParsePath.GetTail(inputFN),\
             ParsePath.GetTail(outputFN),\
             ParsePath.GetTail(outputFN))
        os.chdir(cwd)
        os.chdir(tempTrashDir)                   
        if not useLongJobFileNames:
            jobFN = ParsePath.GetTail(jobFN)
        check.append(currdonefile)
        QueueSubmit(queueList[0], jobFN, jobString, run, 1, fileRoot)

    QueueFlush(force=True)
    
    anaDir =  newItDir + "/analysis/"

    if run['runana'] == 'full':
        #waiting:
        print '  waiting for the NOE analysis file...'
        while 1:
            if os.path.exists(donefile[toDoList[0][0]]): break
            time.sleep(10)

        if os.path.exists(newItDir + '/analysis/NOE_DONE'):
            #run NOE violation analysis
            anaNoeFiles = "/bin/cp " + runDir + "/tools/*_noe_viol* " + newItDir + "/analysis/"
            os.system(anaNoeFiles)
            anaDir =  newItDir + "/analysis/"
            print '    checking all distance restraints violations in', anaDir
            print '        check ana_dist_viol_all.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaNoeViol = "./ana_noe_viol.csh print_dist_all.out > ana_dist_viol_all.lis"
            os.system(anaNoeViol)

            print '    checking all NOE violations in', anaDir
            print '        check ana_noe_viol_all.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaNoeViol = "./ana_noe_viol.csh print_noe_all.out > ana_noe_viol_all.lis"

            os.system(anaNoeViol)
            print '    checking unambiguous NOE violations in', anaDir
            print '        check ana_noe_viol_unambig.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaNoeViol = "./ana_noe_viol.csh print_noe_unambig.out > ana_noe_viol_unambig.lis"
            os.system(anaNoeViol)

            print '    checking ambiguous NOE violations in', anaDir
            print '        check ana_noe_viol_ambig.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaNoeViol = "./ana_noe_viol.csh print_noe_ambig.out > ana_noe_viol_ambig.lis"
            os.system(anaNoeViol)

            print '    checking hbonds violations in', anaDir
            print '        check ana_hbond_viol.out for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaNoeViol = "./ana_noe_viol.csh print_dist_hbonds.out > ana_hbond_viol.lis"
            os.system(anaNoeViol)
            os.chdir(cwd)      
        else: print "Error in NOE analysis, SKIPPED"

        print '  waiting for the dihedral analysis file...'
        while 1:
            if os.path.exists(donefile[toDoList[6][0]]): break
            time.sleep(10)
    
        if os.path.exists(newItDir + '/analysis/DIH_DONE'):
            #run dihedral restraints violation analysis
            anaDihedFiles = "/bin/cp " + runDir + "/tools/*_dihed_viol* " + newItDir + "/analysis/"
            os.system(anaDihedFiles)
            print '    checking dihedral angle restraints violations in', anaDir
            print '        check ana_dihed_viol.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anaDihedViol = "gunzip print_dih.out.gz; ./ana_dihed_viol.csh print_dih.out > ana_dihed_viol.lis"
            os.system(anaDihedViol)
            os.chdir(cwd)      
        else: print "Error in dihedral angle analysis, SKIPPED"
    
        print '  waiting for the H-bonds analysis file...'
        while 1:
            if os.path.exists(donefile[toDoList[10][0]]): break
            time.sleep(10)
    
        if os.path.exists(newItDir + '/analysis/HBONDS_DONE'):
            #Analysis of hydrogen bonds 
            anahbFiles = "/bin/cp " + runDir + "/tools/*_hbon* " + newItDir + "/analysis/"
            os.system(anahbFiles)
            anaDir =  newItDir + "/analysis/"
            print '    checking intermolecular hydrogen bonds', anaDir
            print '        check ana_hbonds.lis for a listing' 
            os.chdir(cwd)
            os.chdir(anaDir)
            anahbViol = "./ana_hbonds.csh hbonds.disp > ana_hbonds.lis"
            os.system(anahbViol)
            os.chdir(cwd)      
        else: print "Error in hydrogen bond analysis, SKIPPED"

        print '  waiting for the hydrophobic analysis file...'
        while 1:
            if os.path.exists(donefile[toDoList[11][0]]): break
            time.sleep(10)
    
        if os.path.exists(newItDir + '/analysis/NB_DONE'):
             #Analysis of hydrophobic contacts 
             print '    checking intermolecular hydrophobic contacts', anaDir
             print '        check ana_nbcontacts.lis for a listing' 
             os.chdir(cwd)
             os.chdir(anaDir)
             ananbViol = "./ana_hbonds.csh nbcontacts.disp > ana_nbcontacts.lis"
             os.system(ananbViol)
        else: print "Error in hydrophobic contact analysis, SKIPPED"

    os.chdir(cwd)
    import glob
    pdbFiles = glob.glob('%s/*.pdb' % anaDir)
    for x in pdbFiles:
        copysegid = runDir + "/tools/pdb_segid-to-chain " + x + ">analysis_tmpfile; \mv analysis_tmpfile " + x
        os.system(copysegid)
        os.chdir(cwd)     
        
    touchFile = open(newItDir + '/analysis/DONE', 'w')
    touchFile.close()
    os.chdir(cwd)
    #declare all jobs finished
    for eachPro in toDoList: 
        donefile = newItDir + '/analysis/' + eachPro[1][:-4] + ".out.gz"
        if donefile in check: QueueFlush(finished=True)
 
