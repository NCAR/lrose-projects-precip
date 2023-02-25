% Read and diplay S-PolKa data

clear all;
close all;

radar='KAMX'; % KAMX, KBYX, KMLB, KTBW, SPOL

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

dbzRange=[12,35];

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/GPM/'];

if strcmp(radar,'SPOL')
    indirGroundBase=test;
    indirGPMbase=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/taiwan/netcdf/'];
else
    indirGroundBase=['/scr/cirrus3/rsfdata/projects/precip/grids/nexrad/gridded/',radar,'/'];
    indirGPMbase=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/florida/netcdf/'];
end

load([figdir,'caseList_',radar,'.mat']);

oGrAll=[];
oGPMall=[];

for aa=1:length(listRadar)

    infileGPM=listRadar{aa};

    disp(infileGPM);

    indate=infileGPM(1:8);
    intime=datetime(str2num(infileGPM(1:4)),str2num(infileGPM(5:6)),str2num(infileGPM(7:8)), ...
        str2num(infileGPM(10:11)),str2num(infileGPM(12:13)),str2num(infileGPM(14:15)));

    indirGround=[indirGroundBase,indate,'/'];
    indirGPM=[indirGPMbase,indate,'/'];

    % Get closest ground file
    gList=dir([indirGround,'*.nc']);

    if isempty(gList)
        disp('No ground data on this day.')
        continue
    end

    gTimes=[];
    for ii=1:length(gList)
        thisName=gList(ii).name;
        gTimes=cat(1,gTimes,datetime(str2num(thisName(5:8)),str2num(thisName(9:10)),str2num(thisName(11:12)), ...
            str2num(thisName(14:15)),str2num(thisName(16:17)),str2num(thisName(18:19))));
    end

    timeDiff=etime(datevec(gTimes),datevec(intime));
    timeDiff(timeDiff>0)=nan;
    fileInd=max(find(~isnan(timeDiff)));

    if isempty(fileInd) | abs(timeDiff(fileInd))>300
        disp('No ground data within 5 minutes.')
        continue
    end

    infileGround=gList(fileInd).name;

    %% Load Data

    % GPM
    lonGPM=ncread([indirGPM,infileGPM],'x0');
    latGPM=ncread([indirGPM,infileGPM],'y0');
    altGPM=ncread([indirGPM,infileGPM],'z0');

    dbzGPM=ncread([indirGPM,infileGPM],'DBZ');

    % Ground
    lonGround=ncread([indirGround,infileGround],'x0');
    latGround=ncread([indirGround,infileGround],'y0');
    altGround=ncread([indirGround,infileGround],'z0');

    dbzGround=ncread([indirGround,infileGround],'REF');

    %% In Ground, go from the top and remove data that is vertically below the first >35 dBZ grid point

    maxDBZ=max(dbzGround,[],3,'omitnan');
    [r,c]=find(maxDBZ>dbzRange(2));

    dbzCensGPM=dbzGPM;
    dbzCensGround=dbzGround;
    
    for ii=1:length(c)
        vertDBZ=squeeze(dbzGround(r(ii),c(ii),:));
        highInd=find(vertDBZ>dbzRange(2),1,'last');
        dbzCensGround(r(ii),c(ii),1:highInd)=nan;
    end

    %% Get overlapping inds and compare

    overlap=~isnan(dbzCensGPM) & ~isnan(dbzCensGround);
    dbzCensGround(~overlap)=nan;
    dbzCensGPM(~overlap)=nan;

    if sum(overlap(:))<5000
        disp('Not enough overlapping data points.')
        continue
    end

    oGPM=dbzCensGPM(overlap==1);
    oGr=dbzCensGround(overlap==1);

    oGPMall=cat(1,oGPMall,oGPM);
    oGrAll=cat(1,oGrAll,oGr);

    %% Fit and counts

    x1=dbzRange(1):0.5:dbzRange(2);
    p1=polyfit(oGr,oGPM,1);
    y1=polyval(p1,x1);

    % Counts
    xedge=dbzRange(1):0.5:dbzRange(2);
    yedge=dbzRange(1):0.5:dbzRange(2);
    [N,~,~]=histcounts2(oGr,oGPM,xedge,yedge);
    N=N';
   
    N=cat(1,N,N(end,:));
    N=cat(2,N,N(:,end));
    N(N==0)=nan;
    %% Plot

    plotGround=max(dbzCensGround,[],3,'omitnan');
    plotGPM=max(dbzCensGPM,[],3,'omitnan');

    allNanRows=all(isnan(plotGPM),1);
    firstRow=find(allNanRows==0,1,'first');
    lastRow=find(allNanRows==0,1,'last');

    allNanCols=all(isnan(plotGPM),2);
    firstCol=find(allNanCols==0,1,'first');
    lastCol=find(allNanCols==0,1,'last');
    
    % GPM
    close all

    figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12);

    s1=subplot(2,2,1);
    surf(lonGPM,latGPM,plotGPM,'EdgeColor','none');
    view(2);
    caxis([-5 70])
    colorbar('XTick',-5:3:70)
    title('GPM DBZ (dBZ)')
    xlabel('Longitude');
    ylabel('Latitude');
    s1.Colormap=dbz_default2;
    axis equal
    xlim([lonGPM(firstRow-1),lonGPM(lastRow+1)]);
    ylim([latGPM(firstCol-1),latGPM(lastCol+1)]);

    grid on
    box on
    
    % Ground

    s2=subplot(2,2,2);
    surf(lonGround,latGround,plotGround,'EdgeColor','none');
    view(2);
    caxis([-5 70])
    colorbar('XTick',-5:3:70)
    title([radar,' DBZ (dBZ)']);
    xlabel('Longitude');
    ylabel('Latitude');
    s2.Colormap=dbz_default2;
    axis equal
    xlim([lonGPM(firstRow-1),lonGPM(lastRow+1)]);
    ylim([latGPM(firstCol-1),latGPM(lastCol+1)]);

    grid on
    box on
    
    s3=subplot(2,2,3);
    hold on
    scatter(oGr,oGPM);
    l1=plot([dbzRange(1),dbzRange(2)],[dbzRange(1),dbzRange(2)],'-k','LineWidth',2);
    l2=plot(x1,y1,'-r','LineWidth',2);
    axis equal
    xlim([dbzRange(1),dbzRange(2)]);
    ylim([dbzRange(1),dbzRange(2)]);

    xlabel(radar)
    ylabel('GPM');
    title(['Number of points: ',num2str(sum(overlap(:)))]);

    grid on
    box on

    s4=subplot(2,2,4);
    s4.Colormap=jet;
    hold on
    surf(xedge(1:end),yedge(1:end),N,'EdgeColor','none');
    view(2);
    plot([dbzRange(1),dbzRange(2)],[dbzRange(1),dbzRange(2)],'-r','LineWidth',2);
    plot([dbzRange(1),dbzRange(2)-1],[dbzRange(1)+1,dbzRange(2)],'--r','LineWidth',2);
    plot([dbzRange(1)+1,dbzRange(2)],[dbzRange(1),dbzRange(2)-1],'--r','LineWidth',2);
    axis equal
    xlim([dbzRange(1),dbzRange(2)]);
    ylim([dbzRange(1),dbzRange(2)]);

    s4.SortMethod='childorder';

    xlabel(radar)
    ylabel('GPM');
    title(['Number of points: ',num2str(sum(overlap(:)))]);

    grid on
    box on

    mtit([radar,' vs GPM ',infileGPM(1:15)],'interpreter','none','xoff',0,'yoff',0.03);

    print([figdir,radar,'_GPM_',infileGPM(1:15),'.png'],'-dpng','-r0');
