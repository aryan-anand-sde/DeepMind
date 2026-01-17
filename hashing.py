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

def normalize_image(image_input):
    if isinstance(image_input,str):
        img = Image.open(image_input)
    else:
        img = image_input
    #Convert to RGB(standardize)
    if img.mode!='RGB':
        img = img.convert('RGB')

    #Remove letterboxing
    img = remove_black_bars(img)

    #Histogram equalization(Lighting fix)
    try:
        img = ImageOps.equalize(img)
    except Exception:
        pass
    return img
