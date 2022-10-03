import os
import shutil
import math
import glob
import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

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
        fpath = glob.glob(f"pro*/S1/*/T1/*/{tar}/*.csv")
        fpath.sort()
        
        for f in fpath:
            dirpath = 'newprocessing/' + f.split(tar)[0] + tar
            if not(os.path.isdir(dirpath)):
                os.makedirs(dirpath)
            savepath = 'newprocessing/' + f
            shutil.copy(f, savepath)
            #print(savepath)


def move_vids(vidlist):
    for vidpath in vidlist:
        vd = cv2.VideoCapture(vidpath)
        len = length = int(vd.get(cv2.CAP_PROP_FRAME_COUNT))
        vd.release()

        angpath = vidpath.replace('/RGB/','/CamAngle/').replace('_rgb_','_cam_').replace('.mp4','.csv')
        disCampath = vidpath.replace('/RGB/','/DistCam2Face/').replace('_rgb_','_dcam_').replace('.mp4','.csv')
        disDippath = vidpath.replace('/RGB/','/DistDisp2Face/').replace('_rgb_','_ddisp_').replace('.mp4','.csv')
        
        angpath = 'newprocessing/' + angpath
        disCampath = 'newprocessing/' + disCampath
        disDippath = 'newprocessing/' + disDippath
        ag = pd.read_csv(angpath)
        dc = pd.read_csv(disCampath)
        dd = pd.read_csv(disDippath)
        fname = vidpath.split('/')[-1]
        
        if(len != ag.shape[0]):
            csv = pd.read_csv(angpath)
            roll = csv['Roll'].tolist()
            pitch = csv['Pitch'].tolist()
            yaw = csv['Yaw'].tolist()
            r, c = csv.shape
            # 프레임 갯수 맞춰서 
            num = (r-1) / len
            newlist = []
                
            for n in range(len):
                r = roll[int(n*num)]
                p = pitch[int(n*num)]
                w = yaw[int(n*num)]
                inrpw = [r, p, w]
                newlist.append(inrpw)
                        
            df = pd.DataFrame(newlist, columns = ['Roll','Pitch','Yaw'])
            df.to_csv(angpath, index=False)
            continue
        
        if(len != dd.shape[0]):
            newdd = dd[:len]
            newdd.to_csv(disDippath, index=False)
            continue


# ready Mediapipe 
mp_face_mesh = mp.solutions.face_mesh
irisIndex = mp_face_mesh.FACEMESH_IRISES
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, 
                            refine_landmarks=True,
                            min_detection_confidence=0.5, 
                            min_tracking_confidence=0.5)


targetIdList = glob.glob("pro*/S1/*")
targetIdList.sort()
print(targetIdList)

