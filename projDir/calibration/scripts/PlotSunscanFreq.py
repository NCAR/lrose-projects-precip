#!/usr/bin/env python

#===========================================================================
#
# Produce plots for FREQ-DEPENDENT SUNSCANS ON SPOL
#
#===========================================================================

import os
import sys
import subprocess
from optparse import OptionParser
import numpy as np
from numpy import convolve
from numpy import linalg, array, ones
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib.ticker as ticker
import math
import datetime
import contextlib

def main():

    # globals

    global options
    global debug
    global startTime
    global endTime
    global figNum
    figNum = 0

    appName = 'PlotSunscanFreq.py'
    projDir = os.environ['PROJ_DIR']
    dataDir = os.environ['DATA_DIR']
    homeDir = os.environ['HOME']
    global dataFilePath
    dataFilePath = os.path.join(homeDir, 'data/sunscan/freq_test/text/SunCal.freq.txt')

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--file',
                      dest='dataFilePath',
                      default=dataFilePath,
                      help='File path for comparison results')
    parser.add_option('--widthMain',
                      dest='mainWidthMm',
                      default=300,
                      help='Width of main figure in mm')
    parser.add_option('--heightMain',
                      dest='mainHeightMm',
                      default=300,
                      help='Height of main figure in mm')
    parser.add_option('--filtLen',
                      dest='filtLen',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='2016 09 22 15 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2016 09 22 19 30 00',
                      help='End time for XY plot')
    
    (options, args) = parser.parse_args()
    
    # time limits

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))
    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    if (options.debug == True):
        print >>sys.stderr, "  dataFilePath: ", options.dataFilePath
        print >>sys.stderr, "  startTime: ", startTime
        print >>sys.stderr, "  endTime: ", endTime

    # read in column headers for bias results

    iret, compHdrs, compData = readColumnHeaders(options.dataFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for comp results

    compData, compTimes = readInputData(options.dataFilePath, compHdrs, compData)

    # load up the data arrays

    loadDataArrays(compData, compTimes)

    # render the plots

    doPlot()

    # show them

    plt.show()

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
        colHeaders = line.lstrip("# ").rstrip("\n").split()
        if (options.debug == True):
            print >>sys.stderr, "n colHeaders: ", len(colHeaders)
            print >>sys.stderr, "colHeaders: ", colHeaders
    else:
        print >>sys.stderr, "ERROR - readColumnHeaders"
        print >>sys.stderr, "  First line does not start with #"
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
    lineNum = 0

    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex >= 0):
            continue

        lineNum = lineNum + 1

        # data
        
        data = line.strip().split()
        if (len(data) != len(colHeaders)):
            if (options.debug == True):
                print >>sys.stderr, "skipping line: ", line
                print >>sys.stderr, "  len(data): ", len(data)
            continue;

        for index, var in enumerate(colHeaders, start=0):
            # print >>sys.stderr, "index, data[index]: ", index, ", ", data[index]
            if (var == 'yyyy' or var == 'mm' or var == 'dd' or \
                var == 'hh' or var == 'min' or var == 'ss'):
                colData[var].append(int(data[index]))
            else:
                colData[var].append(float(data[index]))

    fp.close()

    # load observation times array

    year = colData['yyyy']
    month = colData['mm']
    day = colData['dd']
    hour = colData['hh']
    minute = colData['min']
    sec = colData['ss']
    unixDays = colData['days']

    obsTimes = []
    for ii, var in enumerate(year, start=0):
        thisTime = datetime.datetime(year[ii], month[ii], day[ii],
                                     hour[ii], minute[ii], sec[ii])
        obsTimes.append(thisTime)

    return colData, obsTimes

########################################################################
# Moving average filter

def movingAverage(values, window):

    if (window < 2):
        return values

    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma

########################################################################
# Set up arrays for plotting

def loadDataArrays(compData, compTimes):

    filtLen = int(options.filtLen)
    
    # set up arrays

    global ctimes

    ctimes = np.array(compTimes).astype(datetime.datetime)

    global freqMhz
    freqMhz = np.array(compData["freqMhz"]).astype(np.double)

    global widthRatioDiff
    widthRatioDiff = movingAverage(np.array( \
                        compData["widthRatioElAzDiffHV"]).astype(np.double), filtLen)

    global zdrDiff
    zdrDiff = movingAverage(np.array(compData["zdrDiffElAz"]).astype(np.double), filtLen)

    global corr00H
    corr00H = movingAverage(np.array(compData["Corr00H"]).astype(np.double), filtLen)

    global corr00V
    corr00V = movingAverage(np.array(compData["Corr00V"]).astype(np.double), filtLen)

    global corr00
    corr00 = (corr00H + corr00V) / 2.0

    global S1S2
    S1S2 = movingAverage(np.array(compData["meanS1S2"]).astype(np.double), filtLen)

    global peakPower
    peakPower = movingAverage(np.array(compData["quadPower"]).astype(np.double), filtLen)


########################################################################
# Plot

def doPlot():

    # set up plots

    widthIn = float(options.mainWidthMm) / 25.4
    htIn = float(options.mainHeightMm) / 25.4
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    ax1 = fig.add_subplot(4,1,1,xmargin=0.0)
    ax2 = fig.add_subplot(4,1,2,xmargin=0.0)
    ax3 = fig.add_subplot(4,1,3,xmargin=0.0)
    ax4 = fig.add_subplot(4,1,4,xmargin=0.0)
    
    ax1.plot(freqMhz, zdrDiff, label='zdrDiff(dB)', color='green', linewidth=1)
    ax2.plot(freqMhz, widthRatioDiff, label='widthRatioDiff', color='red', linewidth=1)
    ax3.plot(freqMhz, corr00, label='correlation', color='blue', linewidth=1)
    ax4.plot(freqMhz, S1S2, label='S1S2', color='black', linewidth=1)

    configFreqAxis(ax1, -9999, -9999, "Axis ZDR Diff(dB)", 'lower left')
    configFreqAxis(ax2, -9999, -9999, "Aspect Ratio Diff", 'lower left')
    configFreqAxis(ax3, -9999, -9999, "HV Correlation", 'lower left')
    configFreqAxis(ax4, -9999, -9999, "S1S2", 'lower left')

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.05, left=0.075, right=0.975, top=0.96)
    
    # title name

    fig.suptitle("SPOL SUNSCAN FREQUENCY DEPENDENCE - " + str(startTime) + " to " + str(endTime))

    return

########################################################################
# Configure axes, legends etc

def configTimeAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=8)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
        ax.set_xlabel("Time")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
    hfmt = dates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_locator(dates.AutoDateLocator())
    ax.xaxis.set_major_formatter(hfmt)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8) 

    ax.set_xlim(startTime, endTime)

########################################################################
# Configure axes, legends etc

def configFreqAxis(ax, miny, maxy, ylabel, legendLoc):
    
    legend = ax.legend(loc=legendLoc, ncol=8)
    for label in legend.get_texts():
        label.set_fontsize('x-small')
        ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])

    minx = 2690.0
    maxx = 2875.0

    ax.xaxis.set_ticks(np.arange(minx, maxx, 10))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(10) 
        
    ax.set_xlim(minx, maxx)

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
# Run - entry point

if __name__ == "__main__":
   main()

