/**********************************************************************
 * TDRP params for Iq2Dsr
 **********************************************************************/

//======================================================================
//
// Iq2Dsr reads raw time-series data, computes the moments and writes 
//   the contents into a DsRadar FMQ.
//
//======================================================================
 
//======================================================================
//
// DEBUGGING AND PROCESS CONTROL.
//
//======================================================================
 
///////////// debug ///////////////////////////////////
//
// Debug option.
// If set, debug messages will be printed appropriately.
//
// Type: enum
// Options:
//     DEBUG_OFF
//     DEBUG_NORM
//     DEBUG_VERBOSE
//     DEBUG_EXTRA_VERBOSE
//

debug = DEBUG_OFF;

///////////// instance ////////////////////////////////
//
// Process instance.
// Used for registration with procmap.
// Type: string
//

instance = "cp";

//======================================================================
//
// THREADING FOR SPEED.
//
//======================================================================
 
///////////// use_multiple_threads ////////////////////
//
// Option to use multiple threads to improve performance.
// The read, compute and write stages can overlap in time, to improve 
//   performance. Also, the compute stage can be split into multiple 
//   threads, with each thread working on a discrete number of gates.
// Type: boolean
//

use_multiple_threads = TRUE;

///////////// n_compute_threads ///////////////////////
//
// The number of compute threads.
// The moments computations are segmented in range, with each thread 
//   computing a fraction of the number of gates. For maximum performance, 
//   n_threads should be set to the number of processors multiplied by 4. 
//   For further tuning, use top to maximize CPU usage while varying the 
//   number of threads.
// Minimum val: 1
// Type: int
//

n_compute_threads = 4;

//======================================================================
//
// TIME-SERIES DATA INPUT.
//
//======================================================================
 
///////////// mode ////////////////////////////////////
//
// Operating mode.
// In REALTIME mode, the program waits for a new input file. In ARCHIVE 
//   mode, it moves through the list of file names specified on the 
//   command line. In SIMULATE mode, the program moves repeatedly through 
//   the file list, creating output files with times set to now. This is 
//   useful for simulating an operational radar. In FMQ mode, the program 
//   opens the input_fmq, and reads time series data from the queue.
//
// Type: enum
// Options:
//     ARCHIVE
//     REALTIME
//     SIMULATE
//     FMQ
//

mode = FMQ;

///////////// input_fmq ///////////////////////////////
//
// FMQ name for time series data.
// This is used in FMQ mode only.
// Type: string
//

input_fmq = "$(DATA_DIR)/fmq/ts/sband/shmem_10000";

///////////// position_fmq_at_start ///////////////////
//
// Option to position the input FMQ at the start of the queue.
// FMQ mode only. If false, we start reading at the end of the queue. 
//   This is the default behavior. If true, we position the read pointer 
//   at the start of the queue, and read all data available in the queue 
//   before starting to read new data.
// Type: boolean
//

position_fmq_at_start = FALSE;

///////////// input_dir ///////////////////////////////
//
// Dir for input data files.
// This is used in REALTIME mode only. In ARCHIVE and SIMULATE modes, 
//   the file paths are specified on the command line.
// Type: string
//

input_dir = "./input";

///////////// use_ldata_info_file /////////////////////
//
// Option to use _latest_data_info file as input trigger.
// REALTIME mode only. If true, waits on _latest_data_info file. If 
//   false, scans the directory for new file.
// Type: boolean
//

use_ldata_info_file = FALSE;

///////////// max_realtime_valid_age //////////////////
//
// Max valid age of rdata input files in realtime mode (secs).
// This the max valid age for an incoming file. The program will wait 
//   for a data file more recent than this age.
// Minimum val: 1
// Type: int
//

max_realtime_valid_age = 360;

///////////// invert_hv_flag //////////////////////////
//
// Option to invert the sense of the HV flag in alternating mode.
// In alternating dual-pol mode, the HV flag indicates whether the pulse 
//   is horizontally or vertically polarized. Normally 1 indicates H and 0 
//   V. This parameter allows you to invert the sense of the flag, so that 
//   1 is interpreted as V and 0 as H.
// Type: boolean
//

invert_hv_flag = FALSE;

///////////// prt_is_for_previous_interval ////////////
//
// Does the PRT in the pulse header refer to the previous time 
//   interval?.
// If TRUE, the PRT in the pulse header refers to the time from the 
//   PREVIOUS pulse to THIS pulse. If FALSE, the PRT in the header refers 
//   to the time from THIS pulse to the NEXT pulse.
// Type: boolean
//

prt_is_for_previous_interval = TRUE;

//======================================================================
//
// INTERPOLATION OF ANTENNA ANGLES.
//
//======================================================================
 
///////////// interpolate_antenna_angles //////////////
//
// Option to interpolate antenna angles to make sure they vary smoothly.
// Some systems send angles which jump from one value to another and 
//   then remain constant for a number of pulses. This option allows you 
//   to interpolate these angles so that they vary smoothly from pulse to 
//   pulse. In RHI mode the elevation angles are smoothed. In other modes 
//   the azimuth angles are smoothed.
// Type: boolean
//

interpolate_antenna_angles = FALSE;

///////////// angle_interp_max_change /////////////////
//
// Maximum change in angle for interpolation (deg).
// See interpolate_antenna_angles. This is the maximum permissable 
//   change in angle for interpolation to be performed. If the difference 
//   in angle between 2 pulses exceeds this value, interpolation is not 
//   performed.
// Type: double
//

angle_interp_max_change = 2.5;

///////////// angle_interp_max_queue_size /////////////
//
// Maximum queue size for interpolating angles.
// If more than this number of pulses have constant angles, 
//   interpolation will not be done.
// Type: int
//

angle_interp_max_queue_size = 200;

///////////// angle_interp_adjust_for_latency /////////
//
// Option to adjust antenna angles for latency in the processing.
// In some systems, the angles are tagged to the IQ pulses late, so that 
//   they lag the real angles. Set this to TRUE to adjust for the latency 
//   by adjusting the angles for latency multiplied by the angular rate.
// Type: boolean
//

angle_interp_adjust_for_latency = FALSE;

///////////// angle_interp_latency ////////////////////
//
// Latency of antenna angles (secs).
// See 'adjust_angles_for_latency'.
// Type: double
//

angle_interp_latency = 0.1;

///////////// nsecs_for_antenna_rate //////////////////
//
// Time for computing antenna rate (sec).
// The rate computed over this time period. The rate is used to adjust 
//   for latency in the angles.
// Type: double
//

nsecs_for_antenna_rate = 0.2;

///////////// angle_interp_debug //////////////////////
//
// Option to turn on debugging for antenna angle interpolation.
// If TRUE, interpolation diagnostics will be printed.
// Type: boolean
//

angle_interp_debug = FALSE;

//======================================================================
//
// RADAR PARAMETERS.
//
// Some radar parameters may be included in the time series data. This 
//   section allows you to optionally override some of those values.
//
//======================================================================
 
///////////// override_radar_name /////////////////////
//
// Option to override the radar name.
// If true, the name in this file will be used. If not, the name in the 
//   time series data will be used.
// Type: boolean
//

override_radar_name = FALSE;

///////////// radar_name //////////////////////////////
//
// Name of the radar.
// See 'override_radar_name'.
// Type: string
//

radar_name = "SPOL";

///////////// override_radar_location /////////////////
//
// Option to override the radar location.
// If true, the location in this file will be used. If not, the location 
//   in the time series data will be used.
// Type: boolean
//

override_radar_location = TRUE;

