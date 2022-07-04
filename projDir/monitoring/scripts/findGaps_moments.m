function [saveTimes,noDataTimeNan]=findGaps_moments(inType,baseDir,dateString,noDataTime,noDataTimeNan)

saveFiles=dir([baseDir,inType,'/',dateString,'/*.nc']);
saveTimes=[];
saveDBZ=[];

for jj=1:size(saveFiles,1)    
    inName=saveFiles(jj).name;
    baseTime=ncread([saveFiles(jj).folder,'/',inName],'time_coverage_start');
    baseTime=baseTime';
    baseTimeNum=datetime(str2num(baseTime(1:4)),str2num(baseTime(6:7)),str2num(baseTime(9:10)),...
        str2num(baseTime(12:13)),str2num(baseTime(15:16)),str2num(baseTime(18:19)));
    inTime=ncread([saveFiles(jj).folder,'/',inName],'time');
    fileTime=baseTimeNum+seconds(inTime);
    saveTimes=cat(1,saveTimes,fileTime);
end

saveTimeDiff=etime(datevec(saveTimes(2:end)),datevec(saveTimes(1:end-1)));

if ~isempty(saveTimes)
    goodTimes=zeros(size(saveTimeDiff));
    goodTimes(saveTimeDiff<120)=1;
    diffGoodTimes=diff(goodTimes);

    startGoodInds=find(diffGoodTimes==1)+1;
    endGoodInds=find(diffGoodTimes==-1)+1;

    startGoodTimes=saveTimes(startGoodInds);
    startGoodTimes=cat(1,saveTimes(1),startGoodTimes);
    endGoodTimes=saveTimes(endGoodInds);
    endGoodTimes=cat(1,endGoodTimes,saveTimes(end));

    for kk=1:length(startGoodTimes)
        noDataTimeNan(noDataTime>=startGoodTimes(kk) & noDataTime<=endGoodTimes(kk))=nan;
    end
end
end