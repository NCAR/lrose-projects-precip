#!/usr/bin/python3

#=====================================================================
#
# Download Himawari satellite files from AWS - python3 version
#
#=====================================================================

from __future__ import print_function

import os
import sys
import time
import datetime
from datetime import timedelta
import glob
import shutil
import bz2

import string
import subprocess
from optparse import OptionParser

import urllib.request, urllib.parse, urllib.error
from xml.dom import minidom
from sys import stdin
from urllib.request import urlopen
from subprocess import call

def main():

    global options
    global tmpDir
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
    
    print("=============================================", file=sys.stderr)
    print(beginString, file=sys.stderr)
    print("=============================================", file=sys.stderr)

    # create dirs

    try:
        os.makedirs(options.tmpDir)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: cannot make tmp dir: ", options.tmpDir, file=sys.stderr)
            print("  ", exc, file=sys.stderr)
            
    try:
        os.makedirs(options.outputDir)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: cannot make output dir: ", options.outputDir, file=sys.stderr)
            print("  ", exc, file=sys.stderr)

    try:
        os.makedirs(options.ncDirBase)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: cannot make output dir: ", options.outputDir, file=sys.stderr)
            print("  ", exc, file=sys.stderr)

    # realtime mode - loop forever

    if (options.realtimeMode):
        lookbackSecs = timedelta(0, int(options.lookbackSecs))
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
        # get times every 10 minutes between startTime and endTime
        timeList = getTimeList(startTime,endTime)
        getForInterval(startDay, startTime, endTime, timeList)
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
            timeList = getTimeList(periodStart,periodEnd)
            getForInterval(thisDay, periodStart, periodEnd, timeList)

        elif (thisDay == endDay):
            # get from start of end day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = endTime
            timeList = getTimeList(periodStart,periodEnd)
            getForInterval(thisDay, periodStart, periodEnd, timeList)

        else:
            # get for the full day
            periodStart = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                            0, 0, 0)
            periodEnd = datetime.datetime(thisDay.year, thisDay.month, thisDay.day,
                                          23, 59, 59)
            timeList = getTimeList(periodStart,periodEnd)
            getForInterval(thisDay, periodStart, periodEnd, timeList)

        # go to next day
        thisDay = thisDay + timedelta(1)

    print("---->> Num files downloaded: ", fileCount, file=sys.stderr)

########################################################################
# Get time list for the specified time interval - must be in multiples of
# 10 minutes

def getTimeList(startTime, endTime):

    startHour = startTime.hour
    startMin = startTime.minute

    print('getTimeList: startTime.minute = ',startTime.minute)
    
    if (startMin % 10) == 0:
        begin = startTime
    else:
        startMin = round(startMin/10)*10
        if startMin == 60:
            startMin = 50
        print('   in else: startMin = ',startMin)
        startTime = datetime.datetime(startTime.year,startTime.month,startTime.day,
                                      startTime.hour,startMin)
        startHour = startTime.hour

    timeList = []   
    nextTime = startTime
    nextHour = startHour
    nextMin = startMin
    while nextTime <= endTime:
        hhmm = str(nextHour).zfill(2)+str(nextMin).zfill(2)
        timeList.append(hhmm)
        nextTime = nextTime+timedelta(minutes=10)
        nextHour = nextTime.hour
        nextMin = nextTime.minute

    return timeList

########################################################################
# Get the data for the specified time interval

