#! /bin/csh

#
# Start virtual X server for display number specified as command line arg 1
# arg 1 should be something like 1000
#
# Choose a high display number so that the port does not
# conflict with an ssh session.

if( $#argv != 1 ) then
     echo "Usage: start_Xvfb.qc displayNum"
     echo " e.g.: start_Xvfb.qc 1000"
     exit 1
endif

set displayNum = ":$1.0"

running "Xvfb ${displayNum}"
if ($status == 1) then
    echo "starting Xvfb on displayNum: $displayNum"
    Xvfb ${displayNum} -screen 0 2000x2000x24 -pixdepths 24 -ld 100000 -ls 10000 \
	>& /dev/null &
else
    echo "Xvfb already running on display $displayNum"
endif

# set the font path

setenv DISPLAY ${displayNum}
set_font_path >& /dev/null
xrdb -display $DISPLAY $PROJ_DIR/display/params/XResources4CIDD
