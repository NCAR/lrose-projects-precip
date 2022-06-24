#! /usr/bin/env python3

#============================================
#
# Download lightning data from CWB ftp server
#
#============================================

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
    global archiveMode
    global fileCount

    # initialize file count

    fileCount = 0

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

    # create dirs if necessary

    try:
        os.makedirs(options.localDirBase)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: cannot make output dir: ", options.localDirBase, file=sys.stderr)
            print("  ", exc, file=sys.stderr)

    # realtime mode - loop forever

    if (options.realtimeMode):
        lookbackSecs = datetime.timedelta(0, int(options.lookbackSecs))
        while(True):
            fileCount = 0
            nowTime = time.gmtime()
            endTime = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                                        nowTime.tm_hour, nowTime.tm_min)
            startTime = endTime - lookbackSecs
            manageRetrieval(startTime, endTime)
            time.sleep(int(options.sleepSecs))
        return

    # archive mode - one shot

    manageRetrieval(startTime, endTime)
            
    endString = "END: " + thisScriptName
    nowTime = datetime.datetime.now()
    endString += " at " + str(nowTime)
    
    print("==============================================", file=sys.stderr)
    print(endString, file=sys.stderr)
    print("==============================================", file=sys.stderr)

    sys.exit(0)

########################################################################
# Manage the retrieval

def manageRetrieval(startTime, endTime):

    if (options.debug):
        print("Retrieving for times: ", 
              startTime, " to ", endTime, file=sys.stderr)

    if (startTime.day == endTime.day):

        # single day
        startDay = datetime.date(startTime.year, startTime.month, startTime.day)
        getForInterval(startDay, startTime, endTime)
        print("---->> Num files downloaded: ", fileCount, file=sys.stderr)
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
            getForInterval(thisDay, periodStart, periodEnd)

        elif (thisDay == endDay):
            # get from start of end day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = endTime
            getForInterval(thisDay, periodStart, periodEnd)

        else:
            # get for the full day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                          23, 59, 59)
            getForInterval(thisDay, periodStart, periodEnd)

        # go to next day
        thisDay = thisDay + datetime.timedelta(1)

    print("---->> Num files downloaded: ", fileCount, file=sys.stderr)

########################################################################
# Get the data for the specified time interval

def getForInterval(thisDay, startTime, endTime):

    global fileCount

    # get the local file list, i.e. files already downloaded

    localFileList = getLocalFileList(thisDay)

    # get remote file list
    
    # open ftp connection
    cwbFTP = FTP(options.ftpServer,options.ftpUser,options.ftpPassword)

    # get the ftp file list
    thisDayStr = thisDay.strftime("%Y%m%d")
    try:
        cwbFTP.cwd(thisDayStr)
    except:
        print("WARNING - no data on this day: ", thisDayStr, file=sys.stderr)
        return

    platforms = cwbFTP.nlst()
    if options.platform in platforms:
        platformDir = options.platform + '/' + options.ftpSubDir
        try:
            cwbFTP.cwd(platformDir)
        except:
            print("WARNING - cannot chdir to: ", platformDir, file=sys.stderr)
            return
        #cwbFTP.cwd(options.platform)
        remoteFiles = cwbFTP.nlst()

        # download new files
        for ifile in remoteFiles:
        
            if (not ifile in localFileList and ifile.endswith(options.fileSuffix)) or (not ifile in localFileList and options.platform == 'DISTRO'):
            
                # get time of ifile
                (timeStr,type) = getTimeAndType(ifile)
                year = int(timeStr[0:4]);
                month = int(timeStr[4:6]);
                day = int(timeStr[6:8]);
                hour = int(timeStr[8:10]);
                minute = int(timeStr[10:12]);
                sec = int(timeStr[12:14]);
                fileTime = datetime.datetime(year, month, day, hour, minute, sec);
            
                if(options.verbose):
                    print("checking file, time: ", ifile, fileTime, file=sys.stderr)

                # download file if in time window
                if(fileTime >= startTime and fileTime <= endTime):

                    while True:
                        try:
                            #with open(os.path.join(localDir,ifile),'wb') as ftpFile:
                            with open(os.path.join(options.localDirBase,thisDayStr,ifile),'wb') as ftpFile:
                                cwbFTP.retrbinary(f"RETR {ifile}", ftpFile.write)
                                break
                        except:
                            print("===>>> Reestablishing ftp connection . . . try again.", file=sys.stderr)
                            cwbFTP = FTP(options.ftpServer,options.ftpUser,options.ftpPassword)
                    fileCount = fileCount + 1

                    # write latest_data_info
                    relPath = os.path.join(thisDayStr, ifile)
                    cmd = options.lroseBinDir + "/LdataWriter -dir " + options.localDirBase \
                        + " -rpath " + relPath \
                        + " -ltime " + timeStr \
                        + " -writer " + thisScriptName \
                        + " -dtype " + type
                    runCommand(cmd)

                else:

                    if (options.verbose):
                        print("==>> file not in requested time window: ", ifile, file=sys.stderr)

    # close ftp connection
    cwbFTP.quit()

