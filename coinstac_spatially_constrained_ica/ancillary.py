
import os

def listRecursive(d, key):
    for k, v in d.items():
        if isinstance(v, dict):
            for found in listRecursive(v, key):
                yield found
        if k == key:
            yield v

def chmod_dir_recursive(dir_name):
    for dir_root, dirs, files in os.walk(dir_name):
            for d in dirs:
                os.chmod(os.path.join(dir_root, d), 0o777)
            for f in files:
                os.chmod(os.path.join(dir_root, f), 0o777)
    #except:
    #    pass;

def subsample_images(images_input_dir, file_names, voxel_subsampling_size, output_dir):
    import nibabel
    # https://stackoverflow.com/questions/53642948/down-sample-mri-t1-image-in-python-with-nipy

    #Create output dir - make sure this is a new directory
    os.makedirs(output_dir)
    #output sample image
    subsampled_files = []
    for image_file_name in file_names:
        input_img = nibabel.load(os.path.join(images_input_dir, image_file_name))
        resampled_img = nibabel.processing.resample_to_output(input_img, voxel_subsampling_size)
        output_img_file_name=os.path.join(output_dir, image_file_name)
        nibabel.save(resampled_img, output_img_file_name)
        subsampled_files.append(output_img_file_name)

    return subsampled_files

def print_beta_vectors(args, metric_data, metric_type, covar_labels):
    import pandas as pd
    """Print regression coefficients as nifti files."""
    data_df = pd.DataFrame(metric_data, columns=covar_labels)

    for column in data_df:
        output_file = os.path.join(args["state"]["outputDirectory"], f'{metric_type}_{str(column)}.csv')
        data_df[column].to_csv(output_file, index=False)

def print_rsquared(args, metric_data, metric_type, file_prefix=''):
    import numpy as np
    output_file = os.path.join(args["state"]["outputDirectory"], f'{metric_type}.csv')
    np.savetxt(output_file, metric_data, delimiter=",")

def validate_file(args, filename, default_filename):
    #If empty or None, use the default vale
    if not filename:
        return default_filename
    if os.path.isfile(filename):
        return filename
    if os.path.isfile(os.path.join(args['state']['baseDirectory'], filename)):
        return os.path.join(args['state']['baseDirectory'], filename)
    raise Exception(f'File {filename} does not exists. Please leave it blank or use the default value: "{default_filename}"')


