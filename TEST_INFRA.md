# E2E Test Infra: Cut it by Ai With Atif

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial Testing + Real-World Workload Testing.
- Target: Validate end-to-end user workflows against running server (via `tests/run.py` test harness on spare port).

## Feature Inventory
| # | Feature Area | Source | Tier 1 (Happy Path) | Tier 2 (Boundary & Error) | Tier 3 (Cross-Feature) | Tier 4 (Real-World) |
|---|--------------|--------|:-------------------:|:------------------------:|:----------------------:|:-------------------:|
| 1 | Auth, Permissions & Sessions | ORIGINAL_REQUEST §Stack & AGENTS.md | 5 | 5 | ✓ | ✓ |
| 2 | Video Ingestion (Upload & Link) | ORIGINAL_REQUEST §Description | 5 | 5 | ✓ | ✓ |
| 3 | Job Queue Lifecycle & Fair Scheduling | AGENTS.md & ORIGINAL_REQUEST | 5 | 5 | ✓ | ✓ |
| 4 | AI Clip Selection & Judging | ORIGINAL_REQUEST §Description | 5 | 5 | ✓ | ✓ |
| 5 | Captions, Subtitles & Romanization | ORIGINAL_REQUEST §Description | 5 | 5 | ✓ | ✓ |
| 6 | Video Rendering & Formats | ORIGINAL_REQUEST §Description | 5 | 5 | ✓ | ✓ |
| 7 | Brand Consistency ("Cut it by Ai With Atif") | ORIGINAL_REQUEST §Brand Name | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test runner: `tests/run.py` (spawns isolated FastAPI server on throwaway port with isolated test DB and data directory).
- Python executable: Dedicated `.venv` at `.\.venv\Scripts\python.exe`.
- Pass/fail semantics: Exit code 0, all assertions pass.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | User Upload -> Whisper Transcription -> AI Selection -> Rendered 9:16 Short with Captions | F1, F2, F3, F4, F5, F6 | High |
| 2 | Account Sign-up -> Custom AI Key Setting -> Multi-clip Extraction -> Watermark Toggle | F1, F3, F4, F6, F7 | High |
| 3 | Streaming URL Ingestion -> Concurrent Load -> Fair Queue Scheduling -> Error Handling | F2, F3, F6 | High |
| 4 | Non-Latin Video Transcription -> Hindi/Urdu Romanization -> Subtitle Rendering Without Overlap | F4, F5, F6 | Medium |
| 5 | Storage Relocation & Disk Usage Bounds Verification | F1, F2, F6 | Medium |

## Coverage Thresholds
- Tier 1: ≥5 per feature area
- Tier 2: ≥5 per feature area
- Tier 3: Pairwise combinations across major features
- Tier 4: ≥5 realistic end-user scenarios
