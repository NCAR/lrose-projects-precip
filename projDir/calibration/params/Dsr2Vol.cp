/**********************************************************************
 * TDRP params for Dsr2Vol
 **********************************************************************/

//======================================================================
//
// Dsr2Vol program.
//
// Dsr2Volreads an input FMQ containing radar data, and writes it to a 
//   file in MDV format. Grid remapping and spatial interpolation are 
//   optional.
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
//     DEBUG_EXTRA
//

debug = DEBUG_NORM;

///////////// instance ////////////////////////////////
//
// Process instance.
// Used for registration with procmap.
// Type: string
//

instance = "cp";

//======================================================================
//
// DATA INPUT.
//
//======================================================================
 
///////////// input_fmq_url ///////////////////////////
//
// Input URL for DsRadar data via FMQ.
// Type: string
//

input_fmq_url = "fmqp:://localhost::fmq/moments/sband";

///////////// seek_to_end_of_input ////////////////////
//
// Option to seek to the end of the input FMQ.
// If TRUE, the program will seek to the end of the fmq and only read in 
//   new data. If FALSE, it will start reading from the beginning of the 
//   FMQ.
// Type: boolean
//

seek_to_end_of_input = TRUE;

///////////// end_of_vol_decision /////////////////////
//
// Decision type for end-of-volume.
// If END_OF_VOL_FLAG, the end-of-volume flag in the data will be used 
//   to trigger the end of volume. If CHANGE_IN_VOL_NUM, and end of volume 
//   will be assumed when the volume number changes from one beam to the 
//   next. If LAST_TILT_IN_VOL, the end of the tilt number given by 
//   'last_tilt_in_vol' will be used  to trigger the end-of-volume. If 
//   AUTOMATIC, this program will determine the end-of-volume condition by 
//   using the antenna-angle information.
//
// Type: enum
// Options:
//     END_OF_VOL_FLAG
//     CHANGE_IN_VOL_NUM
//     LAST_TILT_IN_VOL
//     AUTOMATIC
//

end_of_vol_decision = END_OF_VOL_NONE;

///////////// last_tilt_in_vol ////////////////////////
//
// The tilt number used to end the volume.
// Only applies if 'end_of_vol_decision' is set to LAST_TILT_IN_VOL.
// Type: int
//

last_tilt_in_vol = 100;

///////////// write_end_of_vol_when_data_stops ////////
//
// Write end of vol event when data stops.
// Type: boolean
//

write_end_of_vol_when_data_stops = FALSE;

///////////// nsecs_no_data_for_end_of_vol ////////////
//
// Number of secs before writing end of vol.
// See 'write_end_of_vol_when_data_stops'.
// Type: int
//

nsecs_no_data_for_end_of_vol = 5;

///////////// nbeams_overlap_per_vol //////////////////
//
// The number of beams copied from the previous vol.
// If non-zero, this number of beams is copied from the previous volume 
//   into the current one, at the start of the current volume. This is 
//   useful if the exact timing of the end-of-vol condition is in 
//   question, so that the data around the end-of-vol can be used in both 
//   volumes. If you set end_of_vol_decision to AUTOMATIC, it is 
//   recommended that you set this value to between 20 and 50, because the 
//   end-of-vol decision may be a few beams late.
// Type: int
//

nbeams_overlap_per_vol = 0;

///////////// min_beams_in_vol ////////////////////////
//
// The minimum number of beams in a volume.
// This filters out small unwanted bits of data between genuine volumes.
// Type: int
//

min_beams_in_vol = 450;

///////////// max_beams_in_vol ////////////////////////
//
// The maximum number of beams in a volume.
// This prevents memory from filling up if no end-of-volume is found.
// Type: int
//

max_beams_in_vol = 460;

///////////// use_input_scan_mode /////////////////////
//
// Option to use the scan_mode in the input data.
// The scan_mode indicates whether the scan is of type SURVEILLANCE/PPI 
//   RHI. The scan_mode is optionally included in the beam data. If 
//   available, it makes sense to use the scan mode to determine whether 
//   to save the data as a SURVEILLANCE/PPI or RHI. Dsr2Vol treats 
//   SURVEILLANCE and PPI data in the same manner. However, RHIs are saved 
//   in a different way. If the input scan_mode is NOT used, Dsr2Vol uses 
//   the antenna angle changes to determine whether the scan is in PPI or 
//   RHI mode.
// Type: boolean
//

use_input_scan_mode = TRUE;

///////////// use_input_tilt_numbers //////////////////
//
// Option to use tilt numbers instead of the elevation histogram.
// If TRUE, the tilt numbers in the beam data will be used directly to 
//   group the beams into tilts. If FALSE, the antenna angles will be 
//   analysed using a histogram technique to determine the tilt numbers.
// Type: boolean
//

use_input_tilt_numbers = FALSE;

//======================================================================
//
// COMPUTING THE ELEVATION HISTOGRAM.
//
// The program needs to determine the elevation angles used in the scan 
//   strategy. It does this by creating a histgram of elevation angles, 
//   and looking for peaks in this histogram.
//
//======================================================================
 
///////////// use_target_elev /////////////////////////
//
// Option to use target elevation angles instead of actual.
// If TRUE, the beam elevation will be set to the target elevation 
//   angle, and the actual elevation angle will be ignored.
// Type: boolean
//

use_target_elev = FALSE;

