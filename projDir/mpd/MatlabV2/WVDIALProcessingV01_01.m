% Written by: Scott Spuler
% Modified by: Robert Stillwell
% Modified for: National Center For Atmospheric Research
% Modification info: Downloaded: January 17, 2017
%                    
%% Setting up runtime environment
clear; close all; clc

%% Defining processing options
Options = DefineOptions;
Options.System   = 'DIAL03';
Options.Location = 'FL1';
Options.Node     = 'DIAL2';   % Keep for now because hacking jsonde files

%% Defining all file paths
% DatesDesired = {'180501';'180502';'180503';'180504';'180505';'180506';'180507'};
% DatesDesired = {'180415';'180416';'180417';'180418';'180419';'180420';
%                 '180421';'180422';'180423';'180424';'180425';'180426';
%                 '180427';'180428';'180429';'180430'};
% DatesDesired = {'180523';'180524';'180525';'180526';'180527';'180528';
%                 '180529';'180530';'180531'};
DatesDesired = {'180614'};

for m=1:1:size(DatesDesired,1)
    % Parsing the dates out for processing
    Date = DatesDesired{m,1};
    % Setting up the needed filepaths
    Paths.Code          = pwd; % get the current path
    Paths.Catalog       = '/pub/incoming/catalog/operations';
    Paths.Figures       = ['/scr/eldora1/wvdial_',Options.System(6),'_processed_data/Quicklook'];
    Paths.FigureType    = Options.System;
    Paths.RawNetCDFData = ['/scr/eldora1/wvdial_',Options.System(6),'_data/20',Date(1:2),'/20',Date];

    %%%%%%%%%%%%%%%%%%%%%%%%%%% Processing data %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Read date of file
    Paths.Date = Date;
    % Loading calibration information from JSonde file
    if strcmp(Options.Node,'DIAL1')==1
        fprintf('Current JSond info for DIAL 1 is out of date.\n')
    else
        read_dial2_calvals 
        JSondeData.MCS.accum = 14000;
        JSondeData.BlankRange = 450;
        DIALAnalysis_V01_01(JSondeData, Options, Paths)
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
end

