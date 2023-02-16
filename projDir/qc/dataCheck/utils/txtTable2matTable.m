function [outtable]=txtTable2matTable(filename, del1)
% Reads Mikes txt tables and convert to matlab table

fid=fopen(filename,'r');
slurp=fscanf(fid,'%c');
fclose(fid);

M=strread(slurp,'%s','delimiter','\n');

commentInds = find(contains(M,'#'));

header=strread(M{1},'%s','delimiter',del1)';

for i=size(commentInds,1)+1:length(M)
    temp=strread(M{i},'%f','delimiter',del1);
    for j=1:length(temp)
        MM(i,j)=temp(j);
    end;
end;
MM(1:size(commentInds,1),:)=[];

outtable=array2table(MM(:,2:end),'VariableNames',header(2:end));
end