% Modified by Stillwell in Jan-Feb 2018
        % Clear out all unused (commented out) lines and fat 
        % Pushing sub-tasks into subfunctions for readability
        % Changed variable names to push data into structures/cell arrays

        % This function is to replicate Scott's code with nothing added
        % except reading new data format (use with new Labview)
        
function DIALAnalysis_V01_01(JSondeData, Options, Paths)
%
%
%
%
%
%
%
%
%
%%
fprintf(['Processing: ',Options.System,' data from 20',Paths.Date,'\n'])
%% Defining type map
if strcmp(Paths.FigureType,'DIAL01')
    % Map in the stored cell arrays
    Map.Channels  = {'Offline';'Online'};
    Map.Offline   = 1;
    Map.Online    = 2;
    % Map to get to hardware location
    HardwareMap.ChannelName    = {'WV Offline';'WV Online'};
    HardwareMap.Etalon         = [1;1];
    HardwareMap.Laser          = [0;1];
    HardwareMap.PhotonCounting = [0;8];
    HardwareMap.Power          = [0;6];
elseif strcmp(Paths.FigureType,'DIAL02')
    % Map in the stored cell arrays
    Map.Channels  = {'Online';'Offline';'Molecular';'Combined'};
    Map.Combined  = 4;
    Map.Offline   = 2;
    Map.Online    = 1;
    Map.Molecular = 3;
    % Map to get to hardware location
    HardwareMap.ChannelName    = {'WV Online';'WV Offline';'HSRL Molecular';'HSRL Combined'};
    HardwareMap.PhotonCounting = [0;8;2;3];
    HardwareMap.Power          = [0;6;1;1];
    HardwareMap.Etalon         = [0;0;1;1];
    HardwareMap.Laser          = [0;1;2;2];
elseif strcmp(Paths.FigureType,'DIAL03')
    % Map in the stored cell arrays
    Map.Channels  = {'Offline';'Online'};
    Map.Offline   = 1;
    Map.Online    = 2;
    % Map to get to hardware location
    HardwareMap.ChannelName    = {'WV Offline';'WV Online'};
    HardwareMap.Etalon         = [0;0];
    HardwareMap.Laser          = [0;1];
    HardwareMap.PhotonCounting = [0;8];
    HardwareMap.Power          = [0;6];
end

DataTypes = {'Etalonsample*.nc';'LLsample*.nc';'MCSsample*.nc';'Powsample*.nc';'WSsample*.nc'};

%% Pulling information out of the file names and paths
% DayOfYear = juliandate(['20',Paths.Date],'yyyymmdd') - ...
%             juliandate(['20',Paths.Date(1:2),'0101'],'yyyymmdd') + 1; 
DayOfYear = day(datetime(['20',Paths.Date],'inputformat','yyyyMMdd'),'dayofyear');    
        
year      = 2000 + str2double(Paths.Date(1:2)); 
        
Paths.FolderDate = Paths.Date;
Paths.FolderType = 'All';

%% Defining processing options
method        = 'linear';
extrapolation = 'extrap'; 

%% Setting filepaths and loading data            
tic;
% Loading colormap
cd('/usr/local/home/rsfdata/git/lrose-projects-eolbase/projDir/dial/MatlabV2/DataFiles')
Plotting.ColorMap = importdata('NCAR_C_Map.mat');
% Loading HITRAN data
HitranData = dlmread('815nm_841nm_HITRAN_2008.csv',',',[1 1 1676 8]);
cd(Paths.Code)

%% Defining constants 
% use to keep the arbitrary units of RB scale the same before
RB_scale = 1; 
%Spatial averaging (range average) in bins.  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Should be removable with current data availible 
PulseInfo.BinWidth    = round((JSondeData.MCS.bin_duration*1e-9*3e8/2)*10)/10;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
PulseInfo.DeltaRIndex = 150/PulseInfo.BinWidth; % this is the cumlative sum photons gate spacing 
PulseInfo.DeltaR      = PulseInfo.DeltaRIndex*PulseInfo.BinWidth*100; % delta r in cm
% Defining arrays used to smooth the data
AverageRange   = [1;round(1500/PulseInfo.BinWidth);round(2500/PulseInfo.BinWidth)];
SpatialAverage = [150/PulseInfo.BinWidth; 300/PulseInfo.BinWidth; 600/PulseInfo.BinWidth];

%% Importing online and offline files from the selected date
% Loading data
fprintf('Loading Data\n')
[Etalon,Laser,MCS,Power,WStation] = RawNetCDFDataRead(DataTypes,HardwareMap,Paths);
[Counts,PulseInfoNew]             = RawNetCDFDataParse(Etalon,Laser,MCS,Power,WStation,HardwareMap);
[~,PulseInfoNew]                  = RawNetCDFData2RegularGrid(PulseInfoNew);
clear Etalon Laser MCS Power WStation

PulseInfo.DataTimeRaw = double(PulseInfoNew.TimeStamp.LidarData{1,1})./24 + DayOfYear;
clear DayOfYear

%% read in housekeeping station data
PulseInfo.BenchTemperature      = nan.*PulseInfo.DataTimeRaw;                                            % transmitted average power
PulseInfo.LaserCurrent{1,1}     = PulseInfoNew.Laser.Current{1,1};           % Offline current
PulseInfo.LaserCurrent{2,1}     = PulseInfoNew.Laser.Current{2,1};           % Online current
PulseInfo.LaserTemperature{1,1} = PulseInfoNew.Laser.TemperatureActual{1,1}; % offline current
PulseInfo.LaserTemperature{2,1} = PulseInfoNew.Laser.TemperatureActual{2,1}; % online current
% % % PulseInfo.LaserPower            = PulseInfoNew.Laser.Power{1,1};             % transmitted average power

if Options.flag.WS==1
  SurfaceWeather.Temperature      = PulseInfoNew.WeatherStation.Temperature;            %temperature in C
  SurfaceWeather.Pressure         = PulseInfoNew.WeatherStation.Pressure./1013.249977;  % pressure in atm
  SurfaceWeather.RelativeHumidity = PulseInfoNew.WeatherStation.RelHumidity;
  % Calculate surface parameters from weatherstation data
  [SurfaceWeather.AbsoluteHumidity,SurfaceWeather.NumberDensity] = ConvertWeatherStationValues(SurfaceWeather.RelativeHumidity,SurfaceWeather.Temperature);
end

%% Initial data preparation
fprintf('Processing Data\n')
% analyze system stability 
PulseInfo.DataTimeStep = [0;diff(PulseInfoNew.TimeStamp.LidarData{2,1})];
% grid data in time to final array size
PulseInfo.DataTime = (floor(min(PulseInfo.DataTimeRaw)):1/24/60*(Options.ave_time.gr):(floor(min(PulseInfo.DataTimeRaw))+1))';
% remove the time lag from cumsum
PulseInfo.DataTimeShifted    = PulseInfo.DataTime -(1/24/60*((Options.ave_time.wv-1)/2));
%Calculating average wavelenth
for m=1:1:size(Counts.Raw,1)
    if strcmp(Options.System,'DIAL01')
       WavelengthOffset = -0.09e-3;
    else
       WavelengthOffset = 0;
    end
    PulseInfo.Lambda{m,1} = PulseInfoNew.Laser.WavelengthActual{m,1} + WavelengthOffset;
end

for ii=1:size(PulseInfo.Lambda{2,1},1)
    if ii>1&& PulseInfo.Lambda{2,1}(ii)<828
        PulseInfo.Lambda{2,1}(ii)=PulseInfo.Lambda{2,1}(ii-1);
    end
    if ii>1&& PulseInfo.Lambda{1,1}(ii)<828
        PulseInfo.Lambda{1,1}(ii)=PulseInfo.Lambda{1,1}(ii-1);
    end
end
clear ii

if nanstd(PulseInfo.Lambda{2,1}) >= 5e-4
    h = msgbox('Online wavelength not stable during time period','Warning','warn');
end

%% check for multiple wavelengths
Possible = [828.180,828.220; 
            828.280,828.320;
            780.220,780.260];
for m=1:1:size(PulseInfo.Lambda,1)
    PulseInfo.LambdaMedian{m,1} = nanmedian(PulseInfo.Lambda{m,1});
    A = find(sum([Possible(:,1)<PulseInfo.LambdaMedian{m,1}, ...
                  Possible(:,2)>PulseInfo.LambdaMedian{m,1}],2) == 2);
    if isempty(A) == 0
       [value,edges]=histcounts(round(PulseInfo.Lambda{m,1},3),Possible(A,1):.00001:Possible(A,2)); % bin rounded wavelengths
