import os

tasks_per_node = 4

"""
SLURM job manager, Sjoerd de Vries March 2008

Efficiently allocates jobs on a SLURM system
(low number of simultaneous queue jobs, multiple processors per queue job)

Usage:

In run.cns:
- Set cpunumber to infinity
- Put the number of nodes that you want in queue_1 in run.cns, 
  then : and then the queuecommand
I.e. if a node is four processors and you need 32 processors, and the queuecommand is "mnsubmit":
{===>} queue_1="8: mnsubmit";
{===>} cns_exe_1="/home/sjoerd/cns";
{===>} cpunumber_1=999999;

Then, submit HADDOCK to the queue, allocating one processor for it.
  This processor will also be assigned jobs
The queuecommand will be executed without trailing & !!!
"""

nr_nodes = 0
jobfilenames = []
currqueuecommand = None
maxjobfiles = {'it0':1000, 'other':1000, 'it1':200, 'water':200}

pending_jobs = 0

def QueueSubmit(queuecommand, jobfilename, job_contents, run, jobmax, fileroot):
  global jobfilenames, currqueuecommand, nr_nodes, pending_jobs
  
  currit = "other"
  if jobfilename.endswith("w.job"): currit = "water"
  elif jobfilename.rfind("_") > -1:
    j = jobfilename[:jobfilename.rindex("_")]
    if j.endswith("_it0_refine"): currit = "it0"
    elif j.endswith("_it1_refine"): currit = "it1"  
  
  queuemax = 1
  for k in run['cpunumber'].keys():
    if run['queue'][k] == queuecommand:
      queuemax = int(run['cpunumber'][k])
  pos = queuecommand.find(":")
  nr_nodes = int(queuecommand[:pos])
  currqueuecommand0 = queuecommand[pos+1:]
  jf = open(jobfilename, "w")
  jf.write(job_contents)
  jf.close()  
  jobfilenames.append(jobfilename)
  pending_jobs += 1
  try:
    os.remove(jobfilename+"_RUNNING") 
  except:
    pass
  flush = False
  if len(jobfilenames) == queuemax: 
    #should not happen, but...
    flush = True
  if currqueuecommand != None and currqueuecommand0 != currqueuecommand: flush = True
  if len(jobfilenames) == maxjobfiles[currit]: flush = True
  
  if flush: 
    currqueuecommand = currqueuecommand0
    QueueFlush(force=True)
  currqueuecommand = currqueuecommand0
        
def QueueFlush(finished=False, force=False):
  global jobfilenames, currqueuecommand, nr_nodes, pending_jobs
  if finished:
    pending_jobs -= 1 
  if force == False and pending_jobs > len(jobfilenames): return
  if len(jobfilenames) > 0:
    
    currit = "other"
    if jobfilenames[0].endswith("w.job"): currit = "water"
    elif jobfilenames[0].rfind("_") > -1:
      j = jobfilenames[0][:jobfilenames[0].rindex("_")]
      if j.endswith("_it0_refine"): currit = "it0"
      elif j.endswith("_it1_refine"): currit = "it1"  
    
    
    
    jobnr = 1
    while 1:
      slurmscriptname = "slurmjob%d.csh" % jobnr
      masterscriptname = "masterjob%d.csh" % jobnr
      if not os.path.exists(slurmscriptname): break
      jobnr += 1
    
    slurmscript =  "#!/bin/csh\n"    
    slurmscript += "# @ wall_clock_limit = 1:30:00\n"
    
    slurmscript += "# @ total_tasks = %d\n" % (nr_nodes * tasks_per_node)
    slurmscript += "# @ tasks_per_node = %d\n" % (tasks_per_node)
    
    for i in range(nr_nodes):      
      for ii in range(tasks_per_node):
        slurmscript += "set f = {$SLURM_JOBID}_%d\n" % (i*tasks_per_node+ii+1)
        srun = "srun --ntasks=1 --nodes=1-1 --relative=%d csh %s_%d $f &\n" % (i, masterscriptname, i*tasks_per_node+ii+1)
        slurmscript += srun
    slurmscript += "while (1)\n"
    slurmscript += "  sleep 10\n"
    for i in range(nr_nodes):      
      for ii in range(tasks_per_node):
        slurmscript += "  if (!(-e {$SLURM_JOBID}_%d)) continue\n" % (i*tasks_per_node+ii+1)
    slurmscript += "  break\n"
    slurmscript += "end\n"
    for i in range(nr_nodes):      
      for ii in range(tasks_per_node):
        slurmscript += "rm -f {$SLURM_JOBID}_%d\n" % (i*tasks_per_node+ii+1)
     
    
    masterscript = ""
    for f in jobfilenames:
      masterscript += "if (!(-e %s_RUNNING) && !(-e %s.out.gz)) then\n" % (f, f[:-4])
      masterscript += "  touch %s_RUNNING\n" % f
      masterscript += "  csh %s\n" % f
      masterscript += "  rm -f %s_RUNNING\n" % f
      masterscript += "endif\n"
    masterscript += "touch $1\n"
    open(masterscriptname, "w").write(masterscript)
    cmd = "csh %s &" % masterscriptname
    print '      queue command:\n     ', cmd
    os.system(cmd)
    if currit != "other" and nr_nodes > 0:
      for i in range(nr_nodes):
        for ii in range(tasks_per_node):
          nr = i*tasks_per_node+ii+1
          shift = int(float(len(jobfilenames)) / (nr_nodes*tasks_per_node) * nr)
          masterscript = ""
          for fnr in range(len(jobfilenames)):
            ffnr = (fnr + shift) % len(jobfilenames) 
            f = jobfilenames[ffnr]
            masterscript += "if (!(-e %s_RUNNING) && !(-e %s.out.gz)) then\n" % (f, f[:-4])
            masterscript += "  touch %s_RUNNING\n" % f
            masterscript += "  csh %s\n" % f
            masterscript += "  rm -f %s_RUNNING\n" % f
            masterscript += "endif\n"
          masterscript += "touch $1\n"
          open(masterscriptname+"_"+str(nr), "w").write(masterscript)

      open(slurmscriptname, "w").write(slurmscript)
      cmd = currqueuecommand + " " + slurmscriptname
      print '      queue command:\n     ', cmd
      os.system(cmd)
    pending_jobs += len(jobfilenames)
    jobfilenames = []
    nr_nodes = 0
    currqueuecommand = None
        
