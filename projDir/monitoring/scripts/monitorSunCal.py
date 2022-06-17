#!/usr/bin/env python3

#===========================================================================
#
# Make plots to monitor S-Pol sunCal data
#
#===========================================================================

import sys
from optparse import OptionParser
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import matplotlib.pylab as pl
import matplotlib.ticker as ticker
from matplotlib import dates
import datetime
import pathlib
#from matplotlib.dates import DateFormatter
import pandas as pd

#from bokeh.plotting import figure, output_file, show
#from bokeh.layouts import row

def main():

    # globals

    global options
    global debug
    global startTime
    global endTime
    global timeLimitsSet
    timeLimitsSet = False
    global figNum
    figNum = 0
    
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
    parser.add_option('--suncalFile',
                      dest='suncalFile',
                      default='/scr/sleet1/rsfdata/projects/eolbase/tables/spolSunCal/spolSunCal_20210801_000000_to_20210831_235959.txt',
                      help='File with suncal data')
    parser.add_option('--widthMain',
                      dest='mainWidthMm',
                      default=400,
                      help='Width of main figure in mm')
    parser.add_option('--heightMain',
                      dest='mainHeightMm',
                      default=70,
                      help='Height of main figure in mm')
#    parser.add_option('--filtLen',
#                      dest='filtLen',
#                      default=20,
#                      help='Len of moving mean filter')
    parser.add_option('--start',
                      dest='startTime',
                      default='1970 01 01 00 00 00',
                      #default='2019 01 29 17 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      default='1970 01 01 00 00 00',
                      #default='2019 01 29 22 00 00',
                      help='End time for XY plot')
    parser.add_option('--figDir',
                      dest='figureDir',
                      default='/scr/sleet1/rsfdata/projects/eolbase/catalog/images/spol_sunCal/2021/',
                      help='Directory for output figures')

    
    
    (options, args) = parser.parse_args()
    
    if (options.verbose == True):
        options.debug = True

    # time limits

    year, month, day, hour, minute, sec = options.startTime.split()
    startTime = datetime.datetime(int(year), int(month), int(day),
                                  int(hour), int(minute), int(sec))

    year, month, day, hour, minute, sec = options.endTime.split()
    endTime = datetime.datetime(int(year), int(month), int(day),
                                int(hour), int(minute), int(sec))

    Jan1970 = datetime.datetime(1970, 1, 1, 0, 0, 0)
    if ((startTime != Jan1970) and (endTime != Jan1970)):
        timeLimitsSet = True

    if (options.debug == True):
        print("Running %prog", file=sys.stderr)
