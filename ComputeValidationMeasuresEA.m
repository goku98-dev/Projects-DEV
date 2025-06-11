% Validation measures (Precision, Recall, Fmeasure, etc.) and Best Statistics                                          

'Pls. Select a bio network'
'1:  Gavin-PPI-Filtered-0.125 (Yeast-D1)'

NetworkNumber = input('Pls. enter your tested network\n');
'-- Q Model --'

if (NetworkNumber == 1)
     %Load Golden True Complexes - Complex D1 and its information
      load('DataSets/Complex/Complex-D1-Files.mat','ComplexProteinLabel', 'NumberOfProteinsInComplexes', 'NumberOfKnownProteinsInComplexes', 'OverlapComplexesFlag');
      CorrectPartitioning = [];
      [CorrectPartitioning] = ComplexesCorrectPartitioning(ComplexProteinLabel, NumberOfProteinsInComplexes, ...
                                                           CorrectPartitioning);
      %Load Yeast-D1 DataSet with 990 Protein and 4687 interactions
      load('DataSets/Protein/1-Protein-Yeast-D1-Files.mat','ProteinLabel','ProteinLabelPairs','A','N','NumInteractionProtein','MaxNumInteractionProtein','IndicesInteractionProtein','KnownProteins');

      KnownProteinsInYeast = [];
      KnownProteinsInYeast = KnownProteins;
end;
if (NetworkNumber == 2)
     %Load Golden True Complexes - Complex D2 and its information
      load('DataSets/Complex/Complex-D2-Files.mat','ComplexProteinLabel', 'NumberOfProteinsInComplexes', 'NumberOfKnownProteinsInComplexes', 'OverlapComplexesFlag');
%      CorrectPartitioning = [];
%       [CorrectPartitioning] = ComplexesCorrectPartitioning(ComplexProteinLabel, NumberOfProteinsInComplexes, ...
%                                                           CorrectPartitioning);
      %Load Yeast-D2 DataSet with 1443 Protein and ----- interactions
      load('DataSets/Protein/2-Protein-Yeast-D2-Files.mat','ProteinLabel','ProteinLabelPairs','A','N','NumInteractionProtein','MaxNumInteractionProtein','IndicesInteractionProtein');
load('DataSets/Protein/KnownProteinD2.mat','KnownProteins');

      KnownProteinsInYeast = [];
      KnownProteinsInYeast = KnownProteins;
end;

 


StatisticsAtAllGenerations = 0; % either 0 or 1  % kindly always set it to 0 to save time
MaxRuns = input('Pls. enter how many runs you want to find out statistics\n');

% Set Overlapping Score, i.e. overlapping threshold

OS = 0.05; % input('Pls. enter threshold of overlapping score\n'); %0.25; % From Nazar Zaki's settings (pp.17) 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35
for OSCounter = 1 :15
    OS=OS+0.05;
%OS = 0.25; % Like Pizzuti & Rombo's work
%OS = 0.5; % Like Nazar Zaki's work  

NumberOfUnKnownComplexes = length(find(NumberOfKnownProteinsInComplexes == 0));
NumberOfGoldenCmplxes = length(NumberOfKnownProteinsInComplexes) - NumberOfUnKnownComplexes;

IndexOfGoldenCmplxes = [];
GoldenCmplxesCounter = 0;
for CmplxCounter = 1 : length(NumberOfKnownProteinsInComplexes)
    if(NumberOfKnownProteinsInComplexes(CmplxCounter) > 0)
        GoldenCmplxesCounter = GoldenCmplxesCounter + 1;
        IndexOfGoldenCmplxes(GoldenCmplxesCounter) = CmplxCounter;
    end;
end;
length(NumberOfKnownProteinsInComplexes)
length(IndexOfGoldenCmplxes)
           
AvgBestMetric1.Recall = 0;
AvgBestMetric1.Precision = 0;
AvgBestMetric1.Fmeasure = 0;
AvgBestMetric2.Sensitivity = 0;
AvgBestMetric2.PPV = 0;
AvgBestMetric2.Accuracy = 0;
AvgBestMetric3.RecN = 0;
AvgBestMetric3.PrecN = 0;
AvgBestMetric3.FnMeasure = 0;

AvgBestMetric4.CCF = 0;
AvgBestMetric4.Strength = 0;

AvgWorstMetric1.Recall = 0;
AvgWorstMetric1.Precision = 0;
AvgWorstMetric1.Fmeasure = 0;
AvgWorstMetric2.Sensitivity = 0;
AvgWorstMetric2.PPV = 0;
AvgWorstMetric2.Accuracy = 0;
AvgWorstMetric3.RecN = 0;
AvgWorstMetric3.PrecN = 0;
AvgWorstMetric3.FnMeasure = 0;

