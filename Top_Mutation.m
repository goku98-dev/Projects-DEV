function [Child] = Top_Mutation(A, ...
                                Child, ...
                                IndicesInteractionProtein, NumInteractionProtein, ...
                                Pm)
                                            
%------------------  Topological based Heuristic Mutation ----------------%

    N = length(A);
    for Node_i = 1: N
        if(NumInteractionProtein(Node_i) > 0) && (rand <= Pm)
            k_Node_i_in = 0;
            k_Node_i_out = 0;
            for Node_j = 1 : N
                if(Node_i ~= Node_j) && (Child.CmplxID(Node_j) == Child.CmplxID(Node_i))
                        k_Node_i_in = k_Node_i_in + A(Node_i, Node_j);
                end;
                if(Node_i ~= Node_j) && (Child.CmplxID(Node_j) ~= Child.CmplxID(Node_i))
                        k_Node_i_out = k_Node_i_out + A(Node_i, Node_j);
                end;
            end;
            if(k_Node_i_in <= k_Node_i_out)
                OldCluster = Child.CmplxID(Node_i);
                NewCluster = Child.CmplxID(Node_i);
                NewDiff = k_Node_i_in - k_Node_i_out;
                k = max(Child.CmplxID);
                
                for i = 1 : k
                    if(i ~= OldCluster)
                        k_Node_i_in = 0;
                        k_Node_i_out = 0;
                        for Node_j = 1 : N
                            if(Node_i ~= Node_j) && (Child.CmplxID(Node_j) == i)
                                k_Node_i_in = k_Node_i_in + A(Node_i, Node_j);
                            end;
                            if(Node_i ~= Node_j) && (Child.CmplxID(Node_j) ~= i)
                                k_Node_i_out = k_Node_i_out + A(Node_i, Node_j);
                            end;
                        end;
                        if(NewDiff < (k_Node_i_in - k_Node_i_out))
                            NewDiff = (k_Node_i_in - k_Node_i_out);
                            NewCluster = i;
                         else
                            if(NewDiff == (k_Node_i_in - k_Node_i_out)) 
                                if(rand > 0.5)
                                    NewCluster = i;
                                end;
                            end;
                        end;
                    end;
                end;
                Child.CmplxID(Node_i) = NewCluster;
                ConnectedNode = Child.Chromosome(Node_i);
                for ConnectedNodeCounter = 1 : NumInteractionProtein(Node_i)
                    if(Child.CmplxID(IndicesInteractionProtein(Node_i, ConnectedNodeCounter)) == NewCluster)
                        ConnectedNode = IndicesInteractionProtein(Node_i, ConnectedNodeCounter);
                    end;
                end;
                Child.Chromosome(Node_i) = ConnectedNode;
            end;
        end;
    end;