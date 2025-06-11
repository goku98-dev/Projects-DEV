function [child] = Mutation_BorderAware(child, IndicesInteractionProtein, NumInteractionProtein, Pm)

    % Border-Aware Adaptive Mutation on Chromosome(i)
    % Works with your ComputeCmplxDecoding pipeline
    
    % Assumes Individual.CmplxID is already computed (decoded)
    
    for i = 1:length(child)
        
        % Skip proteins with no neighbors
        if NumInteractionProtein(i) == 0
            continue;
        end
        
        % Step 1: Get neighbors of protein i
        neighbors = IndicesInteractionProtein(i, 1:NumInteractionProtein(i));
        
        % Step 2: Get neighbor cluster assignments
        neighborClusters = child.CmplxID(neighbors);
        
        % Step 3: Compute BorderScore(i)
        ownCluster = child.CmplxID(i);
        numOutside = sum(neighborClusters ~= ownCluster);
        BorderScore = numOutside / NumInteractionProtein(i);
        
        % Step 4: Adaptive mutation probability
        if rand <= BorderScore * Pm
            
            % Step 5: Target cluster → most common neighbor cluster
            targetCluster = mode(neighborClusters);
            
            % Step 6: Select neighbors that belong to targetCluster
            candidates = neighbors(neighborClusters == targetCluster);
            
            % Safety check: in rare case no candidate → fallback to any neighbor
            if isempty(candidates)
                candidates = neighbors;
            end
            
            % Step 7: Mutate Chromosome(i) → point to random candidate in target cluster
            child.Chromosome(i) = candidates(randi(length(candidates)));
            
            % Optional debug print:
            % fprintf('Mutated protein %d to cluster %d\n', i, targetCluster);
            
        end
        
    end % for i

end
