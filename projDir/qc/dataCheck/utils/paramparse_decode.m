function assignif = paramparse_decode(def,fld)
% Returns the default state of the variable - if it is one of
% the paramparse_default constants, then it returns the action
% state of that defualt.  Otherwise, it returns an ''.

persistent pds;

if nargin < 2
  fld = [];
end;

if isempty(pds)
  pds{1} = paramparse_default('always',fld);
  pds{2} = paramparse_default('never',fld);
  pds{3} = paramparse_default('exist',fld);
  pds{4} = paramparse_default('noexist',fld);
  pds{5} = paramparse_default('',fld);
end;

if ischar(def) || (isnumeric(def) && length(def)==1)

  switch def
   case pds{1}
    assignif = 'always';
   case pds{2}
    assignif = 'never';
   case pds{3}
    assignif = 'exist';
   case pds{4}
    assignif = 'noexist';
   case pds{5} % default action in paramparse_default
    assignif = 'noexist';
   otherwise
    assignif = '';
  end;
else
  assignif = '';
end;
