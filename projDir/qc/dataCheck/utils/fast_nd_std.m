function [z,n] = fast_nd_std(x,win_sz,varargin)
%  Applies fast N-D std filter
%    usage [z,n] = fast_nd_std(x,win_sz,'param',value,...)
%  where x is matrix of any dim to apply a std filter of size
%  given by vector win_sz.  If x is a vector then win_sz can be scalar.
%  z is the output filtered std, and 'n' is the corresponding number
%  of 'good' points (non-nan's) that went into the std.  This way
%  you can recover the sum, rather than the std.
%  
%  Params can be:
%      mode = 'partial'; can be string or cell array of strings with
%            possiblilities being 'partial' - to do a partial std at edges
%            'trunc' to NaN at edges (window runs off the edge).
%            'wrap' to do std wrapping around edge.
%            If cell array, then each string element dictates what happens
%            at edge for that corresponding dimension
%      nan_std = 0; nan_std set to 1 says to perform the std as a nanstd
%            instead, i.e. if a window contains NaN's, do the std after
%            removing the nan's
%      inf_std = 0; inf_std set to 1 says to perform the mean as if infs 
%            are not there, i.e. if a window contains infs's, do the std after
%            removing the infs's.  If 0, the std will be set to inf.
%      circ_std = 0; if 1, that stds to do a circular std according to the 
%            nyquist.  If 0, don't do a circular std (similar to modular arithmatic)
%      nyq = 1; can be any real value.  Only used if circ_std = 1;  This 
%            nyquist sets the equivalence of -nyq is exactly the same as nyq.
%      sample_std = 1; if 1 then calculate sample standard deviations.  If
%            0, then population.
%
%  A note about the algorithm, to give the maximum flexibility with the fastest
%  performance, an FFT method is used.  This has 1 unfortunate sideaffect in that
%  the output may be prone to more numerical instabilities than if you used a
%  more brute force (i.e. convolution or just iterating like mdapply does);
%  The instabilities should be very small unless the matrix is huge or has very
%  large dynamic range.  Use MDAPPLY - much slower - if this is an issue.
%
%  Maybe this should be implemented with convn instead but it was nice to
%  take advantage of the circular nature of FFT's.
%



mode = 'partial';
nan_std = 0;
inf_std = 0;
circ_std = 0;
nyq = 1;
sample_std = 1;
elliptical = 0;
circ_std_mode = 2;

paramparse(varargin);

nan_mean = nan_std;
inf_mean = inf_std;
circ_mean = 0;
parms = varstruct({'inf_mean','nan_mean','circ_mean','mode','elliptical'});

if circ_std
  switch circ_std_mode
    case 1
      % This alternate but more standard version: 
      % nyq/pi*sqrt(-2*log(mean(x))) Also
      % works pretty well: less biased for larger sample sizes, but
      % more biased at lower input STDs.
      % Another problem is that you can get arbitrarily large values
      x = exp(i*x*pi/nyq);
      [z,n] = fast_nd_mean(x,win_sz,parms);
      sp = abs(z);
      z = nyq/pi*sqrt(-2*log(sp))
      z(z<0) = 0;
      
    case 2
      % I do not have a reference for this method.
      % However, it has been verified that it produces about the same as 
      % linear of smaller input stds.
      % ns = [5 10 20 50 100]; stds = [.1:.1:1 2:30 32:2:60]; xx = zeros(length(stds),length(ns)); for ll = 1:length(ns), for kk = 1:length(stds), xx(kk,ll) = mean(fast_nd_std(randn(100000,1)*stds(kk),[ns(ll) 1],'circ_std',1,'nyq',180)); end; end;
      % figure; plot(stds,xx)
      % hold on
      % grid on
      % legend('N=5','N=10','N=20','N=50','N=100')
      % plot(xlim,xlim,'k-')
      % legend('N=5','N=10','N=20','N=50','N=100')
      % xlabel('pre-wrapped STD of Normal Dist (deg)')
      % ylabel('mean circ STD from IMAT')
      % title('Expected Circ STD for various sample sizes from Norm RV')
      % 
      %
      % The alternate version: nyq/pi*sqrt(-2*log(mean(x))) Also
      % works pretty well: less biased for larger sample sizes, but
      % more biased at lower input STDs.

      x = exp(i*x*pi/nyq);
      [z,n] = fast_nd_mean(x,win_sz,parms);
      sp = 1-abs(z);
      z = sp*2*(nyq/pi)^2;
      z(z<0) = 0;
    otherwise
      zx = exp(i*x*pi/nyq);
      [z,n] = fast_nd_mean(zx,win_sz,parms); 
      mean_vals = nyq/pi*angle(z);
      xx = circ_arith(x-mean_vals,nyq);
      error('NOT WORKING YET!');
  end
else
  [m1,n] = fast_nd_mean(x,win_sz,parms);
  [m2] = fast_nd_mean(x.^2,win_sz,parms);
  
  % claculate poplulation variance
  z = m2-m1.^2;  
  z(z<0) = 0;
  
end;

if sample_std
  ind = n==0;
  n(ind) = 2;
  z = z.*n./(n-1);
  n(ind) = 0;
end;

z = sqrt(z);
