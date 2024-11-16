"""
Created on Mon March 6 2023

@author: Debbrata Saha
"""

import sys
import ujson as json
from .BackRecon import gift_gica
import utils as ut
import os
import glob
import numpy as np
import nibabel as nib
import pandas as pd

from . import ancillary as anc

sys.path.append("../..")
from coinstac_regression_vbm import parsers as reg_vbm_par
from coinstac_regression_vbm import local_ancillary as reg_vbm_loc_anc
from coinstac_regression_vbm import ancillary as reg_vbm_anc
from coinstac_regression_vbm import rw_utils as reg_vbm_rw_ut

loading_parameters = 'gica_cmd_group_loading_coeff_.nii'


def scica_local_0(args):
    state = args["state"]
    ut.log("11111111111111111111111111111111111 ", state)
    cache_dir = state["cacheDirectory"]

    # Load covariates
    categorical_dict, covar_x = reg_vbm_par.parse_for_categorical(args)

    in_files = [os.path.join(state['baseDirectory'], f) for f in covar_x.index]
    
    maskfile = anc.validate_file(args, args["input"]["mask"],
                               os.path.join('/computation', 'local_data', 'mask.nii'))
    ut.log("111111111111111111111111111111111112 ", state)

    scica_template = anc.validate_file(args, args["input"]["scica_template"],
                                      os.path.join('/computation', 'local_data', 'Neuromark_sMRI_1.0_modelorder-30_2x2x2.nii'))

    pyscript = os.path.join(state["outputDirectory"], 'pyscript_gicacommand.m')
    ut.log("111111111111111111111111111111111113 ", state)

    if os.path.exists(pyscript):
        os.remove(pyscript)
    ut.log("1111111111111111111111111111111111133 ", state)
    output = gift_gica(
            in_files=in_files,
            refFiles=[scica_template],
            mask=maskfile,
            out_dir=state["outputDirectory"],
            state=state,
        )
    ut.log("111111111111111111111111111111111114 ", state)
    load_loading_parameter = nib.load(os.path.join(args['state']['outputDirectory'],
                                                   'gica_cmd_group_loading_coeff_.nii'))
    ut.log("111111111111111111111111111111111115 ", state)
    loading_parameter = np.array(load_loading_parameter.dataobj)
    
    ut.log("loading parameters shape: "+str(loading_parameter.shape), args["state"])
    #raise Exception(loading_parameter)

    # send files to transfer directory and save in cache
    np.save(os.path.join(args['state']['transferDirectory'], 'loading_parameter.npy'), loading_parameter)
    np.save(os.path.join(cache_dir, 'loading_parameter.npy'), loading_parameter)

    # file = open(os.path.join(args['state']['transferDirectory'], 'loading_parameter.txt'), "w")
    # loading_parameter = np.array(loading_parameter)
    # content = str(loading_parameter)
    # file.write(content)
    # file.close()



    #computation_output = {
    #    "output": {
    #        "loading_parameter": 'loading_parameter.npy',
    #        "computation_phase": "scica_local_1"
    #    }
    #}

    # Adding code to perform regression using loading paramereters
    #covar_x.to_parquet(os.path.join(cache_dir, "X_df"))
    covar_x.to_pickle(os.path.join(cache_dir, "X_df"))
    # converting all the values of the reference columns to lowercase as
    # all the covariate values are converted to lowercase while parsing
    # in parsers.parse_covar_info()
    reference_dict = dict((k, v.lower()) for k,v in args["input"]["reference_columns"].items())

    output_dict = {
        "categorical_dict": categorical_dict,
        "reference_columns": reference_dict,
        'loading_parameter': 'loading_parameter.npy',
        'computation_phase': 'scica_local_0'
    }
    cache_dict = {
        "covariates": "X_df",
        'loading_parameter': 'loading_parameter.npy'
    }

    computation_output = {
      "output": output_dict,
      "cache": cache_dict,
      "state": state
    }

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output


