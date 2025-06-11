function [ComplexType, ProteinType,ComplexName,ProteinName] = LoadComplexProteinDataSet(SelectedComplexProteinType)


%Data for Complex as well as Protein. 
[ComplexType,ComplexName] = DataComplex(SelectedComplexProteinType)
[ProteinType,ProteinName] = DataProtein(SelectedComplexProteinType)
