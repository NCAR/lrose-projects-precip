#!/usr/bin/env python

#===========================================================================
#
# Put image data to catalog
#
#===========================================================================

import os
import sys
from stat import *
import time
import datetime
from datetime import timedelta
import string
import ftplib
import subprocess
from optparse import OptionParser

def main():

    appName = __file__

    global options
    global ftpUser
    global ftpPassword

    ftpUser = "junk"
    ftpPassword = "front@ucar.edu"

    # parse the command line

    parseArgs()

    # initialize
    
    if (options.debug == True):
        print >>sys.stderr, "======================================================="
        print >>sys.stderr, "BEGIN: " + appName + " " + str(datetime.datetime.now())
        print >>sys.stderr, "======================================================="

    #   compute valid time string

    validTime = time.gmtime(int(options.validTime))
    year = int(validTime[0])
    month = int(validTime[1])
    day = int(validTime[2])
    hour = int(validTime[3])
    minute = int(validTime[4])
    sec = int(validTime[5])
    validDayStr = "%.4d%.2d%.2d" % (year, month, day)
    validTimeStr = "%.4d%.2d%.2d%.2d%.2d" % (year, month, day, hour, minute)
    dateTimeStr = "%.4d%.2d%.2d-%.2d%.2d%.2d" % (year, month, day, hour, minute, sec)

    # produce image file

    if (options.fullFilePath.find("SMN") >= 0):
        # SMN data file
        (fullImagePath, catalogName) = createSkewT()
    elif (options.fileExt == "png"):
        # brazil-generated png file
        # needs renaming
        (fullImagePath, catalogName) = renameBrazilPng()

    if (options.debug == True):
        print >>sys.stderr, "fullImagePath: ", fullImagePath
        print >>sys.stderr, "catalogName: ", catalogName

    # put the image file

    ftpFile(fullImagePath, catalogName)

    # let the user know we are done

    if (options.debug == True):
        print >>sys.stderr, "======================================================="
        print >>sys.stderr, "END: " + appName + " " + str(datetime.datetime.now())
        print >>sys.stderr, "======================================================="

    sys.exit(0)

########################################################################
# Create SKEWT image file

def createSkewT():

    fullImagePath = "junk1"
    catalogName = "junk2"

    return fullImagePath, catalogName

########################################################################
# Rename Brazil file

def renameBrazilPng():

    fullImagePath = "junk3"
    catalogName = "junk4"

    return fullImagePath, catalogName

########################################################################
# Ftp the file

def ftpFile(fileName, filePath):

    return
    # set ftp debug level

    if (options.debug == True):
        ftpDebugLevel = 2
    else:
        ftpDebugLevel = 0
    
    targetDir = options.targetDir
    ftpServer = options.ftpServer
    
    # open ftp connection
    
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
    ftp.storbinary('STOR ' + fileName, fp)
    
    # close ftp connection
                
    ftp.quit()

    return

########################################################################
# Parse the command line

def parseArgs():
    
    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    # these options come from the ldata info file

    parser.add_option('--debug',
                      dest='debug', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--unix_time',
                      dest='validTime',
                      default=0,
                      help='Valid time for image')
    parser.add_option('--full_path',
                      dest='fullPath',
                      default='unknown',
                      help='Full path of image file')
    parser.add_option('--rel_data_path',
                      dest='relDataPath',
                      default='unknown',
                      help='Relative path of image file')
    parser.add_option('--full_file_path',
                      dest='fullFilePath',
                      default='unknown',
                      help='Relative path of image file')
    parser.add_option('--file_name',
                      dest='fileName',
                      default='unknown',
                      help='Name of image file')
    parser.add_option('--file_ext',
                      dest='fileExt',
                      default='txt',
                      help='File extension')

    # these options are specific to the image type

    parser.add_option('--ftp_server',
                      dest='ftpServer',
                      default='catalog.eol.ucar.edu',
                      help='Target FTP server')
    catalog_name = "relampago"
    defaultTargetDir = 'pub/incoming/catalog/' + catalog_name
    parser.add_option('--target_dir',
                      dest='targetDir',
                      default=defaultTargetDir,
                      help='Target directory on the FTP server')
    parser.add_option('--category',
                      dest='category',
                      default='NONE',
                      help='Category portion of the catalog file name')
    parser.add_option('--platform',
                      dest='platform',
                      default='NONE',
                      help='Platform portion of the catalog file name.')

    (options, args) = parser.parse_args()

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  validTime: ", options.validTime
        print >>sys.stderr, "  fullPath: ", options.fullPath
        print >>sys.stderr, "  relDataPath: ", options.relDataPath
        print >>sys.stderr, "  fullFilePath: ", options.fullFilePath
        print >>sys.stderr, "  fileName: ", options.fileName
        print >>sys.stderr, "  fileExt: ", options.fileExt
        print >>sys.stderr, "  ftpServer: ", options.ftpServer
        print >>sys.stderr, "  targetDir: ", options.targetDir
        print >>sys.stderr, "  category: ", options.category
        print >>sys.stderr, "  platform: ", options.platform

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug == True):
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

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
