from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from src.detector import ObjectDetector
import shutil

app = FastAPI()
detector = ObjectDetector()


@app.get("/")
async def root():
    return {"message": "Welcome to the ML API Pipeline"}


@app.post("/detect/")
async def detect(file: UploadFile = File(...)):
    with open(f"temp_{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # annotated_image_path = detector.detect_objects(f"/tmp/temp_{file.filename}")
    annotated_image_path = detector.detect_objects(f"temp_{file.filename}")
    return FileResponse(annotated_image_path)
