%Default colormap for reflectivity values

function x = temp_default(n);


if nargin==1 & isempty(n)
    n = size(get(gcf,'Colormap'),1);
end;

cmap = [...
    0   0   0
    47  79  79
    135 206 255
    0 191 255
    123 104 238
    106  90 205
    0   0 139
    93  71 139
    104  34 139
    122  55 139
    191  62 255
    155  48 255
    255 105 180
    255 192 203
    104  34 139
    39  64 139
    190 190 190
    0 238 118
    0 205 102
    0 139	 69
    255 255	  0
    205 205	  0
    255 215	  0
    255 185	 15
    255 165	  0
    255 130	 71
    255 114	 86
    255 0   0
    ];

cmap=cmap./255;

if nargin < 1
    n = size(cmap,1);
end;

x = interp1(linspace(0,1,size(cmap,1)),cmap(:,1),linspace(0,1,n)','linear');
x(:,2) = interp1(linspace(0,1,size(cmap,1)),cmap(:,2),linspace(0,1,n)','linear');
x(:,3) = interp1(linspace(0,1,size(cmap,1)),cmap(:,3),linspace(0,1,n)','linear');

x = min(x,1);
x = max(x,0);