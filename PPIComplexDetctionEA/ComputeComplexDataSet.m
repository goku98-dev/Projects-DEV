function [ComplexProteinLabel,NumberOfProteinsInComplexes,NumberOfKnownProteinsInComplexes,OverlapComplexesFlag] = ...
    ComputeComplexDataSet(ComplexType,ProteinLabel,ProteinLabelPairs,A,N,NumInteractionProtein,MaxNumInteractionProtein,IndicesInteractionProtein)

LengthComplexType = length(ComplexType);
NumberOfProteinsInComplexes = [];
NumberOfKnownProteinsInComplexes = [];
CurrentComplexCounter = 1;
CurrentComplex = strcat('C', int2str(CurrentComplexCounter), ':');
NextComplexCounter = CurrentComplexCounter + 1;
NextComplex = strcat('C', int2str(NextComplexCounter), ':');
CurrentStringCounter = 2;   %---> CurrentProteinCounter

while( CurrentStringCounter <= LengthComplexType)
    
    NumberOfProteinInCurrentComplex = 0;
    while(CurrentStringCounter <= LengthComplexType) && (strcmp(ComplexType(CurrentStringCounter), NextComplex) ~= 1)
        NumberOfProteinInCurrentComplex = NumberOfProteinInCurrentComplex + 1;
        CurrentStringCounter = CurrentStringCounter + 1;
    end;
    NumberOfProteinsInComplexes(CurrentComplexCounter) = NumberOfProteinInCurrentComplex;
    CurrentComplexCounter = CurrentComplexCounter + 1; % The new complex counter
    NextComplexCounter = CurrentComplexCounter + 1; % The next new complex counter
    NextComplex = strcat('C', int2str(NextComplexCounter), ':');
    CurrentStringCounter = CurrentStringCounter + 1; % To consider the first protein in the new complex
end;

% Create Complex Protein Label matrix. The labels will be identical to those created from Protein DataSets. Any unkown protein will be labeled by -1
MaxNumberOfProteins = max(NumberOfProteinsInComplexes);
ComplexProteinLabel = []; % VIP
for ComplexNumber = 1 : length(NumberOfProteinsInComplexes)
    for ProteinNumber = 1 : MaxNumberOfProteins
        ComplexProteinLabel(ComplexNumber, ProteinNumber) = 0;
    end;
end;

LengthofProteinLabel = length(ProteinLabel);
ProteinCounter = 2; % To consider the first protein in the first complex
for ComplexNumber = 1 : length(NumberOfProteinsInComplexes)
    for ProteinNumber = 1 : NumberOfProteinsInComplexes(ComplexNumber)
        CurrentProteinLabel = 1; % To consider the first protein in ProteinLabel
        Flag = 0;
        while (CurrentProteinLabel <= LengthofProteinLabel) && (Flag == 0)           
             if(strcmp(ComplexType(ProteinCounter), ProteinLabel(CurrentProteinLabel)) == 1)
                 Flag = 1;
                 ComplexProteinLabel(ComplexNumber, ProteinNumber) = CurrentProteinLabel;
             else
                 CurrentProteinLabel = CurrentProteinLabel + 1;
             end;        
         end;
         if (CurrentProteinLabel > LengthofProteinLabel) && (Flag == 0) % There is no such protein code in ProteinLabel
             ComplexProteinLabel(ComplexNumber, ProteinNumber) = -1; 
         end;
         ProteinCounter = ProteinCounter + 1; % To consider the next protein in the current complex
    end;
    % To exclude number of noisy proteins from the total number of proteins in each complex. Thus, yielding number of known proteins
   NumberOfKnownProteinsInComplexes(ComplexNumber) = 0;
    for i = 1 : NumberOfProteinsInComplexes(ComplexNumber)
        if  (ComplexProteinLabel(ComplexNumber, i) ~= -1)
            NumberOfKnownProteinsInComplexes(ComplexNumber) = NumberOfKnownProteinsInComplexes(ComplexNumber) + 1;
        end;    
   end;

    ProteinCounter = ProteinCounter + 1; % To consider the first protein in the next complex
end;
% To check if  ComplexType is of overlap nature, i.e. there is one or more protens belong to more than one complex
% First, the flag is set to 0, means no overlap
OverlapComplexesFlag = 0;
ComplexNumber = 1;
while (ComplexNumber <= length(NumberOfProteinsInComplexes)) && (OverlapComplexesFlag == 0)
    NextComplexNumber = ComplexNumber + 1;
    while(NextComplexNumber <= length(NumberOfProteinsInComplexes)) && (OverlapComplexesFlag == 0)
        a = [];
        b = [];
        c = [];
        % To check till shorter length of a and b
        larger = max(NumberOfProteinsInComplexes(ComplexNumber), NumberOfProteinsInComplexes(NextComplexNumber));
        a(1 : larger) = ComplexProteinLabel(ComplexNumber, 1 : larger);
        b(1 : larger) = ComplexProteinLabel(NextComplexNumber, 1 : larger); 
        c = intersect(a, b); % c will be the intersection of a and b sorted in ascending order
        if(length(c) >= 1) && (c(1) ~= -1) % if one or more proteins are common to current complex and next complex
            OverlapComplexesFlag = 1;
        end;
        NextComplexNumber = NextComplexNumber + 1;
    end;
    ComplexNumber = ComplexNumber + 1;
end;