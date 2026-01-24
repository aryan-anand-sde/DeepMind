# DeepMind – Duplicate & Near-Duplicate Image Detection System 🖼️🔍

## Project Overview

Large-scale digital platforms (social media, e-commerce, news portals) face serious challenges with **duplicate and near-duplicate images**. Images are often resized, cropped, compressed, recolored, or slightly edited to bypass traditional duplicate detection systems.

**DeepMind** is an intelligent, production-ready system designed to detect **exact duplicates and visually similar images** even after such transformations. The system combines **perceptual hashing, deep semantic embeddings (CLIP), and local feature matching (ORB)** to achieve both **speed and high accuracy**.

## Key Highlights

- Detects duplicates despite **cropping, resizing, compression, and color changes**
- Combines **hashing + deep learning + feature matching** for robustness
- Optimized for **real-world, large-scale systems**
- Pointer-based storage optimization for duplicates
- Benchmarking against standard techniques

---

## Core Features

### 🧠 Intelligent Duplicate Detection Pipeline

- **Perceptual Hashing** (pHash, dHash, wHash) for fast candidate filtering
- **CLIP-based deep embeddings** for semantic similarity
- **ORB feature matching** for fine-grained visual confirmation
- Weighted confidence scoring using CLIP + ORB

---

### ⚡ Storage Optimization (Pointer-Based Logic)

- If a duplicate image is detected:
  - The newly uploaded file is deleted
  - A pointer/reference to the original image is maintained
- Automatically restores original image if missing (self-healing logic)

---

### 🔍 Image Similarity Comparison

- Compare any two images
- Outputs:
  - Confidence score
  - CLIP similarity score
  - Hash distances (pHash, dHash, wHash)
  - ORB feature match count
  - Final similarity verdict

---

### 🧪 Robustness Testing

- Apply transformations such as:
  - Cropping
  - Scaling
  - Filters (blur, sharpen, grayscale, sepia, brightness, contrast, etc.)
- Evaluate similarity between original and transformed images

---

### 📊 Benchmarking Module

Compares three approaches:

1. **Pixel Matching** (Exact baseline)
2. **Perceptual Hashing (pHash)**
3. **DeepMind Model (CLIP + ORB)**

Metrics:

- Matches found
- Total execution time
- Time per 100 images

---

### 🧬 Image Lineage & Clustering

- Uses **Union-Find (Disjoint Set)** to group related images
- Retrieve all images belonging to the same duplicate cluster

---

### 🌐 Interactive Web Interface

- Upload and detect duplicates in real-time
- Visual feedback for:
  - Duplicate detected
  - Unique image accepted
- Benchmark visualization table
- Modern, responsive UI

---

## System Architecture

### Backend (FastAPI)

- Image upload & processing
- Duplicate detection logic
- Vector search using FAISS
- Benchmark execution
- Image lineage tracking

### Frontend

- HTML, CSS, JavaScript
- Upload & result visualization
- Benchmark comparison dashboard

---

## Detection Pipeline (High-Level Flow)

1. Image Upload
2. Image Normalization
3. Perceptual Hash Generation
4. Hash-Based Candidate Filtering
5. CLIP Embedding Extraction (Five-Crop Robust Embeddings)
6. FAISS Vector Similarity Search
7. ORB Feature Matching
8. Confidence Score Calculation
9. Duplicate / Unique Decision

---

## Tech Stack

### Backend

- FastAPI
- Python

### Deep Learning & CV

- PyTorch
- OpenCLIP (ViT-B-32)
- OpenCV
- imagehash

### Vector Search

- FAISS

### Data Processing

- NumPy
- Pandas
- Scikit-learn

### Frontend

- HTML
- CSS
- JavaScript

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Clone the Repository

```bash
git clone <https://github.com/aryan-anand-sde/DeepMind.git>
cd DeepMind
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Backend Server

```bash
uvicorn app:app --reload
```

Open your browser at: `http://127.0.0.1:8000/`

---

## API Endpoints

### `/upload`

- Upload an image
- Detect duplicate or store as unique

### `/compare`

- Compare two images for similarity

### `/test_robustness`

- Apply transformations and test similarity

### `/benchmark`

- Run benchmarking on a dataset folder

### `/lineage/{filename}`

- Retrieve all images related to a given image

---

## Datasets Used

- **Google Landmarks V2**
- **INRIA Copydays**

---

## Future Improvements

- Distributed FAISS index for large-scale deployment
- GPU-accelerated ORB alternatives
- Incremental learning for new image domains
- Web-based cluster visualization
- Cloud storage integration (S3/GCS)

---

## Team – DEEPMIND

- **[Pragya Bansal](https://github.com/PragyaBansal12)** (Team Leader)
- **[Ankita Patel](https://github.com/Ankitapatel8175841729)**
- **[Aryan Anand](https://github.com/aryan-anand-sde)**
- **[Ashmit Gupta](https://github.com/ashmitgupta11)**

---

## License

This project is developed for academic and research purposes.

---

> **Note:** This system is designed for duplicate detection and content integrity use cases and does not perform facial recognition or identity inference.
