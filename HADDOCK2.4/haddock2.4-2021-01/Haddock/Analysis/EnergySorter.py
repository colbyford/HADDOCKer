"""
a module for sorting ARIA .pdb files regarding energy
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:21 $"

import glob,  os, re, string, sys
from Haddock.DataIO import InputFileParser
from Haddock.Main import Messages
from Haddock.ThirdParty import TextFile

###############################################################################
def WriteFileList(directory, outDir='', howMany=100000, message=1, fileNam=1,\
                  fileCns=1, nstskip=0, iteration=0):
    """
    reads all PDB files in the given directory
    INPUT:   directory=the directory to look for the .pdb files
             outDir=the directory to write the file.list
             howMany=howMany structures to write in file.list
             message=toggle for printing a message (1=on, 0=off)
             fileNam=toggle for printing file.nam (1=on, 0=off)
    writes the file file.list in given directory
    also writes a file called file.nam for MolMol which contains
    a list of all the pdb files

REMARK            total,bonds,angles,improper,dihe,vdw,elec,air,cdih,coup,rdcs,vean,dani,xpcs,rg
REMARK energies: 242.472, 0, 0, 0, 0, -9.799114E-02, -17.2306, 259.8, 0, 0, 0, 0, 0, 0, 0
                                                     
    """
    run = {}
    run = InputFileParser.ParseRunCns()    #define a dictionary run (variablename:value)

    if outDir == '':
        outDir = directory
    if message == 1:
        print '    creating file.list in', outDir
    if message == 1 and fileNam == 1:
        print '    creating file.nam in', outDir
    if message == 1 and fileCns == 1:
        print '    creating file.cns in', outDir

    #get a list of all the pdb files:
    pdbFiles = glob.glob(directory + '/*[0-9].pdb')
    if len(pdbFiles) == 0:
        pdbFiles = glob.glob(directory + '/*w.pdb')
    if len(pdbFiles) == 0:
        if fileNam == 1:
            print '    no pdb files found => file.list and file.nam not created'
        else:
            print '    no pdb files found => file.list not created'
        return

    #parse the energies from the pdb files:
    energiesAndFiles = {}  #key: energy, value: list of filename(s)
    for x in pdbFiles:  #loop over all the pdb files in given directory
        overallEnergy = 0.0
        vdwEnergy = 0
        elecEnergy = 0
        noeEnergy = 0
        cdihEnergy = 0
        saniEnergy = 0
        veanEnergy = 0
        daniEnergy = 0
        xpcsEnergy = 0
        rgEnergy = 0
        buriedasa = 0
        symEnergy = 0
        dHbinding = 0
        desolvEnergy = 0
        waterEnergy = 0
        watervdw = 0.0
        waterelec = 0.0
        lccEnergy = 0.0
        for line in open(x).readlines():
            if line[0:16] == 'REMARK energies:':
                lineList = string.split(line)
                #get the vdw energy:
                vdwEnergy = lineList[7]
                #get the elec energy:
                elecEnergy = lineList[8]
                #get the NOE restraint energy:
                noeEnergy = lineList[9]
                #get the cdih restraint energy:
                cdihEnergy = lineList[10]
                #get the sani restraint energy:
                saniEnergy = lineList[12]
                #get the vean restraint energy:
                veanEnergy = lineList[13]
                #get the dani restraint energy:
                daniEnergy = lineList[14]
                #get the xpcs estraint energy:
                xpcsEnergy = lineList[15]
                #get the Rg restraint energy:
                rgEnergy = lineList[16]

                #get rid of the comma:
                vdwEnergy = vdwEnergy[:-1]
                elecEnergy = elecEnergy[:-1]
                noeEnergy = noeEnergy[:-1]
                cdihEnergy = cdihEnergy[:-1]
                saniEnergy = saniEnergy[:-1]
                if len(lineList) > 14:
                    veanEnergy = veanEnergy[:-1]
                if len(lineList) > 15:
                    daniEnergy = daniEnergy[:-1]
                if len(lineList) > 16:
                    xpcsEnergy = xpcsEnergy[:-1]
                    
            if line.startswith('REMARK Local cross-correlation:'):
                lccEnergy = float(line.split()[3])

            if line[0:15] == 'REMARK Symmetry':
                lineList = string.split(line)
                symEnergy = lineList[3]

            if line[0:18] == 'REMARK Desolvation':
                lineList = string.split(line)
                desolvEnergy = lineList[3]

            if line[0:14] == 'REMARK Binding':
                lineList = string.split(line)
                dHbinding = lineList[3]

            if line[0:13] == 'REMARK buried':
                lineList = string.split(line)
                buriedasa = lineList[4]
        
            if line[0:20] == 'REMARK water - chain':
                lineList = string.split(line)
                watervdw = watervdw + float(lineList[5])
                waterelec = waterelec + float(lineList[6])

            if line[0:20] == 'REMARK water - water':
                lineList = string.split(line)
                watervdw = watervdw + float(lineList[5])
                waterelec = waterelec + float(lineList[6])
                break

        it = iteration 
        if it not in (0, 1):
            it = 2
        overallEnergy = overallEnergy + float(run['w_vdw'][it]) * float(vdwEnergy)
        overallEnergy = overallEnergy + float(run['w_vdw'][it]) * watervdw
        overallEnergy = overallEnergy + float(run['w_elec'][it]) * float(elecEnergy)
        overallEnergy = overallEnergy + float(run['w_elec'][it]) * waterelec
        overallEnergy = overallEnergy + float(run['w_dist'][it]) * float(noeEnergy)
        overallEnergy = overallEnergy + float(run['w_cdih'][it]) * float(cdihEnergy)
        overallEnergy = overallEnergy + float(run['w_sani'][it]) * float(saniEnergy)
        overallEnergy = overallEnergy + float(run['w_vean'][it]) * float(veanEnergy)
        overallEnergy = overallEnergy + float(run['w_dani'][it]) * float(daniEnergy)
        overallEnergy = overallEnergy + float(run['w_xpcs'][it]) * float(xpcsEnergy)
        overallEnergy = overallEnergy + float(run['w_rg'][it]) * float(rgEnergy)
        overallEnergy = overallEnergy + float(run['w_sym'][it]) * float(symEnergy)
        overallEnergy = overallEnergy + float(run['w_bsa'][it]) * float(buriedasa)
        overallEnergy = overallEnergy + float(run['w_deint'][it]) * float(dHbinding)
        overallEnergy = overallEnergy + float(run['w_desolv'][it]) * float(desolvEnergy)
        overallEnergy = overallEnergy + float(run['w_lcc'][it]) * float(lccEnergy)

        #define a dictionary, use a list for the files:
        if energiesAndFiles.has_key(overallEnergy):
            energiesAndFiles[overallEnergy].append(os.path.split(x)[1])
        else:
            energiesAndFiles[overallEnergy] = [os.path.split(x)[1], ]

    #create a sorted list which contains the energies:
    energies = energiesAndFiles.keys()
    energies.sort()      #numerically sorted because of float() above

    #open file.list , file.nam and file.cns filehandles:
    try:
        fileListHandle = open (outDir + '/file.list', 'w')
    except IOError:
        print "couldn't create file.list in directory", outDir
        if run['cleanup'] == "true":
            os.chdir(run['run_dir'])
            cleancmd = run['toolsdir'] + '/haddock-clean'
            print "  Cleaning up the run directory ... "
            os.system(cleancmd)
        Messages.StopHaddock()
    if fileNam == 1:
        try:
            namHandle = open (outDir + '/file.nam', 'w')
        except IOError:
            print "couldn't create file.nam in directory", outDir
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean'
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()
    else:
        namHandle = None
    cnsHandle = None  # by default
    if fileCns == 1:
        try:
            cnsHandle = open (outDir + '/file.cns', 'w')
        except IOError:
            print "couldn't create file.cns in directory", outDir
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean'
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()
    else:
        cnsHandle = None
        
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

    #output - files sorted regarding energy:
    zzz = 0
    iskip = nstskip
    for value in energies[:min(howMany, len(energies))]:
        xxx = 0
        while xxx < len(energiesAndFiles[value]):
            if iskip == nstskip:
                fileListHandle.write('"PREVIT:' + str(energiesAndFiles[value][xxx]) +\
                                     '"  { ' + str(value) + ' }\n')
                if fileNam == 1:
                    namHandle.write(str(energiesAndFiles[value][xxx]) + '\n')
                if fileCns == 1:
                    cnsHandle.write('evaluate (&filenames.bestfile_' +\
                                    str(zzz+1) + '="PREVIT:' +\
                                    str(energiesAndFiles[value][xxx]) +\
                                    '")\n')
                zzz = zzz + 1 
                iskip=iskip-1
            else:
                iskip=iskip-1
            if iskip < 0: iskip=nstskip
            xxx = xxx + 1
    cnsHandle.write('\n\n') #important for CNS!!!
    
    #close the file handles:
    fileListHandle.close()
    if fileNam == 1:
        namHandle.write('\n\n')
        namHandle.close()
    if fileCns == 1:
        cnsHandle.write('\n\n')
        cnsHandle.close()

    if nstskip > 0:
        #write a second set of files containing all structures since in the
        #first set structures were skipped
        #open file.list , file.nam_all and file.cns_all filehandles:
        try:
            fileListHandle = open (outDir + '/file.list_all', 'w')
        except IOError:
            print "couldn't create file.list_all in directory", outDir
            if run['cleanup'] == "true":
                os.chdir(run['run_dir'])
                cleancmd = run['toolsdir'] + '/haddock-clean'
                print "  Cleaning up the run directory ... "
                os.system(cleancmd)
            Messages.StopHaddock()
        if fileNam == 1:
            try:
                namHandle = open (outDir + '/file.nam_all', 'w')
            except IOError:
                print "couldn't create file.nam_all in directory", outDir
                if run['cleanup'] == "true":
                    os.chdir(run['run_dir'])
                    cleancmd = run['toolsdir'] + '/haddock-clean'
                    print "  Cleaning up the run directory ... "
                    os.system(cleancmd)
                Messages.StopHaddock()
        else:
            namHandle = None
        cnsHandle = None  # by default
        if fileCns == 1:
            try:
                cnsHandle = open (outDir + '/file.cns_all', 'w')
            except IOError:
                print "couldn't create file.cns in directory", outDir
                if run['cleanup'] == "true":
                    os.chdir(run['run_dir'])
                    cleancmd = run['toolsdir'] + '/haddock-clean'
                    print "  Cleaning up the run directory ... "
                    os.system(cleancmd)
                Messages.StopHaddock()
        else:
            cnsHandle = None
            
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

        #output - files sorted regarding energy:
        zzz = 0
        for value in energies[:min(howMany, len(energies))]:
            xxx = 0
            while xxx < len(energiesAndFiles[value]):
                fileListHandle.write('"PREVIT:' + str(energiesAndFiles[value][xxx]) +\
                                     '"  { ' + str(value) + ' }\n')
                if fileNam == 1:
                    namHandle.write(str(energiesAndFiles[value][xxx]) + '\n')
                if fileCns == 1:
                    cnsHandle.write('evaluate (&filenames.bestfile_' +\
                                    str(zzz+1) + '="PREVIT:' +\
                                    str(energiesAndFiles[value][xxx]) +\
                                    '")\n')
                xxx = xxx + 1 
                zzz = zzz 
        cnsHandle.write('\n\n') #important for CNS!!!
    
        #close the file handles:
        fileListHandle.close()
        if fileNam == 1:
            namHandle.write('\n\n')
            namHandle.close()
        if fileCns == 1:
            cnsHandle.write('\n\n')
            cnsHandle.close()
        print 'Since structures were skipped in the sorting of it0 (skip_struc>0 in run.cns'
        print 'a second set of file was created containing all structures.'
        print 'See file.nam_all, file.list_all and file.cns_all'
 
if __name__ == "__main__":
    print 'starting to work on current directory:'
    cwd = os.getcwd()
    print cwd
    WriteFileList(cwd, cwd, 100000, 1, 1, 1, 'totener')
    
