import os
import subprocess
import cv2
import shutil
import uuid
import time
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from src.detector import ObjectDetector


def cleanup_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

os.makedirs("temp/images/uploads", exist_ok=True)
os.makedirs("temp/images/annotated", exist_ok=True)
os.makedirs("temp/videos/uploads", exist_ok=True)
os.makedirs("temp/videos/annotated", exist_ok=True)

app = FastAPI()
detector = ObjectDetector()

app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("src/static/index.html") as f:
        return f.read()


@app.post("/detect/")
async def detect(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_path = f"temp/images/uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prediction_start_time = time.time()
    annotated_image_path = detector.detect_images(file_path)
    prediction_time = time.time() - prediction_start_time

    background_tasks.add_task(cleanup_file, file_path)
    background_tasks.add_task(cleanup_file, annotated_image_path)
    
    return FileResponse(
        annotated_image_path,
        media_type='image/jpeg',
        filename=annotated_image_path,
        headers={"X-Prediction-Time": str(prediction_time)}
    )


@app.post("/detect-video/")
async def detect_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"temp/images/uploads/{file_name}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prediction_start_time = time.time()
    frames = detector.detect_video(file_path)
    prediction_time = time.time() - prediction_start_time

    height, width, _ = frames[0].shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video_path = f"temp/videos/annotated/{file_name}"
    out_video_path2 = f"temp/videos/annotated/new_{file_name}"
    out = cv2.VideoWriter(out_video_path, fourcc, 20.0, (width, height))

    for frame in frames:
        out.write(frame)
    out.release()
    
    subprocess.run([
        'ffmpeg', '-i', out_video_path,
        '-vcodec', 'libx264', '-acodec', 'aac', '-movflags', '+faststart',
        '-strict', 'experimental', out_video_path2,
        '-y'  # Overwrite output file if it exists
    ])

    background_tasks.add_task(cleanup_file, file_path)
    background_tasks.add_task(cleanup_file, out_video_path)
    background_tasks.add_task(cleanup_file, out_video_path2)

    return FileResponse(
        out_video_path,
        media_type='video/mp4',
        filename=out_video_path2,
        headers={"X-Prediction-Time": str(prediction_time)}
    )