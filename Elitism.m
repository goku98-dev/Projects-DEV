function [Child] = Elitism(Population, PopulationSize, ...
                           Child)
                       
ElitistPercentage = 0.1;
ElitistSize = floor(PopulationSize * ElitistPercentage);
Temp = [];


 % Q Model % Maximize
    for IndividualCounter = 1 : PopulationSize
        Temp(IndividualCounter) = Population(IndividualCounter).Q;
    end;
    [TempPopulation, IndexPopulation] = sort(Temp, 'descend');
    for IndividualCounter = 1 : PopulationSize
        Temp(IndividualCounter) = Child(IndividualCounter).Q;
    end;
    [TempChild, IndexChild] = sort(Temp); % default sort in ascending
    for ElitistCounter = 1 : ElitistSize
        Child(IndexChild(ElitistCounter)) = Population(IndexPopulation(ElitistCounter));
    end;

