% Step 1: Load interaction file
filename = 'Collins PPI Dataset.txt';  % <-- change this to your file name
fid = fopen(filename);
C = textscan(fid, '%s %s');  % Read two columns of strings
fclose(fid);



% Step 2: Combine all proteins from both columns
allProteins = [C{1}; C{2}];




% Step 3: Get unique protein names
[uniqueProteins, ~, ic] = unique(allProteins);




% Step 4: Assign ProteinLabels
ProteinLabel = uniqueProteins;  % Cell array, index is ID, value is label




% Step 5 (optional): Create map from label to ID
ProteinIDMap = containers.Map(ProteinLabel, 1:length(ProteinLabel));

ProteinIDTable = table(keys(ProteinIDMap)', cell2mat(values(ProteinIDMap))', ...
                       'VariableNames', {'ProteinLabel', 'ProteinID'});




% Step 6: Convert original interactions to numeric ID pairs
numPairs = length(C{1});
ProteinLabelPairs = zeros(numPairs, 2);

for i = 1:numPairs
    ProteinLabelPairs(i, 1) = ProteinIDMap(C{1}{i});
    ProteinLabelPairs(i, 2) = ProteinIDMap(C{2}{i});
end

ProteinLabel = ProteinLabel.';




% Step 7: Count interactions per protein
numProteins = length(ProteinLabel);  % total number of proteins
NumInteractionProtein = zeros(1, numProteins);  % preallocate
N = length(ProteinLabel); % total number of proteins

for i = 1:size(ProteinLabelPairs, 1)
    p1 = ProteinLabelPairs(i, 1);
    p2 = ProteinLabelPairs(i, 2);

    NumInteractionProtein(p1) = NumInteractionProtein(p1) + 1;
    NumInteractionProtein(p2) = NumInteractionProtein(p2) + 1;
end




% Step 8: Get the max number of interactions
MaxNumInteractionProtein = max(NumInteractionProtein);




% Step 9: Construct IndicesInteractionProtein
maxDegree = MaxNumInteractionProtein;
IndicesInteractionProtein = zeros(numProteins, maxDegree);  % initialize
neighborIndex = ones(1, numProteins);  % track insert position for each row

for i = 1:size(ProteinLabelPairs, 1)
    p1 = ProteinLabelPairs(i, 1);
    p2 = ProteinLabelPairs(i, 2);

    % Add each protein to the other's neighbor list
    IndicesInteractionProtein(p1, neighborIndex(p1)) = p2;
    neighborIndex(p1) = neighborIndex(p1) + 1;

    IndicesInteractionProtein(p2, neighborIndex(p2)) = p1;
    neighborIndex(p2) = neighborIndex(p2) + 1;
end




% Step 10: Create the adjacency matrix
A = zeros(N, N);  % Initialize with zeros

% Fill in the matrix from InteractionPairs
for i = 1:size(ProteinLabelPairs, 1)
    p1 = ProteinLabelPairs(i, 1);
    p2 = ProteinLabelPairs(i, 2);

    A(p1, p2) = 1;
    A(p2, p1) = 1;  % Ensure it's symmetric (undirected)
end




% Step 11: Read the CYC2008.tab file
filename = 'CYC2008.tab';
fid = fopen(filename);
lines = textscan(fid, '%s', 'Delimiter', '\n');  % read each line
fclose(fid);
lines = lines{1};  % cell array of lines

% Step: Split each line into a list of protein labels
numComplexes = length(lines);
ComplexProteinLabel = cell(numComplexes, 1);
maxLength = 0;

% First, split each line and track max number of proteins
for i = 1:numComplexes
    ComplexProteinLabel{i} = strsplit(strtrim(lines{i}), '\t');
    maxLength = max(maxLength, length(ComplexProteinLabel{i}));
end

% Step: Create padded matrix with empty strings
ComplexProteinLabelNames = strings(numComplexes, maxLength);  % string matrix

for i = 1:numComplexes
    proteins = ComplexProteinLabel{i};
    ComplexProteinLabelNames(i, 1:length(proteins)) = proteins;
end


[numComplexes, maxCols] = size(ComplexProteinLabelNames);
ComplexProteinLabel = zeros(numComplexes, maxCols);  % default fill = 0

for i = 1:numComplexes
    for j = 1:maxCols
        label = ComplexProteinLabelNames(i, j);
        
        if strlength(label) > 0
            if isKey(ProteinIDMap, label)
                ComplexProteinLabel(i, j) = ProteinIDMap(label);
            else
                ComplexProteinLabel(i, j) = -1;  % label exists but not found in map
            end
        end
    end
end


% Count all non-zero entries row-wise (i.e., all actual proteins whether known or not)
NumberOfProteinsInComplexes = sum(ComplexProteinLabel ~= 0, 2)';

% Count only known proteins (i.e., IDs > 0)
NumberOfKnownProteinsInComplexes = sum(ComplexProteinLabel > 0, 2)';

OverlapComplexesFlag = 0 ; 




% Step 12
% Identify known proteins i.e. proteins which are present in both collins
% and cyc 2008 . If a protein is present in collins and not in cyc 2008
% mark it as -1 . 
% Step: Initialize variable with all -1 (default: not present in any complex)
KnownProteinsInCollins = -1 * ones(1, N);

% Step: Find all valid (known) protein IDs in ComplexProteinIDMatrixCleaned
validIDs = ComplexProteinLabel(ComplexProteinLabel > 0);
uniqueValidIDs = unique(validIDs);

% Set those protein ID positions to 0 (means "known in CYC2008")
KnownProteinsInCollins(uniqueValidIDs) = 0;





% Save if needed
save('DataSets/Protein/3-Protein-Collins-Files.mat', ...
    'ProteinLabel',...
    'ProteinIDMap',...
    'ProteinLabelPairs',...
    'MaxNumInteractionProtein',...
    'NumInteractionProtein',...
    'IndicesInteractionProtein',...
    'N',...
    'A',...
    'ProteinIDTable',...
    'KnownProteinsInCollins');


save('DataSets/Complex/Complex-3-Collins-Files.mat','ComplexProteinLabelNames',...
    'ComplexProteinLabel',...
    'NumberOfProteinsInComplexes',...
    'NumberOfKnownProteinsInComplexes',...
    'OverlapComplexesFlag');