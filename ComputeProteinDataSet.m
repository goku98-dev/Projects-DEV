function [ProteinLabel, ProteinLabelPairs, A, N, NumInteractionProtein, MaxNumInteractionProtein, IndicesInteractionProtein] = ComputeProteinDataSet(ProteinType)

% create ProteinLables: assign integers, starting from 1, to the distinct protein names 
LengthofProteinType = length(ProteinType);
ProteintLabelIndex = 1;
ProteinLabel(ProteintLabelIndex) = ProteinType(1,1);

Flag = 0;
for RowNumber = 1 : LengthofProteinType
    RowNumber;
    for ColumnNumber = 1 : 2
        ColumnNumber;
        CurrentProteinLabel = 1;
        Flag = 0;
        while (CurrentProteinLabel <= ProteintLabelIndex) && (Flag == 0)
            CurrentProteinLabel;
              
               if(strcmp(ProteinType(RowNumber, ColumnNumber), ProteinLabel(CurrentProteinLabel))==1)
                Flag = 1;
            else
                CurrentProteinLabel = CurrentProteinLabel + 1;
            end;
        end;
        if(Flag == 0)
           ProteintLabelIndex = ProteintLabelIndex + 1;
           ProteinLabel(ProteintLabelIndex) = ProteinType(RowNumber,ColumnNumber);
        end;
    end;
end;

%CreateProteinLabelPairs 
LengthofProteinLabel = length(ProteinLabel);

for RowNumber = 1 : LengthofProteinType          
    for ColumnNumber = 1 : 2
        CurrentProteinLabel = 1;
        Flag = 0;
        while (CurrentProteinLabel <= LengthofProteinLabel) && (Flag == 0)           
             if(strcmp(ProteinType(RowNumber, ColumnNumber), ProteinLabel(CurrentProteinLabel))==1)
                 Flag = 1;
                 ProteinLabelPairs(RowNumber, ColumnNumber) = CurrentProteinLabel;
             else
                 CurrentProteinLabel = CurrentProteinLabel + 1;
            end;        
        end;
    end;
end;

% Adjacency Matrix A 
[A] = ComputeAdjacencyMatrix(ProteinLabelPairs);
    
% Compute the Number of Interaction Protein 

N = length(A);
[NumInteractionProtein] = ComputeNumInteractionProtein(A, N);

% Compute Max Number of Interaction Protein 

MaxNumInteractionProtein = max(NumInteractionProtein);

% Compute Indices Intercation Protein 

[IndicesInteractionProtein] = ComputeIndicesInteractionProtein(A, N);