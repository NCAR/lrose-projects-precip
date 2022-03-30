#!/usr/bin/env python

#===========================================================================
#
# wget images from web site
#
#===========================================================================

import os
import sys
from stat import *
from math import *
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser
import urllib
import ftplib

def main():

    global options
    global _debug
    _debug = False
    global _progName
    _progName = 'wget_images.py'

    # parse the command line

    parseArgs()

    # initialize
    
    if (_debug):
        print >>sys.stderr, "===================================="
        print >>sys.stderr, "START: _progName"
        print >>sys.stderr, "  " + str(datetime.datetime.now())
        print >>sys.stderr, "===================================="

    # loop through the lookback times

    index = int(options.nlookback) - 1
    while (index >= 0):
        handleLookback(index)
        index = index - 1

    # done

    if (_debug):
        print >>sys.stderr, "===================================="
        print >>sys.stderr, "DONE: _progName"
        print >>sys.stderr, "  " + str(datetime.datetime.now())
        print >>sys.stderr, "===================================="

    sys.exit(0)

########################################################################
# Handle the lookback period

def handleLookback(lookbackIndex):

    if (_debug):
        print >>sys.stderr, "==>> handling lookback number: ", lookbackIndex

    # get current time, rounded back to frequency of interest

    currentTime = time.gmtime()
    freqHrs = int(options.frequency)
    year = int(currentTime[0])
    month = int(currentTime[1])
    day = int(currentTime[2])
    hour = int(currentTime[3]) - (int(currentTime[3] % freqHrs))
    minute = 0
    sec = 0

    if (options.timestr != 'none'):
        # time is specified on command line as yyyymmddhh
        year = int(options.timestr[0:4])
        month = int(options.timestr[4:6])
        day = int(options.timestr[6:8])
        hour = int(options.timestr[8:10])

    specTime = datetime.datetime(year, month, day, hour, minute, sec)
    lookbackSecs = datetime.timedelta(0, freqHrs * 3600 * lookbackIndex)
    lookbackTime = specTime - lookbackSecs

    fileHourStr = "%.4d%.2d%.2d%.2d" % (lookbackTime.year,
                                        lookbackTime.month,
                                        lookbackTime.day,
                                        lookbackTime.hour)

    dayDir = "%.4d%.2d%.2d" % (lookbackTime.year,
                               lookbackTime.month,
                               lookbackTime.day)

    fileName = fileHourStr + options.suffix
    url = options.url + "/" + fileName

    if (_debug):
        print >>sys.stderr, "  specTime: ", specTime
        print >>sys.stderr, "  lookbackTime: ", lookbackTime
        print >>sys.stderr, "  lookbackSecs: ", lookbackSecs
        print >>sys.stderr, "  fileHourStr: ", fileHourStr
        print >>sys.stderr, "  fileName: ", fileName
        print >>sys.stderr, "  dayDir: ", dayDir
        print >>sys.stderr, "  url: ", url

    # make output dir

    dayPath = os.path.join(options.outdir, dayDir)
    try:
        os.makedirs(dayPath)
    except OSError, e:
        if (False):
            print >>sys.stderr, "Making output dir: ", dayPath
            print >>sys.stderr, "  exception: ", e

    # go to output dir

    os.chdir(options.outdir)

    # check if output file exists

    relPath = os.path.join(dayDir, fileName)
    if (os.path.exists(relPath)):
        if (_debug):
            print >>sys.stderr, "  file already here: ", relPath
            print >>sys.stderr, "  not retrieving"
        return


    # get file from URL
    
    response = urllib.urlopen(url)
    data = response.read()
    lines = str.split(data, '\n')
    if (len(lines) >= 3):
        if (lines[0].find('DOCTYPE HTML') >= 0 and
            lines[2].find('404 Not Found') >= 0):
            if (_debug):
                print >>sys.stderr, "  no file yet: ", fileName
            return

    # write the file
        
    outFile = open(relPath, "wb")
    outFile.write(data)
    outFile.close()

    if (_debug):
        print >>sys.stderr, "  wrote file: ", relPath

    # write latest_data_info

    cmd = 'LdataWriter -dir ' + options.outdir + \
        ' -rpath ' + relPath + \
        ' -ltime ' + fileHourStr + '0000' + \
        ' -writer ' + _progName
    runCommand(cmd)

    # compute the full path and extension

    outPath = os.path.join(options.outdir, relPath);
    (root, ext) = os.path.splitext(outPath)
    if (_debug):
        print >>sys.stderr, "  outPath: ", outPath
        print >>sys.stderr, "  outExt: ", ext

    # compute the catalog name

    catalogName = \
        options.category + '.' + \
        options.platform + '.' + \
        fileHourStr + '00.' + \
        options.fieldName + ext;
    if (_debug):
        print >>sys.stderr, "  catalogName: ", catalogName
        
    # put to ftp site

    if (options.doFtp == True):
        ftpFile(catalogName, outPath)
        
    if (_debug):
        print >>sys.stderr, "  outPath: ", outPath
        time.sleep(float(options.sleepsecs))

    return

