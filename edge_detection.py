'''
Date: 2022-02-08 20:57:00
LastEditors: yuhhong
LastEditTime: 2022-02-19 23:30:59
'''
#Import the Image and ImageFilter classes from PIL (Pillow)
from PIL import Image, ImageFilter

import sys
import numpy as np

def gray_gradient(img):
    sobelx = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    sobely = [1, 2, 1, 0, 0, 0, -1, -2, -1]
    gx = np.array(img.filter(ImageFilter.Kernel((3,3), sobelx, 1, 0)))
    gy = np.array(img.filter(ImageFilter.Kernel((3,3), sobely, 1, 0)))
    
    gv = np.hypot(gx, gy)
    gd = np.arctan2(gy, gx) # [0 degree, 90 degree]

    # visualization
    # Image.fromarray(np.uint8(gx)).save("./img/test_gx.png")
    # Image.fromarray(np.uint8(gy)).save("./img/test_gy.png")
    # Image.fromarray(np.uint8(gv)).save("./img/test_gradient.png")
    return gv, gd

def nonmax_supress(gv, gd): 
    nms = np.zeros(gv.shape, gv.dtype)  
    h, w = gv.shape
    for x in range(1, w-1):
        for y in range(1, h-1): 
            v = gv[y, x]
            d = gd[y, x] * 180 / np.pi
            if d >= 0 and d < 30:
                dx, dy = 1, 0 
            elif d >= 30 and d < 60:
                dx, dy = 1, 1 
            elif d >= 60 and d <= 90:
                dx, dy = 0, 1
            if v >= gv[y+dy, x+dx] and v >= gv[y-dy, x-dx]: 
                nms[y, x] = v
    # visualization
    # Image.fromarray(np.uint8(nms)).save("./img/test_nms.png")
    return nms

def double_threshold_detect(nms, lth, hth):
    stro_edge = np.zeros(nms.shape)
    weak_edge = np.zeros(nms.shape)
    h, w = nms.shape
    for x in range(1, w-1):
        for y in range(1, h-1):
            if nms[y, x] >= hth:
                stro_edge[y, x] = nms[y, x]
            elif nms[y, x] >= lth:
                weak_edge[y, x] = nms[y, x]
    
    # Process the weak edges
    # If a weak edge connects to a strong edge, it will be added to 
    # the final edges. Otherwise, it will be removed. 
    for x in range(1, w-1):
        for y in range(1, h-1): 
            if weak_edge[y, x] == 0:
                continue
            try_x = [-1, 0, 1, -1, 1, -1, 0, 1]
            try_y = [-1, -1, -1, 0, 0, 1, 1, 1]
            for tx, ty in zip(try_x, try_y): 
                if stro_edge[y+ty, x+tx]!=0:
                    stro_edge[y, x] = nms[y, x]
                    break

    # visualization
    # Image.fromarray(np.uint8(stro_edge)).save("./img/test_stro_edge.png")
    # Image.fromarray(np.uint8(weak_edge)).save("./img/test_weak_edge.png")
    return stro_edge
    
def canny_edge_detect(img, lth, hth):
    '''
    Input: 
        img:        <PIL Image>
        lth, hth:   <int/float> Low and high thresholds.
    Output: 
        edge:       <numpy array>
    '''
    # 1. Gaussian filter
    # This step is for reducing the noise. 
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    # visualization
    # img.save("test_gaussian.png")
    
    # 2. Calculate gradient value and gradient direction
    gv, gd = gray_gradient(img)

    # 3. Non-maximum suppression
    nms = nonmax_supress(gv, gd)

    # 4. Use upper and lower thresholds to detect edges
    edge = double_threshold_detect(nms, lth, hth) 
    return edge

if __name__ == '__main__': 
    # -----------------------------------
    # python edge_detection.py test.png
    # -----------------------------------
    im = Image.open(sys.argv[1])
    gray_im = im.convert("L")

    # Canny edge detection
    print("Canny edge detection...")
    edges = canny_edge_detect(gray_im, lth=50, hth=100)
    Image.fromarray(np.uint8(edges)).save("./img/test_canny.png")
    print("Finished canny edge detection!")