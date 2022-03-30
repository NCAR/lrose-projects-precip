#!/usr/bin/env python

#======================================================================
#
# Create RHI images for a DOW radar.  The DOW radar data is assumed to be
# in cfradial format.  The radar file must be read to get the location
# of the radar.
#
#======================================================================

import os
import sys
import time
import datetime
from datetime import timedelta
import string
import subprocess
from optparse import OptionParser
from stat import *
import math

def main():

    global options
    global fullFilePath
    global validTimeStr
    
    # parse the command line

    parseArgs()

    # initialize
    
    appName = "create_dow_images.rhi.py"
    print "==========================================================="
    print "BEGIN: " + appName + " at " + str(datetime.datetime.now())
    print "==========================================================="

    # Set the environment variables that will be used in the CIDD
    # parameter file

    os.environ['MAX_RANGE_KM'] = '%f' % (options.max_range_km)

    # run HawkEye to create the images
    
    cmd = 'run_HawkEye.catalog.dow7.rhi ' + fullFilePath
    runCommand(cmd);

    print "============================================================="
    print "END: " + appName + " at " + str(datetime.datetime.now())
    print "============================================================="

    sys.exit(0)


########################################################################
# Parse the command line

def parseArgs():
    
    global options
    global fullFilePath
    global validTimeStr

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

    parser.add_option('--abs_dir_path',
                      dest='abs_dir_path',
                      default='',
                      help='The full absolute path for the directory')

    parser.add_option('--rel_data_path',
                      dest='rel_data_path',
                      default='',
                      help='The file path relative to the absolute directory')

    parser.add_option('--valid_time',
                      dest='valid_time',
                      default='',
                      help='Comma-delimited valid time: yyyy,mm,dd,hh,mm,ss')

    # these options are specific to the radar

    parser.add_option('--radar_name',
                      dest='radar_name',
                      default='armor',
                      help='Type of image -- armor, chill, etc')

    # max range

    parser.add_option('--max_range_km',
                      dest='max_range_km',
                      type='float',
                      default='90.0',
                      help='Max range for data.')

    (options, args) = parser.parse_args()
    
    # compute values derived from args

    fullFilePath = os.path.join(options.abs_dir_path, options.rel_data_path)

    (year, month, day, hour, min, sec) = options.valid_time.split(',')
    validTimeStr = year + month + day + hour + min + sec
    
    if (options.verbose == True):
        options.debug = True

    if (options.debug == True):
        print >>sys.stderr, "Options:"
        print >>sys.stderr, "  debug? ", options.debug
        print >>sys.stderr, "  verbose? ", options.verbose
        print >>sys.stderr, "  abs_dir_path: ", options.abs_dir_path
        print >>sys.stderr, "  rel_data_path: ", options.rel_data_path
        print >>sys.stderr, "  fullFilePath: ", fullFilePath
        print >>sys.stderr, "  valid_time: ", options.valid_time
        print >>sys.stderr, "  validTimeStr: ", validTimeStr
        print >>sys.stderr, "  radar_name: ", options.radar_name
        print >>sys.stderr, "  max_range_km: ", options.max_range_km

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