% % %        PulseInfo.LambdaNumber{m,1}  = edges(value>=10);  % wavelength values with occurance > 10
       PulseInfo.LambdaNumber{m,1}  = nanmean(PulseInfo.Lambda{m,1});
       PulseInfo.LambdaNearest{m,1} = round(PulseInfo.Lambda{m,1},4);
    else
       PulseInfo.LambdaNumber{m,1}  = nanmean(PulseInfo.Lambda{m,1});
       PulseInfo.LambdaNearest{m,1} = round(PulseInfo.Lambda{m,1},4);
    end
end
clear A edges value Possible



  
%% Range vector in meters
Altitude.RangeOriginal = single(0:PulseInfo.BinWidth:(size(Counts.Raw{2,1},2)-1)*PulseInfo.BinWidth);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Altitude.RangeSquared  = (Altitude.RangeOriginal).^2./((JSondeData.MCS.bin_duration*JSondeData.MCS.accum*(1-JSondeData.SwitchRatio)));  % in units of km^2 C/ns

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Altitude.RangeShift    = (PulseInfo.DeltaRIndex-1)/2*PulseInfo.BinWidth + JSondeData.RangeCorrection; %
Altitude.RangeActual   = Altitude.RangeOriginal+Altitude.RangeShift; % actual range points of data

%% Processing photon counts
i = size(Counts.Raw{1,1}, 1);         % Number of time bins
j = size(Altitude.RangeOriginal, 2);  % Number of altitude bins

