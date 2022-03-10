"""
This is the main PYTHON script for running HADDOCK from a UNIX command line.
All important information is parsed out of the run.cns or run.param of your 
current run of your project.

For a comprehensive description, read the manual html pages.

Usage for setting up a new project:
1. Use the HADDOCK HTML page for setting up of a new project, save run.param
   in your HADDOCK program directory
2. Go in the directory where run.param was saved
3. call the executable /haddock/Haddock/RunHaddock.py

Usage for running HADDOCK: 
1.  Go in that directory where your current run.cns file was saved
2.  call the executable /haddock/Haddock/RunHaddock.py

Version1.0 originally adapted from the ARIA distribution of Jens Linge and Michael Nilges (Institut Pasteur)

"""
__HaddockVersion__ = "2.4 - January 2021 release"


###############################################################################
# Maximum of number of possible combinations
# out of ensemble docking.
MAX_COMBINATIONS = 5000
###############################################################################
import copy, glob, os, re, string, shutil, sys, time, traceback, subprocess
from itertools import product

try:
    from Haddock.Analysis import CnsAnalysis, ProjectStatus 
    from Haddock.CNS import CallCns
    from Haddock.DataIO import InputFileParser
    from Haddock.Main import MHaddock, Messages, ParsePath, Setup
    from Haddock.Main.QueueSubmit import QueueSubmit, QueueFlush
    from Haddock.ThirdParty import DictWithDefault, TextFile
    from Haddock.Main.UseLongFileNames import useLongJobFileNames
    from Haddock.Main.MHaddock import create_queueDic
    from Haddock.Analysis.Diagnostic import HaddockError
except ImportError:
    print "Exception occurred while importing Python modules:"
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60
    print """
There was an ImportError with importing the HADDOCK Python modules.
Most probably, you haven't set the UNIX system variable $PYTHONPATH properly.

Try:
    echo $PYTHONPATH
    
It should contain something like /software/haddock/Haddock

Use:
    setenv PYTHONPATH /software/haddock/Haddock
in csh or tcsh.

Or use:
    export PYTHONPATH='/software/haddock/Haddock'
in zsh or bash.

Read the installation notes again if you should have more problems with
importing the HADDOCK Python modules.
"""
#    print sys.exc_info()
    print 'YOUR PYTHONPATH WAS SET TO:'
    print sys.path
    print '\nPLEASE CHANGE YOUR $PYTHONPATH SYSTEM VARIABLE AND RESTART HADDOCK.\n'
    sys.exit()

    
#write the first message to STDOUT:
Messages.StartHaddock(__HaddockVersion__)
sys.stdout.flush()

###############################################################################
#looking for run.param (for setup) or run.cns in current directory:
if (os.path.exists('run.param') == 0) and (os.path.exists('run.cns') == 0):
    print 'there is no run.cns OR run.param in your current directory.'
    print '=> HADDOCK stopped'
    Messages.StopHaddock()
elif (os.path.exists('run.param') == 1) and (os.path.exists('run.cns') == 1):
    print 'there is a run.param AND a run.cns in your current directory.'
    print 'remove one of them.'
    print '=> HADDOCK stopped'
    Messages.StopHaddock()
    