///////////// radar_latitude_deg //////////////////////
//
// Radar latitude (deg).
// See override_radar_location.
// Type: double
//

radar_latitude_deg = $(RADAR_LAT);

///////////// radar_longitude_deg /////////////////////
//
// Radar longitude (deg).
// See override_radar_location.
// Type: double
//

radar_longitude_deg = $(RADAR_LON);

///////////// radar_altitude_meters ///////////////////
//
// Radar altitude (meters).
// See override_radar_location.
// Type: double
//

radar_altitude_meters = $(RADAR_ALT_M);

///////////// override_gate_geometry //////////////////
//
// Option to override the gate geometry.
// If true, the gate_spacing and start_range in the time series data is 
//   overridden by the parameters in this file.
// Type: boolean
//

override_gate_geometry = FALSE;

///////////// gate_spacing_meters /////////////////////
//
// Gate spacing (meters).
// See override_gate_geometry.
// Type: double
//

gate_spacing_meters = 150;

///////////// start_range_meters //////////////////////
//
// Start range (meters).
// See override_gate_geometry.
// Type: double
//

start_range_meters = 150;

///////////// override_radar_wavelength ///////////////
//
// Option to override the radar wavelength.
// If true, the radar wavelength in this file will be used. If not, the 
//   wavelength in the time series data will be used if available.
// Type: boolean
//

override_radar_wavelength = FALSE;

///////////// radar_wavelength_cm /////////////////////
//
// Radar wavelength (cm).
// See override_radar_wavelength.
// Type: double
//

radar_wavelength_cm = 10;

///////////// scan_type_id ////////////////////////////
//
// Scan type id.
// Unique identifier for scan strategy.
// Type: int
//

scan_type_id = 0;

///////////// scan_type_name //////////////////////////
//
// Scan type name.
// Descriptive name for scan strategy.
// Type: string
//

scan_type_name = "Default";

///////////// atmos_attenuation ///////////////////////
//
// Atmospheric attenuation (dB/km).
// Reflectivity is corrected for this.
// Type: double
//

atmos_attenuation = 0.012;

//======================================================================
//
// RADAR CALIBRATION.
//
//======================================================================
 
///////////// startup_cal_file ////////////////////////
//
// File name for calibration to be read at startup. Required.
// The startup calibration file is required. The startup cal will be 
//   overridden if set_cal_by_pulse_width is true, or if 
//   use_cal_from_time_series is true.
// Type: string
//

startup_cal_file = "$(PROJ_DIR)/mgen/params/sband_cal.xml";

///////////// set_cal_by_pulse_width //////////////////
//
// Option to read different cal file depending on the pulse width in the 
//   data.
// The calibration changes with pulse width. Therefore, if the radar 
//   supports variable pulse widths, you need to specify the location of 
//   the calibration files for each pulse width.
// Type: boolean
//

set_cal_by_pulse_width = FALSE;

///////////// pulse_width_cals ////////////////////////
//
// Specify the directories in which the calibration files for each pulse 
//   width will be stored.
// See 'set_cal_by_pulse_width'. First, the app will determine which of 
//   the specified pulse widths best matches the pulse width in the data. 
//   The closest available pulse width will be used. The corresponding 
//   directory will then be searched. The cal file in that directory which 
//   is closest in time to the beam time will be used.

// NOTE - the pulse width is specified in micro-seconds.
//
// Type: struct
//   typedef struct {
//      double pulse_width_us;
//      string cal_dir;
//   }
//
// 1D array - variable length.
//

pulse_width_cals = {
  { 0.5, "/tmp/cal_pw_0.5"},
  { 1, "/tmp/cal_pw_1.0"},
  { 2, "/tmp/cal_pw_2.0"}
};

///////////// cal_recheck_period //////////////////////
//
// Frequency at which to check for new cal (secs).
// The program will scan the calibration directory structure once every 
//   period, to check for new calibration files.
// Type: int
//

cal_recheck_period = 600;

///////////// use_cal_from_time_series ////////////////
//
// Option to use cal information from time series data.
// If true, the cal information in the time series data will be used, if 
//   available. If false, the cal info in the param file will be used.
// Type: boolean
//

use_cal_from_time_series = FALSE;

//======================================================================
//
// MOMENTS COMPUTATIONS.
//
//======================================================================
 
///////////// moments_params //////////////////////////
//
// Moments algorithm parameters.
// Sets the moments algorithm parameters by searching through the list 
//   of available options.

// SEARCHING THE LIST: we check 4 possible conditions: (a) 
//   xmit_rcv_mode, (b) scan_mode, (c) prf (pulses per second) and (d) 
//   antenna rate in degrees/sec.

// To ensure that the data will always be processed, include as the last 
//   option a default entry in which none of the checks are performed.

// PROCESSING OPTIONS:
// (a) beam_n_samples: number of hits.
// (b) index_the_beams: compute beams indexed on evenly-spaced angles.
// (c) index_resolution: angular resolution of the indexed beams.
// (d) min_antenna_rate_for_indexing (deg/sec): if the antenna rate is 
//   less than this value, non-indexed beams will be used.
// (e) window: window to be applied to time series. Note that if the 
//   VONHANN or BLACKMAN windows are used, beam_n_samples is automatically 
//   adjusted to account for the fact that the window concentrates the 
//   power in the central part of the time series. The adjustment corrects 
//   beam_n_samples by computing the fraction of the window in which 90% 
//   of the power occurs. For the VONHANN window this factor is just below 
//   2.0, and for the BLACKMAN window it is just above 2.0. For SZ, no 
//   window should be set becasue SZ has its own window setting.
// (f) switching_receiver: set to true if the receiver swicthes on a 
//   pulse-by-pulse basis so that co-polar returns are always on the same 
//   channel.
// (g) xmit_rcv_mode:  mode for xmit and receive for polarization 
//   diversity
// (h) apply_clutter_filter: should we apply clutter filtering?
// (i) apply_sz: should we apply SZ decoding?

// xmit_rcv_mode options:
//  SP: Single polarization
//  DP_ALT_HV_CO_ONLY: Dual pol, alternating transmission, copolar 
//   receiver only (e.g. CP2 S-band)
//  DP_ALT_HV_CO_CROSS: Dual pol, alternating transmission, co-polar and 
//   cross-polar receivers (e.g. SPOL with Mitch Switch and receiver in 
//   switching mode, CHILL)
//  DP_ALT_HV_FIXED_HV: Dual pol, alternating transmission, fixed H and 
//   V receivers (e.g. SPOL with Mitch Switch and receivers in fixed mode)
//  DP_SIM_HV_FIXED_HV: Dual pol, simultaneous transmission, fixed H and 
//   V receivers (e.g. NEXRAD upgrade, SPOL with T and receivers in fixed 
//   mode)
//  DP_SIM_HV_SWITCHED_HV: Dual pol, simultaneous transmission, 
//   switching H and V receivers (e.g. SPOL with T and receivers in 
//   switching mode)
//  DP_H_ONLY_FIXED_HV: Dual pol, H transmission, fixed H and V 
//   receivers (e.g. CP2 X band)
//  DP_V_ONLY_FIXED_HV: Dual pol, V transmission, fixed H and V 
//   receivers

// change_vel_sign: Option to change the sign of the velocity field. For 
//   some radars, the signal processing is set up in such a way that the 
//   velocity sign is incorrect. Set this flag to TRUE to change the sign.

