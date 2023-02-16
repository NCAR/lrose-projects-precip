function [b,bintr,bintjm] = gmregress(x,y,alpha)
%GMREGRESS Geometric Mean Regression (Reduced Major Axis Regression).
%   Model II regression should be used when the two variables in the
%   regression equation are random and subject to error, i.e. not 
%   controlled by the researcher. Model I regression using ordinary least 
%   squares underestimates the slope of the linear relationship between the
%   variables when they both contain error. According to Sokal and Rohlf 
%   (1995), the subject of Model II regression is one on which research and
%   controversy are continuing and definitive recommendations are difficult
%   to make.
%
%   GMREGRESS is a Model II procedure. It standardize variables before the 
%   slope is computed. Each of the two variables is transformed to have a 
%   mean of zero and a standard deviation of one. The resulting slope is
%   the geometric mean of the linear regression coefficient of Y on X. 
%   Ricker (1973) coined this term and gives an extensive review of Model
%   II regression. It is also known as Standard Major Axis.
%
%   [B,BINTR,BINTJM] = GMREGRESS(X,Y,ALPHA) returns the vector B of 
%   regression coefficients in the linear Model II and a matrix BINT of the
%   given confidence intervals for B by the Ricker (1973) and Jolicoeur and
%   Mosimann (1968)-McArdle (1988) procedure.
%
%   GMREGRESS treats NaNs in X or Y as missing values, and removes them.
%
%   Syntax: function [b,bintr,bintjm] = gmregress(x,y,alpha)
%
%   Example. From the Box 14.12 (California fish cabezon [Scorpaenichthys 
%   marmoratus]) of Sokal and Rohlf (1995). The data are:
%
%   x=[14,17,24,25,27,33,34,37,40,41,42];
%   y=[61,37,65,69,54,93,87,89,100,90,97];
%
%   Calling on Matlab the function: 
%                [b,bintr,bintjm] = gmregress(x,y)
%
%   Answer is:
%
%   b =
%      12.1938    2.1194
%
%   bintr =
%     -10.6445   35.0320
%       1.3672    2.8715
%   
%   bintjm =
%     -14.5769   31.0996
%       1.4967    3.0010
%
%   Created by A. Trujillo-Ortiz and R. Hernandez-Walls
%             Facultad de Ciencias Marinas
%             Universidad Autonoma de Baja California
%             Apdo. Postal 453
%             Ensenada, Baja California
%             Mexico.
%             atrujo@uabc.edu.mx
%
%   Copyright (C)  June 15, 2010. 
%
%   To cite this file, this would be an appropriate format:
%   Trujillo-Ortiz, A. and R. Hernandez-Walls. (2010). gmregress: 
%      Geometric Mean Regression (Reduced Major Axis Regression).  
%      A MATLAB file. [WWW document]. URL http://www.mathworks.com/
%      matlabcentral/fileexchange/27918-gmregress
%    
%   References:
%   Jolicoeur, P. and Mosimann, J. E. (1968), Intervalles de confiance pour
%              la pente de laxe majeur dune distribution normale 
%              bidimensionnelle. Biomtrie-Praximtrie, 9:121-140.
%   McArdle, B. (1988), The structural relationship:regression in biology.
%              Can. Jour. Zool. 66:2329-2339.
%   Ricker, W. E. (1973), Linear regression in fishery research. J. Fish.
%              Res. Board Can., 30:409-434. 
%   Sokal, R. R. and Rohlf, F. J. (1995), Biometry. The principles and
%              practice of the statistics in biologicalreserach. 3rd. ed.
%              New-York:W.H.,Freeman. [Sections 14.13 and 15.7] 
%

if  nargin < 2
    error('gmregress:TooFewInputs', ...
          'GMREGRESS requires at least two input arguments.');
elseif nargin == 2
    alpha = 0.05;
end

x = x(:); y = y(:);

% Check that matrix (X) and rigth hand side (Y) have compatible dimensions
[n,ncolx] = size(x);
if ~isvector(y)
    error('gmregress:InvalidData', 'Y must be a vector.');
elseif numel(y) ~= n
    error('gmregress:InvalidData', ...
          'The number of rows in Y must equal the number of rows in X.');
end

% Remove missing values, if any
wasnan = (isnan(y) | any(isnan(x),2));
havenans = any(wasnan);
if havenans
   y(wasnan) = [];
   x(wasnan,:) = [];
   n = length(y);
end

R = corrcoef(x,y);
r = R(1,2); %correlation coefficient
s = r/abs(r); %find sign of the correlation coefficient: this former bug 
              %was efficiently corrected thanks to the valuable suggestions
              %given by Holger Goerlitz and Joel E. Cohen. Yes, a negative
              %slope are always negative!
S = cov(x,y);
SCX = S(1,1)*(n-1);
SCY = S(2,2)*(n-1);
SCP = S(1,2)*(n-1);
v = s*sqrt(SCY/SCX); %slope
u = mean(y)-mean(x)*v; %intercept
b = [u v];

%Ricker procedure
SCv = SCY-(SCP^2)/SCX;
N = SCv/(n-2);
sv = sqrt(N/SCX);
t = tinv(1-(alpha/2),n-2);
vi = v-t*sv; %confidence lower limit of slope
vs = v+t*sv; %confidence upper limit of slope
ui = mean(y)-mean(x)*vs; %confidence lower limit of intercept
us = mean(y)-mean(x)*vi; %confidence upper limit of intercept
uint = [ui us];
vint = [vi vs];
if ui > us
    uint([2 1]) = uint([1 2]);
else
end

if vi > vs
    vint([2 1]) = vint([1 2]);
else
end
bintr = [uint;vint];

%Jolicoeur and Mosimann procedure
r = R(1,2);
F =finv(1-alpha,1,n-2);
B = F*(1-r^2)/(n-2);
a = sqrt(B+1);
c = sqrt(B);
qi = v*(a-c); %confidence lower limit of slope
qs = v*(a+c); %confidence upper limit of slope
pi = mean(y)-mean(x)*qs; %confidence lower limit of intercept
ps = mean(y)-mean(x)*qi; %confidence upper limit of intercept
pint = [pi ps];
qint = [qi qs];
if pi > ps
    pint([2 1]) = pint([1 2]);
else
end

if qi > qs
    qint([2 1]) = qint([1 2]);
else
end
bintjm = [pint;qint];

return,