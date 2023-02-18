#!/usr/bin/env python

#===========================================================================
#
# Produce images for CIDD
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
                      default='2022 05 25 02 06 00',
                      help='Start time for images')
    parser.add_option('--endTime',
                      dest='endTime',
                      default='2022 08 11 00 00 00',
                      help='End time for images')
    parser.add_option('--deltaSecs',
                      dest='deltaSecs',
                      default=720,
                      help='Delta time between images')
    parser.add_option('--ciddParamsPath',
                      dest='ciddParamsPath',
                      default=os.path.join(projDir, "qc/params/CIDD.spol.images"),
                      help='Path to CIDD params path')

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
        print("  ciddParamsPath: ", options.ciddParamsPath, file=sys.stderr)

    deltaTime = datetime.timedelta(0, options.deltaSecs)

    plotTime = startTime
    while (plotTime <= endTime):
        print("  plotTime: ", plotTime, file=sys.stderr)
        ciddTimeStr = plotTime.strftime('%Y%m%d%H%M')
        dateStr = plotTime.strftime('%Y%m%d')
        os.environ['DATE_STR'] = dateStr
        cmd = "CIDD -p " + options.ciddParamsPath + " -t " + ciddTimeStr
        runCommand(cmd)
        plotTime = plotTime + deltaTime

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

