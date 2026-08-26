from collections import deque
from typing import List, Optional
from app.core.config import settings
from app.schemas.detector import DetectionResult

def calculate_iou(boxA: List[float], boxB: List[float]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def calculate_displacement(boxA: List[float], boxB: List[float]) -> float:
    centerA_x = (boxA[0] + boxA[2]) / 2.0
    centerA_y = (boxA[1] + boxA[3]) / 2.0
    
    centerB_x = (boxB[0] + boxB[2]) / 2.0
    centerB_y = (boxB[1] + boxB[3]) / 2.0
    
    return ((centerA_x - centerB_x) ** 2 + (centerA_y - centerB_y) ** 2) ** 0.5

class StabilityTracker:
    def __init__(self):
        self.buffer = deque(maxlen=settings.STABILITY_BUFFER_SIZE)
        self.iou_threshold = settings.STABILITY_IOU_THRESHOLD
        self.max_displacement = settings.STABILITY_MAX_DISPLACEMENT
        self.required_frames = settings.STABILITY_REQUIRED_FRAMES

    def add_frame(self, detections: List[DetectionResult]):
        if len(detections) == 1:
            self.buffer.append(detections[0])
        else:
            self.buffer.append(None)

    def is_stable(self) -> bool:
        if len(self.buffer) < self.required_frames:
            return False

        recent_frames = list(self.buffer)[-self.required_frames:]
        
        if any(det is None for det in recent_frames):
            return False
            
        base_det = recent_frames[0]
        
        for det in recent_frames[1:]:
            if det.fruit_type != base_det.fruit_type:
                return False
                
            iou = calculate_iou(base_det.bbox, det.bbox)
            if iou < self.iou_threshold:
                return False
                
            disp = calculate_displacement(base_det.bbox, det.bbox)
            if disp > self.max_displacement:
                return False
                
            base_det = det
            
        return True
