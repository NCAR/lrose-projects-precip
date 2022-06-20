% Find data gaps in time series

clear all
close all

dataType='spoldrx';

startDate=datetime(2022,5,23);
endDate=datetime(2022,6,4); % This day is included

baseDir=['/scr/cirrus3/rsfdata/projects/precip/spolField/cfradial/moments/',dataType,'/'];

figdir=['/scr/cirrus3/rsfdata/projects/precip/spolField/monitorPlots/dataGaps_moments/',dataType,'/'];

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

    % 'sunscan' directory
    [sunscanTimes,noDataTimeNan]=findGaps_moments('sunscan',baseDir,dateString,noDataTime,noDataTimeNan); 
    sunscanPlot=nan(size(sunscanTimes));
    sunscanPlot(:)=3;

    % 'vert' directory
    [vertTimes,noDataTimeNan]=findGaps_moments('vert',baseDir,dateString,noDataTime,noDataTimeNan); 
    vertPlot=nan(size(vertTimes));
    vertPlot(:)=4;

    % 'sec' directory
    [secTimes,noDataTimeNan]=findGaps_moments('sec',baseDir,dateString,noDataTime,noDataTimeNan); 
    secPlot=nan(size(secTimes));
    secPlot(:)=5;

    %% Plot

    disp(['Plotting ',dateString]);

    close all
    
    f1=figure('DefaultAxesFontSize',12,'Position',[0 300 1500 1200],'renderer','painters','visible','on');

    s1=subplot(4,1,1);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(sunscanTimes,sunscanPlot,'filled','green');
    scatter(vertTimes,vertPlot,'filled','magenta');
    scatter(secTimes,secPlot,'filled','black');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,5.5]);
    yticks=-0:5;
    yticklabels({'missing','sur','rhi','sunscan','vert','sec'})
    xlim([thisDay,thisDay+hours(6)]);
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    s2=subplot(4,1,2);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(sunscanTimes,sunscanPlot,'filled','green');
    scatter(vertTimes,vertPlot,'filled','magenta');
    scatter(secTimes,secPlot,'filled','black');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,5.5]);
    yticks=-0:5;
    yticklabels({'missing','sur','rhi','sunscan','vert','sec'})
    xlim([thisDay+hours(6),thisDay+hours(12)]);
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    s3=subplot(4,1,3);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(sunscanTimes,sunscanPlot,'filled','green');
    scatter(vertTimes,vertPlot,'filled','magenta');
    scatter(secTimes,secPlot,'filled','black');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,5.5]);
    yticks=-0:5;
    yticklabels({'missing','sur','rhi','sunscan','vert','sec'})
    xlim([thisDay+hours(12),thisDay+hours(18)]);
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    s4=subplot(4,1,4);
    hold on
    scatter(surTimes,surPlot,'filled','blue');
    scatter(rhiTimes,rhiPlot,'filled','cyan');
    scatter(sunscanTimes,sunscanPlot,'filled','green');
    scatter(vertTimes,vertPlot,'filled','magenta');
    scatter(secTimes,secPlot,'filled','black');
    scatter(noDataTime,noDataTimeNan,'+','red');
    ylim([-0.5,5.5]);
    yticks=-0:5;
    yticklabels({'missing','sur','rhi','sunscan','vert','sec'})
    xlim([thisDay+hours(18),thisDay+hours(24)]);
    title(datestr(thisDay,'yyyy mm dd'));
    grid on
    box on

    set(gcf,'PaperPositionMode','auto')
    print(f1,[figdir,'dataGaps_timeSeries_',datestr(thisDay,'yyyymmdd'),'.png'],'-dpng','-r0');

end