% Create table with netcdf variables for readme files
clear all
close all

infile='cfrad.20190922_163000.100_to_20190922_163500.000_HCR_VER.nc';
indir='/scr/snow1/rsfdata/projects/otrec/hcr/qc1/cfradial/final/10hz/20190922/';

outFile='/h/eol/romatsch/hcrCalib/varTables/otrec.txt';

info=ncinfo([indir infile]);
vars=info.Variables;

outData=cell(size(vars,2),3);
outData(:,1)={vars.Name};

for ii=1:size(vars,2)
    atts={vars(ii).Attributes};
    attName={atts{1,1}.Name};
    longNameInd=find(ismember(attName, 'long_name'));
    longName={atts{1,1}(longNameInd).Value};
    if ~isempty(longName)
        outData(ii,3)=longName;
    end
    unitInd=find(ismember(attName, 'units'));
    unit={atts{1,1}(unitInd).Value};
    if ~isempty(unit)
        outData(ii,2)=unit;
    end
end

outTable=cell2table(outData);
outTable.Properties.VariableNames={'Name','LongName','Unit'};

writetable(outTable,outFile,'Delimiter',',');