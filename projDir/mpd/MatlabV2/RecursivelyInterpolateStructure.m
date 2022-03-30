% Written by: Robert Stillwell 
% Written for: NCAR
% Modificication Info: Created February 13, 2018

function [ReturnDataStructure] = RecursivelyInterpolateStructure(OriginalDataStructure,OldTime,NewTime,Method,Extraoplation)
%
%
%
%
%% Converting the surface weather structure into a cell array
[Cell, FieldNames] = RecursiveStruct2Cell(OriginalDataStructure);
%% Recursively performing an interpolation of the cell contents
CellDataNew = RecursiveInterpolateData(Cell,OldTime,NewTime,Method,Extraoplation);
%% Convert the surface weather cell array back to a structure
ReturnDataStructure = RecursiveCell2Struct(CellDataNew, FieldNames);

end

% This subfunction converts all cell array elements with a pervious name
% back to a strucutre
function [Struct] = RecursiveCell2Struct(Cell,FieldNames)
%                     
% Inputs: Cell:       
%         FieldNames: 
%                     
% Outputs: Struct:    
%                     
%% Recursively converting cell to strucutre
for m=1:1:size(Cell,1)
    if iscell(Cell{m,1})
        % Need to dive down further into the cell array to convert
        % sub-cells to sub-structures
        if size(FieldNames,2) == 2
            Temp = RecursiveCell2Struct(Cell{m,1},FieldNames{m,2});
            Cell{m,1} = Temp;
        end
    end
   FieldNames2{m,1} = FieldNames{m,1}; 
end
Struct = cell2struct(Cell,FieldNames2);
end

% This function performs interpolation on all elements in a cell array
% recursively
function [CellDataNew] = RecursiveInterpolateData(CellData, OldTime, NewTime, Method, Extraoplation) 
%                        
% Inputs: CellData:      
%         OldTime:       
%         NewTime:       
%         Method:        The method of interpolation. Inputs should be the
%                        same as those for the interp1 function
%         Extrapolation: The method of extrapolation. Inputs should be the
%                        same as those for the interp1 function
%                        
% Outputs: CellDataNew:  
%                        
%% Recursively interpolating data contained within the cell array
for m=1:1:size(CellData,1)
   if iscell(CellData{m,1}) 
       % Need to dive down further into the cell array
       Temp = RecursiveInterpolateData(CellData{m,1},OldTime,NewTime,Method,Extraoplation);
       CellDataNew{m,1} = Temp;                       %#ok<*AGROW>
   else
       % At the bottom of the cell tree so interpolate if it is not just a
       % single number
       if size(OldTime) == size(CellData{m,1})
%            CellDataNew{m,1} = interp1(OldTime,CellData{m,1},NewTime,Method,Extraoplation);
           CellDataNew{m,1} = interp1(OldTime,CellData{m,1},NewTime,Method);
       else
           CellDataNew{m,1} = CellData{m,1};
       end
   end
end
end

% This function converts a named structure to a cell array to allow for a
% later function to loop over the cell elements 
function [Cell,FieldNames] = RecursiveStruct2Cell(Struct)
%                      
% Inputs: Struct:      
%                      
% Outputs: Cell:       
%          FieldNames: 
%                      
%% Converting structure to a cell array
Cell       = struct2cell(Struct);
FieldNames = fieldnames(Struct);

%% Recursively checking if sub-cells should also be converted
for m=1:1:size(Cell,1)
    if isstruct(Cell{m,1})
        % Need to dive down further into the structure to convert
        % sub-strucutres to sub-cells
        [Temp1,Temp2]   = RecursiveStruct2Cell(Cell{m,1});
        Cell{m,1}       = Temp1;
        FieldNames{m,2} = Temp2;
    end
end
end