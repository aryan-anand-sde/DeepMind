import os
import uuid
import imagehash
from PIL import Image,ImageFilter,ImageEnhance,ImageOps

def remove_black_bars(img,threshold=15):
    grayscale = img.convert("L")  
    grayscale = grayscale.point(lambda x: 0 if x < threshold else 255)
    bbox = grayscale.getbbox()
    # get bbox returns the actual image content
    if bbox:
        return img.crop(bbox)
    return img
