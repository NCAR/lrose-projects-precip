% Find data gaps in time series

clear all
close all

scanType='rhi';

startDate=datetime(2022,5,25);
endDate=datetime(2022,8,12); % This day is included

dir1=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc1/rate/sband/v1.0/',scanType,'/'];
dir2=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc2/rate/sband/v2.0/',scanType,'/'];

figdir=['/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc2/rate/plots/fileComp/'];

fileList1=dir([dir1,'*/*.nc']);
fileList2=dir([dir2,'*/*.nc']);

%% What is missing in QC1?

filesT1=struct2table(fileList1);
filesT2=struct2table(fileList2);

filesT1.date=[];
filesT1.isdir=[];
filesT1.datenum=[];

filesT2.date=[];
filesT2.isdir=[];
filesT2.datenum=[];

filesT1=renamevars(filesT1,["name","folder","bytes"],["file1","dir1","bytes1"]);
filesT2=renamevars(filesT2,["name","folder","bytes"],["file2","dir2","bytes2"]);

time1=[];
for ii=1:size(filesT1,1)
    thisname=filesT1.file1{ii};
    time1=cat(1,time1,datetime(str2num(thisname(7:10)),str2num(thisname(11:12)),str2num(thisname(13:14)),...
        str2num(thisname(16:17)),str2num(thisname(18:19)),str2num(thisname(20:21))));
end

time2=[];
for ii=1:size(filesT2,1)
    thisname=filesT2.file2{ii};
    time2=cat(1,time2,datetime(str2num(thisname(7:10)),str2num(thisname(11:12)),str2num(thisname(13:14)),...
        str2num(thisname(16:17)),str2num(thisname(18:19)),str2num(thisname(20:21))));
end

% Round to minute
time1=dateshift(time1,'start','minute','nearest');
time2=dateshift(time2,'start','minute','nearest');

[in1,l1]=ismember(time1,time2);
[in2,l2]=ismember(time2,time1);

only1=filesT1(in1==0,:);
only2=filesT2(in2==0,:);

u1=etime(datevec(time1(2:end)),datevec(time1(1:end-1)));
u1=cat(1,u1,100);
u2=etime(datevec(time2(2:end)),datevec(time2(1:end-1)));
u2=cat(1,u2,100);

both1=filesT1(in1==1 & u1~=0,:);
both2=filesT2(in2==1 & u2~=0,:);

sizeDiff=both2.bytes2-both1.bytes1;

maxSize=max(cat(2,both1.bytes1,both2.bytes2),[],2);
b1norm=both1.bytes1./maxSize*100;
b2norm=both2.bytes2./maxSize*100;

sizeDiffPerc=b2norm-b1norm;

bothTime=time1(in1==1 & u1~=0);

%% Save

writetable(only1,[figdir,'filesOnlyInQC1_',scanType,'.txt']);
writetable(only2,[figdir,'filesOnlyInQC2_',scanType,'.txt']);

u1d=find(u1==0);
u1dd=cat(1,u1d,u1d+1);
u1dd=sort(u1dd);
dupl1=filesT1(u1dd,:);

u2d=find(u2==0);
u2dd=cat(1,u2d,u2d+1);
u2dd=sort(u2dd);
dupl2=filesT2(u2dd,:);

if ~isempty(dupl1)
    writetable(dupl1,[figdir,'withinOneMinQC1_',scanType,'.txt']);
end
if ~isempty(dupl2)
    writetable(dupl2,[figdir,'withinOneMinQC2_',scanType,'.txt']);
end

if strcmp(scanType,'sur')
    bigDiff=cat(2,both1(sizeDiffPerc>5 | sizeDiffPerc<-10,:),both2(sizeDiffPerc>5 | sizeDiffPerc<-10,:));
    bigDiff.bytes2minus1=bigDiff.bytes2-bigDiff.bytes1;
end

if strcmp(scanType,'rhi')
    bigDiff=cat(2,both1(sizeDiff>10000000 | sizeDiff<-5500000,:),both2(sizeDiff>10000000 | sizeDiff<-5500000,:));
    bigDiff.bytes2minus1=bigDiff.bytes2-bigDiff.bytes1;
end

writetable(bigDiff,[figdir,'bigSizeDiff_',scanType,'.txt']);

%% Plot

close all
f1 = figure('Position',[200 500 1600 700],'DefaultAxesFontSize',12);
hold on
scatter(bothTime,sizeDiff);
if strcmp(scanType,'rhi')
    plot([bothTime(1),bothTime(end)],[-5500000,-5500000],'-r');
    plot([bothTime(1),bothTime(end)],[10000000,10000000],'-r');
end
xlim([bothTime(1),bothTime(end)]);
box on
ylabel('Bytes')
title(['File size difference QC2 minus QC1 ',scanType])
set(gcf,'PaperPositionMode','auto')
print(f1,[figdir,'fileSizeDiff_',scanType,'.png'],'-dpng','-r0');

f2 = figure('Position',[200 500 1600 700],'DefaultAxesFontSize',12);
hold on
scatter(bothTime,sizeDiffPerc);
if strcmp(scanType,'sur')
    plot([bothTime(1),bothTime(end)],[-10,-10],'-r');
    plot([bothTime(1),bothTime(end)],[5,5],'-r');
end
xlim([bothTime(1),bothTime(end)]);
box on
ylabel('Percent (%)')
title(['File size difference QC2 minus QC1 ',scanType])
set(gcf,'PaperPositionMode','auto')
print(f2,[figdir,'fileSizeDiffPerc_',scanType,'.png'],'-dpng','-r0');