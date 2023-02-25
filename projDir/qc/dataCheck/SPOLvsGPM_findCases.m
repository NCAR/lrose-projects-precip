% Read and diplay S-PolKa data

clear all;
close all;

radar='KAMX'; % KAMX, KBYX, KMLB, KTBW, SPOL

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

dbzRange=[12,35];

outdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/GPM/'];

if strcmp(radar,'SPOL')
    indirGroundBase=test;
    indirGPMbase=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/taiwan/netcdf/'];
else
    indirGroundBase=['/scr/cirrus3/rsfdata/projects/precip/grids/nexrad/gridded/',radar,'/'];
    indirGPMbase=['/scr/cirrus3/rsfdata/projects/precip/grids/gpm/florida/netcdf/'];
end

listGPM=dir([indirGPMbase,'*/*.nc']);

listRadar={};

for aa=1:length(listGPM)

    infileGPM=listGPM(aa).name;

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

    if sum(overlap(:))<10000
        disp('Not enough overlapping data points.')
        continue
    end
    
    listRadar{end+1}=infileGPM;
end

save([outdir,'caseList_',radar,'.mat'],'listRadar');