import matplotlib.pyplot as plt 
import cv2
import numpy as np
from nia22.eyes import mask_one_eye, Eye

def check_mask(cropped, mask, fn):
    fig,axs = plt.subplots(1,3)
    fig.set_size_inches(12,9)

    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    axs[0].imshow(cropped)
    axs[1].imshow(mask)
    axs[2].imshow(cropped)
    axs[2].imshow(mask, alpha=0.3)

    for ax in axs.ravel():
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    plt.tight_layout()
    plt.savefig(fn, bbox_inches='tight')
    plt.close()

def gen_mask(img, anno, fn, png_dir, label_dir):
    """RITNet mask generation"""
    # temporary version
    eye = Eye(anno["Annotations"]['annotations'])
    if eye._has_eyelid & eye._has_iris:
        # Final version
        cropped, mask = mask_one_eye(img, eye, "r")
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        fn_png = png_dir+fn+"r.png"
        cv2.imwrite(fn_png, cropped)
        check_mask(cropped, mask, fn_png.replace(".png", "_check.png").replace("/images/","/"))
        np.save(label_dir+fn+"r.npy",mask)

        cropped, mask = mask_one_eye(img, eye, "l")
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        fn_png = png_dir+fn+"l.png"
        cv2.imwrite(fn_png, cropped)
        check_mask(cropped, mask, fn_png.replace(".png", "_check.png").replace("/images/","/"))
        np.save(label_dir+fn+"l.npy" ,mask)
                
    else:
        print(fn)
        print("not enough labels. Eyes are closed?")
