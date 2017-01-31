#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 17:16:45 2016

@author: askahlon

"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 17:16:45 2016

@author: askahlon

"""

import datetime


def convertTime(time): # takes a string of time as input and converts it into a time obj
    dateObj = datetime.datetime.strptime(time, '%j.%H:%M:%S') #%j represents zero padded day of year
    return dateObj 

def uniqueList(slewTimes): # takes an array as input and remove the duplicates without affecting the worder
	slewTimes = slewTimes	
	emptyList = []
	for time in slewTimes:
		if time not in emptyList:
			emptyList.append(time)
	return emptyList

	
def findErrors(logFilePath):   # reads the log files return the stow times and the day of the year
	########## Lets declare some index locations specific to the log file###########
	dayStart = 5
	dayEnd = 8
	timestart = 5    # index of the string where time starts (from 0) 5 if including day
	timeend = 16
	stowTimes = []   #array to store stow engage and release times
	slewTimes = []
	stowed = False   # antenna is not stowed by default
	try:
		logfile= open(logFilePath,'r') # Read the log file
	except IOError:
		print "Cannot open "+ logFilePath
	for counter,line in enumerate(logfile):    # for each line
	    	if counter<1:
			doy = int(line[dayStart:dayEnd]) # note down the day of the year
	    	if line[35:45] == '7mautostow': #look for mention of 7mautostow
			stowTimes.append(line[timestart:timeend +1])  #if you find it, save the time
			stowed = True
	    	if line[-19:-1] == 'Auto-stow released':  # also check for stow release
			stowTimes.append(line[timestart:timeend +1])  # save that time too 
			stowed = False
		if line[30:37] == 'SLEWING': #look for mention of slewing errors
			slewTimes.append(line[timestart:timeend +1])  #if you find it, save the time
	if stowed == True:
		stowTimes.append(line[timestart:timeend +1])
	endTime = line[timestart:timeend +1]
	logfile.close() # close I/O stream to free up resources
	return stowTimes, slewTimes, doy #output the array of times and the day of the year

def findScansAffected (sumFilePath,stowTimes,doyRange,telescopeSlew):
	dataStart = 19 # line number in the sum file where scan data starts
	scanStartIndexStart = 39
	scanStartIndexEnd =47
	scanEndIndexStart = 49
	scanEndIndexEnd =57
	slewTime = telescopeSlew  # time it takes the telescope to move in seconds
	scansAffected = []
	prevScanEnd = None
	try:
		sumFile = open(sumFilePath,'r')
	except IOError:
		print "Cannot open " + sumFilePath
	for count, line in enumerate(sumFile):
		if count >dataStart-1:
			if line[1:4] in doyRange : #check if line starts with doy
				scanName = line[1:9]
				scanDoy = line[1:4]
				scanStart = line[1:4]+'.'+line[scanStartIndexStart:scanStartIndexEnd]
				scanEnd = line[1:4]+'.'+line[scanEndIndexStart:scanEndIndexEnd]
				scanStart = convertTime(scanStart) - datetime.timedelta(0,slewTime)
				scanEnd = convertTime(scanEnd) + datetime.timedelta(0,slewTime)
		   		for time in stowTimes:
		        		formattedTime = convertTime(time) # convert stow time to a datetime obj
					if scanDoy == formattedTime.strftime('%j'):
			   			if formattedTime.time() >= scanStart.time() and formattedTime.time() <= scanEnd.time():
				   			scansAffected.append(line[1:9]) #store the scan name
						if prevScanEnd != None:
							if formattedTime.time() >= prevScanEnd.time() and formattedTime.time() <= scanStart.time():
								scansAffected.append(line[1:9]) #store the scan name
							
				prevScanEnd = scanEnd
	if len(scansAffected)<len(stowTimes): #if the sizes do not match
		scansAffected.append(scanName) # save the last scan name
	
	sumFile.close()
	return scansAffected

def writeSavedData (stowTimes,slewTimes,scansAffectedStow,scansAffectedSlew,experiment, station,printSlew,printSlewScan):
	stowTimes = stowTimes
	slewTimes = slewTimes	
	scansAffectedStow = scansAffectedStow
	scansAffectedSlew = scansAffectedSlew
	experiment = experiment
	station = station
	printSlew=printSlew
	printSlewScan=printSlewScan
	count=0
	count2=0
	print '\n'
	print '\n'
	print 'The windstow times for ' + experiment + station + ' are:\n'
	if len(stowTimes) == 0:
		print 'There were no windstows.\n'	
	else:
		while int(count/2) < int((len(stowTimes)/2)):    
		    print stowTimes[count] + ' to ' + stowTimes[count+1]+'\n' #writes the times in a x to y format
		    count = count +2  
	print '  \n'
	print 'The Scans affected are:\n'
	if len(scansAffectedStow)==0:
		print 'There were no scans affected by windstows.\n'
	else:
		while int(count2/2) < int((len(scansAffectedStow)/2)):    
		    print scansAffectedStow[count2] + ' to ' + scansAffectedStow[count2+1]+'\n' 
		    count2 = count2 +2   
	print '  \n'
	print '  \n'
	if printSlew.lower() == "yes" or printSlew.lower() == "y":
		print 'Onsource status is Slewing Errors:\n'
		if len(scansAffectedSlew) == 0:
			 StowTimes.write('There were no Slewing errors.\n')	
		else:
			for count3, times in enumerate(slewTimes):
				print  slewTimes[count3] +'\n' 
			print'  \n'
			if printSlewScan.lower() == "yes" or printSlewScan.lower() == "y":
				print 'The scans affected by slewing errors:\n'
				for count4, scans in enumerate(scansAffectedSlew):
					print scansAffectedSlew[count4] +'\n' 
	
def fetchlog(station, experiment):
    import os
    print('Retrieving %s%s.log from pcfs%s' %(experiment,station,station))
    os.system('scp oper@pcfs%s:/usr2/log/%s%s.log /vlbobs/ivs/logs/' %(station,experiment,station))

def main(): # calls all the other functions.
	experiment = raw_input("Please enter the experiment name.\n")
	station = raw_input("Please specify a station [hb|ke|yg].\n")
        newlog = raw_input("Would you like to fetch a new log?[y,N] (warning: overwrites log file on ops2)") or 'no'
	printSlew = raw_input("Would you like to list the Slewing errors? (Could be many) [YES|no].\n") or 'yes'
	printSlewScan = raw_input("Would you like to list the scans associated with Slewing errors? (Could be many) [YES|no].\n") or 'yes'
	logFilePath = '/vlbobs/ivs/logs/'+ experiment + station + '.log'  
	sumFilePath = '/vlbobs/ivs/sched/'+ experiment + station +'.sum'
	
        if newlog.lower() == 'y' or newlog.lower() == 'yes':
            fetchlog(station, experiment)
        
        telescopeSlew = 10  #slew time of the telescope, to give it some time to reach source	
	stowTimes, slewTimes, doy = findErrors(logFilePath)
	if doy <100:
		doyRange = ['0'+str(doy-1),'0'+str(doy),'0'+str(doy+1)]
	else:
		doyRange = [str(doy-1),str(doy),str(doy+1)]
	scansAffectedStow = findScansAffected(sumFilePath, stowTimes, doyRange,telescopeSlew)
	scansAffectedSlew = findScansAffected(sumFilePath, slewTimes, doyRange, 0)
	scansAffectedSlew = uniqueList(scansAffectedSlew)
	writeSavedData(stowTimes, slewTimes, scansAffectedStow,scansAffectedSlew,experiment,station,printSlew,printSlewScan) # write it to a file
	
main() # run the main function
	   
	   
