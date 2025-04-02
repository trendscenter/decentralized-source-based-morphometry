"""
Created on Mon March 6 2023

@author: Debbrata Saha
"""

import sys
import os
import shutil
import ujson as json
import jsonpickle
import utils as ut
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd

from . import ancillary as anc

sys.path.append("../..")
from coinstac_regression_vbm import remote_ancillary as reg_vbm_rem_anc
from coinstac_regression_vbm import ancillary as reg_vbm_anc
from coinstac_regression_vbm import rw_utils as reg_vbm_rw_ut

def scica_remote_0(args):

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
    plt.imshow(corr_matrix, cmap='jet')
    plt.title('Correlation Map')
    c = plt.colorbar()
    plt.clim(-1, 1)

    #ut.log("plotting correlation matrix ", args["state"])
    # save figure and send to each local site
    plt.savefig(os.path.join(args['state']['outputDirectory'],'global_loading_correlation_map.png'))
    plt.savefig(os.path.join(args['state']['transferDirectory'], 'global_loading_correlation_map.png'))

    ut.log("saving correlation matrix plots in output and transfer dirs", args["state"])

    #Perform regression logic

    input_ = args["input"]
    site_info = {site: input_[site]["categorical_dict"] for site in input_.keys()}
    ref_cols = {site: input_[site]["reference_columns"] for site in input_.keys()}
    ut.log("args received to remote_0 : "+str(args), args["state"])
    ut.log("Reference columns received for dummy encoding: "+ str(ref_cols), args["state"] )

    reference_dict=next(iter(ref_cols.values()))
    # assert that reference columns/values for dummy encoding are same across all the sites for
    # the correctness of the decentralized regression. This is always true for coinstac GUI computation.
    assert all(value == reference_dict  for value in ref_cols.values()), \
        "Reference values for dummy encoding are not same across all the sites "+ str(ref_cols)

    df = pd.DataFrame.from_dict(site_info)
    covar_keys, unique_count = reg_vbm_rem_anc.return_uniques_and_counts(df)

    output_dict= {
        "final_embedding" : 0,
        "file_name" : 'sample_fig.png',
        "covar_keys": jsonpickle.encode(covar_keys, unpicklable=False),
        "reference_columns": reference_dict,
        "global_unique_count": unique_count,
        "computation_phase": "scica_remote_0",
    }

    computation_output = {
        "output": output_dict,
        "cache": {},
        "state": args["state"]
    }

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output


def scica_remote_1(args):
    """The second function in the local computation chain"""
    input_ = args["input"]
    state_ = args["state"]
    input_dir = state_["baseDirectory"]
    cache_dir = state_["cacheDirectory"]

    site_list = input_.keys()
    user_id = list(site_list)[0]

    input_list = dict()

    for site in site_list:
        file_name = os.path.join(input_dir, site, "local_output")
        input_list[site] = reg_vbm_rw_ut.read_file(args, "input", file_name)

    X_labels = input_list[user_id]["X_labels"]

    all_local_stats_dicts = [
        input_list[site]["local_stats_list"] for site in input_list
    ]

    beta_vector_0 = sum(
        [
            reg_vbm_anc.loadBin(
                os.path.join(input_dir, site, input_list[site]["XtransposeX_local"])
            )
            for site in input_list
        ]
    )

    beta_vector_1 = sum(
        [
            reg_vbm_anc.loadBin(
                os.path.join(input_dir, site, input_list[site]["Xtransposey_local"])
            )
            for site in input_list
        ]
    )

    try:
        avg_beta_vector = np.transpose(
            np.dot(np.linalg.inv(beta_vector_0), beta_vector_1)
        )
    except np.linalg.LinAlgError:
        cond = np.linalg.cond(beta_vector_0.T @ beta_vector_0);
        raise Exception(f"X.^T*X matrix at remote is Singular with condition number: {cond}")

    mean_y_local = [input_list[site]["mean_y_local"] for site in input_list]
    count_y_local = [np.array(input_list[site]["count_local"]) for site in input_list]
    mean_y_global = np.array(mean_y_local) * np.array(count_y_local)
    mean_y_global = np.sum(mean_y_global, axis=0) / np.sum(count_y_local, axis=0)

    dof_global = sum(count_y_local) - avg_beta_vector.shape[1]

    reg_vbm_anc.saveBin(
        os.path.join(args["state"]["transferDirectory"], "avg_beta_vector.npy"),
        avg_beta_vector,
    )
    reg_vbm_anc.saveBin(
        os.path.join(args["state"]["transferDirectory"], "mean_y_global.npy"),
        mean_y_global,
    )

    reg_vbm_anc.saveBin(
        os.path.join(args["state"]["cacheDirectory"], "avg_beta_vector.npy"),
        avg_beta_vector,
    )

    output_dict = {
        "avg_beta_vector": "avg_beta_vector.npy",
        "mean_y_global": "mean_y_global.npy",
        "computation_phase": "scica_remote_1",
    }

    cache_dict = {
        "avg_beta_vector": "avg_beta_vector.npy",
        "dof_global": dof_global.tolist(),
        "X_labels": X_labels,
        "local_stats_dict": all_local_stats_dicts,
    }

    computation_output_dict = {"output": output_dict, "cache": cache_dict}

    file_name = os.path.join(cache_dir, "remote_cache")
    with open(file_name, "w") as file_h:
        input_list[site] = json.dump(cache_dict, file_h)

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output_dict


