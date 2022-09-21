import glob
import os
import pandas as pd

targetList = ['Smartphone','Tablet']

for tar in targetList:
    camList = glob.glob(f"pro*/S1/*/T1/{tar}/CamAngle/*.csv")

    for cam in camList:
        csv = pd.read_csv(cam)
        csv = csv.to_list()
        
        print(csv)