///////////// elev_hist_resolution ////////////////////
//
// Resolution of elevation histogram (deg).
// The elevation data is binned at this resolution. If the scan strategy 
//   has elevations very close together you may need to decrease this.
// Type: double
//

elev_hist_resolution = 0.1;

///////////// elev_hist_search_width //////////////////
//
// The width of the search in looking for peaks in the histogram.
// When looking for peaks, the program searches by this number of bins 
//   on either side of the search bin. For example, if the 
//   elev_hist_resolution is 0.1 and the elev_hist_search_width is 3, the 
//   program will search 3 bins, or 0.3 degrees, on either side of the 
//   search bin. It looks for a peak with values equal to or below the 
//   peak in the adjacent bins and less than the peak in bins further out.
// Minimum val: 1
// Type: int
//

elev_hist_search_width = 3;

///////////// elev_hist_start /////////////////////////
//
// Histogram start value (deg).
// The elev value for the lowest bin in the histogram.
// Type: double
//

elev_hist_start = -10;

///////////// elev_hist_end ///////////////////////////
//
// Histogram end value (deg).
// The elev value for the highest bin in the histogram.
// Type: double
//

elev_hist_end = 90;

///////////// specify_elev_delta //////////////////////
//
// Option to specify the delta elevation instead of using the elevation 
//   histogram.
// This is useful if you have RHI data as input but want to store the 
//   output as PPIs. Specify the delta elevation.
// Type: boolean
//

specify_elev_delta = FALSE;

///////////// elev_delta //////////////////////////////
//
// The delta elevation to be used (deg).
// See 'specify_elev_delta'.
// Type: double
//

elev_delta = 1;

//======================================================================
//
// CHECKING TILT DATA.
//
// Checking whether tilts should be included.
//
//======================================================================
 
///////////// check_min_beams_in_tilt /////////////////
//
// Option to check the number of beams in a tilt.
// If TRUE, a tilt is only considered valid if the number of beams 
//   exceeds 'min_beams_in_tilt'.
// Type: boolean
//

check_min_beams_in_tilt = TRUE;

///////////// min_beams_in_tilt ///////////////////////
//
// The min number of beams for a tilt to be valid.
// See 'check_min_beams_in_tilt'.
// Type: int
//

min_beams_in_tilt = 20;

///////////// check_min_fraction_in_tilt //////////////
//
// Option to check the fraction of beams in a tilt.
// If TRUE, a tilt is only considered valid if the number of beams in 
//   the tilt, expressed as a fraction of the max number of beams in any 
//   tilt, exceeds 'min_fraction_in_tilt'.
// Type: boolean
//

check_min_fraction_in_tilt = FALSE;

///////////// min_fraction_in_tilt ////////////////////
//
// The min fraction of max beams for a tilt to be valid.
// See 'check_min_fraction_in_tilt'.
// Type: double
//

min_fraction_in_tilt = 0.1;

//======================================================================
//
// CENSORING USING A SPECIFIED FIELD AND/OR SIGNAL-TO-NOISE RATIO.
//
// You have the option of filtering the output data based on the value 
//   of a specified field and/or the signal-to-noise ratio. If both 
//   methods are activated, then both methods must trigger at a gate for 
//   censoring to occur. For example, suppose you set thresholding on for 
//   NCP from 0.2 to 1.0, and sn_threshold of 3.0. Then, for censoring to 
//   occur, NCP must be below 0.2 and SNR must be below 3.
//
//======================================================================
 
///////////// filter_output_using_thresholds //////////
//
// Option to censor the output fields using a min and max threshold on a 
//   specified field.
// If TRUE, the value of the threshold field at a gate will be examined 
//   to see if it is within the desired range. Normally NCP (normalized 
//   coherent power) will be used for this purpose. If the specified field 
//   at a gate falls outside the specified range, a censoring flag will be 
//   set. If check_sn is also set, the SNR at the gate will also be 
//   checked. If both of these tests indicate censoring, then all of the 
//   fields at the gate will be censored. If cgeck_sn is false, then only 
//   the threshold test will be used for censoring.
// Type: boolean
//

filter_output_using_thresholds = FALSE;

///////////// threshold_field_name ////////////////////
//
// Name of field for thresholding.
// This is the DSR (input) field name for the thresholding field. If 
//   this field is available, it is used for thresholding. If not, 
//   thresholding will not be performed.
// Type: string
//

threshold_field_name = "NCP";

///////////// threshold_min_value /////////////////////
//
// Minimum threshold - see 'filter_output_using_thresholds'.
// If the value of the thresholding field at a gate is below this value, 
//   the gate is flagged as a candidate for censoring.
// Type: double
//

threshold_min_value = 0.15;

///////////// threshold_max_value /////////////////////
//
// Maximum threshold - see 'filter_output_using_thresholds'.
// If the value of the thresholding field at a gate is above this value, 
//   the gate is flagged as a candidate for censoring.
// Type: double
//

threshold_max_value = 1000;

///////////// check_sn ////////////////////////////////
//
// Option to check the signal-to-noise for censoring purposes.
// If TRUE, the signal-to-noise ratio value will be checked at each 
//   gate. If the NSR value is below 'sn_threshold', it will be flagged 
//   for censoring. If filter_output_using_thresholds is also true, then 
//   both methods must trigger for censoring to occur.
// Type: boolean
//

check_sn = FALSE;