def scica_remote_2(args):

    cache_ = args["cache"]
    state_ = args["state"]
    input_dir = state_["baseDirectory"]
    cache_dir = state_["cacheDirectory"]

    input_list = dict()
    site_list = args["input"].keys()
    for site in site_list:
        file_name = os.path.join(input_dir, site, "local_output")
        with open(file_name, "r") as file_h:
            input_list[site] = json.load(file_h)

    cache_list = reg_vbm_rw_ut.read_file(args, "cache", "remote_cache")

    X_labels = args["cache"]["X_labels"]

    all_local_stats_dicts = cache_["local_stats_dict"]

    avg_beta_vector = reg_vbm_anc.loadBin(os.path.join(cache_dir, cache_list["avg_beta_vector"]))
    dof_global = cache_list["dof_global"]

    SSE_global = sum([np.array(input_list[site]["SSE_local"]) for site in input_list])
    SST_global = sum([np.array(input_list[site]["SST_local"]) for site in input_list])
    varX_matrix_global = sum(
        [np.array(input_list[site]["varX_matrix_local"]) for site in input_list]
    )

    r_squared_global = 1 - (SSE_global / SST_global)
    MSE = SSE_global / np.array(dof_global)
    ts_global = reg_vbm_rem_anc.remote_stats(MSE, varX_matrix_global, avg_beta_vector)
    ps_global = [2 * stats.t.sf(np.abs(t), df) for t, df in zip(ts_global, dof_global)]

    ut.log(f'ts-global shape" : {str(np.shape(ts_global))}', args["state"])
    ut.log(f'ps-global shape" : {str(np.shape(ps_global))}', args["state"])
    ut.log(f'MSE-global shape" : {str(MSE)}', args["state"])
    ut.log(f'ps-global shape" : {str(r_squared_global)}', args["state"])

    #TODO save output files
    #print_pvals(args, ps_global, ts_global, X_labels)
    #print_beta_images(args, avg_beta_vector, X_labels)
    #print_r2_image(args, r_squared_global)

    anc.print_beta_vectors(args, avg_beta_vector, "beta_vector_global", X_labels)
    anc.print_rsquared(args, r_squared_global, "r_squared_global")

    # Block of code to print local stats as well
    sites = [site for site in input_list]

    all_local_stats_dicts = dict(zip(sites, all_local_stats_dicts))

    # List all output files (global stats)
    global_files = sorted(os.listdir(state_["outputDirectory"]))

    # move global stats to transfer directory to be moved to local sites
    os.mkdir(os.path.join(state_["transferDirectory"], "global_stats"))
    for f in global_files:
        shutil.copy(
            os.path.join(state_["outputDirectory"], f),
            os.path.join(state_["transferDirectory"], "global_stats", f),
        )

    # Get list of global pngs files
    global_png_files = [
        f"global_stats/{file}" for file in global_files if file.endswith(".png") or file.endswith(".csv")
    ]

    # Get list of local png files
    local_png_files = {
        site: [file for file in site_files if file.endswith(".png") or file.endswith(".csv")]
        for site, site_files in all_local_stats_dicts.items()
    }

    # Gather local and global png files (for display in UI)
    output_dict = {"local_stats": local_png_files, "global_stats": global_png_files}

    computation_output_dict = {"output": output_dict, "success": True}

    anc.chmod_dir_recursive(args['state']["transferDirectory"])
    anc.chmod_dir_recursive(args['state']["outputDirectory"])

    return computation_output_dict


def scica_remote_phases(parsed_args):

    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))
    
    ut.log("\nReceived phase key : "+str(phase_key), parsed_args["state"])
    if 'scica_local_0' in phase_key:
        return scica_remote_0(parsed_args)
    elif "scica_local_1" in phase_key:
        return scica_remote_1(parsed_args)
    elif "scica_local_2" in phase_key:
        return scica_remote_2(parsed_args)
    else:
        raise ValueError("Error occurred at Local")


if __name__ == '__main__':
    parsed_args = json.loads(sys.stdin.read())
    scica_remote_phases(parsed_args)
