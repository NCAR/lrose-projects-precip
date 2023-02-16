% Test utils files

clear all
close all

%% S-Pol

indir='/scr/hail1/rsfdata/projects/eolbase/cfradial/spol/moments/spoldrx/sur/20190313/';
infile='cfrad.20190313_191338.302_to_20190313_192125.250_SPOL_SurKa_SUR.nc';

loadfile=[indir infile];

data.DBZ=[];

dataIn=read_spol(loadfile,data);

%% HCR
indir='/scr/snow2/rsfdata/projects/socrates/hcr/qc/cfradial/velcorr/10hz/20180123/';
%indir='/scr/snow2/rsfdata/projects/socrates/hcr/qc/cfradial/moments/10hz/20180123/';
infile='cfrad.20180123_015000.100_to_20180123_015500.000_HCR_VER.nc';

loadfile=[indir infile];

data.VEL_CORR=[];

data=read_HCR(loadfile,data);

asl=-1*((data.range.*cosd(abs(data.elev)-90)./1000)-data.alt./1000);

fig2=surf(data.time,asl,data.VEL_CORR);
fig2.EdgeColor='none';
view(2)
ylim=([0 6]);
hcb=colorbar;