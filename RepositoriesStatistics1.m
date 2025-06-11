% ---------------------------------------------------------------------------------------%
%                         EA Repositories Statistics                                     %
% ---------------------------------------------------------------------------------------%
N=990;
MaxRun = 30;
for RunNumber = 1 : MaxRun
    load(strcat(strcat('Repositories/EA_', ...
                        'PPI_1_Run_', int2str(RunNumber)),'.mat'),'ResultsGroup');
    ComplexNO = max(ResultsGroup(100).CmplxID);
    for ComplexCount = 1 : ComplexNO
         BestSol(ComplexCount).ProteinsInComplex = find (ComplexCount==ResultsGroup(100).CmplxID);
         BestSol(ComplexCount).Length = length(BestSol(ComplexCount).ProteinsInComplex );
    end; 
    BestSolsInfo(RunNumber).ComplexNO = ComplexNO;
    BestSolsInfo(RunNumber).MaxComplexSize = max ([BestSol(:).Length].');
    BestSolsInfo(RunNumber).MinComplexSize = min ([BestSol(:).Length].');
    BestSolsInfo(RunNumber).AvgComplexSize = N / ComplexNO;
end
Avg_info.AvgMaxComplexsize = sum([BestSolsInfo.MaxComplexSize].')/30;
Avg_info.AvgMinComplexsize = sum([BestSolsInfo.MinComplexSize].')/30;
Avg_info.AvgAvgComplexsize = sum([BestSolsInfo.AvgComplexSize].')/30;

 save('Repositories/EA_PPI_All_Run.mat','BestSolsInfo','Avg_info');  