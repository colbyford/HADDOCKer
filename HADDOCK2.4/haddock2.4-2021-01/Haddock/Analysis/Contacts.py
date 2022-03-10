"""
Author: Niklas Blomberg, EMBL 1999
"""

__version__ = "$Revision: 2.1 $"

import glob, string, sys
import Numeric

from Aria.Analysis import ToMMa
from Aria.ThirdParty import Gnuplot, stats

def getResid(line):
    line=string.split(line)
    pos=line.index('resid')
    return int(line[pos+1])


def getContacts(fileobject):
    tblfile=fileobject.readlines()
    pairs=[]
    residuehash={}
    restraintCounter=0
    for index  in range(len(tblfile)):
        if string.find(tblfile[index],'ASSI') != -1 or string.find(tblfile[index],'OR') !=-1:
            if string.find(tblfile[index],'ASSI') !=-1 :
                restraintCounter=restraintCounter+1 #Count ASSI's
            newNoe=(getResid(tblfile[index+1]),getResid(tblfile[index+2]))
            if newNoe not in pairs:
                pairs.append(newNoe)
            
            
    return pairs,restraintCounter

def makeContactMatrix(pairlist):
    lastResidue=max(max(pairlist))
    contactMatrix= Numeric.zeros((lastResidue,lastResidue))
    for pair in pairlist:
        contactMatrix[pair[0]-1,pair[1]-1]=1
    return contactMatrix




class ariaIteration:
    """
    
    """
    def __init__(self,iteration):
        """
        __init__(self)
        Initialize a new instance.
        """

        self.iteration=iteration
        self.structures=[]
        self.getStructures()
        self.getContacts()
        
    def getStructures(self):
        """
        getStructures(self)
        """
        pdbfiles=glob.glob(self.iteration + '/*.pdb')
        for f in pdbfiles:
            fileobject=open(f)
            self.structures.append(ariaStructure(f,fileobject))
            fileobject.close()
        energy=[]
        rms=[]
        viol=[]
        for struc in self.structures:
            energy.append(struc.energies)
            rms.append(struc.rms)
            viol.append(struc.violations)
        self.energy=Numeric.array(energy)
        self.rms=Numeric.array(rms)
        self.viol=Numeric.array(viol)

        self.avgTotalEnergy=stats.mean(self.energy[:,0])
        self.sdvTotalEnergy=stats.stdev(self.energy[:,0])
        self.avgNoeEnergy=stats.mean(self.energy[:,-2])
        self.sdvNoeEnergy=stats.stdev(self.energy[:,-2])

        self.avgNoeRms=stats.mean(self.rms[:,-2])
        self.sdvNoeRms=stats.stdev(self.rms[:,-2])

        self.avgNoeViol=stats.mean(self.viol[:,0])
        self.sdvNoeViol=stats.stdev(self.viol[:,0])
        return
    
    def getContacts(self):
        """
        getContacts(self)
        """
        self.residueContacts={}
        self.pairlist=[]
        self.restraintCount=0
        f=open(self.iteration+'/ambig.tbl')
        self.pairlist,self.restraintCount=getContacts(f)
        f.close()
        f=open(self.iteration+'/unambig.tbl')
        pairs,count=getContacts(f)
        self.pairlist=self.pairlist+pairs
        self.restraintCount=self.restraintCount+count
        f.close()
        for i in self.pairlist:
            if self.pairlist.count(i)>1:
                self.pairlist.remove(i)
        for pair in self.pairlist:
            if pair[0]==pair[1]:
                continue
            for res in pair:
                if self.residueContacts.has_key(res):
                    self.residueContacts[res]=self.residueContacts[res]+1
                else:
                    self.residueContacts[res]=1
        
        self.contactMatrix=makeContactMatrix(self.pairlist)
        return



class ariaStructure:
    """
    
    """
    def __init__(self,name,fileobject):
        """
        __init__(self)
        Initialize a new instance.
        """
        self.name=name
        while 1:
            line=fileobject.readline()
            if string.find(line,'ATOM') != -1:
                break
            elif string.find(line,'energies') !=-1 :
                line=string.split(string.replace(line,',',' '))
                #catch missing energy terms
                self.energies=[]
                for energy in line[2:]:
                    try:
                        self.energies.append(float(energy))
                    except:
                        self.energies.append(0)
            elif string.find(line,'rms-dev')!=-1 :
                line=string.split(string.replace(line,',',' '))
                self.rms=map(float,line[2:])
            elif string.find(line,'violations')!=-1 :
                line=string.split(string.replace(line,',',' '))
                self.violations=map(float,line[2:])




                                   
                

def loopIterations(itList):
    """
    main()
    Module mainline (for standalone execution)
    """
    iterations=[]
    for it in itList:
        iter=ariaIteration(it)
        iterations.append(iter)
    return iterations

###########################################################################
# Now use Gnuplot to plot some interesting analysis + make a summary file
# - in iteration SummaryFile,contact plot
# in structures directory
# variation in energy,contacts,rms,viol
###########################################################################

