# -*- coding: utf-8 -*-
import warnings

warnings.simplefilter("ignore")
import sys
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
from PIL import Image, ImageDraw,ImageFont
import matplotlib.pyplot as plt

'''
input : two nii.gz file  (before some process and after them)
output : an overlay image
main function: compare_two_niigz

make sure you have "arial.ttf" character, or you can change it if you like
default character size = 20, you can change it if you like
be careful about the legend(Axial, Coronal, Sagittal), because it will be different from your data

sample:
file_path1 = r'F:/JHU/ndd/dataset/part_of_SWU4/sub-0025629_ses-1_T1w.nii.gz'
file_path2 = r'C:/Users/luochuankai/Desktop/trash/skulled/sub-0025629_ses-1_T1w_noskull.nii.gz'
save_path = r'F:/JHU/ndd/dataset/output1/sub-0025864/ses-1/qa/'
compare_two_niigz(file_path1,file_path2,save_path,textsize=10)
'''

def get_filename(label):
    return os.path.splitext(os.path.splitext(os.path.basename(label))[0])[0]


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
    arrays = dict()
    img_nii=nib.load(img_path)
    img_arr=img_nii.get_data()
    Sagittal,Coronal, Axial = get_true_volume(img_arr)
    arrays['Sagittal1'] = img_arr[Sagittal[0],:,:] , Sagittal[0]
    arrays['Sagittal2'] = img_arr[Sagittal[1], :, :], Sagittal[1]
    arrays['Sagittal3'] = img_arr[Sagittal[2], :, :], Sagittal[2]
    arrays['Coronal1'] = img_arr[:, Coronal[0], :], Coronal[0]
    arrays['Coronal2'] = img_arr[:, Coronal[1], :], Coronal[1]
    arrays['Coronal3'] = img_arr[:, Coronal[2], :], Coronal[2]
    arrays['Axial1'] = img_arr[:, :, Axial[0]], Axial[0]
    arrays['Axial2'] = img_arr[:, :, Axial[1]], Axial[1]
    arrays['Axial3'] = img_arr[:, :, Axial[2]], Axial[2]
    # image_arr_1 = np.concatenate((img_arr[x[0],:,:],img_arr[x[1],:,:],img_arr[x[2],:,:]),axis=1)
    # image_arr_2 = np.concatenate((img_arr[:,y[0],:],img_arr[:,y[1],:],img_arr[:,y[2],:]),axis=1)
    # image_arr_3 = np.concatenate((img_arr[:,:,z[0]],img_arr[:,:,z[1]],img_arr[:,:,z[2]]),axis=1)
    # image_arr = np.vstack((image_arr_1,image_arr_2,image_arr_3))
    return arrays

def draw_overlay_images(img0, img1):
    # Normalize the input images to [0,255]
    img0 = 255 * ((img0 - img0.min()) / (img0.max() - img0.min()))
    img1 = 255 * ((img1 - img1.min()) / (img1.max() - img1.min()))
    # Create the color images
    img0_red = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    img1_green = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    overlay = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    # Copy the normalized intensities into the appropriate channels of the color images
    img0_red[..., 0] = img0
    img1_green[..., 1] = img1
    overlay[..., 0] = img0
    overlay[..., 1] = img1
    overlay[..., 2] = img0
    new = 255 - overlay #
    return new



def make_title(str):
    text = 'Sagittal(XZ fixed)  Coronal(YZ fixed)  Axial(XY fixed)'
    if str == 'Axial':
        text = 'Axial  Z='
    elif str == 'Coronal':
        text = 'Coronal  X='
    elif str == 'Sagittal':
        text = 'Sagittal  Y='
    return text

def gen_small_picture(overlay,before_num,key,textsize = 20):
    new_str = filter(str.isalpha, key)
    key_words = ''.join(list(new_str))
    overlay_img = Image.fromarray(overlay).transpose(Image.ROTATE_90)
    W, H = overlay_img.size
    fillColor = "#000000"
    textsize = textsize
    draw = ImageDraw.Draw(overlay_img)
    setFont = ImageFont.truetype("arial.ttf",textsize)
    txt = make_title(key_words) + str(int(before_num))
    w, h = draw.textsize(txt,font=setFont)
    draw.text(((W-w)/2,0.05*H), txt,align="center", font=setFont,fill=fillColor)
    # overlay_img.show()
    return overlay_img


def compare_two_niigz(file_path1,file_path2,save_path,textsize):
    '''
    file_path1: path to nii.gz file  (before some process)
    file_path2: path to nii.gz file  (after some process)
    save_path: path that you want to save the png file
    textsize: size of character as label shown in your image, default is 20

    '''
    before = get_sliced_array(file_path1)
    after = get_sliced_array(file_path2)
    small_img = dict()
    maxW = []
    maxH = []
    for key in before:
        before_img = before[key][0]
        before_num = before[key][1]
        after_img = after[key][0]
        overlay = draw_overlay_images(before_img, after_img)
        picture = gen_small_picture(overlay,before_num,key,textsize)
        W, H = picture.size
        maxW.append(W)
        maxH.append(H)
        small_img[key] = picture
    realH = Image.fromarray(before['Sagittal1'][0]).size[0] + Image.fromarray(before['Coronal1'][0]).size[0] + Image.fromarray(before['Axial1'][0]).size[0]
    realW = Image.fromarray(before['Sagittal1'][0]).size[1] + Image.fromarray(before['Sagittal2'][0]).size[1] + Image.fromarray(before['Sagittal3'][0]).size[1]
    def get_loc(i):
        x = 0
        y = 0
        if i%3 ==0:
            y = 0
        elif i%3 ==1:
            y =Image.fromarray(before['Sagittal1'][0]).size[0]
        elif i%3 ==2:
            y =Image.fromarray(before['Sagittal1'][0]).size[0] + Image.fromarray(before['Sagittal2'][0]).size[0]
        if int(i / 3) ==0:
            x = 0
        elif int(i / 3) ==1:
            x = Image.fromarray(before['Sagittal1'][0]).size[1]
        elif int(i / 3) ==2:
            x = Image.fromarray(before['Sagittal1'][0]).size[1] + Image.fromarray(before['Coronal1'][0]).size[1]
        return x,y
    toImage = Image.new('RGBA',(realW,realH))
    i = 0
    for key in small_img:
        fromImge = small_img[key]
        loc = get_loc(i)
        toImage.paste(fromImge, loc)
        i += 1
    # toImage.show()
    full_save_path = save_path + get_filename(file_path1) + '.png'
    print('save your compare image at  ',full_save_path)
    toImage.save(full_save_path, quality = 100)


