import os
import numpy as np
from PIL import Image, ImageDraw
from glob import glob

device_dict={"S":"Smartphone", 
             "T":"Tablet",
             "L":"Laptop",
             "V":"VehicleLCD",
             "M":"Monitor"}

class Eye():
    def __init__(self, anno):
        self.anno = anno
        for ano in anno:
            try:
                setattr(self, ano['label'], ano)
            except:
                print("what is this annotation?", ano)
                
        #self.l_iris.update({"rotate":.4})
        #self.r_iris.update({"rotate":.1})
                
    def __repr__(self):
        print(self.anno)
        return ""


def crop_eye(img, eyelid, magnify=1.5, width=400, height=640):
    """Crop around a eye enforcing the aspect ratio 
    
    RITnet is trained with 400 x 640 images.
    """
    xl = eyelid[:,0].min()
    xr = eyelid[:,0].max()
    yl = eyelid[:,1].min()
    yr = eyelid[:,1].max()
    
    dx = abs(xl - xr)
    dy = abs(yl - yr)
    
    if dx > dy:
        ratio = height/width
    else:
        ratio = width/height

    xc = int((xl+xr)/2)
    yc = int((yl+yr)/2)

    hw = int(magnify*dx/2)
    hh = int(hw*ratio)

    # X-Y transposed
    cropped = img[yc-hh:yc+hh, xc-hw:xc+hw] 
    return {'xrange':(yc-hh,yc+hh), 
            'yrange':(xc-hw,xc+hw)}, cropped

def mask_eyelid(eyelid, area, cropped):
    points = eyelid['points']
    polygon = []
    for pp in points:
        polygon.append((pp[0]-area['yrange'][0], pp[1]-area['xrange'][0]))

    height, width, _ = cropped.shape

    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)
    return np.array(mask)

def mask_iris(iris, area, fill=2):
    """Mask for RITnet
    """
    nx = area['xrange'][1] - area['xrange'][0]
    ny = area['yrange'][1] - area['yrange'][0]
    
    y = np.repeat(np.arange(nx), ny)
    x = np.tile(np.arange(ny), nx)

    xc = iris['cx'] - area['yrange'][0]
    yc = iris['cy'] - area['xrange'][0]

    xdist = (x-xc).reshape(nx,ny)
    ydist = (y-yc).reshape(nx,ny)

    angle = iris['rotate']
    ra = iris['rx']
    rb = iris['ry']

    cos_angle = np.cos(np.radians(angle))
    sin_angle = np.sin(np.radians(angle))

    xct = (x - xc) * cos_angle - (y - yc) * sin_angle
    yct = (x - xc) * sin_angle + (y - yc) * cos_angle 

    rad_cc = (xct**2/ra**2) + (yct**2/rb**2)

    mask = np.zeros_like(rad_cc)
    mask[rad_cc <= 1.] = fill
    return mask.reshape(nx, ny)


def mask_one_eye(img, eye, side = "l"):
    eyelid = getattr(eye, f"{side}"+"_eyelid")
    area, cropped = crop_eye(img, np.array(eyelid['points']))
    mask = mask_eyelid(eyelid, area, cropped)

    iris = getattr(eye, f"{side}"+"_iris")
    iris_mask = mask_iris(iris, area)

    # pupil center
    pupil_x, pupil_y = getattr(eye, f"{side}"+"_center")['points'][0]

    # pupil as a small iris
    pupil ={'rotate': 0.0,
                'rx': 0.2 * iris['rx'],
                'ry': 0.2 * iris['rx'],
                'cx': pupil_x,
                'cy': pupil_y}

    pupil_mask = mask_iris(pupil, area, fill=3)
    mask = np.maximum.reduce([mask, iris_mask, pupil_mask])
    return cropped, mask

class Info():
    """An iterator over the frames of a video.
    """
    def __init__(self, fn_full, vid_dir=None):
        # {path/to/file/}{X_X_X_X_X_}{#frame}.{ext}
        self.fn_full = fn_full
        self.fn_json = fn_full.split("/")[-1]
        self._dir = fn_full.replace(self.fn_json, "")
        
        _,_,id,_,scenario,device,dtype,status,posture,orientation,num = \
            self.fn_json.split("_")
        self.id = id
        self.scenario = scenario
        self.device = device        
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
        if vid_dir is None:
            self.vid_dir = self._dir
        else:
            self.vid_dir = vid_dir
    
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