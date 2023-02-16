function paramparse(parsearray,varlist,warnoff,defstr,re)
% usage  paramparse(parsearray,varlist,quiet)
%  parsearray is a cell array of the form
%    {'var1name',var1value,...}
%    OR parsearray is a struct.
%    OR parsearray is a cell array of the form
%    {struct,'var1name',var1value,...}
%
%    The structs are evaluated as such: the fieldnames
%    become the 'varNname's, and their values become the 'varNvalue's.
%  varlist (optional) is a cell array of variables to 
%    restrict the parsing to
%  warnoff (optional) 2, 1 or 0 - default 2 ('error'), 
%       0 or 'warn' - Warn if the variable has not been defaulted 
%              before paramparse is run.  If the warnings are 
%              shut off (using WARNING) then no warning is given.
%       1 or 'none' - Quiet mode
%       2 or 'error' - Error if the variable has not been defaulted.
%       3 or 'warn_skip' - like 0, but skip instead of running
%       4 or 'none_skip' - like 1, but skip instead of running
%  defstr (optional) - The string that is the paramparse_default base
%      sting.  See paramparse_default
%  re (optional) 1 or 0.  default 0.  If 1 then the varlist is treated
%      as containing regular expressions.  This is slower.
%
%  This function evaluates
%    var1name = var1value 
%  into the caller functions workspace.
%  If varlist is given, then only those in the varlist will
%  be evaluated.  
%
%  This function is useful for allowing a function to be passed
%  parameters like 
%    myfun('xdata',x,'ydata',y)
%    myfun('ydata',y,'PlotOptions','r.')
%  where:
%    function myfun(varargin)
%      % initialize defaults
%      xdata=1:10;
%      ydata=2:11;
%      PlotOptions='g';
%
%      paramparse(varargin)
%
%      plot(xdata,ydata,PlotOptions);
%      return;
%
%  This is beneficial for functions with a large number of 
%  parameters, so that 1) the calling the function becomes
%  more readable and 2) defaults are easier to deal with.
%  3) the order the parameters are given does not matter
%  4) Backwards compatibilty is easier to maintain.
%
%  PARAMPARSE_DEFAULT: The result from this function can be
%  passed as a value in the function call.  When this is done
%  the paramparse parses or not, that variable depending
%  on which default is used and whether that variable already exists 
%  or not. (SEE PARAMPARSE_DEFAULT)  An example:
%    DEFAULT = paramparse_default; % returns the 'noexist default'
%    myfun('ydata',y,'PlotOptions',DEFAULT)
%   Thus, after the paramparse statement in myfun,
%   ydata is overridden but PlotOptions is not, assuming that PlotOptions
%   is defaulted before the 
%

if nargin < 1 || isempty(parsearray)
  return;
end;

if ~(iscell(parsearray) || isstruct(parsearray))
  error('parsearray must be a cell array or a struct.');
end;

% if the first element of the cell array is a struct then
%  this struct contains the fields and values
%  make parsearray just the struct
if iscell(parsearray) && length(parsearray)>0 && isstruct(parsearray{1})
  parsearray = cat(2,struct2args(parsearray{1}),{parsearray{2:end}});
end;

% if parsearray is a struct then we will use the struct 
%  to get the fields and values.  Just flag that we're in
%  struct mode.
isstrct = isstruct(parsearray);
if isstrct
  parsearray = parsearray(1);
end;

% if cell array, the length of parsearry must be even
if ~isstrct && mod(length(parsearray),2)~=0 
  error('Must give an even number of vars to parse');
  return;
end;

% if varlist is not given, then default the
% varlist to the fields in parsearray
if nargin < 2 || isempty(varlist)
  % if its a cell, the fields are the odd fields.
  if ~isstrct
    varlist = parsearray(1:2:end);
    %otherwise it's a struct, so get the fieldnames
  else
    varlist = fieldnames(parsearray);
  end;
  % if varlist is given preprocess the list
else
  %if it's a string make a cell array out of it
  if ischar(varlist)
    varlist = {varlist};
    % otherwise if its a struct, extract the fieldnames
  elseif isstruct(varlist)
    varlist = fieldnames(varlist);
    % otherwise if it's not a cell, bonk.
  elseif ~iscell(varlist)
    error('varlist must be a string, cell array of strings, or a struct.')
  end;
