#!/usr/bin/env python

#===========================================================================
#
# RUN CIDD FOR GENERATING IMAGES
#
#===========================================================================

import os
import sys
import time
import datetime
from datetime import timedelta
import string
import subprocess

def main():

    global _debug
    _debug = True
    global _progName
    _progName = 'run_CIDD.test.py'

    start_year = 2014
    start_month = 10
    start_day = 01
    start_hour = 02
    start_min = 00
    start_sec = 00

    startTime = datetime.datetime(start_year, start_month, start_day,
                                  start_hour, start_min, start_sec)
    print >>sys.stderr, "startTime:  " + str(startTime)

    end_year = 2014
    end_month = 10
    end_day = 01
    end_hour = 04
    end_min = 00
    end_sec = 00

    endTime = datetime.datetime(end_year, end_month, end_day,
                                end_hour, end_min, end_sec)
    print >>sys.stderr, "endTime:  " + str(endTime)

    deltaTime = datetime.timedelta(0.0, 300.0)
    print >>sys.stderr, "deltaTime:  " + str(deltaTime)

    thisTime = startTime

    while (thisTime <= endTime):
        print >>sys.stderr, "thisTime:  " + str(thisTime)
        timeStr = "%.4d%.2d%.2d%.2d%.2d%.2d" % (thisTime.year,
                                                thisTime.month,
                                                thisTime.day,
                                                thisTime.hour,
                                                thisTime.minute,
                                                thisTime.second)
        print >>sys.stderr, "timeStr:  " + timeStr
        cmdStr = "CIDD -p CIDD.catalog.test -v 2 -t " + timeStr
        print >>sys.stderr, "cmdStr:  " + cmdStr
        runCommand(cmdStr)
        thisTime = thisTime + deltaTime
        

    sys.exit(0)

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (_debug):
        print >>sys.stderr, "running cmd:",cmd
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal: ", -retcode
        else:
            if (_debug):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
        return -1

    return 0

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
