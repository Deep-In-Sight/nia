import os
import glob
import pandas as pd
import shutil

target = ['CamAngle','DistCam2Face','DistDisp2Face']
for tar in target:
    fpath = glob.glob(f"pro*/S1/*/T1/*/{tar}/*.csv")
    fpath.sort()
    
    for f in fpath:
        dirpath = 'new' + f.split(tar)[0] + tar
        if not(os.path.isdir(dirpath)):
            os.makedirs(dirpath)
        savepath = 'new' + f
        shutil.copy(f, savepath)
    
    