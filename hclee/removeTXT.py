import os
import glob
import pandas as pd


dtarget = f"pro*/*/*/*/*/*/*.txt"
dlist = glob.glob(dtarget)
dlist.sort()

for pr in dlist:
    os.remove(pr)
                        