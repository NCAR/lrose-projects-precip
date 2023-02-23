% Read and diplay S-PolKa data

clear all;
close all;

radar='KBYX'; % KAMX, KBYX, KMLB, KTBW, SPOL

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

infileGPM='20220714_035646.mdv.cf.nc';

dbzThresh=35;

plotAlt=3; % Altitude of plot level in km

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/GPM/',radar,'/'];

indate=infileGPM(1:8);
intime=datetime(str2num(infileGPM(1:4)),str2num(infileGPM(5:6)),str2num(infileGPM(7:8)), ...
    str2num(infileGPM(10:11)),str2num(infileGPM(12:13)),str2num(infileGPM(14:15)));

if strcmp(radar,'SPOL')
    indirGround=test;
    indirGPM=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/taiwan/netcdf/',indate,'/'];
else
    indirGround=['/scr/cirrus3/rsfdata/projects/precip/grids/nexrad/gridded/',radar,'/',indate,'/'];
    indirGPM=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/florida/netcdf/',indate,'/'];
end

% Get closest ground file
gList=dir([indirGround,'*.nc']);

gTimes=[];
for ii=1:length(gList)
    thisName=gList(ii).name;
    gTimes=cat(1,gTimes,datetime(str2num(thisName(5:8)),str2num(thisName(9:10)),str2num(thisName(11:12)), ...
        str2num(thisName(14:15)),str2num(thisName(16:17)),str2num(thisName(18:19))));
end

timeDiff=etime(datevec(gTimes),datevec(intime));
timeDiff(timeDiff>0)=nan;
fileInd=max(find(~isnan(timeDiff)));

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

%% In GPM, go from the top and remove data that is vertically below the first >35 dBZ grid point

maxDBZ=max(dbzGPM,[],3,'omitnan');
[r,c]=find(maxDBZ>dbzThresh);

dbzCens=dbzGPM;

for ii=1:length(c)
    vertDBZ=squeeze(dbzGPM(r(ii),c(ii),:));
    highInd=find(vertDBZ>dbzThresh,1,'last');
    dbzCens(r(ii),c(ii),1:highInd)=nan;
end

%% Get overlapping inds and compare

overlap=find(~isnan(dbzCens) & ~isnan(dbzGround));

oGPM=dbzCens(overlap);
oGr=dbzGround(overlap);

%% Fit

dbzRange=[12,35];

x1=dbzRange(1):0.5:dbzRange(2);
p1=polyfit(oGr,oGPM,1);
y1=polyval(p1,x1);

%% Plot

[~,altInd]=min(abs(altGPM-plotAlt));

% GPM
close all

figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12);

s1=subplot(2,2,1);
surf(lonGPM,latGPM,dbzGPM(:,:,altInd),'EdgeColor','none');
view(2);
caxis([-5 70])
colorbar('XTick',-5:3:70)
title('GPM DBZ (dBZ)')
xlabel('Longitude');
ylabel('Latitude');
s1.Colormap=dbz_default2;
xlim([min(lonGPM),max(lonGPM)]);
ylim([min(latGPM),max(latGPM)]);
axis equal

% Ground

s2=subplot(2,2,2);
surf(lonGround,latGround,dbzGround(:,:,altInd),'EdgeColor','none');
view(2);
caxis([-5 70])
colorbar('XTick',-5:3:70)
title('Ground DBZ (dBZ)')
xlabel('Longitude');
ylabel('Latitude');
s2.Colormap=dbz_default2;
axis equal
xlim([min(lonGround),max(lonGround)]);
ylim([min(latGround),max(latGround)]);

s3=subplot(2,2,3);
hold on
scatter(oGr,oGPM);
l1=plot([dbzRange(1),dbzRange(2)],[dbzRange(1),dbzRange(2)],'-k','LineWidth',2);
l2=plot(x1,y1,'-r','LineWidth',2);
axis equal
xlim([dbzRange(1),dbzRange(2)]);
ylim([dbzRange(1),dbzRange(2)]);

grid on
box on

% print([figdir,'DBZ_vs_ZDR_',dateStr,'_elev_',num2str(elev),'deg.png'],'-dpng','-r0');