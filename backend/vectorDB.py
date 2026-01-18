import faiss
import numpy as np

dimension = 512
index = faiss.IndexFlatIP(dimension)
image_paths = []

def add_vector(vec, path):
    # Add embedding vector to FAISS index
    if isinstance(vec, np.ndarray):
        vec = vec.astype(np.float32)
    if len(vec.shape) == 1:
        vec = vec.reshape(1, -1)
    index.add(vec)
    image_paths.append(path)

def search(vec, k=5):
    # Search for similar embeddings in FAISS index
    if isinstance(vec, np.ndarray):
        vec = vec.astype(np.float32)
    if len(vec.shape) == 1:
        vec = vec.reshape(1, -1)
    
    if index.ntotal == 0:
        return np.array([]), []
    
    D, I = index.search(vec, min(k, index.ntotal))
    return D[0], [image_paths[i] for i in I[0] if i < len(image_paths)]