#processing dir이 위치한 곳과 같은 dir에서 실행
import os
import glob

csvpath = glob.glob("pro*/S1/*/T1/*/GazeAngle1/*.csv")
csvpath.sort()

for csv in csvpath:
    dirpath = csv.split('GazeAngle1')[0] + 'CamAngle'
    os.makedirs(dirpath, exist_ok=True)
    savename1 = csv.replace("GazeAngle1","CamAngle")
    savename2 = savename1.replace("_gaze_", "_cam_")
    
    os.rename(csv,savename2)
    
delpath = glob.glob("pro*/S1/*/T1/*/GazeAngle1")
delpath.sort()
for dl in delpath:
    os.rmdir(dl)