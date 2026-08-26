import time
from app.core.config import settings

class FrameSampler:
    def __init__(self):
        self.target_fps = settings.SAMPLING_FPS
        self.min_interval = 1.0 / self.target_fps if self.target_fps > 0 else 0
        self.last_capture_time = 0.0

    def should_sample(self) -> bool:
        current_time = time.time()
        if current_time - self.last_capture_time >= self.min_interval:
            self.last_capture_time = current_time
            return True
        return False
