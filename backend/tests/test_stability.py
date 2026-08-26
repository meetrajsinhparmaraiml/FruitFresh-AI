import pytest
from app.cv.stability import StabilityTracker
from app.schemas.detector import DetectionResult
from app.core.config import settings

@pytest.fixture
def tracker():
    settings.STABILITY_REQUIRED_FRAMES = 3
    settings.STABILITY_IOU_THRESHOLD = 0.8
    settings.STABILITY_MAX_DISPLACEMENT = 10.0
    return StabilityTracker()

def test_stable_trajectory(tracker):
    for _ in range(3):
        tracker.add_frame([
            DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])
        ])
    assert tracker.is_stable() is True

def test_jittery_trajectory_iou_failure(tracker):
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[50, 50, 140, 140])])
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False

def test_jittery_trajectory_displacement_failure(tracker):
    tracker.max_displacement = 1.0 
    tracker.iou_threshold = 0.0 
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[15, 15, 105, 105])]) 
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False

def test_class_flipping(tracker):
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([DetectionResult(fruit_type="banana", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False

def test_missing_frames(tracker):
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([]) 
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False

def test_multiple_fruits_is_unstable(tracker):
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    tracker.add_frame([
        DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100]),
        DetectionResult(fruit_type="banana", detection_confidence=0.9, bbox=[200, 200, 300, 300])
    ])
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False

def test_not_enough_frames(tracker):
    tracker.add_frame([DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=[10, 10, 100, 100])])
    assert tracker.is_stable() is False
