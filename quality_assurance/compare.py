# -*- coding: utf-8 -*-
import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op

def erode_mask(mask, v=0):
    """
    A function to erode a mask by a specified number of
    voxels. Here, we define erosion as the process of checking
    whether all the voxels within a number of voxels for a
    mask have values.
    **Positional Arguments:**
        mask:
            - a numpy array of a mask to be eroded.
        v:
            - the number of voxels to erode by.
    """
    print("Eroding Mask...")
    for i in range(0, v):
        # masked_vox is a tuple 0f [x]. [y]. [z] cooords
        # wherever mask is nonzero
        erode_mask = np.zeros(mask.shape)
        x, y, z = np.where(mask != 0)
        if x.shape == y.shape and y.shape == z.shape:
            # iterated over all the nonzero voxels
            for j in range(0, x.shape[0]):
                # check that the 3d voxels within 1 voxel are 1
                # if so, add to the new mask
                md = mask.shape
                if (
                        mask[x[j], y[j], z[j]]
                        and mask[np.min((x[j] + 1, md[0] - 1)), y[j], z[j]]
                        and mask[x[j], np.min((y[j] + 1, md[1] - 1)), z[j]]
                        and mask[x[j], y[j], np.min((z[j] + 1, md[2] - 1))]
                        and mask[np.max((x[j] - 1, 0)), y[j], z[j]]
                        and mask[x[j], np.max((y[j] - 1, 0)), z[j]]
                        and mask[x[j], y[j], np.max((z[j] - 1, 0))]
                ):
                    erode_mask[x[j], y[j], z[j]] = 1
        else:
            raise ValueError("Your mask erosion has an invalid shape.")
        mask = erode_mask
    return mask

def getthemask(path):
    # Load a nifti as 3d numpy image [H, W, D]
    img1 = nib.load(path).get_fdata()  # 3D array anat
    imgall = nib.load(path)
    t = 1
    mask = (img1 > t).astype(int)
    mask_img = nib.Nifti1Image(mask, header=imgall.header, affine=imgall.affine)
    mask_np = mask_img.dataobj
    # nib.save(mask_img, 'F:/JHU/ndd/skullstrip/masklck_sub-0025864_ses-1_T1w.nii__test.nii.gz' )
    return mask_np



def compute_diff(img_path1,img_path2,img_path3):
    img1 = getthemask(img_path1)
    img2 = getthemask(img_path2)
    img3 = getthemask(img_path3)
    d = nib.load(img_path1).get_fdata()
    total = d.shape[0]*d.shape[1]*d.shape[2]
    diff12 = abs(np.count_nonzero(img2 - img1)/total)
    diff23 = abs(np.count_nonzero(img2 - img3)/total)
    diff13 = abs(np.count_nonzero(img1 - img3)/total)
    maxdiff = max(diff13,diff12,diff23)
    mindiff = min(diff13,diff12,diff23)

    return maxdiff,mindiff

'''
example:
img_path1 = 'F:/JHU/ndd/dataset/BNU1_output/sub-0025864_ses-1_T1w_noskull.nii.gz'    # AFNI
img_path2 = 'F:/JHU/ndd/skullstrip/prediction_sub-0025864_ses-1_T1w.nii__test.nii.gz'   # CNN theano
img_path3 = ''     # deepbrain method


if maxdiff > 0.3 , we can consume that at least one method get bad skull-strip result
if mindiff < 0.05 , we can consume that these three methods are all the good result
the exact number like 0.3 and 0.05 can be change after we get the statistic result of all data
'''
