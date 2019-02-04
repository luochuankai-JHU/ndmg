#!/usr/bin/env python
# Copyright 2019 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# ndmg_dwi_pipeline.py
# Repackaged for native space tractography by Derek Pisner in 2019
# Email: dpisner@utexas.edu
# Originally created by Greg Kiar and Will Gray Roncal on 2016-01-27.

from __future__ import print_function
import shutil
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
from argparse import ArgumentParser
from datetime import datetime
#from ndmg.stats.qa_regdti import *
import time
from ndmg.stats.qa_tensor import *
from ndmg.stats.qa_fibers import *
from ndmg.stats.qa_mri import qa_mri
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as rgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
import ndmg.preproc as mgp
import numpy as np
import nibabel as nib
import os
from ndmg.graph import gen_biggraph as ndbg
import traceback
from ndmg.utils.bids_utils import name_resource
import sys
from nibabel.streamlines import Tractogram, save

os.environ["MPLCONFIGDIR"] = "/tmp/"


def ndmg_dwi_worker(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                    vox_size, clean, big):
    """
    Creates a brain graph from MRI data
    """
    startTime = datetime.now()
    fmt = '_adj.csv'
    # Create derivative output directories
    namer = name_resource(dwi, t1w, atlas, outdir)

    paths = {'prep_m': "dwi/preproc",
             'prep_a': "anat/preproc",
             'reg_m': "dwi/registered",
             'reg_a': "anat/registered",
             'tensor': "dwi/tensor",
             'fiber': "dwi/fiber",
             'voxelg': "dwi/voxel-connectomes",
             'conn': "dwi/roi-connectomes"}

    opt_dirs = ['prep_m', 'prep_a', 'reg_m', 'reg_a']
    clean_dirs = ['tensor', 'fiber']
    label_dirs = ['conn']  # create label level granularity

    namer.add_dirs(paths, labels, label_dirs)
    qc_stats = "{}/{}_stats.csv".format(namer.dirs['qa']['base'],
        namer.get_mod_source())

    # Create derivative output file names
    reg_dname = "{}_{}".format(namer.get_mod_source(),
        namer.get_template_info())
    reg_aname = "{}_{}".format(namer.get_anat_source(),
        namer.get_template_info())
    streams = namer.name_derivative(namer.dirs['output']['fiber'],
        "{}_streamlines.trk".format(reg_dname))

    if big:
        voxel = namer.name_derivative(namer.dirs['output']['voxel'],
            "{}_voxel-connectome.npz".format(reg_dname))
        print("Voxelwise Fiber Graph: {}".format(voxel))

    # Again, connectomes are different
    if not isinstance(labels, list):
        labels = [labels]
    connectomes = [namer.name_derivative(
        namer.dirs['output']['conn'][namer.get_label(lab)],
        "{}_{}_measure-spatial-ds{}".format(namer.get_mod_source(),
            namer.get_label(lab), fmt)) for lab in labels]

    print("Connectomes downsampled to given labels: " +
          ", ".join(connectomes))

    if vox_size == '1mm':
	zoom_set = (1.0,1.0,1.0)
    elif vox_size == '2mm':
	zoom_set = (2.0,2.0,2.0)
    else:
	raise ValueError('Voxel size not supported. Use 2mm or 1mm')

    qc_dwi = qa_mri(namer, 'dwi')  # for quality control
    # -------- Preprocessing Steps --------------------------------- #
    # Perform eddy correction
    start_time = time.time()
    dwi_prep = "{}/eddy_corrected_data.nii.gz".format(namer.dirs['output']['prep_m'])
    cmd='eddy_correct ' + dwi + ' ' + dwi_prep + ' 0'
    os.system(cmd)
  
    # Check orientation (dwi_prep)
    img = nib.load(dwi_prep)
    if nib.aff2axcodes(img.affine)[0] == 'L':
        start_time = time.time()
        print('Reorienting dwi image to RAS+ canonical...')
        # Orient dwi to std
        dwi_orig = dwi_prep
        dwi_prep = "{}/dwi_prep_reor.nii.gz".format(namer.dirs['output']['prep_m'])
        shutil.copyfile(dwi_orig, dwi_prep)
        canonical_dwi_img = nib.as_closest_canonical(img)
        nib.save(canonical_dwi_img, dwi_prep)
        # Swap x-y axis in bvecs
        bvecs_orig = bvecs
        bvecs = "{}/bvec_reor.bvec".format(namer.dirs['output']['prep_m'])
        shutil.copyfile(bvecs_orig, bvecs)
        bvecs_mat = np.genfromtxt(bvecs)
        bvecs_mat[[0, 1]] = bvecs_mat[[1, 0]]
        np.savetxt(bvecs, bvecs_mat)
        print("%s%s%s" % ('Reorienting runtime: ', str(np.round(time.time() - start_time, 1)), 's'))

    # Check dimensions
    hdr = img.get_header()
    zooms = hdr.get_zooms()
    if (abs(zooms[0]), abs(zooms[1]), abs(zooms[2])) is not zoom_set:
        start_time = time.time()
        dwi_orig = dwi_prep
        dwi_prep = "{}/dwi_prep_reslice.nii.gz".format(namer.dirs['output']['prep_m'])
        shutil.copyfile(dwi_orig, dwi_prep)
	if vox_size == '1mm':
	    print('Reslicing preprocessed dwi to 1mm...')
            dwi_prep = rgu.reslice_to_xmm(dwi_prep, 1.0)
	elif vox_size == '2mm':
            print('Reslicing preprocessed dwi to 2mm...')
            dwi_prep = rgu.reslice_to_xmm(dwi_prep, 2.0)
        print("%s%s%s" % ('Reslicing runtime: ', str(np.round(time.time() - start_time, 1)), 's'))

    print("Rotating b-vectors and generating gradient table...")
    eddy_rot_param = "{}/eddy_corrected_data.ecclog".format(namer.dirs['output']['prep_m'])
    bvec_scaled = "{}/bvec_scaled.bvec".format(namer.dirs['output']['prep_m'])
    bvec_rotated = "{}/bvec_rotated.bvec".format(namer.dirs['output']['prep_m'])
    bval = "{}/bval.bval".format(namer.dirs['output']['prep_m'])
    shutil.copyfile(bvals, bval)

    # Rotate bvecs
    cmd='bash fdt_rotate_bvecs ' + bvecs + ' ' + bvec_rotated + ' ' + eddy_rot_param + ' 2>/dev/null'
    os.system(cmd)

    # Rescale bvecs
    mgp.rescale_bvec(bvec_rotated, bvec_scaled)

    # Build gradient table
    [gtab, nodif_B0, nodif_B0_mask] = mgu.make_gtab_and_bmask(bvals, bvec_scaled, dwi_prep, namer.dirs['output']['prep_m'])

    print("%s%s%s" % ('Preprocessing runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # -------- Registration Steps ----------------------------------- #
    # Check orientation (t1w)
    img = nib.load(t1w)
    if nib.aff2axcodes(img.affine)[0] == 'L':
	start_time = time.time()
	print('Reorienting t1w image to RAS+ canonical...')
        # Orient t1w to std
        t1w_orig = t1w
        t1w = "{}/t1w_reor.nii.gz".format(namer.dirs['output']['prep_m'])
        shutil.copyfile(t1w_orig, t1w)
        canonical_t1w_img = nib.as_closest_canonical(img)
        nib.save(canonical_t1w_img, t1w)
	print("%s%s%s" % ('Reorienting runtime: ', str(np.round(time.time() - start_time, 1)), 's'))	

    # Check dimensions
    hdr = img.get_header()
    zooms = hdr.get_zooms()
    if (abs(zooms[0]), abs(zooms[1]), abs(zooms[2])) is not zoom_set:
	start_time = time.time()
        t1w_orig = t1w
        t1w = "{}/t1w_reslice.nii.gz".format(namer.dirs['output']['prep_m'])
        shutil.copyfile(t1w_orig, t1w)
        if vox_size == '1mm':
            print('Reslicing preprocessed t1w to 1mm...')
            t1w = rgu.reslice_to_xmm(t1w, 1.0)
        elif vox_size == '2mm':
            print('Reslicing preprocessed t1w to 2mm...')
            t1w = rgu.reslice_to_xmm(t1w, 2.0)
	print("%s%s%s" % ('Reslicing runtime: ', str(np.round(time.time() - start_time, 1)), 's'))

    # Instantiate registration
    reg = mgr.dmri_reg(outdir, nodif_B0, nodif_B0_mask, t1w, vox_size, simple=False)
    # Perform anatomical segmentation
    start_time = time.time()
    reg.gen_tissue()
    print("%s%s%s" % ('gen_tissue runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # align t1w to dwi
    start_time = time.time()
    reg.t1w2dwi_align()
    print("%s%s%s" % ('t1w2dwi_align runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # align tissue classifiers
    start_time = time.time()
    reg.tissue2dwi_align()
    print("%s%s%s" % ('tissue2dwi_align runtime: ', str(np.round(time.time() - start_time, 1)), 's'))

    # -------- Tensor Fitting and Fiber Tractography ---------------- #
    # Compute tensors and track fiber streamlines
    print("Beginning tractography...")
    trct = mgt.run_track(dwi_prep, nodif_B0_mask, reg.gm_in_dwi, reg.vent_csf_in_dwi, reg.wm_in_dwi, reg.wm_in_dwi_bin, gtab)
    [streamlines, tens] = trct.run()

    #tracks = [sl for sl in streamlines if len(sl) > 1]

    # Save streamlines to disk
    print('Saving streamlines: ' + streams)
    tractogram = Tractogram(streamlines, affine_to_rasmm=nib.load(dwi_prep).affine)
    save(tractogram, streams)

    # Visualize fibers using VTK
    if nib.load(mask).get_data().shape == (182, 218, 182):
        try:
            visualize_fibs(streamlines, streams, aligned_atlas, namer.dirs['qa']['fiber'], 0.02, 2000)
        except:
            print("Fiber QA failed - VTK for Python not configured properly.")

    # -------- Big Graph Generation --------------------------------- #
    # Generate big graphs from streamlines
    if big is True:
        print("Making Voxelwise Graph...")
        bg1 = ndbg.biggraph()
        bg1.make_graph(streamlines)
        bg1.save_graph(voxel)

    # ------- Connectome Estimation --------------------------------- #
    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(labels):
        print("Generating graph for {} parcellation...".format(label))
	print("%s%s" % ('Applying native-space alignment to ', labels[idx]))
	# align atlas to t1w to dwi
        labels_im_file = reg.atlas2t1w2dwi_align(labels[idx])
	print('Aligned Atlas: ' + labels_im_file)
	labels_im = nib.load(labels_im_file)
	g1 = mgg.graph_tools(attr=len(np.unique(labels_im.get_data()))-1, rois=labels[idx], streamlines=streamlines)
        g1.make_graph()
        g1.summary()
        g1.save_graph(connectomes[idx])

    exe_time = datetime.now() - startTime
    qc_dwi.save(qc_stats, exe_time)

    # Clean temp files
    if clean is True:
        print("Cleaning up intermediate files... ")
        del_dirs = [namer.dirs['tmp']['base']] + \
            [namer.dirs['output'][k] for k in opt_dirs]
        cmd = "rm -rf {}".format(" ".format(del_dirs))
        mgu.execute_cmd(cmd)

    print("Execution took: {}".format(exe_time))
    print("Complete!")
    sys.exit(0)


def ndmg_dwi_pipeline(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                      vox_size, clean, big):
    """
    A wrapper for the worker to make our pipeline more robust to errors.
    """
    try:
        ndmg_dwi_worker(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                        vox_size, clean, big)
    except Exception, e:
        print(traceback.format_exc())
        os.exit()
    finally:
        try:
            os.exit()
        except Exception, e:
            os.exit()
    return


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("dwi", action="store", help="Nifti DTI image stack")
    parser.add_argument("bval", action="store", help="DTI scanner b-values")
    parser.add_argument("bvec", action="store", help="DTI scanner b-vectors")
    parser.add_argument("t1w", action="store", help="Nifti T1w MRI image")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("mask", action="store", help="Nifti binary mask of \
                        brain space in the atlas")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    parser.add_argument("vox_size", action="store", nargs="*", default='1mm', 
			help="Voxel size to use for template registrations \
			(e.g. '1mm')")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-b", "--big", action="store_true", default=False,
                        help="whether or not to produce voxelwise big graph")
    result = parser.parse_args()

    # Create output directory
    print("Creating output directory: {}".format(result.outdir))
    print("Creating output temp directory: {}/tmp".format(result.outdir))
    mgu.utils.execute_cmd("mkdir -p {} {}/tmp".format(result.outdir, result.outdir))

    ndmg_dwi_pipeline(result.dwi, result.bval, result.bvec, result.t1w,
                      result.atlas, result.mask, result.labels, result.outdir,
                      result.vox_size, result.clean, result.big)


if __name__ == "__main__":
    main()
