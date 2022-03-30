#!/usr/bin/env python

#===========================================================================
#
# Put relampago images data to catalog
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
    
    # parse the command line

    parseArgs()

    # initialize
    
    if (options.debug):
        print >>sys.stderr, "======================================================"
        print >>sys.stderr, "BEGIN: " + appName + " " + str(datetime.datetime.now())
        print >>sys.stderr, "======================================================"

    #   compute valid time string

    unixTime = time.gmtime(int(options.unixTime))
    year = int(unixTime[0])
    month = int(unixTime[1])
    day = int(unixTime[2])
    hour = int(unixTime[3])
    minute = int(unixTime[4])
    sec = int(unixTime[5])
    validDayStr = "%.4d%.2d%.2d" % (year, month, day)
    validTimeStr = "%.4d%.2d%.2d%.2d%.2d" % (year, month, day, hour, minute)
    dateTimeStr = "%.4d%.2d%.2d-%.2d%.2d%.2d" % (year, month, day, hour, minute, sec)

    # compute full path of image
    
    dataDir = os.environ['DATA_DIR']
    incomingFilePath = os.path.join(dataDir, options.relFilePath);
    
    # extract the platform and product from the file name.
    # The image files are named like:
    #   <category>.<legend_label>.<button_label>.<platform>.<time>.png.
    
    file_tokens = options.fileName.split(".")
    if (options.debug):
        print >>sys.stderr, "filename toks: "
        print >>sys.stderr, file_tokens

    if len(file_tokens) != 6:
        print >>sys.stderr, "!!! ==>> Invalid file name: ", options.fileName
        sys.exit(0)

    # check for valid time

    timeStr = file_tokens[4]
    yearStr = timeStr[0:4]
    year = int(yearStr)
    if (year < 2018):
        print >>sys.stderr, "!!! ==>> Invalid time string: ", yearStr
        sys.exit(0)
    dayStr = timeStr[0:8]

    # incoming category

    inCat = file_tokens[0]
    if (inCat != 'radar'):
        print >>sys.stderr, "!!! ==>> Bad incoming category: ", inCat
        print >>sys.stderr, "         Should be 'radar'"
        sys.exit(0)

    # field
        
    field_name = file_tokens[2]

    # platform name

    platform = file_tokens[3]

    # compute catalog file name

    catalogFieldName = field_name

    # extension

    extension = file_tokens[5]

    catalogFileName = (options.catalogCategory + "." +
                       platform + "." +
                       validTimeStr + "." +
                       catalogFieldName + "." +
                       extension)

    # put the image file

    ftpFile(incomingFilePath, catalogFileName)
    
    #  # put the associated XML file
    #  xmlFilePath = os.path.join(options.imageDir, options.fileName[:-3] + "xml")
    #  xmlCatalogName = options.category + "." + platform + \
    #                   "." + validTimeStr + "." + product + ".xml"
    #  putFile(xmlFilePath, xmlCatalogName)

    # let the user know we are done

    if (options.debug):
        print >>sys.stderr, "======================================================="
        print >>sys.stderr, "END: " + appName + " " + str(datetime.datetime.now())
        print >>sys.stderr, "======================================================="

    sys.exit(0)

########################################################################
# Put the specified file

def putFile(filePath, catalogFileName):
    
    if (options.debug):
        print >>sys.stderr, "Handling file: ", filePath
        print >>sys.stderr, "  catalogFileName: ", catalogFileName

    # create tmp dir if necessary

    catalog_name = 'relampago'
    imageDir = os.path.join(catalog_name, "raw/tmp/images")
    dataDir = os.environ['DATA_DIR']
    tmpDir = os.path.join(dataDir, imageDir)
    if (options.debug):
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

def ftpFile(incomingFilePath, catalogFileName):
    
    if (options.debug):
        print >>sys.stderr, "==>> doing ftp <<=="
        print >>sys.stderr, "  incomingFilePath: ", incomingFilePath
        print >>sys.stderr, "  catalogFileName: " + catalogFileName
        print >>sys.stderr, "  to ftpDir: " + options.ftpDir

    # set ftp debug level

    if (options.debug):
        ftpDebugLevel = 2
    else:
        ftpDebugLevel = 0
    
    # open ftp connection
    
    ftp = ftplib.FTP(options.ftpServer, options.ftpUser, options.ftpPassword)
    ftp.set_debuglevel(ftpDebugLevel)
    
    # go to target dir

    if (options.debug):
        print >>sys.stderr, "ftp cwd to: " + options.ftpDir
    
    ftp.cwd(options.ftpDir)
        
    # put the file

    fp = open(incomingFilePath, 'rb')
    ftp.storbinary('STOR ' + catalogFileName, fp)
    
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
                      dest='unixTime',
                      default=0,
                      help='Valid unix time for image')

    parser.add_option('--full_path',
                      dest='fullPath',
                      default='unknown',
                      help='Full path of image file')

    parser.add_option('--file_name',
                      dest='fileName',
                      default='unknown',
                      help='Name of image file')

    parser.add_option('--rel_file_path',
                      dest='relFilePath',
                      default='unknown',
                      help='Relative path of image file')

    parser.add_option('--catalog_name',
                      dest='catalogName',
                      default='relampago',
                      help='Catalog name - i.e. project name')

    parser.add_option('--catalog_category',
                      dest='catalogCategory',
                      default='gis',
                      help='Outgoing category for the catalog')

    parser.add_option('--ftp_server',
                      dest='ftpServer',
                      default='catalog.eol.ucar.edu',
                      help='FTP server')

    parser.add_option('--ftp_user',
                      dest='ftpUser',
                      default='anonymous',
                      help='FTP user name')

    parser.add_option('--ftp_password',
                      dest='ftpPassword',
                      default='',
                      help='FTP password')

    parser.add_option('--ftp_dir',
                      dest='ftpDir',
                      default='/pub/incoming/catalog/relampago',
                      help='Target directory on the FTP server')

    (options, args) = parser.parse_args()
    
    if (options.debug):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  unixTime: ", options.unixTime
        print >>sys.stderr, "  fullPath: ", options.fullPath
        print >>sys.stderr, "  fileName: ", options.fileName
        print >>sys.stderr, "  relFilePath: ", options.relFilePath
        print >>sys.stderr, "  catalogName: ", options.catalogName
        print >>sys.stderr, "  catalogCategory: ", options.catalogCategory
        print >>sys.stderr, "  ftpServer: ", options.ftpServer
        print >>sys.stderr, "  ftpUser: ", options.ftpUser
        print >>sys.stderr, "  ftpPassword: ", options.ftpPassword
        print >>sys.stderr, "  ftpDir: ", options.ftpDir

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug):
        print >>sys.stderr, "running cmd:",cmd
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal: ", -retcode
        else:
            if (options.debug):
                print >>sys.stderr, "Child returned code: ", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

########################################################################
# kick off main method

if __name__ == "__main__":

   main()
