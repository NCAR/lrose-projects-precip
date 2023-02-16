%Default colormap for reflectivity values

function x = backscat_default(n);


if nargin==1 & isempty(n)
    n = size(get(gcf,'Colormap'),1);
end;

cmap = [...
    0         0    0.6667
    0         0    0.8333
    0         0    1.0000
    0    0.1667    1.0000
    0    0.3333    1.0000
    0    0.5000    1.0000
    0    0.6667    1.0000
    0    0.8333    1.0000
    0    1.0000    1.0000
    0.1667    1.0000    0.8333
    0.3333    1.0000    0.6667
    0.5000    1.0000    0.5000
    0.6667    1.0000    0.3333
    0.8333    1.0000    0.1667
    1.0000    1.0000         0
    1.0000    0.8333         0
    1.0000    0.6667         0
    1.0000    0.5000         0
    1.0000    0.3333         0
    1.0000    0.1667         0
    1.0000         0         0
    0.8333         0         0
    ];

if nargin < 1
    n = size(cmap,1);
end;

x = interp1(linspace(0,1,size(cmap,1)),cmap(:,1),linspace(0,1,n)','linear');
x(:,2) = interp1(linspace(0,1,size(cmap,1)),cmap(:,2),linspace(0,1,n)','linear');
x(:,3) = interp1(linspace(0,1,size(cmap,1)),cmap(:,3),linspace(0,1,n)','linear');

x = min(x,1);
x = max(x,0);