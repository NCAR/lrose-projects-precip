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
subplotInd=round(length(timeAll)/subplotNum);

startDate=timeAll(1);
for jj=1:subplotNum-1
    startInd=subplotInd*jj;
    indTime=timeAll(startInd);
    startDate=[startDate;dateshift(indTime, 'start', 'day')];
end

endDate=cat(1,startDate(2:end),timeAll(end));

%% Plot

close all

figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12);

for jj=1:subplotNum
s1=subplot(2,2,1);
h=surf(XX,YY,data.DBZ_F,'edgecolor','none');
view(2);
caxis([-5 70])
colorbar('XTick',-5:3:70)
title('DBZ (dBZ)')
xlabel('km');
ylabel('km');
s1.Colormap=dbz_default2;
axis equal

grid on
box on

end

% ZDR

s2=subplot(2,2,2);
h=surf(XX,YY,data.ZDR_F,'edgecolor','none');
view(2);
title('ZDR (dB)')
xlabel('km');
ylabel('km');

cols=zdr_default;
s2.Colormap=cols(1:17,:);
caxis([-1.6,1.8]);
colorbar('XTick',-2:0.2:2)

axis equal
grid on
box on

% Scatter plot

% Fit
nanInd=find(isnan(data.DBZ_F(:)) | isnan(data.ZDR_F(:)));
dbzNoNan=data.DBZ_F(:);
dbzNoNan(nanInd)=[];

zdrNoNan=data.ZDR_F(:);
zdrNoNan(nanInd)=[];

x1=dbzRange(1):dbzRange(2);
p1=polyfit(dbzNoNan,zdrNoNan,1);
y1=polyval(p1,x1);
p2=polyfit(dbzNoNan,zdrNoNan,2);
y2=polyval(p2,x1);

% Bin average
[binInds,E]=discretize(dbzNoNan,dbzRange(1):2:dbzRange(2));
binMed=nan(1,length(E)-1);
for ii=1:length(E)-1
    zdrBin=zdrNoNan(binInds==ii);
    binMed(ii)=median(zdrBin);
end

% Plot scatter
subplot(2,2,3)
hold on
scatter(data.DBZ_F(:),data.ZDR_F(:))
l1=plot(x1,y1,'-k','LineWidth',2);
l2=plot(x1,y2,'-c','LineWidth',2);
l3=plot(E(1:end-1)+1,binMed,'-r','LineWidth',2);
ylim([-2,3]);
%ylim([-20,10]);
xlim([E(1)+1,E(end)-1]);

legend([l1,l2,l3],{'Linear fit','Quadratic fit','2 DBZ bin median'},'Location','southeast');

text(15,2.6,['ZDR=',num2str(p1(1),3),'*DBZ+',num2str(p1(2),3)],...
    'fontweight','bold','FontSize',12,'BackgroundColor','w');
text(15,2.3,['ZDR=',num2str(p2(1),3),'*DBZ^2+',num2str(p2(2),3),'*DBZ+',num2str(p2(3),3)],...
    'fontweight','bold','FontSize',12,'BackgroundColor','w');

xlabel('DBZ (dBZ)');
ylabel('ZDR (dB)');

grid on
box on

% Table
dataTable=cat(2,(E(1:end-1)+1)',binMed',y1(2:2:length(x1)-1)',y2(2:2:length(x1)-1)');

uitable('Data', dataTable, 'ColumnName', {'DBZ', 'Bin med', 'Lin','Quad'}, 'Position', [800 125 355 430]);

mtit([dateStr,', elev ',num2str(elev),' deg'],'interpreter','none','xoff',0,'yoff',0.03);

print([figdir,'DBZ_vs_ZDR_',dateStr,'_elev_',num2str(elev),'deg.png'],'-dpng','-r0');