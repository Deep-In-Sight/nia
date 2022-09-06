import glob
import re
import cv2
import mediapipe as mp
import pandas as pd
import math
import numpy as np
import os
import shutil

class Processing():    
    def __init__(self):
        self.Ddisp_haveDepth()
        self.Dcam()
        self.Ddisp_noDepth()
        self.gyro_mobile()
        self.gyro_pc()
        self.gaze()
    
    def gaze(self):
        targetDivList = ['Monitor','Laptop','VehicleLCD','Smartphone','Tablet']

        for Div in targetDivList:
            tarliststr = f"pro*/*/*/*/{Div}/GazeAngle1/*.csv"
            tarlist = glob.glob(tarliststr)
            df = pd.DataFrame()
            
            for target in tarlist:
                print(target)
                csv = pd.read_csv(target)
                roll = csv['Roll'].tolist()
                pitch = csv['Pitch'].tolist()
                yaw = csv['Yaw'].tolist()
                r, c = csv.shape
                # 프레임 갯수 맞춰서 
                num = r / 300
                newlist = []
                
                for n in range(300):
                    r = roll[int(n*num)]
                    p = pitch[int(n*num)]
                    w = yaw[int(n*num)]
                    print(r,p,w)
                    inrpw = [r, p, w]
                    newlist.append(inrpw)
                    
                df = pd.DataFrame(newlist, columns = ['Roll','Pitch','Yaw'])
                df.to_csv(target, index=False)


    def gyro_mobile(self):
        targetDivList = ['Smartphone','Tablet']
        
        for Div in targetDivList:
            tarliststr = f"pro*/*/*/*/{Div}/GazeAngle1/*.txt"
            tarlist = glob.glob(tarliststr)
            
            for target in tarlist:
                tarsize = os.path.getsize(target)
                
                # 비어있으면 파일 안 옮김
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
                    savename = target[:-3] + 'csv'
                    df.to_csv(savename, index=False)
                
            #for target in tarlist:
                #os.remove(target)
            
    def gyro_pc(self):
        targetDivList = ['Monitor','Laptop','VehicleLCD']
    
        for Div in targetDivList:
            tarliststr = f"pro*/*/*/*/{Div}/GazeAngle1/*.txt"
            tarlist = glob.glob(tarliststr)
            tarlist.sort()
            saveliststr = f"pro*/*/*/*/{Div}/RGB/*"
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
            
        #for target in tarlist:
            #os.remove(target)
        
    def Ddisp_haveDepth(self):
        disptarget = ['Monitor','VehicleLCD']

        for tar in disptarget:
            ptarget = f"pro*/*/*/*/{tar}/DistCam*/*.txt"
            plist = glob.glob(ptarget)
            plist.sort()
            
            for pr in plist:
                drname = pr.split("DistCam2Face")[0] + 'DistDisp2Face'
                os.makedirs(drname, exist_ok=True)
                svname = pr.split("DistCam2Face")[0] + 'DistDisp2Face' + pr.split("DistCam2Face")[1]
                svname2 = svname.split("dcam")[0] + 'ddisp' + svname.split("dcam")[1]
                
                os.rename(pr, svname2)
    
    def Ddisp_haveDepth_tocsv(self):
        disptarget = ['Monitor','VehicleLCD']

        for tar in disptarget:
            ptarget = f"pro*/*/*/*/{tar}/DistDisp*/*.txt"
            plist = glob.glob(ptarget)
            plist.sort()
            
            for pr in plist:
                tarsize = os.path.getsize(pr)
                
                if tarsize > 0:
                    with open(pr) as fl:
                        contents = fl.read().splitlines()
                
                df = pd.DataFrame(contents, columns = ['distance'])
                savename = pr[:-3] + 'csv'
                df.to_csv(savename, index=False)
                        
        
    def Ddisp_noDepth(self):
        targetDivList = ['Laptop','Smartphone','Tablet']

        for Div in targetDivList:
            tarliststr = f"pro*/*/*/*/{Div}/DistCam2Face/*.csv"
            tarlist = glob.glob(tarliststr)
            
            for target in tarlist:
                mkdirpath = target.split('DistCam2Face')[0] + 'DistDisp2Face'
                savename = target.split('DistCam2Face')[0] + 'DistDisp2Face' + target.split('DistCam2Face')[1]
                savename = savename.split('dcam')[0] + 'ddisp' + savename.split('dcam')[1]
                os.makedirs(mkdirpath, exist_ok=True)
                
                print(savename)
                shutil.copy(target, savename)
            
    def Dcam(self):
        """미디어파이프로 거리 계산
        """
        mp_face_mesh = mp.solutions.face_mesh
        target = ['Monitor','Laptop','Smartphone','Tablet','VehicleLCD']
        idx = mp_face_mesh.FACEMESH_IRISES
        irisRealSize = 11.7E-3
        distance = -1 #150.47101940872201 # 첫 프레임에 없으면 아무 값이나.  
        for tar in target:
            ptarget = f"pro*/*/*/*/{tar}/RGB/*"
            plist = glob.glob(ptarget)
            plist.sort()
            if tar == 'Monitor' or tar == 'VehicleLCD':
                Focal = 3.7E-3
                FOV = 78
            elif tar == 'Smartphone':
                Focal = 2.2E-3
                FOV = 80
            elif tar == 'Tablet':
                Focal = 2.0E-3
                FOV = 120
            elif tar == 'Laptop':
                #temporary
                Focal == 3.7E-3
                FOV = 78
            pixSize = ( Focal * math.tan((FOV/2) * math.pi / 180) ) / 1920
            for pr in plist:
                svname = pr.split("RGB")[0] + 'DistCam2Face' + pr.split("RGB")[1]
                svname = svname.split('rgb')[0] + 'dcam' + svname.split('rgb')[1]
                svname = svname[:-3] + 'csv'
                if os.path.isfile(svname):
                    print(svname,"isfile")
                    continue
                cap = cv2.VideoCapture(pr)
                resultDistance = []
                drname = pr.split("RGB")[0] + 'DistCam2Face'
                os.makedirs(drname, exist_ok=True)
                with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
                    
                    while(cap.isOpened()):
                        success, image = cap.read()
                        
                        if not(success):
                            print(pr, "done")
                            break
                        
                        try:
                            image.flags.writeable = False
                            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            results = face_mesh.process(image)
                            image.flags.writeable = True
                            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                            irispoints = []

                            if results.multi_face_landmarks:
                                for face_landmarks in results.multi_face_landmarks:
                                    for start,end in idx:
                                        irisx = face_landmarks.landmark[start].x
                                        irisy = face_landmarks.landmark[start].y
                                        
                                        irisxScale = int(irisx * 1920)
                                        irisyScale = int(irisy * 1080)
                                        
                                        irispoints.append([irisxScale, irisyScale])
                                        
                            left1x, left1y = irispoints[5]
                            left2x, left2y = irispoints[6]
                            
                            right1x, right1y = irispoints[2]
                            right2x, right2y = irispoints[4]
                            
                            leftIrisSizePix = ( ((left1x-left2x) ** 2) + ((left1y-left2y) ** 2) ) ** 0.5
                            rightIrisSizePix = ( ((right1x-right2x) ** 2) + ((right1y-right2y) ** 2) ) ** 0.5
                            leftIrisSize = leftIrisSizePix * pixSize
                            rightIrisSize = rightIrisSizePix * pixSize
                            
                            distanceLeft = ( Focal * irisRealSize ) / (leftIrisSize) 
                            distanceRight = ( Focal * irisRealSize ) / (rightIrisSize)
                            
                            distance = ( distanceLeft + distanceRight ) / 2 * 100 #cm
                            
                            resultDistance.append(distance)
                        except:
                            resultDistance.append(distance)
                            continue
                
                ind_first_ok = np.argmax(np.array(resultDistance) > 0)
                for i in range(ind_first_ok):
                    resultDistance[i] = resultDistance[ind_first_ok]
                
                print(svname, "saving..")
                df = pd.DataFrame(resultDistance, columns = ['distance'])
                df.to_csv(svname, index=False)

    
                
if __name__=="__main__" :
    P = Processing()