// proc_flags: special processing options, not active yet.
//
// Type: struct
//   typedef struct {
//      boolean check_scan_mode;
//      scan_mode_t scan_mode;
//        Options:
//          SCAN_MODE_UNKNOWN
//          SCAN_MODE_SECTOR
//          SCAN_MODE_COPLANE
//          SCAN_MODE_RHI
//          SCAN_MODE_VERTICAL_POINTING
//          SCAN_MODE_IDLE
//          SCAN_MODE_SURVEILLANCE
//          SCAN_MODE_SUNSCAN
//          SCAN_MODE_POINTING
//          SCAN_MODE_MANUAL_PPI
//          SCAN_MODE_MANUAL_RHI
//      boolean check_prf;
//      double prf_lower_limit;
//      double prf_upper_limit;
//      boolean check_antenna_rate;
//      double antenna_rate_lower_limit;
//      double antenna_rate_upper_limit;
//      beam_method_t beam_method;
//        Options:
//          BEAM_SPECIFY_N_SAMPLES
//          BEAM_SPECIFY_ANGLE
//      int beam_n_samples;
//      double beam_angle_deg;
//      boolean index_the_beams;
//      double indexed_resolution;
//      double min_antenna_rate_for_indexing;
//      window_t window;
//        Options:
//          WINDOW_RECT
//          WINDOW_VONHANN
//          WINDOW_BLACKMAN
//      boolean switching_receiver;
//      xmit_rcv_mode_t xmit_rcv_mode;
//        Options:
//          SINGLE_POL
//          DP_ALT_HV_CO_ONLY
//          DP_ALT_HV_CO_CROSS
//          DP_ALT_HV_FIXED_HV
//          DP_SIM_HV_FIXED_HV
//          DP_SIM_HV_SWITCHED_HV
//          DP_H_ONLY_FIXED_HV
//          DP_V_ONLY_FIXED_HV
//      boolean apply_clutter_filter;
//      boolean apply_sz;
//      boolean change_velocity_sign;
//      processing_flags_t proc_flags;
//        Options:
//          PROC_FLAGS_NONE
//   }
//
// 1D array - variable length.
//

moments_params = {
  {
    check_scan_mode = TRUE,
    scan_mode = SCAN_MODE_SURVEILLANCE,
    check_prf = FALSE,
    prf_lower_limit = 0,
    prf_upper_limit = 2000,
    check_antenna_rate = FALSE,
    antenna_rate_lower_limit = 0,
    antenna_rate_upper_limit = 90,
    beam_method = BEAM_SPECIFY_ANGLE,
    beam_n_samples = 192,
    beam_angle_deg = 1,
    index_the_beams = TRUE,
    indexed_resolution = 1,
    min_antenna_rate_for_indexing = 1,
    window = WINDOW_VONHANN,
    switching_receiver = TRUE,
    xmit_rcv_mode = DP_ALT_HV_CO_CROSS,
    apply_clutter_filter = TRUE,
    apply_sz = FALSE,
    change_velocity_sign = FALSE,
    proc_flags = PROC_FLAGS_NONE
  }
  ,
  {
    check_scan_mode = TRUE,
    scan_mode = SCAN_MODE_SECTOR,
    check_prf = FALSE,
    prf_lower_limit = 0,
    prf_upper_limit = 2000,
    check_antenna_rate = FALSE,
    antenna_rate_lower_limit = 0,
    antenna_rate_upper_limit = 90,
    beam_method = BEAM_SPECIFY_ANGLE,
    beam_n_samples = 192,
    beam_angle_deg = 1.0,
    index_the_beams = TRUE,
    indexed_resolution = 1.0,
    min_antenna_rate_for_indexing = 1,
    window = WINDOW_VONHANN,
    switching_receiver = TRUE,
    xmit_rcv_mode = DP_ALT_HV_CO_CROSS,
    apply_clutter_filter = TRUE,
    apply_sz = FALSE,
    change_velocity_sign = FALSE,
    proc_flags = PROC_FLAGS_NONE
  }
  ,
  {
    check_scan_mode = TRUE,
    scan_mode = SCAN_MODE_RHI,
    check_prf = FALSE,
    prf_lower_limit = 0,
    prf_upper_limit = 2000,
    check_antenna_rate = FALSE,
    antenna_rate_lower_limit = 0,
    antenna_rate_upper_limit = 90,
    beam_method = BEAM_SPECIFY_ANGLE,
    beam_n_samples = 192,
    beam_angle_deg = 1.0,
    index_the_beams = TRUE,
    indexed_resolution = 0.5,
    min_antenna_rate_for_indexing = -1,
    window = WINDOW_VONHANN,
    switching_receiver = TRUE,
    xmit_rcv_mode = DP_ALT_HV_CO_CROSS,
    apply_clutter_filter = TRUE,
    apply_sz = FALSE,
    change_velocity_sign = FALSE,
    proc_flags = PROC_FLAGS_NONE
  }
  ,
  {
    check_scan_mode = FALSE,
    scan_mode = SCAN_MODE_SURVEILLANCE,
    check_prf = FALSE,
    prf_lower_limit = 0,
    prf_upper_limit = 2000,
    check_antenna_rate = FALSE,
    antenna_rate_lower_limit = 0,
    antenna_rate_upper_limit = 90,
    beam_method = BEAM_SPECIFY_N_SAMPLES,
    beam_n_samples = 192,
    beam_angle_deg = 1,
    index_the_beams = TRUE,
    indexed_resolution = 1,
    min_antenna_rate_for_indexing = 1,
    window = WINDOW_VONHANN,
    switching_receiver = TRUE,
    xmit_rcv_mode = DP_ALT_HV_CO_CROSS,
    apply_clutter_filter = TRUE,
    apply_sz = FALSE,
    change_velocity_sign = FALSE,
    proc_flags = PROC_FLAGS_NONE
  }
};

///////////// min_n_samples ///////////////////////////
//
// Min number of samples when computing nsamples in beam_method = 
//   BEAM_SPECIFY_ANGLE.
// When beam_method is BEAM_SPECIFY_ANGLE, the number of samples is 
//   computed from the antenna rate and the requested dwell. However, if 
//   the antenna moves too fast, the computed n_samples can become small. 
//   This parameter is the lower limits to n_samples.
// Type: int
//

min_n_samples = 32;

///////////// max_n_samples ///////////////////////////
//
// Max number of samples when computing nsamples in beam_method = 
//   BEAM_SPECIFY_ANGLE.
// When beam_method is BEAM_SPECIFY_ANGLE, the number of samples is 
//   computed from the antenna rate and the requested dwell. However, when 
//   the antenna slows down (say in sector scan) the computed n_samples 
//   can become large. This parameter is the upper limits to n_samples.
// Type: int
//

max_n_samples = 256;

///////////// control_n_samples_from_time_series //////
//
// Option to control n_samples by using the integration_cycle_pulses 
//   value in the time series.
// If true, the number of samples will be determined by using the value 
//   of integration_cycle_pulses in the time series. If false, the 
//   beam_n_samples specified in moments_params will be used.
// Type: boolean
//

control_n_samples_from_time_series = FALSE;

///////////// control_beam_indexing_from_time_series //
//
// Option to control the beam indexing by using information in the time 
//   series.
// If true, the beam indexing will be controlled from the time series. 
//   In this case the beams_are_indexed flag in the iwrf_ts_processing 
//   packet will control the indexing decision, along with 
//   specify_dwell_width, indexed_beam_width_deg and 
//   indexed_beam_spacing_deg. If this parameter is false, the following 
//   will be used from moments_params: index_the_beams, beam_method, 
//   beam_angle_deg and indexed_resolition.
// Type: boolean
//

control_beam_indexing_from_time_series = FALSE;