AvgWorstMetric4.CCF = 0;
AvgWorstMetric4.Strength = 0;

AvgAvgMetric1.Recall = 0;
AvgAvgMetric1.Precision = 0;
AvgAvgMetric1.Fmeasure = 0;
AvgAvgMetric2.Sensitivity = 0;
AvgAvgMetric2.PPV = 0;
AvgAvgMetric2.Accuracy = 0;
AvgAvgMetric3.RecN = 0;
AvgAvgMetric3.PrecN = 0;
AvgAvgMetric3.FnMeasure = 0;

AvgAvgMetric4.CCF = 0;
AvgAvgMetric4.Strength = 0;

for RunNumber = 1 : MaxRuns
    RunNumber 
    load(strcat(strcat('Repositories/EA_', ...
                        'PPI_', int2str(NetworkNumber), ...
                        '_Run_', int2str(RunNumber)),'.mat'),'ResultsGroup');

    %because we use parallel computation for multi run.
    Results = [];
    Results = ResultsGroup;                                              
    ResultsSize = length(Results); % should be equal to the max MOEA generations over 10. See in MOEAD the code: if(mode(GenerationCounter, 10) == 0)                                       
                                                                                                                 %%Epoch = floor(GenerationCounter / 10);                                         
                                                                                                                 %%Results(Epoch).NearParetoOptimalSet = NearParetoOptimalSet;
                                                                                                                 %%end;
    BestMetric1 = [];
    BestMetric2 = [];
    BestMetric3= [];
    BestMetric4= [];
    WorstMetric1 = [];
    WorstMetric2 = [];
    WorstMetric3 = [];
    WorstMetric4 = [];
    AverageMetric1 = [];
    AverageMetric2 = [];
    AverageMetric3 = [];
    AverageMetric4 = [];
    
    if(StatisticsAtAllGenerations == 0)
        StartGeneration = ResultsSize;
    else
        StartGeneration = 1;
    end;

    for ResultsInGeneration = StartGeneration : ResultsSize
        ResultsInGeneration
        BestMetric1(ResultsInGeneration).Recall = 0;       
        BestMetric1(ResultsInGeneration).Precision = 0;
        BestMetric1(ResultsInGeneration).Fmeasure = 0;
        BestMetric2(ResultsInGeneration).Sensitivity = 0;        
        BestMetric2(ResultsInGeneration).PPV = 0;
        BestMetric2(ResultsInGeneration).Accuracy = 0;
        BestMetric3(ResultsInGeneration).RecN = 0;
        BestMetric3(ResultsInGeneration).PrecN = 0;
        BestMetric3(ResultsInGeneration).FnMeasure = 0;
        BestMetric4(ResultsInGeneration).CCF = 0;
        BestMetric4(ResultsInGeneration).Strength = 0;
        
        WorstMetric1(ResultsInGeneration).Recall = 1000000;
        WorstMetric1(ResultsInGeneration).Precision = 1000000;
        WorstMetric1(ResultsInGeneration).Fmeasure = 1000000;
        WorstMetric2(ResultsInGeneration).Sensitivity = 1000000;
        WorstMetric2(ResultsInGeneration).PPV = 1000000;
        WorstMetric2(ResultsInGeneration).Accuracy = 1000000;   
        WorstMetric3(ResultsInGeneration).RecN = 1000000;
        WorstMetric3(ResultsInGeneration).PrecN = 1000000;
        WorstMetric3(ResultsInGeneration).FnMeasure = 1000000;
        WorstMetric4(ResultsInGeneration).CCF = 1000000;
        WorstMetric4(ResultsInGeneration).Strength = 1000000;
        
        AverageMetric1(ResultsInGeneration).Recall = 0;
        AverageMetric1(ResultsInGeneration).Precision = 0; 
        AverageMetric1(ResultsInGeneration).Fmeasure = 0;
        AverageMetric2(ResultsInGeneration).Sensitivity = 0;
        AverageMetric2(ResultsInGeneration).PPV = 0;
        AverageMetric2(ResultsInGeneration).Accuracy = 0;
        AverageMetric3(ResultsInGeneration).RecN = 0;
        AverageMetric3(ResultsInGeneration).PrecN = 0;
        AverageMetric3(ResultsInGeneration).FnMeasure = 0;
        AverageMetric4(ResultsInGeneration).CCF = 0;
        AverageMetric4(ResultsInGeneration).Strength = 0;
        
        Length = length(Results(ResultsInGeneration));
        for SolutionCounter = 1 : Length
            SolutionCounter
            MaxIntersectOfPredictedCluster = [];
            PredictedClusterMatchFlag = [];
            CmplxMatchFlag = []; % Since Cmplx network is of constant size, then [] has same effect of CmplxMatchFlag(1 : NumberOfGoldenCmplxes) = 0;
            NumberOfPredictedClusters = max(Results(ResultsInGeneration).CmplxID);
            NumberOfPredictedClusters
            Results(ResultsInGeneration).Q
            PredictedClusterMatchFlag(1 : NumberOfPredictedClusters) = 0;
            NumOfIntersect = [];  
            NumOfunion = [];
            Acc = [];
            Max = [];
            Index = [];
            MatchCmplx = [];
            MatchCluster = [];
            NumofPredictedClusterProteins = [];
            for PredictedClusterCounter = 1 : NumberOfPredictedClusters
                Temp_PredictedClusterProteinLables = [];
                Temp_PredictedClusterProteinLables = find(Results(ResultsInGeneration).CmplxID == PredictedClusterCounter);
                PredictedClusterProteinLables = [];
                %  OverlapComplexesFlag may be used later in our need
                Protein_index = 0;
                for Protein_i_index = 1 : length(Temp_PredictedClusterProteinLables)
                    Protein_i = Temp_PredictedClusterProteinLables(Protein_i_index);
                    if(KnownProteinsInYeast(Protein_i) ~= -1)
                        Protein_index = Protein_index + 1;
                        PredictedClusterProteinLables(Protein_index) = Protein_i;
                    end;
                end;
                NumofPredictedClusterProteins(PredictedClusterCounter) = length(PredictedClusterProteinLables);
             
                for CmplxCounter = 1 : NumberOfGoldenCmplxes
                    GoldenComplexProteinLabels = [];
                    GoldenProteinCounter = 1;
                    ProteinCounter = 1;
                    while(ProteinCounter <= NumberOfProteinsInComplexes(IndexOfGoldenCmplxes(CmplxCounter)))
                        if(ComplexProteinLabel(IndexOfGoldenCmplxes(CmplxCounter), ProteinCounter) ~= -1)
                            GoldenComplexProteinLabels( GoldenProteinCounter) = ComplexProteinLabel(IndexOfGoldenCmplxes(CmplxCounter), ProteinCounter);
                            GoldenProteinCounter = GoldenProteinCounter + 1;
                        end;
                        ProteinCounter = ProteinCounter + 1;
                    end;
                        % Overlapping score is Jaccard index presented in both Nazar Zaki (pp.16) and Sanghamitra Bandyopadhyay (pp.5)
                        % we don't use formula of Pizzuti (pp. 6) and her Prof. formula being referred by [2] in his paper
                        % Pizzuti's formula
                        %OverlappingScore = (length(intersect(PredictedClusterProteinLables, ComplexProteinLabels(IndexOfGoldenCmplxes(CmplxCounter), :)))^2) / ...
                        %                   (length(PredictedClusterProteinLables)* NumberOfKnownProteinsInComplexes(IndexOfGoldenCmplxes(CmplxCounter)));
        
                        % Jaccard Index
                        OverlappingScore = length(intersect(PredictedClusterProteinLables, GoldenComplexProteinLabels)) / ...
                                               length(union(PredictedClusterProteinLables, GoldenComplexProteinLabels));
        
                        
                        % Calculation By Pizzuti
                        if(OverlappingScore >= OS)
                            CmplxMatchFlag(IndexOfGoldenCmplxes(CmplxCounter)) = 1;
                            PredictedClusterMatchFlag(PredictedClusterCounter) = 1;
                        end;
                        % NumOfIntersect = Number of intersect between ComplexProteinLabels and PredictedClusterProteinLables
                        NumOfIntersect(IndexOfGoldenCmplxes(CmplxCounter), PredictedClusterCounter) = length(intersect(PredictedClusterProteinLables, GoldenComplexProteinLabels));
                        NumOfunion(IndexOfGoldenCmplxes(CmplxCounter), PredictedClusterCounter) = length(union(PredictedClusterProteinLables, GoldenComplexProteinLabels)); % To remove 0 from calculation of union 
                end;
            end;
            
            %-------------------------  Begin of Metrics 1 ------------------------------%
            % From Prof. Twan v.: Robust Community Detection Methods with Resolution Parameter for Complex Detection in Protein Protein Interaction Networks, pp.5 
            % Note do not depend on formula of Pizzuti and Rombo's: Algorithms and tools for protein-protein interaction... pp.5  
            % TP = true positive
            P = sum(PredictedClusterMatchFlag);
            if(P == 0) 
                Results(ResultsInGeneration).Precision = 0;
            else
                Results(ResultsInGeneration).Precision = P / NumberOfPredictedClusters;
            end;
            AverageMetric1(ResultsInGeneration).Precision = AverageMetric1(ResultsInGeneration).Precision + Results(ResultsInGeneration).Precision;
            if(BestMetric1(ResultsInGeneration).Precision < Results(ResultsInGeneration).Precision)
                BestMetric1(ResultsInGeneration).Precision = Results(ResultsInGeneration).Precision;
            end;
            if(WorstMetric1(ResultsInGeneration).Precision > Results(ResultsInGeneration).Precision)
                WorstMetric1(ResultsInGeneration).Precision = Results(ResultsInGeneration).Precision;
            end;
            R = sum(CmplxMatchFlag); 
            if(R == 0) 
                Results(ResultsInGeneration).Recall = 0;
            else
                Results(ResultsInGeneration).Recall = R / NumberOfGoldenCmplxes;
            end;
            AverageMetric1(ResultsInGeneration).Recall = AverageMetric1(ResultsInGeneration).Recall + Results(ResultsInGeneration).Recall;
            if(BestMetric1(ResultsInGeneration).Recall < Results(ResultsInGeneration).Recall)
                BestMetric1(ResultsInGeneration).Recall = Results(ResultsInGeneration).Recall;
            end;
            if(WorstMetric1(ResultsInGeneration).Recall > Results(ResultsInGeneration).Recall)
                WorstMetric1(ResultsInGeneration).Recall = Results(ResultsInGeneration).Recall;
            end;
            % Fmeasure = F-measure
            if(Results(ResultsInGeneration). Precision == 0) || (Results(ResultsInGeneration).Recall == 0)
                Results(ResultsInGeneration).Fmeasure = 0;
            else
                Results(ResultsInGeneration).Fmeasure = (2*Results(ResultsInGeneration).Precision * Results(ResultsInGeneration).Recall) / ...
                                        (Results(ResultsInGeneration).Precision + Results(ResultsInGeneration).Recall);
            end;
            AverageMetric1(ResultsInGeneration).Fmeasure = AverageMetric1(ResultsInGeneration).Fmeasure + Results(ResultsInGeneration).Fmeasure;
            if(BestMetric1(ResultsInGeneration).Fmeasure < Results(ResultsInGeneration).Fmeasure)
                BestMetric1(ResultsInGeneration).Fmeasure = Results(ResultsInGeneration).Fmeasure;
            end;
            if(WorstMetric1(ResultsInGeneration).Fmeasure > Results(ResultsInGeneration).Fmeasure)
                WorstMetric1(ResultsInGeneration).Fmeasure = Results(ResultsInGeneration).Fmeasure;
            end;
            %--------------------------  End of Metrics 1 ------------------------------%
            
            %-------------------------  Begin of Metrics 2 -----------------------------%
            % PPV From Twan and Elena's: Robust Community Detection Methods with Resolution... pp.5
            Numerator = sum(max(NumOfIntersect));
            if(Numerator == 0)
                Results(ResultsInGeneration).PPV = 0;
            else
                Results(ResultsInGeneration).PPV = Numerator / sum(sum(NumOfIntersect));
            end;
            AverageMetric2(ResultsInGeneration).PPV = AverageMetric2(ResultsInGeneration).PPV + Results(ResultsInGeneration).PPV;
            if(BestMetric2(ResultsInGeneration).PPV < Results(ResultsInGeneration).PPV)
                BestMetric2(ResultsInGeneration).PPV = Results(ResultsInGeneration).PPV;
            end;
            if(WorstMetric2(ResultsInGeneration).PPV > Results(ResultsInGeneration).PPV)
                WorstMetric2(ResultsInGeneration).PPV = Results(ResultsInGeneration).PPV;
            end;
            % Sensitivity  From Twan and Elena's: Robust Community Detection Methods with Resolution... pp.5
            Numerator = sum(max(NumOfIntersect'));
            Results(ResultsInGeneration).Sensitivity = Numerator / sum(NumberOfKnownProteinsInComplexes);
            AverageMetric2(ResultsInGeneration).Sensitivity = AverageMetric2(ResultsInGeneration).Sensitivity + Results(ResultsInGeneration).Sensitivity;
            if(BestMetric2(ResultsInGeneration).Sensitivity < Results(ResultsInGeneration).Sensitivity)
                BestMetric2(ResultsInGeneration).Sensitivity = Results(ResultsInGeneration).Sensitivity;
            end;
            if(WorstMetric2(ResultsInGeneration).Sensitivity > Results(ResultsInGeneration).Sensitivity)
                WorstMetric2(ResultsInGeneration).Sensitivity = Results(ResultsInGeneration).Sensitivity;
            end;
            % Accuracy ACC from Sanghamitra Bandyopadhyay ... pp. 5 Eq.(6)
            Results(ResultsInGeneration).Accuracy = sqrt(Results(ResultsInGeneration).Sensitivity * Results(ResultsInGeneration).PPV);
            AverageMetric2(ResultsInGeneration).Accuracy = AverageMetric2(ResultsInGeneration).Accuracy + Results(ResultsInGeneration).Accuracy;
            if(BestMetric2(ResultsInGeneration).Accuracy < Results(ResultsInGeneration).Accuracy)
                BestMetric2(ResultsInGeneration).Accuracy = Results(ResultsInGeneration).Accuracy;
            end;
            if(WorstMetric2(ResultsInGeneration).Accuracy > Results(ResultsInGeneration).Accuracy)
                WorstMetric2(ResultsInGeneration).Accuracy = Results(ResultsInGeneration).Accuracy;
            end;
%             -------------------------  End of Metrics 2------------------------------%
            
            %------------------------  Begin of Metrics 3 ----------------------------%
            % Calculation By Nazar M Zaki: Detection of Protein Complexes Using a Protein... pp.16
            Acc = NumOfIntersect ./ NumOfunion;
           
            [Max, Index] = max(Acc');
            MatchCmplx = find(Max >= OS);
            MatchCluster = Index(MatchCmplx);
            Denomenator = 0;
            for i = 1 : length(MatchCmplx)
                Denomenator = Denomenator + NumOfIntersect(MatchCmplx(i), MatchCluster(i));
            end;
            Results(ResultsInGeneration).RecN = Denomenator / sum(NumberOfKnownProteinsInComplexes);
            AverageMetric3(ResultsInGeneration).RecN = AverageMetric3(ResultsInGeneration).RecN + Results(ResultsInGeneration).RecN;
            if(BestMetric3(ResultsInGeneration).RecN < Results(ResultsInGeneration).RecN)
                BestMetric3(ResultsInGeneration).RecN = Results(ResultsInGeneration).RecN;
            end;
            if(WorstMetric3(ResultsInGeneration).RecN > Results(ResultsInGeneration).RecN)
                WorstMetric3(ResultsInGeneration).RecN = Results(ResultsInGeneration).RecN;
            end;
            Max = [];
            Index = [];
            MatchCmplx = [];
            MatchCluster = [];
            [Max, Index] = max(Acc);
            MatchCluster = find(Max >= OS);
            MatchCmplx = Index(MatchCluster);
            Denomenator = 0;
            for i = 1 : length(MatchCluster)
                Denomenator = Denomenator + NumOfIntersect(MatchCmplx(i), MatchCluster(i));
            end;
            Results(ResultsInGeneration).PrecN = Denomenator / sum(NumofPredictedClusterProteins);
            AverageMetric3(ResultsInGeneration).PrecN = AverageMetric3(ResultsInGeneration).PrecN + Results(ResultsInGeneration).PrecN;
            if(BestMetric3(ResultsInGeneration).PrecN < Results(ResultsInGeneration).PrecN)
                BestMetric3(ResultsInGeneration).PrecN = Results(ResultsInGeneration).PrecN;
            end;
            if(WorstMetric3(ResultsInGeneration).PrecN > Results(ResultsInGeneration).PrecN)
                WorstMetric3(ResultsInGeneration).PrecN = Results(ResultsInGeneration).PrecN;
            end;
%             Fnmeasure = Fnmeasure
            if(Results(ResultsInGeneration).PrecN == 0) || (Results(ResultsInGeneration).RecN == 0)
                Results(ResultsInGeneration).FnMeasure = 0;
            else
                Results(ResultsInGeneration).FnMeasure = (2*Results(ResultsInGeneration).PrecN * Results(ResultsInGeneration).RecN) / ...
                                        (Results(ResultsInGeneration).PrecN + Results(ResultsInGeneration).RecN);
            end;
            AverageMetric3(ResultsInGeneration).FnMeasure = AverageMetric3(ResultsInGeneration).FnMeasure + Results(ResultsInGeneration).FnMeasure;
            if(BestMetric3(ResultsInGeneration).FnMeasure < Results(ResultsInGeneration).FnMeasure)
                BestMetric3(ResultsInGeneration).FnMeasure = Results(ResultsInGeneration).FnMeasure;
            end;
            if(WorstMetric3(ResultsInGeneration).FnMeasure > Results(ResultsInGeneration).FnMeasure)
                WorstMetric3(ResultsInGeneration).FnMeasure = Results(ResultsInGeneration).FnMeasure;
            end;
            % P. 1006 of "Community Detection in Social Networks: An Indepth Benchmarking Study with a ProcedureOriented Framework"
            [NCmplx NPC] = size(NumOfIntersect);
            CCF1 = 0;
            for i = 1 : NPC
                CCF1 = CCF1 + max(NumOfIntersect(:, i)); 
            end;
            CCF1 = 0.5 * CCF1;
            CCF2 = 0;
            for j = 1 : NCmplx
                CCF2 = CCF2 + max(NumOfIntersect(j, :)); 
            end;
            CCF2 = 0.5 * CCF2;
            Results(ResultsInGeneration).CCF = CCF1 + CCF2;
            AverageMetric4(ResultsInGeneration).CCF = AverageMetric4(ResultsInGeneration).CCF + Results(ResultsInGeneration).CCF;
            if(BestMetric4(ResultsInGeneration).CCF < Results(ResultsInGeneration).CCF)
                BestMetric4(ResultsInGeneration).CCF = Results(ResultsInGeneration).CCF;
            end;
            if(WorstMetric4(ResultsInGeneration).CCF > Results(ResultsInGeneration).CCF)
                WorstMetric4(ResultsInGeneration).CCF = Results(ResultsInGeneration).CCF;
            end;
                        
            Strength = 0;
            for i = 1 : NPC
                Temp_PredictedClusterProteinLables = [];
                Temp_PredictedClusterProteinLables = find(Results(ResultsInGeneration).CmplxID == i);
                PredictedClusterProteinLables = [];
                %  OverlapComplexesFlag may be used later in our need
                Protein_index = 0;
                for Protein_i_index = 1 : length(Temp_PredictedClusterProteinLables)
                    Protein_i = Temp_PredictedClusterProteinLables(Protein_i_index);
                    if(KnownProteinsInYeast(Protein_i) ~= -1)
                        Protein_index = Protein_index + 1;
                        PredictedClusterProteinLables(Protein_index) = Protein_i;
                    end;
                end;
                Protein_in = [];
                Protein_out = [];
                N_Proteins_Cluster_i = NumofPredictedClusterProteins(i);
                Protein_in(1 : N_Proteins_Cluster_i) = 0;
                Protein_out(1 : N_Proteins_Cluster_i) = 0;
                for Protein_i_index = 1 : N_Proteins_Cluster_i
                    Protein_i = PredictedClusterProteinLables(Protein_i_index);
                    for Protein_j_index = 1 : NumInteractionProtein(Protein_i)
                        Protein_j = IndicesInteractionProtein(Protein_i, Protein_j_index);
                        if(Results(ResultsInGeneration).CmplxID(Protein_i) == ...
                           Results(ResultsInGeneration).CmplxID(Protein_j))
                                Protein_in(Protein_i_index) = Protein_in(Protein_i_index) + 1;
                        else
                                Protein_out(Protein_i_index) = Protein_out(Protein_i_index) + 1;
                        end;
                    end;
                end;
                if(Protein_in > Protein_out)
                    Score_Cluster_i = 1;  
                elseif(sum(Protein_in) > sum(Protein_out))
                    Score_Cluster_i = 0.5;
                else
                    Score_Cluster_i = 0; 
                end;
                Strength = Strength + Score_Cluster_i;
            end;
            Strength = Strength / NPC;
            Results(ResultsInGeneration).Strength = Strength;
            AverageMetric4(ResultsInGeneration).Strength = AverageMetric4(ResultsInGeneration).Strength + Results(ResultsInGeneration).Strength;
            if(BestMetric4(ResultsInGeneration).Strength < Results(ResultsInGeneration).Strength)
                BestMetric4(ResultsInGeneration).Strength = Results(ResultsInGeneration).Strength;
            end;
            if(WorstMetric4(ResultsInGeneration).Strength > Results(ResultsInGeneration).Strength)
                WorstMetric4(ResultsInGeneration).Strength = Results(ResultsInGeneration).Strength;
            end;
        end;
        %-------------------------  End of Metrics 3 -----------------------------%
        % Metrics 1
        AverageMetric1(ResultsInGeneration).Recall = AverageMetric1(ResultsInGeneration).Recall / Length;
        AverageMetric1(ResultsInGeneration).Precision = AverageMetric1(ResultsInGeneration).Precision / Length;
        AverageMetric1(ResultsInGeneration).Fmeasure = AverageMetric1(ResultsInGeneration).Fmeasure / Length;
        
        % Metrics 2
        AverageMetric2(ResultsInGeneration).Sensitivity = AverageMetric2(ResultsInGeneration).Sensitivity / Length;
        AverageMetric2(ResultsInGeneration).PPV = AverageMetric2(ResultsInGeneration).PPV / Length;
        AverageMetric2(ResultsInGeneration).Accuracy = AverageMetric2(ResultsInGeneration).Accuracy / Length;
        
        % Metrics 3
        AverageMetric3(ResultsInGeneration).RecN = AverageMetric3(ResultsInGeneration).RecN / Length;
        AverageMetric3(ResultsInGeneration).PrecN = AverageMetric3(ResultsInGeneration).PrecN / Length;
        AverageMetric3(ResultsInGeneration).FnMeasure = AverageMetric3(ResultsInGeneration).FnMeasure / Length;
        
        AverageMetric4(ResultsInGeneration).CCF = AverageMetric4(ResultsInGeneration).CCF / Length;
        AverageMetric4(ResultsInGeneration).Strength = AverageMetric4(ResultsInGeneration).Strength / Length;
        
    end;
    
    AvgBestMetric1.Recall = AvgBestMetric1.Recall + BestMetric1(ResultsSize).Recall;
    AvgBestMetric1.Precision = AvgBestMetric1.Precision + BestMetric1(ResultsSize).Precision;
    AvgBestMetric1.Fmeasure = AvgBestMetric1.Fmeasure + BestMetric1(ResultsSize).Fmeasure;
   
    AvgBestMetric2.Sensitivity = AvgBestMetric2.Sensitivity + BestMetric2(ResultsSize).Sensitivity;
    AvgBestMetric2.PPV = AvgBestMetric2.PPV + BestMetric2(ResultsSize).PPV;
    AvgBestMetric2.Accuracy = AvgBestMetric2.Accuracy + BestMetric2(ResultsSize).Accuracy;
    
    AvgBestMetric3.RecN = AvgBestMetric3.RecN + BestMetric3(ResultsSize).RecN;
    AvgBestMetric3.PrecN = AvgBestMetric3.PrecN + BestMetric3(ResultsSize).PrecN;
    AvgBestMetric3.FnMeasure = AvgBestMetric3.FnMeasure + BestMetric3(ResultsSize).FnMeasure;
    
    AvgBestMetric4.CCF = AvgBestMetric4.CCF + BestMetric4(ResultsSize).CCF;
    AvgBestMetric4.Strength = AvgBestMetric4.Strength + BestMetric4(ResultsSize).Strength;
    
    AvgWorstMetric1.Recall = AvgWorstMetric1.Recall + WorstMetric1(ResultsSize).Recall;
    AvgWorstMetric1.Precision = AvgWorstMetric1.Precision + WorstMetric1(ResultsSize).Precision;    
    AvgWorstMetric1.Fmeasure = AvgWorstMetric1.Fmeasure + WorstMetric1(ResultsSize).Fmeasure;
    
    AvgWorstMetric2.Sensitivity = AvgWorstMetric2.Sensitivity + WorstMetric2(ResultsSize).Sensitivity;    
    AvgWorstMetric2.PPV = AvgWorstMetric2.PPV + WorstMetric2(ResultsSize).PPV;
    AvgWorstMetric2.Accuracy = AvgWorstMetric2.Accuracy + WorstMetric2(ResultsSize).Accuracy;
    
    AvgWorstMetric3.RecN = AvgWorstMetric3.RecN + WorstMetric3(ResultsSize).RecN;
    AvgWorstMetric3.PrecN = AvgWorstMetric3.PrecN + WorstMetric3(ResultsSize).PrecN;
    AvgWorstMetric3.FnMeasure = AvgWorstMetric3.FnMeasure + WorstMetric3(ResultsSize).FnMeasure;
    
    AvgWorstMetric4.CCF = AvgWorstMetric4.CCF + WorstMetric4(ResultsSize).CCF;
    AvgWorstMetric4.Strength = AvgWorstMetric4.Strength + WorstMetric4(ResultsSize).Strength;

    AvgAvgMetric1.Recall = AvgAvgMetric1.Recall + AverageMetric1(ResultsSize).Recall;    
    AvgAvgMetric1.Precision = AvgAvgMetric1.Precision + AverageMetric1(ResultsSize).Precision;
    AvgAvgMetric1.Fmeasure = AvgAvgMetric1.Fmeasure + AverageMetric1(ResultsSize).Fmeasure;
    
    AvgAvgMetric2.Sensitivity = AvgAvgMetric2.Sensitivity + AverageMetric2(ResultsSize).Sensitivity;    
    AvgAvgMetric2.PPV = AvgAvgMetric2.PPV + AverageMetric2(ResultsSize).PPV;
    AvgAvgMetric2.Accuracy = AvgAvgMetric2.Accuracy + AverageMetric2(ResultsSize).Accuracy;
    
    AvgAvgMetric3.RecN = AvgAvgMetric3.RecN + AverageMetric3(ResultsSize).RecN;
    AvgAvgMetric3.PrecN = AvgAvgMetric3.PrecN + AverageMetric3(ResultsSize).PrecN;
    AvgAvgMetric3.FnMeasure = AvgAvgMetric3.FnMeasure + AverageMetric3(ResultsSize).FnMeasure;
    
    AvgAvgMetric4.CCF = AvgAvgMetric4.CCF + AverageMetric4(ResultsSize).CCF;
    AvgAvgMetric4.Strength = AvgAvgMetric4.Strength + AverageMetric4(ResultsSize).Strength;
end;

% Average Results of N Runs
AvgBestMetric1.Recall = AvgBestMetric1.Recall / MaxRuns;
AvgBestMetric1.Precision = AvgBestMetric1.Precision / MaxRuns;
AvgBestMetric1.Fmeasure = AvgBestMetric1.Fmeasure / MaxRuns;

AvgBestMetric2.Sensitivity = AvgBestMetric2.Sensitivity / MaxRuns;
AvgBestMetric2.PPV = AvgBestMetric2.PPV / MaxRuns;
AvgBestMetric2.Accuracy = AvgBestMetric2.Accuracy / MaxRuns;

AvgBestMetric3.RecN = AvgBestMetric3.RecN / MaxRuns;
AvgBestMetric3.PrecN = AvgBestMetric3.PrecN / MaxRuns;
AvgBestMetric3.FnMeasure = AvgBestMetric3.FnMeasure / MaxRuns;

AvgBestMetric4.CCF = AvgBestMetric4.CCF / MaxRuns;
AvgBestMetric4.Strength = AvgBestMetric4.Strength / MaxRuns;

AvgWorstMetric1.Recall = AvgWorstMetric1.Recall / MaxRuns;
AvgWorstMetric1.Precision = AvgWorstMetric1.Precision / MaxRuns;
AvgWorstMetric1.Fmeasure = AvgWorstMetric1.Fmeasure / MaxRuns;

AvgWorstMetric2.Sensitivity = AvgWorstMetric2.Sensitivity / MaxRuns;
AvgWorstMetric2.PPV = AvgWorstMetric2.PPV / MaxRuns;
AvgWorstMetric2.Accuracy = AvgWorstMetric2.Accuracy / MaxRuns;

AvgWorstMetric3.RecN = AvgWorstMetric3.RecN / MaxRuns;
AvgWorstMetric3.PrecN = AvgWorstMetric3.PrecN / MaxRuns;
AvgWorstMetric3.FnMeasure = AvgWorstMetric3.FnMeasure / MaxRuns;

AvgWorstMetric4.CCF = AvgWorstMetric4.CCF / MaxRuns;
AvgWorstMetric4.Strength = AvgWorstMetric4.Strength / MaxRuns;


AvgAvgMetric1.Recall = AvgAvgMetric1.Recall / MaxRuns;
AvgAvgMetric1.Precision = AvgAvgMetric1.Precision / MaxRuns;
AvgAvgMetric1.Fmeasure = AvgAvgMetric1.Fmeasure / MaxRuns;

AvgAvgMetric2.Sensitivity = AvgAvgMetric2.Sensitivity / MaxRuns;
AvgAvgMetric2.PPV = AvgAvgMetric2.PPV / MaxRuns;
AvgAvgMetric2.Accuracy = AvgAvgMetric2.Accuracy / MaxRuns;

AvgAvgMetric3.RecN = AvgAvgMetric3.RecN / MaxRuns;
AvgAvgMetric3.PrecN = AvgAvgMetric3.PrecN / MaxRuns;
AvgAvgMetric3.FnMeasure = AvgAvgMetric3.FnMeasure / MaxRuns;

AvgAvgMetric4.CCF = AvgAvgMetric4.CCF / MaxRuns;
AvgAvgMetric4.Strength = AvgAvgMetric4.Strength / MaxRuns;

save(strcat(strcat('Repositories/EA_', ...
                   'FinalStats_OS', num2str(OS), ...
                   'PPI', int2str(NetworkNumber)),'.mat'), ...
                   'AvgBestMetric1', 'AvgBestMetric2', 'AvgBestMetric3', 'AvgBestMetric4', ...
                   'AvgWorstMetric1', 'AvgWorstMetric2', 'AvgWorstMetric3', 'AvgWorstMetric4', ...
                   'AvgAvgMetric1', 'AvgAvgMetric2', 'AvgAvgMetric3', 'AvgAvgMetric4');

AvgBestMetric1
AvgBestMetric2
AvgBestMetric3
AvgBestMetric4
end
