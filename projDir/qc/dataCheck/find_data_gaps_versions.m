% Find data gaps in time series

clear all
close all

versionQC='v1.0';

startDate=datetime(2022,5,25);
endDate=datetime(2022,8,12); % This day is included

baseDir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/sband/v1.0/';

figdir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/data_gaps/';

%% Process day by day
dayList=startDate:days(1):endDate;

for ii=1:length(dayList)
    thisDay=dayList(ii);
    dateString=datestr(thisDay,'yyyymmdd');

    noDataTime=thisDay:seconds(1):thisDay+hours(24);
    noDataTimeNan=zeros(size(noDataTime));
    
    % 'sur' directory
    [surTimes,noDataTimeNan]=findGaps_moments('sur',baseDir,dateString,noDataTime,noDataTimeNan); 
    surPlot=nan(size(surTimes));
    surPlot(:)=1;

    % 'rhi' directory
    [rhiTimes,noDataTimeNan]=findGaps_moments('rhi',baseDir,dateString,noDataTime,noDataTimeNan); 
    rhiPlot=nan(size(rhiTimes));
    rhiPlot(:)=2;

    %% Plot

    disp(['Plotting ',dateString]);

    close all
    
    f1=figure('DefaultAxesFontSize',12,'Position',[0 300 1500 800],'renderer','painters','visible','off');

    s1=subplot(4,1,1);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,2.5]);
    yticks(0:2);
    yticklabels({'missing','sur','rhi'})
    xlim([thisDay,thisDay+hours(6)]);
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    s2=subplot(4,1,2);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,2.5]);
    yticks(0:2);
    yticklabels({'missing','sur','rhi'})
    xlim([thisDay+hours(6),thisDay+hours(12)]);
    grid on
    box on

    s3=subplot(4,1,3);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,2.5]);
    yticks(0:2);
    yticklabels({'missing','sur','rhi'})
    xlim([thisDay+hours(12),thisDay+hours(18)]);
    grid on
    box on

    s4=subplot(4,1,4);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,2.5]);
    yticks(0:2);
    yticklabels({'missing','sur','rhi'})
    xlim([thisDay+hours(18),thisDay+hours(24)]);
    grid on
    box on

    set(gcf,'PaperPositionMode','auto')
    print(f1,[figdir,'dataGaps_',versionQC,'_',datestr(thisDay,'yyyymmdd'),'.png'],'-dpng','-r0');

end