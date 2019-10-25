import ndmg
from ndmg import preproc
from ndmg import register
from ndmg import track
from ndmg import graph
from ndmg.utils import gen_utils
from ndmg.utils import reg_utils
from ndmg.utils import cloud_utils
from unittest.mock import Mock
import numpy as np 
import pytest
import os

#requires most up to date pytest for tmp_path to work
def test_rescale_bvac(tmp_path):
	#create temp file dir
	d = tmp_path/"sub"
	d.mkdir()

	#create temp output dir
	bvec_out_temp1_path = d/ "test1_new.bvec"
	bvec_out_temp2_path = d/ "test2_new.bvec"

	bvec_in1_path = '../test_data/inputs/rescale_bvec/rescale_bvec_test_1.bvec' 
	bvec_in2_path = '../test_data/inputs/rescale_bvec/rescale_bvec_test_2.bvec'
 
	bvec_out_cntrl_path = '../test_data/outputs/rescale_bvec/rescale_bvec_output.bvec'

	#load data
	bvec_out_cntrl= np.loadtxt(bvec_out_cntrl_path)

	#run through data
	preproc.rescale_bvec(bvec_in1_path,str(bvec_out_temp1_path))
	preproc.rescale_bvec(bvec_in2_path,str(bvec_out_temp2_path))

	#open data 
	bvec_out_temp1 = np.loadtxt(str(bvec_out_temp1_path))
	bvec_out_temp2 = np.loadtxt(str(bvec_out_temp2_path))

	assert np.allclose(bvec_out_temp1,bvec_out_cntrl) 
	assert np.allclose(bvec_out_temp2,bvec_out_cntrl)


