function [Results] = BestIndividual(Child, PopulationSize, ...
                               GenerationCounter, ...
                               Results)
 
% Either Largest or Smallest according to either maximization or minimization                            
    
 % Q
    BestIndex = 1;
    for ChildCounter = 2 : PopulationSize
        if(Child(ChildCounter).Q > Child(BestIndex).Q)
            BestIndex = ChildCounter;
        end;
    end;
    Results(GenerationCounter).Chromosome = Child(BestIndex).Chromosome;
    Results(GenerationCounter).CmplxID = Child(BestIndex).CmplxID;
    Results(GenerationCounter).Q = Child(BestIndex).Q;
    