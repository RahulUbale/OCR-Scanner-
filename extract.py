'''
Date: 2022-02-18 11:29:33
LastEditors: shahhi
LastEditTime: 2022-02-18 21:51:27
'''
#  This python file is used to extract answer key that is injected in the form of Modified 2 D barcode (QR code) and write it in _output file
from PIL import Image
import os
import sys
import time

from PIL import Image, ImageDraw

import sys
import numpy as np

from edge_detection import canny_edge_detect
from hough_detection import hough_line_detect


def detect_raw(x,y):
    
    raw = ""
    ori_x = x
    ori_y = y
    k = y
    

    # The exact number of inputs we have
    counter = 2737
    
    while counter :
        counter -= 1
        
        # Check whole rectagular region
        if x > 1200:
            x = ori_x
            if y == k:
                y += 5
                k = y
        total = 0

        for i in range(x,x+5):  
            for j in range(y,y+5):
                sums = gray_im.getpixel((i,j)) 
                total = total + sums

        # By taking average of the values we reduce the effect of noise on detection
        final_pixel = int(total/25)
        

        # If average is near to 255 means white square is encountered which is O 
        if final_pixel <= 255 and final_pixel >= 200:

            # if one_count == 2 or one_count  == 5 : 
            raw += "0"
            

         # If average is near to 0 means Black square is encountered which is 1 
        elif final_pixel < 50 and final_pixel >= 0:  

            # if zero_count == 2 or zero_count == 5  : 
            raw += "1"
            
        x += 5
    return raw , ori_x , ori_y  


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

        return ver_a
