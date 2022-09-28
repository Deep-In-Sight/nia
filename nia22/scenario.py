from email.mime import base
import os
from glob import glob
from .eyes import device_dict

class Info():
    """An iterator over the frames of a video.
    """
    def __init__(self, 
                    base_dir = None, 
                    scen = None, 
                    fn_full=None, 
                    vid_dir=None,
                    devices=["S", "T", "L", "V", "M"]):
        # {path/to/file/}{X_X_X_X_X_}{#frame}.{ext}
        try:
            len(devices)
        except:
            devices = [devices]
        
        if scen:
            if base_dir:
                self._dir = base_dir
                self.fn_full = glob(self._dir + f"*{devices[0]}_*_{scen}_???.json")[0]
            else:
                raise Exception("[ERROR], No base_dir is given")
        elif fn_full:
            self.fn_full = fn_full

        self.fn_json = self.fn_full.split("/")[-1]
        self._dir = self.fn_full.replace(self.fn_json, "")
        
        _,_,id,_,scenario,device,dtype,status,posture,orientation,num = \
            self.fn_json.split("_")
        self.id = id
        self.scenario = scenario
        self.device = devices
        self.device_d = device_dict[self.device]
        self.dtype = dtype
        self.status = status
        self.posture = posture
        self.orient = orientation
        
        # X_X_X_X_X
        self._fn_base = "_".join(self.fn_json.split("_")[:-1])
        
        self.fn_family = self._all_json()
        self.frames = self.get_nums()
        self._nframes = len(self.frames)

        # Default
        if vid_dir: self.vid_dir = vid_dir

    @property
    def vid_dir(self):
        return self._vid_dir 

    @vid_dir.setter
    def vid_dir(self, path):
        self._vid_dir = path
        self.fn_vid = self._fn_base + ".mp4"
        self._check_vid()
        
    def _all_json(self):
        """return all jsons belong to the same clip
        """
        ll = glob(self._dir + self._fn_base + "*.json")
        ll.sort()
        return [l.replace(self._dir,"") for l in ll]

    def json_at(self, frame):
        """read jason at a given frame"""
        return self._dir + self._fn_base + f"{frame:03d}.json"

    def __iter__(self):
        self._ind = 0
        return self

    def __next__(self):
        if self._ind < self._nframes:
            out = self.frames[self._ind], self.fn_family[self._ind]
            self._ind += 1
            return out
        else:
            raise StopIteration
    
    def get_nums(self):
        """get the list of frames in a video"""
        return [self._get_num(fn) for fn in self.fn_family]
    
    def _get_num(self, fn):
        num = fn.split("_")[-1]
        return int(num.split(".")[0])

    def _check_vid(self):
        if os.path.isfile(self.vid_dir + self.fn_vid):
            self._vid_good=True
        else:
            self._vid_good=False
            print("[Warning], Can't find the video file...")
            print(self.vid_dir + self.fn_vid, "is missing!")