///////////// control_xmit_rcv_mode_from_time_series //
//
// Option to control the xmit/rcv mode by using the xmit_rcv_mode value 
//   in the time series.
// If true, the moments will be computed according to the xmit_rcv_mode 
//   value in the time series. If false, the xmit_rcv_mode in the 
//   moments_params will be used.
// Type: boolean
//

control_xmit_rcv_mode_from_time_series = FALSE;

///////////// adjust_dbz_for_measured_xmit_power //////
//
// Option to adjust DBZ based on measured transmitter power.
// If true, and the measured transmitter power is available, the 
//   difference between the measured power and calibration power will be 
//   used to adjust the computed DBZ fields.
// Type: boolean
//

adjust_dbz_for_measured_xmit_power = FALSE;

///////////// adjust_zdr_for_measured_xmit_power //////
//
// Option to adjust ZDR based on measured transmitter power.
// If true, and the measured transmitter power is available, the 
//   difference between the measured power and calibration power will be 
//   used to adjust the computed ZDR fields.
// Type: boolean
//

adjust_zdr_for_measured_xmit_power = FALSE;

///////////// check_for_missing_pulses ////////////////
//
// Option to check for missing pulses in the time series.
// If missing pulses are found, the beam formed by those pulses will be 
//   discarded.
// Type: boolean
//

check_for_missing_pulses = TRUE;

///////////// correct_for_system_phidp ////////////////
//
// Option to correct for system phidp.
// If true, the H and V correlation phases will be corrected by 
//   adding/subtracting the system phidp value as appropriate. This avoids 
//   premature wrapping of the phased from which phidp and velocity are 
//   computed. If false, this correction will not be applied. To find the 
//   system phidp, set this to false and compute phidp for 
//   vertically-pointing data.
// Type: boolean
//

correct_for_system_phidp = TRUE;

///////////// zdr_median_filter_len ///////////////////
//
// Length of median filter applied to ZDR field in range (gates).
// Set to 1 if you do not want a median filter applied.
// Type: int
//

zdr_median_filter_len = 1;

///////////// rhohv_median_filter_len /////////////////
//
// Length of median filter applied to RHOHV field in range (gates).
// Set to 1 if you do not want a median filter applied.
// Type: int
//

rhohv_median_filter_len = 1;

///////////// staggered_prt_median_filter_len /////////
//
// Length of median filter applied to unfolding interval for staggered 
//   PRT.
// If less than 3, no filtering will be performed.
// Type: int
//

staggered_prt_median_filter_len = 1;

//======================================================================
//
// CLUTTER FILTERING.
//
// The default clutter filtering method is the Adaptive Filter, with 
//   residue correction activated.
//
//======================================================================
 
///////////// apply_residue_correction_in_adaptive_filter 
//
// Option to apply residue correction to adaptive filter.
// At some gates, the spectral noise floor may be high. If this 
//   correction is applied, the spectral noise floor will be reduced to 
//   the measured noise value.
// Type: boolean
//

apply_residue_correction_in_adaptive_filter = TRUE;

///////////// min_snr_db_for_residue_correction ///////
//
// Min SNR for applying the residue correction (dB).
// Spectral residue seems to occur at high powers, when the receiver is 
//   close to saturated. This is probably related to increased phase 
//   noise. Only apply residue correction if SNR exceeds this value. 
//   Otherwise, do not apply a correction.
// Type: double
//

min_snr_db_for_residue_correction = 75;

///////////// use_polynomial_regression_clutter_filter 
//
// Option to apply a regression clutter filter.
// For the regression filter, a polynomial fit is performed on the I and 
//   Q data individually. The filtered time series is computed as the 
//   original minus the regression fit. If true, this takes preference 
//   over the notch filter.
// Type: boolean
//

use_polynomial_regression_clutter_filter = FALSE;

///////////// regression_filter_polynomial_order //////
//
// Order of the polynomial fit for the regression filter.
// Type: int
//

regression_filter_polynomial_order = 5;

///////////// regression_filter_interp_across_notch ///
//
// For the regression filter, option to interpolate power across the 
//   notch.
// If true, the spectral power in the notch created by the filter will 
//   be interpolated using values to each side of the notch.
// Type: boolean
//

regression_filter_interp_across_notch = TRUE;

///////////// use_simple_notch_clutter_filter /////////
//
// Option to use a simple notch for clutter filtering.
// If false, spectral adaptive clutter filtering is used. If true, a 
//   simple notch is used instead. The width is specified in 
//   notch_filter_width_mps. The depth of the notch is down to the 
//   calibrated noise floor.
// Type: boolean
//

use_simple_notch_clutter_filter = FALSE;

///////////// simple_notch_filter_width_mps ///////////
//
// Width of simple clutter notch (m/s).
// See use_simple_notch_clutter_filter.
// Type: double
//

simple_notch_filter_width_mps = 3;

///////////// use_h_only_for_alt_mode_clutter_vel /////
//
// Option to use H only pulses for computing clutter velocity in 
//   alternation dual pol mode.
// If false, the normal phidp-based method is used everywhere in 
//   alternating dual pol mode. If true, the H-only pulses are used to 
//   compute velocity where CMD flags a gate as clutter.
// Type: boolean
//

use_h_only_for_alt_mode_clutter_vel = TRUE;

//======================================================================
//
// COMPUTING KDP.
//
// Parameters for computing KDP.
//
//======================================================================
 
///////////// KDP_fir_filter_len //////////////////////
//
// Filter length for the FIR filter for PHIDP (gates).
// When computing KDP, an FIR filter is first applied to PHIDP to smooth 
//   it. This is the length of that filter, in gates.
//
// Type: enum
// Options:
//     FIR_LEN_125
//     FIR_LEN_30
//     FIR_LEN_20
//     FIR_LEN_10
//

KDP_fir_filter_len = FIR_LEN_20;

///////////// KDP_phidp_difference_threshold //////////
//
// Sets the threshold for difference of phidp.
// This is used to test the difference between the unfolded phidp value 
//   and the filtered phidp value. If the difference exceeds this value, 
//   we use the original value instead of the filtered value. Applies to 
//   computation of KDP only.
// Type: double
//

KDP_phidp_difference_threshold = 4;

///////////// KDP_phidp_sdev_threshold ////////////////
//
// Sets the threshold for the standard deviation of phidp in range.
// The sdev of phidp is a good test for weather. If the sdev is less 
//   than this value, it is assumed we are in weather. Applies to 
//   computation of KDP only.
// Type: double
//

KDP_phidp_sdev_threshold = 12;

///////////// KDP_zdr_sdev_threshold //////////////////
//
// Sets the threshold for the standard deviation of zdr in range.
// The sdev of zdr is a good test for weather. If the sdev is less than 
//   this value, it is assumed we are in weather. Applies to computation 
//   of KDP only.
// Type: double
//

KDP_zdr_sdev_threshold = 1.8;

///////////// KDP_rhohv_threshold /////////////////////
//
// Sets the threshold for rhohv.
// rhohv is a good test for weather. If rhohv is greater than this 
//   value, it is assumed we are in weather. Applies to computation of KDP 
//   only.
// Type: double
//

KDP_rhohv_threshold = 0.75;

///////////// KDP_constrain_using_dbz /////////////////
//
// Option to constrain KDP to reasonable values using dbz.
// If true, the KDP values will be checked against DBZ, and will be 
//   limited to a reasonable range given the DBZ value.
// Type: boolean
//

KDP_constrain_using_dbz = TRUE;

///////////// KDP_apply_median_filter_to_PHIDP ////////
//
// Option to filter PHIDP with median filter.
// The filter is applied in range.
// Type: boolean
//

KDP_apply_median_filter_to_PHIDP = TRUE;

