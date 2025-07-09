
% ---------------------------------------------------------------------------------------%
%         Single EA for complex Detection in Protein-Protein Interaction Networks        %
% ---------------------------------------------------------------------------------------%

% ---------------------------------------------------------------------------------------%
%      Evolutionary Based Complex Detection in Protein-Protein Interaction Networks      %
% ---------------------------------------------------------------------------------------%
clear;
clc;
NetworkNumber = input('\n Enter the network Number  \n 1: Yeast D1 \n 2: Yeast D2 \n 3: Collins PPI Network \n Network Number: ');; 
if (NetworkNumber == 1)
    DatasetName = "Yeast-D1";
    load('DataSets/Protein/1-Protein-Yeast-D1-Files.mat');
    load('DataSets/Complex/Complex-D1-Files.mat');
elseif (NetworkNumber == 2)
    DatasetName = "Yeast-D2";
    load('DataSets/Protein/2-Protein-Yeast-D2-Files.mat');
    load('DataSets/Complex/Complex-D2-Files.mat');
elseif (NetworkNumber == 3)
    DatasetName = "Collins PPI Network";
    load('DataSets/Protein/3-Protein-Collins-Files.mat');
    load('DataSets/Complex/Complex-3-Collins-Files.mat');
end
MaxRuns = 10;
MutationType = input('\n Enter type of mutation: \n 1: Canonical Mutation \n 2: Topological Mutation \n 3: Delta Mutation \n Mutation-Type: ');

if (MutationType == 1 || MutationType == 3)
    Pm = 0.1;
elseif (MutationType == 2)
    Pm = 0.2;
end

PopulationSize = 100;

for RunNumber = 1 : MaxRuns
    RunNumber
    ResultsGroup = []; 
    Population = [];    
    Population = CreatePopulation(N, NumInteractionProtein, IndicesInteractionProtein, ...
                                  PopulationSize);
    % Chromosome (Solution) decoding
    [Population] = Individual2CmplxDecoding(N, NumInteractionProtein, ...
                                            Population, PopulationSize);                                     
                                                 
     % Step 4: Compute collection of Fitness functions.
     [Population]= ComputeFitnessEA(A, N, ...
                                    IndicesInteractionProtein, NumInteractionProtein, ...
                                    Population, PopulationSize);  
    % Step 5: Compute ResultsGroup by Single EA                          
     [ResultsGroup] = EA(A, N, MutationType, ...
                         IndicesInteractionProtein, NumInteractionProtein, ...
                         Population, PopulationSize, ...
                         Pm);
    
     parsave(strcat(strcat('Repositories/EA_', ...
                        'PPI_', int2str(NetworkNumber), ...
                        '_Run_', int2str(RunNumber)),'.mat'),ResultsGroup);
    
            
end; 


 
 