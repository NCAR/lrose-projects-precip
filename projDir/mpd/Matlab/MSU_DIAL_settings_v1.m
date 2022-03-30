if  date >= 170223 % testing higher range sampling 
    if date >= 170721 % changed to the HSRL & WV combined reciever with match 45mm-20mm telescopes
      receiver_scale_factor=0.5;
      diff_geo_on = 0;
      %load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns
    elseif date >= 170531 % changed to the HSRL & WV combined reciever with match 45mm-20mm telescopes
      receiver_scale_factor=0.6;
      diff_geo_on = 0;
      load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns
    elseif date >= 170511 % changed to the HSRL & WV combined reciever with match 45mm-20mm telescopes
      receiver_scale_factor=0.375;
      diff_geo_on = 0;
      load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns
    elseif date >= 170506
      receiver_scale_factor=0.2;
      diff_geo_on = 0;
      load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns    
    elseif date >= 170320
      receiver_scale_factor=0.725;
      diff_geo_on = 0;
      load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns
    elseif date >= 170302
      receiver_scale_factor=0.45; 
      load('diff_geo_cor_170302D.mat');
      MCS.bins = 560;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 250;  % ns
    elseif date >= 170212
      receiver_scale_factor=0.45;   
      load('diff_geo_cor_170301G.mat');
      MCS.bins = 1400;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 100;  % ns
    end
    MCS.accum = 14285; 
    MCS.accum_delay = 10; %ns
    time_per_column = MCS.accum*((MCS.bins*MCS.bin_duration)+MCS.accum_delay)/1e9; % acummulation time in seconds
    profiles2ave.wv = 2*round(((ave_time.wv*60/time_per_column)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/time_per_column)+1)/2); % 7kHz, 10k accum data rate is ~1.4s 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = ((1.25+1/2)-0.5/2)*150;  % changed hardware timing to start after pulse through
    blank_range = 375; % new pulse generator shifts gate timing so less outgoing pulse contamination
elseif (date >= 161103) && (date <= 170222)  % MSU system in Boulder modfied to use QC pulse generator timing
    receiver_scale_factor=0.77; % changed setup to 70/30 and alignment 20161221 at 17:30UTC
    %receiver_scale_factor = 3.7; % initial 90/10 setup and alignment 
    %receiver_scale_factor = 3.4; %c hanged alignment 20161221 at 0:30UTC
    if date >= 170212
        load('diff_geo_cor_170222A.mat');
        diff_geo1 = diff_geo_corr;
        load('diff_geo_cor_170222B.mat');
        diff_geo2 = diff_geo_corr;
        diff_geo4 = [diff_geo1; diff_geo2];
        diff_geo_corr = nanmean(diff_geo4);    
    elseif date >= 161227
        %dir /Users/spuler/desktop/WV_DIAL/Matlab 
        load('diff_geo_cor_161224.mat')
        diff_geo1 = diff_geo_corr;
        load('diff_geo_cor_161226.mat')
        diff_geo2 = diff_geo_corr;
        load('diff_geo_cor_161227.mat')
        diff_geo3 = diff_geo_corr;
        diff_geo4 = [diff_geo1; diff_geo2; diff_geo3];
        diff_geo_corr = nanmean(diff_geo4);
    end
    MCS.bins = 280;  % setting for 7 kHz (21 km)
    MCS.bin_duration = 500;  % ns
    MCS.accum = 14285; 
    MCS.accum_delay = 10; %ns
    time_per_column = MCS.accum*((MCS.bins*MCS.bin_duration)+MCS.accum_delay)/1e9; % acummulation time in seconds
    profiles2ave.wv = 2*round(((ave_time.wv*60/time_per_column)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/time_per_column)+1)/2); % 7kHz, 10k accum data rate is ~1.4s 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = ((1.25+1/2)-0.5/2)*150;  % changed hardware timing to start after pulse through
    blank_range = 225; % new pulse generator shifts gate timing so less outgoing pulse contamination   
elseif (date >= 160812) && (date <= 161102) % MSU system in Boulder original setup 
    MCS.bins = 280;  % setting for 7 kHz (21 km)
    MCS.bin_duration = 500;  % ns
    MCS.accum = 10000; 
    MCS.accum_delay = 10; %ns
    time_per_column = MCS.accum*((MCS.bins*MCS.bin_duration)+MCS.accum_delay)/1e9; % acummulation time in seconds
    profiles2ave.wv = 2*round(((ave_time.wv*60/time_per_column)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/time_per_column)+1)/2); % 7kHz, 10k accum data rate is ~1.4s 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = ((1.25+1/2)-0.5/2)*150;  % changed hardware timing to start after pulse through
    blank_range = 300; % new pulse generator shifts gate timing so less outgoing pulse contamination 
elseif (date >= 160711) && (date <= 160811) % MSU system in Boulder original setup 
    profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2);  % 9kHz, 10k accum data rate is ~1.1s  
    profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2); % 9kHz, 10k accum data rate is ~1.1s 
    MCS.bins = 220;  
    MCS.bin_duration = 500;  % ns 
    MCS.accum = 10000; 
    P0  = 0.83; % surface pressure in Boulder
    switch_ratio = 0.5; % online switching ratio 
    timing_range_correction = -((0.1+1/2)-0.5/2)*150; 
    blank_range = 375; % new pulse generator shifts gate timing so less outgoing pulse contamination 
end
