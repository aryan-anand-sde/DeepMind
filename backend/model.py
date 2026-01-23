import torch
import open_clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
model = model.to(device)
model.eval()

from backend.hashing import normalize_image, get_five_crops

def get_embedding(image_path):
    # Standard single-pass embedding
    image = preprocess(normalize_image(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy()

def get_robust_embedding(image_path):
    # Embedding with Five-Crop (Center-Crop + 4-Corner-Crop) + Original
    img = normalize_image(image_path)
    crops = get_five_crops(img)
    crops.append(img) # Add original
    
    # Process batch
    images = torch.stack([preprocess(c) for c in crops]).to(device)
    
    with torch.no_grad():
        embeddings = model.encode_image(images)
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        
        avg_embedding = embeddings.mean(dim=0, keepdim=True)
        avg_embedding = avg_embedding / avg_embedding.norm(dim=-1, keepdim=True)
        
    return avg_embedding.cpu().numpy()
