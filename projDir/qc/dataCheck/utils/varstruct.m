function str = varstruct(varlist,excludelist,return_array)
% usage  str = varstruct(varlist,excludelist,return_array)
%
%  inputs: 
%    varlist - a string or a cellarray of strings, each of which
%              contains a fields that you want put into the struct.
%              Can also be a struct, in which case fieldnames(varlist)
%              is used.  If empty or missing, all variables from the
%              caller workspace will be used
%    excludelist - same as varlist.  This will exclude matching variables
%              from the varlist.  If empty or missing, the default is {}
%
%   This function is used to 'wrap' a list of variables from the caller
%   workspace into a struct.  One use for this is to pass back the
%   state of the system to the user.  
%   Another use is to pass all the variables from one function to
%   a called (not caller) function.  If a function uses paramparse,
%   paramparse(strct) will parse out the contents of the struct.
%
%   examples:
%
%     s = varstruct;
%     func(s)  where func is defined by 
%            function func(varargin)
%            ...
%            paramparse(s);
%     This places all the current variables into the workspace of func.
%     ----------
%     if func is defined by
%            function y = func
%            ...
%            y = varstruct;
%     This would return all the variables back to the calling workspace.
%

% default for varlist
if nargin < 1 || isempty(varlist)
  varlist = evalin('caller','whos');
  varlist = {varlist.name};
end;

% default for excludelist
if nargin < 2 || isempty(excludelist)
  excludelist = {};
end;

% default for excludelist
if nargin < 3 || isempty(return_array)
  return_array = 0;
end;
% error checking on varlist
if ischar(varlist)
  varlist = {varlist};
elseif isstruct(varlist)
  varlist = fieldnames(varlist);
end;

if ~iscell(varlist)
  error('varlist must be a string or a cell array of strings');
end;

% error checking and preprocessing on excludelist
if ischar(excludelist)
  excludelist = {excludelist};
elseif isstruct(excludelist)
  excludelist = fieldnames(excludelist);
end;
if ~iscell(excludelist)
  error('excludelist must be a string or a cell array of strings');
end;

% initialize
str.dummydummydummy = 0;

for l = 1:length(varlist)
  if~ischar(varlist{l})
    error('varlist must be a string or a cell array of strings');
  end;
  if ~any(strcmp(varlist{l},excludelist))
    str.(varlist{l}) = evalin('caller',[varlist{l} ';']);
  end;
end;

str = rmfield(str,'dummydummydummy');
if isempty(str)
  str = struct([]);
end;

if return_array
  str = reshape(cat(2,fieldnames(str),struct2cell(str)).',1,[]);
end