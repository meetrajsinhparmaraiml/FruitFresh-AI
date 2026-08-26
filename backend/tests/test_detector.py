import pytest
import numpy as np
from app.inference.detector import FruitDetector
from app.schemas.detector import DetectionResult
from app.core.config import settings

@pytest.fixture
def detector():
    settings.DETECTOR_MODEL_PATH = "../yolo11n.pt"
    return FruitDetector()

def test_inference_contract_no_fruit(detector):
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    results = detector.detect(dummy_image)
    assert len(results) == 0

def test_unsupported_class_filtering(monkeypatch, detector):
    class MockBox:
        def __init__(self, cls, conf, xyxy):
            self.cls = [cls]
            self.conf = [conf]
            self.xyxy = [xyxy]
    
    class MockResult:
        def __init__(self, boxes):
            self.boxes = boxes

    def mock_call(*args, **kwargs):
        # 49 is orange in COCO
        orange_id = 49
        detector.model.names[orange_id] = "orange"
        box = MockBox(cls=orange_id, conf=0.9, xyxy=[10, 10, 100, 100])
        return [MockResult([box])]
        
    monkeypatch.setattr(detector.model, "__call__", mock_call)
    
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    results = detector.detect(dummy_image)
    
    assert len(results) == 0

def test_confidence_threshold_filtering(monkeypatch, detector):
    call_args = {}
    
    class MockResult:
        def __init__(self):
            self.boxes = []

    def mock_call(self, *args, **kwargs):
        call_args['args'] = args
        call_args['kwargs'] = kwargs
        return [MockResult()]
        
    monkeypatch.setattr("app.inference.detector.YOLO.__call__", mock_call)
    
    dummy_image = np.zeros((10, 10, 3), dtype=np.uint8)
    detector.detect(dummy_image)
    
    assert call_args['kwargs']['conf'] == settings.DETECTOR_CONFIDENCE_THRESHOLD
