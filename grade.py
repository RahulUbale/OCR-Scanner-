'''
Date: 2022-02-08 11:48:59
LastEditors: yuhhong
LastEditTime: 2022-02-20 00:28:59
'''

#Import the Image and ImageFilter classes from PIL (Pillow)
from PIL import Image, ImageDraw, ImageFilter

import sys
import numpy as np

from edge_detection import canny_edge_detect
from hough_detection import hough_line_detect

import time

def grade_row(img, start_x, start_y, config):
    mesh_size = config['mesh_size']
    choice_num = config['choice_num']
    answer_dict = config['answer_dict']
    margin_hor_min = config['margin_hor_min']
    margin_hor_max = config['margin_hor_max']
    margin_space = config['margin_space']

    # If the mesh is filled more than 25% space, 
    # we will grade it as choose this answer. 
    thr = mesh_size * mesh_size * 0.25
    extra_thr = 100
    grades = []
    img_gray = img.convert("L")
    img_gray = np.array(img_gray)
    for i in range(choice_num): 
        x = start_x + (mesh_size + margin_hor_min) * i
        y = start_y
        
        # visualization
        draw = ImageDraw.Draw(img)
        draw.rectangle([(int(x), int(y)), (int(x+mesh_size), int(y+mesh_size))], fill=None, outline ='red', width=2)
        img.save("./img/test_grade.png")

        # calculate the pixels in mesh
        filled = img_gray[int(y):int(y+mesh_size), int(x):int(x+mesh_size)] < 64
        filled = np.sum(filled.astype(np.int32))
        if filled > thr: 
            grades.append(answer_dict[i])
    
    # calculate the the pixels outside mesh
    filled = img_gray[int(start_y):int(start_y+mesh_size), int(start_x-margin_hor_max):int(start_x-margin_space)] < 64
    filled = np.sum(filled.astype(np.int32))
    if filled > extra_thr: 
        grades.append(' x')
    
    # visualization
    # draw = ImageDraw.Draw(img)
    # draw.rectangle([(int(start_x-margin_hor_max), int(start_y)), (int(start_x-margin_space), int(start_y+mesh_size))], fill=None, outline ='yellow', width=2)
    # img.save("./img/test_grade.png")
    return "".join(grades)

def grade_column(img, start_x, ys, config, res_question_num):
    row_num = config['row_num']
    
    grades = []
    for row in range(row_num): 
        res_question_num = res_question_num - row
        x = start_x 
        y = ys[row]
        grades.append(grade_row(img, x, y, config))
        if res_question_num == 0: 
            break
    return grades

def grade_all(img, xs, ys, config): 
    mesh_size = config['mesh_size']
    choice_num = config['choice_num']
    question_num = config['question_num']
    row_num = config['row_num']
    col_num = config['col_num']
    margin_hor_min = config['margin_hor_min']
    margin_hor_max = config['margin_hor_max']

    col_width = mesh_size * choice_num + margin_hor_min * (choice_num-1)
    grades = []
    for col in range(col_num): 
        x = xs[0] + (col_width + margin_hor_max) * col
        res_question_num = question_num - col * row_num
        grades.extend(grade_column(img, x, ys, config, res_question_num))
    return grades

def modified_lines(lines, config):
    # split the lines into horizontal lines and vertical lines
    hor_b, ver_a = [], []
    for a, b in lines: 
        if abs(a) >= abs(b): # horizontal line
            hor_b.append(abs(b))
        if abs(a) < abs(b): # vertical line
            ver_a.append(abs(a))
    hor_b = np.sort(np.array(hor_b))
    ver_a = np.sort(np.array(ver_a))
    if len(hor_b) == 0 or len(ver_a) == 0:
        raise ValueError("Didn't detect horizontal line or vertical line.")

    # modified the beginning of vertical lines
    for i in range(len(ver_a)):
        if ver_a[i+1] - ver_a[i] >= config['mesh_size']-4: # 4 is an approximate value
            ver_a = ver_a[i:]
            break
    # modified the horizontal lines
    for i in range(len(hor_b)):
        if hor_b[i] < config['title_len']:
            continue
        if hor_b[i+1] - hor_b[i] >= config['mesh_size']-4: # 4 is an approximate value
            hor_b = hor_b[i:]
            break
    
    out_b = [hor_b[0]]
    standard_ver = hor_b[0] + config['mesh_size'] + config['margin_ver']
    i = 1
    # print('start: {}'.format(hor_b[0]))
    while i < len(hor_b): 
        # the horizontal line is not detected, we insert a standard line into them
        if hor_b[i] > standard_ver + 2:
            # print('standard: {}'.format(standard_ver))
            out_b.append(standard_ver)
            standard_ver = standard_ver + config['mesh_size'] + config['margin_ver']
            i -= 1
        # detect horizontal line 
        elif hor_b[i] >= standard_ver - 2 and hor_b[i] <= standard_ver + 2: 
            # print('detected: {}'.format(hor_b[i]))
            out_b.append(hor_b[i])
            standard_ver = hor_b[i] + config['mesh_size'] + config['margin_ver']
            i += 1
        else: # detect additional line
            i += 1
        if len(out_b) == config['row_num']:
            break
    return out_b, ver_a