///////////// snr_field_name //////////////////////////
//
// Specify the name of SNR field.
// This is the DSR (input) field name for SNR. NOTE - you must also 
//   include this field in the output_fields array if you want to 
//   threshold on SNR. If this field is not available or is not in the 
//   output field list, DBZ will be used to estimate SNR. See 
//   'noise_dbz_at_100km'.
// Type: string
//

snr_field_name = "SNRHC";

///////////// sn_threshold ////////////////////////////
//
// Signal-to-noise threshold for censoring.
// See 'check_sn'.
// Type: double
//

sn_threshold = 3;

///////////// noise_dbz_at_100km //////////////////////
//
// The receiver noise power, represented as dBZ at a range of 100km.
// This is used for computing the SNR value from the DBZ field. This 
//   will be used if SNR is not available. See 'snr_field_name'.
// Type: double
//

noise_dbz_at_100km = -3;

///////////// filtering_min_valid_run /////////////////
//
// Minimum valid run of non-censored gates.
// Only active if set to 2 or greater. A check is made to remove short 
//   runs of noise. Looking along the radial, we compute the number of 
//   contiguous gates (a 'run') with uncensored data. For the gates in 
//   this run to be accepted the length of the run must exceed 
//   censoring_min_valid_run. If the number of gates in a run is less than 
//   this, then all gates in the run are censored.
// Type: int
//

filtering_min_valid_run = 3;

//======================================================================
//
// FILLING IN MISSING BEAMS.
//
//======================================================================
 
///////////// bridge_missing_in_azimuth ///////////////
//
// Option to bridge over missing beams in azimuth.
// If true, missing beams in azimuth will be filled in by interpolating 
//   from the adjacent two beams. Only a single missing beam will be 
//   filled in. If more than one is missing, they will not be filled in. 
//   Azimuth filling is done first, before elevation filling.
// Type: boolean
//

bridge_missing_in_azimuth = TRUE;

///////////// bridge_missing_in_elevation /////////////
//
// Option to bridge over missing beams in elevation.
// If true, missing beams in elevation will be filled in by 
//   interpolating from the adjacent two beams. Only a single missing beam 
//   will be filled in. If more than one is missing, they will not be 
//   filled in. The elevation interpolation is done after the asimuth 
//   interpolation is complete.
// Type: boolean
//

bridge_missing_in_elevation = TRUE;

//======================================================================
//
// CHECK FOR MOVING ANTENNA.
//
//======================================================================
 
///////////// check_antenna_moving ////////////////////
//
// Option to check that the antenna is moving.
// If true, beams will only be stored if the antenna is moving. If the 
//   antenna stops, beams will be ignored.
// Type: boolean
//

check_antenna_moving = TRUE;

///////////// min_angle_change ////////////////////////
//
// Minimun angle change beam-to-beam (deg).
// For the antenna to be considered moving. the antenna much move by 
//   this amount from one beam to the next. The angle check is made in 
//   both azimuth and elevation.
// Type: double
//

min_angle_change = 0.05;

//======================================================================
//
// REMOVING TEST PULSE.
//
//======================================================================
 
///////////// remove_test_pulse ///////////////////////
//
// Option to remove the test pulse data.
// If true, the test pulse data will be removed from the end of the 
//   beam. The test pulse data generally lies in the last few gates in the 
//   beam. If true, the number of gates will be reduced by 
//   'ngates_test_pulse'.
// Type: boolean
//

remove_test_pulse = FALSE;

///////////// ngates_test_pulse ///////////////////////
//
// Number of gates to remove to get rid of test pulse.
// See 'remove_test_pulse'.
// Type: int
//

ngates_test_pulse = 20;

//======================================================================
//
// RADAR PARAMETERS.
//
//======================================================================
 
///////////// delta_az ////////////////////////////////
//
// Target delta azimuth (deg).
// The target spacing of the data beams in azimuth. NOTE: the lookup 
//   table is computed assuming that there is an exact number of beams per 
//   45-degree sector. If delta_az does not satisfy this requirement, it 
//   will be adjusted upwards to the next suitable value.
// Type: double
//

delta_az = 0.75;

///////////// az_correction ///////////////////////////
//
// Correction to angular azimuth values (deg).
// This correction is applied to the azimuth angles before computing the 
//   azimuth position.
// Type: double
//

az_correction = 0;

///////////// override_radar_location /////////////////
//
// Option to override radar location.
// If TRUE, the program will use location specified in the 
//   'radar_location' parameter.
// Type: boolean
//

override_radar_location = FALSE;

///////////// radar_location //////////////////////////
//
// Radar location if override is set true.
// The radar_location is only used if 'override_radar_location' is set 
//   true. Otherwise the information in the input data stream is used. 
//   Note that the altitude is in kilometers, not meters.
//
// Type: struct
//   typedef struct {
//      double latitude;
//      double longitude;
//      double altitude;
//   }
//
//

radar_location = { 0, 0, 0 };

///////////// override_beam_width /////////////////////
//
// Option to override radar beam width.
// If TRUE, the program will use beam width specified in the 
//   'beam_width' parameter.
// Type: boolean
//

override_beam_width = FALSE;

///////////// beam_width //////////////////////////////
//
// Radar beam width if override is set true.
// The beam width is only used if 'override_beam_width' is set true. 
//   Otherwise the information in the input data stream is used.
// Type: double
//

beam_width = 1;

