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

%% Z
close all

figure('Position',[200 500 1800 600],'DefaultAxesFontSize',12);

s1=subplot(1,3,1);
h=surf(XX,YY,data.DBZ_F,'edgecolor','none');
view(2);
caxis([-5 70])
colorbar('XTick',-5:3:70)
title('Zh (dBZ)')
xlabel('km');
ylabel('km');
s1.Colormap=dbz_default2;
axis equal


%% ZDR

s2=subplot(1,3,2);
h=surf(XX,YY,data.ZDR_F,'edgecolor','none');
view(2);
title('Zdr (dB)')
xlabel('km');
ylabel('km');

cols=zdr_default;
s2.Colormap=cols(1:17,:);
caxis([-1.6,1.8]);
colorbar('XTick',-2:0.2:2)
%colLims=[-inf,-20,-2,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3,4,5,6,8,10,15,20,50,99,inf];
%applyColorScale(h,data.ZDR_F,colM,colLims);

axis equal

%% Scatter plot

% Fit
nanInd=find(isnan(data.DBZ_F(:)) | isnan(data.ZDR_F(:)));
dbzNoNan=data.DBZ_F(:);
dbzNoNan(nanInd)=[];

zdrNoNan=data.ZDR_F(:);
zdrNoNan(nanInd)=[];

p=polyfit(dbzNoNan,zdrNoNan,2);
x1=10:50;
y1=polyval(p,x1);

subplot(1,3,3)
hold on
scatter(data.DBZ_F(:),data.ZDR_F(:))
plot(x1,y1,'-k','LineWidth',2);
ylim([-2,3]);

print([figdir,'DBZ_vs_ZDR.png'],'-dpng','-r0');