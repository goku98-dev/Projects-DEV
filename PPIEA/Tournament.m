function [Parent1, Parent2] = Tournament(Population, PopulationSize)

                             
 % Q
    rand1 = floor(rand*(PopulationSize - 1) + 1);
    rand2 = floor(rand*(PopulationSize - 1) + 1);
    
    Candidate1Parent1 = Population(rand1);
    Candidate2Parent1 = Population(rand2);
    if(Candidate1Parent1.Q > Candidate2Parent1.Q)
            Parent1 = Candidate1Parent1;
    else
            Parent1 = Candidate2Parent1;
    end;
    
    rand1 = floor(rand*(PopulationSize - 1) + 1);
    rand2 = floor(rand*(PopulationSize - 1) + 1);
    
    Candidate1Parent2 = Population(rand1);
    Candidate2Parent2 = Population(rand2);
    if(Candidate1Parent2.Q > Candidate1Parent2.Q)
            Parent2 = Candidate1Parent2;
    else
            Parent2 = Candidate2Parent2;
    end;

