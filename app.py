import os
import uuid
import shutil
import traceback
from fastapi import Request
from hashing import process_image
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI,UploadFile,File,Form
from detector import is_Duplicate,check_similarity
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

    is_dup, original_path=is_duplicate(temp_path)

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
            "status":"duplicate",
            "original_image":original_path,
            "message":"Duplicate detected.Storage optimized(pointer created).",
            "storage_saved":True
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
    """"""