#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 2 11:25:00 2018 (MDT)

@author: Rogers F. Silva
"""

import json
import os
import sys
import numpy as np
import utils as ut
from . import local_ancillary as la


def dpca_local_1(args):
    """ Parse input data and parameters, trigger computation of the local PCA, send results to remote

    Parameters
    ----------
    args : dict
        Example:
        {
        "input": {
            "data": [
                [
                    "local0.sub0.data.npz",
                    "local0.sub1.data.npz",
                    "local0.sub2.data.npz",
                    "local0.sub3.data.npz",
                    "local0.sub4.data.npz"
                ],
                [
                    "npzfile"
                ]
            ],
            "num_PC_global": 20,
            "axis": -1,
            "mean_values": [
                [
                    "row_mean_global.npz"
                ],
                [
                    "npzfile"
                ]
            ],
            "subject_level_PCA": false,
            "subject_level_num_PC": 120
        },
        "cache": {}
        }

    Returns
    -------
    computation_output : dict
        Example:
        {
        "output": {
            "reduced_data": reduced_data,
            "num_PC_global": num_PC_global,
            "computation_phase": 'local_1'
        },
        "cache": {}
        }

    """

    state = args['state']
    inputs = args['input']
    cache = args['cache']

    # Input data files
    file_list = inputs['data'][0]
    data_file_list = [
        os.path.join(state["baseDirectory"], file) for file in file_list
    ]
    data_file_type = inputs['data'][1][0]
    # Read local input data files
    datasets = ut.read_data(data_file_list, data_file_type, 'dataset',
                            state['clientId'])

    # Global Number of Principal Components
    num_PC_global = inputs['num_PC_global']

    # Dimension to Be Reduced
    axis = inputs['axis']

    # Define mean_removal tuple
    if axis == -1:
        # Check if Global (Row) Mean Values provided
        file_list = inputs['mean_values'][0]
        if file_list:
            # Row mean files
            row_mean_file_list = [
                os.path.join(state["baseDirectory"], file)
                for file in file_list
            ]
            row_mean_file_type = inputs['mean_values'][1][0]
            # Read local row mean files
            row_mean = ut.read_data(row_mean_file_list, row_mean_file_type,
                                    'row_mean_global', state['clientId'])['0']
        else:
            row_mean = None

        mean_removal = (axis, row_mean)
    elif axis == -2:
        # Column means are always computed locally, on-the-fly
        mean_removal = (axis, None)

    # Subject-Level PCA
    subject_level_PCA = inputs['subject_level_PCA']

    # Number of Principal Components in Subject-Level PCA
    subject_level_num_PC = inputs['subject_level_num_PC']

    # Start local computation:
    reduced_data, projM_local, bkprojM_local = la.local_PCA(
        datasets,
        num_PC=5 * num_PC_global,
        mean_removal=mean_removal,
        subject_level_PCA=subject_level_PCA,
        subject_level_num_PC=subject_level_num_PC)

    # Save local projection and backprojection matrices
    # Option currently not supported.

    # Compile results to be transmitted to remote and cached for reuse in next iteration
    computation_output = {
        "output": {
            # "datasets": {ix:X.tolist() for (ix,X) in datasets.items()},
            "reduced_data": reduced_data.tolist(),
            "num_PC_global": num_PC_global,
            "computation_phase": 'dpca_local_1'
        },
        "cache": dict()
    }

    return computation_output


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        computation_output = local_1(parsed_args)
        # Transmit results to remote
        # as file (for large volumes of data, OS overhead):

        # as JSON string (for smaller volumes of data, JSON conversion overhead):
        sys.stdout.write(json.dumps(computation_output))
    else:
        raise ValueError("Error occurred at Local")
