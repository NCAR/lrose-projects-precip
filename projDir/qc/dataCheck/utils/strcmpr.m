% STRCMPR Determine whether strings match.
%    TF = STRCMPR(STR1,PAT,MATCH_PAT,FORCE_EXACT) returns 1 if the string STR1 matches the 
%    pattern PAT and 0 otherwise, where PAT is a regular expression.  
%
%    MATCH_PAT is optional.  See below for more info on this parameter.
%
%    FORCE_EXACT is optional.  Default is 0.  If 1, then this function requires
%    a full match, rather than a partial match.  e.g. strcmpr({'fool'},{'oo'},[],0)
%    will return true since 'oo' appears in 'fool'.  strcmpr({'fool'},{'oo'},[],1)
%    will return false since 'oo' is only a substring.  strcmpr({'fool'},{'f.*l'},[],1)
%    will return true.  FORCE_EXACT simply appends a '^' to the beginning and a '$' to
%    the end of each pattern, causing the match to be exact, rather than just a 
%    substring.
%
%    If either STR1 or PAT is a cell array, a STRCMPR is performed for
%    each entry and TF is a corresponding numeric array containing the
%    results.
%
%    By default, if both STR1 and PAT are cell arrays, then TF is an array having
%    the same size as STR1 and containing values determined by whether 
%    the corresponding element in STR1 matches ANY element in PAT
%    under a pairwise STRCMPR.  If MATCH_PAT is provided and is not 0 or empty, then
%    TF will be the same size as PAT containing values determined by whether 
%    the corresponding element in PAT matches ANY element in STR1
%    under a pairwise STRCMPR.  To get the default 
%
%    Examples;
%
%      strcmpr('nothing to eat','^n.*t$')
%
%      strcmpr({'knot','not','nut','nothing'},'^n.*t$')
%
%      strcmpr({'fool','idiot','buffoon','nucklehead'},{'^fo.*$','^.*head$','^jerk$'})
%
%      strcmpr({'fool','idiot','buffoon','nucklehead'},{'^fo.*$','^.*head$','^jerk$'},1)
%
%    Note that the different treatment of strings and cell arrays of
%    strings can sometimes cause surprising results; e.g., compare 
%    the outcomes of the next two
%
%      strcmpr('nucklehead',{'^fo.*$','^.*head$'})
%      strcmpr({'nucklehead'},{'^fo.*$','^.*head$'})

function [TF] = strcmpr(str1,pat,match_pat,force_exact)

if nargin<3 | isempty(match_pat)
  match_pat = 0;
end

if nargin<4 | isempty(force_exact)
  force_exact = 0;
end

if iscell(str1) & iscell(pat)
  if ~match_pat
    TF = logical(zeros(size(str1)));
    for ll = 1:prod(size(str1))
      TF(ll) = any(strcmpr(str1{ll},pat,[],force_exact));
    end
  else
    TF = logical(zeros(size(pat)));
    for ll = 1:prod(size(pat))
      TF(ll) = any(strcmpr(str1,pat{ll},[],force_exact));
    end
  end
else
  if force_exact && iscell(pat)
    pat = cellfun(@(x) ['^' x '$'],pat,'UniformOutput',0);
  elseif force_exact
    pat = ['^' pat '$'];
  end
  TF = regexp(str1,pat);
  if iscell(TF)
    TF = ~cellfun(@isempty,TF);
  else
    TF = ~isempty(TF);
  end
end
    
