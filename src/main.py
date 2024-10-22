import os
import cv2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from src.detector import ObjectDetector
import shutil

app = FastAPI()
detector = ObjectDetector()

os.makedirs("temp/images/uploads", exist_ok=True)
os.makedirs("temp/images/annotated", exist_ok=True)
os.makedirs("temp/videos/uploads", exist_ok=True)
os.makedirs("temp/videos/annotated", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to the Person Detection API"}


@app.post("/detect/")
async def detect(file: UploadFile = File(...)):
    file_path = f"temp/images/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    annotated_image_path = detector.detect_images(file_path)
    return FileResponse(annotated_image_path)


@app.post("/detect-video/")
async def detect_video(file: UploadFile = File(...)):
    file_path = f"temp/videos/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    frames = detector.detect_video(file_path)

    height, width, _ = frames[0].shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video_path = f"temp/videos/annotated/{file.filename}"
    out = cv2.VideoWriter(out_video_path, fourcc, 20.0, (width, height))

    for frame in frames:
        out.write(frame)
    out.release()

    return FileResponse(out_video_path)