from pathlib import Path

from ultralytics import YOLO


MODEL_PATH = Path("yolo11n.pt")

SUPPORTED_FRUITS = {
    "apple",
    "banana",
}


class FruitDetector:
    """Detect supported fruits using the YOLO model."""

    def __init__(self, model_path: str | Path = MODEL_PATH) -> None:
        self.model = YOLO(str(model_path))

    def detect(self, source: str | Path):
        """Run object detection on an image or video source."""
        return self.model.predict(
            source=str(source),
            verbose=False,
        )