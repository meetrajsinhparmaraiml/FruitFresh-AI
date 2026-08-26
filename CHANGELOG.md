# Changelog

## [Unreleased]
- **Task 001**: Repo Inspection & Setup Verification completed.
- **Task 002**: Normalized documentation to support only Apple and Banana. Explicitly documented non-claims regarding food safety, internal rot, and pathogens. Removed references to Guava and Mosambi.
- **Task 004**: Initialized React+Vite frontend, built camera screen with environment facingMode, fallback states, target box UI, and disclaimer.
- **Task 005**: Created Detector adapter with YOLO wrapper, environment config, explicit Apple/Banana class mapping, confidence threshold filtering, and passing pytest cases.
- **Task 006**: Defined overlay states, created `DetectionOverlay` component, integrated into `CameraScreen`, and added unit tests for overlay states.
- **Task 007**: Created `FrameSampler` (configurable FPS gate), `StabilityTracker` (IoU + displacement + class-consistency), and 7 passing pytest cases covering jitter, class-flipping, missing frames, multiple fruits, and insufficient buffer.
- **Task 008**: Implemented `QualityGate` with blur (Laplacian variance), brightness (min/max), size (area ratio), and edge-clip (occlusion) checks. All thresholds config-driven. 6 pytest cases all passing.
- **Task 009**: Implemented `FrameBuffer` (bounded FIFO with weighted composite scoring), `AutoCaptureController` (6-state machine: SEARCHING→DETECTED→TRACKING→STABLE→BEST_FRAME_SELECTED→CAPTURED). 8 pytest cases all passing.
- **Task 010**: Implemented CV baseline freshness engine (`freshness.py`) with fruit-specific apple/banana analysis, issue taxonomy (`issues.py`) with 8 issue types and severity mapping. 10 pytest cases all passing.
- **Task 011**: Implemented deterministic `scoring.py` (raw→int 1-10, product labels, uncertainty gate), `templates.py` (template-driven analysis text from structured issues). 20 pytest cases all passing. No hallucination path exists when evidence is insufficient.
- **Task 012**: Implemented `POST/GET /api/v1/scans` endpoints, SQLAlchemy ORM (scans, scan_results, detected_issues tables), SQLite persistence, `app/main.py`. 9 integration tests all passing. No filesystem paths exposed in responses.
