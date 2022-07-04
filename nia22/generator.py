import numpy as np
from scipy import interpolate
from functools import partial
from datetime import datetime, timedelta

#import json


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

class Particle():
    def __init__(self, width, height, nframes_tot):
        """mimic random gaze point move as randomly accelerated point in a lectangle.
        """
        self.width = width
        self.height = height
        self.nframes_tot = nframes_tot
        self.x = np.random.randint(100, self.width)
        self.y = np.random.randint(100, self.height)
        self.xtrace = []
        self.ytrace = []
        self.dxdt = 0
        self.dydt = 0
        self.ddxdtt = 0
        self.ddydtt = 0
        self.complete = False
        
    def accel(self, nframes):
        """accelerate for dt"""
        for i in range(nframes):
            # revert if outside the screen
            if self.x < 0 or self.x > self.width: 
                self.x = min([max([0,self.x]),self.width])
                self.ddxdtt *= -0.5
                self.dxdt *= -0.1
            if self.y < 0 or self.y > self.height: 
                self.y = min([max([0,self.y]),self.height])
                self.ddydtt *= -0.5
                self.dydt *= -0.1
                
            self.dxdt += self.ddxdtt
            self.dydt += self.ddydtt
            self.x += self.dxdt
            self.y += self.dydt

            self.xtrace.append(self.x)
            self.ytrace.append(self.y)
            if len(self.xtrace) == self.nframes_tot:
                self.complete = True
                break
    
    def random_move(self, max_dt = 10, max_acc = 3, min_acc=2, dt_stop=5):
        """
        parameters
        ----------
        dt_stop:
        dt larger than this threshold casues 'staring'
        """
        self.xtrace = []
        self.ytrace = []
        while not self.complete:
            dt = np.random.randint(max_dt) # random duration
            # random acc with 
            self.ddxdtt = np.random.randint(min_acc, max_acc) * np.sign(np.random.rand() - self.x/self.width) 
            self.ddydtt = np.random.randint(min_acc, max_acc) * np.sign(np.random.rand() - self.y/self.height) 
            if dt >= dt_stop:
                self.ddxdtt *= 0.01
                self.ddydtt *= 0.01
                self.dxdt *= 0.001
                self.dydt *= 0.001
                
            self.accel(dt)
        return np.clip(self.xtrace, 0, self.width), np.clip(self.ytrace, 0, self.height)
    

def _gen_focus_xy(key_point_x, key_point_y, dt1, dt2, dt3):
    nrows = 3
    ncols = 5
    tnow = 0
    key_point_x_t = []
    key_point_x_t.append(tnow)
    key_point_y_t = []
    key_point_y_t.append(tnow)

    for i in range(nrows):
        for j in range(ncols):
            # next point
            tnow += dt3
            key_point_x_t.append(tnow)
            # gaze
            tnow += dt1

        # next row
        tnow += dt2
        key_point_y_t.append(tnow)

    key_point_x_t.append(tnow)
    return key_point_x_t, key_point_y_t

def gen_focus_xy():
    nrows = 8 # 8 (virtual) rows 
    ncols = 5 # 5 (virtual) points in a row

    # x, y coordinates of key points 
    key_point_x = [0] + [50, 250, 500, 750, 1000] * nrows + [1050]
    key_point_y = [100, 310, 520, 730, 940, 1150, 1360, 1570, 1880]
    ## time stamp of each key point in fraction of the total length
    # dt1: duration of gazing a point
    # dt2: time taken to switch to the next row
    # dt3: time taken to switch to the next point
    # All values are in relative unit and will be scaled to fit the clip duration.
    dt1 = 0.2
    dt2 = 0.05
    dt3 = 0.01
    
    return _gen_focus_xy(key_point_x, key_point_y, dt1, dt2, dt3)

def gen_no_interest_xy(width, height, nframes):
    p = Particle(width, height, nframes)
    return p.random_move(max_dt=30, dt_stop=15, max_acc=10, min_acc=5)# try other values!

def rescale_duration(key_point_x_t, nframes):
    # rescale to the clip duration
    key_point_x_t = np.array(key_point_x_t)
    key_point_x_t = key_point_x_t / key_point_x_t.max() * nframes
    return key_point_x_t.astype(int) # key point frames

def error(nn, mag=1):
    return (np.random.rand(nn) - 0.5) * mag

def interpolate_pos(key_point_x, key_point_frames_x, nframes, err_mag = 3):
    pos = np.zeros(nframes)
    assert len(key_point_x) == len(key_point_frames_x)

    # x 에러 크기
    for i in range(len(key_point_x)-1):
        nn = key_point_frames_x[i+1] - key_point_frames_x[i]
        pos[key_point_frames_x[i]:key_point_frames_x[i+1]] = key_point_x[i] + error(nn, err_mag)
    
    return pos

