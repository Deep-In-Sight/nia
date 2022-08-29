import numpy as np
from glob import glob
from functools import partial

def get_converter(field:str):
    if field == "inst":
        keys = ["S", "T", "L", "V", "M"]
    elif field == "condition":
        keys = ["F", "S", "D", "A", "N"]
    elif field == "posture":
        keys = ["S", "D", "P", "L", "F", 
                "C", "H", "E", "T", "U"]
    else:
        raise ValueError(field)

    return partial(_concat, keys=keys)

def _concat(value, keys=None):
    """concatenate strings"""
    code =""
    for s in keys:
        if s in value:
            code += s
        else:
            code += "X"
    return code

# get total file size
def get_total_file_size(wdir, pattern, flist=False):
    all_files = glob(wdir+ pattern)
    all_files.sort()
    nfiles = len(all_files)
    
    print(f"found {nfiles} files")
    
    file_sizes_Bytes = [os.path.getsize(cc) for cc in all_files]
    tsize_inMB = np.sum(file_sizes_Bytes) / 1024 / 1024
    if tsize_inMB > 1024:
        if flist:
            return nfiles, f"{tsize_inMB/1024:.2f}GB", all_files
        else:
            return nfiles, f"{tsize_inMB/1024:.2f}GB"
    else:
        if flist:
            return nfiles, f"{tsize_inMB:.2f}MB", all_files
        else:
            return nfiles, f"{tsize_inMB:.2f}MB"

def change_age(age):
    if age.startswith("1"):
        age = 10
    elif age.startswith("2"):
        age = 20
    elif age.startswith("3"):
        age = 30
    elif age.startswith("4"):
        age = 40
    elif age.startswith("5"):
        age = 50
    elif age.startswith("6"):
        age = 60
    return age