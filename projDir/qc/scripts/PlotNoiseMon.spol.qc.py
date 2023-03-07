#!/usr/bin/env python

#===========================================================================
#
# Produce plots for noise mon data by time
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
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--noiseFile',
                      dest='noiseFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/noise_mon/sband/tables/noise_mon.sband.txt',
                      help='File path for noise monitoring')
    parser.add_option('--vertFile',
                      dest='vertFilePath',
                      default='/scr/cirrus3/rsfdata/projects/precip/calibration/spol/vert/sband/tables/vert.sband.txt',
                      help='VertCompute results file path')
    parser.add_option('--title',
                      dest='title',
                      default='ZDR BIAS FROM NOISE and VERT POINTING',
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
    parser.add_option('--noiseMin',
                      dest='noiseMin',
                      default=-77.0,
                      help='Min noise dbm in lower plot')
    parser.add_option('--noiseMax',
                      dest='noiseMax',
                      default=-74.0,
                      help='Max noise dbm in lower plot')
    parser.add_option('--statsStartTime',
                      dest='statsStartTime',
                      default='2022 05 25 03 00 00',
                      help='Start time for computing ZDR stats')
    parser.add_option('--statsEndTime',
                      dest='statsEndTime',
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
    parser.add_option('--tempMin',
                      dest='tempMin',
                      default=20.0,
                      help='Min temperature in plot')
    parser.add_option('--tempMax',
                      dest='tempMax',
                      default=35,
                      help='Max temperature in plot')

    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    global startTime
    global endTime

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    global statsStartTime
    global statsEndTime

    year, month, day, hour, minute, sec = options.statsStartTime.split()
    statsStartTime = datetime.datetime(int(year), int(month), int(day),
                                          int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.statsEndTime.split()
    statsEndTime = datetime.datetime(int(year), int(month), int(day),
                                        int(hour), int(minute), int(sec))

    if (options.debug):
        print("Running %prog", file=sys.stderr)
        print("  noiseFilePath: ", options.noiseFilePath, file=sys.stderr)
        print("  vertFilePath: ", options.vertFilePath, file=sys.stderr)
        print("  startTime: ", startTime, file=sys.stderr)
        print("  endTime: ", endTime, file=sys.stderr)
        print("  statsStartTime: ", statsStartTime, file=sys.stderr)
        print("  statsEndTime: ", statsEndTime, file=sys.stderr)

    # read in column headers for noise results

    global noiseHdrs, noiseData, noiseTimes
    iret, noiseHdrs, noiseData = readColumnHeaders(options.noiseFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for noise results

    noiseData, noiseTimes = readInputData(options.noiseFilePath, noiseHdrs, noiseData)

    # read in column headers for vert results

    global vertHdrs, vertData, vertTimes
    iret, vertHdrs, vertData = readColumnHeaders(options.vertFilePath)
    if (iret != 0):
        sys.exit(-1)

    # read in data for VERT results

    vertData, vertTimes = readInputData(options.vertFilePath, vertHdrs, vertData)

    # set the calibration receiver gains
    
    setCalData()
    
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
# Set calibration gain data

def setCalData():

    global calTimes, calHNoise, calVNoise, calHGain, calVGain
    
    calTimes =  [ datetime.datetime(2022, 5, 24,  12, 0, 0), \
                  datetime.datetime(2022, 6, 1, 12, 0, 0), \
                  datetime.datetime(2022, 6, 20,  12, 0, 0), \
                  datetime.datetime(2022, 6, 21,  12, 0, 0), \
                  datetime.datetime(2022, 6, 23,  12, 0, 0), \
                  datetime.datetime(2022, 7, 16,  12, 0, 0), \
                  datetime.datetime(2022, 7, 23,  12, 0, 0), \
                  datetime.datetime(2022, 8, 3,  12, 0, 0), \
                  datetime.datetime(2022, 8, 10,  12, 0, 0) ]

    calHNoise = [ -74.89, -74.91, -74.88, -74.88, -74.88, -75.12, -75.32, -75.58, -76.38 ]
    calVNoise = [ -75.12, -75.14, -75.14, -75.12, -75.08, -75.10, -74.97, -75.18, -75.05 ]
    calHGain = [ 40.20, 40.16, 40.27, 40.27, 40.10, 39.82, 39.44, 39.17, 38.36 ]
    calVGain = [ 39.46, 39.48, 39.48, 39.50, 39.49, 39.44, 39.44, 39.23, 39.48 ]

########################################################################
# Plot

def doPlot():

    fileName = options.noiseFilePath
    titleStr = "File: " + fileName
    hfmt = dates.DateFormatter('%y/%m/%d')

    lenMeanFilter = int(options.lenMean)

    # set up arrays for ZDR noise

    ntimes = np.array(noiseTimes).astype(datetime.datetime)
    vtimes = np.array(vertTimes).astype(datetime.datetime)
    
    meanNoiseZdr = np.array(noiseData["meanNoiseZdr"]).astype(np.double)
    meanNoiseZdrAv = movingAverage(meanNoiseZdr, lenMeanFilter)
    validMeanNoiseZdr = np.isfinite(meanNoiseZdrAv)
    validMeanNoiseZdrNtimes = ntimes[validMeanNoiseZdr]
    validMeanNoiseZdrVals = meanNoiseZdrAv[validMeanNoiseZdr]

    meanDbmhc = np.array(noiseData["meanDbmhc"]).astype(np.double)
    meanDbmhcAv = movingAverage(meanDbmhc, lenMeanFilter)
    validMeanDbmhc = np.isfinite(meanDbmhcAv)
    validMeanDbmhcNtimes = ntimes[validMeanDbmhc]
    validMeanDbmhcVals = meanDbmhcAv[validMeanDbmhc]
    
    meanDbmvc = np.array(noiseData["meanDbmvc"]).astype(np.double)
    meanDbmvcAv = movingAverage(meanDbmvc, lenMeanFilter)
    validMeanDbmvc = np.isfinite(meanDbmvcAv)
    validMeanDbmvcNtimes = ntimes[validMeanDbmvc]
    validMeanDbmvcVals = meanDbmvcAv[validMeanDbmvc]
    
    vertZdrm = np.array(vertData["meanZdrmVol"]).astype(np.double)
    vertZdrmAv = movingAverage(vertZdrm, lenMeanFilter)
    validVertZdrm = np.isfinite(vertZdrmAv)
    validVertZdrmVtimes = vtimes[validVertZdrm]
    validVertZdrmVals = vertZdrmAv[validVertZdrm]

    global tempsAvail
    tempsAvail = True
    try:
        
        tempSite = np.array(noiseData["WxStationTempC"]).astype(np.double)
        tempSiteAv = movingAverage(tempSite, lenMeanFilter)
        validTempSite = np.isfinite(tempSiteAv)
        validTempSiteNtimes = ntimes[validTempSite]
        validTempSiteVals = tempSiteAv[validTempSite]

        tempDish = np.array(noiseData["DishTempMeanC"]).astype(np.double)
        tempDishAv = movingAverage(tempDish, lenMeanFilter)
        validTempDish = np.isfinite(tempDishAv)
        validTempDishNtimes = ntimes[validTempDish]
        validTempDishVals = tempDishAv[validTempDish]

        tempTrans = np.array(noiseData["AzTransTempC"]).astype(np.double)
        tempTransAv = movingAverage(tempTrans, lenMeanFilter)
        validTempTrans = np.isfinite(tempTransAv)
        validTempTransNtimes = ntimes[validTempTrans]
        validTempTransVals = tempTransAv[validTempTrans]

        tempKlystron = np.array(noiseData["TempKlystronC"]).astype(np.double)
        tempKlystronAv = movingAverage(tempKlystron, lenMeanFilter)
        validTempKlystron = np.isfinite(tempKlystronAv)
        validTempKlystronNtimes = ntimes[validTempKlystron]
        validTempKlystronVals = tempKlystronAv[validTempKlystron]

        tempRx = np.array(noiseData["TempRxEnclosureC"]).astype(np.double)
        tempRxAv = movingAverage(tempRx, lenMeanFilter)
        validTempRx = np.isfinite(tempRxAv)
        validTempRxNtimes = ntimes[validTempRx]
        validTempRxVals = tempRxAv[validTempRx]

        tempLnaH = np.array(noiseData["TempLnaHC"]).astype(np.double)
        tempLnaHAv = movingAverage(tempLnaH, lenMeanFilter)
        validTempLnaH = np.isfinite(tempLnaHAv)
        validTempLnaHNtimes = ntimes[validTempLnaH]
        validTempLnaHVals = tempLnaHAv[validTempLnaH]

        tempLnaV = np.array(noiseData["TempLnaVC"]).astype(np.double)
        tempLnaVAv = movingAverage(tempLnaV, lenMeanFilter)
        validTempLnaV = np.isfinite(tempLnaVAv)
        validTempLnaVNtimes = ntimes[validTempLnaV]
        validTempLnaVVals = tempLnaVAv[validTempLnaV]

    except KeyError as e:
        tempsAvail = False

    # compute the mean noise zdr and vert zdr for the stats time period

    statsNoiseZdr = meanNoiseZdr[np.logical_and(ntimes >= statsStartTime,
                                                ntimes <= statsEndTime)]
    statsVertZdrm = vertZdrm[np.logical_and(vtimes >= statsStartTime,
                                            vtimes <= statsEndTime)]
    noiseZdrStatsMean = np.mean(statsNoiseZdr)
    vertZdrmStatsMean = np.mean(statsVertZdrm)
    noiseToZdrCorr = vertZdrmStatsMean - noiseZdrStatsMean
    # noiseZdrValsCorr = meanNoiseZdrAv[validMeanNoiseZdr] + noiseToZdrCorr
    
    if (tempsAvail):
        statsTempSite = tempSite[np.logical_and(ntimes >= statsStartTime,
                                                ntimes <= statsEndTime)]
        tempSiteMean = np.mean(statsTempSite)

    if (options.debug):
        print("  ==>> noiseZdrStatsMean: ", noiseZdrStatsMean, file=sys.stderr)
        print("  ==>> vertZdrmStatsMean: ", vertZdrmStatsMean, file=sys.stderr)
        print("  ==>>    noiseToZdrCorr: ", noiseToZdrCorr, file=sys.stderr)
        if (tempsAvail):
            print("  ==>>    tempSiteMean: ", tempSiteMean, file=sys.stderr)

    # set up plots

    widthIn = float(options.figWidthMm) / 25.4
    htIn = float(options.figHeightMm) / 25.4

    fig1 = plt.figure(1, (widthIn, htIn))
    if (tempsAvail):
        fig2 = plt.figure(2, (widthIn/2, htIn/2))
        # fig3 = plt.figure(3, (widthIn/2, htIn/2))

    if (tempsAvail):
        ax1a = fig1.add_subplot(3,1,1,xmargin=0.0)
        ax1b = fig1.add_subplot(3,1,2,xmargin=0.0)
        ax1c = fig1.add_subplot(3,1,3,xmargin=0.0)
    else:
        ax1a = fig1.add_subplot(2,1,1,xmargin=0.0)
        ax1b = fig1.add_subplot(2,1,2,xmargin=0.0)

    if (tempsAvail):
        ax2a = fig2.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)
        # ax3a = fig3.add_subplot(1,1,1,xmargin=1.0, ymargin=1.0)

    oneDay = datetime.timedelta(1.0)

    ax1a.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1a.set_title("ZDRm (dB)")
    ax1b.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
    ax1b.set_title("Mean Noise Power (dBm)")
    ax1br = ax1b.twinx()

    if (tempsAvail):
        ax1c.set_xlim([ntimes[0] - oneDay, ntimes[-1] + oneDay])
        ax1c.set_title("Temperatures (C)")

    if (tempsAvail):
        # add linear regression plot of ZDR bias vs temp
        (zdrmSlope, zdrmIntercept) = \
            addVertZdrmTempRegrPlot(ax2a,
                                    ntimes, validVertZdrmVtimes,
                                    validVertZdrmVals, tempSite)
        if (options.debug):
            print("  ==>> zdrmSlope, zdrmIntercept: ",
                  zdrmSlope, zdrmIntercept, file=sys.stderr)
        # add linear regression plot of measured noise vs rx temp
        #addMeasNoisRxTempRegrPlot(ax3a,
        #                          ntimes, validTempRxNtimes,
        #                          validMeanDbmvcVals, tempRx)

        #noiseZdrValsCorr2 = noiseZdrValsCorr + (tempSite - tempSiteMean) * zdrmSlope

    ax1a.plot(validVertZdrmVtimes, validVertZdrmVals, \
              ".", label = 'Vert ZDRm', color='green')
    ax1a.plot(validMeanNoiseZdrNtimes, validMeanNoiseZdrVals, \
              label = 'Mean Noise ZDRm', linewidth=1, color='black')
    # ax1a.plot(validMeanNoiseZdrNtimes, noiseZdrValsCorr2, \
        # label = 'ZdrmTempCorr', linewidth=1, color='orange')
    #ax1a.plot(validMeanNoiseZdrNtimes, noiseZdrValsCorr, \
    #          label = 'NoiseZdr+noiseToZdrCorr', linewidth=1, color='brown')

    ax1b.plot(validMeanDbmhcNtimes, validMeanDbmhcVals, \
              label = 'Mean Noise Dbmhc', linewidth=1, color='red')
    ax1b.plot(validMeanDbmvcNtimes, validMeanDbmvcVals, \
              label = 'Mean Noise Dbmvc', linewidth=1, color='blue')
    
    ax1br.plot(calTimes, calHGain, \
               "^", label = 'Cal H Gain', linewidth=1, color='red', markersize=8)
    ax1br.plot(calTimes, calVGain, \
               "^", label = 'Cal V Gain', linewidth=1, color='blue', markersize=8)
    
    #ax1c.plot(validTempDishNtimes, validTempDishVals, \
    #          label = 'Temp dish (C)', linewidth=1, color='brown')
    #ax1c.plot(validTempTransNtimes, validTempTransVals, \
    #          label = 'Temp trans (C)', linewidth=1, color='pink')

    if (tempsAvail):
        ax1c.plot(validTempKlystronNtimes, validTempKlystronVals, \
                  label = 'Temp Klystron (C)', linewidth=1, color= 'yellow')
        ax1c.plot(validTempLnaVNtimes, validTempLnaVVals, \
                  label = 'Temp Lna V (C)', linewidth=1, color= 'cyan')
        ax1c.plot(validTempLnaHNtimes, validTempLnaHVals, \
                  label = 'Temp Lna H (C)', linewidth=1, color='darkgreen')
        ax1c.plot(validTempRxNtimes, validTempRxVals, \
                  label = 'Temp Rx (C)', linewidth=1, color='blue')
        ax1c.plot(validTempSiteNtimes, validTempSiteVals, \
                  label = 'Temp site (C)', linewidth=1, color='red')
    
    #configDateAxis(ax1a, -9999, -9999, "Noise ZDR (dB)", 'upper right')
    configDateAxis(ax1a,
                   float(options.zdrMin), float(options.zdrMax),
                   "ZDRm (dB)", 'upper right')
    #configDateAxis(ax1b, -9999, -9999, "Noise Power (dBm)", 'upper right')
    configDateAxis(ax1b,
                   float(options.noiseMin), float(options.noiseMax),
                   "Noise Power (dBm)", 'upper right')
    configDateAxis(ax1br, 38.0, 40.5, "Receiver gains", 'upper left')
    if (tempsAvail):
        configDateAxis(ax1c,
                       float(options.tempMin), float(options.tempMax),
                       "Temperatures (C)", 'upper right')

    # add text labels

    label1 = "Stats start: " + statsStartTime.strftime('%Y-%m-%d')    
    label2 = "Stats end: " + statsEndTime.strftime('%Y-%m-%d')    
    label3 = "Ntimes smooth: " + str(options.lenMean)

    label4 = "noiseZdrMean: " + ("%.2f" % noiseZdrStatsMean)
    label5 = "vertZdrmMean: " + ("%.2f" % vertZdrmStatsMean)
    label6 = "noiseToZdrCorr: " + ("%.2f" % noiseToZdrCorr)

    label7 = ""
    if (tempsAvail):
        label7 = "tempSiteMean: " + ("%.2f" % tempSiteMean)

    ax1a.set_facecolor("lightgrey")
    ax1b.set_facecolor("lightgrey")
    if (tempsAvail):
        ax1c.set_facecolor("lightgrey")

    # text on upper plot
    
    fig1.text(0.06, 0.97, label1)
    fig1.text(0.20, 0.97, label2)

    fig1.text(0.06, 0.95, label3)
    fig1.text(0.20, 0.95, label6)

    fig1.text(0.06, 0.93, label5)
    fig1.text(0.20, 0.93, label4)

    if (tempsAvail):
        fig1.text(0.20, 0.91, label7)

    fig1.autofmt_xdate()
    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.08, left=0.06, right=0.94, top=0.90)

    fig1.suptitle(options.title)

    # show
    
    plt.show()


########################################################################
# add regression plot of vert-based zdrm vs site temp

def addVertZdrmTempRegrPlot(ax,
                            ntimes, validVertZdrmVtimes,
                            validVertZdrmVals, tempSite):

    # linear regression of ZDR bias vs temp

    tempVals = []
    zdrmVals = []

    for ii, zdrmVal in enumerate(validVertZdrmVals, start=0):
        zdrmTime = validVertZdrmVtimes[ii]
        if (zdrmTime >= statsStartTime and zdrmTime <= statsEndTime):
            tempTime, tempVal = getClosestTemp(zdrmTime, ntimes, tempSite)
            if (np.isfinite(tempVal)):
                tempVals.append(tempVal)
                zdrmVals.append(zdrmVal)
                if (options.verbose):
                    print("==>> zdrmTime, zdrmVal, tempTime, tempVal:", \
                          zdrmTime, zdrmVal, tempTime, tempVal, file=sys.stderr)

    A = array([tempVals, ones(len(tempVals))])
    # obtaining the fit, ww[0] is slope, ww[1] is intercept
    ww = linalg.lstsq(A.T, zdrmVals, rcond=None)[0]
    regrX = []
    regrY = []

    minTemp = min(tempVals)
    maxTemp = max(tempVals)
    minZdrm = min(zdrmVals)
    maxZdrm = max(zdrmVals)

    regrX.append(minTemp)
    regrX.append(maxTemp)
    regrY.append(ww[0] * minTemp + ww[1])
    regrY.append(ww[0] * maxTemp + ww[1])
    
    # temperature-based regression
    
    label = "ZDRM = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
    ax.plot(tempVals, zdrmVals, 
              ".", label = label, color = 'lightblue')
    ax.plot(regrX, regrY, linewidth=3, color = 'blue')
    
    legend = ax.legend(loc="upper left", ncol=2)
    for label in legend.get_texts():
        label.set_fontsize(12)
    ax.set_xlabel("Site temperature (C)")
    ax.set_ylabel("ZDRM Bias (dB)")
    ax.grid(True)
    ax.set_ylim([minZdrm - 0.1, maxZdrm + 0.1])
    ax.set_xlim([minTemp - 1, maxTemp + 1])
    title = "ZDRM bias Vs Site temp: " + str(statsStartTime) + " - " + str(statsEndTime)
    ax.set_title(title)

    return (ww[0], ww[1])

########################################################################
# add regression plot of measured noise vs rx temp

def addMeasNoisRxTempRegrPlot(ax,
                              ntimes, validTempRxNtimes,
                              validMeanDbmvcVals, tempRx):
    
    # linear regression of V channel noise vs rx temp
    
    tempVals = []
    rxNoiseVals = []

    for ii, rxVal in enumerate(validMeanDbmvcVals, start=0):
        rxTime = validTempRxNtimes[ii]
        if (rxTime >= statsStartTime and rxTime <= statsEndTime):
            tempTime, tempVal = getClosestTemp(rxTime, ntimes, tempRx)
            if (np.isfinite(tempVal)):
                tempVals.append(tempVal)
                rxNoiseVals.append(rxVal)
                if (options.verbose):
                    print("==>> rxTime, rxVal, tempTime, tempVal:", \
                          rxTime, rxVal, tempTime, tempVal, file=sys.stderr)

    A = array([tempVals, ones(len(tempVals))])
    # obtaining the fit, ww[0] is slope, ww[1] is intercept
    ww = linalg.lstsq(A.T, rxNoiseVals, rcond=None)[0]
    regrX = []
    regrY = []
    minTemp = min(tempVals)
    maxTemp = max(tempVals)
    minNoise = min(rxNoiseVals)
    maxNoise = max(rxNoiseVals)
    regrX.append(minTemp)
    regrX.append(maxTemp)
    regrY.append(ww[0] * minTemp + ww[1])
    regrY.append(ww[0] * maxTemp + ww[1])
    
    # temperature-based regression
    
    label = "RxNoiseV = " + ("%.5f" % ww[0]) + " * temp + " + ("%.3f" % ww[1])
    ax.plot(tempVals, rxNoiseVals, 
              ".", label = label, color = 'lightblue')
    ax.plot(regrX, regrY, linewidth=3, color = 'blue')
    
    legend = ax.legend(loc="upper left", ncol=2)
    for label in legend.get_texts():
        label.set_fontsize(12)
    ax.set_xlabel("Rx temperature (C)")
    ax.set_ylabel("Rx V Noise (dBm)")
    ax.grid(True)
    ax.set_ylim([minNoise - 0.1, maxNoise + 0.1])
    ax.set_xlim([minTemp - 1, maxTemp + 1])
    title = "RxNoiseV vs Rx temp: " + str(statsStartTime) + " - " + str(statsEndTime)
    ax.set_title(title)

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

