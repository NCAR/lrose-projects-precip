#!/usr/bin/env python

#===========================================================================
#
# Produce plots for field biases
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
    global debug
    global startTime
    global endTime
    global zdrStatsStartTime
    global zdrStatsEndTime

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
    parser.add_option('--biasFile',
                      dest='biasFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/features/qc1/fieldBias/tables/field_bias.sur.txt',
                      help='File path for field biases')
    parser.add_option('--title',
                      dest='title',
                      default='Field Biases from FixFieldVals app - truth minus orig',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=200,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='2022 05 25 03 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2022 08 11 00 00 00',
                      help='End time for XY plot')

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
        print("  biasFilePath: ", options.biasFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)

    # read in column headers for bias results

    global biasHdrs, biasData, biasTimes
    iret, biasHdrs, biasData = readColumnHeaders(options.biasFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for bias results

    biasData, biasTimes = readInputData(options.biasFilePath, biasHdrs, biasData)

    # render the plot
    
    doPlot()

    sys.exit(0)
    
########################################################################
# Read columm headers for the data
# this is in the first line

def readColumnHeaders(filePath):

    colHeaders = []
    colData = {}

    fp = open(filePath, 'r')
    line = fp.readline()
    fp.close()
    
    commentIndex = line.find("#")
    if (commentIndex == 0):
        # header
        colHeaders = line.lstrip("# ").rstrip("\n").split(',')
        if (options.debug):
            print("colHeaders: ", colHeaders, file=sys.stderr)
    else:
        print("ERROR - readColumnHeaders", file=sys.stderr)
        print("  First line does not start with #", file=sys.stderr)
        return -1, colHeaders, colData
    
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []
        
    return 0, colHeaders, colData

########################################################################
# Read in the data

def readInputData(filePath, colHeaders, colData):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()

    obsTimes = []
    colData = {}
    for index, var in enumerate(colHeaders, start=0):
        colData[var] = []

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue
            
        if (options.verbose):
            print("reading line: ", line, file=sys.stderr)
            
        # data
        
        data = line.strip().split(',')
        if (len(data) != len(colHeaders)):
            if (options.debug):
                print("skipping line: ", line, file=sys.stderr)
            continue;

        values = {}
        for index, var in enumerate(colHeaders, start=0):
            if (var == 'count' or \
                var == 'year' or var == 'month' or var == 'day' or \
                var == 'hour' or var == 'min' or var == 'sec' or \
                var == 'unix_time'):
                values[var] = int(data[index])
            elif (var.find('Name') >= 0):
                values[var] = data[index]
            else:
                values[var] = float(data[index])

        # load observation times array
        
        year = values['year']
        month = values['month']
        day = values['day']
        hour = values['hour']
        minute = values['min']
        sec = values['sec']

        thisTime = datetime.datetime(year, month, day,
                                     hour, minute, sec)

        if (thisTime >= startTime and thisTime <= endTime):
            for index, var in enumerate(colHeaders, start=0):
                colData[var].append(values[var])
            obsTimes.append(thisTime)

    fp.close()

    return colData, obsTimes

########################################################################
# Moving average filter

def movingAverage(values, window):

    if (window < 2):
        return values

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    half = int(window/2)
    sma[0:half] = values[0:half]
    sma[-half:] = values[-half:]
    return sma

########################################################################
# Plot

def doPlot():

    fileName = options.biasFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for bias data

    ntimes = np.array(biasTimes).astype(datetime.datetime)
    
    dbzBias = np.array(biasData["dbzDiff"]).astype(np.double)
    dbzBiasAv = movingAverage(dbzBias, lenMeanFilter)
    dbzBiasAv[dbzBiasAv > 5] = math.nan;
    dbzBiasAv[dbzBiasAv < -0.5] = math.nan;

    zdrBias = np.array(biasData["zdrDiff"]).astype(np.double)
    zdrBiasAv = movingAverage(zdrBias, lenMeanFilter)
    #zdrBiasAv[zdrBiasAv > 5] = math.nan;
    #zdrBiasAv[zdrBiasAv < -5] = math.nan;

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    
    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)

    ax1a.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1a.set_title("DBZ bias (dB)")
    ax1b.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1b.set_title("ZDR bias (dB)")

    ax1a.plot(ntimes, dbzBiasAv, \
              label = 'DBZ Bias', linewidth=1, color='black')

    ax1b.plot(ntimes, zdrBiasAv, \
              label = 'ZDR Bias', linewidth=1, color='black')

    configDateAxis(ax1a, -9999, -9999, "DBZ BIAS (dB)", 'upper right')
    configDateAxis(ax1b, -9999, -9999, "ZDR BIAS (dB)", 'upper right')

    ax1a.set_facecolor("lightgrey")
    ax1b.set_facecolor("lightgrey")

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.10, left=0.06, right=0.97, top=0.90)

    fig1.suptitle(options.title)
    plt.show()

########################################################################
# initialize legends etc

def configDateAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=5)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%y/%m/%d')
    ax.xaxis.set_major_locator(dates.DayLocator(interval = 2))
    ax.xaxis.set_minor_locator(dates.DayLocator(interval = 1))
    ax.xaxis.set_major_formatter(hfmt)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

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