% Looping over channels and performing operations on photon counting data
for m=1:1:size(Counts.Raw,1)
    % Parsing photon counts from raw data
    Counts.Parsed{m,1} = single(Counts.Raw{m,1});
    % Applying saturation correction
    if Options.flag.pileup == 1
        Counts.Parsed{m,1} = CorrectPileUp(Counts.Parsed{m,1},JSondeData.MCS,JSondeData.DeadTime);
    end
    % select last ~1200 meters to measure background
    Counts.Background1D{m,1} = mean(Counts.Parsed{m,1}(:,end-round(1200/PulseInfo.BinWidth):end),2)-0;
    % Instantiate the 2 dimensional background array
    Counts.Background2D{m,1} = repmat(Counts.Background1D{m,1}, 1, size(Counts.Parsed{m,1},2));
    % Background subtracting the parsed counts
    Counts.BackgroundSubtracted{m,1} = (bsxfun(@minus, Counts.Parsed{m,1}, Counts.Background1D{m,1}));
    % smooth RB for 1 minute and set spatial average 
    Counts.RelativeBackscatter{m,1} = movmean(Counts.BackgroundSubtracted{m,1},JSondeData.Profiles2Average.rb.*2,1,'omitnan');
    % Range correcting relative backscatter
    Counts.RelativeBackscatter{m,1} = bsxfun(@times,  Counts.RelativeBackscatter{m,1}, Altitude.RangeSquared);
    Counts.RelativeBackscatter{m,1}(isnan(Counts.Parsed{m,1})) = nan;
    % Integrating photon counts in time and space
    Temp                            = cumsum(Counts.BackgroundSubtracted{m,1},1,'omitnan')-[zeros(JSondeData.Profiles2Average.wv,j); cumsum(Counts.BackgroundSubtracted{m,1}(1:i-JSondeData.Profiles2Average.wv,:),1,'omitnan')];  %rolling average of rows or time
    Counts.Integrated{m,1}          = cumsum(Temp,2,'omitnan')-[zeros(i,PulseInfo.DeltaRIndex), cumsum(Temp(:,1:j-PulseInfo.DeltaRIndex),2,'omitnan')]; % rolling sum of collumns or range
    Counts.Integrated{m,1}(isnan(Counts.Parsed{m,1})) = nan;
    % Converting background to count rate (counts/sec
    Counts.Background1D{m,1}        = Counts.Background1D{m,1}/(JSondeData.MCS.bin_duration*1e-9*JSondeData.MCS.accum*JSondeData.SwitchRatio); 
    % Integrating background counts in time (no need to do space)
    Counts.Background2D{m,1} = cumsum(Counts.Background2D{m,1},1,'omitnan')-[zeros(JSondeData.Profiles2Average.wv,j); cumsum(Counts.Background2D{m,1}(1:i-JSondeData.Profiles2Average.wv,:),1,'omitnan')];  %rolling average of rows or time
    Counts.Background2D{m,1}(isnan(Counts.Parsed{m,1})) = nan;
    % Grid to regular gate spacing (75 m)
    Counts.Integrated{m,1}   = interp1(Altitude.RangeActual,Counts.Integrated{m,1}',   Altitude.RangeOriginal,method,extrapolation)'; % grid on to standard range bins
    Counts.Background2D{m,1} = interp1(Altitude.RangeActual,Counts.Background2D{m,1}', Altitude.RangeOriginal,method,extrapolation)';
    % Regular averaging
    Counts.CountRate{m,1}    = Counts.Integrated{m,1}./JSondeData.Profiles2Average.wv./PulseInfo.DeltaRIndex;
    % Grid to regular gate spacing in time (???????make recursive???????)
    Counts.Background2D{m,1}        = interp1(PulseInfo.DataTimeRaw, Counts.Background2D{m,1}       ,PulseInfo.DataTime,method,extrapolation);
    Counts.Background1D{m,1}        = interp1(PulseInfo.DataTimeRaw, Counts.Background1D{m,1}       ,PulseInfo.DataTime,method,extrapolation);
    Counts.Integrated{m,1}          = interp1(PulseInfo.DataTimeRaw, Counts.Integrated{m,1}         ,PulseInfo.DataTime,method,extrapolation);
    Counts.CountRate{m,1}           = interp1(PulseInfo.DataTimeRaw, Counts.CountRate{m,1}          ,PulseInfo.DataTime,method,extrapolation);
    Counts.ParsedFinalGrid{m,1}     = interp1(PulseInfo.DataTimeRaw, Counts.Parsed{m,1}             ,PulseInfo.DataTime,method,extrapolation);
    Counts.RelativeBackscatter{m,1} = interp1(PulseInfo.DataTimeRaw, Counts.RelativeBackscatter{m,1},PulseInfo.DataTime,method,extrapolation);
    % Remove the time lag from cumsum (???????make recursive???????)
    Counts.Background2D{m,1} = interp1(PulseInfo.DataTimeShifted, Counts.Background2D{m,1},PulseInfo.DataTime,method,extrapolation);
    Counts.CountRate{m,1}    = interp1(PulseInfo.DataTimeShifted, Counts.CountRate{m,1}   ,PulseInfo.DataTime,method,extrapolation);
    Counts.Integrated{m,1}   = interp1(PulseInfo.DataTimeShifted, Counts.Integrated{m,1}  ,PulseInfo.DataTime,method,extrapolation);
    % Removing any negative counts 
    Counts.CountRate{m,1}(real(Counts.CountRate{m,1}) <= 0) = 0;
    Counts.RelativeBackscatter{m,1}(real(Counts.RelativeBackscatter{m,1}) <= 0) = 0;
end
clear m Temp i j

%% temporal and spatial averaging 
% blank lowest gates...not needed on HSRL
blank = nan.*ones(size(Counts.Integrated{1,1}(:,1:JSondeData.BlankRange/PulseInfo.BinWidth)));
Counts.CountRate{Map.Online,1}  = single(horzcat(blank, Counts.CountRate{Map.Online,1} (:,(JSondeData.BlankRange/PulseInfo.BinWidth+1):end)));
Counts.CountRate{Map.Offline,1}  = single(horzcat(blank, Counts.CountRate{Map.Offline,1} (:,(JSondeData.BlankRange/PulseInfo.BinWidth+1):end)));
clear blank

% Recursively interpolate weather station data from collected to averaged grid
if Options.flag.WS == 1
    SurfaceWeather = RecursivelyInterpolateStructure(SurfaceWeather,PulseInfo.DataTimeRaw,PulseInfo.DataTime,method,extrapolation);
end
% Recursively interpolating pulseinfo from collected time grid to averaged grid
PulseInfo = RecursivelyInterpolateStructure(PulseInfo,double(PulseInfo.DataTimeRaw),double(PulseInfo.DataTime),method,extrapolation);

%% Gradient filter
if Options.flag.gradient_filter == 1
    [FX,~] = gradient(Counts.CountRate{Map.Offline,1});
    Counts.CountRate{Map.Offline,1}(FX<-1000 | FX> 1000) = nan; % remove falling (leading) edge of clouds
    if Options.flag.troubleshoot == 1
        Plotting_TroubleshootingPlots4
    end
    clear FX
end

%% Spectral Line Fitting
if strcmp(Options.System, 'DIAL03')
    Options.flag.WS = 0;
end

[DataProducts.Sigma{Map.Online,1},DataProducts.Sigma{Map.Offline,1}] =  ...
    SpectralLineFitting(Options.flag, PulseInfo.LambdaNearest{Map.Online,1},  ...
                                      PulseInfo.LambdaNearest{Map.Offline,1}, ...
                                      PulseInfo.LambdaNumber{Map.Online,1},   ...
                                      PulseInfo.LambdaNumber{Map.Offline,1},  ...
                                      HitranData,                             ...
                                      Counts.CountRate{Map.Offline,1},        ...
                                      Altitude.RangeOriginal,                 ...
                                      SurfaceWeather.Pressure,                ...
                                      SurfaceWeather.Temperature);
if strcmp(Options.System, 'DIAL03')
    Options.flag.WS = 1;
end
                                  
% [DataProducts.Sigma{Map.Online,1},DataProducts.Sigma{Map.Offline,1}] =  ...
%     SpectralLineFitting(Options.flag, PulseInfo.LambdaNearest{Map.Online,1}, PulseInfo.LambdaNearest{Map.Offline,1}, PulseInfo.LambdaNumber{Map.Online,1}, PulseInfo.LambdaNumber{Map.Offline,1}, HitranData,Counts.CountRate{Map.Online,1},Altitude.RangeOriginal, SurfaceWeather.Pressure, SurfaceWeather.Temperature);

%% DIAL Equation to calculate Number Density and error
[DataProducts.N,DataProducts.N_Error] = DIALEquationNarrowlySpaced(Counts.CountRate{Map.Online,1},     ...
                                                                   Counts.Integrated{Map.Online,1},    ...
                                                                   Counts.CountRate{Map.Offline,1},    ...
                                                                   Counts.Integrated{Map.Offline,1},   ...
                                                                   Counts.Background2D{Map.Online,1},  ...
                                                                   Counts.Background2D{Map.Offline,1}, ...
                                                                   DataProducts.Sigma{Map.Online,1},   ...
                                                                   DataProducts.Sigma{Map.Offline,1},  ...
                                                                   PulseInfo.BinWidth);

%% Molecular backscatter 
% Calculate temperature and pressure profile based on surface measurement and 
% asuming a standard lapse rate (-6.5 deg/km) for the entire troposphere
if Options.flag.WS == 1
    T0 = nanmedian(SurfaceWeather.Temperature)+273.15;
    P0 = nanmedian(SurfaceWeather.Pressure);
else
	T0 = 290; % surface temperature
end
% standard lapse rate (-6.5 deg/km) for the entire troposphere
DataProducts.TemperatureProfile = T0-0.0065.*Altitude.RangeOriginal; 
% hydrostatic equation and ideal gas law
DataProducts.PresssureProfile   = P0.*(T0./DataProducts.TemperatureProfile).^-5.5;   
% Defining constants
const.k_B = 1.363806488e-23*9.89*10^-6; % (atm m^3/K)
% Calculating the molecular backscatter profile
DataProducts.BetaMProfile   = 5.45.*10^(-32).*(550/780.2)^4.*DataProducts.PresssureProfile./(DataProducts.TemperatureProfile.*const.k_B); %backscatter coefficient in m^-1 sr^-1
DataProducts.BetaMProfileWV = 5.45.*10^(-32).*(550/828.2)^4.*DataProducts.PresssureProfile./(DataProducts.TemperatureProfile.*const.k_B);
clear T0 P0
  
%% Smoothing Number Density for different range zones
if Options.flag.gradient_filter == 1
    DataProducts.N(DataProducts.N>1E18) = nan; % use this to remove high water vapor errors
end
% Calculating spatial averaging components assuming non-constant averaging
NError = []; Navg = [];
for m=1:1:size(SpatialAverage,1)
    N_error{m,1} = real(DataProducts.N_Error./sqrt(SpatialAverage(m)));      %#ok<AGROW>
    N_avg{m,1}   = movmean(DataProducts.N,SpatialAverage(m).*2,2,'omitnan'); %#ok<AGROW>
    N_avg{m,1}(isnan(DataProducts.N)) = nan;                                 %#ok<AGROW>
    % Finding the array indices to impliment non-uniform averaging 
    StartIndex = AverageRange(m);
    if m ~= 1
        StartIndex = StartIndex + 1;
    end
    if m == size(SpatialAverage,1)
        EndIndex   = size(DataProducts.N_Error,2);
    else
        EndIndex   = AverageRange(m+1);
    end
    % Recombinging non-uniform averaged data into a single contour
    NError = [NError;N_error{m,1}(:,StartIndex:EndIndex)'];                %#ok<AGROW>
    Navg   = [Navg  ;N_avg{m,1}(:,StartIndex:EndIndex)'];                  %#ok<AGROW>
end
%smooth again at the smallest resolution to avoid boundaries
DataProducts.N_Error = movmean(NError',SpatialAverage(1).*2,2,'omitnan');
DataProducts.N_Error(isnan(NError')) = nan;
DataProducts.N_avg   = movmean(Navg',SpatialAverage(1).*2,2,'omitnan');
DataProducts.N_avg(isnan(Navg')) = nan;
clear NError Navg StartIndex EndIndex N_error N_avg m

%% Mask the Number density data based on the error, correct for range center, and add WS data at lowest gate 
DataProducts.N_Masked = DataProducts.N_avg;
DataProducts.N_Masked(DataProducts.N_avg < 0) = nan; % remove non-pysical (negative) wv regions
DataProducts.N_Masked(abs(DataProducts.N_Error./DataProducts.N_avg) > 2.00) = nan; % remove high error regions
DataProducts.N_Masked(Counts.ParsedFinalGrid{1,1}./(JSondeData.MCS.bin_duration*1e-9*JSondeData.MCS.accum) > 5E6) = nan; % remove raw counts above linear count threshold (5MC/s)
% calcuate the range lag for number density (to center in range bin)
Altitude.RangeShift  = PulseInfo.BinWidth/2; %
Altitude.RangeActual = Altitude.RangeOriginal+Altitude.RangeShift; % actual range points of data
% grid to regular (75 m) gate spacing
DataProducts = RecursivelyInterpolateStructure(DataProducts,Altitude.RangeOriginal,Altitude.RangeActual,method, extrapolation);  % grid on to standard range bins
% use the weather station to fill in the bottom gates
if Options.flag.WS == 1 
    DataProducts.N_avg(:,1)    = SurfaceWeather.NumberDensity;  % gate 1, 0 meter
    DataProducts.N_Masked(:,1) = SurfaceWeather.NumberDensity;  % gate 1, 0 meter
end

% if you want to mask the data use this
if Options.flag.mask_data == 1
  DataProducts.N_avg = DataProducts.N_Masked;
end
  
%% Finding optical depth and plotting information
PulseInfo.DataTimeDateNumFormat = datenum(year,1,0)+double(PulseInfo.DataTime);
date     = datestr(nanmean(PulseInfo.DataTimeDateNumFormat), 'dd mmm yyyy');

% OD is - ln(I/I.o), since offline is not the same as online it needs to
% scaled by the first few good gates -- choose 300 m to 450 m
PulseInfo.ScaleOn2Off     = nanmean(Counts.CountRate{2,1}(:,300/PulseInfo.BinWidth:450/PulseInfo.BinWidth),2)./nanmean(Counts.CountRate{1,1}(:,300/PulseInfo.BinWidth:450/PulseInfo.BinWidth),2);
DataProducts.OpticalDepth = -(log(Counts.CountRate{2,1}./bsxfun(@times, Counts.CountRate{1,1}, PulseInfo.ScaleOn2Off))); % calculate column optical depth
  
%% Decimate data in time to final array size
if Options.flag.decimate == 1
    decimate_time  = Options.ave_time.wv/Options.ave_time.gr/2; %ave_time.wv/ave_time.gr;
    decimate_range = 1; % keep native gate spacing
    % Decimating needed count profiles
    for m=1:1:size(Counts.RelativeBackscatter,1)
        % average RB data before decimating
        Counts.RelativeBackscatter{m,1} = movmean(Counts.RelativeBackscatter{m,1},decimate_time*2,1,'omitnan');
        % Decimating
        Counts.RelativeBackscatter{m,1} = Counts.RelativeBackscatter{m,1}(1:decimate_time:end, 1:decimate_range:end);
        Counts.Background1D{m,1}        = Counts.Background1D{m,1}(       1:decimate_time:end, 1:decimate_range:end);
        Counts.CountRate{m,1}           = Counts.CountRate{m,1}(          1:decimate_time:end, 1:decimate_range:end);
    end
    % Decimating altitude to the final grid spacing
    Altitude.RangeOriginal          = Altitude.RangeOriginal(1:decimate_range:end);
    % Decimate data products in space and time
    DataProducts = RecursivelyDecimateStructure2D(DataProducts,decimate_time ,size(DataProducts.OpticalDepth,1), ...
                                                               decimate_range,size(DataProducts.OpticalDepth,2));    
    % Decimating pulse info time series data in time
    PulseInfo = RecursivelyDecimateStructure1D(PulseInfo,decimate_time,size(PulseInfo.LaserPower,1));        
    % Decimating surface weather time series data in time
    if Options.flag.WS ==1
        SurfaceWeather = RecursivelyDecimateStructure1D(SurfaceWeather,decimate_time,size(SurfaceWeather.AbsoluteHumidity,1));        
    end
end

%% Calculate HSRL parameters
% R_size                = 150;
% % Calculating the HSRL retrievals 
% [DataProducts.AExtinction, DataProducts.Extinction, DataProducts.ABackscatterCoeff] = ...
%     FindHSRLParameters(DataProducts.BetaMProfile,Counts.CountRate{4,1},Counts.CountRate{3,1}, ...
%                        ones(1,size(Counts.CountRate{4,1},2)),ones(1,size(Counts.CountRate{4,1},2)), ...
%                        Altitude.RangeOriginal,JSondeData.ReceiverScaleFactor);
% % Applying some data mask for the HSRL data
% if Options.flag.mask_data == 1
%     Combined_masked = Counts.CountRate{3,1};
%     Combined_masked(Counts.CountRate{3,1} < 1/(R_size/PulseInfo.BinWidth)) = nan;
%     Combined_masked(Counts.CountRate{4,1} < 1/(R_size/PulseInfo.BinWidth)) = nan;
%     DataProducts.ABackscatterCoeff(isnan(Combined_masked))          = nan;
%     DataProducts.AExtinction(isnan(DataProducts.ABackscatterCoeff)) = nan;
%     clear Combined_masked
% end
% clear R_size

%% Save Data
fprintf('Saving Data\n')
if Options.flag.save_data == 1
    cd(Paths.SaveData)
    Paths.FileName = ['ProcessedDIALData_20',num2str(Paths.FolderDate),'.mat'];
    save(Paths.FileName,'Altitude','Counts','DataProducts','Options','Paths','Plotting','PulseInfo','SurfaceWeather')
    cd(Paths.Code)
end
if Options.flag.save_netCDF == 1  % save the data as an nc file
    WriteNetCDFData (PulseInfo.LambdaMedian{2,1} ,PulseInfo.LambdaMedian{1,1},DataProducts.N_avg,DataProducts.N_Error,                  ...
                     Counts.CountRate{1,1},Counts.CountRate{2,1}, ...
                     P,Counts.RelativeBackscatter{1,1},Altitude.RangeOriginal,T,PulseInfo.DataTimeDateNumFormat)
end

%% Plot Data
fprintf('Plotting Data\n')
Plotting.ScreenSize = get(0,'ScreenSize');
Plotting.FontSize   = 14;
Plotting.PlotSize1  = [Plotting.ScreenSize(4)/1.5 Plotting.ScreenSize(4)/10 Plotting.ScreenSize(3)/1.5 Plotting.ScreenSize(4)/3];
Plotting.PlotSize2  = [1 Plotting.ScreenSize(4)/2 Plotting.ScreenSize(3)/2 Plotting.ScreenSize(4)/2];
Plotting.x          = (PulseInfo.DataTimeDateNumFormat)';
Plotting.xdata      = linspace(fix(min(PulseInfo.DataTimeDateNumFormat)),...
                              ceil(max(PulseInfo.DataTimeDateNumFormat)), 25);
Plotting.y          = (Altitude.RangeOriginal./1e3);

PlottingMainPlots(Counts,RB_scale,PulseInfo,date,DataProducts,Options,Paths,Plotting,SurfaceWeather)
 
toc
cd(Paths.Code) % point back to original directory
% use this for troubleshooting raw data
if Options.flag.troubleshoot == 1
  Plotting_TroubleshootingPlots2
end

%% Trying to get my arms around the variables
% Variables used only for plotting
clear year date RB_scale XLim YLim 
% Temperary variables used in processing that need not be saved
clear const 
clear HitranData
clear decimate_range decimate_time
clear SpatialAverage AverageRange
clear method extrapolation 
clear m

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Sub-functions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [Surf_AH,Surf_N] = ConvertWeatherStationValues(Surf_RH,Surf_T) 
%
% Inputs: Surf_RH:  Surface relative humidity time series     [Units: %]
%         Surf_T:   Surface temperature time series           [Units: ]
%                   
% Outputs: Surf_AH: Surface absolute humiditiy time series    [Units: g/kg]
%          Surf_N:  Surface number density time series        [Units: ]
%
%% Defining universal constants
R   = 8.31447215;   %J mol^-1 K^-1
N_A = 6.0221415E23; %mol^-1
%% Defining conversion constants for Clausius Clapeyron Equation
a0 = 6.107799961;
a1 = 4.436518521E-1;
a2 = 1.428945805E-2;
a3 = 2.650648471E-4;
a4 = 3.031240396E-6;
a5 = 2.034080948E-8;
a6 = 6.136820929E-11;
%% Calculating vapor pressure of water
e=((a0+Surf_T.*(a1+Surf_T.*(a2+Surf_T.*(a3+Surf_T.*(a4+Surf_T.*(a5+Surf_T.*a6))))))./1); %vapor pressure in hPa
%% Convert RH to number density and absolute humidity
Surf_N  = 1.*(Surf_RH.*(1).*e./(R.*(Surf_T+273).*(1))).*N_A*1e-6;  %cm^3
Surf_AH = Surf_N.*1e6./6.022E23.*18.015;
end

function [CorrCounts] = CorrectPileUp(Counts, MCS, t_d)
%
% Inputs: Counts:      
%         MCS:              
%                      
% Outputs: CorrCounts: 
%
%%
% MCSC gives counts accumulated for set bin duration so convert to count rate  C/s.
% divide by bin time in sec (e.g., 500ns) and # of acumulations (e.g., 10000)
% e.g., 10 accumlated counts is 2000 C/s
CorrFactor = 1./(1-(t_d.*(Counts./(MCS.bin_duration*1E-9*MCS.accum))));
CorrCounts = Counts.*CorrFactor;
end

function [sigma_on_total,sigma_off_total] = SpectralLineFitting(flag, lambda_all_N, lambda_all_off_N, lambda_N, lambda_off_N, hitran, Online_Temp_Spatial_Avg, range, Surf_P, Surf_T)

%Voigt profile calculation
WNmin = 1/(828+4)*1e7;  % 832.0 nm converted to wavenumber
WNmax = 1/(828-4)*1e7;  % 824.0 nm converted to wavenumber

%Find lines from WNmin to WNmax to calculate voigt profile
line_indices = hitran(1:size(hitran,1),1)>WNmin & hitran(1:size(hitran,1),1)<WNmax;

line = double(hitran(line_indices, 1:size(hitran,2)));

%Calculate temperature and pressure profile
if flag.WS == 1
    T0 = nanmedian(Surf_T)+273.15;
    P0 = nanmedian(Surf_P);
else
  T0 = 273+30; % surface temperature
  P0 = 0.83;
end

T = T0-0.0065.*range; % set to match the sounding

% pressure in atmospheres
P = P0.*(T0./T).^-5.5;   % set this value to match sounding

Hitran.T00 = 296;              % HITRAN reference temperature [K]
Hitran.P00 = 1;                % HITRAN reference pressure [atm]
Hitran.nu0_0 = line(:,1);      % absorption line center wavenumber from HITRAN [cm^-1]
Hitran.S0 = line(:,2);         % initial linestrength from HITRAN [cm^-1/(mol*cm^-2)]   
Hitran.gammal0 = line(:,4);    % air-broadened halfwidth at T_ref and P_ref from HITRAN [cm^-1/atm]
Hitran.gamma_s = line(:,5);    % self-broadened halfwidth at T_ref and P_ref from HITRAN [cm^-1/atm]
Hitran.E = line(:,6);          % ground state transition energy from HITRAN [cm^-1]  
Hitran.alpha = line(:,7);      % linewidth temperature dependence factor from HITRAN
Hitran.delta = line(:,8);      % pressure shift from HiTRAN [cm^-1 atm^-1]

% new code to handle multiple wavelength changes during a single day
for l=1:1%length(lambda_N)
    
    Hitran.nu_on = 1/(lambda_N(l))*1e7;
    Hitran.nu_off = 1/(lambda_off_N(l))*1e7;
        
    for i = 1:size(Online_Temp_Spatial_Avg,2) % calculate the absorption cross section at each range
        j=rem(i,25);

        Hitran.nu0 = Hitran.nu0_0+Hitran.delta.*(P(i)./Hitran.P00); % unclear if it should be Pi/P00
        Hitran.gammal = Hitran.gammal0.*(P(i)./Hitran.P00).*((Hitran.T00./T(i)).^Hitran.alpha);    %Calculate Lorentz lineweidth at P(i) and T(i)
        % revise pressure broadened halfwidth to include correction for self broadening term        
        const.m   = 18.015E-3./6.022E23; % mass of a single water molecule
        const.k_B = 1.3806488e-23;       % (J/K)
        const.c   = 299792458;           % (m/s) (exact)
        
        Hitran.gammad = (Hitran.nu0).*((2.0.*const.k_B.*T(i).*log(2.0))./(const.m.*const.c^2)).^(0.5);  %Calculate HWHM Doppler linewidth at T(i)
        
        % term 1 in the Voigt profile
        y = (Hitran.gammal./Hitran.gammad).*((log(2.0)).^(0.5));
        
        % term 2 in the Voigt profile
        x_on = ((Hitran.nu_on-Hitran.nu0)./Hitran.gammad).*(log(2.0)).^(0.5);
        x_off = ((Hitran.nu_off-Hitran.nu0)./Hitran.gammad).*(log(2.0)).^(0.5);
        
        %setting up Voigt convolution
        t = (-(size(line,1))/2:1:size(line,1)/2-1); %set up the integration spectral step size
        t = repmat(t',1,length(x_on))';
        x_on = repmat(x_on,1,length(t));
        x_off = repmat(x_off,1,length(t));
        y = repmat(y,1,length(t));
        f_on = (exp(-t.^2.0))./(y.^2.0+(x_on-t).^2.0);  % combined Voigt term 1 and 2
        f_off = (exp(-t.^2.0))./(y.^2.0+(x_off-t).^2.0);
        %Voigt integration over all of the lines at the on and offline locations
        z_on = trapz(t(1,:),f_on,2);
        z_off =  trapz(t(1,:),f_off,2);
        integral_on = z_on;
        integral_off = z_off;
        %Calculate linestrength at temperature T
        S = Hitran.S0.*((Hitran.T00./T(i)).^(1.5)).*exp(1.439.*Hitran.E.*((1./Hitran.T00)-(1./T(i))));

        %Calculate the Voigt profile
        K_on = (y(:,1)./pi).*integral_on;
        K_off = (y(:,1)./pi).*integral_off;

        %Calculate the Voigt profile absorption cross section [cm^2]
        sigmav_on = S.*(1./Hitran.gammad).*(((log(2.0))./pi).^(0.5)).*K_on; %.*far_wing_on;
        sigmav_off = S.*(1./Hitran.gammad).*(((log(2.0))./pi).^(0.5)).*K_off; %.*far_wing_off;
        
        %Sum contributions from all of the surrounding lines
        sigma_on_total(i) = sum(sigmav_on);
        sigma_off_total(i) = sum(sigmav_off);
        
    end
    
    sigma_on_total = repmat(sigma_on_total,size(Online_Temp_Spatial_Avg,1),1);
    sigma_off_total = repmat(sigma_off_total,size(Online_Temp_Spatial_Avg,1),1);
    
    % new lines to handle multiple wavelengths during the day
    S_on_N(:,:,l) = sigma_on_total;
    S_off_N(:,:,l) = sigma_off_total;
    
% % % %     clear sigma_on_total sigma_off_total sigmav_on sigmav_off
end

% % % % combine the multiwavelenth into a single cross section matrix
% % % sigma_on_total=zeros(size(S_on_N,1),size(S_on_N,2));
% % % sigma_off_total=zeros(size(S_on_N,1),size(S_on_N,2));

sigma_on_total = squeeze(S_on_N);
sigma_off_total = squeeze(S_off_N);

% % % for l=1:length(lambda_N)
% % %     for i = 1:size(Online_Temp_Spatial_Avg,1)
% % %         if single(lambda_all_N(i))==single(lambda_N(l))
% % %             sigma_on_total(i,:)= S_on_N(i,:,l);
% % %         end
% % %         if single(lambda_all_off_N(i))==single(lambda_off_N(l))
% % %             sigma_off_total(i,:)= S_off_N(i,:,l);
% % %         end
% % %     end
% % % end
end

function WriteNetCDFData (lambda,lambda_off,N_avg,N_error,Offline_Temp_Spatial_Avg,Online_Temp_Spatial_Avg,P,RB,range,T,time_new)
%
% Inputs: lambda:
%         lambda_off:
%         N_avg:
%         N_error:
%         Offline_Temp_Spatial_Avg:
%         Online_Temp_Spatial_Avg
%         P:
%         RB:
%         range:
%         T
%         time_new:
%
%% Convert NaN fill values (and Inf) to -1 flag
time_new(isnan(time_new)==1) = -1;  
N_avg(isnan(N_avg)==1)       = -1;
N_error(isnan(N_error)==1)   = -1;
N_avg(isinf(N_avg)==1)       = -1;
N_error(isinf(N_error)==1)   = -1;
Offline_Temp_Spatial_Avg(isinf(Offline_Temp_Spatial_Avg)==1) = -1;
Online_Temp_Spatial_Avg(isinf(Online_Temp_Spatial_Avg)==1)   = -1;
time_unix = (time_new-datenum(1970,1,1))*86400; % convert to unix time
   
%% Creating the NetCDF file and dimensions
% Define the file
cdf_name = strcat('wv_dial.', datestr(date, 'yymmdd'), Paths.FolderType);
ncid     = netcdf.create([cdf_name '.nc'],'CLOBBER');
% define the dimensions and variables
dimid1 = netcdf.defDim(ncid,'time',netcdf.getConstant('NC_UNLIMITED'));
dimid2 = netcdf.defDim(ncid, 'range', length(range));
dimid3 = netcdf.defDim(ncid, 'lambda', length(lambda));
    
%% Defining the variables
myvarID1 = netcdf.defVar(ncid,'time','double',dimid1);
  netcdf.putAtt(ncid, myvarID1, 'units', 'days since January 0, 0000')
myvarID2 = netcdf.defVar(ncid,'range','float',dimid2);
  netcdf.putAtt(ncid, myvarID2, 'units', 'meters')
myvarID3 = netcdf.defVar(ncid,'N_avg','float',[dimid2 dimid1]);
  netcdf.putAtt(ncid, myvarID3, 'long_name', 'water_vapor_number_density')
  netcdf.putAtt(ncid, myvarID3, 'units', 'molecules/cm^3')
  netcdf.putAtt(ncid, myvarID3, 'FillValue', '-1')
myvarID4 = netcdf.defVar(ncid,'N_error','float',[dimid2 dimid1]);
  netcdf.putAtt(ncid, myvarID4, 'long_name', 'water_vapor_number_density_error')
  netcdf.putAtt(ncid, myvarID4, 'units', 'molecules/cm^3')
  netcdf.putAtt(ncid, myvarID4, 'FillValue', '-1')
myvarID5 = netcdf.defVar(ncid,'P','float', dimid2);
  netcdf.putAtt(ncid, myvarID5, 'long_name', 'pressure')
  netcdf.putAtt(ncid, myvarID5, 'units', 'atm')
myvarID6 = netcdf.defVar(ncid,'T','float', dimid2);
  netcdf.putAtt(ncid, myvarID6, 'long_name', 'temperature')
  netcdf.putAtt(ncid, myvarID6, 'units', 'degK')
myvarID7 = netcdf.defVar(ncid,'RB','float',[dimid2 dimid1]);
  netcdf.putAtt(ncid, myvarID7, 'long_name', 'relative_backscatter')
  netcdf.putAtt(ncid, myvarID7, 'units', 'arbitrary_units')
  netcdf.putAtt(ncid, myvarID7, 'FillValue', '-1')
myvarID8 = netcdf.defVar(ncid,'time_unix','double',dimid1);
  netcdf.putAtt(ncid, myvarID8, 'long_name', 'unix time')
  netcdf.putAtt(ncid, myvarID8, 'units', 'seconds since 00:00:00 UTC, January 1, 1970')
  netcdf.putAtt(ncid, myvarID8, 'FillValue', '-1')
myvarID9 = netcdf.defVar(ncid,'Offline_Temp_Spatial_Avg','float',[dimid2 dimid1]);
  netcdf.putAtt(ncid, myvarID9, 'long_name', 'offline counts')
  netcdf.putAtt(ncid, myvarID9, 'units', 'counts')
  netcdf.putAtt(ncid, myvarID9, 'FillValue', '-1')
myvarID10 = netcdf.defVar(ncid,'Online_Temp_Spatial_Avg','float',[dimid2 dimid1]);
  netcdf.putAtt(ncid, myvarID10, 'long_name', 'online counts')
  netcdf.putAtt(ncid, myvarID10, 'units', 'counts')
  netcdf.putAtt(ncid, myvarID10, 'FillValue', '-1')
myvarID11 = netcdf.defVar(ncid,'lambda','float', dimid3);
  netcdf.putAtt(ncid, myvarID11, 'long_name', 'online wavelength')
  netcdf.putAtt(ncid, myvarID11, 'units', 'nm')
  netcdf.putAtt(ncid, myvarID11, 'FillValue', '-1')
myvarID12 = netcdf.defVar(ncid,'lambda_off','float', dimid3);
  netcdf.putAtt(ncid, myvarID11, 'long_name', 'offline wavelength')
  netcdf.putAtt(ncid, myvarID11, 'units', 'nm')
  netcdf.putAtt(ncid, myvarID11, 'FillValue', '-1')
netcdf.endDef(ncid)

%% Save the variables to the file
netcdf.putVar(ncid,myvarID1,0,length(time_new),time_new);
netcdf.putVar(ncid,myvarID2,range);
netcdf.putVar(ncid,myvarID3,[0,0],size(N_avg'),N_avg');
netcdf.putVar(ncid,myvarID4,[0,0],size(N_error'),N_error');
netcdf.putVar(ncid,myvarID5,P);
netcdf.putVar(ncid,myvarID6,T);
netcdf.putVar(ncid,myvarID7,[0,0],size(RB'),RB');
netcdf.putVar(ncid,myvarID8,time_unix);
netcdf.putVar(ncid,myvarID9,[0,0],size(Offline_Temp_Spatial_Avg'),Offline_Temp_Spatial_Avg');
netcdf.putVar(ncid,myvarID10,[0,0],size(Online_Temp_Spatial_Avg'),Online_Temp_Spatial_Avg');
netcdf.putVar(ncid,myvarID11,lambda);
netcdf.putVar(ncid,myvarID12,lambda_off);
netcdf.close(ncid);
end



function [Etalon,Laser,MCS,Power,WStation] = RawNetCDFDataRead(DataTypes,HardwareMap,Paths)
%
%
%
%
%
%
%%
cd(Paths.RawNetCDFData)
%% Pre-allocating data
Etalon.TemperatureActual  = [];
Etalon.TemperatureDesired = [];
Etalon.TimeStamp          = [];
Etalon.Type               = [];  % Not coming through

Laser.Current             = [];
Laser.Locked              = [];
Laser.TemperatureActual   = [];
Laser.TemperatureDesired  = [];
Laser.TimeStamp           = [];
Laser.Type                = []; % Not coming through
Laser.WavelengthActual    = [];
Laser.WavelengthDesired   = [];

MCS.Channel               = [];
% MCS.ChannelAssignment     = []; % Not coming through
MCS.Data                  = [];
MCS.ProfilesPerHistogram  = [];
MCS.RangeResolution       = [];
MCS.TimeStamp             = [];
         
Power.LaserPower          = [];
Power.TimeStamp           = [];

WStation.AbsoluteHumidity = [];
WStation.Pressure         = [];
WStation.RelativeHumidity = [];
WStation.Temperature      = [];
WStation.TimeStamp        = [];

%% Loading data
for m=1:1:size(DataTypes,1)
    % Finding all of the relevant files
   s = dir(DataTypes{m,1}); 
   for n=1:1:size(s,1)
       % Determining the current file name
       Filename = s(n,1).name;
       % Loading the data
       switch DataTypes{m,1}
           case 'Etalonsample*.nc'
               Etalon.TimeStamp          = [Etalon.TimeStamp         ;double(ncread(Filename,'time'))];
%                Etalon.Type               = [Etalon.Type              ;ncread(Filename,'EtalonNum')];
               Etalon.TemperatureActual  = [Etalon.TemperatureActual ;ncread(Filename,'Temperature')];
               Etalon.TemperatureDesired = [Etalon.TemperatureDesired;ncread(Filename,'TempDiff')];
           case 'LLsample*.nc'
               Laser.TimeStamp           = [Laser.TimeStamp          ;double(ncread(Filename,'time'))];
%                Laser.Type                = [Laser.Type               ;ncread(Filename,'LaserName')];
               Laser.WavelengthActual    = [Laser.WavelengthActual   ;double(ncread(Filename,'Wavelength'))];
               Laser.WavelengthDesired   = [Laser.WavelengthDesired  ;double(ncread(Filename,'WaveDiff'))];
               Laser.Locked              = [Laser.Locked             ;ncread(Filename,'IsLocked')];
               Laser.TemperatureActual   = [Laser.TemperatureActual  ;ncread(Filename,'TempMeas')];
               Laser.TemperatureDesired  = [Laser.TemperatureDesired ;ncread(Filename,'TempDesired')];
               Laser.Current             = [Laser.Current            ;ncread(Filename,'Current')];
           case 'MCSsample*.nc'
               A = double(ncread(Filename,'time'));
               if str2double(Filename(10:11)) == 23
                   % Checking to make sure all data is reported today
                   A(A<23) = A(A<23)+24;
               end
               MCS.TimeStamp             = [MCS.TimeStamp            ;A];
               MCS.ProfilesPerHistogram  = [MCS.ProfilesPerHistogram ;ncread(Filename,'ProfilesPerHist')];
               MCS.Channel               = [MCS.Channel              ;ncread(Filename,'Channel')];
               MCS.RangeResolution       = [MCS.RangeResolution      ;ncread(Filename,'CntsPerBin')];
               MCS.Data                  = [MCS.Data                 ;single(ncread(Filename,'Data'))];  
               clear A
           case 'Powsample*.nc'
               Power.LaserPower          = [Power.LaserPower         ;ncread(Filename,'Power')];
               A = double(ncread(Filename,'time'));
               if str2double(Filename(10:11)) == 23
                   % Checking to make sure all data is reported today
                   A(A<23) = A(A<23)+24;
               end
               Power.TimeStamp           = [Power.TimeStamp          ;A];
               clear A
           case 'WSsample*.nc'
               A = double(ncread(Filename,'time'));
               if str2double(Filename(9:10)) == 00
                   A(A>23) = A(A>23)-24;
               end
               WStation.TimeStamp        = [WStation.TimeStamp       ;A];
               WStation.Temperature      = [WStation.Temperature     ;ncread(Filename,'Temperature')];
               WStation.RelativeHumidity = [WStation.RelativeHumidity;ncread(Filename,'RelHum')];
               WStation.Pressure         = [WStation.Pressure        ;ncread(Filename,'Pressure')];
               WStation.AbsoluteHumidity = [WStation.AbsoluteHumidity;ncread(Filename,'AbsHum')];
       end
   end
end
clear m n s A Filename
% Converting differences to actual desired numbers
Etalon.TemperatureDesired = Etalon.TemperatureActual - Etalon.TemperatureDesired;
Laser.WavelengthDesired   = Laser.WavelengthActual   - Laser.WavelengthDesired;

%% Temp code needed because I can't fully read netCDF files
% Temporary code to determine the etalon types
Etalon.Type = zeros(size(Etalon.TimeStamp));
Etalon.Type(Etalon.TemperatureDesired<25) = 0;   % Check this
Etalon.Type(Etalon.TemperatureDesired>25) = 1;
% Temporary code to determine the laser types
Laser.Type = zeros(size(Laser.TimeStamp));
Laser.Type(Laser.WavelengthDesired < 800) = 2;
Laser.Type(Laser.WavelengthDesired > 828.27) = 1;

% Getting better 
A = find(diff(Power.TimeStamp) == 0);
Counter = 0;
while ~isempty(A)
    Counter = Counter + 1;
    Power.TimeStamp(diff(Power.TimeStamp) == 0) = Power.TimeStamp(diff(Power.TimeStamp) == 0) + 1e-9;
    A = find(diff(Power.TimeStamp) == 0);
    if Counter == 300
        fprintf('More than 300 power time stamps were identical.\n')
        break
    end
end
clear A Counter

%% Getting rid of incomplete data
% Checking for MCS data
MCSFirst = find(MCS.Channel == min(HardwareMap.PhotonCounting),1,'first');
MCSLast  = find(MCS.Channel == max(HardwareMap.PhotonCounting),1,'last');
% Removing incomplete scan at the start of the day
if MCSFirst ~= 1
    MCS.Channel(1:(MCSFirst-1)) = nan;
end
% Removing incomplete scan at the end of the day
if MCSLast ~= size(MCS.Channel,1)
    MCS.Channel((MCSLast+1):end) = nan;
end
clear MCSFirst MCSLast
% Removing incomplete scan in the middle of the day
MCS = RemoveIncompleteMCSScans(MCS);

%% Removing bad laser scans
BadData = find(Laser.WavelengthActual == -1);
if isempty(BadData) == 0
    % Converting the names structure to a cell array
    CellArray  = struct2cell(Laser);
    FieldNames = fieldnames(Laser);
    % Removing bad data
    for m=1:1:size(CellArray)
        CellArray{m,1}(BadData,:) = [];
    end
    % Converting back to a named structure
    Laser = cell2struct(CellArray,FieldNames);
    clear CellArray FieldNames m
end
clear BadData 

%% Filling in bad data
TimeBounds = linspace(0,24,100)';
if isempty(WStation.TimeStamp)
   WStation.TimeStamp        = TimeBounds;
   WStation.AbsoluteHumidity = TimeBounds.*nan;
   WStation.Pressure         = TimeBounds.*nan;
   WStation.RelativeHumidity = TimeBounds.*nan;
   WStation.Temperature      = TimeBounds.*nan;
end

%% Marking time gaps


Laser    = PaddingDataStructureTimeSeries(Laser,5);
Etalon   = PaddingDataStructureTimeSeries(Etalon,5);
WStation = PaddingDataStructureTimeSeries(WStation,5);
% Power    = PaddingDataStructureTimeSeries(Power,5);
MCS      = PaddingDataStructureMCS(MCS,5,7043);


%% Changing back to the coding directory
cd(Paths.Code)
end

function [Counts,PulseInfo] = RawNetCDFDataParse(Etalon,Laser,MCS,Power,WStation,HardwareMap)
%
%
%
%
%
%
%%
for m=1:1:size(HardwareMap.ChannelName,1)
    % Parsing out lidar data meta-data
    PulseInfo.Data.ProfilesPerHistogram{m,1}= MCS.ProfilesPerHistogram(MCS.Channel == HardwareMap.PhotonCounting(m));
    PulseInfo.Data.RangeResolution{m,1}     = MCS.RangeResolution(MCS.Channel == HardwareMap.PhotonCounting(m));
    % Parsing out the etalon
    PulseInfo.Etalon.TemperatureActual{m,1}  = Etalon.TemperatureActual(Etalon.Type == HardwareMap.Etalon(m) | isnan(Etalon.Type));
    PulseInfo.Etalon.TemperatureDesired{m,1} = Etalon.TemperatureDesired(Etalon.Type == HardwareMap.Etalon(m) | isnan(Etalon.Type));
    PulseInfo.Etalon.TimeStamp{m,1}          = Etalon.TimeStamp(Etalon.Type == HardwareMap.Etalon(m) | isnan(Etalon.Type));
    % Parsing out the laser
    PulseInfo.Laser.Current{m,1}            = Laser.Current(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
    PulseInfo.Laser.Locked{m,1}             = Laser.Locked(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
%     PulseInfo.Laser.Power{m,1}              = Power.LaserPower(:,HardwareMap.Power(m)+1);
    PulseInfo.Laser.TemperatureActual{m,1}  = Laser.TemperatureActual(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
    PulseInfo.Laser.TemperatureDesired{m,1} = Laser.TemperatureDesired(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
    PulseInfo.Laser.WavelengthActual{m,1}   = Laser.WavelengthActual(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
    PulseInfo.Laser.WavelengthDesired{m,1}  = Laser.WavelengthDesired(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
    % Parsing out the lidar data
    Counts.Raw{m,1}                         = MCS.Data(MCS.Channel == HardwareMap.PhotonCounting(m),:);
    % Time stamps
    PulseInfo.TimeStamp.Etalon{m,1}         = Etalon.TimeStamp(Etalon.Type == HardwareMap.Etalon(m) | isnan(Etalon.Type));
    PulseInfo.TimeStamp.LidarData{m,1}      = MCS.TimeStamp(MCS.Channel == HardwareMap.PhotonCounting(m));
    PulseInfo.TimeStamp.LaserLocking{m,1}   = Laser.TimeStamp(Laser.Type == HardwareMap.Laser(m) | isnan(Laser.Type));
%     PulseInfo.TimeStamp.LaserPower{m,1}     = Power.TimeStamp;
    PulseInfo.TimeStamp.WeatherStation      = WStation.TimeStamp;
    % Parsing out the weather station
    PulseInfo.WeatherStation.AbsHumidity    = WStation.AbsoluteHumidity;
    PulseInfo.WeatherStation.Pressure       = WStation.Pressure;
    PulseInfo.WeatherStation.RelHumidity    = WStation.RelativeHumidity;
    PulseInfo.WeatherStation.Temperature    = WStation.Temperature;
end
end

function [PulseInfoOld,PulseInfo] = RawNetCDFData2RegularGrid(PulseInfo)
%
%
%
%
%%
PulseInfoOld = PulseInfo;
% % % % PulseInfo.TimeStamp.Merged = PulseInfo.TimeStamp.LidarData{1,1};
PulseInfo.TimeStamp.Merged = double(PulseInfo.TimeStamp.LidarData{1,1});
% Pushing weather station data to MCS time grid
PulseInfo = RecursivelyInterpolateStructure(PulseInfo,PulseInfo.TimeStamp.WeatherStation,PulseInfo.TimeStamp.Merged,'linear','extrap');
% Pushing power data to MCS time grid
% % % % PulseInfo = RecursivelyInterpolateStructure(PulseInfo,PulseInfo.TimeStamp.LaserPower{1,1},PulseInfo.TimeStamp.Merged,'linear','extrap');
% Pushing laser locking data to MCS time grid by looping over lasers...need
% to loop because native grids are all unique until this step
for m=1:1:size(PulseInfo.TimeStamp.LaserLocking)
    if size(PulseInfo.TimeStamp.LaserLocking{m,1},1) ~= size(PulseInfo.TimeStamp.Merged,1)
        PulseInfo = RecursivelyInterpolateStructure(PulseInfo,PulseInfo.TimeStamp.LaserLocking{m,1},PulseInfo.TimeStamp.Merged,'linear','extrap');
    end
end
% Pushing laser locking data to MCS time grid by looping over etalons
for m=1:1:size(PulseInfo.TimeStamp.Etalon)
    if size(PulseInfo.TimeStamp.Etalon{m,1},1) ~= size(PulseInfo.TimeStamp.Merged,1)
        PulseInfo = RecursivelyInterpolateStructure(PulseInfo,PulseInfo.TimeStamp.Etalon{m,1},PulseInfo.TimeStamp.Merged,'linear','extrap');
    end
end
end

% This is a general function used to identify missing data times when the
% data are not sent in serial. It inserts nan values into the time series
% which can not be interpolated thus marking all data gaps
function [DataPadded] = PaddingDataStructureTimeSeries(Data,MedianWidths2Flag)
%
%
%
%
%
%
%% Constants
TimeStepToAdd = 1e-9;
%% Defining function handles (distance in medians from the median)
FindOutliers = @(DiffTimes) (DiffTimes - median(DiffTimes))./median(DiffTimes);
%% Finding the points where the time stamps are more than 5 median widths away from the median
A = find(FindOutliers(diff([0;Data.TimeStamp;24])) >= MedianWidths2Flag);
%% Converting the names structure to a cell array
CellArray  = struct2cell(Data);
FieldNames = fieldnames(Data);
%% Looping over cell elements and filling them (if necessary)
if isempty(A)
    NewCell = CellArray;
else
    % Pre-allocating new data structure
    NewCell    = cell(size(CellArray));
    % Looping over cells to fill them with empty data
    for m=1:1:size(CellArray,1)
        % Initializing the new data array
        NewCell{m,1} = [];
        % Initializing the array location
        StartIndexOld = 1;
        EndOfDayBreak = 0;
        % Looping over all data gaps
        for n=1:1:size(A,1)
            EndIndexOld = A(n)-1;
            %%%%%%%% Checking if time stamps or nans should be added %%%%%%%%
            if strcmp(FieldNames{m,1},'TimeStamp')
                ToAdd = TimeStepToAdd;
            else
                ToAdd = nan;
            end
            %%%%%%%% Inserting data into time gaps %%%%%%%%
            if A(n) == 1
                %%%%%%%% There is a break at the start of the day %%%%%%%%
                % Determining if there are multiple breaks in the day,
                % otherwise, just make the end index the last measurement
                if size(A,1)>1
                    EndIndexOld = A(n+1)-1;
                else
                    EndIndexOld = size(CellArray{m,1},1);
                end
                % Padding the new cell array
                NewCell{m,1} = [NewCell{m,1};
                                CellArray{m,1}(StartIndexOld,:)-ToAdd;
                                CellArray{m,1}(StartIndexOld:EndIndexOld,:)];
                StartIndexOld = EndIndexOld+1;
            elseif A(n) == size(CellArray{m,1},1) + 1
                %%%%%%%% There is a break at the end of the day %%%%%%%%
                NewCell{m,1} = [NewCell{m,1};
                                CellArray{m,1}(StartIndexOld:EndIndexOld,:);
                                CellArray{m,1}(EndIndexOld,:)+ToAdd];
                EndOfDayBreak = 1;
            else
                %%%%%%%% There is a break in the middle of the day %%%%%%%%
                % Insert meaningless time stamps in the middle of the day
                NewCell{m,1} = [NewCell{m,1};
                                CellArray{m,1}(StartIndexOld:EndIndexOld,:);
                                CellArray{m,1}(EndIndexOld,:)+ToAdd;
                                CellArray{m,1}(EndIndexOld+1,:)-ToAdd];
                StartIndexOld = EndIndexOld+1;
            end
            %%%%%%%% FIlling end of day if needed %%%%%%%%
            if n == size(A,1) && EndOfDayBreak == 0
                NewCell{m,1} = [NewCell{m,1};
                                CellArray{m,1}(StartIndexOld:end,:)];
            end
        end
    end
end
%% Converting back to a named structure
DataPadded = cell2struct(NewCell,FieldNames);
end

% This function looks at the time series of MCS data and attempts to find
% any sets of data that are incomplete. This can happen when the system is
% turned on or off in the middle of the transmission of a set of MCS
% data-grams or when the set is interupted by the start or end of a day
function [MCS] = RemoveIncompleteMCSScans(MCS)
%
%
%
%
%
%
%% Removing data to simulate bad scans
% for m=1:1:6
%     Index2Flip(m) = floor(rand.*size(GoodRows,1)); %#ok<SAGROW>
% end
% GoodRows(Index2Flip) = [];
%% Identifying bad data
% Checking for the unique channel identification numbers
A = unique(MCS.Channel);
A(isnan(A)) = [];
% Pre-allocating data
BadData = [];
% Looping over the 
for m=1:1:size(A,1)
    % Find all differences different than the scan size
    ThisChannel = find(MCS.Channel == A(m));
    Incomplete  = find(diff(ThisChannel) < size(A,1));
    if isempty(Incomplete) == 0
        BadData     = [BadData;ThisChannel(Incomplete)]; %#ok<AGROW>
    end
end
BadData = [BadData;find(isnan(MCS.Channel))];
%% Printing the number of removed data points to the command window
if isempty(BadData) == 0
   fprintf('%0.0f measurements were removed as incomplete scans.\n',size(BadData,1)) 
end
%% Converting the names structure to a cell array
CellArray  = struct2cell(MCS);
FieldNames = fieldnames(MCS);
%% Removing bad data
for m=1:1:size(CellArray)
    CellArray{m,1}(BadData,:) = [];
end
%% Converting back to a named structure
MCS = cell2struct(CellArray,FieldNames);
end

% This function specifically pads MCS data with bad values to remove any
% data breaks. This is different from the general function as it must
% handle 2d data and also must fill the channel type correctly otherwise
% the inserted data is not later understood
function [MCS] = PaddingDataStructureMCS(MCS,MedianWidths2Flag,LaserRepRate)
%
%
%
%
%
%% Defining function handles (distance in medians from the median)
FindOutliers = @(DiffTimes) (DiffTimes - median(DiffTimes))./median(DiffTimes);
%% Finding unique channel numbers
A = unique(MCS.Channel);
%% Finding the time stamps of the starts of the data transfers
ScanStarts = MCS.TimeStamp(1:size(A,1):end);
%% Finding the points where the time stamps are more than 5 median widths away from the median
B = find(FindOutliers(diff([0;ScanStarts;24])) >= MedianWidths2Flag);
DataBreakIndices = zeros(size(B,1),1);
for m=1:1:size(B,1)
    if B(m) <= size(ScanStarts,1) && B(m) ~= 1
        DataBreakIndices(m) = find(MCS.TimeStamp == ScanStarts(B(m)),1,'first');
    elseif B(m) == 1
        DataBreakIndices(m) = 1;
    else
        % Missing the end of the day
        DataBreakIndices(m)  = size(MCS.TimeStamp,1)+1;
        MCS.TimeStamp(end+1) = 24;
    end
end
%% Estimating the width of the outlying times
DataWidth = zeros(size(DataBreakIndices));
for m=1:1:size(DataBreakIndices)
    if DataBreakIndices(m) == 1
        DataWidth(m) = round((MCS.TimeStamp(DataBreakIndices(m))).*3600 ./ ...
                             (MCS.ProfilesPerHistogram(DataBreakIndices(m))./LaserRepRate));
    else
        DataWidth(m) = round((MCS.TimeStamp(DataBreakIndices(m))-MCS.TimeStamp(DataBreakIndices(m)-1)).*3600 ./ ...
                             (MCS.ProfilesPerHistogram(DataBreakIndices(m)-1)./LaserRepRate));
    end
    
end

% Making sure to only include complete scans
DataWidth = round(DataWidth./size(A,1)).*size(A,1);
              
%% Converting the names structure to a cell array
CellArray  = struct2cell(MCS);
FieldNames = fieldnames(MCS);

%% Filling data arrays (if needed)
if isempty(B)
    NewCell = CellArray;
else
    % Pre-allocating data cell array
    NewCell = cell(size(CellArray));
    % Looping over cells to fill them with empty data
    for n=1:1:size(CellArray,1)
        %%%%%%%% Initializing data array %%%%%%%%
        NewCell{n,1} = [];
        % Initializing the array location
        StartIndex    = 1;
        EndOfDayBreak = 0;
        for m=1:1:size(B)
            EndIndex = DataBreakIndices(m) - 1;
            %%%%%%%% Determining what to put into the time gaps %%%%%%%%
            if strcmp(FieldNames{n,1},'TimeStamp')
                if EndIndex ~= 0
                    ToAdd = linspace(CellArray{n,1}(EndIndex), ...
                                     CellArray{n,1}(EndIndex+1), ...
                                     DataWidth(m).*size(A,1) + 2)';
                else
                    ToAdd = linspace(0, ...
                                     CellArray{n,1}(EndIndex+1), ...
                                     DataWidth(m).*size(A,1) + 2)';
                end
                ToAdd = ToAdd(2:end-1);
            elseif strcmp(FieldNames{n,1},'Channel')
                ToAdd = repmat(A,DataWidth(m),1);
            elseif strcmp(FieldNames{n,1},'Data')
                ToAdd = repmat(A.*nan,DataWidth(m),size(CellArray{n,1},2));
            else
                ToAdd = repmat(A.*nan,DataWidth(m),1);
            end
            %%%%%%%% Inserting data into time gaps %%%%%%%%
            if DataBreakIndices(m) == 1
                %%%%%%%% There is a break at the start of the day %%%%%%%%
                % Determining if there are multiple breaks in the day,
                % otherwise, just make the end index the last measurement
                if size(DataBreakIndices,1)>1
                    EndIndex = DataBreakIndices(n+1)-1;
                else
                    EndIndex = size(CellArray{n,1},1);
                end
                % Padding the new cell array
%                 NewCell{n,1} = [NewCell{n,1};
%                                 ToAdd;
%                                 CellArray{n,1}(StartIndex:EndIndex,:)];
%                 StartIndex = EndIndex+1;
                NewCell{n,1} = [NewCell{n,1};
                                ToAdd];
%                 StartIndex = EndIndex+1;
            elseif DataBreakIndices(m) == size(CellArray{n,1},1) -1
                %%%%%%%% There is a break at the end of the day %%%%%%%%
                NewCell{n,1} = [NewCell{n,1};
                                CellArray{n,1}(StartIndex:EndIndex,:);
                                ToAdd];
                EndOfDayBreak = 1;
            else
                %%%%%%%% There is a break in the middle of the day %%%%%%%%
                % Insert meaningless time stamps in the middle of the day
                NewCell{n,1} = [NewCell{n,1};
                                CellArray{n,1}(StartIndex:EndIndex,:);
                                ToAdd];
                StartIndex = EndIndex+1;
            end
            %%%%%%%% FIlling end of day if needed %%%%%%%%
            if m == size(B,1) && EndOfDayBreak == 0
                NewCell{n,1} = [NewCell{n,1};
                                CellArray{n,1}(StartIndex:end,:)];
            end
        end
    end
end
%% Converting back to a named structure
MCS = cell2struct(NewCell,FieldNames);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Sub-functions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