def gen_error(nframes, mag=30, max_dt=100):    
    # 
    i = 0
    keyframes = []
    keyvalues = []
    while i < nframes-1:
        keyframes.append(i)
        dt = np.random.randint(1, max_dt)
        i += dt

    # to keep both side bounded (not to have exploding extrapolation)
    keyframes.append(nframes-1)
    keyvalues.append(error(len(keyframes), mag))
    
    # interpolate
    smooth_curve = interpolate.interp1d(keyframes, keyvalues, kind='cubic', fill_value='extrapolate')
    err = smooth_curve(np.arange(nframes))[0]
    
    return err

class Fake_generator():
    def __init__(self, wdir, nframes, width, height, display, posture, condition, orientation):
        self.wdir = wdir
        self.nframes = nframes
        self.width  = width
        self.height = height
        self.condition = condition
        self.display = display
        self.posture = posture
        self.orientation = orientation
        #if self.display == "S":
        self.disp_size_x = 7 # in cm, 내 핸드폰
        self.disp_size_y = 17 # in cm
        self.gen_timestamp()
            
    def gen_all(self):
        self.gen_d_cam()
        self.gen_d_disp()        
        self.gen_head()
        self.gen_pose_d()
        self.gen_gaze_eye_trakcer()
        
    def gen_timestamp(self):
        # datetime object containing current date and time
        now = datetime.now()
        self.timestamp = []
        for i in range(self.nframes):
            now += timedelta(milliseconds=33.3)
            self.timestamp.append(str(now).replace(" ", ", "))

    def gen_head(self):
        """head pose in roll,pitch,yaw"""
        if self.condition == "F":
            mag = 0.2
            max_dt = 100
        elif self.condition == "S":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "D":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "A":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "N":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        
        xx = gen_error(self.nframes, mag=mag, max_dt = max_dt)
        yy = gen_error(self.nframes, mag=mag, max_dt = max_dt)
        
        pitch = np.rad2deg(np.arctan(xx)) # incorrect!
        yaw = np.rad2deg(np.arctan(yy))
        
        roll = np.zeros(self.nframes)
        self.head = {"time":self.timestamp, "roll":roll, "pitch":pitch, "yaw":yaw}        
    
    
    def gen_pose_d(self):
        """display pose in roll,pitch,yaw"""
        if self.condition == "F":
            mag = 0.2
            max_dt = 100
        elif self.condition == "S":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "D":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "A":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        elif self.condition == "N":
            mag = 1 # mag 1 -> 45 degree
            max_dt = 50
        
        xx = gen_error(self.nframes, mag=mag, max_dt = max_dt)
        yy = gen_error(self.nframes, mag=mag, max_dt = max_dt)
        
        pitch = np.rad2deg(np.arctan(xx)) # incorrect!
        yaw = np.rad2deg(np.arctan(yy))
        
        roll = np.zeros(self.nframes)
        self.cam = {"time":self.timestamp, "roll":roll, "pitch":pitch, "yaw":yaw}        
        
    def gen_d_cam(self, target_dist):
        condition = self.condition
        if condition == "F":
            d_cam = gen_error(self.nframes, mag=5, max_dt = 50) + target_dist
        elif condition == "S":
            # maximum -50% ~ 250% error
            d_cam = gen_error(self.nframes, mag=6, max_dt = 80) + target_dist * 2.5
        elif condition == "D":
            # maximum -50% ~ 250% error
            d_cam = gen_error(self.nframes, mag=6, max_dt = 20) + target_dist
        elif condition == "A":
            # maximum -50% ~ 250% error
            d_cam = gen_error(self.nframes, mag=6, max_dt = 100) + target_dist
        elif condition == "N":
            # maximum -50% ~ 250% error
            d_cam = gen_error(self.nframes, mag=5, max_dt = 50) + target_dist * 1.5
        self.d_cam = {"time":self.timestamp, 'd_cam':d_cam}
        
    def gen_d_disp(self, target_dist):
        condition = self.condition
        if condition == "F":
            d_disp = gen_error(self.nframes, mag=5, max_dt = 50) + target_dist
        elif condition == "S":
            # maximum -50% ~ 250% error
            d_disp = gen_error(self.nframes, mag=6, max_dt = 80) + target_dist * 2.5
        elif condition == "D":
            # maximum -50% ~ 250% error
            d_disp = gen_error(self.nframes, mag=6, max_dt = 20) + target_dist
        elif condition == "A":
            # maximum -50% ~ 250% error
            d_disp = gen_error(self.nframes, mag=6, max_dt = 100) + target_dist
        elif condition == "N":
            # maximum -50% ~ 250% error
            d_disp = gen_error(self.nframes, mag=5, max_dt = 50) + target_dist * 1.5
        self.d_disp = {"time":self.timestamp, 'd_disp':d_disp}
            
    def gen_gaze_eye_trakcer(self):
        """generate both eye tracker target and gaze pose.
            eye tracker in x,y coords.
            gaze pose in roll, pitch, yaw"""
        condition = self.condition
        if condition == "F":
            # 집중
            key_point_x_t, key_point_y_t = gen_focus_xy()
            key_point_frames_x = rescale_duration(key_point_x_t, self.nframes)
            key_point_frames_y = rescale_duration(key_point_y_t, self.nframes)
            self.gaze_x = interpolate_pos(key_point_x_t, key_point_frames_x, self.nframes, err_mag = 30)
            self.gaze_y = interpolate_pos(key_point_y_t, key_point_frames_y, self.nframes, err_mag = 20)
            point_x = interpolate_pos(key_point_x_t, key_point_frames_x, self.nframes, err_mag = 0)
            point_y = interpolate_pos(key_point_y_t, key_point_frames_y, self.nframes, err_mag = 0)
        elif condition == "S":
            # 졸림
            point_x, point_y = gen_no_interest_xy(self.width, self.height, self.nframes)
            errx = gen_error(self.nframes, mag=10, max_dt = 70)
            erry = gen_error(self.nframes, mag=10, max_dt = 70)
            self.gaze_x = np.clip(point_x + errx, 0, self.width) # [0, 1920]
            self.gaze_y = np.clip(point_y + erry, 0, self.height) # [0, 1080]
        elif condition == "D":
            # 집중결핍
            point_x, point_y = gen_no_interest_xy(self.width, self.height, self.nframes)
            errx = gen_error(self.nframes, mag=3, max_dt = 50)
            erry = gen_error(self.nframes, mag=3, max_dt = 50)
            self.gaze_x = np.clip(point_x + errx, 0, self.width) # [0, 1920]
            self.gaze_y = np.clip(point_y + erry, 0, self.height) # [0, 1080]
        elif condition == "A":
            # 집중하락
            point_x, point_y = gen_no_interest_xy(self.width, self.height, self.nframes)
            errx = gen_error(self.nframes, mag=1, max_dt = 150)
            erry = gen_error(self.nframes, mag=3, max_dt = 150)
            self.gaze_x = np.clip(point_x + errx, 0, self.width) # [0, 1920]
            self.gaze_y = np.clip(point_y + erry, 0, self.height) # [0, 1080]
        elif condition == "N":
            point_x, point_y = gen_no_interest_xy(self.width, self.height, self.nframes)
            errx = gen_error(self.nframes, mag=10, max_dt = 50)
            erry = gen_error(self.nframes, mag=10, max_dt = 50)
            self.gaze_x = np.clip(point_x + errx, 0, self.width) # [0, 1920]
            self.gaze_y = np.clip(point_y + erry, 0, self.height) # [0, 1080]

        self.point = {"time":self.timestamp, 'point_x':point_x.astype(int), 'point_y':point_y.astype(int)}
        self.convert_gaze_to_angle() # also need display pose 

    def save_all(self):
        datasets = ['point', 'head', 'cam', 'gaze', 'd_cam', 'd_disp']
        field = "all"
        for dd in datasets:
            fn = f"{self.wdir}{self.display}_{self.posture}_{self.condition}_{self.orientation}_{dd}.csv"
            self._save_csv(fn, dd, field)
        
    def _save_csv(self, fn, ds, fields):
        dataset = getattr(self, ds)
        if fields == 'all':
            fields = list(dataset.keys())
        header = f"[{ds}] date, "
        fmt = ""
        for ff in fields:
            header = header + ff + ", "
            if ff == "time":
                fmt = fmt + "%.24s, "
            else:
                fmt = fmt + "%.6s, "
        header = header[:-2] # remove trailing ','
        fmt = fmt[:-2] # remove trailing ','
        np.savetxt(fn, np.transpose([dataset[ff] for ff in fields]), 
                    header=header, 
                    #delimiter=",", 
                    fmt=fmt)
                    
    def convert_gaze_to_angle(self):
        """
        assume roll == 0 (눈과 카메라가 수평)
        """
        
        xcen = 0.5 # position of eyes w.r.t. the display
        ycen = 0.5
        xx = (self.gaze_x/self.width - xcen) * self.disp_size_x
        yy = (self.gaze_y/self.height - ycen) * self.disp_size_y
        
        roll = np.zeros(self.nframes)
        pitch = np.rad2deg(np.arctan(xx/self.d_disp['d_disp'])) # incorrect!
        yaw = np.rad2deg(np.arctan(yy/self.d_disp['d_disp']))
        
        self.gaze = {"time":self.timestamp, "roll":roll, "pitch":pitch, "yaw":yaw}
        