import nibabel as nib
# from deepbrain import Extractor
import os
import sys
sys.path.append('/data/jvogels3/lck/ndmg/ndmg/utils/')
sys.path.append('/data/jvogels3/lck/ndmg/ndmg/')
sys.path.append('/data/jvogels3/lck/ndmg/')
import gen_utils as mgu   #from ndmg.utils
import numpy as np
import nilearn.image as nl
import os
import os.path as op
import dipy
from dipy.segment.mask import median_otsu
# img_path = '/home/workspace/chuankailuo/program/skullstrip/BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
# img_path = '/home-net/home-1/cluo16@jhu.edu/data/lck/data_discrim/SWU_4/sub-0025684/ses-1/anat/sub-0025684_ses-1_T1w.nii.gz'
# img_path = 'F:/JHU/ndd/skullstrip/CNN/output/prediction_sub-0025864_ses-1_T1w.nii__test_mask.nii.gz'

def skullstrip_with_dipy(img_path,Skulled_name):
    nodif_B0_data = nib.load(img_path)
    nodif_B0_array = nodif_B0_data.get_fdata()
    nodif_B0_dipy = median_otsu(nodif_B0_array)    #get false true
    # extract bet and bet_mask
    nodif_B0_dipy_bet = nodif_B0_dipy[0]
    # encode True False as float 0,1
    nodif_B0_dipy_bet_mask = nodif_B0_dipy[1].astype(float)
    # apply affine to convert back into nifti image
    nodif_B0_dipy_bet_nifti = nib.Nifti1Image(nodif_B0_dipy_bet, nodif_B0_data.affine)
    nodif_B0_dipy_bet_mask_nifti = nib.Nifti1Image(nodif_B0_dipy_bet_mask, nodif_B0_data.affine)
    # store bet and bet_mask at designated locations
    nib.save(nodif_B0_dipy_bet_nifti, os.path.join(out_niigz_folder,Skulled_name))
    nib.save(nodif_B0_dipy_bet_mask_nifti, os.path.join(out_mask_folder,Skulled_name))




out_niigz_folder = '/data/jvogels3/lck/SWU_4_out/dipy/niigz'
out_mask_folder = '/data/jvogels3/lck/SWU_4_out/dipy/mask'
origional_folder = "/home-net/home-1/cluo16@jhu.edu/data/lck/data_discrim/SWU_4"
alreadyfile = []
for root, dirs, files in os.walk(out_niigz_folder):
    alreadyfile.append(files)
# root是具体文件的上一层,dirs,files是具体文件
errorfile = []
for root, dirs, files in os.walk(origional_folder):
    for name in files:
        t1w = os.path.join(root, name)
        if t1w.endswith('T1w.nii.gz'):
            T1w_name = mgu.get_filename(t1w)
            Skulled_name = T1w_name + '_noskull.nii.gz'
            if Skulled_name not in alreadyfile[0]:
                print ('strip from  ' + t1w)
                try:
                    skullstrip_with_dipy(t1w,Skulled_name)
                except IOError:   #
                    print('!!!!!!! error on ' + t1w)
                    errorfile.append(t1w + "\n")
            elif Skulled_name in alreadyfile[0]:
                print('ALREADY skull-strip  ' + T1w_name)
file = open(r'/data/jvogels3/lck/SWU_4_out/dipy/errorfile.txt','a')
for sss in errorfile:
    file.write(sss)
file.close()

