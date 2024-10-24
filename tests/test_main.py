from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ML API Pipeline"}

def test_detect_image():
    with open("test_inputs/sample_image.png", "rb") as image_file:
        response = client.post("/detect/", files={"file": ("sample_image.png", image_file, "image/png")})
    assert response.status_code == 200

def test_detect_video():
    with open("test_inputs/sample_video.mp4", "rb") as video_file:
        response = client.post("/detect-video/", files={"file": ("sample_video.mp4", video_file, "video/mp4")})
    assert response.status_code == 200