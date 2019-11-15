# -*- coding: utf-8 -*-
import warnings

warnings.simplefilter("ignore")
import sys
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op

def get_filename(label):
    """
    Given a fully qualified path gets just the file name, without extension
    """
    return op.splitext(op.splitext(op.basename(label))[0])[0]


def get_true_volume(nparray):
    img_arr = nparray.astype(int)
    threshold = int(1)
    img_arr[img_arr <= threshold] = 0
    img_arr[img_arr > threshold] = 1
    true_volume = np.where(img_arr == 1)
    x = get_range(true_volume, 0)
    y = get_range(true_volume, 1)
    z = get_range(true_volume, 2)
    return x, y, z

def get_range(array,i):
    min_num = min(array[i])
    max_num = max(array[i])
    arrange = np.arange(min_num, max_num)
    quarter = np.percentile(arrange, [25, 50, 75]).astype(int)
    return quarter

def get_sliced_array(img_path):
    img_nii=nib.load(img_path)
    img_arr=img_nii.get_data()
    x,y,z = get_true_volume(img_arr)
    image_arr_1 = np.concatenate((img_arr[x[0],:,:],img_arr[x[1],:,:],img_arr[x[2],:,:]),axis=1)
    image_arr_2 = np.concatenate((img_arr[:,y[0],:],img_arr[:,y[1],:],img_arr[:,y[2],:]),axis=1)
    image_arr_3 = np.concatenate((img_arr[:,:,z[0]],img_arr[:,:,z[1]],img_arr[:,:,z[2]]),axis=1)
    print(image_arr_1.shape)
    print(image_arr_2.shape)
    print(image_arr_3.shape)
    image_arr = np.vstack((image_arr_1,image_arr_2,image_arr_3))
    return image_arr

def get_overlay_images(img0, img1):
    # Normalize the input images to [0,255]
    img0 = 255 * ((img0 - img0.min()) / (img0.max() - img0.min()))
    img1 = 255 * ((img1 - img1.min()) / (img1.max() - img1.min()))
    # Create the color images
    img0_red = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    img1_green = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    overlay = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    # Copy the normalized intensities into the appropriate channels of the
    # color images
    img0_red[..., 0] = img0
    img1_green[..., 1] = img1
    overlay[..., 0] = img0
    overlay[..., 1] = img1
    return overlay


from PIL import Image
import matplotlib.pyplot as plt
before_ss_path = r'F:\JHU\ndd\dataset\part_of_SWU4\sub-0025629_ses-1_T1w.nii.gz'
after_ss_path = r'C:\Users\luochuankai\Desktop\trash\skulled\sub-0025629_ses-1_T1w_noskull.nii.gz'
filename = get_filename(before_ss_path)
QA_skullstrip_path = r'F:\JHU\ndd\dataset\output1\sub-0025864\ses-1\qa'
# QA_skullstrip(before_ss_path, after_ss_path,filename,QA_skullstrip_path)

before = get_sliced_array(before_ss_path)
after = get_sliced_array(after_ss_path)


overlay = get_overlay_images(before, after)
overlay_img = Image.fromarray(overlay).transpose(Image.ROTATE_90)
# overlay_img.set_title('Coronal(XZ fixed)    Sagittal(YZ fixed)   Axial(XY fixed)')
plt.title('Coronal(XZ fixed),Sagittal(YZ fixed),Axial(XY fixed)')
plt.axis('off') # 不显示坐标轴
plt.imshow(overlay_img)
plt.savefig(r'F:\JHU\ndd\dataset\output1\sub-0025864\ses-1\qa\result.png', dpi=1990)
plt.show()










#
#
#
# def _tile_plot(imgs, titles, **kwargs):
#     """
#     Helper function
#     """
#     # Create a new figure and plot the three images
#     plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1, hspace=1)
#     fig, ax = plt.subplots(3, 3)
#     k = 0
#     for i in [0, 1, 2]:
#         ax[0,0].set_ylabel('Coronal(XZ fixed)')
#         ax[1,0].set_ylabel('Sagittal(YZ fixed)')
#         ax[2,0].set_ylabel('Axial(XY fixed)')
#         for j in [0, 1, 2]:
#             #ax[i][j].set_axis_off()
#             ax[i][j].imshow(imgs[k], **kwargs)
#             ax[i][j].set_title(titles[k])
#             k = k+1
#     fig.tight_layout()
#     return fig
#
# def QA_skullstrip(before_ss_path, after_ss_path,filename,QA_skullstrip_path):
#     before_ss_img = get_sliced_array(before_ss_path)
#     after_ss_img = get_sliced_array(after_ss_path)
#     png_path = QA_skullstrip_path + '/' + filename + '.png'
#     regtools.overlay_images(before_ss_img, after_ss_img, 'before_skullstrip', 'Overlay', 'after_skullstrip',png_path)
#
#
#
# def turn_green(array):
#     new_p = Image.fromarray(array)
#     if new_p.mode != 'RGB':
#         new_p = new_p.convert('RGB')
#     r,g,b = new_p.split()
#     r_array = np.asarray(r)
#     r0_array = np.minimum(r_array, 0)
#     r0 = Image.fromarray(r0_array)
#     b_array = np.asarray(b)
#     b0_array = np.minimum(b_array, 0)
#     b0 = Image.fromarray(b0_array)
#     green_picture = Image.merge('RGB', (r0,g,b0))
#     green_array = np.asarray(green_picture)
#     return green_array
#
# not_overlay_array = turn_green(before - after)   #(608, 768, 3)
# after_img = Image.fromarray(after)
# if after_img.mode != 'RGB':
#     after_img = after_img.convert('RGB')
# after_img.show()
#
# after_array = np.asarray(after_img)
# find = after_array[2]
# overlay_array = after_array + not_overlay_array
# overlay_image = Image.fromarray(overlay_array)
# overlay_image.show()
# green_picture = Image.merge('RGB', (r0, g, b0))
# green_array = np.asarray(green_picture)
#
#
# def QA_skullstrip(file_path,QA_skullstrip_path):
#     '''
#     file_path is the path of nii.gz file
#     QA_skullstrip_path is the folder of QA_skullstrip
#     call slicesdir `imglob pat*` to generate png file and folder
#     move files into QA_skullstrip_path
#     delete slicesdir folder
#     '''
#     file_path.replace('\\', '/')
#     QA_skullstrip_path.replace('\\', '/')
#     generate_png = 'slicesdir ' + "`imglob " + file_path + "`"
#     os.system(generate_png)
#     current_path = os.getcwd()
#     current_path.replace('\\', '/')
#     slicesdir = current_path + '/slicesdir/'
#     if os.path.exists(QA_skullstrip_path):
#         if QA_skullstrip_path.endswith('/'):
#             pass
#         else:
#             QA_skullstrip_path = QA_skullstrip_path + '/'
#         move_file = 'mv ' + slicesdir + '* ' + QA_skullstrip_path
#         os.system(move_file)
#         print(' move the last index.html into folder ' + QA_skullstrip_path)
#         os.removedirs(slicesdir)
#         print(' delete folder ' + slicesdir)
#     else:
#         print (' ERROR!!! your QA_path of skull-strip do not exit. ')
#
#
