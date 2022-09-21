import glob
import os

txtlist = glob.glob("pro*/S1/*/T1/*/DistC*/*.csv")

for f in txtlist:
    newf = f.replace("csv","txt")
    os.rename(f, newf)