# -*- coding: utf-8 -*-
import warnings

warnings.simplefilter("ignore")
import sys
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op

def QA_skullstrip(file_path,QA_skullstrip_path):
    '''
    file_path is the path of nii.gz file
    QA_skullstrip_path is the folder of QA_skullstrip
    call slicesdir `imglob pat*` to generate png file and folder
    move files into QA_skullstrip_path
    delete slicesdir folder
    '''
    file_path.replace('\\', '/')
    QA_skullstrip_path.replace('\\', '/')
    generate_png = 'slicesdir ' + "`imglob " + file_path + "`"
    os.system(generate_png)
    current_path = os.getcwd()
    current_path.replace('\\', '/')
    slicesdir = current_path + '/slicesdir/'
    if os.path.exists(QA_skullstrip_path):
        if QA_skullstrip_path.endswith('/'):
            pass
        else:
            QA_skullstrip_path = QA_skullstrip_path + '/'
        move_file = 'mv ' + slicesdir + '* ' + QA_skullstrip_path
        os.system(move_file)
        print(' move the last index.html into folder ' + QA_skullstrip_path)
        os.removedirs(slicesdir)
        print(' delete folder ' + slicesdir)
    else:
        print (' ERROR!!! your QA_path of skull-strip do not exit. ')

