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

% Save if needed
save('DataSets/Protein/3-Protein-Collins-Files.mat', ...
    'ProteinLabel',...
    'ProteinIDMap',...
    'ProteinLabelPairs',...
    'MaxNumInteractionProtein',...
    'NumInteractionProtein',...
    'IndicesInteractionProtein',...
    'N',...
    'A');
