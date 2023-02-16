function args = struct2args(str)
% struct2args   convert structure to paramparse style cell array
%
% usage  args = struct2args(str)

if ~isstruct(str) || prod(size(str))~=1
  error('argument should be a 1x1 struct')
end

flds = fieldnames(str).';
data = struct2cell(str).';
args = reshape(cat(1,flds,data),1,[]);
