#!/usr/bin/env python

#===========================================================================
#
# Produce plots for sun mon data by time
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
    parser.add_option('--sunFile',
                      dest='sunFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/sun_mon/sband/tables/sun_mon.sband.txt',
                      help='File path for sun monitoring')
    parser.add_option('--vertFile',
                      dest='vertFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/vert/sband/tables/vert.sband.txt',
                      help='VertCompute results file path')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR BIAS FROM SUN and VERT POINTING - RVP8',
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
                      default='2022 05 25 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='2022 08 12 00 00 00',
                      help='End time for XY plot')
    parser.add_option('--zdrStatsStartTime',
                      dest='zdrStatsStartTime',
                      default='2022 05 25 00 00 00',
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
    parser.add_option('--sunMin',
                      dest='sunMin',
                      default=-75.0,
                      help='Min sun dbm in lower plot')
    parser.add_option('--sunMax',
                      dest='sunMax',
                      default=-60.0,
                      help='Max sun dbm in lower plot')
    
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
        print("  sunFilePath: ", options.sunFilePath, file=sys.stderr)
        print("  vertFilePath: ", options.vertFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  zdrStatsStartTime: ", zdrStatsStartTime, file=sys.stderr)
        print("  zdrStatsEndTime: ", zdrStatsEndTime, file=sys.stderr)

    # read in column headers for sun results

    global sunHdrs, sunData, sunTimes
    iret, sunHdrs, sunData = readColumnHeaders(options.sunFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for sun results

    sunData, sunTimes = readInputData(options.sunFilePath, sunHdrs, sunData)

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
    return sma

########################################################################
# Plot

def doPlot():

    fileName = options.sunFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR sun

    ntimes = np.array(sunTimes).astype(datetime.datetime)
    vtimes = np.array(vertTimes).astype(datetime.datetime)
    
    measuredDbmHc = np.array(sunData["measuredDbmHc"]).astype(np.double)
    measuredDbmHcAv = movingAverage(measuredDbmHc, lenMeanFilter)

    measuredDbmVc = np.array(sunData["measuredDbmVc"]).astype(np.double)
    measuredDbmVcAv = movingAverage(measuredDbmVc, lenMeanFilter)

    validMeasuredDbm = np.logical_and(np.isfinite(measuredDbmHcAv),
                                      np.isfinite(measuredDbmVcAv))

    validMeasuredDbmNtimes = ntimes[validMeasuredDbm]
    validMeasuredDbmHcVals = measuredDbmHcAv[validMeasuredDbm]
    validMeasuredDbmVcVals = measuredDbmVcAv[validMeasuredDbm]
    
    sunZdrVals = validMeasuredDbmHcVals - validMeasuredDbmVcVals

    vertZdrm = np.array(vertData["meanZdrmVol"]).astype(np.double)
    vertZdrmAv = movingAverage(vertZdrm, lenMeanFilter)
    validVertZdrm = np.isfinite(vertZdrmAv)
    validVertZdrmNtimes = vtimes[validVertZdrm]
    validVertZdrmVals = vertZdrmAv[validVertZdrm]

    # compute the mean sun zdr and vert zdr for the stats time period

    statsDbmHc = measuredDbmHc[np.logical_and(ntimes >= zdrStatsStartTime,
                                              ntimes <= zdrStatsEndTime)]
    statsDbmVc = measuredDbmVc[np.logical_and(ntimes >= zdrStatsStartTime,
                                              ntimes <= zdrStatsEndTime)]
    statsSunZdr = statsDbmHc - statsDbmVc

    statsVertZdrm = vertZdrm[np.logical_and(vtimes >= zdrStatsStartTime,
                                            vtimes <= zdrStatsEndTime)]
    sunZdrStatsMean = np.mean(statsSunZdr)
    vertZdrmStatsMean = np.mean(statsVertZdrm)
    sunToZdrCorr = vertZdrmStatsMean - sunZdrStatsMean
    sunZdrValsCorr = sunZdrVals + sunToZdrCorr
    
    if (options.debug):
        print("  ==>> sunZdrStatsMean: ", sunZdrStatsMean, file=sys.stderr)
        print("  ==>> vertZdrmStatsMean: ", vertZdrmStatsMean, file=sys.stderr)
        print("  ==>> sunToZdrCorr: ", sunToZdrCorr, file=sys.stderr)

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)

    oneDay = datetime.timedelta(1.0)

    ax1a.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1a.set_title("ZDRm (dB)")
    ax1b.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1b.set_title("Sun Power (dBm)")

    ax1a.plot(validVertZdrmNtimes, validVertZdrmVals, \
              ".", label = 'Vert ZDRm', color='green')
    ax1a.plot(validMeasuredDbmNtimes, sunZdrVals, \
              label = 'Sun ZDRm', linewidth=1, color='black')
    ax1a.plot(validMeasuredDbmNtimes, sunZdrValsCorr, \
              label = 'Sun ZDRm + sunToZdrCorr', linewidth=1, color='brown')

    ax1b.plot(validMeasuredDbmNtimes, validMeasuredDbmHcVals, \
              label = 'Mean Sun DbmHc', linewidth=1, color='red')
    
    ax1b.plot(validMeasuredDbmNtimes, validMeasuredDbmVcVals, \
              label = 'Mean Sun DbmVc', linewidth=1, color='blue')
    
    #configDateAxis(ax1a, -9999, -9999, "Sun ZDR (dB)", 'upper right')
    configDateAxis(ax1a, float(options.zdrMin), float(options.zdrMax), "ZDRm (dB)", 'upper right')
    #configDateAxis(ax1b, -9999, -9999, "Sun Power (dBm)", 'upper right')
    configDateAxis(ax1b, float(options.sunMin), float(options.sunMax), "Sun Power (dBm)", 'upper right')

    # add text labels

    label1 = "Stats start: " + zdrStatsStartTime.strftime('%Y-%m-%d')    
    label2 = "Stats end: " + zdrStatsEndTime.strftime('%Y-%m-%d')    
    label3 = "Ntimes smooth: " + str(options.lenMean)

    label4 = "sunZdrMean: " + ("%.2f" % sunZdrStatsMean)
    label5 = "vertZdrMean: " + ("%.2f" % vertZdrmStatsMean)
    label6 = "sunToZdrCorr: " + ("%.2f" % sunToZdrCorr)

    plt.figtext(0.06, 0.95, label1)
    plt.figtext(0.06, 0.93, label2)
    plt.figtext(0.06, 0.91, label3)

    plt.figtext(0.2, 0.95, label4)
    plt.figtext(0.2, 0.93, label5)
    plt.figtext(0.2, 0.91, label6)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.97, top=0.90)

    fig1.suptitle(options.title)
    plt.show()

########################################################################
# Plot - backup

def doPlot0(noiseData, noiseTimes, vertData, vertTimes):

    fileName = options.noiseFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR noise

    btimes = np.array(noiseTimes).astype(datetime.datetime)
    
    # noiseIce = np.array(noiseData["ZdrInIceMean"]).astype(np.double)
    # noiseIce = movingAverage(noiseIce, lenMeanFilter)

    noiseIce = np.array(noiseData["ZdrInIcePerc25.00"]).astype(np.double)
    noiseIce = movingAverage(noiseIce, lenMeanFilter)
    validIce = np.isfinite(noiseIce)
    
    noiseIceM = np.array(noiseData["ZdrmInIcePerc25.00"]).astype(np.double)
    noiseIceM = movingAverage(noiseIceM, lenMeanFilter)
    validIceM = np.isfinite(noiseIceM)
    
    # noiseBragg = np.array(noiseData["ZdrInBraggMean"]).astype(np.double)
    # noiseBragg = movingAverage(noiseBragg, lenMeanFilter)

    noiseBragg = np.array(noiseData["ZdrInBraggPerc32.00"]).astype(np.double)
    noiseBragg = movingAverage(noiseBragg, lenMeanFilter)
    validBragg = np.isfinite(noiseBragg)

    noiseBraggM = np.array(noiseData["ZdrmInBraggPerc25.00"]).astype(np.double)
    noiseBraggM = movingAverage(noiseBraggM, lenMeanFilter)
    validBraggM = np.isfinite(noiseBraggM)
    
    validIceBtimes = btimes[validIce]
    validIceVals = noiseIce[validIce]
    
    validIceMBtimes = btimes[validIceM]
    validIceMVals = noiseIce[validIceM]
    
    validBraggBtimes = btimes[validBragg]
    validBraggVals = noiseBragg[validBragg]
    
    validBraggMBtimes = btimes[validBraggM]
    validBraggMVals = noiseBragg[validBraggM]
    
    # load up receiver gain etc - axis 4
    
    (dailyTimeIce, dailyValIce) = computeDailyStats(validIceBtimes, validIceVals)
    (dailyTimeBragg, dailyValBragg) = computeDailyStats(validBraggBtimes, validBraggVals)

    (dailyTimeIceM, dailyValIceM) = computeDailyStats(validIceMBtimes, validIceMVals)
    (dailyTimeBraggM, dailyValBraggM) = computeDailyStats(validBraggMBtimes, validBraggMVals)

    # site temp, vert pointing and sun scan results

    ctimes = np.array(vertTimes).astype(datetime.datetime)
    ZdrmVert = np.array(vertData["ZdrmVert"]).astype(np.double)
    validZdrmVert = np.isfinite(ZdrmVert)
    
    SunscanZdrm = np.array(vertData["SunscanZdrm"]).astype(np.double)
    validSunscanZdrm = np.isfinite(SunscanZdrm)

    verttimes = np.array(vertTimes).astype(datetime.datetime)
    tempSite = np.array(vertData["TempSite"]).astype(np.double)
    validTempSite = np.isfinite(tempSite)

    tempIceVals = []
    noiseIceVals = []

    for ii, noiseVal in enumerate(validIceVals, start=0):
        btime = validIceBtimes[ii]
        if (btime >= startTime and btime <= endTime):
            tempTime, tempVal = getClosestTemp(btime, verttimes, tempSite)
            if (np.isfinite(tempVal)):
                tempIceVals.append(tempVal)
                noiseIceVals.append(noiseVal)
                if (options.verbose):
                    print("==>> noiseTime, noiseVal, tempTime, tempVal:", \
                        btime, noiseVal, tempTime, tempVal, file=sys.stderr)

    # linear regression for noise vs temp

    A = array([tempIceVals, ones(len(tempIceVals))])

    if (len(tempIceVals) > 1):
        # obtain the fit, ww[0] is slope, ww[1] is intercept
        ww = linalg.lstsq(A.T, noiseIceVals)[0]
        minTemp = min(tempIceVals)
        maxTemp = max(tempIceVals)
        haveTemps = True
    else:
        ww = (1.0, 0.0)
        minTemp = 0.0
        maxTemp = 40.0
        haveTemps = False
        print("NOTE - no valid temp vs ZDR data for period", file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime  : ", endTime, file=sys.stderr)
        
    regrX = []
    regrY = []
    regrX.append(minTemp)
    regrX.append(maxTemp)
    regrY.append(ww[0] * minTemp + ww[1])
    regrY.append(ww[0] * maxTemp + ww[1])
    
    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))

    ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
    ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)
    #ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)

    if (haveTemps):
        fig2 = plt.figure(2, (widthIn/2, htIn/2))
        ax2a = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)
    ax1a.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1a.set_title("Residual ZDR noise in ice and Bragg, compared with VERT and VERT results (dB)")
    ax1b.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    ax1b.set_title("Daily mean ZDR noise in ice and Bragg (dB)")
    #ax1c.set_xlim([btimes[0] - oneDay, btimes[-1] + oneDay])
    #ax1c.set_title("Site temperature (C)")

    ax1a.plot(validBraggBtimes, validBraggVals, \
              "o", label = 'ZDR Noise In Bragg', color='blue')
    ax1a.plot(validBraggBtimes, validBraggVals, \
              label = 'ZDR Noise In Bragg', linewidth=1, color='blue')
    
    ax1a.plot(validIceBtimes, validIceVals, \
              "o", label = 'ZDR Noise In Ice', color='red')
    ax1a.plot(validIceBtimes, validIceVals, \
              label = 'ZDR Noise In Ice', linewidth=1, color='red')

    ax1a.plot(validBraggMBtimes, validBraggMVals, \
              "o", label = 'ZDRM Noise In Bragg', color='blue')
    ax1a.plot(validBraggMBtimes, validBraggMVals, \
              label = 'ZDRM Noise In Bragg', linewidth=1, color='blue')
    
    ax1a.plot(validIceMBtimes, validIceMVals, \
              "o", label = 'ZDRM Noise In Ice', color='red')
    ax1a.plot(validIceMBtimes, validIceMVals, \
              label = 'ZDRM Noise In Ice', linewidth=1, color='red')
    
    #ax1a.plot(ctimes[validSunscanZdrm], SunscanZdrm[validSunscanZdrm], \
    #          linewidth=2, label = 'Zdrm Sun/VERT (dB)', color = 'green')
    
    ax1a.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
              "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', color = 'yellow')

    ax1b.plot(dailyTimeBragg, dailyValBragg, \
              label = 'Daily Noise Bragg', linewidth=1, color='blue')
    ax1b.plot(dailyTimeBragg, dailyValBragg, \
              "^", label = 'Daily Noise Bragg', color='blue', markersize=10)

    ax1b.plot(dailyTimeIce, dailyValIce, \
              label = 'Daily Noise Ice', linewidth=1, color='red')
    ax1b.plot(dailyTimeIce, dailyValIce, \
              "^", label = 'Daily Noise Ice', color='red', markersize=10)
    ax1b.plot(ctimes[validZdrmVert], ZdrmVert[validZdrmVert], \
              "^", markersize=10, linewidth=1, label = 'Zdrm Vert (dB)', color = 'yellow')

    #ax1c.plot(vert times[validTempSite], tempSite[validTempSite], \
    #          linewidth=1, label = 'Site Temp', color = 'blue')
    
    #configDateAxis(ax1a, -9999, 9999, "ZDR Noise (dB)", 'upper right')
    configDateAxis(ax1a, -0.3, 0.7, "ZDR Noise (dB)", 'upper right')
    configDateAxis(ax1b, -0.5, 0.5, "ZDR Noise (dB)", 'upper right')
    #configDateAxis(ax1c, -9999, 9999, "Temp (C)", 'upper right')

    if (haveTemps):
        label3 = "ZDR Noise In Ice = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
        ax2a.plot(tempIceVals, noiseIceVals, 
                 "x", label = label3, color = 'blue')
        ax2a.plot(regrX, regrY, linewidth=3, color = 'blue')
    
        legend3 = ax2a.legend(loc="upper left", ncol=2)
        for label3 in legend3.get_texts():
            label3.set_fontsize(12)
            ax2a.set_xlabel("Site temperature (C)")
            ax2a.set_ylabel("ZDR Noise (dB)")
            ax2a.grid(True)
            ax2a.set_ylim([-0.5, 0.5])
            ax2a.set_xlim([minTemp - 1, maxTemp + 1])
            title3 = "ZDR Noise In Ice Vs Temp: " + str(startTime) + " - " + str(endTime)
            ax2a.set_title(title3)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.97, top=0.96)
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

