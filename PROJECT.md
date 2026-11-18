# Project: Cut it by Ai With Atif (PeakCut) Full Audit & Production Hardening

## Architecture
Cut it by Ai With Atif is an AI-powered automated video clipping, transcription, and captioning platform.
- **Backend / Web Server (`studio/server.py`, `studio/auth.py`, `studio/account.py`, `studio/admin.py`, `studio/db.py`, `studio/config.py`)**:
  - FastAPI / Starlette application serving REST API and static frontend assets.
  - Session gate (`Gate`) providing user context `ctx.uid()` and change notification counter `ctx.bump()`.
  - SQLAlchemy Core database layer with SQLite (WAL mode) and PostgreSQL (`psycopg3`) support.
- **Media Pipeline & Fair Queue (`studio/jobs.py`, `studio/media.py`, `studio/transcribe.py`, `studio/render.py`, `studio/live.py`)**:
  - Video ingestion via yt-dlp or direct chunked uploads.
  - Fair queue (`_FairQueue`) balancing jobs and clip renders across creators.
  - Speech-to-text transcription via sherpa-onnx / Whisper models with local pool and remote ASR worker options.
  - Video clipping, 9:16 vertical formatting, and animated karaoke subtitle rendering via ffmpeg and Pillow.
  - Live stream capture (YouTube, Twitch, Kick) via streamlink / ffmpeg with audio offset alignment.
- **AI Engine, Brain & UI (`studio/ai.py`, `studio/brain.py`, `studio/usage.py`, `web/index.html`)**:
  - Pluggable AI providers (Gemini, OpenAI, Anthropic, xAI, Groq, Ollama, custom OpenAI-compatible endpoints).
  - Intelligent clip heuristics, live highlight judging, title/hook generation with strict prompt isolation (`brain._safe`).
  - Token tracking, usage analytics, and quota management.
  - Single-page application (vanilla HTML/CSS/JS) polling `/api/sync` for reactive updates.

## Feature Inventory
| # | Feature / Remediation Item | Description | Milestone | Source |
|---|-----------------------------|-------------|-----------|--------|
| 1 | SQLite Foreign Keys Enforcement | Run `PRAGMA foreign_keys = ON;` in `_fast_sqlite` connection listener (`studio/db.py`) | M1 | Survey (Explorer 1) |
| 2 | PostgreSQL Psycopg3 URL Handling | Normalize `postgresql://` and `postgres://` connection strings to `postgresql+psycopg://` in `studio/config.py` | M1 | Survey (Explorer 1) |
| 3 | Upload File Move Exception Handling | Wrap file move in `studio/server.py:create_from_file` in `try...except OSError` to clean up orphaned job directory on disk error | M1 | Survey (Explorer 1) |
| 4 | FastAPI Lifespan Modernization | Migrate deprecated `@app.on_event("startup")` handlers to `@asynccontextmanager async def lifespan(app: FastAPI)` | M1 | Survey (Explorer 1) |
| 5 | Rate Limiter Eviction Bounding | Guard `_attempts` eviction in `studio/auth.py` so memory remains strictly bounded under automated scans | M1 | Survey (Explorer 1) |
| 6 | Baseline Test Suite Stabilization | Increase CPU cooldown timeout to 30s in `tests/test_load_queue.py` and add status code check in `tests/test_upload_parts.py` | M1 | Survey (Explorer 1) |
| 7 | ThreadPoolExecutor Cleanup | Enclose `_run_job` execution in `studio/jobs.py` within `try...finally` to guarantee `fetch`, `ahead`, and `renders` executors are shutdown and cancelled on error | M2 | Survey (Explorer 2) |
| 8 | Double-Render & Stuck Clip Guard | Prevent concurrent duplicate remake tasks in `studio/jobs.py` and catch exceptions in clip remake to avoid stuck queued status | M2 | Survey (Explorer 2) |
| 9 | Clip Timeout Race Condition Fix | Ensure timed-out clips in `studio/jobs.py:_wait_for_clips` cancel underlying tasks and do not allow late completions to overwrite error state | M2 | Survey (Explorer 2) |
| 10 | Interrupted Upload Resume Safety | Guard `_load_file` and `_pick_up_after_restart` in `studio/jobs.py` so incomplete uploads with empty paths are not enqueued to probe | M2 | Survey (Explorer 2) |
| 11 | Whisper Model Pool Deadlock Prevention | Wrap model acquisition (`_take_now()` / `_take()`) and release in `studio/transcribe.py` in robust `try...finally` context | M2 | Survey (Explorer 2) |
| 12 | Windows MAX_PATH Handling | Add path normalization or relative path handling for source video `-i <src>` in `studio/render.py` | M2 | Survey (Explorer 2) |
| 13 | Hardware Video Acceleration | Add detection and support for NVIDIA NVENC (`h264_nvenc`) and Apple VideoToolbox (`h264_videotoolbox`) in `studio/render.py` alongside Intel QSV | M2 | Survey (Explorer 2) |
| 14 | Live Subprocess & Socket Lifecycle | Add `atexit` cleanup and process termination for ffmpeg live capture, and close raw socket on SSL handshake failure in `studio/live.py` | M2 | Survey (Explorer 2) |
| 15 | Media Cache Thread Safety & Durations | Add thread lock to `_PREVIEWS` cache and handle `"N/A"` duration strings in `studio/media.py:probe()` | M2 | Survey (Explorer 2) |
| 16 | Prompt Injection Sanitization | Call `_safe()` on `title`, `uploader`, and `text` in `studio/brain.py:describe()` | M3 | Survey (Explorer 3) |
| 17 | Gemini Safety Response Parsing | Safely check `candidates` and `content` in `studio/ai.py` before indexing `parts` to prevent unhandled 500 errors on safety/recitation block | M3 | Survey (Explorer 3) |
| 18 | Watermark Checkbox State Fix | Correct `web/index.html:4790` to evaluate `i.type === "checkbox" ? i.checked : ...` so watermarks can be toggled off | M3 | Survey (Explorer 3) |
| 19 | Composer Watermark Option | Add `o.watermark = document.getElementById("o_watermark")?.checked || false` in `web/index.html:jobOptions()` | M3 | Survey (Explorer 3) |
| 20 | AI Test Toast Notification Fix | Update `web/index.html:4610` so testing AI without saving does not misleadingly toast "Saved." | M3 | Survey (Explorer 3) |
| 21 | Brand Alignment ("Cut it by Ai With Atif") | Standardize brand name across `web/index.html`, `web/auth.html`, `web/reset.html`, `web/admin.html`, `web/legal.html`, `studio/storage.py`, `studio/tools.py`, `studio/alerts.py`, and `studio/ai.py` | M3 | Survey (Explorer 3) |
| 22 | UI Styling Compliance | Ensure styling conforms with AGENTS.md rules (no shadows, hover states change colour only, palette preservation) | M3 | Survey (Explorer 3) |
| 23 | E2E Requirement Test Infrastructure | Design opaque-box test runner and multi-tier test cases (Tiers 1-4) in `TEST_INFRA.md` published to `TEST_READY.md` | E2E Track | Dual Track |
| 24 | Final Acceptance & Adversarial Hardening | Pass 100% of E2E tests across Tiers 1-4, followed by Tier 5 adversarial stress testing | M4 | Dual Track |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend & Database Reliability | Features 1, 2, 3, 4, 5, 6 (`studio/db.py`, `studio/config.py`, `studio/server.py`, `studio/auth.py`, `tests/test_load_queue.py`, `tests/test_upload_parts.py`) | none | DONE |
| M2 | Media Pipeline, Jobs & Rendering Hardening | Features 7, 8, 9, 10, 11, 12, 13, 14, 15 (`studio/jobs.py`, `studio/media.py`, `studio/transcribe.py`, `studio/render.py`, `studio/live.py`) | none | DONE |
| M3 | AI Engine, Prompt Safety, Frontend & Brand Alignment | Features 16, 17, 18, 19, 20, 21, 22 (`studio/brain.py`, `studio/ai.py`, `web/index.html`, `web/*.html`, `studio/storage.py`, `studio/alerts.py`, `studio/tools.py`) | none | DONE |
| E2E | Requirement-Driven E2E Test Track | Feature 23 (Opaque-box test suite across Tiers 1-4, publish `TEST_READY.md`) | none | DONE |
| M4 | Final Acceptance & Adversarial Hardening | Feature 24 (Pass 100% E2E tests, Tier 5 adversarial testing via Challenger wave, clean audit) | M1, M2, M3, E2E | DONE |

