% Written by: Robert Stillwell
% Written for: National Center For Atmospheric Research
% Modification info: Created: January 17, 2018

function [Options] = DefineOptions
%
% Inputs: none
%
% Outputs: Options: Structure containing all of the user defined processing
%                   options
%
%%
Options.flag.save_quicklook = 1;  % save quicklook to local directory
Options.flag.save_data = 0;       % save files in matlab format
Options.flag.save_netCDF = 0;     % save files netCDF format
Options.flag.save_catalog = 1;    % upload quicklook (and data) to field catalog

Options.flag.mask_data = 1;       % mask applied to data based on error analysis threshold
Options.flag.gradient_filter = 1; % this is used to mask regions with 'high' backscatter gradients which tend to cause errors
Options.flag.pileup = 1;          % use pileup correction for detectors
Options.flag.WS = 1;              % use the surface weather station data to calcuate spectroscopy
Options.flag.decimate = 0;        % decimate all data to half the wv resoltuion
Options.flag.int = 0;             % interpolate nans in nanmoving_average
Options.flag.mark_gaps = 0;       % sets gaps in data to NaNs

Options.flag.plot_data = 1;       % need to have this one to save the figs
Options.flag.troubleshoot = 0;    % shows extra plots used for troubleshooting
Options.p_hour = 12;              % hour to show troubleshooting profiles

Options.ave_time.wv = 5.0;       % averaging time (in minutes) for the water vapor 
Options.ave_time.rb = 1.0;        % averaging time (in minutes) for the relative backscatter
Options.ave_time.gr = 1.0;        % gridding time (in minutes) for the output files

Options.Node     = 'DIAL1';       % DIAL #2 HSRL data on NF channel, WV on FF channel

Options.RBScale  = 1;             % Scale factor for the relative backscatter contour
Options.DeadTime = 37.25E-9;      % Detector dead time 
end