#        print("  suncalFile: ", options.tempFilePath, file=sys.stderr)
        if (timeLimitsSet):
            print("  startTime: ", startTime, file=sys.stderr)
            print("  endTime: ", endTime, file=sys.stderr)
    
    # read in column headers

    iret, suncalHdrs, suncalHdrData = readColumnHeaders(options.suncalFile)
    if (iret != 0):
        sys.exit(-1)
    
    # find number of header lines
    headLines=getHeaderLines(options.suncalFile)
        
    # read in data
    def parse(year, month, day, hour, minute, second):
        return year+ '-' +month+ '-' +day+ ' ' +hour+ ':' +minute+ ':' +second
    
    suncalData=pd.read_csv(options.suncalFile,skiprows=headLines,delimiter=',',
                           names=suncalHdrs, header=0, parse_dates={'datetime': ['year', 'month', 'day','hour', 'min', 'sec']},
                           date_parser=parse)
    suncalData['timeForSiteTemp'] = pd.to_datetime(suncalData['timeForSiteTemp'])
    
    # filter out correct times
    if (timeLimitsSet):
        suncalShortTest=suncalData.loc[(suncalData['datetime'] >= startTime) & (suncalData['datetime'] <= endTime)]
        suncalShort=suncalShortTest.copy()
    else:
        suncalShort=suncalData
    
    # Calculate test pulse ratios
    suncalShort['testPulseRatioVcHc2']=(suncalShort['testPulseDbmVc']-suncalShort['testPulseDbmHc'])*2
    suncalShort['testPulseRatioVxHx2']=(suncalShort['testPulseDbmVx']-suncalShort['testPulseDbmHx'])*2
    suncalShort['testPulseRatioVcHx2']=(suncalShort['testPulseDbmVc']-suncalShort['testPulseDbmHx'])*2
    suncalShort['testPulseRatioVxHc2']=(suncalShort['testPulseDbmVx']-suncalShort['testPulseDbmHc'])*2
    
    # Remove test pulse data when test pulse was off
    tpVxMovMean=suncalShort.testPulseDbmVx.rolling(window=3).mean()
    tpVxMovMean=tpVxMovMean.replace({np.nan:-99})
    suncalShort['testPulseDbmVx'].values[tpVxMovMean < -60] = -9999
    suncalShort['testPulseRatioVxHx2'].values[tpVxMovMean < -60] = -9999
    suncalShort['testPulseRatioVxHc2'].values[tpVxMovMean < -60] = -9999
    
    tpVcMovMean=suncalShort.testPulseDbmVc.rolling(window=3).mean()
    tpVcMovMean=tpVcMovMean.replace({np.nan:-99})
    suncalShort['testPulseDbmVc'].values[tpVcMovMean < -60] = -9999
    suncalShort['testPulseRatioVcHc2'].values[tpVcMovMean < -60] = -9999
    suncalShort['testPulseRatioVcHx2'].values[tpVcMovMean < -60] = -9999
    
    tpHcMovMean=suncalShort.testPulseDbmHc.rolling(window=3).mean()
    tpHcMovMean=tpHcMovMean.replace({np.nan:-99})
    suncalShort['testPulseDbmHc'].values[tpHcMovMean < -60] = -9999
    suncalShort['testPulseRatioVcHc2'].values[tpHcMovMean < -60] = -9999
    suncalShort['testPulseRatioVxHc2'].values[tpHcMovMean < -60] = -9999
    
    tpHxMovMean=suncalShort.testPulseDbmHx.rolling(window=3).mean()
    tpHxMovMean=tpHxMovMean.replace({np.nan:-99})
    suncalShort['testPulseDbmHx'].values[tpHxMovMean < -60] = -9999
    suncalShort['testPulseRatioVxHx2'].values[tpHxMovMean < -60] = -9999
    suncalShort['testPulseRatioVcHx2'].values[tpHxMovMean < -60] = -9999
                    
    # Split datat into sub times based on gaps larger than 3 hours

    suncalSplit={}
    gapInd = suncalShort['datetime'].diff() > pd.to_timedelta('3 hours')
    g = suncalShort.groupby(gapInd.cumsum())
    for n,g1 in g:
        suncalSplit[n] = g1
    
    ############################################################
    #Loop through sub times and plot data
    # make output figure name sting
           
#    outFile=options.figureDir + os.path.splitext(os.path.split(options.compFilePath)[1])[0]
    
    # create figure directory if necessary
    
    pathlib.Path(options.figureDir).mkdir(parents=False, exist_ok=True)
    
    # close all existing figures
    
    mpl.pyplot.close("all")
    
    for key in suncalSplit:
        subData=suncalSplit[key]
                
        if subData.shape[0]>3: # For some reason pandas.dataframe.plot throws an error when plotting less than 4 data points
            
            # Replace -9999 and nans
            for column in subData:
                if(subData[column].dtype == 'float64' or subData[column].dtype == 'int64'):
                    # Replace -9999 with nan but only if not all data in column are -9999
                    lengthMissing=(subData[column] == -9999).sum()
                    if lengthMissing>0 and lengthMissing!=subData.shape[0]:
                        subData[column]=subData[column].replace({-9999:np.nan})
                    # Replace nan with -9999 but only if all data in column are nan
                    lengthMissing2=subData[column].isna().sum()
                    if lengthMissing2>0 and lengthMissing2==subData.shape[0]:
                        subData[column]=-9999
                        
            mpl.pyplot.close("all")
            
            doPlotSunAngles(options.figureDir,subData)
            doPlotPowersNoise(options.figureDir,subData)
            doPlotSunVars(options.figureDir,subData)
            
    #Plot S1S2 vs temperature for whole data set
    
    # Drop data with -9999 
    suncalShort = suncalShort[suncalShort.siteTempC != -9999]
    suncalShort = suncalShort[suncalShort.S1S2 != -9999]
            
    # Remove data with high noise
    #suncalShort=suncalShort[(suncalShort.noiseDbmHc < -75.15)]
    #suncalShort=suncalShort[(suncalShort.noiseDbmHx < -75.15)]
    #suncalShort=suncalShort[(suncalShort.noiseDbmVc < -75.15)]
    #suncalShort=suncalShort[(suncalShort.noiseDbmVx < -75.15)]
    
    # Remove data with faulty zdrDiffElAz
    suncalShort=suncalShort[(suncalShort.zdrDiffElAz > -100)]
    
    # Remove data with low sun angles
    suncalShort=suncalShort[(suncalShort.meanSunEl > 10)]
    
    lengthMissing3=suncalShort['siteTempC'].isna().sum()
    if lengthMissing3!=suncalShort.shape[0]:
        doPlotS1S2temp(options.figureDir,suncalShort)
        doPlotZDRcorrtemp(options.figureDir,suncalShort)
            
    # If you want to show the plots, uncomment the following line
    # Showing the plots will stop the script so it does not work when run as script
    #plt.show()
   
    exit
       
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
        colHeaders = [x.strip(' ') for x in colHeaders]
        if (options.debug == True):
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

