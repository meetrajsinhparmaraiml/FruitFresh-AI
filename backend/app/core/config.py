from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DETECTOR_MODEL_PATH: str = "../yolo11n.pt"
    DETECTOR_CONFIDENCE_THRESHOLD: float = 0.5
    DETECTOR_DEVICE: str = "cpu"
    
    SAMPLING_FPS: int = 10
    STABILITY_BUFFER_SIZE: int = 10
    STABILITY_IOU_THRESHOLD: float = 0.85
    STABILITY_MAX_DISPLACEMENT: float = 20.0
    STABILITY_REQUIRED_FRAMES: int = 5

    QUALITY_MIN_BLUR_VARIANCE: float = 80.0
    QUALITY_MIN_BRIGHTNESS: float = 40.0
    QUALITY_MAX_BRIGHTNESS: float = 220.0
    QUALITY_MIN_FRUIT_AREA_RATIO: float = 0.03
    QUALITY_MAX_EDGE_CLIP_RATIO: float = 0.05

    CAPTURE_BUFFER_SIZE: int = 30
    CAPTURE_WEIGHT_SHARPNESS: float = 0.40
    CAPTURE_WEIGHT_AREA: float = 0.30
    CAPTURE_WEIGHT_BRIGHTNESS: float = 0.20
    CAPTURE_WEIGHT_POSITION: float = 0.10
    CAPTURE_MIN_SCORE_THRESHOLD: float = 0.50

    SCORE_UNCERTAINTY_THRESHOLD: float = 0.10
    SCORE_MIN_ISSUES_CONFIDENCE: float = 0.25

    class Config:
        env_file = ".env"

settings = Settings()