## Interface Contracts
### `studio/db.py` ↔ `studio/server.py` & `studio/account.py`
- SQLite connections guarantee `PRAGMA foreign_keys = ON;`.
- Deleting an account or job enforces referential cascade integrity without orphaned records.
### `studio/jobs.py` ↔ `studio/render.py` & `studio/media.py`
- `_run_job` guarantees deterministic executor shutdown via `try...finally`.
- `render_one` accepts safe extended paths on Windows; does not overwrite timed-out clip records.
### `studio/brain.py` ↔ `studio/ai.py`
- All metadata (`title`, `uploader`, `text`) passed to prompt functions must be sanitized through `brain._safe()`.
- AI providers return `(dict, int, int)` or raise handled exceptions with user-friendly explanations.

## Code Layout
- `studio/server.py` — Web endpoints, session gate, upload streaming.
- `studio/config.py` — Environment configuration, path constants, database connection string normalization.
- `studio/db.py` — SQLAlchemy Core database engine, tables, SQLite WAL and FK pragmas.
- `studio/auth.py`, `studio/account.py`, `studio/admin.py` — User management, passwords, throttling, admin operations.
- `studio/jobs.py` — Queue management, job processing, clip dispatch, lifecycle state machine.
- `studio/media.py` — yt-dlp metadata, media download, audio probing, stream caching.
- `studio/transcribe.py`, `studio/fetch_model.py` — Speech recognition pool, audio chunking, model download.
- `studio/render.py` — Video cutting, vertical framing, Pillow subtitle layout, ffmpeg video rendering.
- `studio/live.py` — Live stream recording, segment buffer, audio alignment.
- `studio/ai.py` — LLM provider HTTP clients, error handling, token accounting.
- `studio/brain.py` — Prompt templates, clip scoring heuristics, input escaping.
- `web/index.html` — Main SPA application (dashboard, uploads, clip editor, settings).
- `web/auth.html`, `web/reset.html`, `web/admin.html`, `web/legal.html` — Authentication and admin pages.
- `tests/` — Test suites executed via `python tests/run.py`.
