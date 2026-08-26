# FruitFresh AI — Task Status

## Project

FruitFresh AI is a real-time computer-vision fruit freshness estimation system.

Supported fruits:

- Apple
- Banana
- Guava
- Mosambi

Freshness score:

- 1 = very poor visible condition
- 10 = excellent visible condition

The system estimates visible external condition only.

It does NOT scientifically determine food safety.

---

# MVP DEVELOPMENT RULE

Target development time: 8–10 focused hours.

Priority:

- P0 = required for MVP
- P1 = useful if time remains
- P2 = future enhancement

Never allow P1/P2 work to block P0.

Development workflow:

READ
→ PLAN
→ IMPLEMENT
→ TEST
→ FIX
→ DOCUMENT
→ COMMIT
→ CHECKPOINT

---

# PHASE 0 — PROJECT FOUNDATION

## TASK-001 — Backend foundation

Status: NOT_STARTED
Priority: P0

Objective:

Create the minimal Python/FastAPI backend foundation.

Expected:

- FastAPI application
- application entry point
- configuration
- health endpoint
- dependency management
- basic project logging

Acceptance criteria:

- Backend starts successfully.
- Health endpoint responds successfully.
- No import errors.
- Environment configuration works.
- Basic test passes.

---

## TASK-002 — Backend testing foundation

Status: NOT_STARTED
Priority: P0

Objective:

Create the testing foundation for the backend.

Expected:

- pytest configuration
- API test structure
- health endpoint test

Acceptance criteria:

- pytest executes successfully.
- Health test passes.

---

# PHASE 1 — FRONTEND FOUNDATION

## TASK-003 — Frontend foundation

Status: NOT_STARTED
Priority: P0

Objective:

Create the minimal mobile-friendly frontend.

Expected:

- React + TypeScript if compatible with the project
- clean application structure
- responsive layout
- scanner page

Acceptance criteria:

- Frontend starts successfully.
- Page loads without errors.
- Mobile layout works.

---

# PHASE 2 — CAMERA

## TASK-004 — Mobile camera access

Status: NOT_STARTED
Priority: P0

Objective:

Access the user's phone camera through the browser.

Expected:

- camera permission request
- live video preview
- front/back camera handling where supported
- camera error states

Acceptance criteria:

- Camera opens on supported mobile browser.
- User sees live video.
- Permission denial is handled.
- Camera unavailable state is handled.

---

# PHASE 3 — FRUIT DETECTION

## TASK-005 — Fruit detection pipeline

Status: NOT_STARTED
Priority: P0

Objective:

Detect supported fruits from video frames.

Classes:

- apple
- banana
- guava
- mosambi

Expected:

- object detector integration
- confidence threshold
- bounding box
- fruit class
- unsupported fruit handling

Acceptance criteria:

- Supported fruit can be detected.
- Bounding box is returned.
- Confidence is returned.
- Unsupported fruit is rejected.
- Detection can run on sampled frames.

---

# PHASE 4 — FRAME QUALITY

## TASK-006 — Single-fruit validation

Status: NOT_STARTED
Priority: P0

Objective:

Ensure V1 analyzes one fruit at a time.

Expected states:

- NO_FRUIT
- MULTIPLE_FRUITS
- SUPPORTED_FRUIT
- UNSUPPORTED_FRUIT

Acceptance criteria:

- No fruit is handled correctly.
- Multiple fruits are rejected.
- Supported fruit is accepted.
- Unsupported fruit is rejected.

---

## TASK-007 — Stability detection

Status: NOT_STARTED
Priority: P0

Objective:

Determine whether the detected fruit remains sufficiently stable.

Factors:

- bounding box movement
- detection consistency
- consecutive frames

Acceptance criteria:

- unstable fruit does not trigger capture.
- stable fruit becomes capture-ready.

---

## TASK-008 — Image quality checks

Status: NOT_STARTED
Priority: P0

Objective:

Reject unsuitable frames.

Check:

- blur
- brightness
- fruit size
- visibility
- occlusion where practical

Acceptance criteria:

- blurry frame rejected.
- extremely dark frame rejected.
- extremely bright frame rejected.
- fruit that is too small rejected.
- acceptable frame marked ready.

---

# PHASE 5 — AUTOMATIC CAPTURE

## TASK-009 — Best-frame selection

Status: NOT_STARTED
Priority: P0

Objective:

Automatically select the best frame after detection becomes stable.

Selection factors:

- detection confidence
- sharpness
- brightness
- fruit size
- stability
- visibility

Acceptance criteria:

- system does not immediately capture the first detection.
- best suitable frame is selected.
- captured frame contains the detected fruit.

---

# PHASE 6 — FRESHNESS ANALYSIS

## TASK-010 — Fruit preprocessing

Status: NOT_STARTED
Priority: P0

Objective:

Prepare the captured fruit image for freshness analysis.

Expected:

- crop fruit using bounding box
- resize
- normalize
- preserve useful visual information

Acceptance criteria:

