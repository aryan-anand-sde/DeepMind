import os
import uuid
import shutil
import traceback
from fastapi import Request
from backend.hashing import process_image
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI,UploadFile,File,Form
from backend.detector import is_Duplicate,check_similarity
from fastapi.responses import JSONResponse, FileResponse

app=FastAPI()
os.makedirs("uploads",exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile=File(...)):
    """
    Upload a single image.
    Pointer-Based DB Logic: If duplicate, delete new file and point to existing one.
    """
    unique_filename=f"{uuid.uuid4()}_{file.filename}"
    temp_path=f"uploads/{unique_filename}"

    with open(temp_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    is_dup, original_path,reason=is_duplicate(temp_path)

    if is_dup:
        if not os.path.exists(original_path):
            print(f"Self-Healing:Original file{original_path} was missing. Restoring with new upload.")
            shutil.move(temp_path,original_path)
        else:
            try:
                os.remove(temp_path)
                print(f"Storage Optimization:Deleted{temp_path},pointing to {original_path}")
            except Exception as e:
                print(f"Error deleting duplicate:{e}")

        original_path=original_path.replace("\\","/")

        return {
            "status": "duplicate",
            "original_image": original_path,
            "message": "Duplicate detected. Storage optimized (pointer created).",
            "storage_saved": True,
            "reason": reason
        }
    else:
        return {"status":"unique","message":"Image stored","image_path":temp_path}
    


@app.exception_handler(Exception)
async def global_exception_handler(request:Request, exc:Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"message":str(exc),"trace":traceback.format_exc()}
    )


@app.post("/compare")
async def compare_images(file1:UploadFile=File(...),file2:UploadFile=File(...)):
    """ Compare two images for similarity"""

    try:
        path1=f"uploads/{uuid.uuid4()}_{file1.filename}"
        path2=f"uploads/{uuid.uuid4()}_{file2.filename}"

        with open(path1,"wb") as buffer:
            shutil.copyfileobj(file1.file,buffer)
        with open(path2, "wb") as buffer:
            shutil.copyfileobj(file2.file,buffer)

        confidenceScore, hashDistances, isSimilar, featureScore, clipScore=check_similarity(path1,path2)

        return{
            "image1":file1.filename,
            "image2":file2.filename,
            "confidenceScore":float(confidenceScore),
            "clipScore":float(clipScore),
            "similarityScore":float(clipScore),
            "hashDistances":hashDistances,
            "phashDistance":int(hashDistances['phash']),
            "featueScore":int(featureScore),
            "isSimilar":bool(isSimilar),
            "paths":[path1,path2]

        }
    except Exception as e:
        traceback.print_exc()
        raise e
    


@app.post("/test_robustness")
async def test_robustness(
    file:UploadFile=File(...),
    crop:str=Form(None),
    scale_width:int=Form(None),
    scale_height:int=Form(None),
    filter_type:str=Form(None)
):
    """
    Test robustness: Upload image,apply transformations, then check similarity between original and modified.
    """

    try:
        original_path=f"uploads/{uuid.uuid4()}_original_{file.filename}"
        with open(original_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        crop_coords=None
        if crop:
            crop_coords=tuple(map(int, crop.split(',')))

        scale_size=(scale_width, scale_height) if (scale_width and scale_height) else None

        modified_path=process_image(
            original_path,
            crop_coords=crop_coords,
            scale_size=scale_size,
            filter_type=filter_type
        )

        confidence_score, hash_distances, is_similar, feature_score, clip_score= check_similarity(original_path, modified_path)

        return{
            "status":"success",
            "original_path":original_path,
            "modified_path":modified_path,
            "similarity_results":{
                "confidence_score":float(confidence_score),
                "clip_score":float(clip_score),
                "hash_distances":hash_distances,
                "phash_distance":int(hash_distances['phash']),
                "feature_score":int(feature_score),
                "is_similar":bool(is_similar)

            },
            "parametres":{
                "crop":str(crop_coords) if crop_coords else None,
                "scale":str(scale_size) if scale_size else None,
                "filter":filter_type
            }
        }
    except Exception as e:
        traceback.print_exc()
        raise e
    


@app.get("/image/{image_id}")
async def get_image(image_id:str):
    """Retrieve a processed image"""

    if ".." in image_id or "/" in image_id or "\\" in image_id:
        return {"error":"Invalid filename"}
    
    file_path_processed=f"processed/{image_id}"
    file_path_upload= f"uploads/{image_id}"

    if os.path.exists(file_path_processed):
        return FileResponse(file_path_processed)
    if os.path.exists(file_path_upload):
        return FileResponse(file_path_upload)
    
    return {"error":"Image not found"}




@app.get("/files/{folder}/{filename}")
async def get_file(folder:str, filename:str):
    if folder not in ["uploads","processed"]:
        return {"error":"Access denied"}
    
    path=f"{folder}/{filename}"
    if os.path.exists(path):
        return FileResponse(path)
    
    return {"error":"File not found"}

app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads")



from detector import is_duplicate, check_similarity, get_cluster



@app.get("/lineage/{filename}")
async def get_lineage(filename:str):
    """Get all images related to the given filename(Cluster)"""

    path= f"uploads/{filename}"
    if not os.path.exists(path):
        path=f"processed/{filename}"

    
    if not os.path.exists(path):

        if os.path.exists(filename):
            path=filename
        
        else:
            return{"status":"error", "message":"File not found"}
        
    
    cluster=get_cluster(path)

    return {"status":"success", "cluster":cluster}


from benchmark import run_benchmark

@app.post("/benchmark")
async def benchmark_endpoint(folder_path: str = Form("benchmark_dataset")):
    """
    Run benchmark on the specified folder.
    """
    try:
        # Validate path
        real_path = folder_path
        if not os.path.isabs(folder_path):
             real_path = os.path.join(os.getcwd(), folder_path)
             
        if not os.path.exists(real_path):
             # Try default if user typed something short
             if os.path.exists(os.path.join("..", folder_path)):
                 real_path = os.path.join("..", folder_path)
             elif os.path.exists(os.path.join("backend", folder_path)):
                 real_path = os.path.join("backend", folder_path)
                 
        if not os.path.exists(real_path):
            return JSONResponse(status_code=400, content={"message": f"Folder not found: {folder_path}"})

        results = run_benchmark(real_path)
        
        if "error" in results:
             return JSONResponse(status_code=400, content={"message": results["error"]})
             
        return {"status": "success", "results": results}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

app.mount("/",StaticFiles(directory="../frontend", html=True),name="frontend")
