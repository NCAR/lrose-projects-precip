function [outValue] = varFromCfRadialString(infile,varName)
%Read variable that is stored in cfradial status_xml string
status_xml_in=ncread(infile,'status_xml');
status_xml_lines=(strsplit(status_xml_in','\n'))';
try
    temp_lines=strfind(status_xml_lines,varName);
    tempInds=find(cellfun(@isempty,temp_lines)==0);
    tempCellsLines=status_xml_lines(tempInds);
    tempCellsSplit = regexp(tempCellsLines, '[><]', 'split');
    outValue=str2num(tempCellsSplit{1,1}{1,3});
    if size(tempCellsSplit,1)>1
        disp(['More than one line with ' varName ' found.']);
        disp('Check if the first one is really the one you want.');
    end
catch
    disp(['Variable ' varName ' not found. Passing NAN.']);
    outValue=nan;
end
end

