import numpy as np

class Scenario():
    def __init__(self):
        self.scenarios={'F':[self.s0,self.s1],
                        'S':[self.s4],
                        'D':[self.s5,self.s6],
                        'A':[self.s4],
                        'N':[self.s2,self.s3]}
        
    def set_points(self, nframes):
        self.nframes = nframes
        self.x0 = np.linspace(0, 1920, self.nframes+2)[1:-1]
        self.y0 = np.linspace(0, 1080, self.nframes+2)[1:-1]
        
        self.xround = np.concatenate((self.x0[::2],self.x0[-1::-2]))
        self.yround = np.concatenate((self.y0[::2],self.y0[-1::-2]))

    def xrand(self):
        return np.repeat(480 + 960*np.random.rand(), self.nframes)
        
    def yrand(self):
        return np.repeat(270 + 540*np.random.rand(), self.nframes)

        
    def xrand2(self):
        return np.repeat(480*np.random.rand() + \
                         int(np.random.rand())*480*3,
                         self.nframes)
    def yrand2(self):
        return np.repeat(270*np.random.rand() + \
                         int(np.random.rand())*270*3,
                         self.nframes)

    def s0(self): 
        return [self.x0,self.y0]
    def s1(self): 
        return [np.repeat(30, self.nframes), self.y0]
    def s2(self): 
        return [self.xround, self.y0]
    def s3(self): 
        return[self.x0, self.yround]
    def s4(self):
        return [self.xrand(), self.yrand()]

    def s5(self): 
        return [np.concatenate((self.xrand()[::5],self.xrand2()[::5],
                          self.xrand()[::5],self.xrand2()[::5],
                          self.xrand()[::5])), self.yrand2()]
    def s6(self):
        return [np.concatenate((self.yrand()[::5],self.yrand2()[::5],
                          self.yrand()[::5],self.yrand2()[::5],
                          self.yrand()[::5])), self.xrand2()]