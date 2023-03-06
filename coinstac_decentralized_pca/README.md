# decentralized-pca
This repository contains code for decentralized PCA written for the new COINSTAC simulator (`v4.0.0`).

## Files
1. local.py - reads input data and parameters, triggers computation of the local PCA, then sends results to remote site.
2. remote.py - aggregates the local PCA results sent by local sites and returns the global PCA.
3. compspec.json - computation specifications.
4. ancillary.py - contains general computation subroutines utilized both by local and remote.
5. local_ancillary.py - contains functions that implement different steps of the local computation.
6. utils.py - utility functions.

## Written For
- Python 3.6.6
- coinstac-simulator 4.0.0

## Usage
1. Update `npm`:\
`sudo npm i npm@latest -g`
2. Install `coinstac-simulator`:\
`sudo npm i -g coinstac-simulator@4.0.0`
3. Clone this repository:\
`git clone https://github.com/rsilva8/decentralized-pca`
4. Change directory:\
`cd decentralized-pca`
5. Build the docker image (Docker must be running):\
`docker build -t decentralized-pca .`
7. Run the code:\
`sudo coinstac-simulator`
