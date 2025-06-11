function [Results]= EA(A, N, MutationType, ...
    IndicesInteractionProtein, NumInteractionProtein, ...
    Population, PopulationSize, ...
    Pm)

Results = [];
Generations = 100;

Child = Population;
% EA Loop
for GenerationCounter = 1 : Generations

    GenerationCounter

    Population = Child;
    SelectedParents = [];
    Parent1 = [];
    Parent2 = [];
    % Tournament
    for ProblemCounter = 1 : PopulationSize

        rand1 = floor(rand*(PopulationSize - 1) + 1);
        rand2 = floor(rand*(PopulationSize - 1) + 1);

        Candidate1Parent1 = Population(rand1);
        Candidate2Parent1 = Population(rand2);
        if(Candidate1Parent1.Q > Candidate2Parent1.Q)
            Parent1 = Candidate1Parent1;
            P1 = rand1;
        else
            Parent1 = Candidate2Parent1;
            P1 = rand2;
        end;

        rand1 = floor(rand*(PopulationSize - 1) + 1);
        rand2 = floor(rand*(PopulationSize - 1) + 1);

        Candidate1Parent2 = Population(rand1);
        Candidate2Parent2 = Population(rand2);
        if(Candidate1Parent2.Q > Candidate1Parent2.Q)
            Parent2 = Candidate1Parent2;
            P2 = rand1;
        else
            Parent2 = Candidate2Parent2;
            P2 = rand2;
        end;

        Index = 2 * (ProblemCounter - 1) + 1;
        SelectedParents(Index) = P1;
        SelectedParents(Index + 1) = P2;
        % Crossover Operator
        [Child(ProblemCounter)] = Crossover(Parent1, Parent2, ...
            N, ...
            Child(ProblemCounter));
    end;
    % Mutation
    for ProblemCounter = 1 : PopulationSize
        % if (MutationType == 1)
        %---------------------------  1: Canonical Mutation -------------------------%
        % [Child(ProblemCounter)] = Mutation(Child(ProblemCounter), ...
        %     IndicesInteractionProtein, NumInteractionProtein, ...
        %    Pm);
        %if (MutationType == 1)
        % [Child(ProblemCounter)] = Mutation_BorderAware(Child(ProblemCounter), ...
        %    IndicesInteractionProtein, NumInteractionProtein, ...
        %   Pm);
        if (MutationType == 1)
            [Child(ProblemCounter)] = Mutation_DeltaQ(Child(ProblemCounter), ...
                IndicesInteractionProtein, NumInteractionProtein, ...
                Pm ,N, A);
        elseif (MutationType == 2)
            %---------------------------  2: Topological Mutation -----------------------%
            [Child(ProblemCounter)] = Top_Mutation(A, ...
                Child(ProblemCounter), ...
                IndicesInteractionProtein, NumInteractionProtein, ...
                Pm);

        end
    end
    [Child] = Individual2CmplxDecoding(N, NumInteractionProtein, ...
        Child, PopulationSize);
    [Child] = ComputeFitnessEA(A, N, ...
        IndicesInteractionProtein, NumInteractionProtein, ...
        Child, PopulationSize);

    [Child] = Elitism(Population, PopulationSize, ...
        Child);
    [Results] = BestIndividual(Child, PopulationSize, ...
        GenerationCounter, ...
        Results);
    Results(GenerationCounter)

end;