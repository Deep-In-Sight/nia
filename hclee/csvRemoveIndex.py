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

    newcsvfile.to_csv(csv, index=False)