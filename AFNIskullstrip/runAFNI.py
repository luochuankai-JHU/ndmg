import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import ndmg_dwi_pipeline



out = "/home-net/home-1/cluo16@jhu.edu/data/lck/SWU_4/mask"
tmpdir = "/home-net/home-1/cluo16@jhu.edu/data/lck/SWU_4"
alreadyfile = []
for root, dirs, files in os.walk(tmpdir):
    alreadyfile.append(files)
errorfile = []

for root, dirs, files in os.walk("/home-net/home-1/cluo16@jhu.edu/data/lck/data_discrim/SWU_4"):#root是具体文件的上一层,dirs,files是具体文件
    for name in files:
        t1w = os.path.join(root, name)
        if t1w.endswith('T1w.nii.gz'):
            T1w_name = mgu.get_filename(t1w)
            Skulled_name = T1w_name + '_noskull.nii.gz'
            if Skulled_name not in alreadyfile[0]:
                print ('strip from  ' + t1w)
                try:
                    extract_t1w_brain(t1w, out, tmpdir)
                except Exception:   #IOError
                    print('!!!!!!! error on ' + t1w)
                    errorfile.append(t1w + "\n")
            elif Skulled_name in alreadyfile[0]:
                print('ALREADY skull-strip  ' + T1w_name)
file = open(r'/home-net/home-1/cluo16@jhu.edu/data/lck/SWU_4/errorfile.txt','a')
for sss in errorfile:
    file.write(sss)
file.close()


