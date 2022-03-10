import os
from Haddock.Main.QueueThread import QueueThread

def QueueSubmit(queuecommand, jobfilename, job_contents, run, jobmax, fileroot):
  jf = open(jobfilename, "w")
  jf.write(job_contents)
  jf.close()
  cmd='chmod +x ' +jobfilename
  os.system(cmd)
  QueueThread(queuecommand, jobfilename)
  
def QueueFlush(finished=False, force=False):
  pass

