% ---------------------------------------------------------------------------------------%
%                         EA Repositories Statistics                                     %
% ---------------------------------------------------------------------------------------%
N = 990;
MaxRun = 30;
for RunNumber = 1 : MaxRun
    load(strcat(strcat('Repositories/EA_', ...
                        'PPI_1_Run_', int2str(RunNumber)),'.mat'),'ResultsGroup');
    Number_of_Complexes = max(ResultsGroup(100).CmplxID);
    Best_Structure = [];
    for ComplexCounter = 1 : Number_of_Complexes
         Best_Structure(ComplexCounter).ProteinsInComplex = find (ResultsGroup(100).CmplxID == ComplexCounter);
         Best_Structure(ComplexCounter).Length = length(Best_Structure(ComplexCounter).ProteinsInComplex );
    end; 
    Best_StructureInfo(RunNumber).Number_of_Complexes = Number_of_Complexes;
    Best_StructureInfo(RunNumber).MaxComplexSize = max ([Best_Structure(:).Length].');
    Best_StructureInfo(RunNumber).MinComplexSize = min ([Best_Structure(:).Length].');
    Best_StructureInfo(RunNumber).AvgComplexSize = N / Number_of_Complexes;
end
Avg_Structure.AvgMax_Complexsize = sum([Best_StructureInfo.MaxComplexSize].')/30;
Avg_Structure.AvgMin_Complexsize = sum([Best_StructureInfo.MinComplexSize].')/30;
Avg_Structure.AvgAvg_Complexsize = sum([Best_StructureInfo.AvgComplexSize].')/30;
Avg_Structure.Avg_Number_of_Complexes = sum([Best_StructureInfo.Number_of_Complexes].')/30;



 save('Repositories/EA_PPI_All_Runs.mat','Best_StructureInfo','Avg_Structure');  