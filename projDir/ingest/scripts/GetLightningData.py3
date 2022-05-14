#!/usr/bin/python3

#============================================
#
# Download lightning data from CWB ftp server
#
#============================================

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

########################################################################
# Manage the retrieval

def manageRetrieval(startTime, endTime):

    if (options.debug):
        print("Retrieving for times: ", 
              startTime, " to ", endTime, file=sys.stderr)

    startDayStr = startTime.strftime('%Y%m%d')
    endDayStr = endTime.strftime('%Y%m%d')

    # single day

    if (startDayStr == endDayStr):

        getData(startDayStr)
        print("---->> Num files downloaded: ", fileCount, file=sys.stderr)
        return

    # multiple days

    thisDayStr = startDayStr
    while (thisDayStr <= endDayStr):

        if (options.debug):
            print("===>>> processing day:  ", thisDay, file=sys.stderr)

        getForInterval(thisDayStr)
            
        # go to next day
        thisDay = datetime.datetime.strptime(thisDayStr,'%Y%m%d') + datetime.timedelta(1)
        thisDayStr = thisDay.strftime('%Y%m%d')

    print("---->> Num files downloaded: ", fileCount, file=sys.stderr)

########################################################################
# Get the data for the specified day

def getData(thisDay):

    global fileCount

    # get the local file list, i.e. files already downloaded
    localDir = options.localDirBase+'/'+thisDay
    if not os.path.exists(localDir):
        os.makedirs(localDir)
    localFiles = os.listdir(localDir)

    # open ftp connection
    cwbFTP = FTP(options.ftpServer,options.ftpUser,options.ftpPassword)

    # get the ftp file list
    cwbFTP.cwd(thisDay)
    platforms = cwbFTP.nlst()
    if options.platform in platforms:
        cwbFTP.cwd(options.platform)
        remoteFiles = cwbFTP.nlst()

    # download new files
    for ifile in remoteFiles:
        if not ifile in localFiles:
            print(ifile)
            with open(os.path.join(localDir,ifile),'wb') as ftpFile:
                cwbFTP.retrbinary(f"RETR {ifile}", ftpFile.write)
            fileCount = fileCount + 1

            # write latest_data_info
            (junk,timeStr,ext) = ifile.split('.')
            relPath = os.path.join(thisDay, ifile)
            cmd = options.lroseBinDir + "/LdataWriter -dir " + options.localDirBase \
                + " -rpath " + relPath \
                + " -ltime " + timeStr \
                + " -writer " + thisScriptName \
                + " -dtype lit"
            runCommand(cmd)

    # close ftp connection
    cwbFTP.quit()

    
########################################################################
# Parse the command line

def parseArgs():
    
    global options

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
    parser.add_option('--ftpServer',
                      dest='ftpServer',
                      default='thpobs.cwb.gov.tw',
                      help='CWB ftp server name')
    parser.add_option('--ftpUser',
                      dest='ftpUser',
                      default='thpwgt',
                      help='CWB ftp server username')
    parser.add_option('--ftpPassword',
                      dest='ftpPassword',
                      default='TAHOPE#tw2022',
                      help='CWB ftp server password')
    parser.add_option('--platform',
                      dest='platform',
                      default='LIGHTNING',
                      help='directory on ftp server:one of [DISTRO/LIGHTNING/NWP/RADAR/SAT/SOUNDING/SURFACE/WINDPRO]')
    parser.add_option('--localDirBase',
                      dest='localDirBase',
                      default=os.environ['DATA_DIR']+'/raw/lightning',
                      help='Path of dir to which the netcdf files are written')
    parser.add_option('--lroseBinDir',
                      dest='lroseBinDir',
                      default='/usr/local/lrose/bin',
                      help='Path of dir of lrose binaries')
    parser.add_option('--lookbackSecs',
                      dest='lookbackSecs',
                      default=3600,
                      help='Lookback secs in realtime mode')
    parser.add_option('--realtime',
                      dest='realtimeMode', default=True,
                      action="store_true",
                      help='Realtime mode - check every sleepSecs, look back lookbackSecs')
    parser.add_option('--sleepSecs',
                      dest='sleepSecs',
                      default=150,
                      help='Sleep secs in realtime mode')

    (options, args) = parser.parse_args()

    if (options.verbose):
        options.debug = True
        
    if (options.debug):
        print("Options:", file=sys.stderr)
        print("  debug? ", options.debug, file=sys.stderr)
        print("  ftpServer ", options.ftpServer, file=sys.stderr)
        print("  ftpUser ", options.ftpUser, file=sys.stderr)
        print("  ftpPassword ", options.ftpPassword, file=sys.stderr)
        print("  platform: ", options.platform, file=sys.stderr)
        print("  localDirBase: ", options.localDirBase, file=sys.stderr)
        print("  lroseBinDir: ", options.lroseBinDir, file=sys.stderr)
        print("  realtimeMode? ", options.realtimeMode, file=sys.stderr)
        print("  lookbackSecs: ", options.lookbackSecs, file=sys.stderr)
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
