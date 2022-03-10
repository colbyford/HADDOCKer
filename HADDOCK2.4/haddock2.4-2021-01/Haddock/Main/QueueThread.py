import sys,subprocess, time
from threading import Thread
from Haddock.Analysis.Diagnostic import HaddockError

def runqueuecommand(queuecommand, jobfilename):
  cmd = queuecommand + " " + jobfilename + " || echo QUEUE_DOWN"
  failures = 0
  print '      queue command:\n     ', queuecommand + " " + jobfilename
  while 1:
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    result = process.stdout.read()
    err = process.stderr.read()
    print result, err
    ok = True
    if len(result) and result.splitlines()[-1].find("QUEUE_DOWN") > -1:
      if failures == 8: raise HaddockError("Your queue command is not working")
      wait = 2**(failures) * 15
      print "Queue command failed, retrying in %d seconds" % (wait)
      sys.stdout.flush()
      time.sleep(wait)
      failures += 1
    else: break
  

def QueueThread(queuecommand, jobfilename):
  thread = Thread(target=runqueuecommand, args = (queuecommand, jobfilename))
  thread.setDaemon(True)
  thread.start()
