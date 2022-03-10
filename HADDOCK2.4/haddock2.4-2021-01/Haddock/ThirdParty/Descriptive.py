class Descriptive:
    def __init__(self, dataSet=[]):
	self.myData = []
	self.count = 0
	self.mean = 0.0
	self.pseudoVariance = 0.0
	self.frequency = None
	self.max = self.min = self.median =  None

	if( len(dataSet) != 0): self.addData(dataSet)

    def addData(self, data):
	oldmean = 0.0
	try:
	    self.myData = self.myData + data
	except TypeError:
	    data = [data]
	    self.myData = self.myData + data

	for d in data:
	    oldmean = self.mean
	    self.count = self.count + 1
	    self.mean = self.mean + ((d - oldmean)/self.count)
	    self.pseudoVariance = self.pseudoVariance + (
		(d - oldmean) * (d - self.mean))

	self.max = self.min = self.median =  None

    def getCount(self):
	if( len(self.myData) == 0): return None
	return self.count

    def getMean(self):
	if( len(self.myData) == 0): return None
	return self.mean

    def getSum(self):
	if( len(self.myData) == 0): return None
	sum = 0
	for x in self.myData:
	    sum = sum + x

	return sum

    def getVariance(self):
	if( len(self.myData) == 0): return None
	if( (self.count - 1) > 0 ):
	    return ( self.pseudoVariance/ (self.count - 1))
	else:
	    return None

    def getStdDev(self):
	if( len(self.myData) == 0): return None
	from math import *
	if( (self.count - 1) > 0 ):
	    return sqrt( self.pseudoVariance/ (self.count - 1))
	else:
	    return None

    def getData(self):
	return self.myData

    def getMax(self):
	if( len(self.myData) == 0): return None
	if( self.max == None):
	    self.max = self.myData[0]
	    for x in range(1,len(self.myData)):
		if( self.myData[x] > self.max ): self.max = self.myData[x]
		
	return self.max


    def getMin(self):
	if( len(self.myData) == 0): return None
	if( self.min == None):
	    self.min = self.myData[0]
	    for x in range(1,len(self.myData)):
		if( self.myData[x] <= self.min ): self.min = self.myData[x]
		
	return self.min

    def getSampleRange(self):
	return (self.getMax() - self.getMin())

    def getMedian(self):
	if( len(self.myData) == 0): return None
	if( self.median == None ):
	    from Numeric import *
	    sort(self.myData)
	    if( self.count%2 == 1):
		self.median = self.myData[(self.count-1)/2] 
	    else:
		self.median = (self.myData[(self.count-2)/2] + 
			       self.myData[(self.count)/2]     )/2

	return self.median


    def leastSquaresFit(self, args=None):
	if( len(self.myData)==0 or self.count<2 ): return None
	if( args == None): 
	    xlist = range(self.count)
	else:
	    xlist = args
	    if( len(x) != self.count ):
		print 'Descriptive:  Range and domain are of unequal length'
		return None
	
	sigmaxy, sigmax, sigmaxx = 0,0,0
	sigmay = self.getSum()
	iter = 0
	for x  in xlist:
	    sigmaxy = sigmaxy + x * self.myData[iter];
	    sigmax  = sigmax  + x
	    sigmaxx = sigmaxx + x*x
	    iter = iter + 1
	    
	coefficients = [0,0]
	coefficients[1] = ( (self.count*sigmaxy - sigmax*sigmay)/
			    (self.count*sigmaxx - sigmax*sigmax) )
	coefficients[0] = ( (sigmay - coefficients[1]*sigmax)/self.count )

	return coefficients

    def getFrequencyDistribution(self, numPartitions):
	if( len(self.myData)==0 or self.count<2 ): return None
	if( self.frequency == None ):
	    numIntervals = numPartitions
	    interval = 1.0 * self.getSampleRange() 
	    interval = interval / numIntervals
	    iter = 1.0 *self.getMin() + interval
	    bins = {}
	    
	    while( iter < self.getMax() ):
		bins[iter] = 0
		iter = iter + interval	
	

	    bins[self.getMax()] = 0
	    
	    from Numeric import sort
	    for el in sort(self.myData):
		for kk in sort(bins.keys()):
		    if( el <= kk ):
			bins[kk] = bins[kk] + 1
			break
	    self.frequency = bins
	
	return self.frequency

    def __repr__(self):
        return "mean=%8.3g (%8.3g) [min,max]=[%8.3g,%8.3g]" %(self.getMean(),self.getStdDev(),
                                                              self.getMin(),self.getMax())
