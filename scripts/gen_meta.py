import os
import numpy as np
import pandas as pd
import csv, json
from datetime import datetime
from glob import glob


from meta_utils import *


wdir = "./"
nas_dir = './NAS/'
fn_meta = '/home/di/Work/data/NIA2022/메타데이터.xlsx'


# Init concatenators
concat_inst = get_converter("inst")
concat_condition = get_converter("condition")
concat_posture = get_converter("posture")


## Read metadata file
xlsx = pd.read_excel(fn_meta)
xlsx = list(xlsx.values)


for data in xlsx:
    clip_list_fn =[]
    
    gender, subject, medical, age, glasses, mask, ver, date, _ = data[1:10]
    date, hour = str(date).split(" ")
    hour = hour[:-3]
    
    ## Variables below are to be read from csv file ##
    username = "hoseung"
    email = "hschoi@dinsight.ai"
    glasses = "no" if glasses == "미착용" else "yes"
    cosmetic= "no"
    mask = "no" if mask == "미착용" else "yes"
    ver  = 453
    rev = str(0)

    wdir = nas_dir + f'{"".join(date.split("-")[1:])}/processing/S1/{subject:03d}/T1/*/'
    
    n_point, tsize_point = get_total_file_size(wdir, "*.txt")
    n_head, tsize_head = get_total_file_size(wdir+"GazeAngle1/", "*.txt")
    n_gaze, tsize_gaze = get_total_file_size(wdir+"GazeAngle2/", "*.txt")
    n_cam, tsize_cam = get_total_file_size(wdir, "*.txt") 
    n_dcam, tsize_d_cam = get_total_file_size(wdir+"DistCam2Face/", "*.txt") # was display pose
    n_disp, tsize_d_disp = get_total_file_size(wdir, "*.txt")
    n_rgb, tsize_rgb, cl_rgb = get_total_file_size(wdir+"RGB/", "*_rgb_*.mp4", flist=True)
    n_ir, tsize_ir, cl_ir = get_total_file_size(wdir+"IR/", "*_ir_*.mp4", flist=True)
    clip_list_fn = cl_rgb + cl_ir
    ######################################

    x = {
        "id": {"subject":subject, 
               "medical":medical},
        "age":change_age(age), 
        "glasses":glasses, 
        "cosmetic":cosmetic, 
        "mask":mask, 
        "gender":gender,
        "ver":ver, 
        "date":date, 
        "loc":loc, 
        "inst":concat_inst(inst), 
        "condition":concat_condition(condition),
        "posture":concat_posture(posture),
        "rev":rev,
        "image": {"format": {"rgb": "mp4","ir": "mp4", "point":"csv", "head":"csv", "gaze":"csv", "cam":"csv",
                             "d_cam":"csv", "d_disp":"csv"},
                    "spec":{"rgb.w":1920, "rgb.h":1080, "ir.w":1920, "ir.h":1080, 
                             "point":"yyyy-mm-dd,hh:mm:ss,x,y",
                             "head":"yyyy-mm-dd,hh:mm:ss,deg,deg,deg",
                             "gaze":"yyyy-mm-dd,hh:mm:ss,deg,deg,deg",
                             "cam":"yyyy-mm-dd,hh:mm:ss,deg,deg,deg",
                             "d_cam":"yyyy-mm-dd,hh:mm:ss,cm",
                             "d_disp":"yyyy-mm-dd,hh:mm:ss,cm"},
                    "total_size":{"rgb":tsize_rgb, "ir":tsize_ir, "point":tsize_point, "head":tsize_head,
                                  "gaze":tsize_gaze, "cam":tsize_cam, "d_cam":tsize_d_cam, "d_disp":tsize_d_disp},
                    "total_count":{"rgb":n_rgb, "ir":n_ir, "point":n_point, "head":n_head, "gaze":n_gaze,
                                   "cam":n_cam, "d_cam":n_dcam, "d_disp":n_disp}
                 },
        "task":{
            "name":"NIA_EYE",
            "created": date + ", " + hour, 
            "updated":"", 
            "username":username, 
            "email":email},
        "filelist":clip_list_fn
    }

    # Dump json file
    fn = f"{subject:03d}.json"
    with open(fn, "w") as f:
        json.dump(x, f, indent=2, ensure_ascii=False)
