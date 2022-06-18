% Find data gaps in time series

clear all
close all

dataType='spoldrx';

startDate=datetime(2022,5,23);
endDate=datetime(2022,6,4); % This day is included

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

    noDataTime=thisDay:minutes(1):thisDay+hours(24);
    noDataTimeNan=ones(size(noDataTime));
    noDataTimeNan=-noDataTimeNan;

    % 'save' directory
    saveFiles=dir([baseDir,'save/',dateString,'/*.iwrf_ts']);
    saveTimes=[];
    saveBytes=nan(length(saveFiles),1);

    for jj=1:size(saveFiles,1)
        inName=saveFiles(jj).name;
        saveTimes=[saveTimes;datetime(str2num(inName(1:4)),str2num(inName(5:6)),str2num(inName(7:8)),...
            str2num(inName(10:11)),str2num(inName(12:13)),str2num(inName(14:15)),str2num(inName(17:19)))];
        saveBytes(jj)=saveFiles(jj).bytes;
    end

    saveTimeDiff=etime(datevec(saveTimes(2:end)),datevec(saveTimes(1:end-1)));
    saveDataRate=saveBytes(1:end-1)./saveTimeDiff;

    if ~isempty(saveTimes)
        goodTimes=zeros(size(saveTimeDiff));
        goodTimes(saveTimeDiff<120)=1;
        diffGoodTimes=diff(goodTimes);

        startGoodInds=find(diffGoodTimes==1)+1;
        endGoodInds=find(diffGoodTimes==-1)+1;

        startGoodTimes=saveTimes(startGoodInds);
        startGoodTimes=cat(1,saveTimes(1),startGoodTimes);
        endGoodTimes=saveTimes(endGoodInds);
        endGoodTimes=cat(1,endGoodTimes,saveTimes(end));

        for kk=1:length(startGoodTimes)
            noDataTimeNan(noDataTime>startGoodTimes(kk) & noDataTime<endGoodTimes(kk))=nan;
        end
    end

    % 'sunscan' directory
    sunscanFiles=dir([baseDir,'sunscan/',dateString,'/*.iwrf_ts']);
    sunscanTimes=[];
    sunscanBytes=nan(length(sunscanFiles),1);

    for jj=1:size(sunscanFiles,1)
        inName=sunscanFiles(jj).name;
        sunscanTimes=[sunscanTimes;datetime(str2num(inName(1:4)),str2num(inName(5:6)),str2num(inName(7:8)),...
            str2num(inName(10:11)),str2num(inName(12:13)),str2num(inName(14:15)),str2num(inName(17:19)))];
        sunscanBytes(jj)=sunscanFiles(jj).bytes;
    end

    sunscanTimeDiff=etime(datevec(sunscanTimes(2:end)),datevec(sunscanTimes(1:end-1)));
    sunscanDataRate=sunscanBytes(1:end-1)./sunscanTimeDiff;

    if ~isempty(sunscanTimes)
        goodTimes=zeros(size(sunscanTimeDiff));
        goodTimes(sunscanTimeDiff<120)=1;
        diffGoodTimes=diff(goodTimes);

        startGoodInds=find(diffGoodTimes==1)+1;
        endGoodInds=find(diffGoodTimes==-1)+1;

        startGoodTimes=sunscanTimes(startGoodInds);
        startGoodTimes=cat(1,sunscanTimes(1),startGoodTimes);
        endGoodTimes=sunscanTimes(endGoodInds);
        endGoodTimes=cat(1,endGoodTimes,sunscanTimes(end));

        for kk=1:length(startGoodTimes)
            noDataTimeNan(noDataTime>startGoodTimes(kk) & noDataTime<endGoodTimes(kk))=nan;
        end

    end
    % 'vert' directory
    vertFiles=dir([baseDir,'vert/',dateString,'/*.iwrf_ts']);
    vertTimes=[];
    vertBytes=nan(length(vertFiles),1);

    for jj=1:size(vertFiles,1)
        inName=vertFiles(jj).name;
        vertTimes=[vertTimes;datetime(str2num(inName(1:4)),str2num(inName(5:6)),str2num(inName(7:8)),...
            str2num(inName(10:11)),str2num(inName(12:13)),str2num(inName(14:15)),str2num(inName(17:19)))];
        vertBytes(jj)=vertFiles(jj).bytes;
    end

    vertTimeDiff=etime(datevec(vertTimes(2:end)),datevec(vertTimes(1:end-1)));
    vertDataRate=vertBytes(1:end-1)./vertTimeDiff;

    if ~isempty(vertTimes)
        goodTimes=zeros(size(vertTimeDiff));
        goodTimes(vertTimeDiff<120)=1;
        diffGoodTimes=diff(goodTimes);

        startGoodInds=find(diffGoodTimes==1)+1;
        endGoodInds=find(diffGoodTimes==-1)+1;

        startGoodTimes=vertTimes(startGoodInds);
        startGoodTimes=cat(1,vertTimes(1),startGoodTimes);
        endGoodTimes=vertTimes(endGoodInds);
        endGoodTimes=cat(1,endGoodTimes,vertTimes(end));
    end

    for kk=1:length(startGoodTimes)
        noDataTimeNan(noDataTime>startGoodTimes(kk) & noDataTime<endGoodTimes(kk))=nan;
    end

    %% Plot

    disp(['Plotting ',dateString]);

    close all
    ylimits=[-1.5 12];

    f1=figure('DefaultAxesFontSize',12,'Position',[0 300 1500 1200],'renderer','painters','visible','on');

    s1=subplot(4,1,1);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'filled','red');
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
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'filled','red');
    ylim(ylimits);
    xlim([thisDay+hours(6),thisDay+hours(12)]);
    ylabel('MB s^{-1}');
    grid on
    box on

    s3=subplot(4,1,3);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'filled','red');
    ylim(ylimits);
    xlim([thisDay+hours(12),thisDay+hours(18)]);
    ylabel('MB s^{-1}');
    grid on
    box on

    s4=subplot(4,1,4);
    hold on
    scatter(saveTimes(1:end-1),saveDataRate./1000000,'filled','blue');
    scatter(sunscanTimes(1:end-1),sunscanDataRate./1000000,'filled','green');
    scatter(vertTimes(1:end-1),vertDataRate./1000000,'filled','cyan');
    scatter(noDataTime,noDataTimeNan,'filled','red');
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