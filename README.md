# Decentralized Constrained Source Based Morphometry (dcSBM) 


## Running in the Simulator

This pipeline has been tested with the latest version of the COINSTAC simulator.


Install the simulator:

```
npm i -g coinstac-simulator
```

Download this repository

```
git clone https://github.com/trendscenter/decentralized-source-based-morphometry.git
```

Initialize submodules

```
git submodule update --init --recursive
```

Copy the mask and template into the local input folders, using the bash script

```
bash copy_data.sh
```

*or* the following commands

```
cp test/remote/simulatorRun/mask.nii test/local0/simulatorRun/ ;
cp test/remote/simulatorRun/mask.nii test/local1/simulatorRun/ ;
```

Input types
```
Data needs to be preprocessed
Input files should be placed under the '/test/input/local_/simulatorRun/' directory
The input can be provided either separately (a single Nifti file for each subject) or combined (concatenate all input files together) 
There is no need to provide the covariate file
```

Finally, run using the bash script (will require entry of password for **sudo**)

```
bash run.sh
```

*or*

Run using the following commands

```
sudo docker build  -t dsbm .
sudo coinstac-simulator
```


