%Calculates attenuation per kilometer after ITU method. It is only valid
%for altitudes up to ~10km and for radar frequencies between 1GHz and 350
%GHz. The naming conventions follow the reference below and the equations
%have been split up into sub terms.

%Radiocommunication Sector of International Telecommunication Union. 
%Recommendation ITU-R P.676-10: Attenuation by atmospheric gases 2013.

%Author: Ulrike Romatschke romatsch@ucar.edu
%Last modified: 20170106

%Input:
%f is the radar freqyency in GHz
%ptot is the pressure in mb
%t is the temperature in C
%rh is the relative humidity in %
%es is the saturation pressure

%Output:
%gamma is the total attenuation
%gamma0 is the dry attenuation
%gammaW is he wet attenuation

function [gamma, gamma0, gammaW]= f_atten_ITUR(f,ptot,t,rh,es)

gamma=[];
gamma0=[];
gammaW=[];

%calculate absolute humidity rho from relative humidity rh
rho=(es.*rh.*2.167)./(273.15+t); %water vapour density in g/m^3 (absolute humidity)

rp = ptot./1013;
rt = 288./(273+t);

%calculate dry attenuation
a60=0.9003;
b60=4.1335;
c60=0.0427;
d60=1.6088;

a62=0.9886;
b62=3.4176;
c62=0.1827;
d62=1.3429;

gamma60=15.*rp.^a60.*rt.^b60.*exp(c60.*(1-rp)+d60.*(1-rt));
gamma62=14.28.*rp.^a62.*rt.^b62.*exp(c62.*(1-rp)+d62.*(1-rt));

if f<=54
    a1=0.0717;
    b1=-1.8132;
    c1=0.0156;
    d1=-1.6515;
    
    a2=0.5146;
    b2=-4.6368;
    c2=-0.1921;
    d2=-5.7416;
    
    a3=0.3414;
    b3=-6.5851;
    c3=0.213;
    d3=-8.5854;
    
    xi1 = rp.^a1.*rt.^b1.*exp(c1.*(1-rp)+d1.*(1-rt));
    xi2 = rp.^a2.*rt.^b2.*exp(c2.*(1-rp)+d2.*(1-rt));
    xi3 = rp.^a3.*rt.^b3.*exp(c3.*(1-rp)+d3.*(1-rt));
    
    A1=(7.2.*rt.^2.8)./(f^2+0.34.*rp.^2.*rt.^1.6);
    A2=(0.62.*xi3)./((54-f).^(1.16.*xi1)+0.83.*xi2);
    A3=f^2.*rp.^2.*10^(-3);
    
    gamma0=(A1+A2).*A3;
    
elseif f>54 & f<=60
    a54=1.8286;
    b54=-1.9487;
    c54=0.4051;
    d54=-2.8509;
    
    a58=1.0045;
    b58=3.561;
    c58=0.1588;
    d58=1.2834;
    
    gamma54=2.192.*rp.^a54.*rt.^b54.*exp(c54.*(1-rp)+d54.*(1-rt));
    gamma58=12.59.*rp.^a58.*rt.^b58.*exp(c58.*(1-rp)+d58.*(1-rt));
        
    B1=log(gamma54)./24.*(f-58).*(f-60);
    B2=log(gamma58)./8.*(f-54).*(f-60);
    B3=log(gamma60)./12.*(f-54).*(f-58);
    
    gamma0=exp(B1-B2+B3);
    
elseif f>60 & f<=62
    
    gamma0=gamma60+(gamma62-gamma60).*(f-60)./2;
    
elseif f>62 & f<=66
    a64=1.432;
    b64=0.6258;
    c64=0.3177;
    d64=-0.5914;
    
    a66=2.0717;
    b66=-4.1404;
    c66=0.491;
    d66=-4.8718;
    
    gamma64=6.819.*rp.^a64.*rt.^b64.*exp(c64.*(1-rp)+d64.*(1-rt));
    gamma66=1.908.*rp.^a66.*rt.^b66.*exp(c66.*(1-rp)+d66.*(1-rt));
    
    C1=log(gamma62)./8.*(f-64).*(f-66);
    C2=log(gamma64)./4.*(f-62).*(f-66);
    C3=log(gamma66)./8.*(f-62).*(f-64);
    
    gamma0=exp(C1-C2+C3);
    
