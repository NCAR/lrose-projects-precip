%Calculates attenuation per kilometer after the Liebe method. 
%The naming conventions follow the reference below and the equations
%have been split up into sub terms.

%Liebe, H. J. (1985), An updated model for millimeter wave propagation in moist air, 
%Radio Sci., 20, 1069–1089

%Author: Ulrike Romatschke romatsch@ucar.edu
%Last modified: 20170106

%Input:
%f is the radar freqyency in GHz
%layer_p is the pressure in mb
%layer_t is the temperature in C
%layer_es is the saturation pressure
%layer_rh is the relative humidity in %

%Output:
%gamma is the total attenuation
%gamma0 is the dry attenuation
%gammaW is he wet attenuation

function [spAlpha]= f_atten_Liebe(f,layer_p,layer_t,layer_es,layer_rh)
%Calculate attenuation after Liebe 1985 method

spAlpha=[];

if f>1000
    disp('Frequency must be <=1000GHz.');
    return;
end

%Files with O2 and H2O line data
O2file='linesLiebe/linesO2.dat';
H2Ofile='linesLiebe/linesH2O.dat';

dataO2=importdata(O2file,' ');

dataH2O=importdata(H2Ofile,' ');

TallIn=layer_t+273.15; %temperature in Kelvin
PallIn=layer_p./10; %pressure in kPa
EallIn=layer_es./10.*layer_rh./100;

thetaAllIn=300./TallIn;

spAlpha=zeros(size(layer_p));

for jj=1:size(TallIn,2)
    Tall=TallIn(:,jj);
    Pall=PallIn(:,jj);
    Eall=EallIn(:,jj);
    thetaAll=thetaAllIn(:,jj);
    
    Po2=repmat(Pall,1,1,size(dataO2,1));
    Ph2o=repmat(Pall,1,1,size(dataH2O,1));
    Eo2=repmat(Eall,1,1,size(dataO2,1));
    Eh2o=repmat(Eall,1,1,size(dataH2O,1));
    thetao2=repmat(thetaAll,1,1,size(dataO2,1));
    thetah2o=repmat(thetaAll,1,1,size(dataH2O,1));
    
    dataO2_3d={};
    for ii=1:size(dataO2,2)
        dataO2_2d=repmat(dataO2(:,ii),1,size(Po2,1));
        dataO2_3d_1=repmat(dataO2_2d,1,1,size(Po2,2));
        dataO2_3d{end+1}=permute(dataO2_3d_1,[2,3,1]);
    end
    
    dataH2O_3d={};
    for ii=1:size(dataH2O,2)
        dataH2O_2d=repmat(dataH2O(:,ii),1,size(Ph2o,1));
        dataH2O_3d_1=repmat(dataH2O_2d,1,1,size(Ph2o,2));
        dataH2O_3d{end+1}=permute(dataH2O_3d_1,[2,3,1]);
    end
    
    SO2=dataO2_3d{2}.*Po2.*thetao2.^3.*exp(dataO2_3d{3}.*(1-thetao2));
    SH2O=dataH2O_3d{2}.*Eh2o.*thetah2o.^3.5.*exp(dataH2O_3d{3}.*(1-thetah2o));
    
    gammaO2=dataO2_3d{4}.*(Po2.*thetao2.^(0.8-dataO2_3d{5})+1.1.*Eo2.*thetao2);
    gammaH2O=dataH2O_3d{4}.*(Ph2o.*thetah2o.^0.8+4.8.*Eh2o.*thetah2o);
    
    deltaO2=dataO2_3d{6}.*Po2.*thetao2.^dataO2_3d{7};
    
    XO2=(dataO2_3d{1}-f).^2+gammaO2.^2;
    XH2O=(dataH2O_3d{1}-f).^2+gammaH2O.^2;
    
    YO2=(dataO2_3d{1}+f).^2+gammaO2.^2;
    YH2O=(dataH2O_3d{1}+f).^2+gammaH2O.^2;
    
    SFO2=SO2.*f./dataO2_3d{1}.*(gammaO2.*(1./XO2+1./YO2)-deltaO2.*((dataO2_3d{1}-f)./XO2+(dataO2_3d{1}+f)./YO2));
    SFH2O=SH2O.*f./dataH2O_3d{1}.*gammaH2O.*(1./XH2O+1./YH2O);
    
    gamma0=5.6.*10.^(-3).*(Pall+1.1.*Eall).*thetaAll.^0.8;
    
    Np=(2.*3.07.*10.^(-4)...
        .*(gamma0.*(1+(f./gamma0).^2).*(1+(f./60).^2)).^(-1)...
        +1.4.*(1-1.2.*f.^1.5.*10.^(-5)).*10.^(-10).*Pall.*thetaAll.^2.5).*f.*Pall.*thetaAll.^2;
    
    Ne=(1.4.*10^(-6).*Pall+5.41.*10.^(-5).*Eall.*thetaAll.^3).*f.*Eall.*thetaAll.^2.5;
    
    Nw=0;%We assume no liquid water content
    
    N=sum(SFO2,3,'omitnan')+Np+sum(SFH2O,3,'omitnan')+Ne+Nw;
    
    spAlpha(:,jj)=0.1820.*f.*N;
end
end