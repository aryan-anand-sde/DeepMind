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

def get_phash(image_path):
    img = normalize_image(image_path)
    return imagehash.phash(img)

def get_ahash(image_path):
    img = normalize_image(image_path)
    return imagehash.average_hash(img)

def get_dhash(image_path):
    img = normalize_image(image_path)
    return imagehash.dhash(img)
def get_five_crops(img):
    #generate 5 crops for robust embedding
    width,height = img.size
    crop_size = min(width,height)//2

    #defining boxes
    center_x,center_y = width // 2,height //2
    half_crop = crop_size // 2

    crops = [
        # Center
        img.crop((center_x - half_crop, center_y - half_crop, center_x + half_crop, center_y + half_crop)),
        # Top-Left
        img.crop((0, 0, crop_size, crop_size)),
        # Top-Right
        img.crop((width - crop_size, 0, width, crop_size)),
        # Bottom-Left
        img.crop((0, height - crop_size, crop_size, height)),
        # Bottom-Right
        img.crop((width - crop_size, height - crop_size, width, height))
    ]
    return crops