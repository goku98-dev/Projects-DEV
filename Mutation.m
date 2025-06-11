function [Child] = Mutation(Child, ...
                            IndicesInteractionProtein, NumInteractionProtein, ...
                            Pm)
                                                                        

%---------------------------  Canonical Mutation -------------------------%                        
    
    for i = 1:length(Child)
        disp(i)
        disp(rand)
        if(NumInteractionProtein(i) > 0) && (rand <= Pm)
            random = floor(rand * (NumInteractionProtein(i)-1) + 1);
            Child.Chromosome(i) = IndicesInteractionProtein(i,random);
        end;
    end;