if __name__ == '__main__':
    config = {'title_end': 365 ,'body_start': 600, 'mesh_size' : 800}

    start_time = time.time()

    # Takes injected student marked .jpg image and corresponding output file with extracted answer key is generated
    answerKey = sys.argv[2]
    im = Image.open(sys.argv[1])

    # Check the dimensions and attributes of input .jpg image
    print("Image is %s pixels wide." % im.width)
    print("Image is %s pixels high." % im.height)
    print("Image mode is %s." % im.mode)
    print("Pixel value at (10,10) is %s" % str(im.getpixel((10,10))))

    

    # size = 1700, 2200

    im = im.resize(( 1700, 2200), Image.ANTIALIAS)
    im.save("resize.jpeg")

    # im.save(outfile, "JPEG")
    print("Image is %s pixels wide." % im.width)
    print("Image is %s pixels high." % im.height)
    print("Image mode is %s." % im.mode)
    print("Pixel value at (10,10) is %s" % str(im.getpixel((10,10))))


    # Convert RGB Image to gray scale Image
    gray_im = im.convert("L")

    

   
   


    # 1. Canny edge detection ------------------------------
    print("1/3 Canny edge detection...")
    edges = canny_edge_detect(gray_im, lth=50, hth=100)
    print("1/3 Finished canny edge detection!\n")
    # visualization
    Image.fromarray(np.uint8(edges)).save("output_canny.png")

    # Set the title space to blank
    edges[:config['title_end'], :] = 0
    edges[config['body_start']:, :] = 0
    
    # visualization
    Image.fromarray(np.uint8(edges)).save("title.png")

    with Image.open("title.png") as title:
        if title.getbbox() == None:
            print("Image is empty")
        (left, upper, right, lower) = title.getbbox()
        print(left, upper, right, lower)
    # Returns four coordinates in the format (left, upper, right, lower)

    #  # 2. Line detection with Hough transform ------------------------------
    # print("2/3 Line detection in Hough space...")
    # xy_high_points = hough_line_detect(edges, th=200, area_size=30, r_dim=4000, theta_dim=4000)
    # # xy_high_points = hough_line_detect(edges, th=100, area_size=30, r_dim=3000, theta_dim=3000) # parameters for test
    # print("2/3 Finished line detection!\n")
    # print(xy_high_points)

    # ver_a = modified_lines(xy_high_points, config)

    # print(ver_a)

    print("detecting start...")
    START_raw = "11001100"
    STOP_raw = "111110011"
    start_raw = ""
    # x = 400
    y = 470
    raw = ""
    left = left + 10 # Correction
    # raw = detect_raw(x,y)
    true = 1
    # while true:
    for x in range(left , right - left): 
        
        for y in range(upper + 10,upper+100):
            raw, ori_x , ori_y  = detect_raw(x,y)
            if raw[:8] == START_raw and raw[-9:] == STOP_raw :
                true = 0
                            
                break
        if raw[:8] == START_raw and raw[-9:] == STOP_raw :   
            true = 0           
            break
    

    while true:
        for x in range(left + 10 , right - left): 
            
            for y in range(upper + 10,upper+120):
                raw, ori_x , ori_y  = detect_raw(x,y)
                if raw[:8] == START_raw and raw[-9:] == STOP_raw :
                              
                    break
            if raw[:8] == START_raw and raw[-9:] == STOP_raw :               
                break
    mid_time = time.time()
    if mid_time - start_time > 10000:
        print("Start not detected")
        
    print(raw)  
    print("Detection complete fount start at: ",ori_x , ori_y )
    # We know the location of injection 
    
    # For each couneter there is a 5 x 5 square 

    # v = y
    # print("detecting start...")
    # START_raw = "11001100"
    # STOP_raw = "111110011"
    # start_raw = ""
    # while True:
    #     u = x
        
    #     print(u,v)
    #     for i in range(len(START_raw)):
    #         start_raw = ""
    #         if u > 1200:
    #             u = 400
    #             if v == k:
    #                 v += 5
    #                 k = v
    #         total = 0

    #         for i in range(u,u+5):  
    #             for j in range(v,v+5):
    #                 sums = gray_im.getpixel((i,j)) 
    #                 total = total + sums

    #         # By taking average of the values we reduce the effect of noise on detection
    #         final_pixel = int(total/25)
            

    #         # If average is near to 255 means white square is encountered which is O 
    #         if final_pixel <= 255 and final_pixel >= 128:

    #             # if one_count == 2 or one_count  == 5 : 
    #             start_raw += "0"
                
    #         # If average is near to 0 means Black square is encountered which is 1 
    #         elif final_pixel < 128 and final_pixel >= 0:  

    #             # if zero_count == 2 or zero_count == 5  : 
    #             start_raw += "1"
    #         u += 5
    #     if START_raw == start_raw:
    #         print("start detected")
    #         raw = raw + start_raw
    #         counter -= 8 
    #         break
    #     x = x +1
    # # print(x,y)
    # # raw = ""
    # # x = 400
    # # y = 370
    # # k = y

    
    # We decode 2 D modified 2 of 5 interleaved barcode: 
    new = raw.replace("11111","W")
    new = new.replace("00000","w")
    new = new.replace("11","N")  
    new = new.replace("00","n") 
    print(new)
    START = "NnNn"
    STOP = "WnN"

    
    CODES = {
        "NNWWN" : 0 ,
        "WNNNW" : 1,
        "NWNNW" : 2,
        "WWNNN" : 3,
        "NNWNW" : 4,
        "WNWNN" : 5,
        "NWWNN" : 6,
        "NNNWW" : 7,
        "WNNWN" : 8,
        "NWNWN" : 9,
    }
    
    # Remove START
    START_NEW = new[0:4]

    # Remove STOP
    STOP_NEW = new[len(new) - 3 :len(new)]
    
    output = ""

    ENCODE = {"A":  10000 ,
            "B": 1000 ,
            "C": 100,"D": 10,"E": 1}
    
    
    for i in range(4, len(new)-3, 10):
        for j in range(10):
            if new[i+j].isupper():
                output += new[i+j].upper() 
        output += " "
        for j in range(10):
            if new[i+j].islower():
                output += new[i+j].upper() 
        output += " "
        
    for key in CODES.keys():
        output = output.replace(key, str(CODES[key]))
    output = output.split(' ')    
    
    # Store the extracted answer in file
    with open(answerKey, 'w') as f: 
    

        for i in range(0,len(output)-2,2):
            final_word = ""
            word = "{0:b}".format(int(output[i]+output[i+1]))
            if len(word) != 5:
                word = "0"*(5-len(word)) + word

            if word[0] == '1':
                final_word += "A"
                
            if word[1] == '1':
                final_word += "B"
                
            if word[2] == '1':
                final_word += "C"
                
            if word[3] == '1':
                final_word += "D"
                
            if word[4] == '1':
                final_word += "E"

            f.writelines(str(int((i/2)+1)) + ' ' + final_word + '\n')
    

    end_time = time.time()
    print("Time taken: {:.2f}s".format(end_time-start_time))




    
     

    
    
       
                    
        

    
    
            

    
   
    
