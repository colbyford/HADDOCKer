import Haddock.Main.QueueSubmit_nopackage 
from Haddock.Main.QueueThread import QueueThread
import os, sys

otherqueuecommand = "/home/enmr/software/bin/ssub haddock"
#otherqueuecommand = "/bin/csh"

currjobfilename = None
currqueuecommand = None
jobfiles = []
pending_jobs = 0
lastcurrit = ""
libfiles = []
prevfiles = []
resultfiles = []

def QueueSubmit(queuecommand, jobfilename, job_contents, run, jobmax, fileroot):
  queuemax = 1
  for k in run['cpunumber'].keys():
    if run['queue'][k] == queuecommand:
      queuemax = int(run['cpunumber'][k])
  global jobfiles, currjobfilename, currqueuecommand, pending_jobs, lastcurrit, libfiles, prevfiles, resultfiles
  currit = "other"
  if jobfilename.endswith("w.job"): currit = "water"
  if "water" in jobfilename and "package" in jobfilename: currit = "water"
  elif jobfilename.rfind("_") > -1:
    j = jobfilename[:jobfilename.rindex("_")]
    if j.endswith("_it0_refine"): currit = "it0"
    elif j.endswith("_it1_refine"): currit = "it1"
  lastcurrit = currit
  if currit == "other": 
    return Haddock.Main.QueueSubmit_nopackage.QueueSubmit(otherqueuecommand, jobfilename, job_contents, run, 1, fileroot)

  if len(jobfiles) == 0:
    currjobfilename = jobfilename
    currqueuecommand = queuecommand
    psffile = "begin/"+ fileroot + ".psf"
    libfiles = [
                 psffile,
                 "protocols", 
                 "data/cryo-em",
                 "data/dani",
                 "data/dihedrals",
                 "data/distances",
                 "data/hbonds",
                 "data/pcs",
                 "data/rdcs",
                 "data/run.param",
                 "data/sequence/dna-rna_restraints.def",
                 "data/tensor",
                 "toppar",
                 "run.cns",
                 "run_newseed.cns",
                 "run_lowtad.cns"]
    libfiles += ["tools/check-error-messages.csh"]
    if currit == "it0":      
      prevfiles = open("begin/file.nam").readlines()
      libfiles += ["structures/it0/ambig.tbl", "structures/it0/unambig.tbl", "structures/it0/iteration.cns"]
    elif currit == "it1":
      prevfiles = open("structures/it0/file.nam").readlines()
      libfiles += ["structures/it1/ambig.tbl", "structures/it1/unambig.tbl", "structures/it1/iteration.cns"]
    elif currit == "water":
      libfiles += ["begin-aa", "structures/it1/ambig.tbl", "structures/it1/unambig.tbl", "structures/it1/water/iteration.cns"]

  jobfiles.append(job_contents)
  pending_jobs += 1
  jobnumber = jobfilename[jobfilename.rindex("_",0,-4)+1:-4]

  if currit == "water": jobnumber = jobnumber[:-1]  

  strucbase = run['fileroot'] + "_" + jobnumber
  prevstrucbase = strucbase + ".pdb"
  if currit == "water":
    failbase = strucbase + "w.fail"
    strucbase += "w.pdb"
  else:
    failbase = strucbase + ".fail"
    strucbase += ".pdb"
    
  #jobnumber = int(jobnumber)  

  if currit == "it0":  
    prevstruc = prevfiles[int(jobnumber)-1].strip()
    prevstrucw = prevstruc[:-4] + "_water.pdbw"
    seedname = strucbase[:-4] + ".seed"
    strucbasew = strucbase[:-4] + "_water.pdbw"
    newlibfiles = [      
                   "begin/%s" % prevstruc,
                   "begin/%s" % prevstrucw,
                   "structures/it0/ambig_%d.tbl" % int(jobnumber),
                  ]
    resultfiles.append((jobfilename[:-4]+".out.gz"))
  elif currit == "it1":    
    prevstruc = prevfiles[int(jobnumber)-1].strip()
    prevstrucw = prevstruc[:-4] + "_water.pdbw"
    seedname = strucbase[:-4] + ".seed" 
    strucbasew = strucbase[:-4] + "_water.pdbw"
    prevseedname = prevstruc[:-4] + ".seed" 
    newlibfiles = ["structures/it1/ambig_%d.tbl" % int(jobnumber), 
                   "structures/it1/%s" % failbase,
                   "structures/it0/%s" % prevstruc,
                   "structures/it0/%s" % prevstrucw,
                   "structures/it0/%s" % prevseedname,
                  ]
    resultfiles.append((jobfilename[:-4]+".out.gz"))
  elif currit == "water":    
    seedname = prevstrucbase[:-4] + ".seed" 
    prevstrucw = prevstrucbase[:-4] + "_water.pdbw"
    strucbasew = strucbase[:-5] + "_h2o-inter.pdb"
    newlibfiles = ["structures/it1/water/ambig_%d.tbl" % int(jobnumber), 
                   "structures/it1/water/%s" % failbase,
                   "structures/it1/%s" % prevstrucbase,
                   "structures/it1/%s" % prevstrucw,
                   "structures/it1/%s" % seedname,
                  ]
    resultfiles.append((jobfilename[:-4]+".out.gz"))  
  newlibfiles.append(jobfilename[:-4]+".inp")
  for f in newlibfiles: 
    if os.path.exists(f) and f not in libfiles: libfiles.append(f)
  if len(jobfiles) == jobmax or queuecommand != currqueuecommand:
    QueueFlush(force=True)
        
def QueueFlush(finished=False, force=False ):
  if lastcurrit == "other": 
    return Haddock.Main.QueueSubmit_nopackage.QueueFlush(finished=finished, force=force)

  global jobfiles, currjobfilename, currqueuecommand, pending_jobs, libfiles, prevfiles, resultfiles
  if finished:
    pending_jobs -= 1 
  if force == False and pending_jobs > len(jobfiles): return  
  if len(jobfiles) > 0:
    
    counter = 1
    while 1:
      packageroot = "package_%s_%d" % (lastcurrit, counter)
      package = "packages/" + packageroot + ".tar.gz"
      if not os.path.exists(package): break
      counter += 1    
    packagerunfiles = []
    for n in range(len(jobfiles)):  
      packagerunfile = packageroot+"_%d.csh" % (n+1)
      jf = open(packagerunfile, "w")
      jf.write(jobfiles[n]+"\n")
      jf.close()
      packagerunfiles.append(packagerunfile)      
    tarcommand = "tar cfz %s " % (package,) + " ".join(libfiles+packagerunfiles) + ">&/dev/null"
    os.popen(tarcommand).read()
    for f in packagerunfiles: 
      if os.path.exists(f): os.remove(f)
    
    extractpackagefile = packageroot + "-extract-results.csh"
    extractfailedstr = """
    tar xfz %s >&/dev/null
    """ % ("packages/" +  packageroot + "-result.tar.gz")
    rf = open(extractpackagefile, "w")
    rf.write(extractfailedstr)
    for outgz in resultfiles:
      extractstr = """
      rm -f %s 
      touch %s
      """ % (outgz[:-len(".gz")], outgz)
      rf.write(extractstr)
    rf.close()    
    libfiles = []
    prevfiles = []
    resultfiles = []   
    

    QueueThread(currqueuecommand, package)
    jobfiles = []
    currjobfilename = None
    currqueuecommand = None
