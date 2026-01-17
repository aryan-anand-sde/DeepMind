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

def get_whash(image_path):
    img = normalize_image(image_path)
    return imagehash.whash(img)

def crop_image(img,crop_coords):
    #Crop image with coordinates (left, top, right, bottom)
    #Accepts PIL Image object
    return img.crop(crop_coords)

def scale_image(img,size):
    #Scale image to specified size (width, height)
    #Accepts PIL Image object
    return img.resize(size,Image.Resampling.LANCZOS)

def apply_filter(img, filter_type):

    #Apply various filters to image
    #Supported filters: blur, sharpen, edge, smooth, grayscale, sepia, brightness, contrast
    #Accepts PIL Image object
    
    if filter_type == 'blur':
        return img.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == 'sharpen':
        return img.filter(ImageFilter.SHARPEN)
    elif filter_type == 'edge':
        return img.filter(ImageFilter.FIND_EDGES)
    elif filter_type == 'smooth':
        return img.filter(ImageFilter.SMOOTH_MORE)
    elif filter_type == 'grayscale':
        return img.convert('L')
    elif filter_type == 'sepia':
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = img.load()
        width, height = img.size
        # Note: Iterate carefully or use matrix transform for speed, but this works for now
        # A matrix approach is much faster:
        # matrix = ( 0.393, 0.769, 0.189, 0,
        #            0.349, 0.686, 0.168, 0,
        #            0.272, 0.534, 0.131, 0 )
        # return img.convert("RGB", matrix) 
        # But keeping original logic behavior for now
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y][:3]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
        return img
    elif filter_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.3)
    elif filter_type == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.5)
    
    return img
    
def process_image(image_path, crop_coords=None, scale_size=None, filter_type=None):
    """
    Process image with multiple operations (crop, scale, filter)
    """
    img = Image.open(image_path)
    
    if crop_coords:
        img = crop_image(img, crop_coords)
    
    if scale_size:
        img = scale_image(img, scale_size)
        
    if filter_type:
        img = apply_filter(img, filter_type)
    
    # Save processed image
    # Note: For temporary processing, we don't strictly need a persistent 'processed' folder anymore.
    # But to avoid breaking legacy code that expects a path, we will save to 'uploads' or a temp dir.
    # For now, let's just use 'uploads' to keep it simple, or 'temp'.
    
    # Using 'uploads' as the unified storage to avoid confusion
    output_filename = f"temp_{uuid.uuid4()}.jpg"
    output_path = f"uploads/{output_filename}"
    
    # Ensure mode is supported for JPEG (e.g. convert RGBA to RGB)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
        
    img.save(output_path, quality=95)
    
    return output_path   