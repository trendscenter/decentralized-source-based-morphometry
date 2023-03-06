#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 2 20:19:00 2018 (MDT)

@author: Rogers F. Silva
"""

import numpy as np
from . import ancillary as an


def local_PCA(site,
              num_PC,
              mean_removal=None,
              subject_level_PCA=True,
              subject_level_num_PC=120):
    """ Local principal component analysis method for decentralized PCA.
    
    Accounts for mean removal and subject-level whitening.
    
    Parameters
    ----------
    site : dict of 2D arrays
        The datasets from local site to be transformed and decomposed.
    num_PC : positive int
        The number of principal components to be retained.
    mean_removal : None or tuple, optional
        The default is ``None``, which does not perform mean removal.
        Otherwise, must be a tuple of two elements.
            First element: (-1 or -2) axis along which the mean should be removed.
            Second element: (1D array) global mean values to be removed.
            If ``axis=-2``, the second element is ignored.
    subject_level_PCA : bool, optional
        If this is set to True, performs additional subject-level PCA.
    subject_level_num_PC : positive int, optional
        Number of components for subject-level PCA. Ignored if ``subject_level_PCA`` is ``False``.
        
    Returns
    -------
    reduced_data : 2D array
        The transformed (and reduced) local representation (aka, the principal components).
    projM : dict of 2D arrays
        The matrices that project each dataset onto the subspace (aka, the sbject-level whitening matrices)
    bkprojM : dict of 2D arrays
        The matrices that reconstruct the datasets from their transformed (and reduced) representations
        (aka, the subject-level dewhitening or back-projection matrices).
    """

    subject_list = site.keys()
    data_subject = np.array([])
    projM = {}
    bkprojM = {}
    for mm in subject_list:
        raw_subject = site[mm]

        if mean_removal:
            axis, mean_values = mean_removal  # mean_removal is a tuple
            if axis == -2:
                # Remove column means
                # Ignore contents of mean_values
                raw_subject = raw_subject - np.mean(raw_subject, axis=-2)
            elif axis == -1:
                # Remove row means
                # mean_values computed in decentralized fashion elsewhere
                raw_subject = raw_subject - mean_values[:, None]

        if subject_level_PCA:
            # This is subject level PCA with whitening
            data_subject_tmp, projM[mm], bkprojM[mm] = an.base_PCA(
                raw_subject,
                num_PC=subject_level_num_PC,
                axis=-1,
                whitening=True)
            data_subject = np.hstack(
                (data_subject,
                 data_subject_tmp)) if data_subject.size else data_subject_tmp
        else:
            data_subject = np.hstack(
                (data_subject,
                 raw_subject)) if data_subject.size else raw_subject

    reduced_data, _, _ = an.base_PCA(data_subject,
                                     num_PC=num_PC,
                                     axis=-1,
                                     whitening=False)
    return reduced_data, projM, bkprojM