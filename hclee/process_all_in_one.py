from genericpath import isfile
import os
import subprocess
import shutil
import math
import glob
import random
import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from eyetracker import Scenario

# [10.07] processing후 Tablet과 Smartphone에서 CamAngle이 *.txt라고 가정


def process_head(arr, factor):
    arr['roll'] -= np.mean(arr['roll'][5::100])
    arr['pitch'] -= np.mean(arr['pitch'][5::100])
    for field in ['roll', 'pitch', 'yaw']:
        ind = np.where(arr[field]!=0)[0]
        if len(ind) < 2:
            print("No valid points", len(ind))
            break
        elif len(ind) < len(arr):
            f = interp1d(ind, arr[field][ind])
            arr[field] = f(np.linspace(min(ind),max(ind), len(arr)))
            print("Interpolated")

    arr["roll"] *= factor
    arr["pitch"] *= factor
    arr["yaw"] *= factor

    return arr 

def move_csv(targets): 
    for tar in targets:
        fpath = glob.glob(f"processing/S1/*/T1/*/{tar}/*.csv")
        fpath.sort()
        
        for f in fpath:
            dirpath = 'newprocessing/' + f.split(tar)[0] + tar
            if not(os.path.isdir(dirpath)):
                os.makedirs(dirpath)
            savepath = 'newprocessing/' + f
            shutil.copy(f, savepath)
            #print(savepath)


def fix_length(vidlist):
    for vidpath in vidlist:
        vd = cv2.VideoCapture(vidpath)
        length = int(vd.get(cv2.CAP_PROP_FRAME_COUNT))
        vd.release()

        angpath = vidpath.replace('/RGB/','/CamAngle/').replace('_rgb_','_cam_').replace('.mp4','.csv')
        #disCampath = vidpath.replace('/RGB/','/DistCam2Face/').replace('_rgb_','_dcam_').replace('.mp4','.csv')
        #disDippath = vidpath.replace('/RGB/','/DistDisp2Face/').replace('_rgb_','_ddisp_').replace('.mp4','.csv')
        #angpath = 'newprocessing/' + angpath
        #disCampath = 'newprocessing/' + disCampath
        #disDippath = 'newprocessing/' + disDippath
        
        # Some filename missmatch expected.
        try:
            #dc = pd.read_csv(disCampath)            
            ag = pd.read_csv(angpath)
            # angle measurement by gyroscope has higher sampling rate        
            nrows = len(ag)
            if(length != nrows):
                #print("Fixing length", length, nrows)
                inds = np.round(np.linspace(0, nrows - 1, length)).astype(int)
                ag.iloc[inds].to_csv(angpath, index=False)
        except:
            continue


def backup(org_path):
    #new_path = org_path.replace("processing", "bck_processing")
    subprocess.call(['rsync', '-a', '--ignore-existing', '--relative', '--exclude=*.mp4', "processing", "bck_processing"])

def get_headangles(image, face_landmarks):
    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []
    # The camera matrix
    focal_length = 1 * img_w

    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                            [0, focal_length, img_w / 2],
                            [0, 0, 1]])                    
    # The Distortion Matrix
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    ## Head pose ##########################
    #for face_landmarks in results.multi_face_landmarks:
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
            #if idx == 1:
            #    nose_2d = (lm.x * img_w, lm.y * img_h)
            #    nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * img_w)

            x, y = int(lm.x * img_w), int(lm.y * img_h)

            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])       

    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    dist_matrix[:,:] = 0

    # Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    # Get rotational matrix
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Get angles
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
    return angles


def get_distance_iris(face_landmarks, irisIndex):
    irisPoints = []
    for start, end in irisIndex:
        irisx = face_landmarks.landmark[start].x
        irisy = face_landmarks.landmark[start].y
        
        irisxScale = int(irisx * 1920)
        irisyScale = int(irisy * 1080)
        
        irisPoints.append([irisxScale, irisyScale])
    
    #왼쪽 눈의 좌우, 오른쪽 눈의 좌우를 활용하여 두 눈 사이의 거리를 계산   
    left1x, left1y = irisPoints[5]
    left2x, left2y = irisPoints[6]
    
    right1x, right1y = irisPoints[2]
    right2x, right2y = irisPoints[4]
    
    leftIrisSizePix = ( ((left1x-left2x) ** 2) + ((left1y-left2y) ** 2) ) ** 0.5
    rightIrisSizePix = ( ((right1x-right2x) ** 2) + ((right1y-right2y) ** 2) ) ** 0.5
    leftIrisSize = leftIrisSizePix * pixSize
    rightIrisSize = rightIrisSizePix * pixSize
    
    distanceLeft = ( Focal * irisRealSize ) / (leftIrisSize) 
    distanceRight = ( Focal * irisRealSize ) / (rightIrisSize)
    
    distance = ( distanceLeft + distanceRight ) / 2 * 100   #cm로 변환
    return distance



