import glob
import cv2
import os

vidlist = glob.glob("09*/pro*/S1/*/T1/*/*/*.mp4")
vidlist.sort()

print(vidlist)