class analyseIteration:

    def __init__(self,c):
        self.component=c
        #Make a summary file for each it
        summaryFile=open (self.component.iteration+'/Summary.tbl','w')
        summaryFile.write('Restraints  %i\n'%self.component.restraintCount)
        summaryFile.write('Pairs       %i\n'%len(self.component.pairlist))
        summaryFile.write('Avg Etot    %f ( %f )\n'% (self.component.avgTotalEnergy,self.component.sdvTotalEnergy))
        summaryFile.write('Avg Enoe    %f ( %f )\n'% (self.component.avgNoeEnergy,self.component.sdvNoeEnergy))
        summaryFile.write('Avg RMSnoe  %f ( %f )\n'% (self.component.avgNoeRms,self.component.sdvNoeRms))
        summaryFile.write('Avg Viol    %f ( %f )\n'% (self.component.avgNoeViol,self.component.sdvNoeViol))
        summaryFile.close()
        #Write out pairlist and contact matrix
        pairFile=open(self.component.iteration+'/pairlist.tbl','w')
        for pair in self.component.pairlist:
            pairFile.write('%i %i\n'% pair)
        pairFile.close()
        contactFile=open(self.component.iteration+'/contactmatrix.mma','w')
        contactFile.write(ToMMa.ToMMa(self.component.contactMatrix))
        contactFile.close()
        resPerResidue=open(self.component.iteration+'/restr_residue.tbl','w')
        average=stats.mean(self.residueContacts.values())
        resPerResidue.write('# Average: %f (unassigned not included) \n'% average)
        for k,v in self.residueContacts.items():
            resPerResidue.write('%i %i\n'%(k,v))
        resPerResidue.close()
        #Dump a Gnuplot hardcopy of contactplot
        g1=Gnuplot.Gnuplot()
        g1('set size square')
        g1.plot(self.component.pairlist)
        g1.hardcopy(self.component.iteration+'/contacts.ps')
        del g1
        g1=Gnuplot.Gnuplot()
        g1('set data style boxes')
        g1.plot(self.residueContacts.items())
        g1.hardcopy(self.component.iteration+'/res_residue.ps')
        del g1
    def __getattr__(self,name):
        return getattr(self.component,name)

class analyseAriaRun:
    
    """
    Analyse a structurecalc using aria
    """
    def __init__(self,iterationlist,currdir):
        """

        """
        self.directory=currdir
        self.iterations=loopIterations( map(lambda x,c=self.directory:c+'/'+x,iterationlist))
        self.directory=currdir
        #Get the data from iterations
        EtotList=[]
        EnoeList=[]
        RMSnoeList=[]
        ViolList=[]
        RestrainList=[]
        PairList=[]
        i=0
        for it in self.iterations:
            analyseIteration(it)
            EtotList.append((i,it.avgTotalEnergy,it.sdvTotalEnergy))
            EnoeList.append((i,it.avgNoeEnergy,it.sdvNoeEnergy))
            RMSnoeList.append((i,it.avgNoeRms,it.sdvNoeRms))
            ViolList.append((i,it.avgNoeViol,it.sdvNoeViol))
            RestrainList.append(i,it.restraintCount)
            PairList.append((i,len(it.pairlist)))
            i=i+1
        #Plot data
        xrange='set xrange [-1:'+str(i)+']'
        #Total Energy
        plot=Gnuplot.Gnuplot()
        plot('set data style errorbars')
        plot('set title "Total Energy"')
        plot(xrange)
        plot.plot(EtotList)
        plot.hardcopy(self.directory+'/Etot.ps')
        del plot
        #NoeEnergy
        plot=Gnuplot.Gnuplot()
        plot('set data style errorbars')
        plot('set title "Noe Energy"')
        plot(xrange)
        plot.plot(EnoeList)
        plot.hardcopy(self.directory+'/Enoe.ps')
        del plot
        #RMS
        plot=Gnuplot.Gnuplot()
        plot('set data style errorbars')
        plot('set title "RMS viol"')
        plot(xrange)
        plot.plot(RMSnoeList)
        plot.hardcopy(self.directory+'/rms.ps')
        del plot
        #Viol
        plot=Gnuplot.Gnuplot()
        plot('set data style errorbars')
        plot('set title "Number of viol"')
        plot(xrange)
        plot.plot(ViolList)
        plot.hardcopy(self.directory+'/viol.ps')
        del plot
        #Restraints
        plot=Gnuplot.Gnuplot()
        plot('set title "Number of restraints"')
        plot(xrange)
        plot.plot(RestrainList)
        plot.hardcopy(self.directory+'/assi.ps')
        del plot
        #Pairs
        plot=Gnuplot.Gnuplot()
        plot('set title "Number of pairs"')
        plot(xrange)
        plot.plot(PairList)
        plot.hardcopy(self.directory+'/pair.ps')
        del plot
        return


    
if __name__ == "__main__":
    import os, sys
    try:
        sys.argv[1],os.getcwd()
        analyseAriaRun(sys.argv[1:],os.getcwd())
    except IndexError:
        print 'Usage: ariaAnalysis it0 it1 ...'
        print 'Empty iterations won\'t work'
        sys.exit(1)
    
