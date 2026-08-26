import numpy as np
from ultralytics import YOLO
from app.core.config import settings
from app.schemas.detector import DetectionResult
from typing import List

class FruitDetector:
    def __init__(self):
        self.model = YOLO(settings.DETECTOR_MODEL_PATH)
        self.model.to(settings.DETECTOR_DEVICE)
        self.confidence_threshold = settings.DETECTOR_CONFIDENCE_THRESHOLD
        self.supported_classes = {"apple", "banana"}

    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        # Run inference
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id].lower()
                
                if class_name in self.supported_classes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detections.append(
                        DetectionResult(
                            fruit_type=class_name, # type: ignore
                            detection_confidence=conf,
                            bbox=[x1, y1, x2, y2]
                        )
                    )
        return detections
