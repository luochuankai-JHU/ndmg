#This is the test code for nifti_to_binary.py
# Assume the original function is true. 
# What the unit test do is to verify whether your code is correct if you change the original code.

from argparse import ArgumentParser
import warnings
from functools import reduce
warnings.simplefilter("ignore")

import pytest
import numpy as np 
import ndmg
import os
import nibabel as nb

#We use the 1.nii as the example test_data. 
#Our goal is to determine if you modify the code correct or not.
#You should first use your modified code run the 1.nii, then you will get a output, for example named 1.dat.

#My code thought is as followed:
#Step 1：try to read the 1.dat document into python. 
#Step2：get the real output document：
#Step 2.1 after the same input image go through the nib_to_bin function, you will get a output document named 2.dat
#Step 2.2: after running, try to read the test output file into here.
#Step 3：compare these two document.


def nib_to_bin(nii, dat):
    im = nb.load(nii)
    im_d = im.get_data()

    length = reduce(lambda x, y: x * y, im_d.shape)
    dat_d = np.reshape(im_d.astype(np.dtype("float32")), (1, length))
    with open(dat, "wb") as fl:
        fl.write(dat_d)

def test_nifti_to_binary():
    content_true = np.fromfile('1.dat', dtype=int)
    nii='1.nii'
    dat='2.dat'
    nib_to_bin(nii,dat)
    content_test = np.fromfile('2.dat', dtype=int)

    assert content_true.all() == content_test.all()