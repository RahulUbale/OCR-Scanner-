'''
Date: 2022-02-18 11:29:33
LastEditors: shahhi
LastEditTime: 2022-02-18 21:51:27
'''
from PIL import Image
import os
import sys
import time


#  This python file is used to inject answer key in the form of Modified 2 D barcode (QR code)

if __name__ == '__main__':
    

    start_time = time.time()
    
    # Takes groundtruth file with answer key and corresponding student marked .jpg image
    answerKey = sys.argv[2]
    im = Image.open(sys.argv[1])

    # Check the dimensions and attributes of input .jpg image
    print("Image is %s pixels wide." % im.width)
    print("Image is %s pixels high." % im.height)
    print("Image mode is %s." % im.mode)
    print("Pixel value at (10,10) is %s" % str(im.getpixel((10,10))))

    # Convert RGB Image to gray scale Image
    gray_im = im.convert("L")

    # # 1. Canny edge detection ------------------------------
    # print("1/3 Canny edge detection...")
    # edges = canny_edge_detect(gray_im, lth=50, hth=100)
    # print("1/3 Finished canny edge detection!\n")
    # # visualization
    # Image.fromarray(np.uint8(edges)).save("output_canny.png")

    # Read the groundtruth values and store in file_data
    with open(answerKey, 'r') as file:
        file_data = ""
        for readline in file: 
            line = readline.strip()
            file_data += line + " "

   # To reduce the storage bits:
   # Convert ABCDE into binary formal A is 10000, B is 01000, C is 00100, D id 00010 and E is 00001
    ENCODE = {"A":  16 ,
            "B": 8 ,
            "C": 4,"D": 2,"E": 1}
    # print(file_data)
    # Now to handle multiple choice behavior of the questions we perform bitwise OR for each 85 questions and store as final_data
    data = file_data.split(' ')
    
    final_data = ""
    for i in range(1,len(data),2):
        # print(data[i])
        x = 0
        for char in data[i]:
            x = x | ENCODE[char]
        if x<10:
            final_data += "0" + str(x)
        else:
            final_data += str(x)
    
    
    # Interleaved 2 of 5 barcode : Used to convert numerical data into wide and narrow space and bars

    # Where W is Wide bar, w is wide space, N is Narrow bar and n is narrow space
    # referenced from : https://github.com/WhyNotHugo/python-barcode ift format from line 59 to 79

    START = "NnNn"
    STOP = "WnN"
    CODES = (    "NNWWN",    "WNNNW",    "NWNNW",    "WWNNN",    "NNWNW",    "WNWNN",    "NWWNN",    "NNNWW",    "WNNWN",    "NWNWN")
    data = START
    for i in range(0, len(final_data), 2):
                bars_digit = int(final_data[i])
                spaces_digit = int(final_data[i + 1])
                for j in range(5):
                    data += CODES[bars_digit][j].upper()
                    data += CODES[spaces_digit][j].lower()
    data += STOP 
    raw = ""
    for e in data:
        if e == "W":
            raw += "1" * 5
        if e == "w":
            raw += "0" * 5
        if e == "N":
            raw += "1" * 2
        if e == "n":
            raw += "0" * 2

    # End of reference

    # Since our input digits and output length of string of ones and zeros are constant we came up with a rectangle of size 800 x 80 (l x h)
    # 800 x 80 aproximates to 2737*5*5
    # This rectangular regionn is represents 1's and 0's in the form of 5 x 5 squares 
    # Fllowing are the x (l) and y (h) values

    # x is from 400 to 1200
    # y is from 470 to 550
    
    for i in range(395,1210):
        for j in range(365,600):
            gray_im.putpixel((i,j), (255))

    for i in range(385,395):
        for j in range(455,570):
            gray_im.putpixel((i,j), (0))

    for i in range(1210,1220):
        for j in range(455,570):
            gray_im.putpixel((i,j), (0))

    for i in range(395,1210):
        for j in range(455,465):
            gray_im.putpixel((i,j), (0))

    for i in range(395,1210):
        for j in range(560,570):
            gray_im.putpixel((i,j), (0))



    # x = 400
    # y = 370
    # k = y
    # for ch in range(len(raw)):
        
    #     if x > 1200:
    #         x = 400
    #         if y == k:
    #             y += 5
    #             k = y

    #     # If 1 is encountered in raw then present it as a  5 x 5 "Black" square in selected rectangular region
    #     if raw[ch] == '1':
    #         for i in range(x,x+5):
    #             for j in range(y,y+5):
    #                 # (R,G,B) = (0,0,0)
    #                 gray_im.putpixel((i,j), (0))
            
    #         x += 5

    #     # If 0 is encountered in raw then present it as a  5 x 5 "White" square in selected rectangular region
    #     elif raw[ch] == '0':
    #         for i in range(x,x+5):
    #             for j in range(y,y+5):
    #                 # (R,G,B) = (255,255,255)
    #                 gray_im.putpixel((i,j), (255))
    #         x += 5
    # print(x,y)

    x = 400
    y = 470
    k = y
    for ch in range(len(raw)):
        
        if x > 1200:
            x = 400
            if y == k:
                y += 5
                k = y

        # If 1 is encountered in raw then present it as a  5 x 5 "Black" square in selected rectangular region
        if raw[ch] == '1':
            for i in range(x,x+5):
                for j in range(y,y+5):
                    # (R,G,B) = (0,0,0)
                    gray_im.putpixel((i,j), (0))
            
            x += 5

        # If 0 is encountered in raw then present it as a  5 x 5 "White" square in selected rectangular region
        elif raw[ch] == '0':
            for i in range(x,x+5):
                for j in range(y,y+5):
                    # (R,G,B) = (255,255,255)
                    gray_im.putpixel((i,j), (255))
            x += 5
    # print(x,y)

    # x = 400
    # y = 570
    # k = y
    # for ch in range(len(raw)):
        
    #     if x > 1200:
    #         x = 400
    #         if y == k:
    #             y += 5
    #             k = y

    #     # If 1 is encountered in raw then present it as a  5 x 5 "Black" square in selected rectangular region
    #     if raw[ch] == '1':
    #         for i in range(x,x+5):
    #             for j in range(y,y+5):
    #                 # (R,G,B) = (0,0,0)
    #                 gray_im.putpixel((i,j), (0))
            
    #         x += 5

    #     # If 0 is encountered in raw then present it as a  5 x 5 "White" square in selected rectangular region
    #     elif raw[ch] == '0':
    #         for i in range(x,x+5):
    #             for j in range(y,y+5):
    #                 # (R,G,B) = (255,255,255)
    #                 gray_im.putpixel((i,j), (255))
    #         x += 5
    # print(x,y)

    """""          
    print(raw)
    # raw = "00110011001100110011001100"

    x = 200
    y = 400
    k = y
    for i in range(len(raw)):
        
        
        
        if raw[i] == '1':
            for j in range(x,x+1):
                for k in range(y,y+2):
                    gray_im.putpixel((j,k), (0))
                
                
            # print("*",x)
       
               
                
            # print(x)
            x = x +1
            if x > 1369:
                x = 200
                if y == k:
                    y += 60
                    k = y   
    """""
    # Saving the image as _injected.jpg
    gray_im.save("injected.jpg")
    end_time = time.time()
    print("Time taken: {:.2f}s".format(end_time-start_time))





    