///////////// KDP_median_filter_len_for_PHIDP /////////
//
// Length of median filter for PHIDP - gates.
// See 'appply_median_filter_to_PHIDP'.
// Type: int
//

KDP_median_filter_len_for_PHIDP = 5;

//======================================================================
//
// REFRACTIVITY FIELDS.
//
//======================================================================
 
///////////// change_aiq_sign /////////////////////////
//
// Option to change sign on AIQ field.
// This affects refractt variables. Set to true to change the sign of 
//   the computed AIQ field.
// Type: boolean
//

change_aiq_sign = FALSE;

//======================================================================
//
// SZ8-64 PHASE CODING.
//
//======================================================================
 
///////////// sz_snr_threshold ////////////////////////
//
// Signal-to-noise value for thresholding for SZ864 (dB).
// This is the signal-to-noise ratio used to thresholding based on the 
//   noise.
// Type: double
//

sz_snr_threshold = 3;

///////////// negate_phase_codes //////////////////////
//
// Option to multiple phase codes by -1.
// In some data sets the phase codes are negated. Set this to true for 
//   such data cases.
// Type: boolean
//

negate_phase_codes = FALSE;

///////////// sz_strong_to_weak_power_ratio_threshold /
//
// Strong-to-weak power ratio censoring threshold (dB).
// SZ decoding only. If the strong to weak trip power ratio is greater 
//   than this, we censor the weak trip.
// Type: double
//

sz_strong_to_weak_power_ratio_threshold = 50;

///////////// sz_out_of_trip_power_ratio_threshold ////
//
// Ratio of peak power to off-peak replica power (dB).
// SZ decoding only. When checking for out-of-trip power after 
//   deconvolution, this is the threshold to be used. The power of the 
//   spectral peak is compared with the peak for the 6 lowest replicas. If 
//   the ratio is less that this for a given number of replicas, it is 
//   assumed that out-of-trip power is present. See 
//   'sz_out_of_trip_power_n_replicas'.
// Type: double
//

sz_out_of_trip_power_ratio_threshold = 6;

///////////// sz_out_of_trip_power_n_replicas /////////
//
// Number of replicas used for checking for out-of-trip power.
// SZ decoding only. When checking for out-of-trip power after 
//   deconvolution, this is the number of peaks to check. See 
//   'sz_out_of_trip_power_ratio_threshold'.
// Minimum val: 1
// Maximum val: 6
// Type: int
//

sz_out_of_trip_power_n_replicas = 3;

//======================================================================
//
// CMD - CLUTTER MITIGATION DECISION system.
//
// Option to compute and use CMD fields.
//
//======================================================================
 
///////////// cmd_kernel_ngates_tdbz //////////////////
//
// Length of CMD kernel in range for TDBZ (gates).
// TDBZ is computed over a kernel in range.
// Type: int
//

cmd_kernel_ngates_tdbz = 9;

///////////// cmd_kernel_ngates_spin //////////////////
//
// Length of CMD kernel in range for SPIN (gates).
// SPIN is computed over a kernel in range.
// Type: int
//

cmd_kernel_ngates_spin = 11;

///////////// cmd_kernel_ngates_zdr_sdev //////////////
//
// Length of CMD kernel in range for ZDR sdev (gates).
// sdev_zdr are computed over a kernel in range.
// Type: int
//

cmd_kernel_ngates_zdr_sdev = 7;

///////////// cmd_kernel_ngates_phidp_sdev ////////////
//
// Length of CMD kernel in range for PHIDP sdev (gates).
// sdev_phidp are computed over a kernel in range.
// Type: int
//

cmd_kernel_ngates_phidp_sdev = 7;

///////////// cmd_spin_dbz_threshold //////////////////
//
// Threshold for computing spin change in the CMD (dBZ).
// The SPIN change variable is computed using the difference in dBZ 
//   between adjacent gates. If the difference exceeds this threshold, the 
//   change counter is incremented.
// Type: double
//

cmd_spin_dbz_threshold = 6.5;

///////////// cmd_snr_threshold ///////////////////////
//
// Signal-to-noise ratio value for CMD (dB).
// Only gates which exceed this snr will be considered for the CMD flag.
// Type: double
//

cmd_snr_threshold = 3;

///////////// cpa_median_filter_len ///////////////////
//
// Length of median filter applied to CPA field in range (gates).
// Set to 1 if you do not want a median filter applied.
// Type: int
//

cpa_median_filter_len = 1;

///////////// cpa_compute_using_alternative ///////////
//
// Option to use alternative method for computing CPA.
// If true, use alternative formulation where we look for the minimum 
//   5-pt running CPA and then compute the CPA values on each side of the 
//   minimum. The mean of these two values is returned. This formulation 
//   works well for time series in which the CPA value is high, then 
//   becomes low for a short period, and then returns to high values for 
//   the rest of the series.
// Type: boolean
//

cpa_compute_using_alternative = TRUE;

///////////// cmd_threshold_for_clutter ///////////////
//
// Threshold CMD value for identifying clutter.
// If the CMD value exceeds this threshold, clutter is assumed to exist 
//   at that point.
// Type: double
//

cmd_threshold_for_clutter = 0.5;

///////////// cmd_check_for_offzero_weather ///////////
//
// Option to check for weather well away from zero m/s.
// If true, the off-zero-velocity SNR will be computed after applying a 
//   notch of width notch_width_for_offzero_snr. If this exceeds 
//   min_snr_for_offzero_weather, cmd_threshold_for_offzero_weather will 
//   be used instead of cmd_threshold_for_clutter.
// Type: boolean
//

cmd_check_for_offzero_weather = TRUE;

///////////// cmd_threshold_for_offzero_weather ///////
//
// Secondary CMD threshold value to be used if off-zero weather is 
//   present.
// This is applied only of the off-zero SNR exceeds 
//   min_snr_for_offzero_weather.
// Type: double
//

cmd_threshold_for_offzero_weather = 0.25;

///////////// min_snr_for_offzero_weather /////////////
//
// Minimum value for off-zero SNR to identify off-zero weather.
// This is applied only of the off-zero SNR exceeds 
//   offzero_snr_threshold.
// Type: double
//

min_snr_for_offzero_weather = 3;

///////////// notch_width_for_offzero_snr /////////////
//
// Notch width for computing off-zero SNR (m/s).
// Off-zero SNR is computed after applying a notch of this width to the 
//   spectrum. This needs to be wide enough to ensure that no clutter 
//   power is included in the off-zero SNR.
// Type: double
//

notch_width_for_offzero_snr = 6;

///////////// apply_db_for_db_correction //////////////
//
// Option to apply legacy NEXRAD db-for-db correction after applying 
//   CMD.
// When a significant level of clutter is present, the noise level in 
//   the spectral skirts rises. It is not possible to adjust for this 
//   directly in the filter. Therefore, an extra correction is needed. If 
//   this is set FALSE, the clutter residue is computed from the spectrum. 
//   This is the preferred method. If TRUE, the legacy db-for-db 
//   correction developed for NEXRAD is used. For every db of power 
//   removed by the filter below the db_for_db_threshold, an extra 
//   db_for_db is removed. For every db of power removed above the 
//   threshold, and extra 1 db is removed.
// Type: boolean
//

apply_db_for_db_correction = TRUE;

///////////// db_for_db_ratio /////////////////////////
//
// Ratio for computing clutter correction when below 
//   db_for_db_threshold.
// If the clutter power removed is less than db_for_db_threshold, the 
//   db_for_db_corection is the clutter db multiplied by this ratio.
// Type: double
//

db_for_db_ratio = 0.2;

