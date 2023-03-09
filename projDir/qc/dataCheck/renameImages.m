% Rename images with correct time

clear all;
close all;

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/dataCheck/utils/'));

camera='east';

shiftHours=8;
shiftMins=8;

basedir='/scr/cirrus3/rsfdata/projects/precip/images/spol_cams/';

indir=[basedir,camera,'/wrongTime/'];

fileList=dir([indir,'*/*.jpg']);

addMins=-(shiftHours*60+shiftMins);

for ii=1:length(fileList)
    nameIn=fileList(ii).name;
    disp(nameIn);
    fileTime=datetime(str2num(nameIn(1:4)),str2num(nameIn(5:6)),str2num(nameIn(7:8)), ...
        str2num(nameIn(10:11)),str2num(nameIn(12:13)),0);

    fileTimeUTC=fileTime+minutes(addMins);

    outDir=[basedir,camera,'/timeTest/',datestr(fileTimeUTC,'yyyymmdd'),'/'];
    outName=[datestr(fileTimeUTC,'yyyymmdd-HHMM'),'.jpg'];

    destName=[outDir,outName];

    sourceName=[fileList(ii).folder,'/',nameIn];
    copyfile(sourceName,destName);
end

