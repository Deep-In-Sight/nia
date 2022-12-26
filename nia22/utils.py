from glob import glob 
from pathlib import Path

device_dict = {"S":"Smartphone", 
             "T":"Tablet",
             "L":"Laptop",
             "V":"VehicleLCD",
             "M":"Monitor"}

status_dict = {"F":"Focus", 
}

def two_way_dict(one_way_dict=None, device=False, status=False):
    if device:
        one_way_dict = device_dict
    elif status:
        one_way_dict = status_dict
    twowaylist = []
    for key, value in one_way_dict.items():
        twowaylist.append((key,value))
        twowaylist.append((value,key))

    return dict(twowaylist)



class VidLoader():
    def __init__(self, base_dir, uid=None, ):
        base_dir = Path(base_dir)
        self._json_dir = base_dir / Path("data/json/")
        self._raw_dir = base_dir / Path("data/raw/")
        self._s_r_dir = str(self._raw_dir)
        print("Base dir:", self._s_r_dir)
        self._ddict = two_way_dict(device=True)
        
    def load(self, uid=None, device=None, status=None, posture=None, orientation=None):
        if not uid: 
            uid="*"
        else:
            uid = f"{uid:03}"
        if not device: 
            device="*"
        else: 
            try:
                self._ddict[device]
                dkey = device
                device = self._ddict[dkey]
            except:
                dkey = self._ddict[device]

        if not status: status="*"
        if not posture: posture="*"
        if not orientation: orientation="*"
            
        search_str = str(self._s_r_dir + f"/{uid}/T1/{device}/RGB/" + \
                         f"NIA22EYE_S1_{uid}_T1_S03_{dkey}_rgb_{status}_{posture}_{orientation}.mp4")
        print(search_str)
        vid_list = glob(search_str)
        return vid_list

    def _switch_fn(self, fn):
        fn_new = fn.split("/")[-1]
        fn_new.replace(".mp4", ".json")
        return fn_new
   
    def _parse_fn(self, fn):
        fn_org = fn.split("/")[-1]
        _, _, uid, _, scen, dkey, dtype, status, posture, orientation = fn_org.split("_")
        orientation, ext = orientation.split(".mp4")
        
        return {"uid":uid, 
                "scen":scen,
                "dkey":dkey,
                "device":self._ddict[dkey], 
                "dtype":dtype, 
                "status":status, 
                "posture":posture, 
                "orientation":orientation, 
                "ext":ext}
    
    def get_jsons(self, fn_vid, sort=True):
        """Get the list of JSONs from a video file"""
        relpath = Path(fn_vid).relative_to(self._raw_dir)
        relpath = str(relpath).replace("/RGB/", "/json_rgb/").replace(".mp4", "*.json")
        json_pattern = str(self._json_dir) / Path(relpath)
        jlist = glob(str(json_pattern))
        if sort: jlist.sort()

        frames = []
        for fnj in jlist:
            frames.append(int(fnj.split("_")[-1].split(".json")[0]))
        
        return {"jsons":jlist, "frames":frames}

    def dump_png(self, fn_vid, frames):
        pass