def getForInterval(thisDay, startTime, endTime, timeList):

    # get the local file list, i.e. files already downloaded

    localFileList = getLocalFileList(thisDay)

    # construct the URL

    for itime in timeList:
        awsDateStr =  startTime.strftime("%Y/%m/%d")
        bucketURL = "http://noaa-himawari8.s3.amazonaws.com"
        dirListURL = bucketURL+ "/?prefix=AHI-L1b-FLDK/" + awsDateStr + "/" + itime
        if (options.debug):
            print("dirListURL: ", dirListURL, file=sys.stderr)

        # get the listing in XML

        xmldoc = minidom.parse(urlopen(dirListURL))
        itemlist = xmldoc.getElementsByTagName('Key')
        if (options.debug):
            print("number of keys found: ", len(itemlist), file=sys.stderr)

        for x in itemlist:
            # Only process files that look like "AHI-L1b-FLDK/2012/07/02/0150/HS_H08_20120702_0150_BXX_FLDK_RXX_S0XXXX.DAT.bz2"
            fileEntry = str(getNodeText(x.childNodes))
            try:
                (fdomain,fyear, fmonth, fday, ftime, fileName) = str.split(fileEntry, '/')
                if (options.verbose):
                    print("==>> fdomain, fyear, fmonth, fday, ftime, fname: ",
                          fdomain, fyear, fmonth, fday, ftime, fileName, file=sys.stderr)
                year = int(fileName[7:11]);
                month = int(fileName[11:13]);
                day = int(fileName[13:15]);
                hour = int(fileName[16:18]);
                minute = int(fileName[18:20]);
                band = fileName[22:24]
                res = fileName[31:33]
                fileTime = datetime.datetime(year, month, day, hour, minute);
            except:
                if(options.verbose):
                    print("bad entry: ", fileEntry, file=sys.stderr)
                continue

            if(options.verbose):
                print("checking file, time: ", fileEntry, fileTime, file=sys.stderr)

            #if(fileTime >= startTime and fileTime <= endTime and band == satBand):
            if( band == (options.satBand).zfill(2) and res == (options.resolution).zfill(2) ):
                
                if (options.force):
                    doDownload(fileTime, fileEntry, fileName)
                else:
                    if (fileName not in localFileList):
                        doDownload(fileTime, fileEntry, fileName)
                    elif (options.debug):
                        print("file previously downloaded: ", fileName, file=sys.stderr)
    
########################################################################
# Get text for nodes

def getNodeText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


########################################################################
# Download specified file

def doDownload(fileTime, fileEntry, fileName):

    global fileCount

    if (options.debug):
        print("Downloading entry, name: ",
              fileEntry, ", ", fileName, file=sys.stderr)

    if(options.dryRun):
        # no download
        return

    # download into tmp file

    dataURL = "https://noaa-himawari8.s3.amazonaws.com"
    tmpPath = os.path.join(options.tmpDir, fileName)
    try:
        tmpFile = open(tmpPath, 'wb')
        opener = urllib.request.URLopener()
        myfile = opener.open(os.path.join(dataURL,fileEntry))
        tmpFile.write(myfile.read())
        tmpFile.close()
        fileCount = fileCount + 1
    except OSError as e:
        print("ERROR: Got error: ", e, file=sys.stderr)

    # create final dir

    dateStr =  fileTime.strftime("%Y%m%d")
    satDir = os.path.join(options.outputDir, 'Channel'+(options.satBand).zfill(2))
    outDayDir = os.path.join(satDir, dateStr)
    try:
        os.makedirs(outDayDir)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: trying to create dir: ", outDayDir, file=sys.stderr)
            print("Exception: ", exc, file=sys.stderr)
    
    # move to output dir
    
    cmd = "mv " + tmpPath + " " + outDayDir
    runCommand(cmd)

    # create netcdf file if all ten strips have been downloaded
    
    timeString = fileTime.strftime('%Y%m%d_%H%M')
    partFiles = glob.glob(outDayDir+'/HS_H08_'+timeString+'_B'+(options.satBand).zfill(2)+'_FLDK_R'+(options.resolution).zfill(2)+'_S*.DAT.bz2')
    
    if len(partFiles) == 10:

        makeNcFile(partFiles, fileTime, dateStr, outDayDir)

########################################################################
# Create netcdf file

