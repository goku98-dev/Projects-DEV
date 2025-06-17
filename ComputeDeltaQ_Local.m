function deltaQ = ComputeDeltaQ_Local(i, ownCluster, targetCluster, ...
    Cluster_k_Volume, Cluster_k_Degree, m, A, CmplxID, IndicesInteractionProtein, NumInteractionProtein)

    % Compute DeltaQ if protein i moves from ownCluster to targetCluster
    
    % Copy volumes and degrees
    V = Cluster_k_Volume;
    D = Cluster_k_Degree;
    
    % Contribution before move
    Q_before = (V(ownCluster)/m) - (D(ownCluster)/(2*m))^2 ...
             + (V(targetCluster)/m) - (D(targetCluster)/(2*m))^2;
    
    % Now simulate move >> update V and D
    
    % Degree of protein i
    d_i = sum(A(i,:));
    
    % Contribution of i to volume of own cluster
    v_in_own = 0;
    for j = 1:NumInteractionProtein(i)
        neighbor = IndicesInteractionProtein(i,j);
        if CmplxID(neighbor) == ownCluster
            v_in_own = v_in_own + A(i,neighbor);
        end
    end
    
    % Contribution of i to volume of target cluster
    v_in_target = 0;
    for j = 1:NumInteractionProtein(i)
        neighbor = IndicesInteractionProtein(i,j);
        if CmplxID(neighbor) == targetCluster
            v_in_target = v_in_target + A(i,neighbor);
        end
    end
    
    % Update volumes
    V(ownCluster) = V(ownCluster) - v_in_own;
    V(targetCluster) = V(targetCluster) + v_in_target;
    
    % Update degrees
    D(ownCluster) = D(ownCluster) - d_i;
    D(targetCluster) = D(targetCluster) + d_i;
    
    % Contribution after move
    Q_after = (V(ownCluster)/m) - (D(ownCluster)/(2*m))^2 ...
            + (V(targetCluster)/m) - (D(targetCluster)/(2*m))^2;
    
    % DeltaQ = Q_after - Q_before
    deltaQ = Q_after - Q_before;
    
end
