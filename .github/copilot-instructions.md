# FruitFresh AI — AI Coding Agent Instructions

## 1. PROJECT

FruitFresh AI is a practical computer-vision prototype that uses a camera to:

1. Detect a fruit in real time.
2. Support exactly four fruits:
   - Apple
   - Banana
   - Guava
   - Mosambi (sweet lime)
3. Check whether the detected fruit/frame is suitable for analysis.
4. Automatically select the best frame.
5. Analyze visible external fruit condition.
6. Generate a practical freshness score from 1 to 10.
7. Provide a short evidence-based analysis.
8. Store scan history.

This is NOT a scientific food-safety system.

The result represents visible external condition only.

Never claim that the system proves that a fruit is safe or unsafe to eat.

---

# 2. DEVELOPMENT PRINCIPLE

Build incrementally.

Never attempt to build the entire application at once.

For every task:

READ
→ PLAN
→ IMPLEMENT
→ TEST
→ INSPECT
→ FIX
→ DOCUMENT
→ CHECKPOINT

Only move to the next task after the current task passes its acceptance criteria.

---

# 3. BEFORE WRITING CODE

Before modifying anything:

1. Inspect the existing repository.
2. Inspect relevant files.
3. Understand the current architecture.
4. Search for existing implementations.
5. Reuse existing code where appropriate.
6. Identify dependencies.
7. State the files you intend to modify.
8. Implement only the requested task.

Never blindly overwrite working code.

---

# 4. DO NOT INVENT REQUIREMENTS

Do not add features that were not requested.

Do not introduce unnecessary:

- microservices
- Docker
- Kubernetes
- cloud infrastructure
- authentication
- payment systems
- message queues
- complex databases
- unnecessary dependencies

Prefer the simplest architecture that satisfies the current task.

---

# 5. SUPPORTED FRUITS

V1 supports ONLY:

- apple
- banana
- guava
- mosambi

"Sweet lime" should be normalized internally to "mosambi".

If another fruit is detected, return an unsupported-fruit state.

Never silently classify an unknown fruit as one of the supported fruits.

---

# 6. REAL-TIME PIPELINE

The intended pipeline is:

Camera
↓
Video frames
↓
Frame sampling
↓
Fruit detection
↓
Single-fruit validation
↓
Stability check
↓
Image-quality check
↓
Best-frame selection
↓
Automatic capture
↓
Fruit-specific freshness analysis
↓
Issue detection
↓
Freshness scoring
↓
Short analysis
↓
Result
↓
History

---

# 7. COMPUTER VISION

Keep these responsibilities separate:

Camera handling
Fruit detection
Tracking/stability
Image quality
Frame selection
Fruit preprocessing
Freshness analysis
Score calculation

Do not put all CV logic into one giant file.

---

# 8. FRESHNESS ANALYSIS

The system estimates visible external condition.

Possible visual evidence includes:

- discoloration
- brown spots
- dark spots
- bruising
- visible surface damage
- wrinkles
- abnormal color
- texture changes

Do NOT claim to detect:

- bacteria
- internal rot
- pesticide residue
- nutritional value
- exact shelf life
- medical safety

If the image is insufficient for reliable visual analysis, return an uncertainty/retake result instead of inventing a score.

---

# 9. SCORE

Freshness score must always be between:

1 and 10

Where:

1 = very poor visible condition

10 = excellent visible condition

The scoring system must be deterministic and explainable.

Do not ask an LLM to randomly choose a score.

The score should be produced by the CV/ML scoring system.

All important scoring weights and thresholds must be configurable.

---

# 10. CONFIGURATION

Never scatter important magic numbers throughout the code.

Examples:

- detection confidence threshold
- stability frames
- stability duration
- minimum fruit size
- blur threshold
- brightness threshold
- score penalties

Keep these in configuration.

---

# 11. ERROR STATES

Use explicit states/errors such as:

NO_FRUIT
UNSUPPORTED_FRUIT
MULTIPLE_FRUITS
LOW_DETECTION_CONFIDENCE
IMAGE_TOO_BLURRY
IMAGE_TOO_DARK
IMAGE_TOO_BRIGHT
FRUIT_TOO_SMALL
FRUIT_OCCLUDED
ANALYSIS_UNCERTAIN
MODEL_UNAVAILABLE
PROCESSING_FAILED

Do not silently ignore expected failures.

---

# 12. CODE QUALITY

Python code must:

- use type hints
- have clear names
- use small focused functions
- follow single responsibility
- avoid unnecessary duplication
- avoid giant files
- use explicit schemas
- use structured errors
- use UTC timestamps

Keep:

CV logic
API logic
database logic
business logic
UI logic

separated.

---

# 13. API

API routes must remain thin.

Do not put large ML/CV algorithms directly inside FastAPI route functions.

Use service/modules for:

- detection
- analysis
- scoring
- persistence

Validate API input/output using explicit schemas.

---

# 14. TESTING

Every meaningful feature must have tests.

When fixing a bug:

1. Reproduce it.
2. Identify the root cause.
3. Fix it.
4. Add a regression test.
5. Run the relevant tests.

Never modify tests simply to make them pass.

---

# 15. MACHINE LEARNING HONESTY

Never invent:

- model accuracy
- precision
- recall
- F1 score
- dataset size
- validation results

Clearly identify whether something is:

- pretrained
- fine-tuned
- rule-based
- heuristic
- experimental

Never describe a heuristic as a trained ML model.

---

# 16. PRIVACY

Do not store continuous camera video by default.

The intended flow is:

Live camera
↓
Best frame
↓
Captured image
↓
Analysis

Only store the captured image when required.

Never commit private user images or secrets to Git.

---

# 17. GIT

Use small logical commits.

Use commit prefixes:

feat:
fix:
refactor:
test:
docs:
chore:

Example:

feat: add fruit detection pipeline

Never commit:

- .env
- secrets
- .venv
- private images
- raw datasets
- unnecessary model artifacts

---

# 18. TASK MANAGEMENT

Before starting a task:

Read TASK_STATUS.md.

After completing a task:

Update:

TASK_STATUS.md
CHANGELOG.md

Record:

- completed task
- files changed
- tests run
- test results
- known limitations
- next task

---

# 19. CURRENT PRIORITY

The first working prototype must prioritize:

1. Camera
2. Real-time fruit detection
3. Stability
4. Automatic best-frame capture
5. Freshness analysis
6. 1–10 score
7. Short analysis
8. Result UI
9. Scan history

Do not spend prototype time on unnecessary production infrastructure.

---

# 20. AGENT BEHAVIOR

When given a task:

1. Inspect the repository first.
2. Explain what you found briefly.
3. Explain the implementation plan.
4. List files that will change.
5. Implement the task.
6. Run tests.
7. Fix failures.
8. Inspect the final changes.
9. Update task documentation.
10. Report:
   - what changed
   - tests performed
   - result
   - limitations
   - next recommended task

Do not proceed to unrelated tasks automatically.

If a requirement is ambiguous, stop and ask.

Do not make large architectural decisions silently.

---

# 21. MOST IMPORTANT RULE

Working software is more important than excessive architecture.

Build the smallest correct version first.

Then improve it.

Never build complexity simply because it looks impressive.