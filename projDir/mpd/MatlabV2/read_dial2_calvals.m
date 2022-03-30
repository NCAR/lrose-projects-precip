addpath('/usr/local/home/rsfdata/git/lrose-projects-eolbase/projDir/dial/MatlabV2/Calibration')
addpath('/usr/local/home/rsfdata/git/lrose-projects-eolbase/projDir/dial/MatlabV2/JSon')
dat=loadjson('dial2_calvals.json','SimplifyCell',1);

%t_date = '11-Jun-2017'
t_date = datetime(num2str(Date),'InputFormat','yyMMdd');

for i=1:size(dat.MCS_bins,2)
    if (t_date >= datetime(dat.MCS_bins(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        MCS.bins = dat.MCS_bins(i).value;
    end
end

for i=1:size(dat.Bin_Width,2)
    if (t_date >= datetime(dat.Bin_Width(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        MCS.bin_duration = dat.Bin_Width(i).value*1e9; % convert to ns
    end
end

for i=1:size(dat.MCS_accum,2)
    if (t_date >= datetime(dat.MCS_accum(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        MCS.accum = dat.MCS_accum(i).value; % convert to ns
    end
end

for i=1:size(dat.MCS_accum_delay,2)
    if (t_date >= datetime(dat.MCS_accum_delay(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        MCS.accum_delay = dat.MCS_accum_delay(i).value*1e9; % convert to ns
    end
end

for i=1:size(dat.Default_P,2)
    if (t_date >= datetime(dat.Default_P(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        P0 = dat.Default_P(i).value;
    end
end

for i=1:size(dat.Molecular_Gain_Matlab,2)
    if (t_date >= datetime(dat.Molecular_Gain_Matlab(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        receiver_scale_factor = dat.Molecular_Gain_Matlab(i).value;
        diff_geo_on = dat.Molecular_Gain_Matlab(i).diff_geo;
    end
end

for i=1:size(dat.switch_ratio,2)
    if (t_date >= datetime(dat.switch_ratio(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        switch_ratio = dat.switch_ratio(i).value;
    end
end

for i=1:size(dat.Location,2)
    if (t_date >= datetime(dat.Location(i).date,'InputFormat','d-MM-yyyy H:m')) == 1
        location = dat.Location(i).location;
    end
end
location; %write the location to the screen

%calcuate the accumuation time per MCS dwell
time_per_column = MCS.accum*((MCS.bins*MCS.bin_duration)+MCS.accum_delay)/1e9; % acummulation time in seconds
profiles2ave.wv = 2*round(((Options.ave_time.wv*60/time_per_column)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s
profiles2ave.rb = 2*round(((Options.ave_time.rb*60/time_per_column)+1)/2); % 7kHz, 10k accum data rate is ~1.4s
% % % load('diff_geo_cor_170810.mat');
timing_range_correction = (1.25-0.2+0.5/2-1.0/2)*150;  % changed hardware timing to start after pulse through
blank_range = 225; % new pulse generator shifts gate timing so less outgoing pulse contamination

clear i

JSondeData.BasePressure        = P0;
JSondeData.BlankRange          = blank_range;
JSondeData.Data                = dat;
JSondeData.Date                = t_date;
JSondeData.DeadTime            = 37.25E-9;
% JSondeData.GeoCorrectionOn     = diff_geo_on;
% JSondeData.GeoCorrectionOff    = diff_geo_corr;
JSondeData.Location            = location;
JSondeData.MCS                 = MCS;
JSondeData.Profiles2Average    = profiles2ave;
JSondeData.RangeCorrection     = timing_range_correction;
JSondeData.ReceiverScaleFactor = receiver_scale_factor;
JSondeData.SwitchRatio         = switch_ratio;
JSondeData.TimePerColumn       = time_per_column;

clear blank_range diff_geo_corr diff_geo_on location MCS profiles2ave
clear switch_ratio time_per_column receiver_scale_factor dat
clear P0 timing_range_correction t_date