function [Individual] = ComputeCmplxDecoding(Individual, N, NumInteractionProtein)



CurrentCmplxID = 0;
NextIndividualGeneLocus = 0;

while(sum(Individual.CmplxFlag) ~= N)
    CurrentCmplxID = CurrentCmplxID + 1;
    NextIndividualGeneLocus = NextIndividualGeneLocus + 1;
    while(Individual.CmplxFlag(NextIndividualGeneLocus) == 1)
        NextIndividualGeneLocus = NextIndividualGeneLocus + 1;
    end;
    if (Individual.Chromosome(NextIndividualGeneLocus ) == 0)
        Individual.CmplxFlag(NextIndividualGeneLocus)= 1;
        NextIndividualGeneLocus = NextIndividualGeneLocus + 1;
    else
        Individual.CmplxID(NextIndividualGeneLocus) = CurrentCmplxID;
        Individual.CmplxID(Individual.Chromosome(NextIndividualGeneLocus)) = CurrentCmplxID;
        Individual.CmplxFlag(NextIndividualGeneLocus) = 1;
        Individual.CmplxFlag(Individual.Chromosome(NextIndividualGeneLocus)) = 1;
    end;
    for i = NextIndividualGeneLocus + 1 : N
        if (Individual.Chromosome(i)== 0)
            Individual.CmplxFlag(i) = 1;
            NextIndividualGeneLocus = NextIndividualGeneLocus + 1;
        elseif (Individual.Chromosome(i) == NextIndividualGeneLocus) || ...
                (Individual.Chromosome(i) == Individual.Chromosome(NextIndividualGeneLocus))
            Individual.CmplxID(i) = CurrentCmplxID;
            Individual.CmplxFlag(i) = 1;
            Individual.CmplxID(Individual.Chromosome(i)) = CurrentCmplxID;
            Individual.CmplxFlag(Individual.Chromosome(i)) = 1;
        end;
    end;
    MoreInteractionInThisCmplx = 1;
    while(sum(Individual.CmplxFlag) ~= N) && (MoreInteractionInThisCmplx == 1)
        Flag = 0;
        for i = NextIndividualGeneLocus + 1 : N
            if(NumInteractionProtein(i) ~= 0)
                if(Individual.CmplxID(i) == 0) && ...
                        (Individual.CmplxID(Individual.Chromosome(i)) == CurrentCmplxID) || ...
                        (Individual.CmplxID(Individual.Chromosome(i)) == 0) && ...
                        (Individual.CmplxID(i) == CurrentCmplxID)
                    Flag = 1;
                    Individual.CmplxID(i) = CurrentCmplxID;
                    Individual.CmplxFlag(i) = 1;
                    Individual.CmplxID(Individual.Chromosome(i)) = CurrentCmplxID;
                    Individual.CmplxFlag(Individual.Chromosome(i)) = 1;
                end;
            end;
        end;
        if(Flag == 0)
            MoreInteractionInThisCmplx = 0;
        end;
    end;
    NextIndividualGeneLocus = 0;
end;