def getHeaderLines(filePath):

    # open file

    fp = open(filePath, 'r')
    lines = fp.readlines()
    
    headerLines=0
    # read in a line at a time, set colData
    for line in lines:
        
        commentIndex = line.find("#")
        if (commentIndex < 0):
           return headerLines
        else:
           headerLines=headerLines+1
    return headerLines

########################################################################
# Moving average filter

#def movingAverage(values, window):
#
#    if (window < 2):
#        return values
#
#    weights = np.repeat(1.0, window)/window
#    sma = np.convolve(values, weights, 'same')
#    return sma
########################################################################
    # Plot sun angles
def doPlotSunAngles(outFilePath,data):

    # set up plots

    widthIn = float(options.mainWidthMm) / 25.4
    htIn = float(options.mainHeightMm)*2 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    colorsA = ['blue', 'red', 'green','black','cyan','magenta']
        
    firstTime=data.datetime.iloc[0]
    lastTime=data.datetime.iloc[-1]
    #lastTime=data.datetime.iloc[-1]
       
# Plot sun angles     
    ax1 = fig.add_subplot(2,1,1,xmargin=0.0)
    ax2 = ax1.twinx()
    
    data.plot('datetime','meanSunEl',ax=ax1,color=colorsA[0],fontsize=fontSize,xlim=[firstTime,lastTime])
    ax1.set_title('Sun angles '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, 0, 80, 'Elevation angle (deg)', 'upper left',firstTime,lastTime,fontSize)
    data.plot(x='datetime',y='meanSunAz',ax=ax2,color=colorsA[1],fontsize=fontSize)
    configTimeAxisMinMax(ax2, 60, 300, 'Azimuth angle (deg)', 'upper right',firstTime,lastTime,fontSize)
    
# Plot centroid offsets
    ax1 = fig.add_subplot(2,1,2,xmargin=0.0)
      
    data.plot(x='datetime',y=['centroidAzOffset','centroidElOffset','centroidAzOffsetHc','centroidElOffsetHc',
                              'centroidAzOffsetVc','centroidElOffsetVc'],ax=ax1,color=colorsA[0:6],fontsize=fontSize,xlim=[firstTime,lastTime])
    ax1.set_title('Centroid offset '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, -0.2, 0.2, 'Offset (deg)', 'upper left',firstTime,lastTime,fontSize)
       
    fig.autofmt_xdate()
    fig.tight_layout()

#    # Overall plot title
#
#    fig.suptitle("Test pulse powers and system temperatures ", fontweight='bold')
#        
    startString=firstTime.strftime("%Y%m%d_%H%M%S")
    endString=lastTime.strftime("%Y%m%d_%H%M%S")
    plt.savefig(outFilePath + 'sunAngles_' + startString + '_to_' + endString+'.png')

    return

########################################################################
    
def doPlotPowersNoise(outFilePath,data):

    # set up plots

    widthIn = float(options.mainWidthMm) / 25.4
    htIn = float(options.mainHeightMm)*4 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    colorsA = ['blue', 'red', 'green','black','cyan','magenta']
    
    firstTime=data.datetime.iloc[0]
    lastTime=data.datetime.iloc[-1]
    