if __name__ == '__main__':
    config = {'title_len': 600, 
                'mesh_size': 32, # meshes are squares
                'choice_num': 5,
                'question_num': 85, 
                'answer_dict': ['A', 'B', 'C', 'D', 'E'],
                'row_num': 29, 
                'col_num': 3, 
                'margin_hor_min': 37,
                'margin_hor_max': 163,
                'margin_ver': 15,
                'margin_space': 46}
    # config = {'title_len': 600,
    #             'mesh_size': 32, # meshes are squares
    #             'choice_num': 5,
    #             'question_num': 10, 
    #             'answer_dict': ['A', 'B', 'C', 'D', 'E'],
    #             'row_num': 5, 
    #             'col_num': 2, 
    #             'margin_hor_min': 27,
    #             'margin_hor_max': 163,
    #             'margin_ver': 14,
    #             'margin_space': 46} # parameters for test
    start_time = time.time()

    # Load an image 
    im = Image.open(sys.argv[1]).convert("RGB")

    # Output file
    outf = sys.argv[2]

    # 1. Canny edge detection ------------------------------
    print("1/3 Canny edge detection...")
    # We do not need RGB in our missions, so it is transfered into grayscale.
    gray_im = im.convert("L")
    edges = canny_edge_detect(gray_im, lth=10, hth=50)
    # edges = np.array(im.filter(ImageFilter.FIND_EDGES).convert("L"))
    print("1/3 Finished canny edge detection!\n")
    # visualization
    # Image.fromarray(np.uint8(edges)).save("output_canny.png")
        
    # Set the title space to blank
    edges[:config['title_len'], :] = 0
    # visualization
    # Image.fromarray(np.uint8(edges)).save("./img/test_rm_title.png")

    # 2. Line detection with Hough transform ------------------------------
    print("2/3 Line detection in Hough space...")
    xy_high_points = hough_line_detect(edges, th=200, area_size=30, r_dim=3000, theta_dim=3000)
    # xy_high_points = hough_line_detect(edges, th=100, area_size=30, r_dim=3000, theta_dim=3000) # parameters for test
    print("2/3 Finished line detection!\n")
    # visualization
    draw = ImageDraw.Draw(im)
    for a, b in xy_high_points: 
        if b != np.inf and a != np.inf:
            draw.line([(0, b), (a, 0)], fill="green", width=0)
        if b == np.inf and a != np.inf:
            draw.line([(a, im.height), (a, 0)], fill="green", width=0)
        if b != np.inf and a == np.inf:
            draw.line([(0, b), (im.width, b)], fill="green", width=0)
    im.save("output_lines.png")

    # 3. Calculate pixels for each question ------------------------------
    # Find the topmost horizontal line and the leftmost vertical line as the beginning of our meshes
    hor_b, ver_a = modified_lines(xy_high_points, config)
    print("3/3 Find the beginning point at ({}, {})".format(hor_b[0], ver_a[0]))
    # visualization
    # draw = ImageDraw.Draw(im)
    # draw.rectangle([(int(min_a), int(min_b)), (int(min_a+5), int(min_b+5))], fill=None, outline ='red', width=2)
    # im.save("output_grade.png")

    # Calculate the pixels in fixed meshes
    print("3/3 Scan answers...")
    grades = grade_all(im, xs=ver_a, ys=hor_b, config=config)
    with open(outf, 'w') as f: 
        for idx, g in enumerate(grades): 
            f.writelines(str(idx+1) + ' ' + g + '\n')
            if idx == config['question_num']-1:
                break
    print("3/3 Save the answers to {}!".format(outf))

    end_time = time.time()
    print("Time: {:.2f}s".format(end_time-start_time))
