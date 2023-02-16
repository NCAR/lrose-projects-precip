function [data] = read_spol(infile,indata)
% Load and reorganize ppi cfradial file

vars = fieldnames(indata);
existInds=[];

for ii=1:size(vars,1)
    try
        indata.(vars{ii})=ncread(infile,vars{ii});
        goodInd=ii;
    catch
        disp([vars{ii},' not found.']);
        %vars(ii)=[];
    end
end

% Metadat variables
metadata.azimuth=[];
metadata.elevation=[];
metadata.time=[];
metadata.range=[];

mets = fieldnames(metadata);

for ii=1:size(mets,1)
    metadata.(mets{ii})=ncread(infile,mets{ii});
end

% build up time variable
volStart=ncread(infile,'time_coverage_start');
volStart=volStart';
dtVolStart=datetime(str2num(volStart(1:4)),str2num(volStart(6:7)),str2num(volStart(9:10)),...
    str2num(volStart(12:13)),str2num(volStart(15:16)),str2num(volStart(18:19)));
volEnd=ncread(infile,'time_coverage_end');
volEnd=volEnd';
dtVolEnd=datetime(str2num(volEnd(1:4)),str2num(volEnd(6:7)),str2num(volEnd(9:10)),...
    str2num(volEnd(12:13)),str2num(volEnd(15:16)),str2num(volEnd(18:19)));
metadata.time=dtVolStart+seconds(metadata.time);

sweepStartRayInd=ncread(infile,'sweep_start_ray_index');
sweepEndRayInd=ncread(infile,'sweep_end_ray_index');

% Check format of input data
if min(size(indata.(vars{goodInd})))==1
    rayNgates=ncread(infile,'ray_n_gates');
    rayStartInd=ncread(infile,'ray_start_index');
end

% loop over sweeps
for kk = 1:length(sweepStartRayInd)
    
    ray_inds = 1+(sweepStartRayInd(kk):sweepEndRayInd(kk));
    
    % If we have variable number of gates
    if min(size(indata.(vars{goodInd})))==1
        % pull out the number of gates and the index starts for the rays in this sweep
        ngates = rayNgates(ray_inds);
        rstart = rayStartInd(ray_inds)+1;
        
        % figure out how many gates we need to hold the sweep
        final_num_gates = max(ngates);
        
        % the idea is to generate a matrix of indices such that
        % data.vars.fld(gate_inds) is a num_beams x num_ranges matrix.
        % The complication is that the number of gates in an az could
        % vary.
        
        % create the matrix (num_ranges x num_beams) if indices with rstart
        % as the first row, rstart+1 for the second, etc.
        gate_inds = ones(final_num_gates,length(ray_inds));
        gate_inds(1,:) = rstart;
        gate_inds = cumsum(gate_inds,1);
        
        % The problem is that rays that are shorter than final_num_gates will go
        % beyond their bounds.  So NaN these out.
        x=(ngates+rstart-1).';
        sz=size(gate_inds);
        x_sz = size(x);
        m = max(length(sz),length(x_sz));
        sz = [sz ones(1,m-length(sz))];
        x_sz = [x_sz ones(1,m-length(x_sz))];
        
        mult_vec = sz./x_sz;
        
        ng = repmat(x,mult_vec);
        
        %ng = resize((ngates+rstart-1).',size(gate_inds));
        gate_inds(gate_inds>ng) = NaN;
   else
       final_num_gates=length(metadata.range);
   end
    
    % cp meta_data over
    for ll = 1:length(mets)
        if strcmp(mets{ll},'range')
            tmpdata.range = reshape(metadata.(mets{ll})(1:final_num_gates),1,[])/1000;
        else
            tmpdata.(mets{ll})=metadata.(mets{ll})(ray_inds,:,:,:,:,:);
        end
    end

    % cp over the moment variables
    for ll = 1:length(vars)
        if ~isempty(indata.(vars{ll}))
            if min(size(indata.(vars{goodInd})))==1
                % pull out the data saving into correct place
                tmp = repmat(NaN,size(gate_inds));
                tmp(~isnan(gate_inds)) = indata.(vars{ll})(gate_inds(~isnan(gate_inds)));
                tmpdata.(vars{ll}) = tmp.';
            else
                tmp=nan(length(tmpdata.range),length(tmpdata.time));
                tmp=indata.(vars{ll})(:,ray_inds);
                tmpdata.(vars{ll}) = tmp.';
            end
        end
    end
    data(kk) = tmpdata;
end
end