# Plot noise     
    ax1 = fig.add_subplot(4,1,1,xmargin=0.0)
        
    data.plot(x='datetime',y=['noiseDbmHc','noiseDbmHx','noiseDbmVc','noiseDbmVx'],ax=ax1,color=colorsA[0:4],fontsize=fontSize)
    ax1.set_title('Noise '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, -76.0, -74.6, 'Noise (dBm)', 'upper left',firstTime,lastTime,fontSize)
       
# Plot noise number
    ax1 = fig.add_subplot(4,1,2,xmargin=0.0)
        
    data.plot(x='datetime',y='nBeamsNoise',ax=ax1,color=colorsA[0],fontsize=fontSize)
    configTimeAxisMinMax(ax1, 0, 3000, 'Number', 'upper right',firstTime,lastTime,fontSize)
       
# Plot maxPower and quadPower
    ax1 = fig.add_subplot(4,1,3,xmargin=0.0)
        
    data.plot('datetime',['maxPowerDbm','quadPowerDbm','maxPowerDbmHc','quadPowerDbmHc',
                              'maxPowerDbmVc','quadPowerDbmVc'],ax=ax1,color=colorsA[0:6],fontsize=fontSize)
    ax1.set_title('Max power and quad power '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, -63, -60, 'Power (dBm)', 'upper left',firstTime,lastTime,fontSize)
        
# Plot mean Xmit powers
    ax1 = fig.add_subplot(4,1,4,xmargin=0.0)
    
    data.plot(x='datetime',y=['meanXmitPowerHDbm','meanXmitPowerVDbm'],ax=ax1,color=colorsA[0:2],fontsize=fontSize)
    ax1.set_title('Xmit power '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, 87.0, 88.0, 'Power (dBm)', 'upper left',firstTime,lastTime,fontSize)
       
    fig.autofmt_xdate()
    fig.tight_layout()

#    # Overall plot title
#
#    fig.suptitle("Test pulse powers and system temperatures ", fontweight='bold')
#        
    startString=firstTime.strftime("%Y%m%d_%H%M%S")
    endString=lastTime.strftime("%Y%m%d_%H%M%S")
    plt.savefig(outFilePath + 'noise_powers_' + startString + '_to_' + endString+'.png')
    
    return

########################################################################
    
def doPlotSunVars(outFilePath,data):

    # set up plots

    widthIn = float(options.mainWidthMm) / 25.4
    htIn = float(options.mainHeightMm)*4 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    colorsA = ['blue', 'red', 'green','black','cyan','magenta']
    
    firstTime=data.datetime.iloc[0]
    lastTime=data.datetime.iloc[-1]
    
