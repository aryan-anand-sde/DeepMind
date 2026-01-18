import cv2
from hashing import get_phash, get_dhash, get_whash
from model import get_embedding, get_robust_embedding
from vectorDB import search, add_vector

PHASH_THRESHOLD = 10
DHASH_THRESHOLD = 10
WHASH_THRESHOLD = 12

# Confidence Thresholds
CONFIDENCE_THRESHOLD = 0.85  # Threshold for the final weighted score
CLIP_WEIGHT = 0.6
ORB_WEIGHT = 0.4
MAX_ORB_MATCHES = 50  # Value to normalize ORB score (matches/50 capped at 1.0)


hash_db = []

class UnionFind:
    def __init__(self):
        self.parent = {}
    
    def find(self, i):
        if i not in self.parent:
            self.parent[i] = i
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    
    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j

uf = UnionFind()
path_to_id = {}

def get_cluster(image_path):
    """Get all images in the same cluster/lineage as image_path"""
    if image_path not in path_to_id:
        return []
    
    target_root = uf.find(path_to_id[image_path])
    cluster = []
    
    for path, id_ in path_to_id.items():
        if uf.find(id_) == target_root:
            cluster.append(path)
            
    return cluster

def calculate_confidence(clip_score, orb_matches):

    # Normalize ORB matches (0 to 1)
    norm_orb = min(orb_matches / MAX_ORB_MATCHES, 1.0)
    
    # Weighted Sum
    # Ensure clip_score is not negative
    clip_score = max(0, clip_score)
    
    final_score = (CLIP_WEIGHT * clip_score) + (ORB_WEIGHT * norm_orb)
    return final_score