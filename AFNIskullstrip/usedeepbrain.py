import nibabel as nib
from deepbrain import Extractor
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
# img_path = '/home/workspace/chuankailuo/program/skullstrip/BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
img_path = '/home-net/home-1/cluo16@jhu.edu/data/lck/data_discrim/SWU_4/sub-0025684/ses-1/anat/sub-0025684_ses-1_T1w.nii.gz'
# img_path = 'F:/JHU/ndd/skullstrip/CNN/output/prediction_sub-0025864_ses-1_T1w.nii__test_mask.nii.gz'

def db(img_path):
    # Load a nifti as 3d numpy image [H, W, D]
    img0 = nib.load(img_path)
    img = nib.load(img_path).get_fdata()   # 3D array anat
    ext = Extractor()
    # Load a nifti as 3d numpy image [H, W, D]
    img = nib.load(img_path).get_fdata()
    ext = Extractor()
    # `prob` will be a 3d numpy image containing probability
    # of being brain tissue for each of the voxels in `img`
    prob = ext.run(img)
    # mask can be obtained as:
    mask = prob > 0.5
    return prob


out_mask_folder = "/data/jvogels3/lck/SWU_4_out/deepbrain/mask"
out_niigz_folder = "/data/jvogels3/lck/SWU_4_out/deepbrain/niigz"
out_npy_folder = "/data/jvogels3/lck/SWU_4_out/deepbrain/npy"
origional_folder = "/home-net/home-1/cluo16@jhu.edu/data/lck/data_discrim/SWU_4"
alreadyfile = []
for root, dirs, files in os.walk(out_folder):
    alreadyfile.append(files)

#root是具体文件的上一层,dirs,files是具体文件
for root, dirs, files in os.walk(origional_folder):
    for name in files:
        t1w = os.path.join(root, name)
        if t1w.endswith('T1w.nii.gz'):
            T1w_name = mgu.get_filename(t1w)
            Skulled_name = T1w_name + '_noskull.nii.gz'
            Skulled_name2 = T1w_name + '_noskull.npy'
            if Skulled_name not in alreadyfile[0]:
                print ('strip from  ' + t1w)
                prob = db(t1w)
                mask = prob > 0.5
                img = nib.load(t1w)
                affine = img.affine
                labels = np.argmax(prob, axis=-1)
                out = nib.Nifti1Image(labels, affine)
                labels2 = np.argmax(mask, axis=-1)
                out2 = nib.Nifti1Image(labels2, affine)
                nib.save(out, os.path.join(out_niigz_folder,Skulled_name))
                nib.save(out2, os.path.join(out_mask_folder, Skulled_name))
                np.save(os.path.join(out_npy_folder, Skulled_name2),prob)
            elif Skulled_name in alreadyfile[0]:
                print('ALREADY skull-strip  ' + T1w_name)









