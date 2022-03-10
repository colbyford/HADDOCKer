from Haddock.Main import ParsePath
import random

class HaddockError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "\n\t" + self.value

class RunCNSError(HaddockError):
  pass    
    
import os, sys, time

rundir = ""
fixlog_file = ""
read_fixlog = False
fixlog = {}
fixmessages = { 'FixTAD': "Adjusting TAD factor", 'Copy': "Copying structure...", 'FixSEED': "Changing random seed", 'Resubmit': "Resubmitting structure...", 'FixFAIL': "Performing only EM ..."}

def Fix_OpenLog():
  global read_fixlog,  fixlog_file
  if read_fixlog == False:
    read_fixlog = True
    fixlog_file = rundir + '/' + 'haddock.log'
    if os.path.exists(fixlog_file):
      f = open(fixlog_file)
      for l in f.readlines():
        ll = l.split()
        if len(ll) < 5: continue
        if ll[2] != 'structure': continue
        if ll[3][-1] != ':': continue
        key = "it" + ll[1]+'_' + ll[3][:-1]
        if key not in fixlog: fixlog[key] = []
        fixlog[key].append(l[l.index(':')+1:].strip())
      f.close()

def Fix_AddLog(run, nr, currit, value):
    Fix_OpenLog()
    key = "it" + str(currit) + '_' + str(nr)
    if key not in fixlog: fixlog[key] = []
    fixlog[key].append(value)
    logentry = "Iteration " + str(currit) + " structure " + str(nr) + ": " + value + '\n'
    open(fixlog_file, "a").write(logentry)

def Fix_AdjustSEED(run, nr, currit, jobroot):
    seed = int(run["iniseed"])
    #newseed = int(float(seed)/2 + 17)
    newseed = random.randint(1,100000)
    fileroot = run['fileroot']
    print "FIX: Modifying random seed for it %s structure %d" % (currit, nr)
    if not os.path.exists(rundir + '/run_newseed.cns'):
      lines = open(rundir + '/run.cns').readlines()
      f = open(rundir + '/run_newseed.cns', 'w')
      for l in lines:
          if l.find('{===>} iniseed=') > -1:
              l = '{===>} iniseed=%d;\n' % newseed
          f.write(l)
      f.close()
    if not os.path.exists(jobroot + '.inp'):
        raise HaddockError("input file not found")
    buf = open(jobroot + '.inp').read()
    if not os.path.exists(jobroot + '_backup.inp'):
        open(jobroot + '_backup.inp', 'w').write(buf)
    buf = buf.replace('@RUN:run.cns(', '@RUN:run_newseed.cns(')
    #print "OK?"
    open(jobroot + '.inp', 'w').write(buf)
    if currit == '2': 
        jobroot   = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out'
        jobrootgz = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out.gz'
    else:
        jobroot   = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
          + str(currit) + '_refine_' + str(nr) + '.out'
        jobrootgz = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
          + str(currit) + '_refine_' + str(nr) + '.out.gz'
    if os.path.exists(jobroot):
        os.remove(jobroot)
    if os.path.exists(jobrootgz):
        os.remove(jobrootgz)
    Fix_AddLog(run, nr, currit, fixmessages['FixSEED'])

def Fix_AdjustTADFactor(run, nr, currit, jobroot):
    tadfactor = int(run["tadfactor"])
    newtadfactor = int(float(tadfactor)/2 + 0.99999)
    fileroot = run['fileroot']
    print "FIX: Adjusting TAD factor for it %s structure %d" % (currit, nr)
    if not os.path.exists(rundir + '/run_lowtad.cns'):
      lines = open(rundir + '/run.cns').readlines()
      f = open(rundir + '/run_lowtad.cns', 'w')
      for l in lines:
          if l.find('{===>} tadfactor=') > -1:
              l = '{===>} tadfactor=%d;\n' % newtadfactor
          f.write(l)
      f.close()
    if not os.path.exists(jobroot + '.inp'):
        raise HaddockError("input file not found")
    buf = open(jobroot + '.inp').read()
    if not os.path.exists(jobroot + '_backup.inp'):
        open(jobroot + '_backup.inp', 'w').write(buf)
    buf = buf.replace('@RUN:run.cns(', '@RUN:run_lowtad.cns(')
    open(jobroot + '.inp', 'w').write(buf)
    if currit == '2': 
        jobroot   = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out'
        jobrootgz = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out.gz'
    else:
        jobroot   = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
          + str(currit) + '_refine_' + str(nr) + '.out'
        jobrootgz = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
          + str(currit) + '_refine_' + str(nr) + '.out.gz'
    if os.path.exists(jobroot):
        os.remove(jobroot)
    if os.path.exists(jobrootgz):
        os.remove(jobrootgz)
    Fix_AddLog(run, nr, currit, fixmessages['FixTAD'])

def Fix(run, nr, currit, jobroot):
  #tries to fix a crashed structure, must return True (fix attempted) or False (no fix known)
  #jobroot is like /home/sjoerd/1AVX/run1/1AVX_run1_1w or [...]/1AVX_run1_refine_it1
  currit = str(currit)
  key = "it" + str(currit) + '_' + str(nr)
  if currit == '0': 
      if key not in fixlog or fixmessages['FixSEED'] not in fixlog[key]:
          return Fix_AdjustSEED(run, nr, currit, jobroot)
      return False
  else:
      if key not in fixlog or fixmessages['FixFAIL'] not in fixlog[key]:
          return MiniStructure(nr, currit, run)
      return False


