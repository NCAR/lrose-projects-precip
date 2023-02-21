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
    qcVersion = os.environ['VERSION']
    parser.add_option('--debug',
                      dest='debug', default=True,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--imagesTopDir',
                      dest='imagesTopDir',
                      default=os.path.join(dataDir,
                                           "precip/images/" + qcVersion + "/spol_moments"),
                      help='Path to dir containing CIDD images')
    parser.add_option('--movieDir',
                      dest='movieDir',
                      default=os.path.join(dataDir,
                                           "precip/images/" + qcVersion + "/spol_movies"),
                      help='Path to dir containing CIDD movies')
    parser.add_option('--fieldName',
                      dest='fieldName',
                      default="DBZ_F",
                      help='Field name for movie')
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
        print("  imagesTopDir: ", options.imagesTopDir, file=sys.stderr)
        print("  fieldName: ", options.fieldName, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  deltaSecs: ", options.deltaSecs, file=sys.stderr)

    deltaTime = datetime.timedelta(0, int(options.deltaSecs))

     # ensure movie output dir exists

    if (os.path.isdir(options.movieDir) == False):
        os.makedirs(options.movieDir)

    # loop through movie times, creating movie at each time
    
    movieStartTime = startTime
    movieEndTime = movieStartTime + deltaTime
    while (movieStartTime <= endTime):
        createMovie(movieStartTime, movieEndTime)
        movieStartTime = movieEndTime
        movieEndTime += deltaTime

    sys.exit(0)

########################################################################
# Create movie

def createMovie(startTime, endTime):

    if (options.debug):
        print("==>> creating movie, startTime, endTime: ",
              startTime, ", ", endTime)

    # create the list of images to be in the loop

    imagePathList = []

    # search for files to be in movie
    
    deltaTimeDay = datetime.timedelta(1)
    dayTime = startTime
    while (dayTime <= endTime):
        
        dayStr = dayTime.strftime('%Y%m%d')
        subDirPath = os.path.join(options.imagesTopDir, dayStr)
        if (options.verbose):
            print("  adding files from dir: ", subDirPath)
            
        # get list of image files for the designated field
        
        fileList = os.listdir(subDirPath)
        for entry in fileList:
            if (entry.endswith('.png') and (entry.find(options.fieldName) > 0)):
                # get data time from file name
                fileTimeStr = entry[-18:-4]
                fileDataTime = datetime.datetime.strptime(fileTimeStr, "%Y%m%d%H%M%S")
                if (fileDataTime >= startTime and fileDataTime <= endTime):
                    filePath = os.path.join(subDirPath, entry)
                    imagePathList.append(filePath)

        dayTime += deltaTimeDay

    # sort the image paths into time order
    
    imagePathList.sort()

    # generate command to create animated gif
        
    startTimeStr = startTime.strftime('%Y%m%d%H%M%S')
    movieFileName = options.fieldName + "_" + startTimeStr + "_loop.gif"
    moviePath = os.path.join(options.movieDir, movieFileName)

    if (options.debug):
        print("==>> creating movie, path: ", moviePath)
        
    cmd = "convert -verbose -delay 25 -loop 0 "
    for fieldFile in imagePathList:
        cmd += fieldFile
        cmd += " "
    cmd += moviePath

    # run the command
        
    runCommand(cmd)
    
    return

# get list of image files for the designated field
        
#fileList = os.listdir(dirPath)
#imageFileList = []
#imageFileList += [entry for entry in fileList if entry.endswith('.png')]
#fieldFileList = []
#fieldFileList += [entry for entry in imageFileList if (entry.find(options.fieldName) > 0)]
#fieldFileList.sort()

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.verbose):
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

