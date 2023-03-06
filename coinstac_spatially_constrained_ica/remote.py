"""
Created on Mon March 6 2023

@author: Debbrata Saha
"""

import sys
import ujson as json
from utils import listRecursive
import numpy as np
import matplotlib.pyplot as plt

def scica_remote_noop(args):

    # concat the loading parameters from all sites
    concat_loading_parameters = np.vstack([np.load(os.path.join(args["state"]["baseDirectory"], site, args["input"][site]["loading_parameter"])) for site in args["input"]])

    # compute the correlation matrix
    correlation_matrix = np.corrcoef(concat_loading_parameters)

    # plot correlation matrix
    plt.imshow(correlation_matrix)
    plt.title('Correlation map of loading parameters')
    c = plt.colorbar()
    plt.clim(-1, 1)

    # save figure and send to each local site
    pl.savefig(os.path.join(args['state']['outputDirectory'],'loading_correlation_map.png'))
    pl.savefig(os.path.join(args['state']['transferDirectory'], 'loading_correlation_map.png'))

    computation_output = {}
    computation_output['success'] = True
    computation_output['output'] = {}
    computation_output['output']['final_embedding'] = 0
    computation_output['output']['file_name'] = 'sample_fig.png'

    return json.dumps(computation_output)


if __name__ == '__main__':
    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if phase_key == 'scica_local_1':
        computation_output = spatially_constrained_ica_remote_noop(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Local")
