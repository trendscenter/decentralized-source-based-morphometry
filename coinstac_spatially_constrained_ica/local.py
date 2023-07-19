"""
Created on Mon March 6 2023

@author: Debbrata Saha
"""

import sys
import ujson as json
from .BackRecon import gift_gica
from utils import listRecursive
import utils as ut
import os
import glob
import numpy as np
import nibabel as nib

loading_parameters = 'gica_cmd_group_loading_coeff_.nii'


def scica_local_1(args):
    state = args["state"]
    in_files = [os.path.join(state['baseDirectory'], f)
                for f in args["input"]["data"]]
    
    #raise Exception(in_files[0])
    maskfile = os.path.join('/computation', 'local_data', 'mask.nii')
    template = os.path.join('/computation', 'local_data', 'Neuromark_v01_sMRI_low_30.nii')
    #template = ut.get_interpolated_nifti(in_files[0], template, destination_dir=state["outputDirectory"])
    pyscript = os.path.join(state["outputDirectory"], 'pyscript_gicacommand.m')

    

    
    if os.path.exists(pyscript):
        os.remove(pyscript)
    output = gift_gica(
            in_files=in_files,
            refFiles=[template],
            mask=maskfile,
            out_dir=state["outputDirectory"],
        )

    load_loading_parameter = nib.load(os.path.join(args['state']['outputDirectory'], 'gica_cmd_group_loading_coeff_.nii'))
    loading_parameter = np.array(load_loading_parameter.dataobj)
    
    ut.log("loading parameters shape: "+str(loading_parameter.shape), args["state"])
    #raise Exception(loading_parameter)

    # send files to transfer directory
    np.save(os.path.join(args['state']['transferDirectory'], 'loading_parameter.npy'), loading_parameter)

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

    computation_output = {
      "output": { 'loading_parameter': 'loading_parameter.npy','computation_phase': 'scica_local_1'},
      "cache": {},
      "state": state
    }



    return computation_output


    output_dict = {
        'loading_parameter': loading_parameter.npy,
        'computation_phase': 'scica_local_1'
    }
    cache_dict = {}
    computation_output = {
        "output": output_dict,
        "cache": cache_dict,
        "state": state
    }

    return computation_output


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
       

if __name__ == '__main__':
    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        computation_output = scica_local_1(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Local")
