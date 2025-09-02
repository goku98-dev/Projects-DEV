 function [ A ] = ComputeAdjacencyMatrix( ProteinLabelPairs )
  

% Adjacency Matrix had ( n * n ) dim : 
RowsandColumns = size(ProteinLabelPairs);
    for RowNumber = 1 : RowsandColumns
        i = ProteinLabelPairs(RowNumber, 1);
        j = ProteinLabelPairs(RowNumber, 2);
        A(i,j) = 1;
        A(j,i) = 1;
        A(i,i) = 0;
        
    end;

