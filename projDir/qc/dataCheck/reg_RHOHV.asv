% Plot rhohv bias against velocity

clear all
close all

addpath(genpath('~/git/lrose-projects-precip/projDir/qc/'));

indir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qcr/moments/sband/uncorrected/sur/20220608/';
infile='cfrad.20220608_000050.529_to_20220608_000650.301_SPOL_PrecipSur1_SUR.nc';

figdir='/scr/cirrus3/rsfdata/projects/precip/grids/spol/radarPolar/qc2/rate/plots/RHOHVvsVEL/';

% data.RHOHV_TEST_FILT=[];
% 
% data=read_spol([indir,infile],data);

rhoHVtruth=ncread([indir,infile],'RHOHV_TEST_FILT');
rhoHVmom=ncread([indir,infile],'RHOHV_NNC_F');
regOrder=ncread([indir,infile],'REGR_FILT_POLY_ORDER');
vel=ncread([indir,infile],'VEL_F');

rhoBias=rhoHVtruth-rhoHVmom;

orderEdges=0:5:25;
velEdges=-50:1:50;
velX=velEdges(1:end-1)-(velEdges(end)-velEdges(end-1))/2;

biasOut=nan(length(velEdges)-1,length(orderEdges)-1);
orderLeg={};

figure('Position',[200 500 600 600],'DefaultAxesFontSize',12);
hold on

for ii=1:length(orderEdges)-1   
    for jj=1:length(velEdges)-1
        goodInds=find(regOrder>=orderEdges(ii) & regOrder<orderEdges(ii+1) & vel>=velEdges(jj) & vel<velEdges(jj+1));
        thisBias=rhoBias(goodInds);
        biasOut(jj,ii)=mean(thisBias,'omitmissing');
    end
    plot(velX,biasOut(:,ii),'LineWidth',1.5);
    orderLeg=[orderLeg,{[num2str(orderEdges(ii)),'-',num2str(orderEdges(ii+1))]}];
end

xlim([-max(abs([min(vel),max(vel)])),max(abs([min(vel),max(vel)]))]);
grid on
box on

xlabel('Velocity (m/s)');
ylabel('\rho_{HV} bias');
leg=legend(orderLeg,'Location','northoutside','Orientation','horizontal');
leg.ItemTokenSize=[15,9];
title(leg,'Orders:')

print([figdir,'rhoBiasVSvel.png'],'-dpng','-r0');