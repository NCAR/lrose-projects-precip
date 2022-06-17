#!/usr/bin/env python3

#===========================================================================
#
# Make plots to monitor S-Pol data
#
#===========================================================================

import sys
from optparse import OptionParser
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.ticker as ticker
from matplotlib import dates
import datetime
import pathlib
from matplotlib.dates import DateFormatter
import pandas as pd

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
    parser.add_option('--monFile',
                      dest='monFile',
                      default='/scr/hail1/rsfdata/eolbase/tables/spolMon/spolMon_20190501_000000_to_20190531_235959.txt',
                      help='File with monitoring data')
    parser.add_option('--widthMain',
                      dest='mainWidthMm',
                      default=400,
                      help='Width of main figure in mm')
    parser.add_option('--heightMain',
                      dest='mainHeightMm',
                      default=70,
                      help='Height of main figure in mm')
    parser.add_option('--start',
                      dest='startTime',
                      #default='1970 01 01 00 00 00',
                      default='2019 05 01 00 00 00',
                      help='Start time for XY plot')
    parser.add_option('--end',
                      dest='endTime',
                      #default='1970 01 01 00 00 00',
                      default='2019 05 31 23 59 59',
                      help='End time for XY plot')
    parser.add_option('--figDir',
                      dest='figureDir',
                      default='/scr/sci/romatsch/spolPlots/timeSeriesPy/test/',
                      help='Directory for output figures')
    parser.add_option('--plotHours',
                      dest='plotHours',
                      default='6',
                      help='Plot time frame in hours starting at the full hour')
    parser.add_option('--printTable',
                      dest='printTable',
                      default='0',
                      help='Print table with operation hours: yes=1, no=0')
    
    
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
#        print("  monFile: ", options.tempFilePath, file=sys.stderr)
        if (timeLimitsSet):
            print("  startTime: ", startTime, file=sys.stderr)
            print("  endTime: ", endTime, file=sys.stderr)
    
    # read in column headers

    iret, monHdrs, monHdrData = readColumnHeaders(options.monFile)
    if (iret != 0):
        sys.exit(-1)
    
    # find number of header lines
    headLines=getHeaderLines(options.monFile)
        
    # read in data
    def parse(year, month, day, hour, minute, second):
        return year+ '-' +month+ '-' +day+ ' ' +hour+ ':' +minute+ ':' +second
    
    monData=pd.read_csv(options.monFile,skiprows=headLines,delimiter=',',
                           names=monHdrs, header=0, parse_dates={'datetime': ['year', 'month', 'day','hour', 'min', 'sec']},
                           date_parser=parse)
    
    # filter out correct times
    if (timeLimitsSet):
        monShortTest=monData.loc[(monData['datetime'] >= startTime) & (monData['datetime'] <= endTime)]
        monShort=monShortTest.copy()
    else:
        monShort=monData.copy()
                    
    # Calculate test pulse ratios
    monShort['TestPulseRatioVcHc2']=(monShort['TestPulsePowerDbVc']-monShort['TestPulsePowerDbHc'])*2
    monShort['TestPulseRatioVxHx2']=(monShort['TestPulsePowerDbVx']-monShort['TestPulsePowerDbHx'])*2
    monShort['TestPulseRatioVcHx2']=(monShort['TestPulsePowerDbVc']-monShort['TestPulsePowerDbHx'])*2
    monShort['TestPulseRatioVxHc2']=(monShort['TestPulsePowerDbVx']-monShort['TestPulsePowerDbHc'])*2
    
    # Remove test pulse data when test pulse was off
    tpVxMovMean=monShort.TestPulsePowerDbVx.rolling(window=3).mean()
    tpVxMovMean=tpVxMovMean.replace({np.nan:-99})
    monShort['TestPulsePowerDbVx'].values[tpVxMovMean < -60] = -9999
    monShort['TestPulseRatioVxHx2'].values[tpVxMovMean < -60] = -9999
    monShort['TestPulseRatioVxHc2'].values[tpVxMovMean < -60] = -9999
    
    tpVcMovMean=monShort.TestPulsePowerDbVc.rolling(window=3).mean()
    tpVcMovMean=tpVcMovMean.replace({np.nan:-99})
    monShort['TestPulsePowerDbVc'].values[tpVcMovMean < -60] = -9999
    monShort['TestPulseRatioVcHc2'].values[tpVcMovMean < -60] = -9999
    monShort['TestPulseRatioVcHx2'].values[tpVcMovMean < -60] = -9999
    
    tpHcMovMean=monShort.TestPulsePowerDbHc.rolling(window=3).mean()
    tpHcMovMean=tpHcMovMean.replace({np.nan:-99})
    monShort['TestPulsePowerDbHc'].values[tpHcMovMean < -60] = -9999
    monShort['TestPulseRatioVcHc2'].values[tpHcMovMean < -60] = -9999
    monShort['TestPulseRatioVxHc2'].values[tpHcMovMean < -60] = -9999
    
    tpHxMovMean=monShort.TestPulsePowerDbHx.rolling(window=3).mean()
    tpHxMovMean=tpHxMovMean.replace({np.nan:-99})
    monShort['TestPulsePowerDbHx'].values[tpHxMovMean < -60] = -9999
    monShort['TestPulseRatioVxHx2'].values[tpHxMovMean < -60] = -9999
    monShort['TestPulseRatioVcHx2'].values[tpHxMovMean < -60] = -9999
    
    # Split datat into episodes
    hourLengthStr=options.plotHours+'H'
    
    monSplit={}
    g=monShort.groupby(pd.Grouper(key='datetime',freq=hourLengthStr))
    grouperInds=g.grouper.result_index
    for n,g1 in g:
        monSplit[n] = g1
    
    ############################################################
    #Loop through sub times and plot data
     
    # create figure directory if necessary    
    pathlib.Path(options.figureDir).mkdir(parents=False, exist_ok=True)
    
    # close all existing figures    
    mpl.pyplot.close("all")
    
    for idx,key in enumerate(monSplit):
        subData=monSplit[key].copy()
                
        if subData.shape[0]>1:
         
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
                        subData.loc[:,column]=-9999
            
            mpl.pyplot.close("all")
            print(grouperInds[idx])
            doPlotTestTempFaults(options.figureDir,subData,grouperInds[idx],float(options.plotHours))
            
    # If you want to show the plots, uncomment the following line
    # Showing the plots will stop the script so it does not work when run as script
    #plt.show()
    
    if int(options.printTable)==1:
        # Count time of operation
        # Split data into daily episodes
        monDaily={}
        g2=monShort.groupby(pd.Grouper(key='datetime',freq='24H'))
        for n,g3 in g2:
            monDaily[n] = g3
    
        allTimes=monShort['datetime'].dt.normalize().dt.strftime('%Y-%m-%d').unique()
        allDays=np.zeros((len(allTimes),4))
        
        jj=0

        # Count time per day
        for ii,key in enumerate(monDaily):
            subDay=monDaily[key].copy()      
            if subDay.shape[0]!=0:
                allDays[jj,:]=doCountTime(subDay)
                jj=jj+1
    
        outTable=pd.DataFrame(allDays,columns=['Oil_Press_Good','Az_Brakes_Off',
                                           'High_Volts_On','Xmit_Power_On'], index=allTimes)
        outTable.index.name = 'Date               '
    
        # Add extra row before total
        outTable.loc[''] = np.nan
        # Calculate sum
        outTable.loc['Total hours'] = outTable.sum()
    
        #Save data
        firstTime=grouperInds[0]
        startString=firstTime.strftime("%Y%m%d%H%M")
        outTable.to_csv(options.figureDir + 'radar.SPOL.' + startString + '.Operation_Hours_Table.txt',
                        sep='\t',float_format='%12.1f',doublequote=False)
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
    # Plot test pulse power and system temperatures
