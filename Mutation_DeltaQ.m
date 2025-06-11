function [child] = Mutation_DeltaQ(child, IndicesInteractionProtein, NumInteractionProtein, Pm, N, A)

    % DeltaQ-Based Adaptive Mutation on Chromosome(i)
    % Assumes child.CmplxID is already computed
    m = sum(sum(A));
    
    % First, precompute current Cluster Volume and Degree
    K = max(child.CmplxID);
    Cluster_k_Volume = zeros(1,K);
    Cluster_k_Degree = zeros(1,K);
    
    % Build initial Cluster_k_Volume and Cluster_k_Degree
    for i = 1:N
        Cluster_k_Degree(child.CmplxID(i)) = Cluster_k_Degree(child.CmplxID(i)) + sum(A(i,:));
        for j = 1:NumInteractionProtein(i)
            neighbor = IndicesInteractionProtein(i,j);
            if child.CmplxID(i) == child.CmplxID(neighbor)
                Cluster_k_Volume(child.CmplxID(i)) = Cluster_k_Volume(child.CmplxID(i)) + A(i,neighbor);
            end
        end
    end
    
    % Now do mutation
    for i = 1:N
        
        % Skip proteins with no neighbors
        if NumInteractionProtein(i) == 0
            continue;
        end
        
        % Mutation probability
        if rand > Pm
            continue;
        end
        
        neighbors = IndicesInteractionProtein(i, 1:NumInteractionProtein(i));
        neighborClusters = child.CmplxID(neighbors);
        
        ownCluster = child.CmplxID(i);
        
        uniqueClusters = unique(neighborClusters);
        uniqueClusters(uniqueClusters == ownCluster) = []; % exclude own cluster
        
        bestDeltaQ = -Inf;
        bestCluster = ownCluster;
        
        % Try moving to each neighbor cluster
        for c = uniqueClusters
            
            deltaQ = ComputeDeltaQ_Local(i, ownCluster, c, ...
                Cluster_k_Volume, Cluster_k_Degree, m, A, child.CmplxID, IndicesInteractionProtein, NumInteractionProtein);
            
            if deltaQ > bestDeltaQ
                bestDeltaQ = deltaQ;
                bestCluster = c;
            end
        end
        
        % If bestDeltaQ > 0 → perform mutation
        if bestDeltaQ > 0
            
            % Select neighbor in bestCluster
            candidates = neighbors(neighborClusters == bestCluster);
            if isempty(candidates)
                candidates = neighbors; % fallback
            end
            
            % Mutate Chromosome(i)
            child.Chromosome(i) = candidates(randi(length(candidates)));
            
        end
        
    end % for i

end
