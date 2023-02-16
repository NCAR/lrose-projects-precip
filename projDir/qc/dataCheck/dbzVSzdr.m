% Read and diplay S-PolKa data

clear all;
close all;

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/plots/DBZvsZDR/'];

indir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/sband/sur/';

% Ocean
%infile='cfrad.20220608_020050.439_to_20220608_020652.355_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220607_090050.341_to_20220607_090652.113_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220609_090050.301_to_20220609_090652.147_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220609_202450.849_to_20220609_203052.621_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220611_200050.709_to_20220611_200652.411_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220613_061254.327_to_20220613_061851.293_SPOL_PrecipSur1_SUR.nc'; % Range [0,80]
%infile='cfrad.20220614_141250.221_to_20220614_141851.997_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220614_204850.513_to_20220614_205452.285_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220615_011250.403_to_20220615_011852.177_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220615_020050.325_to_20220615_020652.025_SPOL_PrecipSur1_SUR.nc';

% Land
%infile='cfrad.20220610_000050.125_to_20220610_000652.117_SPOL_PrecipSur1_SUR.nc';
%infile='cfrad.20220615_020050.325_to_20220615_020652.025_SPOL_PrecipSur1_SUR.nc';

% Other
infile='cfrad.20220802_061250.595_to_20220802_061852.229_SPOL_PrecipSur1_SUR.nc'; % elev 2.0 deg,  az 240 - 350 deg, range 10 - 100 km
%infile='cfrad.20220803_120050.601_to_20220803_120652.305_SPOL_PrecipSur1_SUR.nc'; % elev 1.0 deg,  az 230 - 270 deg, range 30 - 120 km
%infile='cfrad.20220804_114850.069_to_20220804_115452.199_SPOL_PrecipSur1_SUR.nc'; % elev 1.0 deg,  az 230 - 270 deg, range 30 - 120 km
%infile='cfrad.20220721_120918.837_to_20220721_121139.109_SPOL_PrecipSur2_SUR.nc'; % elev 0.5 deg, az 240 - 290 deg, range 50 - 120 km
%infile='cfrad.20220723_120918.899_to_20220723_121139.321_SPOL_PrecipSur2_SUR.nc'; % elev 0.5 deg, az 250 - 290 deg, range 50 - 120 km

% Ocean
% elev=1; % Ocean
% minMaxRange=[0,75]; % Ocean default [0,75]
% minMaxAz=[240,360];% Ocean

% Land
% elev=2; % Land
% minMaxRange=[0,50]; % Land default [0,50]
% minMaxAz=[0,90];% Land

% Other
elev=2;
minMaxRange=[10,100];
minMaxAz=[240,350];

dbzRange=[9,51];
%% Read data

dateStr=infile(7:21);

data.DBZ_F=[];
data.ZDR_F=[];

data=read_spol([indir,dateStr(1:8),'/',infile],data);

% Get elevation index
allElev=[];
for ii=1:length(data)
    allElev=[allElev,median(data(ii).elevation)];
end

[~,elevInd]=min(abs(allElev-elev));

data=data(elevInd);

%% Cut range

inFields=fields(data);

goodInds=find(data.range>=minMaxRange(1) & data.range<=minMaxRange(2));
rangeLength=length(data.range);

for ii=1:size(inFields,1)
    thisField=data.(inFields{ii});
    if size(thisField,2)==rangeLength
        data.(inFields{ii})=data.(inFields{ii})(:,goodInds);
    end
end

%% Censor DBZ
data.DBZ_F(data.DBZ_F<dbzRange(1) | data.DBZ_F>dbzRange(2))=nan;
%% Cut azimuth

badInds=find(data.azimuth<=minMaxAz(1) | data.azimuth>=minMaxAz(2));
azLength=length(data.azimuth);

for ii=1:size(inFields,1)
    thisField=data.(inFields{ii});
    if size(thisField,1)==azLength & size(thisField,2)~=1
        data.(inFields{ii})(badInds,:)=nan;
    end
end

%% Plot preparation

ang_p = deg2rad(90-data.azimuth);

angMat=repmat(ang_p,size(data.range,1),1);

XX = (data.range.*cos(angMat));
YY = (data.range.*sin(angMat));

%% Plot

% Z
close all

figure('Position',[200 500 1400 1200],'DefaultAxesFontSize',12);

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