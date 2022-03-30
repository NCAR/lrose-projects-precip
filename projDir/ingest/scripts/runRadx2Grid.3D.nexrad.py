#!/usr/bin/env python

#===========================================================================
#
# Run Radx2Grid for 3D products
#
#===========================================================================

import os
import sys
from stat import *
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser

def main():

    global options
    global scriptName
    scriptName = "runRadx2Grid.3D.nexrad.py"

    # parse the command line

    parseArgs()

    # start message
    
    if (options.debug == True):
        print >>sys.stderr, "=============================================="
        print >>sys.stderr, \
            "START: " + scriptName + " at " + str(datetime.datetime.now())
        print >>sys.stderr, "=============================================="

    # compute full path of data
    
    dataFilePath = os.path.join(options.absDirPath, options.relDataPath);

    if (options.debug == True):
        print "dataFilePath: ", dataFilePath
        print "file exists: ", os.path.exists(dataFilePath)

    # set up command

    radar_name = options.radarName
    RADAR_NAME = radar_name.upper()

    os.environ["radar_name"] = radar_name
    os.environ["RADAR_NAME"] = RADAR_NAME
    os.environ["MDV_WRITE_FORMAT"] = "FORMAT_MDV"
    os.environ["MDV_WRITE_USING_EXTENDED_PATHS"] = "TRUE"

    projDir = os.environ["PROJ_DIR"]
    paramsDir = os.path.join(projDir, "ingest/params")
    paramsFile = os.path.join(paramsDir, "Radx2Grid.3D.nexrad")

    if (options.debug == True):
        print "radar_name: ", radar_name
        print "RADAR_NAME: ", RADAR_NAME
        print "projDir: ", projDir
        print "paramsDir: ", paramsDir
        print "paramsFile: ", paramsFile

    cmd = "Radx2Grid -instance " + radar_name + " -params " + paramsFile + " -debug -f " + dataFilePath

    runCommand(cmd)

    sys.exit(0)

########################################################################
# Parse the command line

def parseArgs():
    
    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default='False',
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default='False',
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--valid_utime',
                      dest='validUnixTime',
                      default=0,
                      help='Valid unix time for data')
    parser.add_option('--valid_time',
                      dest='validTimeStr',
                      default=0,
                      help='Valid time string for data')
    parser.add_option('--abs_dir_path',
                      dest='absDirPath',
                      default='unknown',
                      help='Full path of data file')
    parser.add_option('--rel_data_path',
                      dest='relDataPath',
                      default='unknown',
                      help='Relative path of data file')
    parser.add_option('--radar_name',
                      dest='radarName',
                      default='unknown',
                      help='Name of radar')

    (options, args) = parser.parse_args()

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  validUnixTime: ", options.validUnixTime
        print >>sys.stderr, "  validTimeStr: ", options.validTimeStr
        print >>sys.stderr, "  absDirPath: ", options.absDirPath
        print >>sys.stderr, "  relDataPath: ", options.relDataPath
        print >>sys.stderr, "  radarName: ", options.radarName

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
