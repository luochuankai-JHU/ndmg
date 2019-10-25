import numpy.testing as npt
from dipy.segment.tissue import (TissueClassifierHMRF)
import nibabel as nib


image_nii = nib.load('/mnt/d/Downloads/neurodatadesign/ndmg/tests/ndmg_outputs/anat/preproc/t1w_brain.nii.gz')
image = image_nii.get_data()
nclasses = 3

def test_classify():
    imgseg = TissueClassifierHMRF()
    beta = 0.1
    tolerance = 0.0001
    max_iter = 10
    print(image.max())
    print(image.min())
    # npt.assert_(image.max() == 1.0)
    # npt.assert_(image.min() == 0.0)
    # First we test without setting iterations and tolerance
    seg_init, seg_final, PVE = imgseg.classify(image, nclasses, beta)
    npt.assert_(seg_final.max() == nclasses)
    npt.assert_(seg_final.min() == 0.0)
    # Second we test it with just changing the tolerance
    seg_init, seg_final, PVE = imgseg.classify(image, nclasses, beta,
                                               tolerance)
    npt.assert_(seg_final.max() == nclasses)
    npt.assert_(seg_final.min() == 0.0)
    # Third we test it with just the iterations
    seg_init, seg_final, PVE = imgseg.classify(image, nclasses, beta, max_iter)
    npt.assert_(seg_final.max() == nclasses)
    npt.assert_(seg_final.min() == 0.0)
    # Next we test saving the history of accumulated energies from ICM
    imgseg = TissueClassifierHMRF(save_history=True)
    seg_init, seg_final, PVE = imgseg.classify(200 * image, nclasses,
                                               beta, tolerance)
    npt.assert_(seg_final.max() == nclasses)
    npt.assert_(seg_final.min() == 0.0)
    npt.assert_(imgseg.energies_sum[0] > imgseg.energies_sum[-1])