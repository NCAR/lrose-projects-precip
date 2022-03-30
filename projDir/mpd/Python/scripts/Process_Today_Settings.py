import matplotlib
matplotlib.use('Agg') # disable display to avoid crashing crontab

import LidarProfileFunctions as lp
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os

"""
USER INPUTS
"""
# LidarNumber definition is as follows:
#    0:  NCAR (NCAR0)
#    1:  MSU  (NCAR1)
LidarNumber = 1  

if datetime.datetime.today().hour > 4.0:
	process_day =datetime.datetime.today()
else:
	process_day =datetime.datetime.today()-datetime.timedelta(days=1)

#process_day = datetime.datetime(2017,8,29) # override for processing day

Years,Months,Days,Hours = lp.generate_WVDIAL_day_list(process_day.year,process_day.month,process_day.day,startHr=0,duration=24)

print("Processing " + process_day.strftime("%A %B %d, %Y"))

process_HSRL = True
process_WV = True

plotAsDays = False
getMLE_extinction = False
run_MLE = False
runKlett = False
wv_full = False  # use 2D T and P (True, increases processing time) or average profile (False)
use_denoise = True  # Run Marias' denoising routine (requires that his code is installed)
N_Denoise_Block = 1  # number of profiles in a block used for molecular denoising. Set to 1 except in special cases.
accelerate_denoise = True # accelerate denoising by shrinking the TV penalty search space.  For best accuracy set to False, but it will slow the processing down.

WV_Denoise = True  # Use horizontal (time) denoising on water vapor profiles

save_as_nc = True
save_figs = True
nctag = ''  # tag added to saved files
overwrite_nc = False  # overwrite netcdf data if it already exists
official_day_file = True  # save to offical path and according to standard filenaming
push_ftp = True  # push images to ftp site

run_geo_cal = False
lin_fit_lower = 140  # index where the geo calibration switches to a fit routine
lin_fit_upper = 330  # index where the geo calibration stops using data for the fit routine
assumed_LR_cal = 20  # assumed lidar ratio when running geo cal
z_upper = 5e3  # upper limit (in meters) on where aerosol extinction effects are included in the geo calibration

model_atm = True


use_diff_geo = False   # no diff geo correction after April when we switched to fiber field stop
use_geo = True

use_mask = True
SNRmask = 1.0  #SNR level used to decide what data points we keep in the final data product
countLim_WV = 15.0
countLim_HSRL = 0.1

MaxAlt = 12e3 #12e3
WV_Min_Alt = 350  # mask data below this altitude
wv_lim = [0, 20]  # climis for WV field
bs_lim = [1e-8,1e-4]  # climits for backscatter coefficient
plot_combined = True
WV_MaxAlt = 6e3  # maximum plotted WV altitude if plot_combined = False


plot_compare_denoise = False  # plot a comparison between directed and denoised estimates
plot_backscatter = True  # plot combined and molecular attenuated backscatter

KlettAlt = 14e3  # altitude where Klett inversion starts (if enabled)

# set bin sizes
tres_hsrl = 1.0*60.0  # HSRL bin time resolution in seconds (2 sec typical base)
tres_wv = 1.0*60.0    # WV-DIAL bin time resolution in seconds (2 sec typical base)
zres = 37.5  # bin range resolution in m (37.5 m typical base)

# parameters for WV Channels smoothing
tsmooth_wv = 1*60 # convolution kernal time (Halfwidth sigma) in seconds
zsmooth_wv = 1 #150  # convolution kernal range (Halfwidth sigma) in meters
tsmooth2_wv = 1*60  # time smoothing applied to retrieved WV data
zsmooth2_wv = np.sqrt(150**2+75**2)  # 75 # second range smoothing conducted on the actual WV retrieval

t_plot = [0,24]  # time limits on plot (in hours).  Setting to nans results in auto scale.

exec(open(os.path.abspath(__file__+'/../Path_Settings.py')).read())
exec(open(os.environ['HOME']+'/projDir/dial/Python/NCAR-LidarProcessing/processors/Processor_DiodeLaserLidar.py').read())

print('\nProcessing Completed successfully\n')
#plt.show()
