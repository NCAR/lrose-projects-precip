function [dataSmoothed] = smoothByArea(data,X,Y,km,scanType,az)
% Smooth input data over a certain area in both x an y direction
dataSmoothed=nan(size(data));

distRange=mean(mean(sqrt(diff(X,1,2).^2+diff(Y,1,2).^2)));
distAng=mean(sqrt(diff(X,1,1).^2+diff(Y,1,1).^2),1);

pointsRange=round(km/distRange);
pointsAng=round(km./distAng);
pointsAng(pointsAng<1)=1;

runMeanRange=movmedian(data,pointsRange,2,'omitnan');

azDiff=abs(az(end)-az(1));
if strcmp(scanType,'sur') | azDiff<2
    dataTemp=cat(1,runMeanRange(end-19:end,:),runMeanRange,runMeanRange(1:20,:));
else
    dataTemp=runMeanRange;
end

for ii=1:size(dataTemp,2)
    smoothed=movmedian(dataTemp(:,ii),pointsAng(ii),'omitnan');
    if strcmp(scanType,'sur') | azDiff<2
        smoothed=smoothed(21:end-20);
    end
    dataSmoothed(:,ii)=smoothed;
end
    
dataSmoothed(isnan(data))=nan;
end

