function [z,n,r] = fast_nd_mean(x,win_sz,varargin)
%  Applies fast N-D mean filter
%    usage [z,n] = fast_nd_mean(x,win_sz,'param',value,...)
%  where x is matrix of any dim to apply a mean filter of size
%  given by vector win_sz.  If x is a vector then win_sz can be scalar.
%  z is the output filtered mean, and 'n' is the corresponding number
%  of 'good' points (non-nan's) that went into the mean.  This way
%  you can recover the sum, rather than the mean.
%
%  Params can be:
%      mode = 'partial'; can be string or cell array of strings with
%            possiblilities being 'partial' - to do a partial mean at edges
%            'trunc' to NaN at edges (window runs off the edge).
%            'wrap' to do mean wrapping around edge.
%            If cell array, then each string element dictates what happens
%            at edge for that corresponding dimension
%      nan_mean = 0; nan_mean set to 1 says to perform the mean as a nanmean
%            instead, i.e. if a window contains NaN's, do the mean after
%            removing the nan's
%      inf_mean = 0; inf_mean set to 1 says to perform the mean as if infs 
%            are not there, i.e. if a window contains infs's, do the mean after
%            removing the infs's.  If 0, the mean will be set to inf.
%      circ_mean = 0; if 1, that means to do a circular mean according to the 
%            nyquist.  If 0, don't do a circular mean (similar to modular arithmatic)
%      nyq = 1; can be any real value.  Only used if circ_mean = 1;  This 
%            nyquist sets the equivalence of -nyq is exactly the same as nyq.
%      
%      elliptical = 0; can be 0 or 1.  If 1, then the region of the filter 
%            is elliptical, rather than a multi-dimensional rectangular box.
%            win_sz vector is taken to be the number of elements used along 
%            the axis of the corresponding dimension of the ellipse.  
%
%  Even elements in win_sz: win_sz corresponds to a number of points. 
%    For odd values, the region of interest is symmetric.  E.g., if win_sz
%    is 3, then -1, 0, and 1 index offsets are used to compute the mean
%    for all points.  If even, then the region is not symmetric.  The
%    assymetry is done by skewing 1 point in the positive direction.  E.g.,
%    for win_sz is 2, then 0 and 1 index offsets are used.  This skews
%    the results slightly towards the negative direction.  
%    E.g.: fast_nd_mean([ 0 0 1 0 0 ],2) => [0.0 0.5 0.5 0.0 0.0]
%  
%  A note about the algorithm, to give the maximum flexibility with the fastest
%  performance, an FFT method is used.  This has 1 unfortunate sideaffect in that
%  the output may be prone to more numerical instabilities than if you used a
%  more brute force (i.e. convolution or just iterating like mdapply does);
%  The instabilities should be very small unless the matrix is huge or has very
%  large dynamic range.  Use MDAPPLY - much slower - if this is an issue.  
%  Other possibilities are to break up the matrix into smaller blocks.
%
%  Maybe this should be implemented with convn instead but it was nice to
%  take advantage of the circular nature of FFT's

mode = 'partial';
nan_mean = 0;
inf_mean = 0;
circ_mean = 0;
nyq = 1;
elliptical = 0;

paramparse(varargin);

x_sz = size(x);
% if x is real, make sure we know about this so that we can ensure
% that the output is real
x_real = isreal(x);

% clean up the inputs
if prod(x_sz)==length(x) && length(win_sz)==1 && length(x)>1
  tmp = win_sz;
  win_sz = x_sz;
  win_sz(win_sz>1) = tmp;
elseif prod(x_sz)==length(x) && length(win_sz)==1 && length(x)<=1
  error('filter too big for input');
end;

if length(win_sz)~=length(x_sz)
  error('window does not match dimensionality of input matrix');
end;

if any(win_sz>x_sz)
  warning('window is bigger than matrix in at least 1 dimension');
end;

if ~iscell(mode)
  mode = {mode};
end;

if length(mode)<length(x_sz)
  mode(length(mode)+1:length(x_sz)) = mode(1);
end;

if circ_mean && ~isreal(x)
  error('Cannot to circular means on complex data');
end;

% need to keep track of 4 masks
% nanmask - need to see sphere of influence of a nan by the window
% edgemask - in case of 'trunc' we need to see sphere of influence
%            of edge points along 'trunc' dimensions
% gdptmask - need to know how many good points so can divide the sums
nanmask = isnan(x);
infmask = isinf(x);
edgemask = resize(logical(0),size(x));
% nan's never contribute to total
gdptmask = ~nanmask & ~infmask;

for l = 1:length(x_sz)
  switch mode{l}
   case {'partial','trunc'}
    % pad the end with Nan
    tmp = size(x);
    tmp(l) = win_sz(l)-1;
    x = cat(l,x,resize(NaN,tmp));
    % set the nanmask to 0 in padding
    nanmask = cat(l,nanmask,resize(logical(0),tmp));
    % set the nanmask to 0 in padding
    infmask = cat(l,infmask,resize(logical(0),tmp));
    % edges do not add to good points
    gdptmask = cat(l,gdptmask,resize(logical(0),tmp));
    % if partial - then edges are like good points
    if strcmp(mode{l},'partial')
      edgemask = cat(l,edgemask,resize(logical(0),tmp));
    else
      % if trunc - then edges are like bad points
      edgemask = cat(l,edgemask,resize(logical(1),tmp));
    end;
   case 'wrap'
    % nothing happens here
  end;
end;

% design window function.
if ~elliptical
  win = zeros(size(x));
  tmp = {};
  for l = 1:length(x_sz)
    tmp{l} = 1:win_sz(l);
  end;
  win(tmp{:}) = 1;

  win = circshift(win,-1*floor(win_sz/2));
else
  win = zeros(size(x));
  center = (win_sz-1)/2;
  tmp = 1:length(x_sz);
  for ll = 1:length(x_sz)
    tmpp = tmp;
    tmpp([2 ll]) = tmpp;
    coord = permute(0:size(x,ll)-1,tmpp);
    % center can be 0, .5, 1, etc
    win = bsxfun(@plus,win,(coord-center(ll)).^2./max(center(ll),.1).^2);
  end
  win = double(win<=1);
  win = circshift(win,-1*floor(win_sz/2));
  
end

if circ_mean
  % for circular means, we map to complex circle and then average
  x = exp(i*x*pi/nyq);
end;
  
% can't have Nan's/inf's for the fft method
x(~gdptmask) = 0;
fftwin =  fftn(win); 
% compute sum of x
sx = ifftn(fftn(x).*fftwin);
% calculate how many points in sum were good
n = real(ifftn(fftn(gdptmask).*fftwin));
n = round(n);
old_n = n;

if ~inf_mean && any(infmask(:))
  % if we are not using naninf find places where the number
  % of inf's around is 1 or more
  n_inf = real(ifftn(fftn(infmask).*fftwin));
  ind = round(n_inf)~=0;
  % set sz to Nan and n to 1 there
  sx(ind) = inf;
  n(ind) = 1;
end;

if ~nan_mean && any(nanmask(:))
  % if we are not using nanmean find places where the number
  % of nan's around is 1 or more
  n_nan = real(ifftn(fftn(nanmask).*fftwin));
  ind = round(n_nan)~=0;
  % set sz to Nan and n to 1 there
  sx(ind) = NaN;
  n(ind) = 1;
end;

if any(strcmp(mode,'trunc'))
  % if there is a trunc somewhere than we need to do this
  % find places where there is at least 1 edge point 
  n_nan = real(ifftn(fftn(edgemask).*fftwin));
  ind = round(n_nan)~=0;
  % set sz to Nan and n to 1 there
  sx(ind) = NaN;
  n(ind) = 1;
end;

% just incase - find places where there would be /0
sx(n==0) = NaN;
n(n==0) = 1;

% calculate mean
z = sx./n;

if circ_mean
  % if circular mean then finish calculation
  z = angle(z)*nyq/pi;
end;

% if x was real, ensure that the output is real
if x_real 
  z = real(z);
end;

% chop off padding
tmp = {};
for l = 1:length(x_sz)
  tmp{l} = 1:x_sz(l);
end;
z = z(tmp{:});
n = old_n(tmp{:});


% chop of padding
% tmp = {};
% for l = 1:length(x_sz)
%   tmp{l} = 1:x_sz(l);
% end;
% z = z(tmp{:});
% n = old_n(tmp{:});
