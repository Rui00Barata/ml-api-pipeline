from ultralytics import YOLO
import cv2


class ObjectDetector:
    def __init__(self, model_path="yolov8l.pt"):
        self.model = YOLO(model_path)

    def detect_images(self, image_path):
        results = self.model(image_path)[0]  # Get the first result
        image = cv2.imread(image_path)

        # Iterate over detections and draw bounding boxes for persons (class 0)
        for box in results.boxes:
            if int(box.cls) == 0:  # Check if the class is 'person'
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
                cv2.rectangle(
                    image, (x1, y1), (x2, y2), (255, 0, 0), 2
                )  # Draw rectangle

        annotated_image_path = image_path.replace("uploads", "annotated")
        cv2.imwrite(annotated_image_path, image)
        return annotated_image_path

    def detect_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        output_frames = []

        for _ in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame)[0]

            for box in results.boxes:
                if int(box.cls) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            output_frames.append(frame)

        cap.release()
        return output_frames