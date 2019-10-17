import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import ndmg_dwi_pipeline

out = "/mnt/f/JHU/ndd/dataset/keyerror_output/mask"
tmpdir = "/mnt/f/JHU/ndd/dataset/keyerror_output/"
for root, dirs, files in os.walk("/mnt/f/JHU/ndd/dataset/keyerror/"):  #root是具体文件的上一层,dirs,files是具体文件
    for name in files:
        t1w = os.path.join(root, name)
        if t1w.endswith('T1w.nii.gz'):
            print ('strip from  ' + t1w)
            extract_t1w_brain(t1w, out, tmpdir)