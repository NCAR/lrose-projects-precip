#!/usr/bin/env python

#===========================================================================
#
# Produce plots for clut mon data by time
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
    global pulseShaperChangeTime1
    global pulseShaperChangeTime2

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
    parser.add_option('--clutFile',
                      dest='clutFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/clut_mon/sband/tables/clut_mon.sband.txt',
                      help='File path for clutter monitoring')
    parser.add_option('--vertFile',
                      dest='vertFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/vert/sband/tables/vert.sband.txt',
                      help='VertCompute results file path')
    parser.add_option('--title',
                      dest='title',
                      default='CLUTTER AND TRANSMITTER POWER MONITORING',
                      help='Title for plot')
    parser.add_option('--width',
                      dest='figWidthMm',
                      default=400,
                      help='Width of figure in mm')
    parser.add_option('--height',
                      dest='figHeightMm',
                      default=300,
                      help='Height of figure in mm')
    parser.add_option('--lenMean',
                      dest='lenMean',
                      default=1,
                      help='Len of moving mean filter')
    parser.add_option('--startTime',
                      dest='startTime',
                      default='2022 05 25 03 00 00',
                      help='Start time for XY plot')
    parser.add_option('--endTime',
                      dest='endTime',
                      default='2022 08 11 00 00 00',
                      help='End time for XY plot')
    parser.add_option('--pulseShaperChangeTime1',
                      dest='pulseShaperChangeTime1',
                      default='2022 06 21 04 00 00',
                      help='First pulse shaper change')
    parser.add_option('--pulseShaperChangeTime2',
                      dest='pulseShaperChangeTime2',
                      default='2022 07 08 04 00 00',
                      help='Second pulse shaper change')
    parser.add_option('--zdrMin',
                      dest='zdrMin',
                      default=-2.0,
                      help='Min zdr in upper plot')
    parser.add_option('--zdrMax',
                      dest='zdrMax',
                      default=2.0,
                      help='Max zdr in upper plot')
    parser.add_option('--clutMin',
                      dest='clutMin',
                      default=-50.0,
                      help='Min clut dbm in lower plot')
    parser.add_option('--clutMax',
                      dest='clutMax',
                      default=5.0,
                      help='Max clut dbm in lower plot')
    parser.add_option('--xmitPwrMin',
                      dest='xmitPwrMin',
                      default=82.0,
                      help='Min xmit power')
    parser.add_option('--xmitPwrMax',
                      dest='xmitPwrMax',
                      default=90.0,
                      help='Max xmit power')
    parser.add_option('--dbzMin',
                      dest='dbzMin',
                      default=47.0,
                      help='Min clutter dbz')
    parser.add_option('--dbzMax',
                      dest='dbzMax',
                      default=55.0,
                      help='Max clutter dbz')

    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.pulseShaperChangeTime1.split()
    pulseShaperChangeTime1 = datetime.datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.pulseShaperChangeTime2.split()
    pulseShaperChangeTime2 = datetime.datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running %prog", file=sys.stderr)
        print("  clutFilePath: ", options.clutFilePath, file=sys.stderr)
        print("  vertFilePath: ", options.vertFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  pulseShaperChangeTime1: ", pulseShaperChangeTime1, file=sys.stderr)
        print("  pulseShaperChangeTime2: ", pulseShaperChangeTime2, file=sys.stderr)

    # read in column headers for clut results

    global clutHdrs, clutData, clutTimes
    iret, clutHdrs, clutData = readColumnHeaders(options.clutFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for clut results

    clutData, clutTimes = readInputData(options.clutFilePath, clutHdrs, clutData)

    # read in column headers for vert results

    global vertHdrs, vertData, vertTimes
    iret, vertHdrs, vertData = readColumnHeaders(options.vertFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for VERT results

    vertData, vertTimes = readInputData(options.vertFilePath, vertHdrs, vertData)

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

    fileName = options.clutFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR clut

    ntimes = np.array(clutTimes).astype(datetime.datetime)
    vtimes = np.array(vertTimes).astype(datetime.datetime)
    
    meanDbzStrong = np.array(clutData["meanDbzStrong"]).astype(np.double)
    meanDbzStrong[meanDbzStrong > 54] = math.nan;
    meanDbzStrongAv = movingAverage(meanDbzStrong, lenMeanFilter)
    validMeanDbzStrong = np.isfinite(meanDbzStrongAv)
    validMeanDbzStrongNtimes = ntimes[validMeanDbzStrong]
    validMeanDbzStrongVals = meanDbzStrongAv[validMeanDbzStrong]

    meanDbmhcStrong = np.array(clutData["meanDbmhcStrong"]).astype(np.double)
    meanDbmhcStrongAv = movingAverage(meanDbmhcStrong, lenMeanFilter)
    validMeanDbmhcStrong = np.isfinite(meanDbmhcStrongAv)
    validMeanDbmhcStrongNtimes = ntimes[validMeanDbmhcStrong]
    validMeanDbmhcStrongVals = meanDbmhcStrongAv[validMeanDbmhcStrong]

    meanDbmvcStrong = np.array(clutData["meanDbmvcStrong"]).astype(np.double)
    meanDbmvcStrongAv = movingAverage(meanDbmvcStrong, lenMeanFilter)
    validMeanDbmvcStrong = np.isfinite(meanDbmvcStrongAv)
    validMeanDbmvcStrongNtimes = ntimes[validMeanDbmvcStrong]
    validMeanDbmvcStrongVals = meanDbmvcStrongAv[validMeanDbmvcStrong]

    meanZdrStrong = np.array(clutData["meanZdrStrong"]).astype(np.double)
    meanZdrStrongAv = movingAverage(meanZdrStrong, lenMeanFilter)
    validMeanZdrStrong = np.isfinite(meanZdrStrongAv)
    validMeanZdrStrongNtimes = ntimes[validMeanZdrStrong]
    validMeanZdrStrongVals = meanZdrStrongAv[validMeanZdrStrong]

    meanDbzWeak = np.array(clutData["meanDbzWeak"]).astype(np.double)
    meanDbzWeakAv = movingAverage(meanDbzWeak, lenMeanFilter)
    validMeanDbzWeak = np.isfinite(meanDbzWeakAv)
    validMeanDbzWeakNtimes = ntimes[validMeanDbzWeak]
    validMeanDbzWeakVals = meanDbzWeakAv[validMeanDbzWeak]

    meanDbmhcWeak = np.array(clutData["meanDbmhcWeak"]).astype(np.double)
    meanDbmhcWeakAv = movingAverage(meanDbmhcWeak, lenMeanFilter)
    validMeanDbmhcWeak = np.isfinite(meanDbmhcWeakAv)
    validMeanDbmhcWeakNtimes = ntimes[validMeanDbmhcWeak]
    validMeanDbmhcWeakVals = meanDbmhcWeakAv[validMeanDbmhcWeak]

    meanDbmvcWeak = np.array(clutData["meanDbmvcWeak"]).astype(np.double)
    meanDbmvcWeakAv = movingAverage(meanDbmvcWeak, lenMeanFilter)
    validMeanDbmvcWeak = np.isfinite(meanDbmvcWeakAv)
    validMeanDbmvcWeakNtimes = ntimes[validMeanDbmvcWeak]
    validMeanDbmvcWeakVals = meanDbmvcWeakAv[validMeanDbmvcWeak]

    meanZdrWeak = np.array(clutData["meanZdrWeak"]).astype(np.double)
    meanZdrWeakAv = movingAverage(meanZdrWeak, lenMeanFilter)
    validMeanZdrWeak = np.isfinite(meanZdrWeakAv)
    validMeanZdrWeakNtimes = ntimes[validMeanZdrWeak]
    validMeanZdrWeakVals = meanZdrWeakAv[validMeanZdrWeak]

    XmitPowerDbmBoth = np.array(clutData["XmitPowerDbmBoth"]).astype(np.double)
    XmitPowerDbmBoth[XmitPowerDbmBoth < 85] = math.nan;
    XmitPowerDbmBothAv = movingAverage(XmitPowerDbmBoth, lenMeanFilter)
    validXmitPowerDbmBoth = np.isfinite(XmitPowerDbmBothAv)
    validXmitPowerDbmBothNtimes = ntimes[validXmitPowerDbmBoth]
    validXmitPowerDbmBothVals = XmitPowerDbmBothAv[validXmitPowerDbmBoth]

    XmitPowerDbmH = np.array(clutData["XmitPowerDbmH"]).astype(np.double)
    XmitPowerDbmH[XmitPowerDbmH < 82] = math.nan;
    XmitPowerDbmHAv = movingAverage(XmitPowerDbmH, lenMeanFilter)
    validXmitPowerDbmH = np.isfinite(XmitPowerDbmHAv)
    validXmitPowerDbmHNtimes = ntimes[validXmitPowerDbmH]
    validXmitPowerDbmHVals = XmitPowerDbmHAv[validXmitPowerDbmH]

    XmitPowerDbmV = np.array(clutData["XmitPowerDbmV"]).astype(np.double)
    XmitPowerDbmV[XmitPowerDbmV < 82] = math.nan;
    XmitPowerDbmVAv = movingAverage(XmitPowerDbmV, lenMeanFilter)
    validXmitPowerDbmV = np.isfinite(XmitPowerDbmVAv)
    validXmitPowerDbmVNtimes = ntimes[validXmitPowerDbmV]
    validXmitPowerDbmVVals = XmitPowerDbmVAv[validXmitPowerDbmV]

    PulseWidthUs = np.array(clutData["pulseWidthUsec"]).astype(np.double)
    PulseWidthUsAv = movingAverage(PulseWidthUs, lenMeanFilter)
    validPulseWidthUs = np.isfinite(PulseWidthUsAv)
    validPulseWidthUsNtimes = ntimes[validPulseWidthUs]
    validPulseWidthUsVals = PulseWidthUsAv[validPulseWidthUs]

    meanDbmhc = meanDbmhcStrong - 10.0 * np.log10(PulseWidthUs)
    meanDbmhcAv = movingAverage(meanDbmhc, lenMeanFilter)
    validMeanDbmhc = np.isfinite(meanDbmhcAv)
    validMeanDbmhcNtimes = ntimes[validMeanDbmhc]
    validMeanDbmhcVals = meanDbmhcAv[validMeanDbmhc]

    meanDbmvc = meanDbmvcStrong - 10.0 * np.log10(PulseWidthUs)
    meanDbmvcAv = movingAverage(meanDbmvc, lenMeanFilter)
    validMeanDbmvc = np.isfinite(meanDbmvcAv)
    validMeanDbmvcNtimes = ntimes[validMeanDbmvc]
    validMeanDbmvcVals = meanDbmvcAv[validMeanDbmhc]

    vertZdrm = np.array(vertData["meanZdrmVol"]).astype(np.double)
    vertZdrmAv = movingAverage(vertZdrm, lenMeanFilter)
    validVertZdrm = np.isfinite(vertZdrmAv)
    validVertZdrmVtimes = vtimes[validVertZdrm]
    validVertZdrmVals = vertZdrmAv[validVertZdrm]

    # compute the mean clut dbz for each pulse shaper interval

    meanDbzShaper0 = np.nanmean(meanDbzStrong[np.logical_and(ntimes >= startTime,
                                                             ntimes <= pulseShaperChangeTime1)])
    meanDbzShaper1 = np.nanmean(meanDbzStrong[np.logical_and(ntimes >= pulseShaperChangeTime1,
                                                             ntimes <= pulseShaperChangeTime2)])
    meanDbzShaper2 = np.nanmean(meanDbzStrong[np.logical_and(ntimes >= pulseShaperChangeTime2,
                                                             ntimes <= endTime)])
    meanDbzShaper01 = np.nanmean(meanDbzStrong[np.logical_and(ntimes >= startTime,
                                                              ntimes <= pulseShaperChangeTime2)])
    if (options.debug):
        print("  ==>> meanDbzShaper0: ", meanDbzShaper0, file=sys.stderr)
        print("  ==>> meanDbzShaper1: ", meanDbzShaper1, file=sys.stderr)
        print("  ==>> meanDbzShaper2: ", meanDbzShaper2, file=sys.stderr)
        print("  ==>> meanDbzShaper01: ", meanDbzShaper01, file=sys.stderr)

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(3,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(3,1,2,xmargin=0.0)
    ax1br = ax1b.twinx()
    ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)

    #    ax1a.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    #    ax1a.set_title("ZDR (dB)")
    #    ax1b.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    #    ax1b.set_title("Clut Power (dBZ)")
    #    ax1c.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    #    ax1c.set_title("XmitPower Power (dBm)")

    ax1a.set_xlim([startTime - oneDay, endTime + oneDay])
    ax1a.set_title("Received clutter ZDR (dB)")
    ax1b.set_xlim([startTime - oneDay, endTime + oneDay])
    ax1b.set_title("Received clutter power corrected for pulse width (dBm)")
    ax1c.set_xlim([startTime - oneDay, endTime + oneDay])
    ax1c.set_title("Measured XmitPower power (dBm)")

    ax1a.plot(validMeanZdrStrongNtimes, validMeanZdrStrongVals, \
              linewidth=1, label = 'ZDR Clutter (dB)', color='blue')

    #ax1a.plot(validMeanZdrWeakNtimes, validMeanZdrWeakVals, \
    #          linewidth=1, label = 'ZDR Weak (dB)', color='red')
    
    #ax1b.plot(validMeanDbmhcStrongNtimes, validMeanDbmhcStrongVals, \
    #          '.', label = 'Mean Dbmhc Clut (dBm)', color='red')

    #ax1b.plot(validMeanDbmvcStrongNtimes, validMeanDbmvcStrongVals, \
    #          label = 'Mean Dbmvc Clut (dBm)', linewidth=2, color='blue')

    ax1b.plot(validMeanDbmhcNtimes, validMeanDbmhcVals, \
              '.', label = 'Dbmhc Corr (dBm)', color='red')

    ax1b.plot(validMeanDbmvcNtimes, validMeanDbmvcVals, \
              label = 'Dbmvc Corr (dBm)', linewidth=2, color='blue')

    ax1br.plot(validMeanDbzStrongNtimes, validMeanDbzStrongVals, \
               label = 'Dbz (dBZ)', linewidth=2, color='green')

    #ax1b.plot(validMeanDbmhcWeakNtimes, validMeanDbmhcWeakVals, \
    #          label = 'Mean Dbmhc Weak (dBm)', linewidth=1, color='red')
    #ax1b.plot(validMeanDbmvcWeakNtimes, validMeanDbmvcWeakVals, \
    #          label = 'Mean Dbmvc Weak (dBm)', linewidth=1, color='brown')

    ax1c.plot(validXmitPowerDbmBothNtimes, validXmitPowerDbmBothVals, \
              label = 'Xmit Power Both (dBm)', linewidth=1, color='black')
    ax1c.plot(validXmitPowerDbmHNtimes, validXmitPowerDbmHVals, \
              '.', label = 'Xmit Power H (dBm)', color='red')
    ax1c.plot(validXmitPowerDbmVNtimes, validXmitPowerDbmVVals, \
              label = 'Xmit Power V (dBm)', linewidth=2, color='blue')

    #configDateAxis(ax1a, -9999, -9999, "Clut ZDR (dB)", 'upper right')
    configDateAxis(ax1a, float(options.zdrMin), float(options.zdrMax),
                   "ZDRm (dB)", 'upper right')
    #configDateAxis(ax1b, -9999, -9999, "Clut Power (dBm)", 'upper right')
    configDateAxis(ax1b, float(options.clutMin), float(options.clutMax),
                   "Clut Power (dBm)", 'upper right')
    configDateAxis(ax1br, float(options.dbzMin), float(options.dbzMax),
                   "DBZ", 'upper left')
    #configDateAxis(ax1c, -9999, -9999, "Xmit Power (dBm)", 'upper right')
    configDateAxis(ax1c, float(options.xmitPwrMin), float(options.xmitPwrMax),
                   "Xmit Power (dBm)", 'upper right')
    
    # add text labels

    label1 = "Pulse shaper change 1: " + pulseShaperChangeTime1.strftime('%Y-%m-%d')    
    label2 = "Pulse shaper change 2: " + pulseShaperChangeTime2.strftime('%Y-%m-%d')    
    label3 = "meanDbzShaper01: " + ("%.2f" % meanDbzShaper01)

    label4 = "meanDbzShaper0: " + ("%.2f" % meanDbzShaper0)
    label5 = "meanDbzShaper1: " + ("%.2f" % meanDbzShaper1)
    label6 = "meanDbzShaper2: " + ("%.2f" % meanDbzShaper2)
    
    plt.figtext(0.06, 0.95, label1)
    plt.figtext(0.06, 0.93, label2)
    plt.figtext(0.06, 0.91, label3)

    plt.figtext(0.25, 0.95, label4)
    plt.figtext(0.25, 0.93, label5)
    plt.figtext(0.25, 0.91, label6)

    ax1a.set_facecolor("lightgrey")
    ax1b.set_facecolor("lightgrey")
    ax1c.set_facecolor("lightgrey")

    fig1.autofmt_xdate()
    
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.97, top=0.90)

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
# get temp closest in time to the search time

def getClosestTemp(clutTime, tempTimes, obsTemps):

    twoHours = datetime.timedelta(0.0, 7200.0)

    validTimes = ((tempTimes > (clutTime - twoHours)) & \
                  (tempTimes < (clutTime + twoHours)))

    if (len(validTimes) < 1):
        return (clutTime, float('NaN'))
    
    searchTimes = tempTimes[validTimes]
    searchTemps = obsTemps[validTimes]

    if (len(searchTimes) < 1 or len(searchTemps) < 1):
        return (clutTime, float('NaN'))

    minDeltaTime = 1.0e99
    ttime = searchTimes[0]
    temp = searchTemps[0]
    for ii, temptime in enumerate(searchTimes, start=0):
        deltaTime = math.fabs((temptime - clutTime).total_seconds())
        if (deltaTime < minDeltaTime):
            minDeltaTime = deltaTime
            temp = searchTemps[ii]
            ttime = temptime

    return (ttime, temp)

########################################################################
# compute daily stats for a variable

def computeDailyStats(times, vals):

    dailyTimes = []
    dailyMeans = []

    nptimes = np.array(times).astype(datetime.datetime)
    npvals = np.array(vals).astype(np.double)

    validFlag = np.isfinite(npvals)
    timesValid = nptimes[validFlag]
    valsValid = npvals[validFlag]
    
    startTime = nptimes[0]
    endTime = nptimes[-1]
    
    startDate = datetime.datetime(startTime.year, startTime.month, startTime.day, 0, 0, 0)
    endDate = datetime.datetime(endTime.year, endTime.month, endTime.day, 0, 0, 0)

    oneDay = datetime.timedelta(1)
    halfDay = datetime.timedelta(0.5)
    
    thisDate = startDate
    while (thisDate < endDate + oneDay):
        
        nextDate = thisDate + oneDay
        result = []
        
        sum = 0.0
        sumDeltaTime = datetime.timedelta(0)
        count = 0.0
        for ii, val in enumerate(valsValid, start=0):
            thisTime = timesValid[ii]
            if (thisTime >= thisDate and thisTime < nextDate):
                sum = sum + val
                deltaTime = thisTime - thisDate
                sumDeltaTime = sumDeltaTime + deltaTime
                count = count + 1
                result.append(val)
        if (count > 5):
            mean = sum / count
            meanDeltaTime = datetime.timedelta(0, sumDeltaTime.total_seconds() / count)
            dailyMeans.append(mean)
            dailyTimes.append(thisDate + meanDeltaTime)
            # print >>sys.stderr, " daily time, meanStrong: ", dailyTimes[-1], meanStrong
            result.sort()
            
        thisDate = thisDate + oneDay

    return (dailyTimes, dailyMeans)


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

