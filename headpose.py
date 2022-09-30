import cv2
import mediapipe as mp
import numpy as np
import os
from glob import glob
import shutil

from scipy.interpolate import interp1d


evice_dict={"S":"Smartphone", 
             "T":"Tablet",
             "L":"Laptop",
             "V":"VehicleLCD",
             "M":"Monitor"}
status_dict={"F":"Focus"}

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

factor = 360*10 # In fact, we need to take acount of focal length, pixel scale, and distortion


base_dir = ["/mnt/syn2422/raw/raw/",
           "/media/di/mx500_2tb2/NIA2022_2/"][0]

for date in ["0913"]:
    wdir = base_dir+f'{date}/processing/S1/'

    flist = glob(wdir+"0??/T1/*/RGB/*_rgb_*.mp4")
    flist.sort()
    print(len(flist))
    # .mp4 파일명 수정
    # .csv도 필요하면 적용
    # mp4 먼저 고치고 나머지 처리하면 csv 파일 이름 변경할 필요 없음. 
    for fncsv in flist:
        fnew = fncsv.replace("_K_", "_T_")
        if fnew != fncsv:
            shutil.move(fncsv, fnew)
            
    # 수정된 이름으로 다시 
    flist = glob(wdir+"0??/T1/*/RGB/*_rgb_*.mp4")
    flist.sort()
    for iin, fn in enumerate(flist):
        #fn.replace("processing")
        out_dir = fn.split("NIA22EYE")[0]
        fn_ = fn.split("/")[-1]

        _, _, ID, _, scenario, device, imgtype, status, action, orientation = fn_.split("_")
        orientation = orientation.split(".mp4")[0]

        new_dir = out_dir.replace("RGB/", "FaceAngle/")

        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        fn_out = fn_.replace("rgb", "head")
        fn_out = fn_out.replace(".mp4", ".csv")
        
        if os.path.isfile(new_dir+fn_out) and os.path.getsize(new_dir+fn_out) > 40:
            print("pass")
            continue

        cap = cv2.VideoCapture(fn)    
        nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        arr = np.zeros(nframes, dtype=[("roll", float), 
                                       ("pitch", float),
                                       ("yaw", float)])
        i = 0
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Flip the image horizontally for a later selfie-view display
            # Also convert the color space from BGR to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

            # To improve performance
            image.flags.writeable = False

            # Get the result
            results = face_mesh.process(image)

            # To improve performance
            image.flags.writeable = True

            # Convert the color space from RGB to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []

            if results.multi_face_landmarks:
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

                    # The camera matrix
                    focal_length = 1 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])

                    # The Distortion Matrix
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    # Solve PnP
                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                    # Get rotational matrix
                    rmat, jac = cv2.Rodrigues(rot_vec)

                    # Get angles
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                    arr['roll'][i]  = angles[0]
                    arr['pitch'][i] = angles[1]
                    arr['yaw'][i]   = angles[2]

            i+=1

        cap.release()

        # temp
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


        with open(new_dir+fn_out, "w") as f:
            f.write("[head angle] roll      pitch      yaw\n")
            for roll, pitch, yaw in arr:
                f.write(f"{roll:.4f}, {pitch:.4f}, {yaw:.4f}\n")

        print(new_dir+fn_out, "done")










for date in ["0829", "0901", "0902", "0905", "0907", "0908"][:1]:
    wdir = base_dir+f'{date}/processing/S1/'

    flist = glob(wdir+"0??/T1/*/RGB/*_rgb_*.mp4")
    flist.sort()
    print(len(flist))
    # .mp4 파일명 수정
    # .csv도 필요하면 적용
    # mp4 먼저 고치고 나머지 처리하면 csv 파일 이름 변경할 필요 없음. 
    for fncsv in flist:
        fnew = fncsv.replace("_K_", "_T_")
        if fnew != fncsv:
            shutil.move(fncsv, fnew)
            
    # 수정된 이름으로 다시 
    flist = glob(wdir+"0??/T1/*/RGB/*_rgb_*.mp4")
    flist.sort()
    for iin, fn in enumerate(flist):
        out_dir = fn.split("NIA22EYE")[0]
        fn_ = fn.split("/")[-1]

        _, _, ID, _, scenario, device, imgtype, status, action, orientation = fn_.split("_")
        orientation = orientation.split(".mp4")[0]

        new_dir = out_dir.replace("RGB/", "FaceAngle/")

        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        fn_out = fn_.replace("rgb", "head")
        fn_out = fn_out.replace(".mp4", ".csv")
        
        if os.path.isfile(new_dir+fn_out) and os.path.getsize(new_dir+fn_out) > 40:
            print("pass")
            continue

        cap = cv2.VideoCapture(fn)    
        nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        arr = np.zeros(nframes, dtype=[("roll", float), 
                                       ("pitch", float),
                                       ("yaw", float)])
        i = 0
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Flip the image horizontally for a later selfie-view display
            # Also convert the color space from BGR to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

            # To improve performance
            image.flags.writeable = False

            # Get the result
            results = face_mesh.process(image)

            # To improve performance
            image.flags.writeable = True

            # Convert the color space from RGB to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []

            if results.multi_face_landmarks:
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

                    # The camera matrix
                    focal_length = 1 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])

                    # The Distortion Matrix
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    # Solve PnP
                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                    # Get rotational matrix
                    rmat, jac = cv2.Rodrigues(rot_vec)

                    # Get angles
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                    arr['roll'][i]  = angles[0]
                    arr['pitch'][i] = angles[1]
                    arr['yaw'][i]   = angles[2]

            i+=1

        cap.release()

        # temp
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


        with open(new_dir+fn_out, "w") as f:
            f.write("[head angle] roll      pitch      yaw\n")
            for roll, pitch, yaw in arr:
                f.write(f"{roll:.4f}, {pitch:.4f}, {yaw:.4f}\n")

        print(new_dir+fn_out, "done")