########################################################################
# Parse the command line

def parseArgs():
    
    global options
    global _debug

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    # these options come from the ldata info file

    parser.add_option('--debug',
                      dest='debug', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--url',
                      dest='url',
                      default='unknown',
                      help='URL for file location')
    parser.add_option('--suffix',
                      dest='suffix',
                      default='_KDNR.gif',
                      help='Suffix in file name, after date/time')
    parser.add_option('--outdir',
                      dest='outdir',
                      default='/tmp/test',
                      help='Output directory')
    parser.add_option('--frequency',
                      dest='frequency',
                      default='12',
                      help='Frequency of data in hours.')
    parser.add_option('--nlookback',
                      dest='nlookback',
                      default='1',
                      help='Number of periods to look back for data.')
    parser.add_option('--sleepsecs',
                      dest='sleepsecs',
                      default='0',
                      help='Number of seconds to sleep between downloads.')
    parser.add_option('--timestr',
                      dest='timestr',
                      default='none',
                      help='Specify the time string as yyyymmddhh.')

    # ftp to catalog

    parser.add_option('--do_ftp',
                      dest='doFtp', default='False',
                      action="store_true",
                      help='Activate FPT transfers')
    parser.add_option('--ftp_server',
                      dest='ftpServer',
                      default='catalog.eol.ucar.edu',
                      help='Target FTP server')
    parser.add_option('--target_dir',
                      dest='targetDir',
                      default='pub/incoming/catalog/front',
                      help='Target directory on the FTP server')
    parser.add_option('--category',
                      dest='category',
                      default='upperair',
                      help='Category portion of the catalog file name')
    parser.add_option('--platform',
                      dest='platform',
                      default='DEN-radiosonde',
                      help='Platform portion of the catalog file name.')
    parser.add_option('--fieldName',
                      dest='fieldName',
                      default='skewT',
                      help='Field name for the catalog file name.')

    (options, args) = parser.parse_args()
    if (options.debug == True):
        _debug = True
    else:
        _debug = False

    if (_debug):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  url: ", options.url
        print >>sys.stderr, "  suffix: ", options.suffix
        print >>sys.stderr, "  outdir: ", options.outdir
        print >>sys.stderr, "  frequency: ", options.frequency
        print >>sys.stderr, "  nlookback: ", options.nlookback
        print >>sys.stderr, "  sleepsecs: ", options.sleepsecs
        print >>sys.stderr, "  timestr: ", options.timestr
        print >>sys.stderr, "  ftpServer: ", options.ftpServer
        print >>sys.stderr, "  targetDir: ", options.targetDir
        print >>sys.stderr, "  category: ", options.category
        print >>sys.stderr, "  platform: ", options.platform
        print >>sys.stderr, "  doFtp: ", options.doFtp

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
            if (options.debug == True):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
        return -1

    return 0

########################################################################
# Ftp the file

def ftpFile(catalogName, filePath):

    # set ftp debug level

    if (options.debug == True):
        ftpDebugLevel = 2
    else:
        ftpDebugLevel = 0
    
    targetDir = options.targetDir
    ftpServer = options.ftpServer
    
    # open ftp connection
    
    ftpUser = "anonymous"
    ftpPassword = "front@ucar.edu"

    ftp = ftplib.FTP(ftpServer, ftpUser, ftpPassword)
    ftp.set_debuglevel(ftpDebugLevel)
    
    # go to target dir

    if (options.debug == True):
        print >>sys.stderr, "ftp cwd to: " + targetDir
    
    ftp.cwd(targetDir)

    # put the file

    if (options.debug == True):
        print >>sys.stderr, "putting file: ", filePath

    fp = open(filePath, 'rb')
    ftp.storbinary('STOR ' + catalogName, fp)
    
    # close ftp connection
                
    ftp.quit()

    return

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