########################################################################
# Get list of files already downloaded

def getLocalFileList(date):

    # make the target directory and go there
    
    dateStr = date.strftime("%Y%m%d")
    dayDir = os.path.join(options.localDirBase, dateStr)
    try:
        os.makedirs(dayDir)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: trying to create dir: ", dayDir, file = sys.stderr)
            print("  exception: ", exc, file = sys.stderr)

    # get local file list - i.e. those which have already been downloaded
    
    os.chdir(dayDir)
    localFileList = os.listdir(dayDir)
    localFileList.reverse()

    if (options.verbose):
        print("==>> localFileList: ", localFileList, file=sys.stderr)

    return localFileList
            
########################################################################
# Get time and type of file

def getTimeAndType(file):

    global options

    if options.platform == 'LIGHTNING':
        (junk,timeStr,ext) = file.split('.')
        type = options.fileSuffix
    elif options.platform == 'SURFACE':
        (timeStr,junk,junk,ext) = file.split('.')
        timeStr = timeStr+'00'
        type = 'mdf'
    elif options.platform == 'RADAR':
        if options.ftpSubDir == 'MOSAIC2D' or options.ftpSubDir == 'MOSAIC3D':
            (junk,date,time,junk) = file.split('.')
            timeStr = date+time+'00'
            type = 'unkown'
        elif options.ftpSubDir == 'QPE1HR':
            (junk,date,time,junk) = file.split('.')
            timeStr = date+time+'00'
            type = 'unkown'
        elif options.ftpSubDir == 'RCWF':
            (date,time,junk,junk) = file.split('_')
            timeStr = date+time+'00'
            type = 'nexrad'
        else:
            (base,ext) = os.path.splitext(file)
            timeStr = base[0:14]
            type = options.fileSuffix
    elif options.platform == 'SOUNDING':
        (baseStr,junk,ext) = file.split('.')
        (stnid,timeStr) = baseStr.split('-')
        timeStr = timeStr+'0000'
        type = options.fileSuffix
    elif options.platform == 'DISTRO':
        (date,time) = file.split('_')
        timeStr = date+time+'00'
        type = 'txt'

    return timeStr, type

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
    parser.add_option('--force',
                      dest='force', default=False,
                      action="store_true",
                      help='Force transfer even if file previously downloaded')
    parser.add_option('--ftpServer',
                      dest='ftpServer',
                      default='thpobs.cwb.gov.tw',
                      help='CWB ftp server name')
    parser.add_option('--ftpUser',
                      dest='ftpUser',
                      default=os.environ['CWB_FTP_USER'],
                      help='CWB ftp server username')
    parser.add_option('--ftpPassword',
                      dest='ftpPassword',
                      default=os.environ['CWB_FTP_PWD'],
                      help='CWB ftp server password')
    parser.add_option('--ftpSubDir',
                      dest='ftpSubDir',
                      default='',
                      help='CWB ftp server password')
    parser.add_option('--platform',
                      dest='platform',
                      default='',
                      help='directory on ftp server:one of [DISTRO/LIGHTNING/NWP/RADAR/SAT/SOUNDING/SURFACE/WINDPRO]')
    parser.add_option('--localDirBase',
                      dest='localDirBase',
                      default=os.environ['DATA_DIR']+'/raw',
                      help='Path of dir to which the netcdf files are written')
    parser.add_option('--lroseBinDir',
                      dest='lroseBinDir',
                      default=os.environ['HOME']+'/lrose/bin',
                      help='Path of dir of lrose binaries')
    parser.add_option('--fileSuffix',
                      dest='fileSuffix',
                      default='lit',
                      help='Suffix of target files')
    parser.add_option('--lookbackSecs',
                      dest='lookbackSecs',
                      default=3600,
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
        print("  instance ", options.instance, file=sys.stderr)
        print("  force? ", options.force, file=sys.stderr)
        print("  ftpServer ", options.ftpServer, file=sys.stderr)
        print("  ftpUser ", options.ftpUser, file=sys.stderr)
        print("  ftpPassword ", options.ftpPassword, file=sys.stderr)
        print("  ftpSubDir ", options.ftpSubDir, file=sys.stderr)
        print("  platform: ", options.platform, file=sys.stderr)
        print("  localDirBase: ", options.localDirBase, file=sys.stderr)
        print("  lroseBinDir: ", options.lroseBinDir, file=sys.stderr)
        print("  fileSuffix: ", options.fileSuffix, file=sys.stderr)
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
