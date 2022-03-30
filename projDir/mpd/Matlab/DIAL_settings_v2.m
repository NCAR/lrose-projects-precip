    if date >= 160311 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio 
      timing_range_correction = ((1.25+1/2)-0.5/2)*150;  % changed hardware timing to start after pulse through
      blank_range = 300; % new pulse generator shifts gate timing so less outgoing pulse contamination 
    elseif (date >= 160211) && (date <= 160310)         
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio 
      timing_range_correction = 0;  % changed the hardware timing to start at pulse midpoint and corrected MCS error
      blank_range = 300; % new pulse generator shifts gate timing so less outgoing pulse contamination 
    elseif (date >= 150922) && (date <= 160211) 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 150917) && (date <= 150921) 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.75; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 150823) && (date <= 150916)
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 150617) && (date <= 150822) 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.929; % surface pressure in Ellis KS
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 150610) && (date <= 150616) 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2)  % 9kHz, 10k accum data rate is ~1.1s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2) % 9kHz, 10k accum data rate is ~1.1s 
      MCS.bins = 220;  % 14-June-2014 to 2-Feb-2015
      MCS.bin_duration = 500;  % ns 
      MCS.accum = 10000;   
      P0  = 0.929; % surface pressure in Ellis KS
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000; not clear that this is being read
      blank_range = 300;
    elseif (date >= 150422) && (date <= 150609) 
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.4)+1)/2);  % 7kHz, 10k accum data rate is ~1.4s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.4)+1)/2); % 7kHz, 10k accum data rate is ~1.4s  
      MCS.bins = 280;  % setting for 7 kHz (21 km)
      MCS.bin_duration = 500;  % ns
      MCS.accum = 10000; 
      P0  = 0.929; % surface pressure in Ellis KS
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 150206) && (date <=  150421)
      profiles2ave.wv = 2*round(((ave_time.wv*60/4.2)+1)/2);  % 7kHz, 30k accum data rate is ~4.2s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/4.2)+1)/2); % 7kHz, 30k accum data rate is ~4.2s 
      MCS.bins = 280;  % after 2-Feb-2015
      MCS.bin_duration = 500;  % ns
      MCS.accum = 30000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 140613) && (date <=  150205) % FRAPPE data set
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2);  % 9kHz, 10k accum data rate is ~1.1s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2); % 9kHz, 10k accum data rate is ~1.1s 
      MCS.bins = 220;  % 14-June-2014 to 2-Feb-2015
      MCS.bin_duration = 500;  % ns 
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    elseif (date >= 140517) && (date <=  140613)
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2);  % 9kHz, 10k accum data rate is ~1.1s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2); % 9kHz, 10k accum data rate is ~1.1s
      MCS.bins = 2195; % 17-May-2014 to 13-June-2014
      MCS.bin_duration = 50;  %initial code assumed a 50 ns bin duration or 7.5 meter gate
      MCS.accum = 10000; 
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    else
      profiles2ave.wv = 2*round(((ave_time.wv*60/1.1)+1)/2);  % 9kHz, 10k accum data rate is ~1.1s  
      profiles2ave.rb = 2*round(((ave_time.rb*60/1.1)+1)/2); % 9kHz, 10k accum data rate is ~1.1s
      MCS.bins= 1995; % 17-Dec-2013 to 17-May-2014
      MCS.bin_duration = 50;  %initial code assumed a 50 ns bin duration or 7.5 meter gate
      MCS.accum = 10000;
      P0  = 0.83; % surface pressure in Boulder
      switch_ratio = 0.5; % online switching ratio
      % the timing range correction moves range to the center of the pulse
      % and then corrects for a MCS error were the first bin was a control bit
      timing_range_correction = -((0.1+1/2)-0.5/2)*150 %- 150*MCS.bin_duration/1000;
      blank_range = 300;
    end
