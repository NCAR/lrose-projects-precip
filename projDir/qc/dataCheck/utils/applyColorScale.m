function applyColorScale(h,fld,color_map,limits)

col_def1 = nan(size(fld));
col_def2 = nan(size(fld));
col_def3 = nan(size(fld));
for ii=1:size(color_map,1)
    col_ind=find(fld>limits(ii) & fld<=limits(ii+1));
    col_def1(col_ind)=color_map(ii,1);
    col_def2(col_ind)=color_map(ii,2);
    col_def3(col_ind)=color_map(ii,3);
end
if ~isequal(size(col_def1),(size(fld)))
    col_def=cat(3,col_def1',col_def2',col_def3');
else
    col_def=cat(3,col_def1,col_def2,col_def3);
end
h.CData=col_def;

hcb=colorbar;
colormap(gca,color_map);
caxis([0 size(color_map,1)]);
caxis_yticks=(1:1:size(color_map,1)-1);
caxis_ytick_labels=num2str(limits(2:end-1)');
while length(caxis_yticks)>30
    caxis_yticks=caxis_yticks(1:2:end);
    caxis_ytick_labels=caxis_ytick_labels((1:2:end),:);
end
set(hcb,'ytick',caxis_yticks);
set(hcb,'YTickLabel',caxis_ytick_labels);