end

%% Fit and counts

x1=dbzRange(1):0.5:dbzRange(2);
p1=polyfit(oGrAll,oGPMall,1);
y1=polyval(p1,x1);

% Counts
xedge=dbzRange(1):0.5:dbzRange(2);
yedge=dbzRange(1):0.5:dbzRange(2);
[N,~,~]=histcounts2(oGrAll,oGPMall,xedge,yedge);
N=N';

N=cat(1,N,N(end,:));
N=cat(2,N,N(:,end));
N(N==0)=nan;
%% Plot

% GPM
close all

figure('Position',[200 500 1200 600],'DefaultAxesFontSize',12);

s1=subplot(1,2,1);
hold on
scatter(oGrAll,oGPMall);
l1=plot([dbzRange(1),dbzRange(2)],[dbzRange(1),dbzRange(2)],'-k','LineWidth',2);
l2=plot(x1,y1,'-r','LineWidth',2);
axis equal
xlim([dbzRange(1),dbzRange(2)]);
ylim([dbzRange(1),dbzRange(2)]);

xlabel(radar)
ylabel('GPM');
title(['Number of points: ',num2str(length(oGPMall))]);

grid on
box on

s2=subplot(1,2,2);
s2.Colormap=jet;
hold on
surf(xedge(1:end),yedge(1:end),N,'EdgeColor','none');
view(2);
plot([dbzRange(1),dbzRange(2)],[dbzRange(1),dbzRange(2)],'-r','LineWidth',2);
plot([dbzRange(1),dbzRange(2)-1],[dbzRange(1)+1,dbzRange(2)],'--r','LineWidth',2);
plot([dbzRange(1)+1,dbzRange(2)],[dbzRange(1),dbzRange(2)-1],'--r','LineWidth',2);
axis equal
xlim([dbzRange(1),dbzRange(2)]);
ylim([dbzRange(1),dbzRange(2)]);

s2.SortMethod='childorder';

xlabel(radar)
ylabel('GPM');
title(['Number of points: ',num2str(length(oGPMall))]);

grid on
box on

mtit([radar,' vs GPM'],'interpreter','none','xoff',0,'yoff',0.01);

print([figdir,radar,'_GPM.png'],'-dpng','-r0');