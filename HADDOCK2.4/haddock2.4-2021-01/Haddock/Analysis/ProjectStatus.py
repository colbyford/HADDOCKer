"""
a module for checking the status of your project
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:21 $"

import os, string, time
from Haddock.Analysis.Diagnostic import DiagnoseStructures
from Haddock.Main import Messages

topology_timeout = {}

def GetStatus(run):
    """
    checks the whole directory tree of your project
    GetStatus is looking for all the files and directories, which are
    necessary to run your project
    it creates an dictionary, in which the value:
    0 means: 'has to been done, not yet finished'
    1 means: 'is o.k., already done'
    values for the structures (pdb_..., wpdb_...) are set by DiagnoseStructures and are verbose:
    'waiting'
    'running'
    'finished'
    'crashed'
    
    INPUT:   run is a dictionary with all the information parsed out of
             run.cns
    OUTPUT:  returns a dictionary with the status (0 or 1)
    USAGE:   status = GetStatus(run)
    """
    global topology_timeout 

    status = {}   #the dictionary with all the status information

    #looking for a list of files and directories:
    lookfor = {run['haddock_dir']: 'haddock_dir',            #Haddock program
               run['protocolsdir']: 'protocolsDir',
               run['run_dir']: 'run_dir',
               run['begindir']: 'begindir',
               run['datadir']: 'datadir',
               run['sequencedir']: 'sequencedir',
               run['structuresdir']: 'structuresdir',      
               run['templatefile']: 'templatefile'
               }
    run['project_dir'] = run['run_dir'] + '/' + run['fileroot']
    runDir = run['run_dir']

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
    
    for file in lookfor.keys():
        if os.path.exists(file):
#           print ' ', file, 'exists'
            status[lookfor[file]] = 1
        else:
#           print ' ', file, 'does not exist'
            status[lookfor[file]] = 0

    #looking for pdb and psf files in the begin directory
    ncomp = int(run['ncomponents'])
    for ccii in range(0,1+ncomp):
        if ccii == 0:           
          lookfor = {run['psffile']: 'psffile'}
          tmp_out = run['begindir'] + '/generate_complex.out'
        else:
          tmp_psf =  'prot_psf_mol' + str(ccii)
          tmp_coor = 'prot_coor_mol' + str(ccii)
          tmp_out = run['begindir'] + '/generate_' + str(ccii) + '.out'
          lookfor = {run[tmp_coor]: tmp_coor,
                     run[tmp_psf]: tmp_psf
                    }
        for file in lookfor.keys():
            if os.path.exists(file):
                status[lookfor[file]] = 'finished'
            elif os.path.exists(tmp_out):
                lastlines = open(tmp_out).readlines()[-20:]
                finished = len([l for l in lastlines if l.find("Program stopped at:") > -1])
                if finished:                
                    if file not in topology_timeout:
                      topology_timeout[file] = 0
                    if os.path.exists(file):
                      status[lookfor[file]] = 'finished'
                    else:
                      status[lookfor[file]] = 'pending'                     
                      print 'waiting for %s...' % file                                
                      topology_timeout[file] += 1
                      if topology_timeout[file] >= 7:
                        status[lookfor[file]] = 'crashed'
                else:
                    status[lookfor[file]] = 'running'
            else:
#               print ' ', file, 'does not exist'
                status[lookfor[file]] = 0
  
    #looking for file.list, ambig.tbl and unambig.tbl in the
    #directories of every iteration:
    for currit in range(0,3):
        currit = str(currit)
        if os.path.exists(run['run_dir'] + '/structures/it' + currit +\
                          '/file.list'):
#           print ' ', 'file.list of iteration', currit, 'exists'
            status['filelist' + currit] = 1
        else:
#           print ' ', 'file.list of iteration', currit, "doesn't exist"
            status['filelist' + currit] = 0
        if os.path.exists(run['run_dir'] + '/structures/it' + currit + '/unambig.tbl'):
            status['unambigtbl' + currit] = 1
        else:
            status['unambigtbl' + currit] = 0
            
        if os.path.exists(run['run_dir'] + '/structures/it' + currit + '/ambig.tbl'):
            status['ambigtbl' + currit] = 1
        else:
            status['ambigtbl' + currit] = 0
    #looking for each structure in each iteration:
    DiagnoseStructures(run, status)
    #looking for the analysis files (just look for the 'DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/analysis/DONE'):
        status['analysis'] = 1
    else:
        status['analysis'] = 0
    
    #looking for the water analysis files (just look for the 'DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/water/analysis/DONE'):
        status['analysis_water'] = 1
    else:
        status['analysis_water'] = 0
        
    #looking for the matrix analysis files (just look for the 'MTX_DONE' file)
    # since we run either FCC or RMSD, there shouldnt be a conflict.
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/analysis/MTX_DONE'):
        status['matrix'] = 1
    else:
        status['matrix'] = 0
    
    #looking for the ene-residue analysis file (just look for the 'ENE_DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/analysis/ENE_DONE'):
        status['ene'] = 1
    else:
        status['ene'] = 0
        
    #looking for the water ene-residue analysis files (just look for the 'ENE_DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/water/analysis/ENE_DONE'):
        status['ene_water'] = 1
    else:
        status['ene_water'] = 0
        
    #looking for the water matrix analysis files (just look for the 'MTX_DONE' file)
    # since we run either FCC or RMSD, there shouldnt be a conflict.
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/water/analysis/MTX_DONE'):
	status['matrix_water'] = 1
    else:
        status['matrix_water'] = 0

    #looking for the clustering analysis files (just look for the 'CLUST_DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/analysis/CLUST_DONE'):
        status['clust'] = 1
    else:
        status['clust'] = 0
    
    #looking for the water clustering analysis files (just look for the 'CLUST_DONE' file)
    #that's a simple check:
    if os.path.exists(run['run_dir'] + '/structures/it1/water/analysis/CLUST_DONE'):
        status['clust_water'] = 1
    else:
        status['clust_water'] = 0
        
    #looking for the waterrefined structures in /structures/it1/water:
#CHANGE    
#/CHANGE    
    return status
