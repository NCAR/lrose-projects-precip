#!/usr/bin/env python

#===========================================================================
#
# Create movies from SPOL images
#
#===========================================================================

from __future__ import print_function

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
from numpy import linalg, array, ones
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import datetime
import contextlib

def main():

#   globals

    global options

# parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    projDir = os.environ['PROJ_DIR']
    dataDir = os.environ['DATA_DIR']
    parser.add_option('--debug',
                      dest='debug', default=True,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--startTime',
                      dest='startTime',
                      default='2022 05 25 00 00 00',
                      help='Start time for images')
    parser.add_option('--endTime',
                      dest='endTime',
                      default='2022 08 11 00 00 00',
                      help='End time for images')
    parser.add_option('--deltaSecs',
                      dest='deltaSecs',
                      default=86400,
                      help='Delta time between images')
    parser.add_option('--imagesTopDir',
                      dest='imagesTopDir',
                      default=os.path.join(dataDir, "precip/images/spol"),
                      help='Path to dir containing CIDD images')
    parser.add_option('--fieldName',
                      dest='fieldName',
                      default="DBZ_F",
                      help='Field name for movie')

    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running %prog", file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  deltaSecs: ", options.deltaSecs, file=sys.stderr)
        print("  imagesTopDir: ", options.imagesTopDir, file=sys.stderr)

    deltaTime = datetime.timedelta(0, options.deltaSecs)

    # go to the image top dir, and get the date dir list

    os.chdir(options.imagesTopDir)

    # get listing of dated dirs
    
    dirList = os.listdir(options.imagesTopDir)
    dirList.sort()

    # loop through directories
    
    for dirName in dirList:
        dirPath = os.path.join(options.imagesTopDir, dirName)
        if (options.debug):
            print("  working on dir: ", dirPath)
        os.chdir(dirPath)

        # get list of image files for the designated field
        
        fileList = os.listdir(dirPath)
        imageFileList = []
        imageFileList += [entry for entry in fileList if entry.endswith('.png')]
        fieldFileList = []
        fieldFileList += [entry for entry in imageFileList if (entry.find(options.fieldName) > 0)]
        fieldFileList.sort()
        #if (options.debug):
        #    for fieldFile in fieldFileList:
        #        print("       file: ", fieldFile)

        # generate command to create animated gif

        movieFileName = options.fieldName + "_" + dirName + "_loop.gif"
        moviePath = os.path.join(dirPath, movieFileName)

        cmd = "convert -verbose -delay 50 -loop 0 "
        for fieldFile in fieldFileList:
            cmd += fieldFile
            cmd += " "
        cmd += moviePath
        runCommand(cmd)
        

    sys.exit(0)

    plotTime = startTime
    while (plotTime <= endTime):
        print("  plotTime: ", plotTime, file=sys.stderr)
        plotTime = plotTime + deltaTime
        ciddTimeStr = plotTime.strftime('%Y%m%d%H%M')
        dateStr = plotTime.strftime('%Y%m%d')
        os.environ['DATE_STR'] = dateStr
        cmd = "CIDD -p " + options.ciddParamsPath + " -t " + ciddTimeStr
        runCommand(cmd)

    sys.exit(0)
    
########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.debug):
        print("running cmd:",cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.debug):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