end;

% filter out non-strings from the varlist.
newvarlist = {};
for l = 1:length(varlist)
  if ischar(varlist{l})
    newvarlist{end+1} = varlist{l};
  else
     warning(['Bad field #' num2str(l) ' of varlist.  Class: '  ...
	      class(varlist{l})]);
  end;
end;

% get list of all possible fields from parsearray
if isstrct
  fields = fieldnames(parsearray);
else
  fields = parsearray(1:2:end);
end;

if nargin<5 || isempty(re)
  re = 0;
end

if ~re
  % use intersect to find the requested fields.  Note that we have to flip the fields array backwards
  % so that intersect will fine the LAST one rather than the first. 
  [ofields,ofield_inds] = intersect(fields,newvarlist);
  fields = ofields;
  field_inds = ofield_inds;
  
  %fields = reshape(fields,1,[]);
  %[nfields,field_inds] = intersect(fliplr(fields),newvarlist);
  %field_inds = length(fields)-field_inds+1;
  %fields = nfields;
  %if ~isequal(ofield_inds,field_inds)
  %  warning('paramparse:orderchange','The behavior of paramparse changed.  Now if there are repeated fields, the last one is chosen, rather than the first.  Please check the code to make sure that this is accounted for.  To turn off this message, type: warning(''off'',''paramparse:orderchange'')');
  %end
else
  field_inds = find(strcmpr(fields,newvarlist,[],1));
  fields = fields(field_inds);
end

if ~isstrct
  values = parsearray(2*field_inds);
end;

errstate = 'error';
warn = warning;
warn = warn(strcmp('all',{warn.identifier}));
if length(warn)<1
  warning('warn function did not return any ''all'' state: defaulting to ''on''');
  clear warn;
  warn.state = 'on';
elseif length(warn)>1
  warning('warn function returned more than 1 ''all'' state: defaulting to first');
  warn = warn(1);
end;  

skip = 0;
if nargin>=3 && ~isempty(warnoff)
  switch warnoff
   case {2,'error'}
    errstate = 'error';
   case {0,'warn'}
    if strcmp(warn.state,'on')
      errstate = 'warn';
    else
      errstate = 'none';
    end;
   case {1,'none'}
    errstate = 'none';
   case {3,'warn_skip'}
    skip = 1;
    if strcmp(warn.state,'on')
      errstate = 'warn';
    else
      errstate = 'none';
    end;
   case {4,'none_skip'}
    skip = 1;
    errstate = 'none';
   otherwise
    error('invalid option for paramparse');
  end;
end;

if nargin < 4
  defstr = '';
end;

%gdb('save',0);
%gdb('off',0);
if ~exist('debug_on_error')
  err_status = dbstatus;
  restore_error_str = '';
  
  err_ind = find(strcmp({err_status.cond},'error'));
  if length(err_ind)>0 && isequal(err_status(err_ind(1)).identifier,{'all'})
    restore_error_str = cat(2, restore_error_str, 'dbstop if error;');
  end
  err_ind = find(strcmp({err_status.cond},'caught error'));
  if length(err_ind)>0 && isequal(err_status(err_ind(1)).identifier,{'all'})
    restore_error_str = cat(2, restore_error_str, 'dbstop if caught error;');
  end
  
  dbclear if error;
  dbclear if caught error;  
else
  restore_error_str = '';
end