def doPlotTestTempFaults(outFilePath,data,firstTime,timeSpan):

    # set up plots

    widthIn = float(options.mainWidthMm) / 25.4
    htIn = float(options.mainHeightMm)*4 / 25.4
    
    fontSize=12
    
    global figNum
    fig = plt.figure(figNum, (widthIn, htIn))
    figNum = figNum + 1
    
    colorsP = pl.cm.Dark2(np.linspace(0,1,8))
    colorsT = pl.cm.tab10(np.linspace(0,1,10))
    #colorsT2 = pl.cm.gist_rainbow(np.linspace(0,1,16))
    colorsT2 = np.vstack((pl.cm.tab10(np.linspace(0,1,10)), pl.cm.gist_rainbow(np.linspace(0,1,6))))
        
    #firstTime=data.datetime.iloc[0]
    #lastTime=data.datetime.iloc[-1]
    lastTime=firstTime+pd.DateOffset(hours=timeSpan)
       
# Plot test pulses and test pulse ratios
    ax1 = fig.add_subplot(3,1,1,xmargin=0.0)
    ax2 = ax1.twinx()
    
    data.plot(x='datetime',y=['TestPulsePowerDbHc','TestPulsePowerDbVc',
              'TestPulsePowerDbHx','TestPulsePowerDbVx'],ax=ax1,color=colorsP[0:4],fontsize=fontSize, linewidth=2,x_compat=True)
    ax1.set_title('Test pulses and temperatures '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    
    # Make adjustable axis limits depending of test pulse value
    sortedTHc=data.sort_values('TestPulsePowerDbHc', ascending=False)
    medTHc=sortedTHc.TestPulsePowerDbHc[0:30].median()
    sortedTHx=data.sort_values('TestPulsePowerDbHx', ascending=False)
    medTHx=sortedTHx.TestPulsePowerDbHx[0:30].median()
    sortedTVc=data.sort_values('TestPulsePowerDbVc', ascending=False)
    medTVc=sortedTVc.TestPulsePowerDbVc[0:30].median()
    sortedTVx=data.sort_values('TestPulsePowerDbVx', ascending=False)
    medTVx=sortedTVx.TestPulsePowerDbVx[0:30].median()
    
    allMeds=[medTHc, medTHx, medTVc, medTVx]
    allMeds[:] = [np.nan if x<-8888 else x for x in allMeds]
    if np.count_nonzero(~np.isnan(allMeds))==0:
        bottomVal=-1000
    else:
        bottomVal=np.floor(np.nanmean(allMeds)/10)*10
    topVal=bottomVal+10    
    configTimeAxis(ax1, bottomVal, topVal, 'Power (dB)', 'upper left',firstTime,lastTime,fontSize)
    
    medians=[data.TestPulseRatioVcHc2.median(),data.TestPulseRatioVxHx2.median(),
             data.TestPulseRatioVcHx2.median(),data.TestPulseRatioVxHc2.median()]
    new_medians = [x if x>-100 else np.nan for x in medians]   
    if np.count_nonzero(~np.isnan(new_medians))==0:
        meanMed=-1000
    else:
        meanMed=np.nanmean(new_medians)
    data.plot(x='datetime',y=['TestPulseRatioVcHc2','TestPulseRatioVxHx2','TestPulseRatioVcHx2','TestPulseRatioVxHc2'],
              ax=ax2,color=colorsT[5:10],fontsize=fontSize, linewidth=1,x_compat=True)
    configTimeAxisMedSpread(ax2, meanMed, 0.3, 'Test pulse ratio (db)', 'lower left',firstTime,lastTime,fontSize)
        
    hfmt = dates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_locator(dates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(hfmt)

    fig.tight_layout()
    
# Plot temperatures
    ax1 = fig.add_subplot(3,1,2,xmargin=0.0)
       
    data.plot(x='datetime',y=['Temp_Klystron','Temp_Rear_Wall','Temp_CIRC_V','Temp_CIRC_H',
                              'Temp_LNA_V','Temp_LNA_H','Temp_RX_enclosure','Temp_TP_enclosure',
                              'Temp_RX_plate','Temp_TX_coupler_H','Temp_DUMMY_H','Temp_DUMMY_V',
                              'Temp_MITCH_SWITCH','Temp_SCC','Temp_Annex','Temp_UPS_Container'],
                              ax=ax1,color=colorsT2[0:16],fontsize=fontSize, linewidth=1,x_compat=True)
    configTimeAxis(ax1, -10, 50, 'Temperature (C)', 'lower left',firstTime,lastTime,fontSize)
        
    hfmt = dates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_locator(dates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(hfmt)

    fig.tight_layout()
    
# Plot faults
    ax1 = fig.add_subplot(3,1,3,xmargin=0.0)
    ax2 = ax1.twinx()
      
    data['Oil_Pressure']=data['Oil_Pressure_Fault']
    data['Azimuth_Brakes']=data['Azimuth_Brakes_Fault']+2
    data['High_Volts_On']=data['HighVoltsOn']+4
    
    data.plot(x='datetime',y=['Oil_Pressure',
                              'Azimuth_Brakes','High_Volts_On'],ax=ax1,color=colorsP[0:4],fontsize=fontSize, linewidth=2,x_compat=True)
    ax1.set_title('Antenna faults and transmit status '+str(firstTime)+' to '+str(lastTime), fontsize=fontSize, fontweight='bold')
    configTimeAxis(ax1, -3.5, 9, '', 'upper left',firstTime,lastTime,fontSize)
    ax1.set_yticks(np.arange(-3, 9, step=1), minor=False)
    ax1.set_yticklabels(['','','','False','True','False','True','False','True','','',''])
    data.plot(x='datetime',y='XmitPowerDbmTxTop',ax=ax2,color='black',fontsize=fontSize, linewidth=1,x_compat=True)
    configTimeAxis(ax2, 35, 100, 'Power (dBm)', 'upper right',firstTime,lastTime,fontSize)
        
    hfmt = dates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_locator(dates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(hfmt)

    fig.tight_layout()
    
    subFolder=''
    
#    # Make sub folder based on month
#    subFolder=firstTime.strftime("%Y%m")
#    # Create sub folder if it doesn't exist
#    pathlib.Path(outFilePath+subFolder).mkdir(parents=False, exist_ok=True)
    
    startString=firstTime.strftime("%Y%m%d%H%M")
    plt.savefig(outFilePath + subFolder + '/' + 'radar.SPOL.' + startString + '.Monitoring.png')

    return


########################################################################
# Configure axes, legends etc

def configTimeAxis(ax, miny, maxy, ylabel, legendLoc, firstTime, lastTime,fontSize):
        
    legend = ax.legend(loc=legendLoc, ncol=4)
    for label in legend.get_texts():
        label.set_fontsize(fontSize)
    ax.set_xlim([firstTime, lastTime])
    ax.set_xlabel("Time (UTC)",fontsize=fontSize)
    ax.set_ylabel(ylabel,fontsize=fontSize)
    ax.grid(False)
    if (miny > -9990 and maxy > -9990):
        ax.set_ylim([miny, maxy])
        
def configTimeAxisMedSpread(ax, ymedian, yhalfSpread, ylabel, legendLoc, firstTime, lastTime,fontSize):
        
    legend = ax.legend(loc=legendLoc, ncol=6)
    for label in legend.get_texts():
        label.set_fontsize(fontSize)
    ax.set_xlim([firstTime, lastTime])
    ax.set_xlabel("Time (UTC)",fontsize=fontSize)
    ax.set_ylabel(ylabel,fontsize=fontSize)
    ax.grid(False)
    if (ymedian > -9990 and yhalfSpread > -9990):
        ax.set_ylim([ymedian-yhalfSpread,ymedian+yhalfSpread])
    hfmt = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(dates.AutoDateLocator())
    ax.xaxis.set_major_formatter(hfmt)
        
########################################################################
# Count operation time
def doCountTime(data):
    
    #Split into hours
    monMin={}
    g=data.groupby(pd.Grouper(key='datetime',freq='10Min'))
    for n,g1 in g:
        monMin[n] = g1
        
    oilFmin=0
    abFmin=0
    hvoTmin=0
    powTmin=0    
    
    for key in monMin:
        subHour=monMin[key].copy()
        if subHour.shape[0]>0:
            oilF=(subHour['Oil_Pressure_Fault'] == 0).sum()
            abF=(subHour['Azimuth_Brakes_Fault'] == 0).sum()
            hvoT=(subHour['HighVoltsOn'] == 1).sum()
            powT=(subHour['XmitPowerDbmTxTop'] > 75).sum()
    
            totLen=subHour.shape[0]
    
            oilFmin=oilFmin+oilF/totLen*10
            abFmin=abFmin+abF/totLen*10
            hvoTmin=hvoTmin+hvoT/totLen*10
            powTmin=powTmin+powT/totLen*10
            
            retArray=np.array([oilFmin/60,abFmin/60,hvoTmin/60,powTmin/60])
    
    return retArray

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()

