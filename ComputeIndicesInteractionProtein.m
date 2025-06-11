function [IndicesInteractionProtein] = ComputeIndicesInteractionProtein(A, N, ...
                                                                        IndicesInteractionProtein)

for i = 1 : N
    j = 1;
    k = 1;
    while (j <= N)
        if (A(i,j) == 1)
            IndicesInteractionProtein(i,k) = j;
            k = k + 1;
        end;
        j = j + 1;
    end;
end;


