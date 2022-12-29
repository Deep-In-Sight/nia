#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import matplotlib.pyplot as plt 

import cv2
import json

from pathlib import Path
from glob import glob

import json
import nia22
from nia22 import utils
from nia22.mask_utils import gen_mask

# Load annotation
base_dir = Path("/home/hoseung/Work/NIA/") 
json_dir = base_dir / Path("data/json/")
raw_dir = base_dir / Path("data/raw/")

# dkey <-> device
conditions = ["F", "S", "D", "A", "N"]
postures = ["S", "D", "P", "L", "F", "C", "H", "E", "T", "U"]
device = ["S", "T", "L", "V", "M"]

dir_names = ["Eye-tracker/", "FaceAngle/", 
             "CamAngle/", "DistCam2Face/", 
             "DistDisp2Face/"]
file_names = ["_point_", "_head_", "_cam_", 
              "_dcam_", "_ddisp_"]

#data dir
dout_dir = base_dir / Path("data/rit_data")
os.makedirs(dout_dir, exist_ok=True)

# cropped img 
png_dir = str(dout_dir / Path("images/")) + '/'
os.makedirs(png_dir, exist_ok=True)

# npy label
label_dir = str(dout_dir / Path("labels/")) + '/'
os.makedirs(label_dir, exist_ok=True)

vl = utils.VidLoader(base_dir)

for uid in range(157, 165):
    for device in ["L", "M", "V", "T", "S"][:3]:
        vlist = vl.load(uid, device=device)
        # save PNG 
        for fn_vid in vlist:
            fn_base = fn_vid.split("/")[-1].split(".mp4")[0]
            cap = cv2.VideoCapture(fn_vid)
            if cap.isOpened():
                jlist = vl.get_jsons(fn_vid)
                for ff, fn_json in zip(jlist['frames'], jlist['jsons']):
                    #if True:
                    try:
                        anno = json.load(open(fn_json,"r"))
                        cap.set(cv2.CAP_PROP_POS_FRAMES, ff)
                        ok, frame = cap.read()
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        fn_png_out = str(fn_base) + f"_{ff}"
                        err = gen_mask(frame, anno, fn_png_out, png_dir, label_dir)
                        #del anno
                    except:
                    #else:
                        print("something wrong", fn_json)
            else:
                print("Can't open video file")
                print(">>>", fn_vid)
            cap.release()
            print(fn_vid, "done")