///////////// db_for_db_threshold /////////////////////
//
// Threshold for db_for_db correction.
// If the computed clutter power is less than this threshold, then the 
//   db_for_db correction is computed as the db_for_db_ratio multiplied by 
//   the clutter power. If the clutter power exceeds this threshold, the 
//   correction is 1 db for every db by which the clutter exceeds the 
//   threshold.
// Type: double
//

db_for_db_threshold = 40;

///////////// apply_cmd_speckle_filter ////////////////
//
// Option to apply speckle filter to CMD flag field.

// After CMD is run, and the gap filter has been applied, the CMD flag 
//   field can still have isolated gates marked as clutter. We refer to 
//   these as speckle. These can be point targets - in which case they 
//   should be filtered. Or they could be false-alarms, in which case they 
//   should be removed from the CMD flag field.

// The speckle filter is designed to remove these gates.

// See cmd_speckle_thresholds.
// Type: boolean
//

apply_cmd_speckle_filter = TRUE;

///////////// cmd_speckle_filter_thresholds ///////////
//
// Thesholds use to test speckle.
// You specify a series of thresholds for speckle of different lengths 
//   (in gates). length is the length of the speckle in gates. 
//   min_valid_cmd is the cmd threshold for testing those gates. If the 
//   cmd at a gate is below the threshold, the CMD_FLAG is set to false. 
//   The filter is run once for each specified length, starting at the 
//   longest length and moving to the shortest length.
//
// Type: struct
//   typedef struct {
//      int length;
//      double min_valid_cmd;
//   }
//
// 1D array - variable length.
//

cmd_speckle_filter_thresholds = {
  { 1, 0.75},
  { 2, 0.65},
  { 3, 0.55}
};

///////////// apply_cmd_gap_filter ////////////////////
//
// Option to apply gap filter to CMD flag field.

// After CMD is run, the CMD flag field tends to have gaps, which should 
//   be filtered, since they are surrounded by filtered gates. The gap 
//   infill process is designed to fill the gaps in the flag field.

// Initialization:

// A template of weights, of length n, is computed with the following 
//   values:
//       1, 1/2, 1/3, 1/4, ... 1/n
// where n = cmd_gap_filter_len

// Computing the forward sum of weights:
//   For each gate at which the flag is not yet set, compute the sum of 
//   the (weight * cmd) for each of the previous n gates at which the flag 
//   field is set. A weight of 1*cmd applies to the previous gate, 
//   (1/2)*cmd applies to the second previous gate, etc.

// Computing the reverse sum of weights:
//   For each gate at which the flag is not yet set, compute the sum of 
//   the (weight * cmd) for each of the next n gates at which the flag 
//   field is set. The weights are used in the reverse sense, i.e 1*cmd 
//   applies to the next gate, (1/2)*cmd applies to the second next gate 
//   etc.

// The sum-of-weights*cmd is then compared to cmd_gap_filter_threshold

// A threshold of 0.35 (the default) will succeed with:
//   a single adjacent flag gate, or
//   2 consecutive gates starting 2 gates away, or
//   3 consecutive gates starting 3 gates away, or
//   4 consecutive gates starting 4 gates away, etc.

// The test will also succeed with a mixture of flagged and unflagged 
//   gates at various distances from the test gate.

// Checking the sums against the threshold:
//   If both the forward sum and the reverse sum exceed the threshold, 
//   then this gate is considered likely to have clutter, and the cmd_flag 
//   is set.
// Type: boolean
//

apply_cmd_gap_filter = TRUE;

///////////// cmd_gap_filter_len //////////////////////
//
// Number of gates on either side of target gate.
// See apply_cmd_gap_filter.
// Type: int
//

cmd_gap_filter_len = 6;

///////////// cmd_gap_filter_threshold ////////////////
//
// Threshold for sum of (weight * cmd) in gap filter.
// If the sum exceeds this value, the gap is filled in. If not, it is 
//   left open.
// Type: double
//

cmd_gap_filter_threshold = 0.35;

///////////// apply_nexrad_spike_filter_after_cmd /////
//
// Option to apply spike filter after the CMD.
// If true, the NEXRAD spike filter will be applied to the filtered 
//   fields.
// Type: boolean
//

apply_nexrad_spike_filter_after_cmd = TRUE;

//======================================================================
//
// CMD INTEREST MAPS and WEIGHTS.
//
// Each map should hold at least 2 points. The points should be 
//   increasing in value, i.e. the value should increase for each 
//   subsequent point. The various interest values are combined using the 
//   specified weights in a weighted mean to produce the final CMD value.
//
//======================================================================
 
///////////// tdbz_interest_map ///////////////////////
//
// Interest mapping for TDBZ.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

tdbz_interest_map = {
  { 20, 0.001},
  { 40, 1}
};

///////////// tdbz_interest_weight ////////////////////
//
// Weight for TDBZ interest.
// Defaults to 0.0 since we normally use the max interest of TDBZ and 
//   SPIN instead of TDBZ and SPIN individually.
// Type: double
//

tdbz_interest_weight = 0;

///////////// spin_interest_map ///////////////////////
//
// Interest mapping for dBZ spin.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

spin_interest_map = {
  { 15, 0.001},
  { 30, 1}
};

///////////// spin_interest_weight ////////////////////
//
// Weight for SPIN interest.
// Defaults to 0.0 since we normally use the max interest of TDBZ and 
//   SPIN instead of TDBZ and SPIN individually.
// Type: double
//

spin_interest_weight = 0;

///////////// max_of_tdbz_and_spin_interest_weight ////
//
// Weight for max of TDBZ and SPIN interest.
// A combined interest field is formed by applying the interest maps to 
//   TDBZ and SPIN, and taking the maximum of the result. The combined 
//   field can then be used as an interest field instead of TDBZ and SPIN 
//   individually.
// Type: double
//

max_of_tdbz_and_spin_interest_weight = 0.75;

///////////// cpa_interest_map ////////////////////////
//
// Interest mapping for clutter phase alignment.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

cpa_interest_map = {
  { 0.75, 0},
  { 0.9, 1}
};

///////////// cpa_interest_weight /////////////////////
//
// Weight for clutter phase alignment.
// Type: double
//

cpa_interest_weight = 1;

///////////// tpt_interest_map ////////////////////////
//
// Interest mapping for time series power trend.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

tpt_interest_map = {
  { 11.5, 0.001},
  { 12.5, 1}
};

///////////// tpt_interest_weight /////////////////////
//
// Weight for TPT interest.
// Defaults to 0.0 since we normally use TCLUT - the max interest of TPT 
//   and CPD instead of TPT and CPD individually. See 
//   tclut_interest_weight.
// Type: double
//

tpt_interest_weight = 0;

///////////// cpd_interest_map ////////////////////////
//
// Interest mapping for cumulative phase difference.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

cpd_interest_map = {
  { 110, 1},
  { 120, 0.001}
};

///////////// cpd_interest_weight /////////////////////
//
// Weight for CPD interest.
// Defaults to 0.0 since we normally use TCLUT - the max interest of TPT 
//   and CPD instead of TPT and CPD individually. See 
//   tclut_interest_weight.
// Type: double
//

cpd_interest_weight = 0;

///////////// tclut_interest_weight ///////////////////
//
// Weight for time series clutter interest.
// TCLUT is the maximum of TPT interest and CPD interest.
// Type: double
//

tclut_interest_weight = 0;

///////////// zdr_sdev_interest_map ///////////////////
//
// Interest mapping for zdr.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

zdr_sdev_interest_map = {
  { 1.2, 0},
  { 2.4, 1}
};

