#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 16:07:00 2018 (MDT)

@author: Rogers F. Silva
"""

import json
import os
import sys
import numpy as np
from . import ancillary as an
import utils as ut


def dpca_remote_1(args):
    """ Parse input data and parameters, trigger computation of the local PCA, send results to remote

    Parameters
    ----------
    args : dict
        Example:
        {
        "input": {
            "local0": {
                "reduced_data": reduced_data,
                "num_PC_global": num_PC_global,
                "computation_phase": 'local_1'
            },
            "local1": {
                "reduced_data": reduced_data,
                "num_PC_global": num_PC_global,
                "computation_phase": 'local_1'
            },
            "local2": {
                "reduced_data": reduced_data,
                "num_PC_global": num_PC_global,
                "computation_phase": 'local_1'
            }
        },
        "state": {
            "baseDirectory":
            "outputDirectory":
            "cacheDirectory":
            "clientId": remote
        },
        "cache": {}
        }

    Returns
    -------
    computation_output : dict
        Example:
        {
        "output": {
            "PC_global": PC_global
        },
        "cache": {},
        "success": True
        }

    """

    state = args['state']
    inputs = args['input']
    cache = args['cache']

    # Start remote computation:

    # Concatenate all local reduced_data along columns
    all_reduced_data = np.hstack(
        tuple(
            np.array(si['reduced_data']) for (localID, si) in inputs.items()))

    # Global Number of Principal Components
    num_PC_global = np.hstack(
        tuple(si['num_PC_global'] for (localID, si) in inputs.items())).max()

    # Compute global principal components
    PC_global, _, _ = an.base_PCA(all_reduced_data,
                                  num_PC=num_PC_global,
                                  axis=-1,
                                  whitening=False)

    # # Concatenate all raw local datasets along columns
    # all_data = np.hstack(
    #     tuple(np.array(su)
    #           for (localID,si) in inputs.items()
    #           for (subID,su) in si['datasets'].items()
    #     )
    # )
    #
    # # Compute global number of columns over all local num_cols
    # PC_global_true, _, _ = an.base_PCA(all_data-all_data.mean(axis=-1)[:,None],
    #                                    num_PC=num_PC_global,
    #                                    axis=-1,
    #                                    whitening=False)

    # Compile results to be transmitted to local sites and cached for reuse in next iteration
    computation_output = {
        "output": {
            "PC_global": PC_global.tolist(),
            "computation_phase": "dpca_remote_1"
        },
        "cache": dict(),
        "success": True
    }

    #output_file = os.path.join(state['outputDirectory'], 'row_mean_global.data')
    #np.savetxt(output_file, row_mean_global, fmt='%.6f')

    #import pdb; pdb.set_trace()
    return computation_output


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        raise ValueError(
            "Error occurred at Remote: missing phase key from local site(s).")
    elif "local_1" in phase_key:
        computation_output = remote_1(parsed_args)
        # Transmit results to remote
        # as file (for large volumes of data; OS overhead):

        # as JSON string (for smaller volumes of data; JSON conversion overhead):
        sys.stdout.write(json.dumps(computation_output))
    else:
        raise ValueError("Error occurred at Remote: unknown phase key.")
