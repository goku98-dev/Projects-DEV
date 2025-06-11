function [Child] = Crossover(Parent1, Parent2, ...
                             ParameterDimension, ...
                             Child)
Pc = 0.8;
for i = 1 : ParameterDimension
    if(rand <= Pc)
        Child.Chromosome(i) = Parent1.Chromosome(i);
    else
        Child.Chromosome(i) = Parent2.Chromosome(i);
    end;
end;
