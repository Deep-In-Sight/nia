import os
import glob
import pandas as pd

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
                        