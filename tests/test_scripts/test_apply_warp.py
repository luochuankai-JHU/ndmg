import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op
import nilearn.image as nl
import pytest
from ndmg.utils.reg_utils import apply_warp


from ndmg.utils import reg_utils as rgu

def test_apply_warp(tmp_path):
    #ref= r"/Users/xueminzhu/ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz"
    #trainout= r"/Users/xueminzhu/ndmg_outputs/tmp/reg_a/desikan_space-MNI152NLin6_res-2x2x2_reor_RAS_nores_aligned_atlas_skull.nii.gz"
    #warp=r"/Users/xueminzhu/ndmg_outputs/tmp/reg_a/mni2t1w_warp.nii.gz"
    #ref_in_path = r"/Users/xueminzhu/ndmg_outputs/anat/preproc/t1w_brain_norse.nii.gz"
    #inp_in_path= r"/Users/xueminzhu/ndmg_outputs/tmp/reg_a/desikan_space-MNI152NLin6_res-2x2x2_reor_RAS_nores_aligned_atlas_t1w_mni.nii.gz"
    #out= r"/Users/xueminzhu/ndmg_outputs/tmp/reg_a/desikan_space-MNI152NLin6_res-2x2x2_reor_RAS_nores_aligned_atlas_skull.nii.gz"
    #warp1=r"/Users/xueminzhu/ndmg_outputs/tmp/reg_a/mni2t1w_warp.nii.gz"

    #make a temporary path#
    d = tmp_path / "sub"
    d.mkdir()
    out_out_cntl_path = d / "outnii.nii.gz"
    warp_out_cntl_path = d/  "warpnii.nii.gz"

    #define correct input data path
    ref_in_path = '../test_data/inputs/apply_warp/t1w_brain_nores.nii.gz'
    inp_in_path = '../test_data/inputs/apply_warp/desikan_space-MNI152NLin6_res-2x2x2_reor_RAS_nores_aligned_atlas_t1w_mni.nii.gz'
    warp_out_cntl_path_temp = '../test_data/outputs/apply_warp/mni2t1w_warp.nii.gz'
    out = out_out_cntl_path
    warp = warp_out_cntl_path

    apply_warp(str(ref_in_path),str(inp_in_path),str(out_out_cntl_path),str(warp_out_cntl_path))



    warp_out_cntl_temp = nib.load(str(warp_out_cntl_path_temp)).get_fdata()
    
    warp_out_cntl = nib.load(str(warp_out_cntl_path)).get_fdata()
    

    assert np.allclose(warp_out_cntl_temp,warp_out_cntl)