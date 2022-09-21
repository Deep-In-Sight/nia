import os
import glob
import pandas as pd
import shutil

csvpath = glob.glob("08*/pro*/S1/*/T1/*/GazeAngle1/*.csv")
csvpath.sort()

for csv in csvpath:
    dirpath = csv.split('GazeAngle1')[0] + 'CamAngle'
    os.makedirs(dirpath, exist_ok=True)
    savename1 = csv.replace("GazeAngle1","CamAngle")
    savename2 = savename1.replace("_gaze_", "_cam_")
    
    os.rename(csv,savename2)
    
# delpath = glob.glob("08*/pro*/S1/*/T1/*/GazeAngle1")
# delpath.sort()
# for dl in delpath:
#     os.rmdir(dl)
    
print('GazeAngle2CamAngle done')

disptarget = ['Monitor','VehicleLCD']

for tar in disptarget:
    ptarget = f"08*/pro*/*/*/*/{tar}/DistDisp*/*.txt"
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
        
print('DdispTXT2CSV done')

tarpath = glob.glob("08*/pro*/S1/*/T1/*/*/*_K_*")
tarpath.sort()

for tar in tarpath:
    savename = tar.replace("_K_", "_T_")

print('K2T done')

target = ['CamAngle','DistCam2Face','DistDisp2Face']
savecnt = 0;
for tar in target:
    csvpath = glob.glob(f"08*/pro*/S1/*/T1/*/{tar}/*.csv")
    csvpath.sort()

    for csv in csvpath:
        csvfile = pd.read_csv(csv)
        try:
            newcsvfile = csvfile.drop(['Unnamed: 0'], axis=1)
        except:
            newcsvfile = csvfile
        if(len(newcsvfile)) == 0:
            savecnt = 1;
            csv = csv.replace('_gaze1_','_cam_')
            csv = csv.replace('_ir_','_cam_')
            savebeforename = csv;
            continue;
        if len(newcsvfile) > 300:
            newcsvfile = newcsvfile[:300]
        if(len(newcsvfile)) != 300:
            print(len(newcsvfile), csv)
            newdata = newcsvfile.loc[len(newcsvfile)-1]
            newdata = newdata.to_dict()
            fill = 300 - len(newcsvfile)
            for i in range(fill):
                newcsvfile = newcsvfile.append(newdata, ignore_index=True)
            
        if(len(newcsvfile)) != 300:
            print(newcsvfile)
        csv = csv.replace('_gaze1_','_cam_')
        csv = csv.replace('_ir_','_cam_')
        print(csv)
        
        newcsvfile.to_csv(csv, index=False)
        if savecnt == 1:
            savecnt = 0;
            newcsvfile.to_csv(savebeforename, index=False)
            
print('csvRemoveindex done')


fpath = glob.glob(f"08*/pro*/S1/*/T1/*/Cam*/*_gaze1_*.csv")

for f in fpath:
    print(f)
    os.remove(f)
           
fpath = glob.glob(f"08*/pro*/S1/*/T1/*/Cam*/*_ir_*.csv")

for f in fpath:
    print(f)
    os.remove(f)

target = ['CamAngle','DistCam2Face','DistDisp2Face']
for tar in target:
    fpath = glob.glob(f"08*/pro*/S1/*/T1/*/{tar}/*.csv")
    fpath.sort()
    
    for f in fpath:
        dirpath = 'newprocessing/' + f.split(tar)[0] + tar
        if not(os.path.isdir(dirpath)):
            os.makedirs(dirpath)
        savepath = 'newprocessing/' + f
        shutil.copy(f, savepath)
    
