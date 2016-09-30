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
	logfile= open(logFilePath,'r') # Read the log file and store the times
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
	sumFile = open(sumFilePath,'r')
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

def writeSavedData (outFilePath, stowTimes,slewTimes,scansAffectedStow,scansAffectedSlew,experiment, station):
	StowTimes= open(outFilePath ,'w') #save to a file 
	stowTimes = stowTimes
	slewTimes = slewTimes	
	scansAffectedStow = scansAffectedStow
	scansAffectedSlew = scansAffectedSlew
	experiment = experiment
	station = station
	count=0
	count2=0
	StowTimes.write('The windstow times for ' + experiment + station + ' are:\n')
	if len(stowTimes) == 0:
		StowTimes.write('There were no windstows.\n')	
	else:
		while int(count/2) < int((len(stowTimes)/2)):    
		    StowTimes.write( stowTimes[count] + ' to ' + stowTimes[count+1]+'\n' ) #writes the times in a x to y format
		    count = count +2  
	StowTimes.write('  \n')
	StowTimes.write('The Scans affected are:\n')
	if len(scansAffectedStow)==0:
		StowTimes.write('There were no scans affected by windstows.\n')	
	else:
		while int(count2/2) < int((len(scansAffectedStow)/2)):    
		    StowTimes.write( scansAffectedStow[count2] + ' to ' + scansAffectedStow[count2+1]+'\n' )
		    count2 = count2 +2   
	StowTimes.write('  \n')
	StowTimes.write('  \n')
	StowTimes.write('Onsource status is Slewing Errors:\n')
	if len(scansAffectedSlew) == 0:
		 StowTimes.write('There were no Slewing errors.\n')	
	else:
		for count3, times in enumerate(slewTimes):
			StowTimes.write( slewTimes[count3] +'\n' )
		StowTimes.write('  \n')
		StowTimes.write('The scans affected by slewing errors:\n')
		for count4, scans in enumerate(scansAffectedSlew):
			StowTimes.write( scansAffectedSlew[count4] +'\n' )
	print "Data saved in: ", outFilePath
	StowTimes.close()  

def main(): # calls all the other functions.
	experiment = raw_input("Please enter the experiment name.\n")
	station = raw_input("Please specify a station [hb|ke|yg].\n")
	logFilePath = '/home/arwin/Documents/Code/Python/Whenstow/'+ experiment + station + '.log'  
	outFilePath = '/home/arwin/Documents/Code/Python/Whenstow/StowTimesandScans23.txt'
	sumFilePath = '/home/arwin/Documents/Code/Python/Whenstow/'+ experiment + station +'.sum'
	telescopeSlew = 10  #slew time of the telescope, to give it some time to reach source	
	stowTimes, slewTimes, doy = findErrors(logFilePath)
	doyRange = [str(doy),str(doy+1)] #possible values of Day of year
	scansAffectedStow = findScansAffected(sumFilePath, stowTimes, doyRange,telescopeSlew)
	scansAffectedSlew = findScansAffected(sumFilePath, slewTimes, doyRange, 0)
	scansAffectedSlew = uniqueList(scansAffectedSlew)
	writeSavedData(outFilePath,stowTimes, slewTimes, scansAffectedStow,scansAffectedSlew,experiment,station) # write it to a file
	
main() # run the main function
	   
