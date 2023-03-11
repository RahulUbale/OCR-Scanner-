'''
Date: 2022-02-13 12:00:02
LastEditors: yuhhong
LastEditTime: 2022-02-14 22:49:25
'''
import os
import sys

if __name__ == '__main__':
    out_dir = sys.argv[1]
    gt_dir = sys.argv[2]

    f_list = [f.replace('.jpg', '') for f in os.listdir(gt_dir) if f.endswith('.jpg')]
    out_list = os.listdir(out_dir)
    gt_list = os.listdir(gt_dir)
    for f in f_list: 
        out_f = os.path.join(out_dir, 'output_'+f+'.txt')
        if 'output_'+f+'.txt' not in out_list:
            continue
        with open(out_f, 'r') as of: 
            out_data = of.readlines()

        gt_f = os.path.join(gt_dir, f+'_groundtruth.txt')
        if f+'_groundtruth.txt' not in gt_list:
            continue
        with open(gt_f, 'r') as gf:
            gt_data = gf.readlines()

        right_cnt = 0
        wrong_cnt = 0
        for o, g in zip(out_data, gt_data): 
            if o == g:
                right_cnt += 1
            else:
                wrong_cnt += 1
        print('{}: right: {}, wrong: {}, accuracy: {}'.format(f, right_cnt, wrong_cnt, right_cnt/(right_cnt+wrong_cnt)))