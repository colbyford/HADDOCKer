import os, sys, time
import Haddock.Main.QueueSubmit_default
from Haddock.Main.QueueThread import QueueThread

currjobfilename = None
currqueuecommand = None
jobcounter = 0
jobstring = ""
#jobmax = {} 
#jobmax["it0"] = 10
#jobmax["it1"] = 1
#jobmax["water"]= 1
#jobmax["other"]= 1
pending_jobs = 0

def QueueSubmit(queuecommand, jobfilename, job_contents, run, jobmax, fileroot):
  queuemax = 1
  for k in run['cpunumber'].keys():
    if run['queue'][k] == queuecommand:
      queuemax = int(run['cpunumber'][k])
  
  global jobcounter, jobstring, currjobfilename, currqueuecommand, pending_jobs
  currit = "other"
  if jobfilename.endswith("w.job"): currit = "water"
  elif jobfilename.rfind("_") > -1:
    j = jobfilename[:jobfilename.rindex("_")]
    if j.endswith("_it0_refine"): currit = "it0"
    elif j.endswith("_it1_refine"): currit = "it1"
  if currit == "other":
    return Haddock.Main.QueueSubmit_default.QueueSubmit(queuecommand, jobfilename, job_contents, run, 1, fileroot)
  if jobcounter == 0:
    currjobfilename = jobfilename
    currqueuecommand = queuecommand
    jobstring = ""
  jobstring += job_contents + '\n'
  jobcounter += 1
  pending_jobs += 1
  if jobcounter == jobmax or queuecommand != currqueuecommand:
    QueueFlush(force=True)

        
def QueueFlush(finished=False, force=False):
  global jobcounter, jobstring, currjobfilename, currqueuecommand, pending_jobs
  if finished:
    pending_jobs -= 1 
  if force == False and pending_jobs > jobcounter: return  
  if jobcounter > 0:
    stringlist = []; echolist = []
    for line in jobstring.split("\n"):
        if line.startswith('#'):
            pass
        elif line.startswith('echo'):
            echolist.append(line) 
        elif 'KeepAlive' in line:
            echolist.append(line) 
        else:
            stringlist.append(line)
    jobstring = "#!/bin/csh\n"
    jobstring += '\n'.join(sorted(echolist))
    jobstring += '\n\n'
    jobstring += '\n'.join(stringlist)
    jf = open(currjobfilename, "w")
    jf.write(jobstring)
    jf.close()
    cmd='chmod +x ' + currjobfilename
    os.system(cmd)
#    time.sleep(2) 
    QueueThread(currqueuecommand, currjobfilename)
    jobcounter = 0
    jobstring = ""
    currjobfilename = None
    currqueuecommand = None
        
