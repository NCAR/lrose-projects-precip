function writeCfRadial(data,nameAppend,outdir)
% This function doesn't work it is just something I saved from a different
% location
%% Write CfRadial file

dataWriteVars={'FLAG';'topo'};

dataWrite.time=data.time;
dataWrite.range=data.range;
for ii=1:length(dataWriteVars)
    dataWrite.(dataWriteVars{ii})=data.(dataWriteVars{ii});
end

pre='cfradial.';
post='_HCR_otrec.nc';

metaData=ncinfo(fileList{1,1});
dataVarsOut=fields(dataWrite);

% Split up data into five minute junks
interv=5; %output time interval

loopStartTime= dateshift(dataWrite.time(1),'start','second');
loopStartTime.Minute= interv * floor(loopStartTime.Minute/interv);
loopEndTime=loopStartTime+minutes(5);

while loopStartTime<=dataWrite.time(end)
    
    outData=[];
    % Find data in right time interval
    loopInds=find(dataWrite.time>=loopStartTime & dataWrite.time<loopEndTime);
        
    for ii=1:length(dataVarsOut)
        outData.(dataVarsOut{ii})=data.(dataVarsOut{ii})(:,loopInds);        
    end
    
    % Convert time to seconds since
    fileStartTime=outData.time(1);
    fileEndTime=outData.time(end);
    fileStartTimeSec=dateshift(fileStartTime,'start','second');
    secondTime=etime(datevec(outData.time),datevec(fileStartTimeSec));
    outData.time=secondTime';
    
    outData.range=outData.range(:,1);
    
    outDataDir=[dataOut,datestr(fileStartTime,'yyyymmdd'),'/'];
    if ~exist(outDataDir, 'dir')
        mkdir(outDataDir)
    end
    outname=[outDataDir,pre,datestr(fileStartTime,'yyyymmdd_HHMMSS.FFF'),'_to_',...
        datestr(fileEndTime,'yyyymmdd_HHMMSS.FFF'),post];
    
    % Create file
    ncid = netcdf.create(outname,'NC_WRITE');
    
    % Add dimensions
    dimtime = netcdf.defDim(ncid,'time',length(outData.time));
    dimrange = netcdf.defDim(ncid,'range',length(outData.range));
    %dimsweep = netcdf.defDim(ncid,'sweep',1);
    %dimstr8 = netcdf.defDim(ncid,'string_length_8',8);
    %dimstr32 = netcdf.defDim(ncid,'string_length_32',32);
    %dimxml = netcdf.defDim(ncid,'status_xml_length',7693);
    %dimcal = netcdf.defDim(ncid,'r_calib',1);
    %dimfreq = netcdf.defDim(ncid,'frequency',1);
    netcdf.endDef(ncid);
    
    % Write variables
    
    % time
    netcdf.reDef(ncid);
    varid = netcdf.defVar(ncid,'time','NC_DOUBLE',[dimtime]);
    netcdf.endDef(ncid);
    netcdf.putVar(ncid,varid,outData.time);
    
    % range
    netcdf.reDef(ncid);
    varid = netcdf.defVar(ncid,'range','NC_FLOAT',[dimrange]);
    netcdf.endDef(ncid);
    netcdf.putVar(ncid,varid,outData.range);
    
    % topo
    netcdf.reDef(ncid);
    varid = netcdf.defVar(ncid,'topo','NC_DOUBLE',[dimtime]);
    netcdf.endDef(ncid);
    netcdf.putVar(ncid,varid,outData.topo);
    
    % FLAG
    netcdf.reDef(ncid);
    varid = netcdf.defVar(ncid,'FLAG','NC_INT',[dimtime dimrange]);
    netcdf.endDef(ncid);
    netcdf.putVar(ncid,varid,outData.FLAG);
    
    netcdf.close(ncid);
    
    % Write global attributes
    for ii=1:length(metaData.Attributes)
        if strcmp(metaData.Attributes(ii).Name,'start_datetime')
            ncwriteatt(outname,'/','start_datetime',...
                datestr(fileStartTime,'yyyy-mm-ddTHH:MM:SSZ'));
        elseif strcmp(metaData.Attributes(ii).Name,'time_coverage_start')
            ncwriteatt(outname,'/','time_coverage_start',...
                datestr(fileStartTime,'yyyy-mm-ddTHH:MM:SSZ'));
        elseif strcmp(metaData.Attributes(ii).Name,'start_time')
            ncwriteatt(outname,'/','start_time',...
                datestr(fileStartTime,'yyyy-mm-dd HH:MM:SS.FFF'));
        elseif strcmp(metaData.Attributes(ii).Name,'end_datetime')
            ncwriteatt(outname,'/','end_datetime',...
                datestr(fileEndTime,'yyyy-mm-ddTHH:MM:SSZ'));
        elseif strcmp(metaData.Attributes(ii).Name,'time_coverage_end')
            ncwriteatt(outname,'/','time_coverage_end',...
                datestr(fileEndTime,'yyyy-mm-ddTHH:MM:SSZ'));
        elseif strcmp(metaData.Attributes(ii).Name,'end_time')
            ncwriteatt(outname,'/','end_time',...
                datestr(fileEndTime,'yyyy-mm-dd HH:MM:SS.FFF'));
        else
            ncwriteatt(outname,'/',metaData.Attributes(ii).Name,metaData.Attributes(ii).Value);
        end
    end
       
    loopStartTime=loopEndTime;
    loopEndTime=loopStartTime+minutes(5);
end

end

