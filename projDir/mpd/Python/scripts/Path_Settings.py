import os
import sys

"""
Paths
"""
# base path to the NCAR-LidarProcessing package
software_path = os.path.join (os.environ ['HOME'], 'projDir/dial/Python/NCAR-LidarProcessing/')

# path for saving data and figures
save_data_path = os.path.join (os.environ ['HOME'], 'projDir/dial/Python/Processed_Data/')
save_fig_path = os.path.join (os.environ ['HOME'], 'projDir/dial/Python/Processed_Data/Plots/')

# path to sonde data (if sondes are used)
sonde_path = '/scr/eldora1/HSRL_data/'

# path to calibration files
cal_path = software_path + 'calibrations/'

# path to saved calibration files
# UNADVISEABLE TO MAKE THIS THE SAME AS THE CALIBRATION FILE PATH
cal_save_path = '/h/eol/mhayman/Python/tmp_cals/'

if push_ftp:
	ftp_address = 'catalog.eol.ucar.edu'
	ftp_usr = 'anonymous'
	ftp_pw = 'mhayman@ucar.edu'
	ftp_dir = '/pub/incoming/catalog/operations'

# path to data
if LidarNumber == 0:
    basepath = '/scr/eldora1/wvdial_1_data/'
    cal_file = cal_path+'dlb_calvals_ncar0.json'
    LidarName = 'NCAR-WV-DIAL'
    if official_day_file:
	save_data_path = '/scr/eldora1/wvdial_1_processed_data/'
	save_fig_path = '/scr/eldora1/wvdial_1_processed_data/'
    process_HSRL = False  # no HSRL in NCAR 1
elif LidarNumber == 1:
    basepath = '/scr/eldora1/wvdial_2_data/'
    cal_file = cal_path+'dlb_calvals_msu.json'
    LidarName = 'MSU-WV-DIAL'
    if official_day_file:
	LidarName = 'NDIAL'  # name for LAFE
	save_data_path = '/scr/eldora1/wvdial_2_processed_data/'
	save_fig_path = '/scr/eldora1/wvdial_2_processed_data/'
else:
    print('LidarNumber == %d\n   value not recognized'%LidarNumber)

print('Save Data Path:\n ' + save_data_path)
print('Save Figure Path:\n ' + save_fig_path)

# field labels
FieldLabel_WV = 'FF'
ON_FileBase = 'Online_Raw_Data.dat'
OFF_FileBase = 'Offline_Raw_Data.dat'

FieldLabel_HSRL = 'NF'
MolFileBase = 'Online_Raw_Data.dat'
CombFileBase = 'Offline_Raw_Data.dat'

# ---------------------------------------------------------------------------------------------------------------------
# Add path to lidar Python modules to sys.path
# ---------------------------------------------------------------------------------------------------------------------
tmp_fileP_str = os.path.join (os.environ ['HOME'], software_path + '/libraries')
if tmp_fileP_str not in sys.path:
    sys.path.append (tmp_fileP_str)

# ---------------------------------------------------------------------------------------------------------------------
# Add path to Willem Marias' Python modules for denoising to sys.path
# ---------------------------------------------------------------------------------------------------------------------
tmp_fileP_str = os.path.join (os.environ ['HOME'], 'projDir/dial/Python/ptvv1_python/python')
if tmp_fileP_str not in sys.path:
    sys.path.append (tmp_fileP_str)