for targetId in targetIdList:
    deviceList = glob.glob(f"{targetId}/T1/*")
    deviceList.sort()

    for device in deviceList:
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
        
        for videoPath in videoPathList:
            saveName = videoPath.replace("/RGB/","/DistCam2Face/").replace('_rgb_','_dcam_').replace('.mp4','.csv')
            saveName_head = videoPath.replace("/RGB/","/FaceAngle/").replace('_rgb_','_head_').replace('.mp4','.csv')
            
            video = cv2.VideoCapture(videoPath)
            frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            frameCountDict[videoPath] = frameCount

            print("FRAME COUNT", frameCount)
            headposes = np.zeros(frameCount, dtype=[("roll", float), 
                                       ("pitch", float),
                                       ("yaw", float)])
            
            pixSize = ( Focal * math.tan((Fov/2) * math.pi / 180) ) / 1920 * 2
            
            resultDistance = []
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

                    img_h, img_w, img_c = image.shape

                    # The camera matrix
                    focal_length = 1 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])                    
                    # The Distortion Matrix
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    ## Head pose ##########################
                    for face_landmarks in results.multi_face_landmarks:
                        for idx, lm in enumerate(face_landmarks.landmark):
                            if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                                if idx == 1:
                                    nose_2d = (lm.x * img_w, lm.y * img_h)
                                    nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * img_w)

                                x, y = int(lm.x * img_w), int(lm.y * img_h)

                                # Get the 2D Coordinates
                                face_2d.append([x, y])

                                # Get the 3D Coordinates
                                face_3d.append([x, y, lm.z])       

                        # Convert it to the NumPy array
                        face_2d = np.array(face_2d, dtype=np.float64)

                        # Convert it to the NumPy array
                        face_3d = np.array(face_3d, dtype=np.float64)

                        dist_matrix[:,:] = 0

                        # Solve PnP
                        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                        # Get rotational matrix
                        rmat, jac = cv2.Rodrigues(rot_vec)

                        # Get angles
                        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                        headposes['roll'][i]  = angles[0]
                        headposes['pitch'][i] = angles[1]
                        headposes['yaw'][i]   = angles[2]
                    ## Head pose ##########################
                    i+=1

                    #iris point를 추출하고 리스트에 저장
                    irisPoints = []
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            for start,end in irisIndex:
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
                    
                    resultDistance.append(int(distance))
                except:     #iris를 못 찾을 경우 이전 값을 그대로 사용
                    resultDistance.append(int(distance))
                    continue
            
            video.release()

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
            indexFirstCheck = np.argmax(np.array(resultDistance) > 0)
            for i in range(indexFirstCheck):
                resultDistance[i] = resultDistance[indexFirstCheck]
            
            #csv파일로 저장
            print(saveName, "saving..")
            df = pd.DataFrame(resultDistance, columns = ['distance'])
            df.to_csv(saveName, index=False)



        # Rename files 

        #if deviceName in ['Monitor', 'VehicleLCD', 'Laptop']:
        if deviceName == ['Tablet', 'Smartphone', 'Laptop']:
            #Distance Display csv 처리 (스마트폰, 랩탑, 태블릿의 경우 depth가 없음)
            dcamPathlist = glob.glob(f"{device}/DistCam2Face/*.csv")
            dcamPathlist.sort()
            for dcamPath in dcamPathlist:
                saveName = dcamPath.replace("/DistCam2Face/","/DistDisp2Face/").replace("_dcam_","_ddisp_")
                shutil.copy(dcamPath,saveName)
                print(saveName)
        else:
            #Distance Display csv 처리 (모니터, 차량의 경우 Depth 센서가 존재함)
            ddispPathlist = glob.glob(f"{device}/DistDisp2Face/*.txt")
            ddispPathlist.sort()
            for ddispPath in ddispPathlist:
                frameCountKey = ddispPath.replace("/DistDisp2Face/", "/RGB/").replace("_ddisp_","_rgb_").replace(".txt",".mp4")
                frameCount = int(frameCountDict[frameCountKey])
                if os.path.getsize(ddispPath):
                    with open(ddispPath) as ddispTxt:
                        ddispValue = ddispTxt.read().splitlines()
                        ddispValue = ddispValue[:frameCount]
                    ddispCsv = pd.DataFrame(ddispValue, columns=['dintance'])
                    saveName = ddispPath.replace(".txt",".csv")
                    ddispCsv.to_csv(saveName, index=False)
                    print(saveName)        

        #CamAngle csv 처리
        camAnglePathList = glob.glob(f"{device}/CamAngle/*.txt")
        camAnglePathList.sort()
        for camAnglePath in camAnglePathList:
            if os.path.getsize(camAnglePath) > 0:
                with open(camAnglePath) as camAngleTxt:
                    camAngleValue = camAngleTxt.read().splitlines()
                    while "" in camAngleValue:
                        camAngleValue.remove("")
                    
                    camAngleCsvData = []
                    for camAngle in camAngleValue:
                        camAngles = camAngle.split(',')
                        camAngleRPY = [camAngles[1], camAngles[2], camAngles[3]]
                        camAngleCsvData.append(camAngleRPY)
        
                    if deviceName in ['Monitor', 'VehicleLCD', 'Laptop']:                        
                        CamAngleCsv = pd.DataFrame(camAngleCsvData, columns = ['Roll','Pitch','Yaw'])
                        
                        for videoPath in videoPathList:
                            saveName = videoPath.replace("/RGB/","/CamAngle/").replace("_rgb_","_cam_").replace(".mp4",".csv")
                            CamAngleCsv.to_csv(saveName, index=False)
                            print(saveName)
                        break
                    
                    elif deviceName in ['Tablet', 'Smartphone']:                       
                        CamAngleCsv = pd.DataFrame(camAngleCsvData, columns = ['Roll','Pitch','Yaw'])
                        saveName = camAnglePath.replace(".txt",".csv")
                        CamAngleCsv.to_csv(saveName, index=False)


# Move .csv files under new directory
targets = ['CamAngle','DistCam2Face','DistDisp2Face']
move_csv(targets)

# Move .mp4 files under new directory
vidlist = glob.glob("pro*/S1/*/T1/*/RGB/*.mp4")
vidlist.sort()
move_vids(vidlist)

