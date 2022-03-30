


function [N,NError] = DIALEquationNarrowlySpaced(Online,OnlineInt,Offline,OfflineInt,OnlineBG,OfflineBG,SigmaOn,SigmaOff,BinWidth)
%
%
%
%
%
%
%%
Inside = (Online.*(circshift(Offline, [0, -1])))./((circshift(Online, [0, -1])).*Offline);
del_cross = single(1./(2.*(SigmaOn-SigmaOff).*BinWidth*100));

N           =  (del_cross.*log(Inside));
N(N == inf) = nan;

% error calculation
NError = (1/2./(SigmaOn -SigmaOff )./(BinWidth*100)...
    .*sqrt((OnlineInt+OnlineBG)./OnlineInt.^2 + (circshift(OnlineInt, [0, -1])+OnlineBG)./circshift(OnlineInt, [0, -1]).^2 + ...
           (OfflineInt+OfflineBG)./OfflineInt.^2 + (circshift(OfflineInt, [0, -1])+OfflineBG)./circshift(OfflineInt, [0, -1]).^2));
end