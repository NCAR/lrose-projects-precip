function s = movingstd2(A,k)
% movingstd: efficient windowed standard deviation of a 2-d array
% usage: s = movingstd(x,windowsize)
%
% Central windows around every element of the array will be employed,
% so a windowsize of 1 will generate a sliding window of size
% (2*k+1)*(2*k+1) around every element in the array. Thus, when k=1,
% the sliding window will be a 3x3 window. For k=2, this will result in
% a 5x5 sliding window.
%
% Only central windows are allowed in movingstd2, as opposed to movingstd
% which allowed several window types.
%
% Movingstd2 uses conv2 to compute the standard deviation, using
% the trick of std = sqrt((sum(x.^2) - n*xbar.^2)/(n-1)).
% Beware that this formula can suffer from numerical problems for
% data which is large in magnitude. Your data is automatically
% centered and scaled to alleviate these problems as much as possible.
%
% Along the edges of the array, the window is truncated to fit as
% necessary.
%
% arguments: (input)
%  A   - Array containing the data. Must be numeric, although A will
%        be internally converted to double if it is not double already.
%
%        A should NOT have any INF or NaN elements in it, as that will
%        corrupt the computation.
%
%  k   - size of the sliding window to use
%        Window width is adjusted near the edges as necessary.
%
%        Where k is so large that the window size is actually larger than
%        the array, the window is truncated as necessary.
%
%        k must be an integer
%
%        default: k=2, so a 5x5 window
%
% arguments: (output)
%  s   - array containing the windowed standard deviation.
%        size(A) will be the same as size(s)
%
% Example:
% movingstd2(magic(5),1)
% ans =
%        8.7321       9.8065       8.1343       5.8452        3.594
%        9.2826       8.5065       7.4907       6.6039        4.916
%        7.0711       6.5192       6.1237       6.5192       7.0711
%         4.916       6.6039       7.4907       8.5065       9.2826
%         3.594       5.8452       8.1343       9.8065       8.7321
%
% Author: John D'Errico
% e-mail: woodchips@rochester.rr.com
%   date: 4/8/2016
% check for k default
if (nargin<2) || isempty(k)
  % supply the default:
  k = 1;
elseif ~isnumeric(k) || ~isscalar(k) || (k < 1) || (k~=round(k))
  error('If supplied, k must be integer, positive, scalar')
end
% size of the array
n = size(A);
if numel(n) ~= 2
  error('A must be a 2-dimensional array')
end
% ensure the array is a double precision one.
if ~isa(A,'double')
  A = double(A);
end
% Improve the numerical analysis by subtracting off the array mean
% this has no effect on the standard deviation, but when the mean
% islarge, the formula used will incur numerical issues.
A = A - mean(A(:),'omitnan');
% scale the array to have unit variance too. will put that
% scale factor back into the result at the end
Astd = std(A(:),'omitnan');
A = A./Astd;
% we will need the squared elements 
A2 = A.^2;
% we also need an array of ones of the same size as A. This will let us
% count the number of elements in each truncated window near the edges.
wuns = ones(size(A));

% convolution kernel
kernel = ones(2*k+1,2*k+1);
% compute the std using:
%     std = sqrt((sum(x.^2) - (sum(x)).^2/n)/(n-1))
N = conv2(wuns,kernel,'same');
s = sqrt((conv2(A2,kernel,'same') - ((conv2(A,kernel,'same')).^2)./N)./(N-1));
% catch any complex cases that may have fallen through the cracks.
% that must be due to a floating point error, so in those cases, the std
% would be so small as to be zero.
s(imag(s) ~= 0) = 0;
% restore the scale factor that was used before to normalize the data
s = s.*Astd;
