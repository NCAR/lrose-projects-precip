#!/usr/bin/env python

#===========================================================================
#
# Run VertCompute on time series for PRECIP
#
#===========================================================================

from __future__ import print_function

import os
import sys
import subprocess
from optparse import OptionParser
import math
import datetime

def main():

#   globals

    global options
    global debug
    global startTime
    global endTime

    homeDir = os.environ.get('HOME')
    projDir = os.environ.get('PROJ_DIR')
    dataDir = os.environ.get('DATA_DIR')

# parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--start',
                      dest='startTime',
                      default='2022 06 08 00 00 00',
                      help='Start time for plots')
    parser.add_option('--end',
                      dest='endTime',
                      default='2022 06 09 00 00 00',
                      help='End time for plots')
    parser.add_option('--deltaSecs',
                      dest='deltaSecs',
                      default=3600,
                      help='Number of seconds for each analysis, between start time and end time')
    parser.add_option('--paramFile',
                      dest='paramFile',
                      default='calibration/params/VertCompute.spoldrx.sim',
                      help='Parameter file for VertCompute, relative to PROJ_DIR')
    
    parser.add_option('--timeSeriesDir',
                      dest='timeSeriesDir',
                      default='time_series/spoldrx/save',
                      help='Time series directory relative to DATA_DIR')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    deltaTime = datetime.timedelta(0, options.deltaSecs)
    if (options.debug):
        print("Running %prog", file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  deltaSecs: ", options.deltaSecs, file=sys.stderr)
        print("  deltaTime: ", deltaTime, file=sys.stderr)

    # loop through the times, running VertCompute

    time1 = startTime
    time2 = time1 + deltaTime

    
    while (time1 < endTime):

        print("  time1, time2: ", time1, time2, file=sys.stderr)

        date1Str = time1.strftime("%Y%m%d")
        hour1Str = time1.strftime("%Y%m%d_%H")

        cmd = "VertCompute -params " + \
              projDir + "/" + options.paramFile + " " + \
              "-f " + dataDir + "/" + options.timeSeriesDir + "/" + \
              date1Str + "/" + hour1Str + "*"

        print("  cmd: ", cmd, file=sys.stderr)
        
        runCommand(cmd)

        time1 = time1 + deltaTime
        time2 = time2 + deltaTime

    sys.exit(0)
    
########################################################################
# decode date and time

def decodeDateTime(dateTimeStr):

    dateTimeParts = dateTimeStr.split('_')
    dateStr = dateTimeParts[0]
    timeStr = dateTimeParts[1]

    dateParts = dateStr.split("/")
    timeParts = timeStr.split(":")

    year = int(dateParts[0])
    month = int(dateParts[1])
    day = int(dateParts[2])

    hour = int(timeParts[0])
    minute = int(timeParts[1])
    secs = float(timeParts[2])
    sec = int(secs)
    usec = int((secs - sec) * 1000000.0)

    thisTime = datetime.datetime(year, month, day,
                                 hour, minute, sec, usec)
    
    return thisTime

########################################################################
# Check is a number

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

########################################################################
# Moving average filter

def movingAverage(values, window):

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')

    for ii in range(0, int(window / 2) + 1):
        sma[ii] = values[ii]
        sma[len(sma)-ii-1] = values[len(sma)-ii-1]

    return sma

########################################################################
# define funtion for linear fit

def flinear(B, x):
    '''Linear function y = m*x + b'''
    # B is a vector of the parameters.
    # x is an array of the current x values.
    # x is in the same format as the x passed to Data or RealData.
    #
    # Return an array in the same format as y passed to Data or RealData.
    return B[0]*x + B[1]

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug):
        print("running cmd:",cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.debug):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

