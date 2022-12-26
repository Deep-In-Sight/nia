#!/usr/bin/env python
# coding: utf-8

# In[11]:


import shutil
import os
from glob import glob
import numpy as np

alist = glob("./labels/*.npy")

ind = np.arange(len(alist))

fracs = (np.array((0.8, 0.9))*len(alist)).astype(int)

itrain, itest, ivalid = np.split(ind, fracs)

for i in itrain:
    fn =alist[i]
    shutil.move(fn, "train/" + fn)
    fn_img = fn.replace("labels", "images").replace(".npy", ".png")
    shutil.move(fn_img, "train/" + fn_img)
    
for i in itest:
    fn =alist[i]
    shutil.move(fn, "test/" + fn)
    fn_img = fn.replace("labels", "images").replace(".npy", ".png")
    shutil.move(fn_img, "test/" + fn_img)

for i in ivalid:
    fn =alist[i]
    shutil.move(fn, "validation/" + fn)
    fn_img = fn.replace("labels", "images").replace(".npy", ".png")
    shutil.move(fn_img, "validation/" + fn_img)

