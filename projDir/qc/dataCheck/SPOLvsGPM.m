% Read and diplay S-PolKa data

clear all;
close all;

radar='KAMX'; % KAMX, KBYX, KMLB, KTBW, SPOL

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

infileGPM='20220710_194400.mdv.cf.nc';

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

%% Plot

% Z
close all

figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12);

s1=subplot(2,2,1);
surf(lonGPM,latGPM,dbzGPM(:,:,10),'EdgeColor','none');
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


% print([figdir,'DBZ_vs_ZDR_',dateStr,'_elev_',num2str(elev),'deg.png'],'-dpng','-r0');