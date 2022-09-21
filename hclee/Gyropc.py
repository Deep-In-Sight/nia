import glob
import re
import cv2
import mediapipe as mp
import pandas as pd
import math
import numpy as np
import os
import shutil

targetDivList = ['Monitor','Laptop','VehicleLCD']

for Div in targetDivList:
    tarliststr = f"08*/pro*/*/*/*/{Div}/CamAngle/*.txt"
    tarlist = glob.glob(tarliststr)
    tarlist.sort()
    saveliststr = f"08*/pro*/*/*/*/{Div}/RGB/*"
    savelist = glob.glob(saveliststr)
    savelist.sort()
    
    for target in tarlist:
        tarsize = os.path.getsize(target)
        
        if tarsize > 0:
            with open(target) as fl:
                contents = fl.read().splitlines()
            
            while "" in contents:
                contents.remove("")
                
            savecontents = []
            for con in contents:
                cons = con.split(',')
                strcons = [cons[1], cons[2], cons[3]]
                savecontents.append(strcons)
            
            df = pd.DataFrame(savecontents, columns = ['Roll','Pitch','Yaw'])
            
            for save in savelist:
                savename = save.split("RGB")[0] + "GazeAngle1" + save.split("RGB")[1]
                savename = savename.split('rgb')[0] + 'gaze1' + savename.split('rgb')[1]
                savename = savename[:-3] + 'csv'
                df.to_csv(savename, index=False)
                print(savename)
            break;