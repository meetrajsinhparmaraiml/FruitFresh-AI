from pydantic import BaseModel
from typing import List, Literal

class DetectionResult(BaseModel):
    fruit_type: Literal["apple", "banana"]
    detection_confidence: float
    bbox: List[float] # [x1, y1, x2, y2]
