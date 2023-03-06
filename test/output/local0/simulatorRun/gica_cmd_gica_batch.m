%% Batch script for running gica

%% Performance type
perfType = 1;
%% Reliability analysis
which_analysis = 1;
%% Output directory
outputDir = '/output/local0/simulatorRun';

%% Output files prefix
prefix = 'gica_cmd';

dataSelectionMethod = 4;

%% modalityType may be fMRI, EEG, and smr 
modalityType = 'sMRI';

%% Input file patterns
input_data_file_patterns = {'/input/local0/simulatorRun/sub-001_task-sbm_bold_prev.nii';
};

%% Dummy scans
dummy_scans = 0;
%% Input mask
maskFile = '/computation/local_data/mask.nii';

%% PCA Algorithm
pcaType = 'Standard';
%% ICA Algorithm
algoType = 16;
%% Back-reconstruction type
backReconType = 5;
%% Pre-processing type
preproc_type = 1;
%% Number of data reduction steps
numReductionSteps = 2;
%% MDL Estimation 
doEstimation = 0;
%% Number of PC in the first PCA step
numOfPC1 = 5;
%% Number of PC in the second PCA step
numOfPC2 = 4;
%% Scaling type 
scaleType = 0;
%% Spatial references 
refFiles = {'/computation/local_data/NeuroMark.nii';
};

%% Report generator 
display_results = 1;
