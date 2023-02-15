% Read and diplay S-PolKa data

clear all;
close all;

addpath(genpath('/h/eol/romatsch/gitPriv/utils/'));

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/'];

indir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/sband/sur/20220608/';
infile='cfrad.20220608_020050.439_to_20220608_020652.355_SPOL_PrecipSur1_SUR.nc';

elev=1;
minMaxRange=[0,75];
minMaxAz=[240,360];

%% Read data

data.DBZ_F=[];
data.ZDR_F=[];

data=read_spol([indir,infile],data);

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
data.DBZ_F(data.DBZ_F<10 | data.DBZ_F>50)=nan;
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

dateStr=infile(7:21);
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

x1=10:50;
p1=polyfit(dbzNoNan,zdrNoNan,1);
y1=polyval(p1,x1);
p2=polyfit(dbzNoNan,zdrNoNan,2);
y2=polyval(p2,x1);

% Bin average
binInds=discretize(dbzNoNan,10:2:50);
binMed=[];
for ii=1:max(binInds)
    zdrBin=zdrNoNan(binInds==ii);
    binMed=[binMed,median(zdrBin)];
end

% Plot scatter
subplot(2,2,3)
hold on
scatter(data.DBZ_F(:),data.ZDR_F(:))
l1=plot(x1,y1,'-k','LineWidth',2);
l2=plot(x1,y2,'-c','LineWidth',2);
l3=plot(11:2:49,binMed,'-r','LineWidth',2);
ylim([-2,3]);

legend([l1,l2,l3],{'Linear fit','Quadratic fit','2 DBZ bin median'},'Location','southeast');

text(15,2.6,['ZDR=',num2str(p1(1),3),'*DBZ+',num2str(p1(2),3)],...
    'fontweight','bold','FontSize',12,'BackgroundColor','w');
text(15,2.3,['ZDR=',num2str(p2(1),3),'*DBZ^2+',num2str(p2(2),3),'*DBZ+',num2str(p2(3),3)],...
    'fontweight','bold','FontSize',12,'BackgroundColor','w');

xlabel('DBZ (dBZ)');
ylabel('ZDR (dB)');

grid on
box on

mtit([dateStr,', elev ',num2str(elev),' deg'],'interpreter','none','xoff',0,'yoff',.03);

print([figdir,'DBZ_vs_ZDR_',dateStr,'_elev_',num2str(elev),'deg.png'],'-dpng','-r0');