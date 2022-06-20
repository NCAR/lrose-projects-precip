function [saveTimes,saveDataRate,noDataTimeNan]=findGaps_timeSeries(inType,baseDir,dateString,noDataTime,noDataTimeNan)

saveFiles=dir([baseDir,inType,'/',dateString,'/*.iwrf_ts']);
saveTimes=[];
saveBytes=nan(length(saveFiles),1);

for jj=1:size(saveFiles,1)
    inName=saveFiles(jj).name;
    saveTimes=[saveTimes;datetime(str2num(inName(1:4)),str2num(inName(5:6)),str2num(inName(7:8)),...
        str2num(inName(10:11)),str2num(inName(12:13)),str2num(inName(14:15)),str2num(inName(17:19)))];
    saveBytes(jj)=saveFiles(jj).bytes;
end

saveTimeDiff=etime(datevec(saveTimes(2:end)),datevec(saveTimes(1:end-1)));
saveDataRate=saveBytes(1:end-1)./saveTimeDiff;

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
        noDataTimeNan(noDataTime>startGoodTimes(kk) & noDataTime<endGoodTimes(kk))=nan;
    end
end
end