///////////// radar_description ///////////////////////
//
// General description of radar.
// Used for data_set_info in MDV file.
// Type: string
//

radar_description = "SPOL RVP8";

//======================================================================
//
// FILTER DATA BASED ON GEOMETRY or PRF.
//
//======================================================================
 
///////////// filter_gate_spacing /////////////////////
//
// Option to filter data based on gate spacing.
// If TRUE, the program will use only beam data which matches the 
//   'keep_gate_spacing' parameter.
// Type: boolean
//

filter_gate_spacing = FALSE;

///////////// keep_gate_spacing ///////////////////////
//
// Desired radar gate spacing (km).
// The specified gate spacing is only used if 'filter_gate_spacing' is 
//   set true. Otherwise all gate spacings in the input data stream are 
//   used.
// Type: double
//

keep_gate_spacing = 0.25;

///////////// filter_start_range //////////////////////
//
// Option to filter data based on start range.
// If TRUE, the program will use only beam data which matches the 'keep 
//   _start_range' parameter.
// Type: boolean
//

filter_start_range = FALSE;

///////////// keep_start_range ////////////////////////
//
// Desired radar start range (km).
// The specified start range is only used if 'filter_start_range' is set 
//   true. Otherwise all start ranges in the input data stream are used.
// Type: double
//

keep_start_range = 0;

///////////// filter_prf //////////////////////////////
//
// Option to filter data based on PRF.
// If TRUE, the program will use only beam data with PRFs between the 
//   given limits.
// Type: boolean
//

filter_prf = FALSE;

///////////// min_prf /////////////////////////////////
//
// Minimum acceptable PRF (/s).
// See 'filter_prf'.
// Type: double
//

min_prf = 100;

///////////// max_prf /////////////////////////////////
//
// Maximum acceptable PRF (/s).
// See 'filter_prf'.
// Type: double
//

max_prf = 2000;

///////////// filter_elev /////////////////////////////
//
// Option to filter data based on elevation angle.
// If TRUE, the program will use only beam data with elevations between 
//   the given limits.
// Type: boolean
//

filter_elev = FALSE;

///////////// min_elev ////////////////////////////////
//
// Minimum valid elevation for beams (deg).
// If the elevation is below this value, the beam is ignored.
// Type: double
//

min_elev = -10;

///////////// max_elev ////////////////////////////////
//
// Maximum valid elevation for beams (deg).
// If the elevation is above this value, the beam is ignored.
// Type: double
//

max_elev = 90;

///////////// filter_antenna_transitions //////////////
//
// Option to filter data when the transition flag is set.
// If TRUE, the program will filter out beams which are computed when 
//   the antenna is moving from one tilt to the next, or one volume to the 
//   next.
// Type: boolean
//

filter_antenna_transitions = TRUE;

//======================================================================
//
// INTERPOLATION.
//
//======================================================================
 
///////////// min_nvalid_for_interp ///////////////////
//
// Minimum number of valid data points for theinterpolation.
// The program performs an 8-point linear interpolation. This is the 
//   number of valid data points, out of the possible 8, which must be 
//   present for interpolation to proceed. A high number will exclude 
//   marginal points. A low number will include marginal points.
// Minimum val: 1
// Maximum val: 8
// Type: int
//

min_nvalid_for_interp = 4;

//======================================================================
//
// OUTPUT FIELDS.
//
//======================================================================
 
///////////// output_compression //////////////////////
//
// Output compression options.
// The data may be optionally compressed for output. BZIP is generally 
//   the slowest but most compact. ZLIB uses the gzip compression 
//   algorithm, which is faster than BZIP, and for some data more compact 
//   as well. LZO is faster than BZIP and ZLIB, but not as compact. RLE is 
//   simple run-length encoding compression, which is the fastest and 
//   least compact.
//
// Type: enum
// Options:
//     NO_COMPRESSION
//     RLE_COMPRESSION
//     LZO_COMPRESSION
//     ZLIB_COMPRESSION
//     BZIP_COMPRESSION
//     GZIP_COMPRESSION
//

output_compression = ZLIB_COMPRESSION;

///////////// output_fields ///////////////////////////
//
// Array of output fields.
// The program will only output these fields. The dsr_name is the field 
//   name in the dsr data. If the output_name is an empty string, the 
//   output name will be set to the dsr_name. If output_name is non-empty, 
//   this will be used. Likewise for the units. Set the transform to dB, 
//   dBZ or none. Indicate the dBZ field by setting is_dbz to true. Set 
//   interp_db_as_power if you want to compute power from db before 
//   interpolating. Set is_vel for velocity field so that interpolation 
//   can take nyquist folding into account. If allow_interp is set to 
//   false, interpolation is not permitted on this field, and 
//   nearest-neighbor will be used instead. Set the output encoding type 
//   to select the resolution of the output data.
//
// Type: struct
//   typedef struct {
//      string dsr_name;
//      string output_name;
//      string output_units;
//      string transform;
//      boolean is_dbz;
//      boolean interp_db_as_power;
//      boolean is_vel;
//      boolean allow_interp;
//      encoding_t encoding;
//        Options:
//          ENCODING_INT8
//          ENCODING_INT16
//          ENCODING_FLOAT32
//   }
//
// 1D array - variable length.
//

