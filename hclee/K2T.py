import os
import glob

tarpath = glob.glob("pro*/S1/*/T1/*/*/*_K_*")
tarpath.sort()

for tar in tarpath:
    savename = tar.replace("_K_", "_T_")
    
