% Read and diplay S-PolKa data

clear all;
close all;

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/precipEvents/'];

indir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/sband/sur/';

startTime=datetime(2022,5,25,0,0,0);
endTime=datetime(2022,8,12,0,0,0);

fileList=makeFileList(indir,startTime,endTime,'xxxxxx20YYMMDDxhhmmss',1);

elev=2;

%% Read data

timeAll=[];
dbzGates=[];

for aa=1:length(fileList)

    disp(fileList{aa});

    data=[];

    data.DBZ_F=[];

    data=read_spol(fileList{aa},data);

    % Only one elev
    % Get elevation index
    allElev=[];
    for ii=1:length(data)
        allElev=[allElev,median(data(ii).elevation)];
    end

    [~,elevInd]=min(abs(allElev-elev));

    data=data(elevInd);

    %% Censor DBZ
    data.DBZ_F(data.DBZ_F<0)=nan;

    %% Get time and gates with refl
    timeAll=[timeAll;data.time(1)];
    dbzGates=[dbzGates;sum(~isnan(data.DBZ_F(:)))];
end

%% Save data
save([figdir,'timeEventGates'],'timeAll','dbzGates');

%% Plot preparation

subplotNum=4;

ticksX=timeAll(1):timeAll(end);
ticksX=dateshift(ticksX, 'start', 'day');
ticksX=cat(2,ticksX,ticksX(end)+hours(24),ticksX(end)+hours(48));

subplotInd=round(length(ticksX)/subplotNum);

startDate=ticksX(1);
for jj=1:subplotNum-1
    startInd=subplotInd*jj;
    startDate=[startDate;ticksX(startInd)];
end

endDate=cat(1,startDate(2:end),ticksX(end));

dbzGatesPlotRaw=dbzGates./max(dbzGates);
dbzGatesPlot=movmedian(dbzGatesPlotRaw,5);

%% Plot

close all

figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12,'renderer','painters');

for jj=1:subplotNum
subplot(subplotNum,1,jj);
inds=find(timeAll>=startDate(jj) & timeAll<=endDate(jj));
plot(timeAll(inds),dbzGatesPlot(inds),'-b','LineWidth',1.5);
xlim([startDate(jj),endDate(jj)]);
xticks(ticksX);
xtickformat('MM/dd');
xtickangle(0);
ylim([0,1]);
if jj==1
    title('PRECIP events');
end
grid on
box on

end

print([figdir,'PRECIPevents.png'],'-dpng','-r0');