% list through desired fields
for l = 1:length(fields)
  if ischar(fields{l})
    % if we want this field, try to evaluate in caller
    try
      %first check to see if it already existed - removing sub-qualifiers
      lastwarn('');
      ind = find(fields{l}=='(' | fields{l}=='.' | fields{l}=='{');
      if isempty(ind)
	ind = length(fields{l})+1;
      end;
      varthere = evalin('caller',['exist(''' fields{l}(1:ind(1)-1) ''',''var'')']);
      filethere = exist(fields{l}(1:ind(1)-1),'file');
      varspecial = any(strcmp(fields{l}(1:ind(1)-1),{'varargin','ans'}));
      if ~varthere
	error('Not found');  
      end;
      % if got here, then a variable exists, if there was a sub-qualifier
      % then check to see if the full qualified variable exists
      if ind(1)<=length(fields{l})
	isvar = evalin('caller',fields{l});
	if ~isempty(lastwarn)
	  error('Not found');
	end;
      end;
      % isvar = 1 means that fully qualified variable exists
      % this is different than varthere since that one only
      % sees if variable with no sub-qualifiers, exisits.
      isvar = 1;
    catch
      % If got here then the fully qualified varaible does not exist.
      isvar = 0;
    end;
    %if strcmp(fields{l},'PARAMPARSE_GETDEFAULTS')
    %  global LAST_PARAMPARSE_DEFAULTS
    %  LAST_PARAMPARSE_DEFAULTS = evalin('caller','varstruct');
    %  error('data put into global LAST_PARAMPARSE_DEFAULTS');
    %end;
    if strcmp(errstate,'warn') && ~isvar
      disp('*****************************************');
      warning([fields{l} ' has not been defaulted.  ' ...
	       'Possible misspelled parameter name.']);
      disp('*****************************************');
    end;
    if any(strcmp(errstate,{'warn','none'})) && ~isvar && skip
      continue
    end
    if (strcmp(errstate,'warn') || strcmp(errstate,'none')) && ~varthere && filethere && ...
	  ~varspecial
      disp('*****************************************');
      warning([fields{l}(1:ind(1)-1) ' has not been defaulted.  ' ...
	       'BUT it exists as a function.  This may lead to a weird error.  ' ...
	       'If the program crashes (outside this function) try declaring ' ...
	       'this variable before this paramparse call (set it [])']);
      disp('*****************************************');
    end;
    if strcmp(errstate,'error') && ~isvar
      fprintf('\n');
      dbstack
      %gdb('load',0);
      eval(restore_error_str);
      error([fields{l} ' has not been defaulted.  ' ...
	     'Possible misspelled parameter name.']);
    end;
    % get data
    %  this actually does not waste space because
    %  of the way variables are allocated that
    %  are equal (i.e. x = rand(5000); y = x; requires
    %  almost 1/2 the space that x = rand(5000); y = rand(5000);
    if isstrct
      tmp = getfield(parsearray,fields{l});
    else
      tmp = values{l};
    end;	  
    % assign!  Assign first to some weird named variable in
    % the caller workspace and then reassign to the one
    % that you actually want.  This allows one to pass
    % {'data.x',2}.  You can't use assignin to do this
    % directly because of '.', but if you try to only use eval 
    % you have to stringify the value part of the assignment
    switch paramparse_decode(tmp,defstr)
     case 'always'
      asn = 1;
     case 'never'
      asn = 0;
     case 'exist'
      asn = isvar;
     case 'noexist'
      asn = ~isvar;
     otherwise
      asn = 1;
    end;
    if asn
      try
	assignin('caller','humungous_kerblooey',tmp);
	evalin('caller',[fields{l} '= humungous_kerblooey;']);
      catch
	%gdb('load',0);
        eval(restore_error_str);
	error(['Assign of ' fields{l} ' failed! Reason:']);
	lasterr
      end;
    end;
  else
    warning(['Assign of ' fields{l} ' failed! Reason: Not a string']);
  end;
end;
%gdb('load',0);
eval(restore_error_str);
evalin('caller','clear humungous_kerblooey;');
lasterr('');

global PARAMPARSE_LOG
if ~isempty(PARAMPARSE_LOG)
  if ~isempty(evalin('caller','varstruct;'))
    if ~isstruct(PARAMPARSE_LOG)
      clear global PARAMPARSE_LOG
      global PARAMPARSE_LOG
      PARAMPARSE_LOG(1).stack = dbstack;
      PARAMPARSE_LOG(1).stack = PARAMPARSE_LOG(1).stack(2:end);
      PARAMPARSE_LOG(1).file = PARAMPARSE_LOG(1).stack(1).name;
      PARAMPARSE_LOG(1).data = evalin('caller','varstruct;');
    else
      PARAMPARSE_LOG(end+1).stack = dbstack;
      PARAMPARSE_LOG(end).stack = PARAMPARSE_LOG(end).stack(2:end);
      PARAMPARSE_LOG(end).file = PARAMPARSE_LOG(end).stack(1).name;
      PARAMPARSE_LOG(end).data = evalin('caller','varstruct;');
    end;
  end;
else
  clear global PARAMPARSE_LOG;
end;
  