# Plot XpolRatio and transmit power ratio
    ax1 = fig.add_subplot(4,1,1,xmargin=0.0)
    ax2 = ax1.twinx()
    
    data['meanXmitPowerRatio']=data['meanXmitPowerVDbm']-data['meanXmitPowerHDbm']
        
    data.plot(x='datetime',y=['S1S2','meanXpolRatioDb','meanXmitPowerRatio'],ax=ax1,color=colorsA[0:3],fontsize=fontSize)
    ax1.set_title('S1S2, Xpol ratio, transmit power ratio, site temperature '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    med1=data.S1S2.median()
    med2=data.meanXpolRatioDb.median()
    med3=data.meanXmitPowerRatio.median()
    configTimeAxisMedSpread(ax1, np.mean([med1,med2,med3]), 0.7, '(dB)', 'upper left',firstTime,lastTime,fontSize)
    
    data.plot(x='timeForSiteTemp',y='siteTempC',ax=ax2,fontsize=fontSize,color=colorsA[4])    
    configTimeAxisMedSpread(ax2, data.siteTempC.median(), 15, 'Temperature (C)', 'upper right',firstTime,lastTime,fontSize)
    
# Plot coco xx testpulses, S1S2, and site temperature
    ax1 = fig.add_subplot(4,1,2,xmargin=0.0)
    ax2 = ax1.twinx()
              
    data.plot(x='datetime',y=['S1S2','zdrCorr'],ax=ax1,color=colorsA[0:2],fontsize=fontSize)
    ax1.set_title('S1S2, zdrCorr, test pulse ratios, '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    med1=data.S1S2.median()
    med2=data.zdrCorr.median()
    configTimeAxisMedSpread(ax1, np.mean([med1,med2]), 0.6, 'S1S2, zdrCorr (dB)', 'upper left',firstTime,lastTime,fontSize)
    
    data.plot(x='datetime',y=['testPulseRatioVcHc2','testPulseRatioVxHx2'],ax=ax2,color=colorsA[3:5],fontsize=fontSize)
    medians=[data.testPulseRatioVcHc2.median(),data.testPulseRatioVxHx2.median()]
    new_medians = [x if x>-100 else np.nan for x in medians]
    if np.count_nonzero(~np.isnan(new_medians))==0:
        meanMed=-1000
    else:
        meanMed=np.nanmean(new_medians)
    configTimeAxisMedSpread(ax2, meanMed, 0.25, 'TestPulseRatio*2 (dB)', 'upper right',firstTime,lastTime,fontSize)
           
# Plot widths
    ax1 = fig.add_subplot(4,1,3,xmargin=0.0)
    
    data['widthRatioElAzHcSub']=1-data['widthRatioElAzHc']
    data['widthRatioElAzVcSub']=1-data['widthRatioElAzVc']
    
    data.plot(x='datetime',y=['widthRatioElAzHcSub','widthRatioElAzVcSub',
                              'zdrDiffElAz'],ax=ax1,color=colorsA[0:4],fontsize=fontSize)
    ax1.set_title('Width Ratio and zdf diff el az '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxisMinMax(ax1, -1.5, 0.5, ' ', 'upper left',firstTime,lastTime,fontSize)
           
# Plot cox testpulses and number of xpol points
    ax1 = fig.add_subplot(4,1,4,xmargin=0.0)
    ax2 = ax1.twinx()
    
    data.plot(x='datetime',y=['testPulseRatioVcHx2','testPulseRatioVxHc2'],ax=ax1,fontsize=fontSize,color=colorsA[0:3])
    ax1.set_title('Test pulse ratios, number of Xpol points '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')    
    medians=[data.testPulseRatioVcHx2.median(),data.testPulseRatioVxHc2.median()]
    new_medians = [x if x>-100 else np.nan for x in medians]   
    if np.count_nonzero(~np.isnan(new_medians))==0:
        meanMed=-1000
    else:
        meanMed=np.nanmean(new_medians)
    configTimeAxisMedSpread(ax1, meanMed, 0.4, 'TestPulseRatio*2 (dB)', 'upper left',firstTime,lastTime,fontSize)
    
    data.plot(x='datetime',y='nXpolPoints',ax=ax2,color=colorsA[4],fontsize=fontSize)
    configTimeAxisMinMax(ax2, 0, 300000, 'Number', 'upper right',firstTime,lastTime,fontSize)
    
    fig.autofmt_xdate()
    fig.tight_layout()

#    # Overall plot title
#
#    fig.suptitle("Test pulse powers and system temperatures ", fontweight='bold')
#        
    startString=firstTime.strftime("%Y%m%d_%H%M%S")
    endString=lastTime.strftime("%Y%m%d_%H%M%S")
    plt.savefig(outFilePath + 'solarVars_' + startString + '_to_' + endString+'.png')

    return

########################################################################
# Plot S1S2 vs temperatures

def doPlotS1S2temp(outFilePath,data):
    # Don't remove outliers
    #rmOut,indsOut=reject_outliers(data['S1S2'],float('inf'))
    # Remove outliers
    rmOut,indsOut=reject_outliers(data['S1S2'],4.5)
    
    dataRMout=pd.DataFrame([data['S1S2'].loc[indsOut],data['siteTempC'].loc[indsOut]])
    dataRMout=dataRMout.T
    # set up plots

    widthIn = float(options.mainHeightMm)*3 / 25.4
    htIn = float(options.mainHeightMm)*3 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    firstTime=data.datetime.iloc[0]
    lastTime=data.datetime.iloc[-1]
    
    ax1 = fig.add_subplot(1,1,1,xmargin=0.0)
    
    dataRMout.plot.scatter(x='siteTempC',y='S1S2',ax=ax1,fontsize=fontSize)
    ax1.set_title('S1S2 vs site temperature '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configScattAxis(ax1, -9999, 'Temperature (C)', 'S1S2 (dB)',fontSize)
    
    ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))

    fig.tight_layout()
       
    startString=firstTime.strftime("%Y%m%d_%H%M%S")
    endString=lastTime.strftime("%Y%m%d_%H%M%S")
    plt.savefig(outFilePath + 's1s2_temps_' + startString + '_to_' + endString+'.png')

    return

########################################################################
# Plot zdrCorr vs temperatures

def doPlotZDRcorrtemp(outFilePath,data):
    # Don't remove outliers
    #rmOut,indsOut=reject_outliers(data['S1S2'],float('inf'))
    # Remove outliers
    rmOut,indsOut=reject_outliers(data['S1S2'],4.5)
    
    dataRMout=pd.DataFrame([data['zdrCorr'].loc[indsOut],data['siteTempC'].loc[indsOut]])
    dataRMout=dataRMout.T
    # set up plots

    widthIn = float(options.mainHeightMm)*3 / 25.4
    htIn = float(options.mainHeightMm)*3 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    firstTime=data.datetime.iloc[0]
    lastTime=data.datetime.iloc[-1]
    
    ax1 = fig.add_subplot(1,1,1,xmargin=0.0)
    
    dataRMout.plot.scatter(x='siteTempC',y='zdrCorr',ax=ax1,fontsize=fontSize)
    ax1.set_title('zdrCorr vs site temperature '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configScattAxis(ax1, -9999, 'Temperature (C)', 'zdrCorr (dB)',fontSize)
    
    ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))

    fig.tight_layout()
       
    startString=firstTime.strftime("%Y%m%d_%H%M%S")
    endString=lastTime.strftime("%Y%m%d_%H%M%S")
    plt.savefig(outFilePath + 'zdrCorr_temps_' + startString + '_to_' + endString+'.png')

    return
########################################################################
# Configure axes, legends etc

def configTimeAxisMinMax(ax, ymin, ymax, ylabel, legendLoc, firstTime, lastTime,fontSize):
        
    legend = ax.legend(loc=legendLoc, ncol=6)
    for label in legend.get_texts():
        label.set_fontsize(fontSize)
    ax.set_xlim([firstTime, lastTime])
    ax.set_xlabel("Time (UTC)",fontsize=fontSize)
    ax.set_ylabel(ylabel,fontsize=fontSize)
    ax.grid(False)
    if (ymin > -9990 and ymax > -9990):
        ax.set_ylim([ymin,ymax])
    hfmt = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(dates.AutoDateLocator())
    ax.xaxis.set_major_formatter(hfmt)
    
def configTimeAxisMedSpread(ax, ymedian, yhalfSpread, ylabel, legendLoc, firstTime, lastTime,fontSize):
        
    legend = ax.legend(loc=legendLoc, ncol=6)
    for label in legend.get_texts():
        label.set_fontsize(fontSize)
    ax.set_xlim([firstTime, lastTime])
    ax.set_xlabel("Time (UTC)",fontsize=fontSize)
    ax.set_ylabel(ylabel,fontsize=fontSize)
    ax.grid(False)
    if (ymedian > -9990 and yhalfSpread > -9990):
        ax.set_ylim([ymedian-yhalfSpread,ymedian+yhalfSpread+yhalfSpread/4])
    hfmt = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(dates.AutoDateLocator())
    ax.xaxis.set_major_formatter(hfmt)
    
def configScattAxis(ax, yspread, xlabel, ylabel, title):
    
    fontSize=12
    ax.set_ylabel(ylabel,fontsize=fontSize)
    ax.set_xlabel(xlabel,fontsize=fontSize)
    if (yspread > -9990):
        ylimMean=np.mean(ax.get_ylim())        
        ax.set_ylim([ylimMean-yspread,ylimMean+yspread+yspread/10])
    xlims=ax.get_xlim()
    ax.set_xlim([xlims[0]-1,xlims[1]+1])
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
    
########################################################################
# Remove outliers in temperature data
def reject_outliers(data, m = 5):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    inds = s<m
    return data[s<m], inds
    
########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