output_fields = {
  { "DBZ", "DBZ", "dBZ", "dB", TRUE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBZ_F", "DBZ_F", "dBZ", "dB", TRUE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "VEL", "VEL", "m/s", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "VEL_F", "VEL_F", "m/s", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "WIDTH", "WIDTH", "m/s", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "WIDTH_F", "WIDTH_F", "m/s", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "ZDR", "ZDR", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "ZDR_F", "ZDR_F", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "ZDRM", "ZDRM", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "ZDRM_F", "ZDRM_F", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "LDRH", "LDRH", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "LDRH_F", "LDRH_F", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "LDRV", "LDRV", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "LDRV_F", "LDRV_F", "dB", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "RHOHV", "RHOHV", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "RHOHV_F", "RHOHV_F", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "PHIDP", "PHIDP", "deg", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "PHIDP_F", "PHIDP_F", "deg", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "KDP", "KDP", "deg/km", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "KDP_F", "KDP_F", "deg/km", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMHC", "DBMHC", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMHC_F", "DBMHC_F", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMHX", "DBMHX", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMHX_F", "DBMHX_F", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMVC", "DBMVC", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMVC_F", "DBMVC_F", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMVX", "DBMVX", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "DBMVX_F", "DBMVX_F", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRHC", "SNRHC", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRHC_F", "SNRHC_F", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRHX", "SNRHX", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRHX_F", "SNRHX_F", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRVC", "SNRVC", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRVC_F", "SNRVC_F", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRVX", "SNRVX", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "SNRVX_F", "SNRVX_F", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "NCP", "NCP", "", "", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "NCP_F", "NCP_F", "", "", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "CPA", "CPA", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "AIQ", "AIQ", "deg", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "NIQ", "NIQ", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "CLUT", "CLUT", "dB", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "SDEV_VV", "SDEV_VV", "dBm", "dB", FALSE, FALSE, FALSE, TRUE, ENCODING_INT16},
  { "CMD", "CMD", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "CMD_FLAG", "CMD_FLAG", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "TDBZ", "TDBZ", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "SPIN", "SPIN", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "ZDR_SDEV", "ZDR_SDEV", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8},
  { "PHIDP_SDEV", "PHIDP_SDEV", "none", "none", FALSE, FALSE, FALSE, TRUE, ENCODING_INT8}
};

///////////// output_coverage_field ///////////////////
//
// Option to output a field depicting radar coverage.
// If true, and extra field, with the name 'Coverage', is included in 
//   the output. This is a simple flag field, with a 1 indicating that the 
//   radar covers that pixel, and a 0 indicating that is does not.
// Type: boolean
//

output_coverage_field = FALSE;

///////////// override_missing_dbz_for_interp /////////
//
// Option to set dBZ values if they are missing.
// If true, missing dBZ values will be replaced by a low dbz value 
//   before interpolation takes place. If this is not done, non-missing 
//   dBZ values tend to be propagated into the missing areas, patricularly 
//   in the vertical dimension at long range where the vertical spacing 
//   between the beams is large. This leads to a ballooning of 
//   reflectivity from low heights.
// Type: boolean
//

override_missing_dbz_for_interp = FALSE;

///////////// override_nyquist ////////////////////////
//
// Option to override nyquist velocity in incoming data.
// If true, the nyquist_velocity parameter is used to specify the 
//   nyquist. If false, the nyquist is computed from the incoming radar 
//   data stream. The nyquist is used for velocity interpolation, to 
//   ensure that folded values are treated correctlty.
// Type: boolean
//

override_nyquist = FALSE;

///////////// nyquist_velocity ////////////////////////
//
// Specify nyquist velocity (m/s).
// See 'override_nyquist'.
// Type: double
//

nyquist_velocity = 25;

//======================================================================
//
// OUTPUT FILES.
//
//======================================================================
 
///////////// output_cart_files ///////////////////////
//
// Option to output files with Cartesian geometry.
// If true, the parameters in the cart_files array are used. The grid 
//   origin is at the radar. nxy is the number of grid points in x and y. 
//   dxy is the grid resolution in x and y. Therefore the grid is a square 
//   in x,y. nz is the number of CAPPI heights. minz is the height of the 
//   lowest CAPPI and dz is the height between successive CAPPIs. If 
//   interpolate is true, an 8-point linear interpolation grid 
//   transformation is performed. If interpolate is false, a 
//   nearest-neighbor transformation is performed. The MDV files are 
//   stored at mdv_url. The max_range parameter (km) can be used to limit 
//   the useful data range. Input data beyond this range is ignored. Set 
//   to a negative value to disable it, in which case no limit is placed 
//   on range.
// Type: boolean
//

output_cart_files = FALSE;

///////////// cart_files //////////////////////////////
//
// Details for files in cart geometry.
// Only active if 'output_cart_files' is true.
//
// Type: struct
//   typedef struct {
//      int nxy;
//      double dxy;
//      int nz;
//      double minz;
//      double dz;
//      boolean interpolate;
//      string mdv_url;
//      double max_range;
//   }
//
// 1D array - variable length.
//

cart_files = {
  { 600, 0.5, 25, 2, 0.5, TRUE, "$(DATA_DIR)/$(project)/mdv/cart/moments/sband", -1}
};

///////////// output_ppi_files ////////////////////////
//
// Option to output files with PPI geometry.
// If true, the parameters in the ppi_files array are used. The grid 
//   origin is at the radar. nxy is the number of grid points in x and y. 
//   dxy is the grid resolution in x and y. Therefore the grid is a square 
//   in x,y. min_elev is the lowest elevation angle to be stored, in 
//   degrees. Similarly for for max_elev. If interpolate is true, an 
//   8-point linear interpolation grid transformation is performed. If 
//   interpolate is false, a nearest-neighbor transformation is performed. 
//   The MDV files are stored at mdv_url. All gates with heights below 
//   min_ht or above max_ht (in km) will be set to missing. The max_range 
//   parameter (km) can be used to limit the useful data range. Input data 
//   beyond this range is ignored. Set to a negative value to disable it, 
//   in which case no limit is placed on range.
// Type: boolean
//

output_ppi_files = FALSE;

///////////// ppi_files ///////////////////////////////
//
// Details for files in ppi geometry.
// Only active if 'output_ppi_files' is true.
//
// Type: struct
//   typedef struct {
//      int nxy;
//      double dxy;
//      double min_elev;
//      double max_elev;
//      boolean interpolate;
//      string mdv_url;
//      double min_ht;
//      double max_ht;
//      double max_range;
//   }
//
// 1D array - variable length.
//

ppi_files = {
  { 400, 1, 0, 90, FALSE, "$(DATA_DIR)/$(project)/mdv/ppi/moments/sband", 0, 50, -1}
};

///////////// output_polar_files //////////////////////
//
// Option to output files with Polar radar geometry.
// If true, the parameters in the polar_files array are used. max_range 
//   is the maximum range to be stored, in km. min_elev is the lowest 
//   elevation angle to be stored, in degrees. Similarly for for max_elev. 
//   If interpolate is true, an 8-point linear interpolation grid 
//   transformation is performed. If interpolate is false, a 
//   nearest-neighbor transformation is performed. The MDV files are 
//   stored at mdv_url.
// Type: boolean
//

output_polar_files = TRUE;

///////////// polar_files /////////////////////////////
//
// Details for files in polar geometry.
// Only active if 'output_polar_files' is true.
//
// Type: struct
//   typedef struct {
//      double max_range;
//      double min_elev;
//      double max_elev;
//      string mdv_url;
//   }
//
// 1D array - variable length.
//

polar_files = {
  { 450, 0, 90, "$(DATA_DIR)/$(project)/mdv/radial/moments/cp"}
};

///////////// trim_polar_sectors //////////////////////
//
// Option to store only the sector in which there is data.
// This only applies to polar files. In the MDV file a sector may be 
//   stored as a full 360 or with only the beams in which there is data - 
//   the rest of the azimuths will be filled with missing values. If this 
//   is set TRUE, only the sector in which data is present will be stored.
// Type: boolean
//

trim_polar_sectors = FALSE;

//======================================================================
//
// SEPARATING SECTOR VOLUMES FROM SURVEILLANCE VOLUMES.
//
//======================================================================
 
///////////// separate_sector_files ///////////////////
//
// Option to separate the sector files from surveillance files.

// Sometimes a scan strategy will switch between sector scans and 
//   surveillance scans. In these cases, it can be useful to separate the 
//   sectors by storing them in different directories.

// If you set this option to true, the directory path for sectors will 
//   be determined by appending the 'sector_subdirectory' parameter to the 
//   paths of cart, ppi or polar files. Similarly, for surveillance scans, 
//   the parameter 'surveillance_subdirectory' will be appended to the 
//   paths.

// If the parameter 'use_input_scan_mode' is true, the scan mode will be 
//   used to determine which scans are sectors. If use_input_scan_mode is 
//   false, the number of beams will be computed as a fraction of the 
//   maximum number possible. If this fraction is greater than the 
//   parameter 'min_fraction_for_surveillance', the scan will be assumed 
//   to be a surveillance scan. Otherwise it will be assumed to be a 
//   sector scan.
// Type: boolean
//

separate_sector_files = FALSE;

///////////// sector_subdirectory /////////////////////
//
// The directory name for sector scan files.
// See 'separate_sector_files'. If a volume is a sector, this will be 
//   appended to the path for cart, ppi and polar files.
// Type: string
//

sector_subdirectory = "sec";

///////////// surveillance_subdirectory ///////////////
//
// The directory name for surveillance scan files.
// See 'separate_sector_files'. If a volume is a surveillance scan, this 
//   will be appended to the path for cart, ppi and polar files.
// Type: string
//

surveillance_subdirectory = "sur";

///////////// min_fraction_for_surveillance ///////////
//
// The min fraction of max beams for a surveillance scan.
// See 'separate_sector_files'. If the fraction of beams in the volume 
//   exceeds this min value, the volume will be considered a full 
//   revolution. Otherwise it will be considered a sector scan. Only 
//   active if 'use_input_scan_mode' is false.
// Type: double
//

min_fraction_for_surveillance = 0.8;

//======================================================================
//
// SEPARATE VERTICALLY-SCANNED VOLUMES.
//
//======================================================================
 
///////////// separate_vert_files /////////////////////
//
// Option to write vertically-pointing data files to a separate 
//   directory.
// This allows you to separate volumes of vertically-pointing data and 
//   save them to a separate directory. If the elevation angles in a 
//   volume are consistently above a specified value, the volume will be 
//   written to the specified directory. This only applies to polar data. 
//   If is ignored for cart and ppi output.
// Type: boolean
//

separate_vert_files = TRUE;

///////////// vert_subdirectory ///////////////////////
//
// The directory name for vertically-pointing volumes.
// See 'separate_vert_files'.
// Type: string
//

vert_subdirectory = "vert";

///////////// min_elevation_for_vert_files ////////////
//
// The min elevation angle for vertically-pointing operations (deg).
// This is the elevation threshold for vertically-pointing operations. 
//   If the specified fraction of the data has an elevation angle in 
//   excess of this angle, the volume will be considered to be from 
//   vertically-pointing operations.
// Type: double
//

min_elevation_for_vert_files = 85;

///////////// min_vert_fraction_for_vert_files ////////
//
// The min fraction of data with elevations in excess of the min 
//   elevation.
// If the fraction of the data with elevation angles above the specified 
//   min_elevation exceeds this fraction,  the volume will be considered 
//   to be from vertically-pointing operations.
// Type: double
//

min_vert_fraction_for_vert_files = 0.9;

//======================================================================
//
// RHI MODE - OPTION TO SAVE RHI DATA.
//
// If the program finds RHI data, it performs a histogram analysis to 
//   decide which radials are active and stores out the data in the MDV 
//   files as RHIs.
//
//======================================================================
 
///////////// output_rhi_files ////////////////////////
//
// Option to save RHIs if available.
// When creating RHI files, the elevation angles are stored in a regular 
//   grid while the azimuths are stored in the vlevels array.

// If the beams are indexed in elevation (i.e. are computed on a regular 
//   grid), the RHIs are saved out on that regular grid.

// If the beams are not indexed, the actual RHI elevation angles are 
//   resampled onto the regular grid. The oversampling ratio is computed 
//   as the number of elevation angles stored divided by the number of 
//   elevations measured. The higher the number the more accurate the 
//   elevation values. This step is necessary because the measured angles 
//   vary from one RHI to another, but all RHIs must be stored with the 
//   same elevation angles. Oversampling allows the program to interpolate 
//   the measured values onto the stored angles.

// The interpolation flag governs whether the RHI data is interpolated 
//   when it is put onto the regular elevation grid. If false, nearest 
//   neighbor is used.
// Type: boolean
//

output_rhi_files = TRUE;

///////////// rhi_files ///////////////////////////////
//
// Details for files in RHI geometry.
// Only active if 'output_rhi_files' is true.
//
// Type: struct
//   typedef struct {
//      double oversampling_ratio;
//      boolean interp_in_elevation;
//      string mdv_url;
//   }
//
// 1D array - variable length.
//

rhi_files = {
  { 4, FALSE, "$(DATA_DIR)/$(project)/mdv/radial/moments/sband/rhi"}
};

///////////// rhi_az_hist_resolution //////////////////
//
// Resolution of azimuth histogram (deg).
// For determining RHI azimuths. The azimuth data is binned at this 
//   resolution.
// Type: double
//

rhi_az_hist_resolution = 0.1;

///////////// rhi_az_hist_search_width ////////////////
//
// The width of the search in looking for peaks in the azimuth 
//   histogram.
// When looking for peaks in azimuth histogram, the program searches by 
//   this number of bins on either side of the search bin. For example, if 
//   the az_hist_resolution is 0.1 and the az_hist_search_width is 3, the 
//   program will search 3 bins, or 0.3 degrees, on either side of the 
//   search bin. It looks for a peak with values equal to or below the 
//   peak in the adjacent bins and less than the peak in bins further out.
// Minimum val: 1
// Type: int
//

rhi_az_hist_search_width = 3;

///////////// check_min_beams_in_rhi //////////////////
//
// Option to check the number of beams in an rhi.
// If TRUE, an rhi is only considered valid if the number of beams 
//   exceeds 'min_beams_in_rhi'.
// Type: boolean
//

check_min_beams_in_rhi = TRUE;

///////////// min_beams_in_rhi ////////////////////////
//
// The min number of beams for an rhi to be valid.
// See 'check_min_beams_in_rhi'.
// Type: int
//

min_beams_in_rhi = 20;

///////////// check_min_fraction_in_rhi ///////////////
//
// Option to check the fraction of beams in an rhi.
// If TRUE, an rhi is only considered valid if the number of beams in 
//   the rhi, expressed as a fraction of the max number of beams in any 
//   rhi, exceeds 'min_fraction_in_rhi'.
// Type: boolean
//

check_min_fraction_in_rhi = FALSE;

///////////// min_fraction_in_rhi /////////////////////
//
// The min fraction of max beams for an rhi to be valid.
// See 'check_min_fraction_in_rhi'.
// Type: double
//

min_fraction_in_rhi = 0.3;

//======================================================================
//
// REGISTERING MASTER LATEST_DATA_INFO FOR SEPARATED SCAN TYPES.
//
//======================================================================
 
///////////// write_master_ldata_info /////////////////
//
// Option to write a master latest_data_info for separated scan types.
// If the files for different scan types (surveillance, sector, rhi, 
//   vert etc.) are written to separate subdirectories, you have the 
//   option of registering the latest_data_info to a master location. This 
//   allows the system monitor to stay current, no matter which scan type 
//   is active.
// Type: boolean
//

write_master_ldata_info = FALSE;

///////////// master_ldata_info_url ///////////////////
//
// The URL for the master latest_data_info.
// See 'write_master_ldata_info'.
// Type: string
//

master_ldata_info_url = "$(DATA_DIR)/$(project)/mdv/radial/moments/sband";

//======================================================================
//
// OUTPUT FILE TIME-STAMP.
//
//======================================================================
 
///////////// auto_mid_time ///////////////////////////
//
// Option to automatically compute the volume mid time.
// If TRUE, the mid_time is the mean of the start and end times of the 
//   data in the volume. If FALSE, the mid time is computed as the end 
//   time minus 'age_at_end_of_volume'.
// Type: boolean
//

auto_mid_time = FALSE;

///////////// age_at_end_of_volume ////////////////////
//
// Specified age (secs) of the data relative to the data time at the end 
//   of the volume.
// Used if 'auto_mid_time' is FALSE.
// Type: int
//

age_at_end_of_volume = 0;

///////////// max_vol_duration ////////////////////////
//
// Maximum volume duration (secs).
// If a volume exceeds this duration it is not saved. This takes care of 
//   cases in which the radar data stops in the middle of a volume for 
//   some reason. Then the early data in the volume will not match the 
//   late data.
// Type: int
//

max_vol_duration = 1900;

//======================================================================
//
// OUTPUT DATA SET INFORMATION.
//
//======================================================================
 
///////////// data_set_info ///////////////////////////
//
// Data set info.
// This is placed in the MDV master header for documentation purposes.
// Type: string
//

data_set_info = "This MDV radar volume file was created by Dsr2Vol.";

///////////// data_set_source /////////////////////////
//
// Data set source details.
// This is placed in the MDV master header for documentation purposes.
// Type: string
//

data_set_source = "SPOL, Sigmet IQ data.";

//======================================================================
//
// AUTOMATIC END-OF-VOLUME DETECTION.
//
// These parameters are used if end_of_volume_decision is set to 
//   AUTOMATIC. This assumes a simple bottom-up or top-down scan strategy. 
//   No attempt will be made to search for RHIs, or other complicattions 
//   in the SCAN strategy.
//
//======================================================================
 
///////////// set_end_of_vol_from_elev_change /////////
//
// Option to set the end of vol flag based on change in elevation angle.
// If true, the program will look for changes in elevation angle to 
//   compute the end of volume. Only this test, and the test for prf 
//   change, will be used to identify the end of volume condition.
// Type: boolean
//

set_end_of_vol_from_elev_change = FALSE;

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

///////////// set_end_of_vol_on_prf_change ////////////
//
// Option to set the end-of-vol flag when the PRF changes.
// Type: boolean
//

set_end_of_vol_on_prf_change = FALSE;

///////////// nbeams_history //////////////////////////
//
// Number of beams in history list.
// This is the number of beams stored in the history list. The list is 
//   used for determining the status of the antenna. The antenna algorithm 
//   checks o see if either the elevation angle is stable (PPI mode) or 
//   the azimuth angle is stable (RHI mode). The el_accuracy and 
//   az_accuracy parameters are used to detect whether el or az are 
//   stable.
// Type: int
//

nbeams_history = 16;

///////////// el_accuracy /////////////////////////////
//
// Accuracy of antenna controller in elevation (deg).
// Used to determine if antenna is stationary in elevation, i.e. is it 
//   in PPI mode? If the cumulative elevation change during the history 
//   period is less than this value, the antenna is assumed to be in PPI 
//   mode.
// Type: double
//

el_accuracy = 0.25;

///////////// az_accuracy /////////////////////////////
//
// Accuracy of antenna controller in azimuth (deg).
// Used to determine if antenna is stationary in azimuth, i.e. is it in 
//   RHI mode? If the cumulative azimuth change during the history period 
//   is less than this value, the antenna is assumed to be in RHI mode.
// Type: double
//

az_accuracy = 0.25;

///////////// min_az_change_ppi ///////////////////////
//
// Min azimuth change for PPI (deg).
// For a valid PPI, the azimuth must change by at least this amount 
//   during nbeams_history, while the elevation is not changing.
// Type: double
//

min_az_change_ppi = 4;

///////////// min_el_change_rhi ///////////////////////
//
// Min elevation change for RHI (deg).
// For a valid RHI, the elevation must change by at least this amount 
//   during nbeams_history, while the azimuth is not changing.
// Type: double
//

min_el_change_rhi = 4;

///////////// max_az_change_per_tilt //////////////////
//
// Maximum azimuth change per tilt (deg).
// If the tilt elevation has not changed by the time the azimuth has 
//   changed by this number of degrees, an end-of-volume condition is 
//   triggered. This is used to handle the single-elevation surveillance 
//   case in which the antenna scans in PPI at a single elevation angle.
// Type: int
//

max_az_change_per_tilt = 540;

///////////// min_beams_per_ppi_vol ///////////////////
//
// Min number of beams per PPI volume.
// Used to prevent end-of-volume conditions being determined during 
//   antenna transition to the start of the next volume.
// Type: int
//

min_beams_per_ppi_vol = 180;

///////////// min_beams_per_rhi_vol ///////////////////
//
// Min number of beams per RHI volume.
// Used to prevent end-of-volume conditions being determined during 
//   antenna transition to the start of the next volume.
// Type: int
//

min_beams_per_rhi_vol = 30;

///////////// debug_auto_detection ////////////////////
//
// Flag for debugging auto end-of-vol detection.
// If set, messages will be printed to stderr on how the auto-detection 
//   algorithm is making decisions.
// Type: boolean
//

debug_auto_detection = FALSE;

