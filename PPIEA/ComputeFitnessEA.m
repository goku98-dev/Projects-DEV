function [Population] = ComputeFitnessEA(A, N, ...
                                         IndicesInteractionProtein, NumInteractionProtein, ...
                                         Population, PopulationSize)
                                             

%---------------------------------- Q Model ------------------------------%                                             
m = sum(sum(A)); %Degree of whole network 
for IndividualCounter = 1 : PopulationSize
    % K is the number of clusters for the partitioning of the network in the current individual
    K = max(Population(IndividualCounter).CmplxID);
    Cluster_k_Volume(1 : K) = 0;
    Cluster_k_Cardinality(1 : K) = 0;
    Cluster_k_Degree(1 : K) = 0;
    Cluster_k_Q(1 : K) = 0;
    for Node_i = 1 : N
        Cluster_k_Cardinality(Population(IndividualCounter).CmplxID(Node_i)) = Cluster_k_Cardinality(Population(IndividualCounter).CmplxID(Node_i)) + 1;                                                                              1;
        Cluster_k_Degree(Population(IndividualCounter).CmplxID(Node_i)) = Cluster_k_Degree(Population(IndividualCounter).CmplxID(Node_i)) + sum(A(Node_i,:));%NumInteractionProtein(Node_i);
        for Node_j = 1 : NumInteractionProtein(Node_i)
            if(Population(IndividualCounter).CmplxID(Node_i) == ...
                                                                   Population(IndividualCounter).CmplxID(IndicesInteractionProtein(Node_i, Node_j)))
                 Cluster_k_Volume(Population(IndividualCounter).CmplxID(Node_i)) = Cluster_k_Volume(Population(IndividualCounter).CmplxID(Node_i)) + ...
                                                                                                                                                   A(Node_i, IndicesInteractionProtein(Node_i, Node_j));%+1;
            end;
        end;
    end;
    Cluster_k_Q(1 : K) = (Cluster_k_Volume(1 : K) / m) - ((Cluster_k_Degree(1 : K) / (2*m)).^2); % Maximization since numerator includes k-Volume 
    Q = sum(Cluster_k_Q(1 : K));
    Population(IndividualCounter).Q = Q;
end;

%------------------------------ End of Q Model ---------------------------%