///////////// zdr_sdev_interest_weight ////////////////
//
// Weight for standard deviation of zdr.
// Type: double
//

zdr_sdev_interest_weight = 1;

///////////// phidp_sdev_interest_map /////////////////
//
// Interest mapping for standard deviation of phidp.
//
// Type: struct
//   typedef struct {
//      double value;
//      double interest;
//   }
//
// 1D array - variable length.
//

phidp_sdev_interest_map = {
  { 10, 0},
  { 15, 1}
};

///////////// phidp_sdev_interest_weight //////////////
//
// Weight for standard deviation of phidp.
// Type: double
//

phidp_sdev_interest_weight = 1;

//======================================================================
//
// OUTPUT TO DSRADAR FMQ.
//
//======================================================================
 
///////////// output_fmq_url //////////////////////////
//
// Output URL for DsRadar data via FMQ.
// Type: string
//

output_fmq_url = "$(DATA_DIR)/fmq/moments/sband";

///////////// output_fmq_size /////////////////////////
//
// Size of output FMQ, in bytes.
// This is the total size of the output FMQ buffer. Some of this buffer 
//   will be used for control bytes (12 bytes per message).
// Type: int
//

output_fmq_size = 1000000000;

///////////// output_fmq_nslots ///////////////////////
//
// Number of slots in output FMQ.
// The number of slots corresponds to the maximum number of messages 
//   which may be written to the buffer before overwrites occur. However, 
//   overwrites may occur sooner if the size is not set large enough.
// Type: int
//

output_fmq_nslots = 7200;

///////////// output_fmq_compress /////////////////////
//
// FMQ compression option.
// If TRUE FMQ messages are compressed.
// Type: boolean
//

output_fmq_compress = FALSE;

///////////// nbeams_for_params_and_calib /////////////
//
// Number of beams between sending params and calibration.
// The params and calibration data is sent when the radar operation 
//   changes, as well as once every tilt. However, if none of these 
//   triggers a change, the params will be sent regardless when this 
//   number of beams have been written.
// Type: int
//

nbeams_for_params_and_calib = 90;

///////////// write_blocking //////////////////////////
//
// Option to set up the FMQ as blocking.
// If TRUE, FMQ will be set up FMQ for blocking operation. If the FMQ 
//   becomes full, Test2Dsr will then block until there is space for more 
//   data.
// Type: boolean
//

write_blocking = TRUE;

///////////// beam_wait_msecs /////////////////////////
//
// Wait per beam (milli-secs).
// ARCHIVE and SIMULATE modes only.
// Type: int
//

beam_wait_msecs = 0;

///////////// set_end_of_vol_from_elev_angle //////////
//
// Option to set the end of vol flag based on elevation angle.
// If true, the program will look for changes in antenna angle to 
//   compute the end of volume.
// Type: boolean
//

set_end_of_vol_from_elev_angle = FALSE;

///////////// vol_starts_at_bottom ////////////////////
//
// Flag to indicate that elevation angles increase in the volume.
// If the volume starts at the top, i.e. elevations decrease during the 
//   volume, set this to FALSE.
// Type: boolean
//

vol_starts_at_bottom = TRUE;

///////////// elev_change_for_end_of_vol //////////////
//
// Change in elevation which triggers and end of volume.
// If the elevation angle changes by this amount, and end of volume flag 
//   will be set.
// Minimum val: 0.1
// Type: double
//

elev_change_for_end_of_vol = 1.5;

///////////// min_beams_per_vol ///////////////////////
//
// Min number of beams per volume.
// Used to prevent end-of-volume conditions being determined during 
//   antenna transition to the start of the next volume. Only used for 
//   set_end_of_vol_from_elev_angle.
// Type: int
//

min_beams_per_vol = 360;

///////////// set_end_of_vol_on_prf_change ////////////
//
// Option to set the end-of-vol flag when the PRF changes.
// Type: boolean
//

set_end_of_vol_on_prf_change = TRUE;

///////////// set_end_of_vol_on_pulse_width_change ////
//
// Option to set the end-of-vol flag when the pulse width changes.
// Type: boolean
//

set_end_of_vol_on_pulse_width_change = FALSE;

///////////// output_fields ///////////////////////////
//
// Indicate which fields should be written to the Dsr FMQ.
// Choose the ID from the list. The name and units can be set however 
//   the user prefers. The scale and bias are applied to the floating 
//   point value to compute the 16-bit output value for the FMQ. The 
//   write_filtered and write_unfiltered flags indicate which fields 
//   should be written.
//
// Type: struct
//   typedef struct {
//      field_id_t id;
//        Options:
//          NCP
//          SNR
//          DBM
//          DBZ
//          VEL
//          WIDTH
//          WIDTH_R0R1
//          WIDTH_R1R2
//          WIDTH_R1R3
//          WIDTH_PPLS
//          DBZHC
//          DBZVC
//          DBZHX
//          DBZVX
//          VEL_PRT_SHORT
//          VEL_PRT_LONG
//          STAGGERED_VDIFF
//          STAGGERED_UNFOLD_INTERVAL
//          CLUT
//          CLUT_2_WX_RATIO
//          SPECTRAL_NOISE
//          SPECTRAL_SNR
//          ZDR
//          ZDRM
//          LDRH
//          LDRV
//          RHOHV
//          PHIDP0
//          PHIDP
//          KDP
//          SNRHC
//          SNRHX
//          SNRVC
//          SNRVX
//          DBMHC
//          DBMHX
//          DBMVC
//          DBMVX
//          CPA
//          PRATIO
//          MVAR
//          TSS
//          TPT
//          CPD
//          TCLUT
//          OZSNR
//          TDBZ
//          SPIN
//          MAX_TDBZ_SPIN
//          ZDR_SDEV
//          PHIDP_SDEV
//          DBZ_DIFF_SQ
//          DBZ_SPIN_CHANGE
//          CMD
//          CMD_FLAG
//          CPR_MAG
//          CPR_PHASE
//          CPR_LDR
//          RHO_HC_VX
//          RHO_VC_HX
//          RHO_PHIDP
//          AIQ
//          NIQ
//          MEANIQ_DB
//          MEANIQ_PHASE
//          SZ_TRIP_FLAG
//          SZ_LEAKAGE
//          CENSORING_FLAG
//          LAG0_HC_DB
//          LAG0_HX_DB
//          LAG0_VC_DB
//          LAG0_VX_DB
//          LAG0_HCVX_DB
//          LAG0_HCVX_PHASE
//          LAG0_VCHX_DB
//          LAG0_VCHX_PHASE
//          LAG1_HC_DB
//          LAG1_HC_PHASE
//          LAG1_VC_DB
//          LAG1_VC_PHASE
//          LAG1_HCVC_DB
//          LAG1_HCVC_PHASE
//          LAG1_VCHC_DB
//          LAG1_VCHC_PHASE
//          LAG1_VXHX_DB
//          LAG1_VXHX_PHASE
//          LAG2_HC_DB
//          LAG2_HC_PHASE
//          LAG2_VC_DB
//          LAG2_VC_PHASE
//          LAG3_HC_DB
//          LAG3_HC_PHASE
//          LAG3_VC_DB
//          LAG3_VC_PHASE
//          SDEV_VV
//          PRT
//          NUM_PULSES
//          TEST
//      string name;
//      string units;
//      double scale;
//      double bias;
//      boolean write_unfiltered;
//      boolean write_filtered;
//   }
//
// 1D array - variable length.
//