timekeep = {}      
maxtimeout = 5 * 60

def CheckTimeOut(run, nr, currit, jobroot):
  global timekeep
  #returns True if structure has timed out 
    #i.e. nonzero size of outfile and no modification of outfile in last 10 minutes
    # (to make sure that the outfile is modified, a KeepAlive script has been added to the jobfile)
  outfile = jobroot + ".out"
  if not os.path.exists(outfile): return False
  try:
    if os.path.getsize(outfile) == 0: return False
    if (nr, currit) not in timekeep:
      timekeep[(nr,currit)] = (os.path.getmtime(outfile), time.time())
    mtime0 = timekeep[(nr,currit)][0]
    if os.path.getmtime(outfile) == mtime0:
      ptime = timekeep[(nr,currit)][1]
      if time.time() - ptime > maxtimeout:
        if os.path.exists(outfile):
          os.remove(outfile)
          print "Timeout - deleting: ",outfile
        return True
    else: timekeep[(nr,currit)] = (os.path.getmtime(outfile), time.time())
    return False
  except OSError:
    return False

def CheckForLateArrival(run, nr, currit):
  global timekeep
  currtime = time.time()
  rundir = run['run_dir']
  currit = str(currit)
  fileroot = run['fileroot']
  w = ''
  curritstr = currit
  if currit == '2': 
    w = 'w'
    curritstr = '1/water'

  root = run['run_dir'] + '/structures/it' + curritstr + '/' + fileroot + '_' + str(nr)      
  if currit == '2':
    jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out.gz'
  else:
    jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
      + str(currit) + '_refine_' + str(nr) + '.out.gz'

  if os.path.exists(root + w + '.pdb'):
    del timekeep[(nr,str(currit))]
    return 'finished'
  elif os.path.exists(jobroot):
    del timekeep[(nr,str(currit))]
    return 'crashed'
  elif currtime - timekeep[(nr,str(currit))][0] > maxtimeout: 
    del timekeep[(nr,str(currit))]
    return 'crashed'
  else: return 'pending'
    
def MiniStructure(nr, currit, run):  
  #Instructs refine.inp to copy the structure to the next iteration.
  #Use this function only for it1 or water structures!  
  currit = str(currit)
  fileroot = run['fileroot']
  w = ''
  curritstr = currit
  if currit == '2': 
    w = 'w'
    curritstr = '1/water'
  root = run['run_dir'] + '/structures/it' + curritstr + '/' + fileroot + '_' + str(nr)
  failfile = root + w + ".fail"
  f = open(failfile, "w")
  f.close()
  if currit == '2': 
    jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_' + str(nr) + 'w.out.gz'
  else:
    jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
      + str(currit) + '_refine_' + str(nr) + '.out.gz'
  if os.path.exists(jobroot):
#    print "Deleting ",jobroot
    os.remove(jobroot)
  Fix_AddLog(run, nr, currit, fixmessages['FixFAIL'])
    
def RestartStructure(nr, currit, run):  
  currit = str(currit)
  fileroot = run['fileroot']
  jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_'\
      + str(currit) + '_refine_' + str(nr) + '.out'
  if os.path.exists(jobroot):
    print "Deleting: ",jobroot
    os.remove(jobroot)
  
def GetDiagnose(nr, currit, run, status):
  global rundir, timekeep
  rundir = run['run_dir']
  currit = str(currit)
  fileroot = run['fileroot']
  w = ''
  curritstr = currit
  if currit == '2': 
    w = 'w'
    curritstr = '1/water'
  root = run['run_dir'] + '/structures/it' + curritstr + '/' + fileroot + '_' + str(nr)
  if os.path.exists(root + w + '.pdb'):
    ret = 'finished'
  else:
    if currit == '2': 
      jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_'\
      + str(nr) + 'w'
    else: 
      jobroot = run['temptrash_dir'] + '/' + fileroot + '_' + ParsePath.GetTail(run['run_dir']) + '_it'\
      + str(currit) + '_refine_' + str(nr)
    if os.path.exists(jobroot + '.out'):
      ret = 'running'
    elif os.path.exists(jobroot + '.out.gz'):
      ret = 'crashed'
      timekeep[(nr,currit)] = (time.time(),time.time())
    else:
      ret = 'waiting'
  #if ret == 'running' or ret == 'crashed': print 'it' + str(currit), 'structure ' + str(nr) + ':' , ret      
  return ret

def DiagnoseStructures(run, status):
  
  iterations = {} #dictionary for quickchecking the existence of file.list
  for currit in (0,1):
    iterations['pdb_'+str(currit)+'_'] = (currit, str(currit))
  iterations['wpdb_'] = (2, '2')
  
  rotate_1 = run['rotate180_it1']
  for i in iterations.keys():
    key = iterations[i][0]
    nrstruc = int(run['structures'][key])
    if iterations[i][0] > 1 and nrstruc < int(run["structures"][1]):
      nrstruc = int(run["structures"][1])
    if iterations[i][0] > 1 and rotate_1 == 'true': 
      nrstruc *= 2
    if status['filelist' + iterations[i][1]] == 1: #file.list exists... 
      for n in range(1,nrstruc+1):
        status[i+str(n)] = 'finished'
      continue
    
    currit = iterations[i][1]
    for n in range(1,nrstruc+1):      
      status[i+str(n)] = GetDiagnose(n, currit, run, status)