def scica_local_1(args):

    """The second function in the local computation chain"""
    cache_ = args["cache"]
    state_ = args["state"]
    output_dir = state_["transferDirectory"]
    cache_dir = state_["cacheDirectory"]


    #X = pd.read_parquet(os.path.join(cache_dir, cache_["covariates"]))
    X = pd.read_pickle(os.path.join(cache_dir, cache_["covariates"]))

    ut.log("args received to local_1 : "+str(args), state_)
    # Local Statistics
    #encoded_X, y = reg_vbm_loc_anc . vbm_parser(args, X) #Replaced this with the below 2 lines

    encoded_X = reg_vbm_par.perform_encoding(args, X)
    y = np.load(os.path.join(cache_dir, cache_["loading_parameter"]));

    meanY_vector, lenY_vector = reg_vbm_loc_anc.mean_and_len_y(y)
    local_beta, local_stats_list, local_r_squared, local_X_labels = reg_vbm_loc_anc.local_stats_to_dict_numba(args, encoded_X, y)
    ut.log(f'local_stats_list: {str(local_stats_list)}', state_)
    ut.log(f'beta_shape: {local_beta} ', state_)
    ut.log(f'r_squared: {local_r_squared}', state_)

    anc.print_beta_vectors(args, local_beta, "beta_vector_local", local_X_labels)
    anc.print_rsquared(args, local_r_squared, "r_squared_local")
    local_stats_list = sorted(os.listdir(args["state"]["outputDirectory"]))

    # Global Statistics
    augmented_X = reg_vbm_loc_anc.add_site_covariates(args, X)
    X_labels = list(augmented_X.columns)
    biased_X = augmented_X.values.astype("float64")

    ut.log("Encoded array columns : "+str(list(encoded_X.sort_index(axis=1).columns)), state_);
    ut.log("Augmented array columns : "+str(list(augmented_X.sort_index(axis=1).columns)), state_);

    ut.log("size of biased_X : "+ str(biased_X.shape), state_);
    ut.log("size of y : "+ str(y.shape), state_);

    XtransposeX_local = reg_vbm_loc_anc.multiply(biased_X, biased_X)
    Xtransposey_local = reg_vbm_loc_anc.multiply(biased_X, y)

    # Writing covariates and dependents to cache as files
    reg_vbm_anc.saveBin(os.path.join(cache_dir, "X.npy"), biased_X)
    reg_vbm_anc.saveBin(os.path.join(cache_dir, "y.npy"), y)

    # Writing XTX and XTy to output as files
    reg_vbm_anc.saveBin(os.path.join(output_dir, "XTX.npy"), XtransposeX_local)
    reg_vbm_anc.saveBin(os.path.join(output_dir, "XTy.npy"), Xtransposey_local)

    output_dict = {
        "XtransposeX_local": "XTX.npy",
        "Xtransposey_local": "XTy.npy",
        "mean_y_local": meanY_vector.tolist(),
        "count_local": lenY_vector.tolist(),
        "local_stats_list": local_stats_list,
        "X_labels": X_labels,
    }
    cache_dict = {"covariates": "X.npy", "dependents": "y.npy",
                  "reference_columns": args["input"]["reference_columns"]}

    reg_vbm_rw_ut.write_file(args, output_dict, "output", "local_output")

    computation_output_dict = {
        "output": {"computation_phase": "scica_local_1"},
        "cache": cache_dict,
    }

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output_dict


def scica_local_2(args):

    input_ = args["input"]
    cache_ = args["cache"]
    state_ = args["state"]
    cache_dir = state_["cacheDirectory"]

    biased_X = reg_vbm_anc.loadBin(os.path.join(cache_dir, cache_["covariates"]))
    y = reg_vbm_anc.loadBin(os.path.join(cache_dir, cache_["dependents"]))

    avg_beta_vector = reg_vbm_anc.loadBin(
        os.path.join(args["state"]["baseDirectory"], input_["avg_beta_vector"])
    )

    mean_y_global = reg_vbm_anc.loadBin(
        os.path.join(args["state"]["baseDirectory"], input_["mean_y_global"])
    )

    varX_matrix_local = reg_vbm_loc_anc.multiply(biased_X, biased_X)

    sse_local, sst_local = reg_vbm_loc_anc.stats_calculation(
        biased_X, y, avg_beta_vector, mean_y_global
    )

    output_dict = {
        "SSE_local": sse_local.tolist(),
        "SST_local": sst_local.tolist(),
        "varX_matrix_local": varX_matrix_local.tolist(),
    }

    reg_vbm_rw_ut.write_file(args, output_dict, "output", "local_output")

    output_dict = {"computation_phase": "scica_local_2"}
    cache_dict = {}
    computation_output_dict = {"output": output_dict, "cache": cache_dict}

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output_dict

def scica_check_out(args):
    state = args["state"]
    gigica_dir = os.path.join(state["outputDirectory"], "gica_gmc_gica_results")
    output_dict = {
        "gigica_output": None
    }
    if os.path.exists(gigica_dir):
        output_dict["gigica_output"] = gigica_dir
    cache_dict = {}
    computation_output = {
        "output": output_dict,
        "cache": cache_dict,
        "state": state
    }
    return computation_output


def scica_local_phases(parsed_args):

    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        return scica_local_0(parsed_args)
    elif "scica_remote_0" in phase_key:
        return scica_local_1(parsed_args)
    elif "scica_remote_1" in phase_key:
        return scica_local_2(parsed_args)
    else:
        raise ValueError("Error occurred at Local")


if __name__ == '__main__':
    parsed_args = json.loads(sys.stdin.read())
    scica_local_phases(parsed_args)