def makeNcFile(partFiles, fileTime, dateStr, outDayDir):

    if (options.debug):
        print("Creating netcdf file for: ", dateStr, fileTime, file=sys.stderr)
        
    ncDir = options.ncDirBase + '/himawari_ch'+(options.satBand).zfill(2)
    ncDateDir = ncDir + '/' + fileTime.strftime('%Y%m%d')
    if not os.path.exists(ncDateDir):
        os.makedirs(ncDateDir)
    ncFile = 'himawari_ch'+(options.satBand).zfill(2)+'.'+fileTime.strftime('%Y%m%d.%H%M')+'.nc'
    #cmd = '/home/disk/meso-home/brodzik/PRECIP/DATA/Himawari/hisd2netcdf/hisd2netcdf'
    cmd = os.environ.get('PROJ_DIR') + '/ingest/scripts/hisd2netcdf'
    for file in partFiles:
        (root,ext) = os.path.splitext(file)
        with bz2.BZ2File(file) as fr, open(root,'wb') as fw:
            shutil.copyfileobj(fr,fw)
        cmd = cmd + ' -i '+root
    cmd = cmd + ' -o ' + ncDateDir + '/' + ncFile
    runCommand(cmd)
    datFiles = glob.glob(outDayDir+'/HS_H08_*.DAT')
    for file in datFiles:
        os.remove(file)
    
    # write latest_data_info
    
    timeStr = fileTime.strftime("%Y%m%d%H%M%S")
    relPath = os.path.join(dateStr, ncFile)
    cmd = "LdataWriter -dir " + ncDir \
        + " -rpath " + relPath \
        + " -ltime " + timeStr \
        + " -writer " + thisScriptName \
        + " -dtype netcdf"
    runCommand(cmd)

########################################################################
# Get list of files already downloaded

def getLocalFileList(date):

    # make the target directory and go there
    
    dateStr = date.strftime("%Y%m%d")
    satDir = os.path.join(options.outputDir, 'Channel'+(options.satBand).zfill(2) )
    dayDir = os.path.join(satDir, dateStr)
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
    parser.add_option('--satBand',
                      dest='satBand',
                      default=13,
                      help='satellite band ranging from 01 to 16')
    parser.add_option('--resolution',
                      dest='resolution',
                      default='20',
                      help="resolution: '05'=>0.5km, '10'=>1.0km, '20'=>2.0km")
    parser.add_option('--ncDirBase',
                      dest='ncDirBase',
                      default='/tmp/aws',
                      help='Path of dir to which the netcdf files are written')
    parser.add_option('--outputDir',
                      dest='outputDir',
                      default='/tmp/aws',
                      help='Path of dir to which the raw files are written')
    parser.add_option('--tmpDir',
                      dest='tmpDir',
                      default='/tmp/stage',
                      help='Path of tmp dir for staging data')
    parser.add_option('--force',
                      dest='force', default=False,
                      action="store_true",
                      help='Force transfer even if file previously downloaded')
    parser.add_option('--dryRun',
                      dest='dryRun', default=False,
                      action="store_true",
                      help='Dry run: do not download data, list what would be downloaded')
    parser.add_option('--realtime',
                      dest='realtimeMode', default=False,
                      action="store_true",
                      help='Realtime mode - check every sleepSecs, look back lookbackSecs')
    parser.add_option('--lookbackSecs',
                      dest='lookbackSecs',
                      default=1800,
                      help='Lookback secs in realtime mode')
    parser.add_option('--sleepSecs',
                      dest='sleepSecs',
                      default=10,
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
        print("  force? ", options.force, file=sys.stderr)
        print("  dryRun? ", options.dryRun, file=sys.stderr)
        print("  satBand: ", options.satBand, file=sys.stderr)
        print("  resolution: ", options.resolution, file=sys.stderr)
        print("  ncDirBase: ", options.ncDirBase, file=sys.stderr)
        print("  outputDir: ", options.outputDir, file=sys.stderr)
        print("  tmpDir: ", options.tmpDir, file=sys.stderr)
        print("  archiveMode? ", archiveMode, file=sys.stderr)
        print("  realtimeMode? ", options.realtimeMode, file=sys.stderr)
        print("  lookbackSecs: ", options.lookbackSecs, file=sys.stderr)
        print("  sleepSecs: ", options.sleepSecs, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)

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
