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
                      default='/scr/cirrus3/rsfdata/projects/precip/features/qc1/fieldBias/sur/tables/field_diffs.sur.txt',
                      help='File path for field biases')
    parser.add_option('--title',
                      dest='title',
                      default='FIELD BIASES computed from FixFieldVals app',
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
    parser.add_option('--zdrStatsStartTime',
                      dest='zdrStatsStartTime',
                      default='2022 05 25 03 00 00',
                      help='Start time for computing ZDR stats')
    parser.add_option('--zdrStatsEndTime',
                      dest='zdrStatsEndTime',
                      default='2022 07 09 00 00 00',
                      help='End time for computing ZDR stats')
    parser.add_option('--zdrMin',
                      dest='zdrMin',
                      default=-2.0,
                      help='Min zdr in upper plot')
    parser.add_option('--zdrMax',
                      dest='zdrMax',
                      default=2.0,
                      help='Max zdr in upper plot')
    
    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.zdrStatsStartTime.split()
    zdrStatsStartTime = datetime.datetime(int(year), int(month), int(day),
                                          int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.zdrStatsEndTime.split()
    zdrStatsEndTime = datetime.datetime(int(year), int(month), int(day),
                                        int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running %prog", file=sys.stderr)
        print("  biasFilePath: ", options.biasFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  zdrStatsStartTime: ", zdrStatsStartTime, file=sys.stderr)
        print("  zdrStatsEndTime: ", zdrStatsEndTime, file=sys.stderr)

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
    #dbzBiasAv[:int(lenMeanFilter/2)] = math.nan;
    #dbzBiasAv[int(-lenMeanFilter/2):] = math.nan;

    zdrBias = np.array(biasData["zdrDiff"]).astype(np.double)
    zdrBiasAv = movingAverage(zdrBias, lenMeanFilter)
    #zdrBiasAv[zdrBiasAv > 5] = math.nan;
    #zdrBiasAv[zdrBiasAv < -5] = math.nan;
    #zdrBiasAv[:int(lenMeanFilter/2)] = math.nan;
    #zdrBiasAv[int(-lenMeanFilter/2):] = math.nan;

    # measuredDbmVc = np.array(biasData["measuredDbmVc"]).astype(np.double)
    # measuredDbmVcAv = movingAverage(measuredDbmVc, lenMeanFilter)
    # measuredDbmVcAv[measuredDbmVcAv > -66] = math.nan;
    # measuredDbmVcAv[measuredDbmVcAv < -70] = math.nan;
    # measuredDbmVcAv[:int(lenMeanFilter/2)] = math.nan;
    # measuredDbmVcAv[int(-lenMeanFilter/2):] = math.nan;

    # validDbzBias = np.logical_and(np.isfinite(dbzBiasAv),
    #                               np.isfinite(measuredDbmVcAv))

    # validMeasuredDbmNtimes = ntimes[validMeasuredDbm]
    # validMeasuredDbmHcVals = dbzBiasAv[validMeasuredDbm]
    # validMeasuredDbmVcVals = measuredDbmVcAv[validMeasuredDbm]
    
    # biasZdrVals = validMeasuredDbmHcVals - validMeasuredDbmVcVals

    # vertZdrm = np.array(vertData["meanZdrmVol"]).astype(np.double)
    # vertZdrmAv = movingAverage(vertZdrm, lenMeanFilter)
    # validVertZdrm = np.isfinite(vertZdrmAv)
    # validVertZdrmNtimes = vtimes[validVertZdrm]
    # validVertZdrmVals = vertZdrmAv[validVertZdrm]

    # compute the mean bias zdr and vert zdr for the stats time period

    # statsDbmHc = dbzBias[np.logical_and(ntimes >= zdrStatsStartTime,
    #                                           ntimes <= zdrStatsEndTime)]
    # statsDbmVc = measuredDbmVc[np.logical_and(ntimes >= zdrStatsStartTime,
    #                                           ntimes <= zdrStatsEndTime)]
    # statsBiasZdr = statsDbmHc - statsDbmVc

    # statsVertZdrm = vertZdrm[np.logical_and(vtimes >= zdrStatsStartTime,
    #                                         vtimes <= zdrStatsEndTime)]
    # biasZdrStatsMean = np.mean(statsBiasZdr)
    # vertZdrmStatsMean = np.mean(statsVertZdrm)
    # biasToZdrCorr = vertZdrmStatsMean - biasZdrStatsMean
    # biasZdrValsCorr = biasZdrVals + biasToZdrCorr
    
    # if (options.debug):
    #     print("  ==>> biasZdrStatsMean: ", biasZdrStatsMean, file=sys.stderr)
    #     print("  ==>> vertZdrmStatsMean: ", vertZdrmStatsMean, file=sys.stderr)
    #     print("  ==>> biasToZdrCorr: ", biasToZdrCorr, file=sys.stderr)

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

    # ax1a.plot(validMeasuredDbmNtimes, biasZdrValsCorr, \
    #           label = 'Bias ZDRm + biasToZdrCorr', linewidth=1, color='brown')
    # ax1a.plot(validVertZdrmNtimes, validVertZdrmVals, \
    #           ".", label = 'Vert ZDRm', color='green')

    # ax1b.plot(validMeasuredDbmNtimes, validMeasuredDbmHcVals, \
    #           label = 'Mean Bias DbmHc', linewidth=1, color='red')
    
    # ax1b.plot(validMeasuredDbmNtimes, validMeasuredDbmVcVals, \
    #           label = 'Mean Bias DbmVc', linewidth=1, color='blue')
    
    configDateAxis(ax1a, -9999, -9999, "DBZ BIAS (dB)", 'upper right')
    #configDateAxis(ax1a, float(options.zdrMin), float(options.zdrMax), "ZDRm (dB)", 'upper right')
    configDateAxis(ax1b, -9999, -9999, "ZDR BIAS (dB)", 'upper right')
    #configDateAxis(ax1b, float(options.biasMin), float(options.biasMax), "Bias Power (dBm)", 'upper right')

    # add text labels

    # label1 = "Stats start: " + zdrStatsStartTime.strftime('%Y-%m-%d')    
    # label2 = "Stats end: " + zdrStatsEndTime.strftime('%Y-%m-%d')    
    # label3 = "Ntimes smooth: " + str(options.lenMean)

    # label4 = "biasZdrMean: " + ("%.2f" % biasZdrStatsMean)
    # label5 = "vertZdrMean: " + ("%.2f" % vertZdrmStatsMean)
    # label6 = "biasToZdrCorr: " + ("%.2f" % biasToZdrCorr)

    ax1a.set_facecolor("lightgrey")
    ax1b.set_facecolor("lightgrey")

    # plt.figtext(0.06, 0.95, label1)
    # plt.figtext(0.06, 0.93, label2)
    # plt.figtext(0.06, 0.91, label3)

    # plt.figtext(0.2, 0.95, label4)
    # plt.figtext(0.2, 0.93, label5)
    # plt.figtext(0.2, 0.91, label6)

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
# get temp closest in time to the search time

def getClosestTemp(noiseTime, tempTimes, obsTemps):

    twoHours = datetime.timedelta(0.0, 7200.0)

    validTimes = ((tempTimes > (noiseTime - twoHours)) & \
                  (tempTimes < (noiseTime + twoHours)))

    if (len(validTimes) < 1):
        return (noiseTime, float('NaN'))
    
    searchTimes = tempTimes[validTimes]
    searchTemps = obsTemps[validTimes]

    if (len(searchTimes) < 1 or len(searchTemps) < 1):
        return (noiseTime, float('NaN'))

    minDeltaTime = 1.0e99
    ttime = searchTimes[0]
    temp = searchTemps[0]
    for ii, temptime in enumerate(searchTimes, start=0):
        deltaTime = math.fabs((temptime - noiseTime).total_seconds())
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