elseif f>66 & f<=120
    a4=-0.0112;
    b4=0.0092;
    c4=-0.1033;
    d4=-0.0009;
    
    a5=0.2705;
    b5=-2.7192;
    c5=-0.3016;
    d5=-4.1033;
    
    a6=0.2445;
    b6=-5.9191;
    c6=0.0422;
    d6=-8.0719;
    
    a7=-0.1833;
    b7=6.5589;
    c7=-0.2402;
    d7=6.131;
    
    xi4 = rp.^a4.*rt.^b4.*exp(c4.*(1-rp)+d4.*(1-rt));
    xi5 = rp.^a5.*rt.^b5.*exp(c5.*(1-rp)+d5.*(1-rt));
    xi6 = rp.^a6.*rt.^b6.*exp(c6.*(1-rp)+d6.*(1-rt));
    xi7 = rp.^a7.*rt.^b7.*exp(c7.*(1-rp)+d7.*(1-rt));
    
    D1=3.02.*10.^(-4).*rt.^3.5;
    D2=(0.283.*rt.^3.8)./((f-118.75).^2+2.91.*rp.^2.*rt.^1.6);
    D3=(0.502.*xi6.*(1-0.0163.*xi7.*(f-66)))./((f-66).^(1.4346.*xi4)+1.15.*xi5);
    D4=f.^2.*rp.^2.*10.^(-3);
    
    gamma0=(D1+D2+D3).*D4;
    
elseif f>120 & f<=350
    adelta=3.211;
    bdelta=-14.94;
    cdelta=1.583;
    ddelta=-16.37;
    
    delta=-0.00306.*rp.^adelta.*rt.^bdelta.*exp(cdelta.*(1-rp)+ddelta.*(1-rt));
    
    E1=3.02.*10.^(-4)./(1+1.9.*10.^(-5).*f.^1.5);
    E2=0.283.*rt.^0.3./((f-118.75).^2+2.91.*rp.^2.*rt.^1.6);
    E3=f.^2.*rp.^2.*rt.^3.5.*10.^(-3);
    
    gamma0=(E1+E2).*E3+delta;
else
    disp('Frequency must be <=350 GHz.');
    return;
end

fi1=22;
fi2=557;
fi3=752;
fi4=1780;

g1=1+((f-fi1)./(f+fi1)).^2;
g2=1+((f-fi2)./(f+fi2)).^2;
g3=1+((f-fi3)./(f+fi3)).^2;
g4=1+((f-fi4)./(f+fi4)).^2;

eta1=0.955.*rp.*rt.^0.68+0.006.*rho;

eta2=0.735.*rp.*rt.^0.5+0.0353.*rt.^4.*rho;

F=(3.98.*eta1.*exp(2.23.*(1-rt)))./((f-22.235).^2+9.42.*eta1.^2).*g1;
G=(11.96.*eta1.*exp(0.7.*(1-rt)))./((f-183.31).^2+11.14.*eta1.^2);
H=(0.081.*eta1.*exp(6.44.*(1-rt)))./((f-321.226).^2+6.29.*eta1.^2);
I=(3.66.*eta1.*exp(1.6.*(1-rt)))./((f-325.153).^2+9.22.*eta1.^2);
J=(25.37.*eta1.*exp(1.09.*(1-rt)))./(f-380).^2;
K=(17.4.*eta1.*exp(1.46.*(1-rt)))./(f-448).^2;
L=(844.6.*eta1.*exp(0.17.*(1-rt)))./(f-557).^2.*g2;
M=(290.*eta1.*exp(0.41.*(1-rt)))./(f-752).^2.*g3;
N=(8.3328.*10.^4.*eta2.*exp(0.99.*(1-rt)))./(f-1780).^2.*g4;
O=f.^2.*rt.^2.5.*rho.*10.^(-4);

gammaW=(F+G+H+I+J+K+L+M+N).*O;

gamma=gamma0+gammaW;
