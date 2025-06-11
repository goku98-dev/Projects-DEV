
% ---------------------------------------------------------------------------------------%
%         Single EA for complex Detection in Protein-Protein Interaction Networks        %
% ---------------------------------------------------------------------------------------%

% ---------------------------------------------------------------------------------------%
%      Evolutionary Based Complex Detection in Protein-Protein Interaction Networks      %
% ---------------------------------------------------------------------------------------%
clear;
clc;
NetworkNumber = 1; 
if (NetworkNumber == 1)
    DatasetName = "Yeast-D1";
    load('DataSets/Protein/1-Protein-Yeast-D1-Files.mat');
    load('DataSets/Complex/Complex-D1-Files.mat');
elseif (NetworkNumber == 2)
    DatasetName = "Yeast-D2";
    load('DataSets/Protein/2-Protein-Yeast-D2-Files.mat');
    load('DataSets/Complex/Complex-D2-Files.mat');
end
MaxRuns = 10;
MutationType = input('\n Enter type of mutation: \n 1: Canonical Mutation \n 2: Topological Mutation \n Mutation-Type: ');

if (MutationType == 1)
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


 
 