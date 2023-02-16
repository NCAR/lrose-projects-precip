function def = paramparse_default(assignif,fld);
% PARAMPARSE_DEFAULT Returns default value for paramparse
%
%  Used to generate default action strings for interpretation
%  by paramparse:  The possible actions of paramparse is to
%  parse the variable or not.  The decision to parse or not 
%  is based on whether a variable by that name exists or not
%  and based on what default value is used:
%  paramparse_default('noexist')
%  paramparse_default('nexist')
%  paramparse_default('always')
%  paramparse_default('never')
%
%  usage default = paramparse_default(assignif,fld);
%
%   assignif (optional) - can be 'noexist','exist','always','never'
%      'noexist' (default) - parse only if the variable has not
%            previously been assigned in that workspace.
%            Typically 'noexist' is the natural setting because
%            normally the idea is that you don't want to override
%            the default setting.  Thus parse only if it doesn't
%            exist.
%      'exist' - parse only if the variable already exists in
%            that workspace.
%       'always' - always parse regardless of whether or not the
%            variable had already been set.
%       'never' - never parse regardless of whether or not the
%            variable had already been set.  Not sure of the 
%            point of this one.
%   fld (optional) - this is the base paramparse default field.
%       the default is:
%       'XXXyyyQQQvvvPaRaMpArSeDeFaUlTvAlUeXXXyyyQQQvvv'
%       This was chosen because it is a value that is probably
%       otherwise never seen.  Change this ONLY if you want 
%       to use some other default string.  (Rarely)
%
%  This function generates the default string by concatenating
%  the base string (fld) with the assignif string.  This function
%  should be used in the assignment of defaults for use in paramparse.
%
%  This function returns the default values used by paramparse (SEE 
%  PARAMPARSE).  When paramparse parses a variable, it will decide whether 
%  or not to parse the variable depending on whether the variable existed or 
%  not as well as which paramparse_default value it is set to.
%
%                     Table to determine action
%  Does the 
%  Variable Exist
%  In Caller Work-
%  space before     |            assignif
%  Paramparse call  | noexist   | exist     | always    | never
%  -------------------------------------------------------
%   Var  Exists     | no action | parse     | parse     | no action
%   Var no Exist    | parse     | no action | parse     | no action
% 
% 
%  See PARAMPARSE
%
%  code example (in .m file):
%
%  function fun1(varargin)
%  % get default paramparse value
%  DEFAULT = paramparse_default; % defaults to 'noexist'
%  % set x to the default
%  x = DEFAULT;
%  % parse the input arguments
%  paramparse(varargin);
%  % run fun2 setting fun2's y to x
%  fun2('y',x);
%  return;
%
%  % in different .m file
%  function fun2(varargin)
%  % set default value for y
%  y = 1;
%  % parse the inputs
%  paramparse(varargin);
%  % display value for y
%  disp(y);
%  return;
%
%  >> fun1
%    1
%    % in fun1 - first x is set to DEFAULT. paramparse does not
%    %override becuase nothing passed at commandline. in fun 2
%    %first y set to 1. The paramparse is given {'y',DEFAULT}.  
%    %Thus y is not overriden and stays at 1
%  >> fun1('x',2);
%    2
%    % in fun1 - first x is set to DEFAULT. paramparse overrides
%    this to 2 becuase {'x',2} was passed at commandline. in fun 2
%    %first y set to 1. The paramparse is given {'y',2}.  
%    %Thus y is overriden and is set to 2
%
%  If instead, DEFAULT = paramparse_default('exist') then
%  >> fun1
%    XXXyyyQQQvvvPaRaMpArSeDeFaUlTvAlUeXXXyyyQQQvvvexist
%    % in fun1 - first x is set to DEFAULT. paramparse does not
%    %override becuase nothing passed at commandline. in fun 2
%    %first y set to 1. The paramparse is given {'y',DEFAULT}.  
%    %Thus y is overriden and is set to the value in DEFAULT
%  >> fun1('x',2);
%    2
%    % in fun1 - first x is set to DEFAULT. paramparse overrides
%    this to 2 becuase {'x',2} was passed at commandline. in fun 2
%    %first y set to 1. The paramparse is given {'y',2}.  
%    %Thus y is overriden and is set to 2
%   
%  NOTE: In general, paramparse_default('exist' or 'always' or 'never') 
%  are not used when calling paramparse or paramparses.
%

if nargin==0 
  assignif = 'noexist';
end

if nargin < 2 || isempty(fld)
  fld = 'XXXyyyQQQvvvPaRaMpArSeDeFaUlTvAlUeXXXyyyQQQvvv';
end

if length(fld)<20 || ~ischar(fld)
  error('fld must be a character string with at least 20 characters');
end;

if ~any(strcmp(assignif,{'noexist','exist','always','never'}))
  def = fld;
else
  def = [fld assignif];
end;
