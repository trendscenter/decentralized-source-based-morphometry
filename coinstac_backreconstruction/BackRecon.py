import os
from nipype.interfaces.base import File, traits
from nipype.interfaces.matlab import MatlabCommand, MatlabInputSpec

ALGORITHM_FILES = dict(
    gigica="icatb_gigicar",
    dualregress="icatb_dualregress"
)
PREPROC_TYPES = dict(
    time_mean=1,
    voxel_mean=2,
    intensity_norm=3,
    variance_norm=4
)
DEFAULT_PREPROC = "time_mean"
DEFAULT_ALGORITHM = "gigica"
DEFAULT_MASK = "mask.nii"
DEFAULT_ICA_SIG = "ica_sig.mat"
DEFAULT_ICA_VARNAME = "SM"


class BackReconInputSpec(MatlabInputSpec):
    algorithm = traits.Str(mandatory=False,
                           default_value=DEFAULT_ALGORITHM,
                           desc='Algorithm to use for Back-Reconstruction')
    mask = traits.Str(mandatory=False,
                      default_value=DEFAULT_MASK,
                      desc='Mask to use for Back-Reconstruction')
    ica_sig = traits.Str(mandatory=True,
                         desc=".Mat file containing ICA Signals")
    ica_varname = traits.Str(mandatory=True,
                             desc="Variable name to load from the signal file")
    preproc_type = traits.Str(mandatory=False,
                              default_value=DEFAULT_PREPROC,
                              desc="")
    files = traits.List(mandatory=True,
                        desc='List of Files for Back-Reconstruction')


class BackReconOutputSpec(MatlabInputSpec):
    matlab_output = traits.Str()


class BackRecon(MatlabCommand):
    """ Basic Hello World that displays Hello <name> in MATLAB

    Returns
    -------

    matlab_output : capture of matlab output which may be
                    parsed by user to get computation results

    Example
    --------

    >>> recon = BackRecon()
    >>> recon.inputs.files = ['subject_1.nii', 'subject_2.nii']
    >>> recon.inputs.mask = 'mask.nii'
    >>> recon.inputs.ica_sig = 'gica_signal.mat'
    >>> recon.inputs.ica_varname = 'SM'
    >>> recon.inputs.preproc_type = 'time_mean'
    >>> recon.inputs.algorithm = 'gigica'
    >>> out = recon.run()
    """
    input_spec = BackReconInputSpec
    output_spec = BackReconOutputSpec

    def _runner_script(self):
        files_line = {"%s" % file for file in self.inputs.files}
        script = """
            addpath('matcode');
            ica_sig = load('%s');
            ica_sig = ica_sig.SM;
            files = %s;
            mask = load('%s');
            mask_data = mask.mask;
            for i = 1:length(files)
                disp(files{i});
                nii = load_nii(files{i});
                s = size(nii.img);
                data = reshape(nii.img, [prod(s(1:3)), s(4)]);
                masked_data = data(mask_data==1, :);
                data = icatb_preproc_data(masked_data, %d, 1);
                [TC, SM] = %s(data, ica_sig);
                save([files{i} '.backrecon.mat'],'TC','SM')
            end
        """ % (self.inputs.ica_sig,
               files_line,
               self.inputs.mask,
               PREPROC_TYPES.get(self.inputs.preproc_type, 1),
               ALGORITHM_FILES.get(self.inputs.algorithm, "icatb_gigicar")
               )
        #print("MATLAB SCRIPT IS %s" % script)
        return script

    def run(self, **inputs):
        # inject your script
        self.inputs.script = self._runner_script()
        results = super().run(**inputs)
        stdout = results.runtime.stdout
        # attach stdout to outputs to access matlab results
        results.outputs.matlab_output = stdout
        return results

    def _list_outputs(self):
        outputs = self._outputs().get()
        return outputs


if __name__ == "__main__":
    recon = BackRecon()
    recon.inputs.files = ['subject_1.nii', 'subject_2.nii']
    recon.inputs.mask = 'mask.mat'
    recon.inputs.ica_sig = 'gica_signal.mat'
    recon.inputs.algorithm = 'gigica'
    out = recon.run()
