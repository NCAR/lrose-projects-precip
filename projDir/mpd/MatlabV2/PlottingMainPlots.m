


function PlottingMainPlots(Counts,RB_scale,PulseInfo,date,DataProducts,Options,Paths,Plotting,SurfaceWeather)
%
%
%
%
%
%
%
%% Plotting relative backscatter
figure1 = figure('visible', 'off','Position',[Plotting.ScreenSize(4)/1.5 Plotting.ScreenSize(4)/10 Plotting.ScreenSize(3)/1.5 Plotting.ScreenSize(4)/1.5]);
set(figure1, 'visible', 'off', 'PaperUnits', 'points', 'PaperPosition', [0 0 1280 800]);
if Options.flag.plot_data == 1
    set(figure1, 'visible', 'on');
end
subplot1=subplot(2,1,1,'Parent',figure1);
box(subplot1,'on');
set(gcf,'renderer','zbuffer');
Z = double(log10((real(Counts.RelativeBackscatter{1,1}')./RB_scale)));
h = pcolor(Plotting.x,Plotting.y,Z);
set(h, 'EdgeColor', 'none');
set(gca,'TickDir','out');
set(gca,'TickLength',[0.005; 0.0025]);
set(gca, 'XTick',  Plotting.xdata)
colorbar('EastOutside');
axis([fix(min(PulseInfo.DataTimeDateNumFormat)) fix(min(PulseInfo.DataTimeDateNumFormat))+1 0 12])
caxis([1 6]);
datetick('x','HH','keeplimits', 'keepticks');
colormap(Plotting.ColorMap)
%shading interp
hh = title({[date,'  Relative Backscatter (C/ns km^2)']},'fontweight','b','fontsize',Plotting.FontSize);
P_t = get(hh, 'Position');
set(hh,'Position', [P_t(1) P_t(2)+0.2 P_t(3)])
xlabel('Time (UTC)','fontweight','b','fontsize',Plotting.FontSize);
ylabel('Height (km, AGL)','fontweight','b','fontsize',Plotting.FontSize);
set(gca,'Fontsize',Plotting.FontSize,'Fontweight','b');

%% Plot water vapor in g/m^3
subplot1=subplot(2,1,2,'Parent',figure1);
box(subplot1,'on'); %(number density in mol/cm3)(1e6 cm3/m3)/(N_A mol/mole)*(18g/mole)
set(gcf,'renderer','zbuffer');
Z = double(real(DataProducts.N_avg'.*1e6./6.022E23.*18.015));
h = pcolor(Plotting.x,Plotting.y,Z);
set(h, 'EdgeColor', 'none');
set(gca, 'XTick',  Plotting.xdata)
set(gca,'TickDir','out');
set(gca,'TickLength',[0.005; 0.0025]);
colorbar('EastOutside');
axis([fix(min(PulseInfo.DataTimeDateNumFormat)) fix(min(PulseInfo.DataTimeDateNumFormat))+1 0 6])
caxis([0 6]);
datetick('x','HH','keeplimits', 'keepticks');
colormap(Plotting.ColorMap)
%shading interp
hh = title({[date,'  Water Vapor (g/m^{3})']},'fontweight','b','fontsize',Plotting.FontSize);
P_t = get(hh, 'Position');
set(hh,'Position', [P_t(1) P_t(2)+0.2 P_t(3)])
xlabel('Time (UTC)','fontweight','b','fontsize',Plotting.FontSize);
ylabel('Height (km, AGL)','fontweight','b','fontsize',Plotting.FontSize);
set(gca,'Fontsize',Plotting.FontSize,'Fontweight','b');

%% Saving the quickloook plot
if Options.flag.save_quicklook == 1
    fprintf('Making Quicklook and Uploading to Field Catalog\n')
    cd(Paths.Figures) % point to the directory where data is stored
    date=datestr(nanmean(PulseInfo.DataTimeDateNumFormat), 'yyyymmdd');
    % save the image as a PNG to the local data folder
    name=strcat('lidar.NCAR-WV-',Options.System,'_',Options.Location,'.20',Paths.Date, '0000.Backscatter_WV.png');
    print(figure1, name, '-dpng', '-r300') % set the resolution as 300 dpi
    if Options.flag.save_catalog == 1 % upload figure to the field catalog
        test=ftp('catalog.eol.ucar.edu', 'anonymous', 'spuler@ucar.edu');
        cd(test, Paths.Catalog);
        mput(test, name);
        cd(test);
        dir(test,'lidar*')
        close(test);
    end
    cd(Paths.Code)
end



%     % plot the online wavelength
%     figure20 = figure('Position', Plotting.PlotSize2);
%         plot(PulseInfo.DataTimeDateNumFormat, PulseInfo.Lambda{2,1});
%     datetick('x','HH','keeplimits');
%     title({[date,'  Online wavelength']},...
%         'fontweight','b','fontsize',20)
%     ylim([PulseInfo.LambdaMedian{2,1}-.001 PulseInfo.LambdaMedian{2,1}+.001])
%     
%     % plot the offline wavelength
%     figure21 = figure('Position', Plotting.PlotSize2);
%     plot(PulseInfo.DataTimeDateNumFormat, PulseInfo.Lambda{1,1});
%     datetick('x','HH','keeplimits');
%     title({[date,'  Offline wavelength']},...
%         'fontweight','b','fontsize',20)
%     ylim([PulseInfo.LambdaMedian{1,1}-.001 PulseInfo.LambdaMedian{1,1}+.001])
    
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Data2Save.WavelengthX   = PulseInfo.DataTimeDateNumFormat;
% Data2Save.WavelengthOn  = PulseInfo.Lambda{1,1};
% Data2Save.WavelengthOff = PulseInfo.Lambda{2,1};
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CurrentPath = pwd;
% MeasurementsTotal = size(Counts.Raw{1,1},1);
% cd(Paths.SaveData)
% ExtraSave = [Paths.FigureType,'NewDataProcessing20',num2str(Paths.FolderDate),'.mat'];
% save(ExtraSave,'Data2Save','MeasurementsTotal');
% cd(CurrentPath)
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

   
end

