# DeepMind Image Similarity Detector

This application detects image duplicates and similarities using Perceptual Hashing and CLIP Embeddings. It is robust to modifications like cropping, scaling, and filtering.

## Project Structure

- `backend/`: FastAPI backend and logic.
- `frontend/`: Modern web interface.

## Setup & Running

1. **Install Dependencies**
   Ensure you have the required Python packages:

   ```bash
   pip install fastapi uvicorn python-multipart pillow imagehash numpy torch open_clip_torch faiss-cpu
   ```

2. **Run the Application**
   Start the server from the backend directory:

   ```bash
   uvicorn backend.app:app --reload
   ```

   _Note: On first run, it will download the CLIP model (approx 600MB)._

3. **Access the UI**
   Open your browser to:
   [http://localhost:8000](http://localhost:8000)

## Features

- **Robustness Test**: Upload an image, apply crop/scale/filters, and verify if the system still recognizes it as similar.
- **Compare Two**: Upload two different images to get similarity metrics.
- **Duplicate Detection**: Check if an uploaded image already exists in the database.
