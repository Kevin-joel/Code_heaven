from ultralytics import YOLO

# Load a lightweight model
model = YOLO("yolov8n.pt")

# Train on your dataset
model.train(
    data="C:/Users/velev/OneDrive/Desktop/fire_dataset/data.yaml",  # ✅ forward slashes
    epochs=20,
    imgsz=640,
    batch=8,
    name="fire_model_v1"
)
