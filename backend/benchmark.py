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
    

    
