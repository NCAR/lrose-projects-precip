#!/usr/bin/env python

#===========================================================================
#
# Put DOW RHI image data to catalog
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

    global options
    global ftpUser
    global ftpPassword

    ftpUser = "anonymous"
    # ftpPassword = "front@ucar.edu"
    ftpPassword = "dixon@ucar.edu"

    # parse the command line

    parseArgs()

    # initialize
    
    if (options.debug == True):
        print >>sys.stderr, "=================================================================="
        print >>sys.stderr, "BEGIN: put_dow_rhi_images_to_catalog at " + str(datetime.datetime.now())
        print >>sys.stderr, "=================================================================="

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

    # compute full path of image
    
    fullFilePath = options.imageDir
    fullFilePath = os.path.join(fullFilePath, options.relDataPath);
    
    # extract the platform and product from the file name.
    # The image files are named like:
    #   <category>.<platform>.<time>.<field>.png.
    
    file_tokens = options.fileName.split(".")
    if (options.debug == True):
        print >>sys.stderr, "filename toks: "
        print >>sys.stderr, file_tokens

    if len(file_tokens) != 5:
        print "*** Invalid file name: ", options.fileName
        sys.exit(0)

    # category

    category = file_tokens[0]
    if (options.category.find("NONE") < 0):
        category = options.category

    # platform

    platform = file_tokens[1]
    if (options.platform.find("NONE") < 0):
        platform = options.platform

    # platform

    timeStr = file_tokens[2]

    # field
        
    field_name = file_tokens[3]

    # time - use from latest data file
    # time_tokens = file_tokens[4].split(".")
    # validTimeStr = time_tokens[0];

    # compute catalog file name

    catalogName = (category + "." + platform + "." +
                   validTimeStr + "." +
                   field_name + "." + "png")

    if (options.debug == True):
        print >>sys.stderr, "catalogName: ", catalogName

    # put the image file

    putFile(fullFilePath, catalogName)

    # optionally remove the file

    if (options.removeAfterCopy == True):
        if (options.debug):
            print >>sys.stderr, "Removing file: ", fullFilePath
        os.remove(fullFilePath)

    # let the user know we are done

    if (options.debug == True):
        print >>sys.stderr, "=================================================================="
        print >>sys.stderr, "END: put_images_to_catalog.py at " + str(datetime.datetime.now())
        print >>sys.stderr, "=================================================================="

    sys.exit(0)

########################################################################
# Put the specified file

def putFile(filePath, catalogName):

    if (options.debug == True):
        print >>sys.stderr, "Handling file: ", filePath
        print >>sys.stderr, "  catalogName: ", catalogName

    # create tmp dir if necessary

    dataDir = os.environ['DATA_DIR']
    tmpDir = os.path.join(dataDir, "images/tmp")
    if (options.debug == True):
        print >>sys.stderr, "  tmpDir: ", tmpDir
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir, 0775)

    # copy the file to the tmp directory

    tmpPath = os.path.join(tmpDir, catalogName)
    cmd = "cp " + filePath + " " + tmpPath
    runCommand(cmd)

    # send the file to the catalog
    
    ftpFile(catalogName, tmpPath)

    # remove the tmp file

    os.remove(tmpPath)

    return 0
    
########################################################################
# Ftp the file

def ftpFile(fileName, filePath):

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
    
    # make dir in case needed
    
    try:
        ftp.mkd(targetDir)
    except ftplib.all_errors, e:
        print >>sys.stderr, "WARNING - mkd failed, dir perhaps already exists?", e

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
    parser.add_option('--verbose',
                      dest='verbose', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--unix_time',
                      dest='validTime',
                      default=0,
                      help='Valid time for image')
    parser.add_option('--full_path',
                      dest='imageDir',
                      default='unknown',
                      help='Full path of image file')
    parser.add_option('--file_name',
                      dest='fileName',
                      default='unknown',
                      help='Name of image file')
    parser.add_option('--rel_data_path',
                      dest='relDataPath',
                      default='unknown',
                      help='Relative path of image file')

    # these options are specific to the image type

    parser.add_option('--ftp_server',
                      dest='ftpServer',
                      default='catalog.eol.ucar.edu',
                      help='Target FTP server')
    parser.add_option('--target_dir',
                      dest='targetDir',
                      default='pub/incoming/catalog/winter',
                      help='Target directory on the FTP server')
    parser.add_option('--category',
                      dest='category',
                      default='NONE',
                      help='Category portion of the catalog file name')
    parser.add_option('--platform',
                      dest='platform',
                      default='NONE',
                      help='Platform portion of the catalog file name.  Overrides platform in image file name if specified.')
    parser.add_option('--remove_after_copy',
                      dest='removeAfterCopy', default='False',
                      action="store_true",
                      help='Remove files after copy to ftp server')

    (options, args) = parser.parse_args()

    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  verbose? ", options.verbose
        print >>sys.stderr, "  validTime: ", options.validTime
        print >>sys.stderr, "  imageDir: ", options.imageDir
        print >>sys.stderr, "  relDataPath: ", options.relDataPath
        print >>sys.stderr, "  fileName: ", options.fileName
        print >>sys.stderr, "  ftpServer: ", options.ftpServer
        print >>sys.stderr, "  targetDir: ", options.targetDir
        print >>sys.stderr, "  category: ", options.category
        print >>sys.stderr, "  platform: ", options.platform
        print >>sys.stderr, "  removeAfterCopy: ", options.removeAfterCopy

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