output_fields = {
  { DBZ, "DBZ", "dBZ", 0.01, -320, TRUE, TRUE},
  { VEL, "VEL", "m/s", 0.01, -320, TRUE, TRUE},
  { WIDTH, "WIDTH", "m/s", 0.001, -0.01, TRUE, TRUE},
  { CLUT, "CLUT", "dB", 0.01, -320, TRUE, FALSE},
  { ZDR, "ZDR", "dB", 0.001, -32, TRUE, TRUE},
  { ZDRM, "ZDRM", "dB", 0.001, -32, TRUE, TRUE},
  { LDRH, "LDRH", "dB", 0.005, -160, TRUE, TRUE},
  { LDRV, "LDRV", "dB", 0.005, -160, TRUE, TRUE},
  { RHOHV, "RHOHV", "", 0.0001, -1, TRUE, TRUE},
  { PHIDP, "PHIDP", "deg", 0.06, -200, TRUE, TRUE},
  { KDP, "KDP", "deg/km", 0.001, -32, TRUE, TRUE},
  { SNRHC, "SNRHC", "dB", 0.01, -320, TRUE, TRUE},
  { SNRHX, "SNRHX", "dB", 0.01, -320, TRUE, TRUE},
  { SNRVC, "SNRVC", "dB", 0.01, -320, TRUE, TRUE},
  { SNRVX, "SNRVX", "dB", 0.01, -320, TRUE, TRUE},
  { DBMHC, "DBMHC", "dBm", 0.01, -320, TRUE, TRUE},
  { DBMHX, "DBMHX", "dBm", 0.01, -320, TRUE, TRUE},
  { DBMVC, "DBMVC", "dBm", 0.01, -320, TRUE, TRUE},
  { DBMVX, "DBMVX", "dBm", 0.01, -320, TRUE, TRUE},
  { NCP, "NCP", "", 0.0001, -0.01, TRUE, TRUE},
  { CPA, "CPA", "", 0.0001, -1, TRUE, FALSE},
  { TDBZ, "TDBZ", "dBzSq", 0.1, -0.1, TRUE, FALSE},
  { SPIN, "SPIN", "", 0.01, -0.1, TRUE, FALSE},
  { MAX_TDBZ_SPIN, "MAX_TDBZ_SPIN", "", 0.0001, -1, TRUE, FALSE},
  { ZDR_SDEV, "ZDR_SDEV", "dB", 0.001, -32, TRUE, FALSE},
  { PHIDP_SDEV, "PHIDP_SDEV", "deg", 0.02, -640, TRUE, FALSE},
  { DBZ_DIFF_SQ, "DBZ_DIFF_SQ", "dBzSq", 0.01, -320, FALSE, FALSE},
  { DBZ_SPIN_CHANGE, "DBZ_SPIN_CHANGE", "", 0.01, -320, FALSE, FALSE},
  { CMD, "CMD", "", 0.001, -0.01, TRUE, FALSE},
  { CMD_FLAG, "CMD_FLAG", "", 1, -100, TRUE, FALSE},
  { AIQ, "AIQ", "deg", 0.12, -360, TRUE, FALSE},
  { NIQ, "NIQ", "dBm", 0.01, -320, TRUE, FALSE},
  { SZ_TRIP_FLAG, "SZ_TRIP_FLAG", "", 1, -1000, FALSE, FALSE},
  { SZ_LEAKAGE, "SZ_LEAKAGE", "", 0.0001, -1, FALSE, FALSE},
  { CENSORING_FLAG, "CENSORING_FLAG", "", 1, -1000, FALSE, FALSE},
  { LAG0_HC_DB, "LAG0_HC_DB", "dBm", 0.005, -160, TRUE, TRUE},
  { LAG0_HX_DB, "LAG0_HX_DB", "dBm", 0.005, -160, TRUE, TRUE},
  { LAG0_VC_DB, "LAG0_VC_DB", "dBm", 0.005, -160, TRUE, TRUE},
  { LAG0_VX_DB, "LAG0_VX_DB", "dBm", 0.005, -160, TRUE, TRUE},
  { LAG0_HCVX_DB, "LAG0_HCVX_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG0_HCVX_PHASE, "LAG0_HCVX_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG0_VCHX_DB, "LAG0_VCHX_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG0_VCHX_PHASE, "LAG0_VCHX_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG1_HC_DB, "LAG1_HC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG1_HC_PHASE, "LAG1_HC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG1_VC_DB, "LAG1_VC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG1_VC_PHASE, "LAG1_VC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG1_HCVC_DB, "LAG1_HCVC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG1_HCVC_PHASE, "LAG1_HCVC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG1_VCHC_DB, "LAG1_VCHC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG1_VCHC_PHASE, "LAG1_VCHC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG1_VXHX_DB, "LAG1_VXHX_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG1_VXHX_PHASE, "LAG1_VXHX_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG2_HC_DB, "LAG2_HC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG2_HC_PHASE, "LAG2_HC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG2_VC_DB, "LAG2_VC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG2_VC_PHASE, "LAG2_VC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG3_HC_DB, "LAG3_HC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG3_HC_PHASE, "LAG3_HC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { LAG3_VC_DB, "LAG3_VC_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { LAG3_VC_PHASE, "LAG3_VC_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { RVVHH0_DB, "RVVHH0_DB", "dBm", 0.005, -240, TRUE, TRUE},
  { RVVHH0_PHASE, "RVVHH0_PHASE", "deg", 0.006, -190, TRUE, TRUE},
  { SDEV_VV, "SDEV_VV", "dBm", 0.01, -320, TRUE, FALSE},
  { TEST, "TEST", "", 0.01, -320, FALSE, FALSE}
};

//======================================================================
//
// SWEEP INFORMATION.
//
// Option to read volume and tilt numbers from sweep information in the 
//   incoming pulse data.
//
//======================================================================
 
///////////// use_sweep_info_from_time_series /////////
//
// Option to read sweep info from time series data.
// If not, we need to guess at the sweep information.
// Type: boolean
//

use_sweep_info_from_time_series = TRUE;

///////////// delay_tilt_start_msg_during_ant_trans ///
//
// Option to delay start of tilt message if antenna transition from time 
//   series data.
// Type: boolean
//

delay_tilt_start_msg_during_ant_trans = FALSE;

///////////// sweep_search_margin /////////////////////
//
// Time margin for searching for relevant sweep info - secs.
// This is the time margin, on either side of the beam time, to search 
//   for sweep information. It should be at least as long as the maximum 
//   sweep duratation.
// Type: int
//

sweep_search_margin = 180;

//======================================================================
//
// TRANSITION FLAG.
//
//======================================================================
 
///////////// transition_method ///////////////////////
//
// Method for identifying whether a beam occurs during an antenna 
//   transition.

// Some time series data includes a transition flag, which indicates 
//   when the antenna is in transition from one scan strategy to another.

//   TRANSITION_FLAG_AT_CENTER: the beam is flagged as in transition if 
//   the center pulse of the beam has the transition flag set.

//   TRANSITION_FLAG_AT_BOTH_ENDS: the beam is flagged as in transition 
//   if both the start and end pulses of the beam have the transition flag 
//   set.

//   TRANSITION_FLAG_AT_EITHER_END: the beam is flagged as in transition 
//   if either the start or end pulses of the beam have the transition 
//   flag set.

//   TRANSITION_FLAG_MISSING: transition flag is not available.
//
// Type: enum
// Options:
//     TRANSITION_FLAG_AT_CENTER
//     TRANSITION_FLAG_AT_BOTH_ENDS
//     TRANSITION_FLAG_AT_EITHER_END
//     TRANSITION_FLAG_MISSING
//

transition_method = TRANSITION_FLAG_AT_CENTER;

