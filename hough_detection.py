'''
Date: 2022-02-09 11:29:33
LastEditors: yuhhong
LastEditTime: 2022-02-13 21:51:27
'''
import sys
from PIL import Image, ImageDraw
import numpy as np

from edge_detection import canny_edge_detect

def hough_transform(img, r_dim, theta_dim): 
    h, w = img.shape
    hough_space = np.zeros((r_dim, theta_dim))
    for x in range(1, w-1):
        for y in range(1, h-1):
            if img[y, x] == 0:
                continue
            # transfer edge points to one line in parameter (hough) space
            for itheta in range(theta_dim): 
                theta = itheta * np.pi / theta_dim
                r = x * np.cos(theta) + y * np.sin(theta)
                ir = int(r * r_dim / np.hypot(w, h))
                hough_space[ir, itheta] += 1
    # visualization
    # hough_space = (hough_space - np.min(hough_space)) / (np.max(hough_space) - np.min(hough_space)) * 255
    # Image.fromarray(np.uint8(hough_space)).save("./img/test_hough_space.png")
    return hough_space

def maximums(img, th, area_size): 
    '''
    This function gets the x,y-coordinates of the brightest pixel in an area, which is
    also the detected line. 
    '''
    h, w = img.shape
    high_points = []
    for x in range(0, w, area_size): 
        for y in range(0, h, area_size): 
            area = img[y:y+area_size, x:x+area_size]
            if np.amax(area) > th:
                ind = np.unravel_index(np.argmax(area, axis=None), area.shape)
                high_points.append((ind[0]+y, ind[1]+x))
    # visualization
    # img = (img - np.min(img)) / (np.max(img) - np.min(img)) * 255
    # color_img = Image.fromarray(np.uint8(img)).convert('RGB')
    # for y, x in high_points: 
    #     (R,G,B) = (255,255,0)
    #     color_img.putpixel((x,y), (R,G,B))
    # color_img.save("./img/test_hough_space_highpoints.png")
    return high_points

def re_hough_transform(img, high_points, r_dim, theta_dim): 
    h, w = img.shape
    xy_high_points = []
    for ir, itheta in high_points:
        r = ir * np.hypot(w, h) / r_dim
        theta = itheta * np.pi / theta_dim
        # y = ax + b
        if np.cos(theta):
            a = r / np.cos(theta)
        else:
            a = np.inf
        if np.tan(theta):
            b = a / np.tan(theta)
        else:
            b = np.inf
        xy_high_points.append((a, b))
    # visualization
    # img = Image.fromarray(np.uint8(img)).convert('RGB')
    # draw = ImageDraw.Draw(img)
    # for a, b in xy_high_points: 
    #     if b != np.inf and a != np.inf:
    #         draw.line([(0, b), (a, 0)], fill="green", width=0)
    #     if b == np.inf and a != np.inf:
    #         draw.line([(a, h), (a, 0)], fill="green", width=0)
    #     if b != np.inf and a == np.inf:
    #         draw.line([(0, b), (w, b)], fill="green", width=0)
    # img.save("./img/test_lines.png")
    return xy_high_points

def hough_line_detect(edges, th, area_size, r_dim=400, theta_dim=400): 
    '''
    Input: 
        edges:      <numpy array> The non-zero value represents the edge.
        th:         <int/float> The threshold of pick the pixel in Hough space.
        area_size:  <int> For one area, only one pixel will be picked.
        r_dim:      <int> The range of r. 
                    The larger it is the result will be more accurate.
        theta_dim:  <int> The range of theta. 
                    The larger it is the result will be more accurate.
    Output:
        high_points: <list> A list of detected lines. Each line is represented 
                    by its intercept, (a, b).
    '''
    # 1. Hough transform
    hough_space = hough_transform(edges, r_dim, theta_dim)
    
    # 2. Find maximums (lines in Hough space)
    high_points = maximums(hough_space, th, area_size)

    # 3. Transfer high points in Hough space to x,y-space
    xy_high_points = re_hough_transform(edges, high_points, r_dim, theta_dim)
    return xy_high_points

if __name__ == '__main__': 
    # -----------------------------------
    # python hough_detection.py test.png
    # -----------------------------------
    im = Image.open(sys.argv[1])
    gray_im = im.convert("L")

    # Canny edge detection
    print("Canny edge detection...")
    edges = canny_edge_detect(gray_im, lth=50, hth=100)
    # Image.fromarray(np.uint8(edges)).save("test_canny.png")
    print("Finished canny edge detection!")

    # Line detection in Hough space
    print("Line detection in Hough space...")
    xy_high_points = hough_line_detect(edges, th=50, area_size=20, r_dim=400, theta_dim=400)
    draw = ImageDraw.Draw(im)
    for a, b in xy_high_points: 
        if b != np.inf and a != np.inf:
            draw.line([(0, b), (a, 0)], fill="green", width=0)
        if b == np.inf and a != np.inf:
            draw.line([(a, im.height), (a, 0)], fill="green", width=0)
        if b != np.inf and a == np.inf:
            draw.line([(0, b), (im.width, b)], fill="green", width=0)
    im.save("test_lines.png")
    print("Finished line detection!")
