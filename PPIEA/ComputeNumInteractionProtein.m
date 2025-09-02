function [ NumInteractionProtein ] = ComputeNumInteractionProtein( A, N )

for i = 1 : N
    NumInteractionProtein(i) = sum(A(i,:));
end;
end