if __name__ == '__main__':

    # ready Mediapipe 
    mp_face_mesh = mp.solutions.face_mesh
    irisIndex = mp_face_mesh.FACEMESH_IRISES
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, 
                                refine_landmarks=True,
                                min_detection_confidence=0.5, 
                                min_tracking_confidence=0.5)

    targetIdList = glob.glob("processing/S1/*")
    targetIdList.sort()
    print(targetIdList)

    # backup first
    for targetId in targetIdList:
        backup(targetId)

    #deviceList = ["Monitor", "Laptop", "VehicleLCD", "Tablet", "Smartphone"]
    for targetId in targetIdList:
        deviceList = glob.glob(f"{targetId}/T1/*")
        #deviceList.sort()

        for device in deviceList:
            # duplicate "K" and "T"
            K_csvList = glob.glob(f"{device}/*/*_K_?.csv")
            for K_csv in K_csvList:
                shutil.copyfile(K_csv, K_csv.replace("_K_", "_T_"))

            os.makedirs(f"{device}/DistCam2Face", exist_ok=True)
            os.makedirs(f"{device}/DistDisp2Face", exist_ok=True)
            os.makedirs(f"{device}/CamAngle", exist_ok=True)
            os.makedirs(f"{device}/FaceAngle", exist_ok=True)
            os.makedirs(f"{device}/Eye-tracker", exist_ok=True)
            # 모니터, 차량의 경우 DEPTH 센서를 가지고 있고, Gyro는 파일 중 소수만 데이터가 제대로 들어가 있다.
            # DEPTH 센서로 들어온 값의 경우 DistDisp2Face dir에 txt로 존재하며, Gyro 데이터의 경우 CamAngle dir에 txt로 존재한다.
            # 모니터, 차량의 코드 처리 순서는 Distance Cam 생성, Distance Display csv 처리, CamAngle csv 처리 순서로 진행된다.
            deviceName = device.split('/')[-1]
            if deviceName in ['Monitor', 'VehicleLCD']:
                distance = -1   #첫 프레임에 없으면 아무 값이나.
                Focal = 3.7E-3  #카메라의 초점거리와 시야각
                Fov = 78        #각 촬영 기기마다 고유의 값을 가짐
            elif deviceName == "Tablet":
                distance = -1   #첫 프레임에 없으면 아무 값이나.
                Focal = 2.0E-3  #카메라의 초점거리와 시야각
                Fov = 120       #각 촬영 기기마다 고유의 값을 가짐
            elif deviceName == 'Smartphone':
                distance = -1   #첫 프레임에 없으면 아무 값이나.
                Focal = 2.2E-3  #카메라의 초점거리와 시야각
                Fov = 80        #각 촬영 기기마다 고유의 값을 가짐
            elif deviceName == 'Laptop':
                distance = -1   #첫 프레임에 없으면 아무 값이나.
                #노트북의 초점거리, 시야각은 임시값임 
                Focal = 3.7E-3  #카메라의 초점거리와 시야각
                Fov = 78        #각 촬영 기기마다 고유의 값을 가짐            
            irisRealSize = 11.7E-3  #사람의 실제 눈동자 크기 (편차 약 ±0.5E-3)

            frameCountDict = {}
            
            #Distance Cam 생성
            videoPathList = glob.glob(f"{device}/RGB/*.mp4")
            videoPathList.sort()

            sco = Scenario()
            
            for videoPath in videoPathList:
                saveName = videoPath.replace("/RGB/","/DistCam2Face/").replace('_rgb_','_dcam_').replace('.mp4','.csv')
                saveName_head = videoPath.replace("/RGB/","/FaceAngle/").replace('_rgb_','_head_').replace('.mp4','.csv')
                saveName_eye = videoPath.replace("/RGB/","/Eye-tracker/").replace('_rgb_','_point_').replace('.mp4','.csv')
                
                video = cv2.VideoCapture(videoPath)
                frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                frameCountDict[videoPath] = frameCount

                print("FRAME COUNT", frameCount)
                headposes = np.zeros(frameCount, dtype=[("roll", float), 
                                        ("pitch", float),
                                        ("yaw", float)])
                resultDistance = np.zeros(frameCount, dtype=float)
                
                pixSize = ( Focal * math.tan((Fov/2) * math.pi / 180) ) / 1920 * 2
                
                #MediaPipe로 distance 계산, 추후 보정이 필요할 수 있음
                i  = 0    
                while(video.isOpened()):
                    success, image = video.read()
                    if not(success):
                        break
                    try:    #해당 image에서 iris를 못 찾을 경우 except의 코드 실행
                        image.flags.writeable = False
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results = face_mesh.process(image)
                        
                        # To improve performance
                        image.flags.writeable = True

                        if len(results.multi_face_landmarks) > 1:
                            print("Too many faces")
                            break
                        else:
                            face_landmarks = results.multi_face_landmarks[0]
                            angles = get_headangles(image, face_landmarks)
                        
                        headposes['roll'][i]  = angles[0]
                        headposes['pitch'][i] = angles[1]
                        headposes['yaw'][i]   = angles[2]
                        ## Head pose ##########################
                        

                        # distance
                        distance = get_distance_iris(face_landmarks, irisIndex)
                        resultDistance[i] = int(distance)
                    except:     #iris를 못 찾을 경우 이전 값을 그대로 사용
                        resultDistance[i] = int(distance)
                        continue
                    i+=1
                
                video.release()

                ## Eye-tracker #################
                sco.set_points(frameCount)

                fn_ = videoPath.split("/")[-1]
                _, _, ID, _, scenario, device, imgtype, status, action, orientation = fn_.split("_")
                orientation = orientation.split(".mp4")[0]

                #### Eye-tracker
                # Knee -> lapTop
                #fn_ = fn_.replace("_K_", "_T_")

                #if os.path.isfile(saveName_eye) and os.path.getsize(saveName_eye) > 1000:
                #    print(">>>>>   file exists", saveName_eye)
                #    continue
                with open(saveName_eye, "w") as f:
                    f.write("[point] x y \n")
                    px, py = random.choice(sco.scenarios[status])()
                    for xx, yy in zip(px, py):
                        f.write(f"{int(xx)}, {int(yy)}\n")
                ######################################################

                # Post process 
                factor = 360*10 # Temporary...
                process_head(headposes, factor)

                ### Save head pose 
                with open(saveName_head, "w") as f:
                    f.write("[head angle] roll      pitch      yaw\n")
                    for roll, pitch, yaw in headposes:
                        f.write(f"{roll:.4f}, {pitch:.4f}, {yaw:.4f}\n")

                print(saveName_head, "done")

                ### save iris dist
                #이미지의 시작부터 iris를 못 찾을 경우 -1로 저장된 부분을 후처리
                indexFirstCheck = np.argmax(resultDistance > 0)
                resultDistance[:indexFirstCheck] = resultDistance[indexFirstCheck]
                indexLastCheck = np.argmax(resultDistance < 0)
                resultDistance[indexLastCheck:] = resultDistance[indexLastCheck]
                
                #csv파일로 저장
                print(saveName, "saving..")
                #print(resultDistance)
                df = pd.DataFrame(resultDistance, columns = ['distance'])
                df.to_csv(saveName, index=False)

                saveName_ddist = saveName.replace("/DistCam2Face/","/DistDisp2Face/").replace("_dcam_","_ddisp_")
                if deviceName in ['Tablet', 'Smartphone', 'Laptop']:
                    df.to_csv(saveName_ddist, index=False)

                # Rename files 
                # if deviceName in ['Tablet', 'Smartphone', 'Laptop']:
                #     #Distance Display csv 처리 (스마트폰, 랩탑, 태블릿의 경우 depth가 없음)
                #     dcamPathlist = glob.glob(f"{device}/DistCam2Face/*.csv")
                #     dcamPathlist.sort()
                #     dd = pd.read_csv(disDippath)
                #     # disCam은 따로 안 고쳐? 
                #     if(length < dd.shape[0]):
                #         newdd = dd[:length]
                #         newdd.to_csv(disDippath, index=False)

                #     for dcamPath in dcamPathlist:
                #         saveName = dcamPath.replace("/DistCam2Face/","/DistDisp2Face/").replace("_dcam_","_ddisp_")
                #         print("saveName", saveName)
                        # shutil.copyfile(dcamPath,saveName)
                else:
                    #Distance Display csv 처리 (모니터, 차량의 경우 Depth 센서가 존재함)
                    #ddispPathlist = glob.glob(f"{device}/DistDisp2Face/*.txt")
                    #ddispPathlist.sort()
                    #for ddispPath in ddispPathlist:
                    #frameCountKey = ddispPath.replace("/DistDisp2Face/", "/RGB/").replace("_ddisp_","_rgb_").replace(".txt",".mp4")
                    #frameCount = int(frameCountDict[frameCountKey])
                    fn_txt = saveName_ddist.replace(".csv",".txt")
                    if os.path.isfile(fn_txt):
                        if os.path.getsize(fn_txt) > 1000:
                            with open(fn_txt) as ddispTxt:
                                ddispValue = ddispTxt.read().splitlines()
                                #ddispValue = ddispValue[:frameCount]
                                ddispCsv = pd.DataFrame(ddispValue, columns=['dintance'])
                    else:
                        ddispCsv = pd.read_csv(saveName_ddist)                        
                    
                    nrows = len(ddispCsv)
                    if(frameCount != nrows):
                        #print("Fixing length", length, nrows)
                        inds = np.round(np.linspace(0, nrows - 1, frameCount)).astype(int)
                        ddispCsv.iloc[inds].to_csv(saveName_ddist, index=False, float_format='%.1g')
                    else:
                        ddispCsv.to_csv(saveName_ddist, index=False, float_format='%.1g')
                    #print(saveName)        

            #CamAngle txt -> csv
            camAnglePathList = glob.glob(f"{device}/CamAngle/*.txt")
            camAnglePathList.sort()            
            for camAnglePath in camAnglePathList:
                if os.path.getsize(camAnglePath) > 10:
                    with open(camAnglePath) as camAngleTxt:
                        camAngleValue = camAngleTxt.read().splitlines()
                        while "" in camAngleValue:
                            camAngleValue.remove("")
                        
                        camAngleCsvData = []
                        for camAngle in camAngleValue:
                            camAngleRPY = camAngle.split(',')[1:4]
                            #= [camAngles[1], camAngles[2], camAngles[3]]
                            camAngleCsvData.append(camAngleRPY)
                        
                        CamAngleCsv = pd.DataFrame(camAngleCsvData, columns = ['Roll','Pitch','Yaw'])
                        if deviceName in ['Monitor', 'VehicleLCD', 'Laptop']:                        
                            for videoPath in videoPathList:
                                saveName = videoPath.replace("/RGB/","/CamAngle/").replace("_rgb_","_cam_").replace(".mp4",".csv")
                                CamAngleCsv.to_csv(saveName, index=False)
                                print(saveName)
                            break
                        
                        elif deviceName in ['Tablet', 'Smartphone']:                       
                            saveName = camAnglePath.replace(".txt",".csv")
                            CamAngleCsv.to_csv(saveName, index=False)
                else:
                    # Delete empty files
                    os.remove(camAnglePath)
            
            # Copy if missing CamAngle
            if deviceName in ['Monitor', 'VehicleLCD', 'Laptop']:
                camAngle_good = glob.glob(f"{device}/CamAngle/*.txt")[0]
                for videoPath in videoPathList:
                    camAnglePath = videoPath.replace("/RGB/","/CamAngle/").replace("_rgb_","_cam_").replace(".mp4",".txt")
                    if not os.path.isfile(camAnglePath):
                        print("Copying CamAngle", camAnglePath)
                        shutil.copyfile(camAngle_good, camAnglePath)


    # Move .csv files under new directory
    #targets = ['CamAngle','DistCam2Face','DistDisp2Face', 'Eye-Tracker', 'FaceAngle']
    #move_csv(targets)

    # Move .mp4 files under new directory
    vidlist = glob.glob("pro*/S1/*/T1/*/RGB/*.mp4")
    vidlist.sort()
    fix_length(vidlist)


