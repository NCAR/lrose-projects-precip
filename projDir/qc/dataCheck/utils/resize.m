function y = resize(x,varargin)
% RESIZE Resizes an object to a specified size by tiling
%
%  This function is an alternative to directly calling repmat,
%  when you want an object to have a specific size.  
%
%  y = resize(x,size_vec)
%  y = resize(x,dim1_size,dim2_size,...);
%
%  x is the object that you want to repmat up to a specific 
%  size.  The size is given by size_vec or dim{n}_size.  
%  
%  NOTE: the size(x) must divide (component-wise) size_vec. 
%  size_vec is not the same argument that you would specify
%  in repmat, size_vec is the size that you want the result
%  to be (not the number of times to tile x).
%  
%  examples:
%   x = rand(2,3);
%   y = (1:2)'; % column vector with same number or rows as x
%   z = (1:3); % row vector with same number or columns as x
%   resize(y,size(x))
%      ans = 
%        1    1    1
%        2    2    2
%   % repmat way of doing the same thing assuming only that the
%   % number of columns is the same as the number in x.
%   repmat(z,1,size(x,1)) 
%      ans = 
%        1    1    1
%        2    2    2
%   resize(z,size(x))
%      ans = 
%        1    2    3
%        1    2    3
%   repmat(z,size(x,2),1)  % repmat way of doing the same thing
%      ans = 
%        1    1    1
%        2    2    2
%   a = x.*resize(y,size(x))./resize(z,size(x));
%
%  Uses:  This function is useful when you have data, say 'x', that 
%  is n-dimensional, and data that is less than n-D, say y, but the
%  non-trivial dimensions of y have the same size as x.  Now we want
%  to multiply x.*y.  This doesn't make sense because 1)
%  they are not the same size and 2) one of them is not a scalar.
%  To us it makes sense because we think y should just be repmat'd
%  to the right size.  RESIZE saves a little work by figuring out
%  how to repmat y to get it to be the same size as x.  
%
%  See REPMAT.


if length(varargin)==1
  sz = varargin{1};
else
  sz = cat(2,varargin{:});
end;

x_sz = size(x);
m = max(length(sz),length(x_sz));
sz = [sz ones(1,m-length(sz))];
x_sz = [x_sz ones(1,m-length(x_sz))];

mult_vec = sz./x_sz;

if any(mult_vec-round(mult_vec))
  error('The size of ''x'' should divide the desired size');
end;

y = repmat(x,mult_vec);
