function [Population, FrequencyMatrix] = CreatePopulation(N, NumInteractionProtein, IndicesInteractionProtein, PopulationSize)
FrequencyMatrix = zeros(990, 990);

for IndividualCounter = 1 : PopulationSize
    for ProteinCounter = 1 : N
        if(NumInteractionProtein(ProteinCounter) > 0)
             % Get list of neighbors for this protein
            neighbors = IndicesInteractionProtein(ProteinCounter, 1:NumInteractionProtein(ProteinCounter));
            
            % Get corresponding frequencies for each neighbor
            freqs = FrequencyMatrix(ProteinCounter, neighbors);
            
            % Find the minimum frequency among neighbors
            minFreq = min(freqs);
            
            % Filter neighbors with that minimum frequency
            minFreqIndices = neighbors(freqs == minFreq);
            
            % Randomly choose one of the least-used neighbors
            selected = minFreqIndices(randi(length(minFreqIndices)));
            
            % Assign selected to chromosome
            Population(IndividualCounter).Chromosome(ProteinCounter) = selected;

            % Update frequency matrix
            FrequencyMatrix(ProteinCounter, selected) = FrequencyMatrix(ProteinCounter, selected) + 1;
        else
           Population(IndividualCounter).Chromosome(ProteinCounter) = 0;
        end;
    end;
end;

