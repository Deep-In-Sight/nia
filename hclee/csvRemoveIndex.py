import os
import glob
import pandas as pd

csvpath = glob.glob("pro*/S1/*/T1/*/*/*.csv")
csvpath.sort()

for csv in csvpath:
    csvfile = pd.read_csv(csv)
    try:
        newcsvfile = csvfile.drop(['Unnamed: 0'], axis=1)
    except:
        newcsvfile = csvfile
    if len(newcsvfile) > 300:
        newcsvfile = newcsvfile[:300]
    if(len(newcsvfile)) != 300:
        newdata = newcsvfile.loc[298]
        newdata = newdata.to_dict()
        newcsvfile = newcsvfile.append(newdata, ignore_index=True)
        
    if(len(newcsvfile)) != 300:
        print(newcsvfile)

    newcsvfile.to_csv(csv, index=False)