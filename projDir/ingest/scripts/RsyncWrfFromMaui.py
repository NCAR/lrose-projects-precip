#!/usr/bin/env python

#=====================================================================
#
# rsync the WRF data from MAUI at CSU
#
#=====================================================================

from __future__ import print_function

import os
import sys
import time
import shutil
import glob
import datetime

import string
import subprocess
from optparse import OptionParser

def main():

    global options
    global startTime, endTime
    global archiveMode

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

    if (options.realtimeMode):
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

    for genHour in [ 0, 6, 12, 18]:

        genTime = datetime.datetime(thisDay.year, 
                                    thisDay.month,
                                    thisDay.day,
                                    genHour, 0, 0)
        
        genDir = genTime.strftime("%Y/%m%d%H")

        print("rsync for gen time: ", genDir, file=sys.stderr)

        # make the target dir, go there

        targetDir = options.targetDir + "/" + genDir

        try:
            os.makedirs(targetDir)
        except:
            print("Note: dir exists: ", targetDir, file=sys.stderr)

        os.chdir(targetDir)

        # create rsync command - only copy the ensemble mean

        cmd = "rsync -av " \
            + options.remoteUser + "@" \
            + options.remoteHost + ":" \
            + options.remoteDir + "/" + genDir + "/" \
            + "mean" + " ."
                  
        # run the command
        
        runCommand(cmd)

    return

########################################################################
# Parse the command line

def parseArgs():
    
    global options
    global startTime, endTime
    global archiveMode

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
    parser.add_option('--instance',
                      dest='instance',
                      default='test',
                      help='Provides uniqueness on the command line')
    parser.add_option('--remoteHost',
                      dest='remoteHost',
                      default='maui.atmos.colostate.edu',
                      help='remote server IP address')
    parser.add_option('--remoteUser',
                      dest='remoteUser',
                      default='mdixon',
                      help='user name on remote server')
    parser.add_option('--remoteDir',
                      dest='remoteDir',
                      default='/bell-scratch2/precip/DATA/model/PSU_enkf',
                      help='Source dir on remote server')
    parser.add_option('--targetDir',
                      dest='targetDir',
                      default='/scr/cirrus3/rsfdata/projects/precip/raw/wrf/psu',
                      help='Path of target dir to copy files')
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

    if (options.verbose):
        options.debug = True
        
    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))
    
    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))
    if (startTime.year > 1970 and endTime.year > 1970):
        archiveMode = True
    else:
        archiveMode = False
    
    if (options.debug):
        print("Options:", file=sys.stderr)
        print("  debug? ", options.debug, file=sys.stderr)
        print("  remoteHost ", options.remoteHost, file=sys.stderr)
        print("  remoteUser ", options.remoteUser, file=sys.stderr)
        print("  remoteDir ", options.remoteDir, file=sys.stderr)
        print("  targetDir: ", options.targetDir, file=sys.stderr)
        print("  lookbackSecs: ", options.lookbackSecs, file=sys.stderr)
        print("  archiveMode? ", archiveMode, file=sys.stderr)
        print("  realtimeMode? ", options.realtimeMode, file=sys.stderr)
        print("  sleepSecs: ", options.sleepSecs, file=sys.stderr)

    if (options.realtimeMode == True and archiveMode == True):
        print("ERROR - ", thisScriptName, file=sys.stderr)
        print("  For realtime mode, do not set start or end times", file=sys.stderr)
        sys.exit(1)
        
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
