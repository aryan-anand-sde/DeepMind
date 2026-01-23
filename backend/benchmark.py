import time
import os
import glob
import imagehash
from PIL import Image
from hashing import get_phash
from model import get_robust_embedding
from detector import check_similarity, calculate_confidence, match_features
import numpy as np

class LocalBenchmarkDB:
    def __init__(self):
        self.hashes = []
        self.vectors = []
        self.paths = []

    def add(self, p_hash, vector, path):
        self.hashes.append(p_hash)
        self.vectors.append(vector)
        self.paths.append(path)

    def search(self, p_hash, vector, path):
        # 1. Fast Hash Check
        for i, h in enumerate(self.hashes):
            if abs(h - p_hash) < 10:
                return True, self.paths[i]
        
        # 2. Vector Check (Linear scan for benchmark accuracy)
        best_score = -1
        best_match = None
        
        if len(self.vectors) > 0:
            
            # Simple dot product against all
            scores = np.dot(self.vectors, vector.T).flatten()
            
            # Find candidates > 0.70
            candidates_idx = np.where(scores > 0.70)[0]
            
            for idx in candidates_idx:
                candidate_path = self.paths[idx]
                clip_score = scores[idx]
                
                # Check ORB
                orb_matches = match_features(path, candidate_path)
                conf = calculate_confidence(clip_score, orb_matches)
                
                if conf > 0.85:
                    if conf > best_score:
                        best_score = conf
                        best_match = candidate_path
                        
        if best_match:
            return True, best_match
            
        return False, None

def run_benchmark(dataset_path):
    # Extensions to look for
    exts = ('/*.jpg', '/*.jpeg', '/*.png')
    images = []
    for ext in exts:
        images.extend(glob.glob(dataset_path + ext))
    
    # Sort to ensure consistent order (optional)
    images.sort()
    
    if not images:
        return {"error": "No images found in dataset path"}

    # Limit to reasonable number for demo speed
    images = images[:50] 

    metrics = []

    # --- Method 1: Pixel Matching (Baseline) ---
    start_time = time.time()
    matches_pixel = 0
    seen_pixels = set()
    
    for img_path in images:
        try:
            with open(img_path, "rb") as f:
                content = f.read()
                if content in seen_pixels:
                    matches_pixel += 1
                else:
                    seen_pixels.add(content)
        except: pass
    
    time_pixel = time.time() - start_time

# --- Method 2: Perceptual Hash (Standard) ---
    start_time = time.time()
    matches_phash = 0
    seen_hashes = []
    
    for img_path in images:
        try:
            h = get_phash(img_path)
            is_dup = False
            for existing_h in seen_hashes:
                if abs(h - existing_h) < 10: # Threshold
                    is_dup = True
                    break
            
            if is_dup:
                matches_phash += 1
            else:
                seen_hashes.append(h)
        except Exception as e:
            print(f"Error in pHash for {img_path}: {e}")

    time_phash = time.time() - start_time

  # --- Method 3: Our Model (CLIP + ORB) ---
    start_time = time.time()
    matches_our = 0
    db = LocalBenchmarkDB()
    
    # Pre-load/embed first (Indexing phase) 
    # Actually, in a real stream, we index one by one.
    # We will simulate the "Check then Add" flow.
    
    for img_path in images:
        try:
            p_hash = get_phash(img_path)
            vector = get_robust_embedding(img_path) # Depending on model.py impl
            
            is_dup, match_path = db.search(p_hash, vector, img_path)
            
            if is_dup:
                matches_our += 1
            else:
                db.add(p_hash, vector, img_path)
        except Exception as e:
             print(f"Error in OurModel for {img_path}: {e}")

    time_our = time.time() - start_time
    
    
    
    total = len(images)
    
    return [
        {
            "method": "Pixel Matching",
            "description": "Baseline (Exact Identity)",
            "matches_found": matches_pixel,
            "speed_sec": round(time_pixel, 3),
            "speed_per_100": round((time_pixel / total) * 100, 3) if total else 0
        },
        {
            "method": "Perceptual Hash",
            "description": "Industry Standard (pHash)",
            "matches_found": matches_phash,
            "speed_sec": round(time_phash, 3),
            "speed_per_100": round((time_phash / total) * 100, 3) if total else 0
        },
        {
            "method": "DeepMind Detector",
            "description": "Our Model (CLIP + ORB)",
            "matches_found": matches_our,
            "speed_sec": round(time_our, 3),
            "speed_per_100": round((time_our / total) * 100, 3) if total else 0
        }
    ]