- valid fruit crop produced.
- preprocessing works for all four fruits.

---

## TASK-011 — Visible condition analysis

Status: NOT_STARTED
Priority: P0

Objective:

Estimate visible external fruit condition.

Potential visual signals:

- discoloration
- brown spots
- dark spots
- bruising
- visible damage
- wrinkles
- abnormal color
- texture changes

Important:

This must not be presented as scientific food-safety analysis.

Acceptance criteria:

- analysis produces structured evidence.
- analysis can identify supported visual conditions where implemented.
- insufficient-quality images produce uncertainty.

---

# PHASE 7 — FRESHNESS SCORE

## TASK-012 — Deterministic freshness scoring

Status: NOT_STARTED
Priority: P0

Objective:

Convert visible condition evidence into a reproducible score from 1–10.

Requirements:

- deterministic
- configurable
- explainable
- bounded between 1 and 10

Acceptance criteria:

- same input produces same score.
- score is always 1–10.
- score calculation can be explained.
- penalties/weights are configurable.

---

## TASK-013 — Freshness categories

Status: NOT_STARTED
Priority: P0

Objective:

Convert score into simple user-friendly categories.

Initial categories:

- 1–3: Poor
- 4–5: Low
- 6–7: Fair
- 8–9: Fresh
- 10: Very Fresh

These are product categories, not scientific classifications.

Acceptance criteria:

- category is deterministic.
- category matches configured score range.

---

# PHASE 8 — RESULT UI

## TASK-014 — Result screen

Status: NOT_STARTED
Priority: P0

Objective:

Display the scan result clearly.

Show:

- fruit type
- freshness score
- category
- short analysis
- detected visible issues
- confidence where available
- captured image

Acceptance criteria:

- result is understandable within seconds.
- score is clearly visible.
- analysis is short.
- uncertainty is clearly communicated.

---

# PHASE 9 — DATABASE / HISTORY

## TASK-015 — Scan persistence

Status: NOT_STARTED
Priority: P0

Objective:

Persist completed scans.

Core data:

- scan ID
- fruit type
- captured image
- detection confidence
- freshness score
- analysis
- issues
- timestamp

Acceptance criteria:

- completed scan can be stored.
- result can be retrieved.
- invalid scans are not incorrectly stored as successful scans.

---

## TASK-016 — Scan history

Status: NOT_STARTED
Priority: P0

Objective:

Display previous scans.

Expected:

- scan date
- fruit
- score
- category
- thumbnail

Acceptance criteria:

- previous scans are visible.
- newest scans appear first.
- result can be opened.

---

# PHASE 10 — API INTEGRATION

## TASK-017 — Scanner API integration

Status: NOT_STARTED
Priority: P0

Objective:

Connect frontend scanner flow with backend processing.

Acceptance criteria:

- captured frame reaches backend.
- backend processes the frame.
- result reaches frontend.
- errors are displayed.

---

# PHASE 11 — ERROR HANDLING

## TASK-018 — User-facing error states

Status: NOT_STARTED
Priority: P0

Implement:

- NO_FRUIT
- UNSUPPORTED_FRUIT
- MULTIPLE_FRUITS
- LOW_DETECTION_CONFIDENCE
- IMAGE_TOO_BLURRY
- IMAGE_TOO_DARK
- IMAGE_TOO_BRIGHT
- FRUIT_TOO_SMALL
- FRUIT_OCCLUDED
- ANALYSIS_UNCERTAIN
- MODEL_UNAVAILABLE
- PROCESSING_FAILED

Acceptance criteria:

Every expected failure has a clear user-facing response.

---

# PHASE 12 — INTEGRATION TESTING

## TASK-019 — End-to-end MVP test

Status: NOT_STARTED
Priority: P0

Test:

Camera
→ detection
→ stability
→ capture
→ analysis
→ scoring
→ result
→ persistence
→ history

Acceptance criteria:

A complete scan can be performed successfully.

---

# PHASE 13 — POLISH

## TASK-020 — MVP polish

Status: NOT_STARTED
Priority: P0

Improve:

- loading states
- error messages
- mobile responsiveness
- UI consistency
- performance
- logging
- documentation

Acceptance criteria:

The application is demo-ready.

---

# P1 — OPTIONAL

Only attempt after every P0 task works.

Possible P1 features:

- improved fruit tracking
- better issue localization
- confidence visualization
- scan comparison
- improved model
- richer analytics
- better animations

---

# P2 — FUTURE

Do NOT implement during the 8–10 hour MVP unless everything else is complete.

Possible future features:

- user accounts
- cloud deployment
- multiple-fruit scanning
- fruit shelf-life estimation
- personalized recommendations
- advanced ML model
- dataset management platform
- mobile native application
- notifications

---

# CURRENT TASK

TASK-001

Status: NOT_STARTED

Next action:

Inspect the repository and implement the minimal FastAPI backend foundation.

Do not start TASK-002 until TASK-001 passes its acceptance criteria.