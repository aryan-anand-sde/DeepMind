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

def is_duplicate(image_path):
    """
    Check if image is a duplicate.
    Run FULL analysis (Hashes + Embeddings) to return comprehensive stats.
    """
    # Register ID for current image
    curr_id = len(path_to_id)
    path_to_id[image_path] = curr_id
    
    # 1. Check Hashes (Fast filter)
    p_hash = get_phash(image_path)
    d_hash = get_dhash(image_path)
    w_hash = get_whash(image_path)
    
    hash_match = None
    min_hash_dist = float('inf')
    
    # Scan Hash DB
    for entry in hash_db:
        p_dist = abs(entry['phash'] - p_hash)
        d_dist = abs(entry['dhash'] - d_hash)
        w_dist = abs(entry['whash'] - w_hash)
        
        # Check if any threshold is met
        if (p_dist < PHASH_THRESHOLD or d_dist < DHASH_THRESHOLD or w_dist < WHASH_THRESHOLD):
            # We found a candidate.
            # Heuristic: sum of distances as a tie-breaker
            total_dist = p_dist + d_dist + w_dist
            if total_dist < min_hash_dist:
                min_hash_dist = total_dist
                hash_match = entry['path']

    # 2. Check Embedding (Cluster Search)
    emb = get_robust_embedding(image_path)
    scores, matches = search(emb, k=5)
    
    vector_match = None
    best_conf_score = -1
    
    for i in range(len(matches)):
        clip_score = float(scores[i])
        candidate_path = matches[i]
        
        if clip_score < 0.70: continue
            
        feature_matches = match_features(image_path, candidate_path)
        conf_score = calculate_confidence(clip_score, feature_matches)
        
        if conf_score > CONFIDENCE_THRESHOLD:
            if conf_score > best_conf_score:
                best_conf_score = conf_score
                vector_match = candidate_path

    # 3. Determine Final Verdict
    # Hash match is "Stronger/Faster", but Vector match might be "More Meaningful"
    # If both exist, we prioritize the one with higher confidence if we checked it, 
    # but since hash match skips ORB usually, let's prioritize Hash if it's very close.
    
    final_match = hash_match if hash_match else vector_match
    
    if final_match:
        # Link in Union-Find
        uf.union(curr_id, path_to_id[final_match])
        
        # 4. Generate FULL Report for the User
        # We run check_similarity explicitly to get every single metric
        conf, hashes, is_sim, feats, clip = check_similarity(image_path, final_match)
        
        # F1 Score approximation
        # Precision/Recall are binary here (Match vs No Match), so we just use Confidence as the score
        f1_score = conf 
        
        reason = {
            'method': 'Comprehensive Analysis' if (hash_match and vector_match) else ('Perceptual Hash' if hash_match else 'Semantic Search'),
            'score': f"{f1_score:.2f}",
            'detail': f"""
                <strong>F1 / Confidence Score:</strong> {f1_score:.2f}<br>
                <strong>CLIP Semantic Score:</strong> {clip:.2f}<br>
                <strong>ORB Feature Matches:</strong> {feats}<br>
                <hr style="margin: 5px 0; opacity: 0.3">
                <strong>pHash Dist:</strong> {hashes['phash']} (Thresh: {PHASH_THRESHOLD})<br>
                <strong>dHash Dist:</strong> {hashes['dhash']} (Thresh: {DHASH_THRESHOLD})<br>
                <strong>wHash Dist:</strong> {hashes['whash']} (Thresh: {WHASH_THRESHOLD})
            """,
            'sub_scores': '' # Handled in detail
        }
        
        return True, final_match, reason
    # Save to DB if unique
    add_vector(emb, image_path)
    hash_db.append({
        'phash': p_hash,
        'dhash': d_hash,
        'whash': w_hash,
        'path': image_path
    })
    
    return False, None, None

def add_image(image_path):
    
    p_hash = get_phash(image_path)
    d_hash = get_dhash(image_path)
    w_hash = get_whash(image_path)
    
    emb = get_embedding(image_path)
    add_vector(emb, image_path)
    
    hash_db.append({
        'phash': p_hash,
        'dhash': d_hash,
        'whash': w_hash,
        'path': image_path
    })


def check_similarity(image_path1, image_path2):
    """
    Compare two images and return similarity metrics
    Returns: (confidence_score, hash_distances, is_similar, feature_score, clip_score)
    """
    # 1. Calculate Bag of Hashes
    p1 = get_phash(image_path1)
    d1 = get_dhash(image_path1)
    w1 = get_whash(image_path1)
    
    p2 = get_phash(image_path2)
    d2 = get_dhash(image_path2)
    w2 = get_whash(image_path2)
    
    hash_distances = {
        "phash": abs(p1 - p2),
        "dhash": abs(d1 - d2),
        "whash": abs(w1 - w2)
    }
    
    # 2. Get embeddings & CLIP Score
    emb1 = get_embedding(image_path1)
    emb2 = get_embedding(image_path2)
    
    import numpy as np
    clip_score = np.dot(emb1, emb2.T)[0][0]
    
    # 3. Feature Matching (ORB)
    feature_score = match_features(image_path1, image_path2)
    
    # 4. Calculate Confidence Score
    confidence_score = calculate_confidence(clip_score, feature_score)
    
    # 5. Determine if similar
    # Match if any hash is close OR confidence score is high
    is_similar = (
        (hash_distances['phash'] < PHASH_THRESHOLD) or 
        (hash_distances['dhash'] < DHASH_THRESHOLD) or 
        (hash_distances['whash'] < WHASH_THRESHOLD) or 
        (confidence_score > CONFIDENCE_THRESHOLD)
    )

    return confidence_score, hash_distances, is_similar, feature_score, clip_score
