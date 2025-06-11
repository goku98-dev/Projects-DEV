function [Population] = Individual2CmplxDecoding(N, NumInteractionProtein, ...
                                                 Population, PopulationSize)

for IndividualCounter = 1 : PopulationSize
    for ProteinCounter = 1 : N
        if(NumInteractionProtein(ProteinCounter) ~= 0)
            Population(IndividualCounter).CmplxFlag(ProteinCounter) = 0;
            Population(IndividualCounter).CmplxID(ProteinCounter) = 0;
        else
           Population(IndividualCounter).CmplxFlag(ProteinCounter) = 1;
           Population(IndividualCounter).CmplxID(ProteinCounter) = 0; 
        end;
    end;
end;

for IndividualCounter = 1 : PopulationSize
    Population(IndividualCounter) = ComputeCmplxDecoding(Population(IndividualCounter), N, NumInteractionProtein);
end;