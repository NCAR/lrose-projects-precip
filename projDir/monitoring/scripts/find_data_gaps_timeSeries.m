% Find data gaps in time series

clear all
close all

dataType='sband';

startDate=datetime(2022,6,1);
endDate=datetime(2022,7,4); % This day is included

if strcmp(dataType,'spoldrx')
    baseDir='/scr/cirrus3/rsfdata/projects/precip/spolField/time_series/spoldrx/';
elseif strcmp(dataType,'sband')
    baseDir='/scr/cirrus2/rsfdata/projects/precip/spolField/time_series/sband/';
end

figdir=['/scr/cirrus3/rsfdata/projects/precip/spolField/monitorPlots/dataGaps_ts/',dataType,'/'];

%% Process day by day

dayList=startDate:days(1):endDate;

for ii=1:length(dayList)
    thisDay=dayList(ii);
    dateString=datestr(thisDay,'yyyymmdd');

    noDataTime=thisDay:seconds(1):thisDay+hours(24);
    noDataTimeNan=ones(size(noDataTime));
    noDataTimeNan=-noDataTimeNan;

    % 'save' directory
    [saveTimes,saveDataRate,noDataTimeNan]=findGaps_timeSeries('save',baseDir,dateString,noDataTime,noDataTimeNan);    

    % 'sunscan' directory
    [sunscanTimes,sunscanDataRate,noDataTimeNan]=findGaps_timeSeries('sunscan',baseDir,dateString,noDataTime,noDataTimeNan);

    % 'vert' directory
    [vertTimes,vertDataRate,noDataTimeNan]=findGaps_timeSeries('vert',baseDir,dateString,noDataTime,noDataTimeNan);

    %% Plot

    disp(['Plotting ',dateString]);

    close all
    ylimits=[-1.5 12];

    f1=figure('DefaultAxesFontSize',12,'Position',[0 300 1500 1200],'renderer','painters','visible','on');

    s1=subplot(4,1,1);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','magenta');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim(ylimits);
    xlim([thisDay,thisDay+hours(6)]);
    ylabel('MB s^{-1}');
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    s2=subplot(4,1,2);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','magenta');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim(ylimits);
    xlim([thisDay+hours(6),thisDay+hours(12)]);
    ylabel('MB s^{-1}');
    grid on
    box on

    s3=subplot(4,1,3);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','magenta');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim(ylimits);
    xlim([thisDay+hours(12),thisDay+hours(18)]);
    ylabel('MB s^{-1}');
    grid on
    box on

    s4=subplot(4,1,4);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','magenta');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim(ylimits);
    xlim([thisDay+hours(18),thisDay+hours(24)]);
    ylabel('MB s^{-1}');
    grid on
    box on
    s4pos=s4.Position;
    legend('save','sunscan','vert','missing','Orientation','horizontal','Location','southoutside')
    s4.Position=s4pos;

    set(gcf,'PaperPositionMode','auto')
    print(f1,[figdir,'dataGaps_timeSeries_',datestr(thisDay,'yyyymmdd'),'.png'],'-dpng','-r0');

end