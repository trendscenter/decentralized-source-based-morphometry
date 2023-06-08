"""
Created on Mon March 6 2023

@author: Debbrata Saha
"""

import sys
import os
import ujson as json
import utils as ut
from utils import listRecursive
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def scica_remote_noop(args):

    # concat the loading parameters from all sites
    for site in args["input"]:
        temp_lp=np.load(os.path.join(args["state"]["baseDirectory"], site, args["input"][site]["loading_parameter"]));
        ut.log("Received loading parameters shape for site local-"+str(site)+" : "+str(temp_lp.shape), args["state"])

    concat_loading_parameters = np.vstack([np.load(os.path.join(args["state"]["baseDirectory"], site, args["input"][site]["loading_parameter"])) for site in args["input"]])
    ut.log("Stacked loading parameters shape: "+str(concat_loading_parameters.shape), args["state"])

    corr_dataframe = pd.DataFrame(concat_loading_parameters)

    # compute the correlation 
    corr_matrix = corr_dataframe.corr(method='pearson')

    #ut.log("Computed correlation matrix ", args["state"])

    # plot correlation matrix
    plt.imshow(corr_matrix)
    plt.title('Correlation Map')
    c = plt.colorbar()
    plt.clim(-1, 1)

    #ut.log("plotting correlation matrix ", args["state"])
    # save figure and send to each local site
    plt.savefig(os.path.join(args['state']['outputDirectory'],'loading_correlation_map.png'))
    plt.savefig(os.path.join(args['state']['transferDirectory'], 'loading_correlation_map.png'))

    ut.log("saving correlation matrix plots in output and transfer dirs", args["state"])
    computation_output = {}
    computation_output['success'] = True
    computation_output['output'] = {}
    computation_output['output']['final_embedding'] = 0
    computation_output['output']['file_name'] = 'sample_fig.png'
    computation_output['state'] = args["state"]

    return computation_output


if __name__ == '__main__':
    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if phase_key == 'scica_local_1':
        computation_output = spatially_constrained_ica_remote_noop(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Local")