###############################################################################
#1. if run.param exists: parse run.param and set up a new project or a new run
if os.path.exists('run.param') == 1:
    new = DictWithDefault.DictWithDefault(None)
    #newparsed is a simple dictionary:
    newparsed = {}
    #get the dictionary for the variables:
    newparsed = InputFileParser.ParseRunParam()
    #copy all the parameters to 'new':
    for kkparsed in newparsed.keys():
        new[kkparsed] = newparsed[kkparsed]

    #for a new project:
    new['RUN_DIR'] = new['PROJECT_DIR'] + '/run' + new['RUN_NUMBER']  

    #get and check the number of components:
    ncomp = int(new['N_COMP'])
    if (ncomp < 2):
        print 'WARNING: Only one molecule defined!'
        print 'This will not be called docking!!!'
    if (ncomp > 20):
        print 'HADDOCK is currently configured for a maximum of twenty molecules!'
        print '=> HADDOCK stopped'
        Messages.StopHaddock()

    #for multiple components: N_COMP contains number of components
    #pdbfileandlist is dictonairy containing <i>:<(pdbfilei,pdblisti)>
    pdbfileandlist={}
    cgpdbfileandlist={}
    #segidkk is dictionairy containing <i>:segidi
    segidkk={}
    for ccii in range(1,1+ncomp):
         pdbfileandlist.update({ccii:('','')})
         pdbnri='PDB_FILE'+str(ccii)
         listnri='PDB_LIST'+str(ccii)
         cgpdbfileandlist.update({ccii:('','')})
         cgpdbnri='CGPDB_FILE'+str(ccii)
         cglistnri='CGPDB_LIST'+str(ccii)
         segidnri='PROT_SEGID_'+str(ccii)
         pdbfileandlist.update({ccii:(new[pdbnri],new[listnri])})
         cgpdbfileandlist.update({ccii:(new[cgpdbnri],new[cglistnri])})
         segidkk.update({ccii:new[segidnri]})
    #set up the project:
    Setup.SetupNewProject(new['HADDOCK_DIR'],\
                          new['PROJECT_DIR'],\
                          new['RUN_NUMBER'],\
                          pdbfileandlist,\
                          cgpdbfileandlist,\
                          new['DIHED_FILE'],\
                          new['RDC1_FILE'], new['RDC2_FILE'],\
                          new['RDC3_FILE'], new['RDC4_FILE'],\
                          new['RDC5_FILE'],\
                          new['DANI1_FILE'], new['DANI2_FILE'],\
                          new['DANI3_FILE'], new['DANI4_FILE'],\
                          new['DANI5_FILE'],\
                          new['PCS1_FILE'], new['PCS2_FILE'],\
                          new['PCS3_FILE'], new['PCS4_FILE'],\
                          new['PCS5_FILE'], new['PCS6_FILE'],\
                          new['PCS7_FILE'], new['PCS8_FILE'],\
                          new['PCS9_FILE'], new['PCS10_FILE'],\
                          new['TENSOR_FILE'],\
                          new['HBOND_FILE'],\
                          segidkk,int(new['N_COMP']),
                          new['CRYO-EM_FILE'],
                          )


    #check if existing distance restraints
    os.mkdir(new['RUN_DIR'] + '/data/distances')
    if new['UNAMBIG_TBL']:
        if os.path.exists(new['UNAMBIG_TBL']) == 1:
            copyunambigtbl2data = new['RUN_DIR'] + '/data/distances/unambig.tbl'
            print '  copying distance restraints data to', copyunambigtbl2data 
            shutil.copyfile(new['UNAMBIG_TBL'], copyunambigtbl2data)
            copyunambigtbl2it0 = new['RUN_DIR']+'/structures/it0/unambig.tbl'
            print '  copying distance restraints data to', copyunambigtbl2it0 
            shutil.copyfile(new['UNAMBIG_TBL'], copyunambigtbl2it0)
            copyunambigtbl2it1 = new['RUN_DIR']+'/structures/it1/unambig.tbl'
            print '  copying distance restraints data to', copyunambigtbl2it1 
            shutil.copyfile(new['UNAMBIG_TBL'], copyunambigtbl2it1)
        else:
            print '  could not find', new['UNAMBIG_TBL']
            whatToDo = 'rm -rf ' + new['RUN_DIR']
            os.system(whatToDo)
            print '  HADDOCK aborted and run directory removed'
            Messages.StopHaddock()
    else: #touch to get an empty file
        touchFile = open(new['RUN_DIR'] + '/data/distances/unambig.tbl', 'w')
        touchFile = open(new['RUN_DIR'] + '/structures/it0/unambig.tbl', 'w')
        touchFile = open(new['RUN_DIR'] + '/structures/it1/unambig.tbl', 'w')
        touchFile.close()
            
    if new['AMBIG_TBL']:
        if os.path.exists(new['AMBIG_TBL']) == 1:
            copyambigtbl2data = new['RUN_DIR'] + '/data/distances/ambig.tbl'
            print '  copying AIR restraint data to', copyambigtbl2data
            shutil.copyfile(new['AMBIG_TBL'], copyambigtbl2data)
            copyambigtbl2it0 = new['RUN_DIR']+'/structures/it0/ambig.tbl'
            print '  copying AIR restraint data to', copyambigtbl2it0
            shutil.copyfile(new['AMBIG_TBL'], copyambigtbl2it0)
            copyambigtbl2it1 = new['RUN_DIR']+'/structures/it1/ambig.tbl'
            print '  copying AIR restraint data to', copyambigtbl2it1
            shutil.copyfile(new['AMBIG_TBL'], copyambigtbl2it1)
        else:
            print 'could not find', new['AMBIG_TBL']
            whatToDo = 'rm -rf ' + new['RUN_DIR']
            os.system(whatToDo)
            print '  HADDOCK aborted and run directory removed'
            Messages.StopHaddock()
    else: #touch to get an empty file
        touchFile = open(new['RUN_DIR'] + '/data/distances/ambig.tbl', 'w')
        touchFile = open(new['RUN_DIR'] + '/structures/it0/ambig.tbl', 'w')
        touchFile = open(new['RUN_DIR'] + '/structures/it1/ambig.tbl', 'w')
        touchFile.close()

    #check if existing CG-to-AA distance restraints
    if new['CGTOAA_TBL']:
        if os.path.exists(new['CGTOAA_TBL']) == 1:
            copycgtoaatbl2data = new['RUN_DIR'] + '/data/distances/cg-to-aa.tbl'
            print '  copying coarse grain to all atom distance restraints data to', copycgtoaatbl2data 
            shutil.copyfile(new['CGTOAA_TBL'], copycgtoaatbl2data)
        else:
            print '  could not find', new['CGTOAA_TBL']
            whatToDo = 'rm -rf ' + new['RUN_DIR']
            os.system(whatToDo)
            print '  HADDOCK aborted and run directory removed'
            Messages.StopHaddock()
    else: #touch to get an empty file
        touchFile = open(new['RUN_DIR'] + '/data/distances/cg-to-aa.tbl', 'w')
        touchFile.close()
            
    #copy files containing list of structures if exisiting
    for ccii in range(1,1+ncomp):
        listnri='PDB_LIST'+str(ccii)
        if new[listnri]: 
          pdbnri='PDB_FILE'+str(ccii)
          copypdbensemble = new['RUN_DIR'] + '/data/ensemble-models/'
          if os.path.exists(new[listnri]) == 1:
            copypdblist = new['RUN_DIR'] + '/data/sequence/file_' + str(ccii) + '.list'
            print '  copying PDB file list of molecule ',ccii,' to ',copypdblist
            shutil.copyfile(new[listnri], copypdblist)
            print '  copying PDB files of the list of molecule ',ccii,' to ',copypdbensemble
            ListFilePDB = open(copypdblist)
            for pdb_location in ListFilePDB.readlines():
                print '  removing chain and segIDs and copying PDB file ',(pdb_location.strip('\n')).replace('\"',''),' of list to ', copypdbensemble
                whatToDo = new['HADDOCK_DIR'] + '/tools/pdb_blank_chain-segid ' + os.path.abspath(pdb_location.strip('\n').replace('\"','')) + '>' + copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"',''))
                os.system(whatToDo)
                #shutil.copyfile(os.path.abspath(pdb_location.strip('\n').replace('\"','')), copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"','')))
            ListFilePDB.close()

            ListFilePDB = open(copypdblist)
            ListFilePDBNew = open(copypdblist + "_", 'w')

            for pdb_location in ListFilePDB.readlines():
                if not useLongJobFileNames:
                    absolute_path="./data/ensemble-models/" + os.path.basename(pdb_location.strip('\n').replace('\"',''))
                else:
                    absolute_path=os.path.abspath(copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"','')))
                ListFilePDBNew.write("\"" + absolute_path + "\"\n")
            ListFilePDB.close()
            ListFilePDBNew.close()
            shutil.move(copypdblist + "_", copypdblist )

            
            #print '  updating PDB file list of molecule ',ccii,' to ',copypdblist, 'with relatif path'
          else:
            print 'could not find', new[listnri]
            whatToDo = 'rm -rf ' + new['RUN_DIR']
            os.system(whatToDo)
            print '  HADDOCK aborted and run directory removed'
            Messages.StopHaddock()

    #copy files containing list of CG structures if exisiting
    for ccii in range(1,1+ncomp):
        listnri='CGPDB_LIST'+str(ccii)
        if new[listnri]: 
          pdbnri='CGPDB_FILE'+str(ccii)
          copypdbensemble = new['RUN_DIR'] + '/data/ensemble-models/'
          if os.path.exists(new[listnri]) == 1:
            copypdblist = new['RUN_DIR'] + '/data/sequence/file_' + str(ccii) + '.list-cg'
            print '  copying coarse grained PDB file list of molecule ',ccii,' to ',copypdblist
            shutil.copyfile(new[listnri], copypdblist)
            print '  copying coarse grained PDB files of the list of molecule ',ccii,' to ',copypdbensemble
            ListFilePDB = open(copypdblist)
            for pdb_location in ListFilePDB.readlines():
                print '  removing chain and segIDs and copying coarse grained PDB file ',(pdb_location.strip('\n')).replace('\"',''),' of list to ', copypdbensemble
                whatToDo = new['HADDOCK_DIR'] + '/tools/pdb_blank_chain-segid ' + os.path.abspath(pdb_location.strip('\n').replace('\"','')) + '>' + copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"',''))
                os.system(whatToDo)
                #shutil.copyfile(os.path.abspath(pdb_location.strip('\n').replace('\"','')), copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"','')))
            ListFilePDB.close()

            ListFilePDB = open(copypdblist)
            ListFilePDBNew = open(copypdblist + "_", 'w')

            print '  Enforcing PDB file absolute path for ' + copypdbensemble
            for pdb_location in ListFilePDB.readlines():
                absolute_path=os.path.abspath(copypdbensemble + os.path.basename(pdb_location.strip('\n').replace('\"','')))
                ListFilePDBNew.write("\"" + absolute_path + "\"\n")
            ListFilePDB.close()
            ListFilePDBNew.close()
            shutil.move(copypdblist + "_", copypdblist )

            
            #print '  updating PDB file list of molecule ',ccii,' to ',copypdblist, 'with relatif path'
          else:
            print 'could not find', new[listnri]
            whatToDo = 'rm -rf ' + new['RUN_DIR']
            os.system(whatToDo)
            print '  HADDOCK aborted and run directory removed'
            Messages.StopHaddock()

    #end of the setup:
    print 'new project',  new['PROJECT_DIR'], 'has been set up.'
    print 'Now you have to edit run.cns in', new['RUN_DIR']
    Messages.StopHaddock()

        
###############################################################################
#2. if run.cns exists:
elif os.path.exists('run.cns') == 1:
    #parse variables out of run.cns in current directory
    print 'parsing run.cns file'
    run = {}
    run = InputFileParser.ParseRunCns()    #define a dictionary run (variablename:value)
    
    #find and check number of components
    ncomp = int(run['ncomponents'])
    tmpdict={1:"A",2:"B",3:"C",4:"D",5:"E",6:"F",7:"G",8:"H",9:"I",10:"J",11:"K",12:"L",13:"M",14:"N",15:"O",16:"P",17:"R",18:"S",19:"T",20:"U"}
    if (ncomp < 2):
        print 'WARNING: Only one molecule defined!'
        print 'This will not be called docking!!!'
    if (ncomp > 20):
        print 'HADDOCK is currently configured for a maximum of twenty molecules!'
        print '=> HADDOCK stopped'
        Messages.StopHaddock()

    #find and check the number of partition for random removal of restraints
    ncvpart = float(run['ncvpart'])
    noecv = run['noecv']
    if (noecv == 'true'):
        if (int(ncvpart) != ncvpart):
            print 'The number of partitions (ncvpart) for random removal of restraints must be an integer!'
            print '=> HADDOCK stopped'
            Messages.StopHaddock()

    #parse run.param in the data directory:
    print 'parsing run.param in', run['datadir']
    new = DictWithDefault.DictWithDefault(None)
    #newparsed is a simple dictionary:
    newparsed = {}
    #get the variables from run.param:
    newparsed = InputFileParser.ParseRunParam(run['datadir'])
    #copy from newparsed to new:
    for kkparsed in newparsed.keys():
              new[kkparsed] = newparsed[kkparsed]
              print kkparsed,new[kkparsed]
        
    #set segids: 
    for ccjj in range(1,1+int(new['N_COMP'])):
      tmpprot_segid='prot_segid_mol'+str(ccjj)
      tmpprot_segidnr='prot_segid_mol'+str(ccjj)
      if (string.strip(run[tmpprot_segid]) == ''):
        run[tmpprot_segid] = tmpdict[ccjj]+'   '
      else:
        run[tmpprot_segid] = run[tmpprot_segid]

    print 'looking for existing files'
    status = {}
    status = ProjectStatus.GetStatus(run)

    #CHANGE    
    #create the queueDic:
    queueDic = create_queueDic(run,1)
    #/CHANGE
    
    #get the runPlusNumber as string (e.g. 'run12'):
    runPlusNumber = ParsePath.GetTail(run['run_dir'])

    #create the CNS links in the protocol directory:
    for icns in range(1, len(run['cns_exe'])+1):
        if run['cns_exe'][icns] != "":
            cnslink = "protocols/cns"+str(icns)
            if not os.path.exists(cnslink):
                if os.path.islink(cnslink): # if link is defined, remove it 
                    os.remove(cnslink)
                os.symlink(run['cns_exe'][icns], cnslink)

            cns_check = subprocess.Popen("./protocols/cns_test.csh", 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                                        
            csh_stdout, csh_stderr = cns_check.communicate()
            match = re.search('CNS-OK', csh_stdout)
            if not match: 
                print "There is a problem with the CNS executable defined in run.cns:"
                print 
                print csh_stderr
                print
                print '=> HADDOCK stopped'
                Messages.StopHaddock()

    #now generate all topology files and missing coordinates
    if run['waterdock'] == 'true':
      generate_complex_inp='/generate_complex-water.inp'
      generate_inp='/generate-water.inp'
      print "waterdock true"
    else:
      print "waterdock false"
      generate_complex_inp='/generate_complex.inp'
      generate_inp='/generate.inp'

    #for substituting the chain 
    parseEval = re.compile('!The next line will be changed automatically.*?\n\s*?evaluate.*?\)')

    check = []
    for cckk in range(1,1+ncomp):
        tmp_psf = 'prot_psf_mol' + str(cckk)
        tmp_cg = 'cg_mol' + str(cckk)
        if status[tmp_psf] == 0:
          check.append(tmp_psf)
          print 'generating PSF and PDB file of molecule %s with the command:' % str(cckk)
          if run[tmp_cg] == 'true':
            print '    generating coarse grained model'
            generate_inp='/generate-cg.inp'

          #change chain numnber in generate script
          generate_out = os.path.join(run['temptrash_dir'], run['fileroot'] + '_' +\
                                      runPlusNumber + '_generate_' + str(cckk) + '.inp')
          inputHandle = open(run['protocolsdir'] + generate_inp)
          outputHandle = open(generate_out, 'w')
          wholeProtocol = string.join(inputHandle.readlines(), '')
          wholeProtocol = parseEval.sub(' evaluate ($chain =' + str(cckk) + ')', wholeProtocol, 1)
          outputHandle.write(wholeProtocol)
          outputHandle.close()                             

          #write the temporary job files in the tempTrashDir:
          jobString = """#!/bin/csh
setenv CURRIT %s
setenv NEWIT 
setenv PREVIT
setenv RUN ./
setenv BEGIN ./begin/
setenv TEMPTRASH $RUN
%s < %s >! %s
          """ % ('0',\
                 cnslink,generate_out,\
                 run['begindir'] + '/generate_' + str(cckk) + '.out')

          jobFN = os.path.join(run['temptrash_dir'], run['fileroot'] + '_' +\
                  runPlusNumber + '_generate_' + str(cckk) + '.job')
          if not useLongJobFileNames:
              jobFN = ParsePath.GetTail(jobFN)
          QueueSubmit(run['queue'][1], jobFN, jobString, run, 1, run['fileroot'])

          if run[tmp_cg] == 'true':
            print '    generating all atoms model'
            generate_inp='/generate.inp'

            #change chain numnber in generate script
            generate_out = os.path.join(run['temptrash_dir'], run['fileroot'] + '_' +\
                                        runPlusNumber + '_generate_' + str(cckk) + '-aa.inp')
            inputHandle = open(run['protocolsdir'] + generate_inp)
            outputHandle = open(generate_out, 'w')
            wholeProtocol = string.join(inputHandle.readlines(), '')
            wholeProtocol = parseEval.sub(' evaluate ($chain =' + str(cckk) + ')', wholeProtocol, 1)
            outputHandle.write(wholeProtocol)
            outputHandle.close()                             

            jobString = """#!/bin/csh
setenv CURRIT %s
setenv NEWIT 
setenv PREVIT
setenv RUN ./
setenv BEGIN ./begin-aa/
setenv TEMPTRASH $RUN
%s < %s >! %s
            """ % ('0',\
                   cnslink,\
                   generate_out,\
                   run['begin_aa_dir'] + '/generate_' + str(cckk) + '.out')
            jobFN = os.path.join(run['temptrash_dir'], run['fileroot'] + '_' +\
                    runPlusNumber + '_generate_' + str(cckk) + '-aa.job')
            if not useLongJobFileNames:
                jobFN = ParsePath.GetTail(jobFN)
            QueueSubmit(run['queue'][1], jobFN, jobString, run, 1, run['fileroot'])
    QueueFlush()
    while 1:
      breaking = True
      status = ProjectStatus.GetStatus(run)              
      for ccll in range(1,1+ncomp):
        tmp_psf = 'prot_psf_mol' + str(ccll)
        if status[tmp_psf] == "finished": continue
        if status[tmp_psf] == "crashed":
            print "Error in the topology generation: %s could not be created" % tmp_psf
            print '=> HADDOCK stopped'
            Messages.StopHaddock()
        breaking = False
      print '  waiting for the psf files...'
      time.sleep(10)
      if breaking: break

    # Generating the topology and coordinate files for the complex
    #merging topologies and coordinate files:                     

    if status['templatefile'] == 0:
        # Generate combinations.list file to feed generate_complex.inp
        # if crossdock is false, take pairs (1,1), (2,2), ..
        crossdock_bool = 'true' == run['crossdock'].lower() # str..

        # Build list of models per component
        lst_models = []
        for ccll in range(1, 1+ncomp):
            listf = 'file_' + str(ccll) + '.list'
            fpath = os.path.join(run['begindir'], listf)
            with open(fpath, 'r') as fhandle:
                lst_models.append([model.strip() for model in fhandle])

        if crossdock_bool:
            combinations = list(product(*lst_models))

            n_combinations = len(combinations)
            if n_combinations > MAX_COMBINATIONS:
                print
                print "Maximum number of combinations reached."
                print '=> HADDOCK stopped'
                Messages.StopHaddock()

            fpath = os.path.join(run['begindir'], 'combinations.list')
            if os.path.exists(fpath):
                os.remove(fpath)
            with open(fpath, 'w') as fhandle:
                for cmplx in combinations:
                    fhandle.write('\n'.join([c for c in cmplx]))
                    fhandle.write('\n')
            fhandle.close()
        else:
            # All ensembles should be the same size
            lst_n_models = map(len, lst_models)
            max_n_models = max(lst_n_models)
            if len(set(lst_n_models)) > 1:
                print
                print "Ensemble size differs for some models. Check your input."
                print "When not crossdocking, all ensembles must have the same number of models"
                print '=> HADDOCK stopped'
                Messages.StopHaddock()
            else:
                combinations = [[i for c in range(ncomp)] for i in xrange(max_n_models)]
        
            n_combinations = len(combinations)
            if n_combinations > MAX_COMBINATIONS:
                print
                print "Maximum number of combinations reached."
                print '=> HADDOCK stopped'
                Messages.StopHaddock()

            # write combinations.list file
            fpath = os.path.join(run['begindir'], 'combinations.list')
            if os.path.exists(fpath):
                os.remove(fpath)
            fhandle = open(fpath, 'w')
            for cmplx in combinations:
                for imol, mol in enumerate(cmplx):
                    fhandle.write(lst_models[imol][mol] + '\n')
            fhandle.close()

        print 'merging topologies and coordinates files with the command:'
        time.sleep(2) #just to make sure that .psf file is written out...
        #write the temporary job files in the tempTrashDir:    
        jobString = """#!/bin/csh
setenv CURRIT %s
setenv NEWIT
setenv PREVIT
setenv RUN ./
setenv BEGIN ./begin
setenv TEMPTRASH $RUN
%s < %s >! %s
        """ %  ('0',\
               cnslink,\
               run['protocolsdir'] + generate_complex_inp,\
               run['begindir'] + '/generate_complex.out')
        jobFN = os.path.join(run['temptrash_dir'], run['fileroot'] + '_' +\
                             runPlusNumber +\
                             '_generate_complex.job')
        if not useLongJobFileNames:
            jobFN = ParsePath.GetTail(jobFN)
        QueueSubmit(run['queue'][1], jobFN, jobString, run, 1, run['fileroot'])
        QueueFlush()
        #wait for the template file:
        print '  waiting for the merged files...'
        while 1:
            status = ProjectStatus.GetStatus(run)
            if status['psffile'] == "finished": break
            if status['psffile'] == "crashed":
                print "Error in the topology generation: merged files could not be created" 
                print '=> HADDOCK stopped'
                Messages.StopHaddock()
            time.sleep(10)
        QueueFlush(finished=True)

    #Check that an eventual skipping of structures in it0 will result in at
    #least the number of structures defined for it1 otherwise decrease the value

    nstruc0=int(run['structures'][0])
    nstruc1=int(run['structures'][1])
    nskip=int(run['skip_struc'])
    nskip=nskip+1
    nkeep=int(nstruc0/nskip)
    while nkeep < nstruc1:
        nskip=nskip-1
        nkeep=int(nstruc0/nskip)
        run['skip_struc']=str(nskip-1)
        print'skip_struc decreased to ',nskip-1,' to keep enough structures for it1'
      
    for currit in range(0,2):
       
        nstruc=int(run['structures'][currit])
        if nstruc == 0:
            print 'Number of structures for iteration',currit,' is zero.'
            print '=> HADDOCK stopped'
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean' 
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()
        newit_tail = 'structures/it'+str(currit)
        run['newit'] = os.path.join(run['run_dir'], newit_tail)
        status = ProjectStatus.GetStatus(run)
        print 'looking for iteration', currit
        fileliststatus = 'filelist' + str(currit)
        if status[fileliststatus] == 0:
            print 'working on iteration ' + str(currit)
            if currit == 0:
                previt_tail = 'begin'                
            else:
                lastit = currit - 1
                previt_tail = 'structures/it'+str(lastit) 
            #numstruc = int(run['structures'][1]) * (int(run['skip_struc'])+1)
            run['previt'] = os.path.join(run['run_dir'], previt_tail)
            if currit > 0:
              prev_filenam = run['previt'] + "/file.nam"
              prev_nrs = []
              for a in open(prev_filenam).readlines():
                if len(a.strip()) == 0: continue
                prev_nrs.append(int(a[a.rindex("_")+1:a.rindex(".pdb")])-1)
              for n in range(int(run['structures'][currit])):
                destfile = "%s/ambig.tbl_%d" % (run['newit'], n+1)
                sourcefile = "%s/ambig.tbl_%d" % (run['previt'], prev_nrs[n]+1)
                if os.path.exists(sourcefile) and not os.path.exists(destfile): shutil.copyfile(sourcefile, destfile)
            try:  
              MHaddock.ForAllIterations(run['run_dir'], run['protocolsdir'],\
                                   newit_tail, run['temptrash_dir'],\
                                   currit,run['fileroot'], previt_tail,\
                                   run['templatefile'],\
                                   run['structures'] [currit],\
                                   run['haddock_dir'], run)
            except HaddockError, error:
              print error.value
              Messages.StopHaddock()
                                   
#            if currit == 0:
#                if run['smoothing'] == 'true':
#                    com = run['haddock_dir' ]+ "/smoothing/csb_selection.csh " \
#                        + run['prot_segid_A']+ " " + run['prot_segid_B'] + " " + str(numstruc)
#                    olddir = os.getcwd()
#                    os.chdir(run['newit'])
#                    os.system(com)
#                    os.chdir(olddir)
        
        else:
            print 'file.list exists => iteration', \
                  currit, 'finished.'

       
##################################################
#analysis of iteration 1:
        if run['runana'] != 'none':

            if currit == 1:
                status = ProjectStatus.GetStatus(run)
                if status['analysis'] == 0:
                 
                    CnsAnalysis.Analysis(run['run_dir'], run['haddock_dir'], run['protocolsdir'],\
                                         newit_tail, run['temptrash_dir'],\
                                         currit, queueDic, run['fileroot'])
                else:
                    print 'CNS analysis files in it1/analysis already exist.'
                    print 'To rerun the analysis delete the "DONE" file in the analysis directory.'

#water refinement of iteration 1:
        if currit == 1 and run['firstwater'] == "no":
            waterrun = os.path.join(run['run_dir'], 'structures/it1/water')
            run['previt'] = os.path.join(run['run_dir'] , 'structures/it1')
            os.system("rm -rf %s" % (waterrun))
            os.system("cd %s; ln -s ./ water" % (run['previt']))

        if currit == 1 and run['firstwater'] == "yes":
            waterrun = os.path.join(run['run_dir'], 'structures/it1/water')
            run['previt'] = os.path.join(run['run_dir'] , 'structures/it1')
            if (run['firstwater'] == 'yes' and run['waterrefine'] != '0'):
                if int(run['waterrefine']) > int(run['structures'][1]):
                    run['waterrefine'] = run['structures'][1]
                if os.path.exists(waterrun + '/file.list'):
                    print 'file it1/water/file.list already exists => water refinement done.'
                else:
                    for n in range(int(run['structures'][currit])):
                      destfile = "%s/ambig.tbl_%d" % (run['newit'], n+1)
                      sourcefile = "%s/ambig.tbl_%d" % (run['previt'], n+1)
                      if os.path.exists(sourcefile) and not os.path.exists(destfile): shutil.copyfile(sourcefile, destfile)
                
                    try:
                        MHaddock.ForAllIterations(run['run_dir'], run['protocolsdir'],\
                                       newit_tail, run['temptrash_dir'],\
                                       '2',run['fileroot'], "structures/it1",\
                                       run['templatefile'],\
                                       run['waterrefine'],\
                                       run['haddock_dir'], run)
                    except HaddockError, error:
                        print error.value
                        Messages.StopHaddock()

#analysis of the waterrefined structures (after iteration 1):
            if run['runana'] != 'none':
                if status['analysis_water'] == 0:
                    #1. copy unambig.tbl and ambig.tbl from it1 to it1/water:
                    shutil.copyfile(run['newit'] + '/ambig.tbl', run['newit'] + '/water/ambig.tbl')
                    shutil.copyfile(run['newit'] + '/unambig.tbl', run['newit'] + '/water/unambig.tbl')
                    #2. start the cns protocols:
                    CnsAnalysis.Analysis(run['run_dir'], run['haddock_dir'], run['protocolsdir'],\
                                         newit_tail + '/water', run['temptrash_dir'],\
                                         2, queueDic, run['fileroot'])
                else:
                    print 'CNS analysis files of the water refined structures already exist.'
                    print 'To rerun the analysis delete the "DONE" file in the analysis directory.'
   
        if run['runana'] != 'none':

            if currit == 1:
                status = ProjectStatus.GetStatus(run)
                if status['clust'] == 0:
                    print '  waiting for the matrix file in it1/analysis...'
                    while 1:
                        if status['matrix'] : break
                        status = ProjectStatus.GetStatus(run)
                        time.sleep(10)

                    print '  matrix file in it1/analysis is found'
                    print '  running clustering for it1/'
                    if run['clust_meth'] == 'RMSD':
                        clstcmd = run['toolsdir'] + '/cluster_struc ' + run['fileroot'] + '_rmsd.disp'  \
                                  + ' ' + run['clust_cutoff'] + ' ' + run['clust_size']+ ' >cluster.out'
                    else:
                        clstcmd = run['toolsdir'] + '/cluster_fcc.py ' + run['fileroot'] + '_fcc.disp'  \
                                  + ' ' + run['clust_cutoff'] + ' -c ' + run['clust_size']+ ' >cluster.out'
                    anaDir = run['newit'] + "/analysis"
                    os.chdir(anaDir)
                    os.system(clstcmd)
                    while os.stat("cluster.out").st_size == 0 and int(run['clust_size']) > 1:
                        run['clust_size'] = str(int(int(run['clust_size'])/2))
                        print 'No cluster, redo clustering with lower clust_size: ', run['clust_size']
                        if run['clust_meth'] == 'RMSD':
                            clstcmd = run['toolsdir'] + '/cluster_struc ' + run['fileroot'] + '_rmsd.disp'  \
                                      + ' ' + run['clust_cutoff'] + ' ' + run['clust_size']+ ' >cluster.out'
                        else:
                            clstcmd = run['toolsdir'] + '/cluster_fcc.py ' + run['fileroot'] + '_fcc.disp'  \
                                      + ' ' + run['clust_cutoff'] + ' -c ' + run['clust_size']+ ' >cluster.out'
                        os.system(clstcmd)

                    print "  Clustering in ",anaDir," DONE"
                    print "  Check file ",anaDir,"/cluster.out"
                    touchFile = open(anaDir + '/CLUST_DONE', 'w')
                    touchFile.close()

                else:
                    print 'Cluster file in it1/analysis already exist.'
                    print 'To rerun the clustering delete the "CLUST_DONE" file in the analysis directory.'

                if run['runana'] == 'full': 

                    print '  waiting for the ene-residue file in it1/analysis...'
                    while 1:
                        if status['ene'] : break
                        status = ProjectStatus.GetStatus(run)
                        time.sleep(10)
                    print '  ene-residue file in it1/analysis is found'

                import glob
                psFiles = glob.glob('*.out')
                for fileN in psFiles:
                    os.system('gzip -f ' + fileN) # -f for overwriting

            if (currit == 1 and run['firstwater'] == 'yes' and run['waterrefine'] != '0'):
                if status['clust_water'] == 0:
                    print '  waiting for the matrix file in water/analysis...'
                    while 1:
                        if status['matrix_water'] : break
                        status = ProjectStatus.GetStatus(run)
                        time.sleep(10)

                    print '  matrix file in water/analysis is found'
                    print '  running clustering for it1/water'
                    if run['clust_meth'] == 'RMSD':
                        clstcmd = run['toolsdir'] + '/cluster_struc ' + run['fileroot'] + '_rmsd.disp'  \
                                  + ' ' + run['clust_cutoff'] + ' ' + run['clust_size']+ ' >cluster.out'
                    else:
                        clstcmd = run['toolsdir'] + '/cluster_fcc.py ' + run['fileroot'] + '_fcc.disp'  \
                                  + ' ' + run['clust_cutoff'] + ' -c ' + run['clust_size']+ ' >cluster.out'

                    anaDir = run['newit'] + "/water/analysis"
                    os.chdir(anaDir)
                    os.system(clstcmd)
                    print "  Clustering in ",anaDir," DONE"
                    while os.stat("cluster.out").st_size == 0 and int(run['clust_size']) > 1:
                        run['clust_size'] = str(int(run['clust_size'])/2)
                        print 'No cluster, redo clustering with lower clust_size: ', run['clust_size']
                        if run['clust_meth'] == 'RMSD':
                            clstcmd = run['toolsdir'] + '/cluster_struc ' + run['fileroot'] + '_rmsd.disp'  \
                                      + ' ' + run['clust_cutoff'] + ' ' + run['clust_size']+ ' >cluster.out'
                        else:
                            clstcmd = run['toolsdir'] + '/cluster_fcc.py ' + run['fileroot'] + '_fcc.disp'  \
                                      + ' ' + run['clust_cutoff'] + ' -c ' + run['clust_size']+ ' >cluster.out'
                        os.system(clstcmd)

                    print "  Check file ",anaDir,"/cluster.out"
                    touchFile = open(anaDir + '/CLUST_DONE', 'w')
                    touchFile.close()

                else:
                    print 'Cluster file in it1/water/analysis already exist.'
                    print 'To rerun the clustering delete the "CLUST_DONE" file in the analysis directory.'

                if run['runana'] == 'full':

                    print '  waiting for the ene-residue file in it1/water/analysis...'
                    while 1:
                        if status['ene_water'] : break
                        status = ProjectStatus.GetStatus(run)
                        time.sleep(10)
                    print '  ene-residue file in it1/water/analysis is found'

                    print '  Now compressing the output files...'
                    import glob
                    psFiles = glob.glob('*.out')
                    for fileN in psFiles:
                        os.system('gzip -f ' + fileN) # -f for overwriting

            messageString = """finished the analysis.

###############################################################################

Please have a look at the structure ensemble in
%s/structures/it1

The water refined structures can be found in:
%s/structures/it1/water

Analysis files were written to the directories:
%s/structures/it1/analysis
%s/structures/it1/water/analysis

###############################################################################
############################################################################### """

        else:
            messageString = """No analysis performed.

###############################################################################

Please have a look at the structure ensemble in
%s/structures/it1

The water refined structures can be found in:
%s/structures/it1/water

###############################################################################
############################################################################### """

if run['cleanup'] == "true":
    os.chdir(run['run_dir'])
    cleancmd = run['toolsdir'] + '/haddock-clean' 
    print "  Cleaning up the run directory ... "
    os.system(cleancmd)
#regular end of HADDOCK:
Messages.StopHaddock()
