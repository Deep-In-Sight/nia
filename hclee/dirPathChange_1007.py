import glob
import os
import shutil

posedic = {'서기':'S','앉기':'D','위로눕기':'P',
        '옆으로눕기':'L','엎드리기':'F', '턱괴기':'C', 
        '한손기기사용':'H', '음식섭취':'E', 
        '무릎거치':'T', '휴대폰사용':'U'}
statedic = {'집중':'F','졸림':'S','집중결핍(산만)':'D',
        '집중하락':'A','태만(이탈)':'N'}
dispdic = {'상단에위치':'T','좌측에위치':'L','우측에위치':'R'}
typedic = {'차량':'VehicleLCD','모니터':'Monitor','노트북1':'Laptop',
        '노트북3':'Laptop','태블릿2':'Tablet','태블릿3':'Tablet',
        '스마트폰2':'Smartphone','스마트폰3':'Smartphone'}
idDirlist = glob.glob('*_*')
pcClass = ['차량','모니터','노트북']
moClass = ['태블릿','스마트폰']

for idDir in idDirlist:
    ID = idDir.split('_')[0]
    place = 'S1'
    Try = 'T1'
    
    for cl in pcClass:
        dirlist = glob.glob(f'{idDir}/*{cl}*/*/*')
        dirlist.sort()
        dirlist = dirlist[::-1]
        
        for dirpath in dirlist:
            print(dirpath)
            type = dirpath.split('/')[1]
            dirname = dirpath.split('/')[-1]
            pose = dirname.split('_')[1]
            state = dirname.split('_')[-1]
            disp = dirname.split('_')[2].split('-')[-1]
            if dirname.split('_')[0] != '11':
                scenario = dirname.split('_')[0]
                scenario = scenario.zfill(2)
                
            pose = posedic[pose]
            state = statedic[state]
            disp = dispdic[disp]
            type = typedic[type]
            
            rgbvid = glob.glob(dirpath + '/video1*')
            irvid = glob.glob(dirpath + '/video2*')    
            gyro1 = glob.glob(dirpath + '/*1.txt')
            depth = glob.glob(dirpath + '/*sensor.txt')
            
            if rgbvid:
                rgbvid = rgbvid[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/RGB"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_rgb_{state}_{pose}_{disp}.mp4"
                if os.path.isfile(targetname):
                    print("isfile!", rgbvid)
                    print("filesize", os.path.getsize(targetname))
                else:
                    os.rename(rgbvid, targetname)
                print(targetname)
            
            if irvid:
                irvid = irvid[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/IR"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_ir_{state}_{pose}_{disp}.mp4"
                if os.path.isfile(targetname):
                    print("isfile!", irvid)
                    print("filesize", os.path.getsize(targetname))
                else:
                    os.rename(irvid, targetname)
                print(targetname)
            if gyro1:
                gyro1 = gyro1[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/CamAngle"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_cam_{state}_{pose}_{disp}.csv"
                if os.path.isfile(targetname):
                    print("isfile!", gyro1)
                    print("filesize", os.path.getsize(targetname))
                else:
                    shutil.copyfile(gyro1, targetname)
                    #os.rename(gyro1, targetname)
                print(targetname)
            if depth:
                depth = depth[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/DistCam2Face"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_dcam_{state}_{pose}_{disp}.csv"
                if os.path.isfile(targetname):
                    print("isfile!", depth)
                    print("filesize", os.path.getsize(targetname))
                else:
                    shutil.copyfile(depth, targetname)
                    #os.rename(depth, targetname)
                print(targetname)
                
    for cl in moClass:
        dirlist = glob.glob(f'{idDir}/*{cl}*/*/*')
        dirlist.sort()
        
        for dirpath in dirlist:
            print(dirpath)
            type = dirpath.split('/')[1]
            dirname = dirpath.split('/')[-1]
            pose = dirname.split('_')[1]
            state = dirname.split('_')[-1]
            disp = dirname.split('_')[2].split('-')[-1]
            # 랜덤 시나리오가 PC에서는 10, 모바일에서는 11로 나옴 
            if dirname.split('_')[0] != '11' or dirname.split('_')[0] != '10':
                scenario = dirname.split('_')[0]
                scenario = scenario.zfill(2)
                
            pose = posedic[pose]
            state = statedic[state]
            disp = dispdic[disp]
            type = typedic[type]
            
            rgbvid = glob.glob(dirpath + '/video*')   
            gyro1 = glob.glob(dirpath + '/*.txt')

            
            if rgbvid:
                rgbvid = rgbvid[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/RGB"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_rgb_{state}_{pose}_{disp}.mp4"
                if os.path.isfile(targetname):
                    print("isfile!", rgbvid)
                    print("filesize", os.path.getsize(targetname))
                else:
                    os.rename(rgbvid, targetname)
                print(targetname)
            
            if gyro1:
                gyro1 = gyro1[0]
                targetpath = f"processing/{place}/{ID}/{Try}/{type}/CamAngle"
                os.makedirs(targetpath,exist_ok=True)
                targetname = f"{targetpath}/NIA22EYE_{place}_{ID}_{Try}_S{scenario}_{type[0]}_cam_{state}_{pose}_{disp}.csv"
                if os.path.isfile(targetname):
                    print("isfile!", gyro1)
                    print("filesize", os.path.getsize(targetname))
                else:
                    shutil.copyfile(gyro1, targetname)
                    #os.rename(gyro1, targetname)
                print(targetname)

        
            
