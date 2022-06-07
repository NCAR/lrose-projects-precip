#!/usr/bin/env python

#=====================================================================
#
# rsync the SPOL realtime data to the UW server bob
#
#=====================================================================

from __future__ import print_function

import os
import sys
import time
import shutil
import glob
from ftplib import FTP
import datetime

import string
import subprocess
from optparse import OptionParser

def main():

    global options
    global startTime, endTime
    global archiveMode, realtimeMode

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

    # parse the command line

    parseArgs()

    # initialize
    
    beginString = "BEGIN: " + thisScriptName
    nowTime = datetime.datetime.now()
    beginString += " at " + str(nowTime)
    
    print("=========================================================", file=sys.stderr)
    print(beginString, file=sys.stderr)
    print("=========================================================", file=sys.stderr)

    # realtime mode - loop forever

    if (realtimeMode):
        lookbackSecs = datetime.timedelta(0, int(options.lookbackSecs))
        while(True):
            nowTime = time.gmtime()
            endTime = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                                        nowTime.tm_hour, nowTime.tm_min)
            startTime = endTime - lookbackSecs
            manageRsync(startTime, endTime)
            time.sleep(int(options.sleepSecs))
        return

    # archive mode - one shot

    manageRsync(startTime, endTime)
            
    endString = "END: " + thisScriptName
    nowTime = datetime.datetime.now()
    endString += " at " + str(nowTime)
    
    print("==============================================", file=sys.stderr)
    print(endString, file=sys.stderr)
    print("==============================================", file=sys.stderr)

    sys.exit(0)

########################################################################
# Manage the rsync

def manageRsync(startTime, endTime):

    if (options.debug):
        print("Retrieving for times: ", 
              startTime, " to ", endTime, file=sys.stderr)

    if (startTime.day == endTime.day):

        # single day
        startDay = datetime.date(startTime.year, startTime.month, startTime.day)
        rsyncDay(startDay, startTime, endTime)
        return

    # multiple days

    tdiff = endTime - startTime
    tdiffSecs = tdiff.total_seconds()
    if (options.debug):
        print("Proc interval in secs:  ", tdiffSecs, file=sys.stderr)

    startDay = datetime.date(startTime.year, startTime.month, startTime.day)
    endDay = datetime.date(endTime.year, endTime.month, endTime.day)
    thisDay = startDay
    while (thisDay <= endDay):

        if (options.debug):
            print("===>>> processing day:  ", thisDay, file=sys.stderr)
            
        if (thisDay == startDay):
            # get to end of start day
            periodStart = startTime
            periodEnd = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                          23, 59, 59)
            rsyncDay(thisDay, periodStart, periodEnd)

        elif (thisDay == endDay):
            # get from start of end day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = endTime
            rsyncDay(thisDay, periodStart, periodEnd)

        else:
            # get for the full day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                          23, 59, 59)
            rsyncDay(thisDay, periodStart, periodEnd)

        # go to next day
        thisDay = thisDay + datetime.timedelta(1)

########################################################################
# Rsync for the specified day

def rsyncDay(thisDay, startTime, endTime):

    thisDayStr = thisDay.strftime("%Y%m%d")

    print("rsync for day: ", thisDayStr, file=sys.stderr)

    # go to the source dir
    
    os.chdir(sourceDir)

    # create rsync command

    cmd = "rsync -av " + thisDayStr + " " \
          + options.uwUser + "@" \
          + options.uwServer + ":" \
          + targetDir 

    # run the command

    runCommand(cmd)

########################################################################
# Parse the command line

def parseArgs():
    
    global options
    global startTime, endTime
    global archiveMode, realtimeMode

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
    parser.add_option('--uwServer',
                      dest='uwServer',
                      default='bob.atmos.washington.edu',
                      help='UW server name - destination')
    parser.add_option('--uwUser',
                      dest='uwUser',
                      default='meso',
                      help='UW server username')
    parser.add_option('--uwDataDir',
                      dest='uwDataDir',
                      default='/home/disk/monsoon/precip/cfradial/spol_ncar/cfradial/spoldrx',
                      help='UW destination directory')
    parser.add_option('--sourceDir',
                      dest='sourceDir',
                      default='/scr/cirrus3/rsfdata/projects/precip/cfradial/moments/spoldrx',
                      help='Path of dir for source files')
    parser.add_option('--subDir',
                      dest='subDir',
                      default='sur',
                      help='Subdirectory of radar data')
    parser.add_option('--lookbackSecs',
                      dest='lookbackSecs',
                      default=100000,
                      help='Lookback secs in realtime mode')
    parser.add_option('--realtime',
                      dest='realtimeMode', default=False,
                      action="store_true",
                      help='Realtime mode - check every sleepSecs, look back lookbackSecs')
    parser.add_option('--sleepSecs',
                      dest='sleepSecs',
                      default=60,
                      help='Sleep secs in realtime mode')
    parser.add_option('--start',
                      dest='startTime',
                      default='1970 01 01 00 00 00',
                      help='Start time for retrieval - archive mode')
    parser.add_option('--end',
                      dest='endTime',
                      default='1970 01 01 00 00 00',
                      help='End time for retrieval - archive mode')

    (options, args) = parser.parse_args()

    global sourceDir, targetDir
    sourceDir = os.path.join(options.sourceDir, options.subDir)
    targetDir = os.path.join(options.uwDataDir, options.subDir)

    if (options.verbose):
        options.debug = True
        
    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))
    
    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))
    if (options.realtimeMode):
        realtimeMode = True
        archiveMode = False
    elif (startTime.year > 1970 and endTime.year > 1970):
        realtimeMode = False
        archiveMode = True
    else:
        realtimeMode = True
        archiveMode = False
    
    if (options.debug):
        print("Options:", file=sys.stderr)
        print("  debug? ", options.debug, file=sys.stderr)
        print("  uwServer ", options.uwServer, file=sys.stderr)
        print("  uwUser ", options.uwUser, file=sys.stderr)
        print("  uwDataDir ", options.uwDataDir, file=sys.stderr)
        print("  sourceDir: ", options.sourceDir, file=sys.stderr)
        print("  subDir: ", options.subDir, file=sys.stderr)
        print("  lookbackSecs: ", options.lookbackSecs, file=sys.stderr)
        print("  archiveMode? ", archiveMode, file=sys.stderr)
        print("  realtimeMode? ", realtimeMode, file=sys.stderr)
        print("  archiveMode? ", archiveMode, file=sys.stderr)
        print("  sleepSecs: ", options.sleepSecs, file=sys.stderr)

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug):
        print("running cmd: ", cmd, file=sys.stderr)
        
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.debug):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
