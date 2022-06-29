import numpy as np

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

class Eye():
    def __init__(self, anno):
        self.anno = anno
        for ano in anno:
            try:
                setattr(self, ano['label'], ano)
            except:
                print("what is this annotation?", ano)
                
        #$self.l_iris.update({"rotate":12.4})
        #self.r_iris.update({"rotate":21.1})
                
    def __repr__(self):
        print(self.anno)
        return ""