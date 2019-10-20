import os
from ndmg.utils.reg_utils import reslice_to_xmm

def reslice_to_xmm(infile, vox_sz=2):
    cmd = "flirt -in {} -ref {} -out {} -nosearch -applyisoxfm {}"
    out_file = "%s%s%s%s%s%s" % (
        os.path.dirname(infile),
        "/",
        os.path.basename(infile).split("_pre_res")[0],
        "_res_",
        int(vox_sz),
        "mm.nii.gz",
    )
    cmd = cmd.format(infile, infile, out_file, vox_sz)
    os.system(cmd)
    return out_file

def test_reslice_to_xmm():
