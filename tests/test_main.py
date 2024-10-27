from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ML API Pipeline" in response.text

def test_detect_image():
    # Use a sample image file for testing
    with open("tests/sample_image.jpg", "rb") as image_file:
        response = client.post("/detect/", files={"file": ("sample_image.jpg", image_file, "image/jpeg")})
    assert response.status_code == 200
    assert "filename" in response.json()

def test_detect_video():
    # Use a sample video file for testing
    with open("tests/sample_video.mp4", "rb") as video_file:
        response = client.post("/detect-video/", files={"file": ("sample_video.mp4", video_file, "video/mp4")})
    assert response.status_code == 200
    assert "filename" in response.json()