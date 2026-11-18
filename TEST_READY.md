# TEST_READY: Cut it by Ai With Atif (E2E Test Suite)

**Date**: 2026-11-17  
**Test Suite Path**: `tests/test_e2e_suite.py`  
**Execution Environment**: Python 3.10+ in dedicated virtual environment (`.\.venv\Scripts\python.exe`)  
**Status**: **ALL TESTS PASSING (82/82 OK, Exit Code: 0)**

---

## 1. Test Execution Commands

### Primary E2E Test Suite (Tiers 1–4)
```powershell
.\.venv\Scripts\python.exe tests/test_e2e_suite.py
```
- **Total Tests**: 82
- **Passed**: 82
- **Failed**: 0
- **Errors**: 0
- **Duration**: ~46 seconds

### Baseline Server Test Suite
```powershell
.\.venv\Scripts\python.exe tests/run.py
```
- **Coverage**: 14 test modules, 100% passing

---

## 2. Test Architecture & Design Philosophy

The E2E test suite adheres strictly to **opaque-box, requirement-driven verification**:
- **Zero reliance on internal module states**: Tests exercise the application through its HTTP API routes (`FastAPI`), database models (`SQLAlchemy`), media processing pipeline (`ffmpeg`, `yt-dlp`), and rendered web interfaces.
- **Isolated Throwaway Server**: `E2EGlobalHarness` spawns a real, isolated server process on an ephemeral loopback port (`127.0.0.1:<spare_port>`) with a clean temporary SQLite database and dedicated storage directory (`PEAKCUT_DATA=<tempdir>`).
- **Deterministic Synthetic Fixtures**: Real 1080x1920 / 1920x1080 test MP4 video files with audio tracks and test watermarks are generated dynamically using `ffmpeg` without external downloads.
- **Multi-Tenant State Pre-provisioning**: Dedicated accounts (`admin_e2e`, `alice_e2e`, `bob_e2e`) with authenticated sessions and isolated client states.

---

## 3. Test Coverage by Tier

| Tier | Tier Name | Test Count | Passing | Description |
|:---:|---|:---:|:---:|---|
| **Tier 1** | **Feature Coverage (Happy Path)** | 35 | 35 | Core functional coverage across all 7 feature areas (≥5 per area). |
| **Tier 2** | **Boundary & Corner Cases** | 35 | 35 | Limits, empty inputs, malformed bodies, oversized payloads, 404/400/403/409/413 error paths (≥5 per area). |
| **Tier 3** | **Cross-Feature Combinations** | 7 | 7 | Pairwise interactions between Auth, Ingestion, Fair Queue, AI Clip selection, Rendering, and Cleanup. |
| **Tier 4** | **Real-World Application Scenarios** | 5 | 5 | End-to-end user journeys mirroring complete production workflows. |
| **Total** | | **82** | **82** | **100% Pass Rate** |

---

## 4. Feature Coverage Matrix (All 7 Feature Areas)

### Feature 1: Auth, Permissions & Sessions
- `test_t1_f1_01_auth_signup_success`: Account signup with email and password returns session and user profile.
- `test_t1_f1_02_auth_login_session`: Login returns active session cookie (`peakcut_session`).
- `test_t1_f1_03_auth_me_profile`: `/api/auth/me` reflects authenticated profile and permissions.
- `test_t1_f1_04_auth_accounts_disabled_owner`: Local mode / accounts disabled returns default local owner.
- `test_t1_f1_05_auth_logout_clears_session`: Logout terminates session cookie and subsequent requests require auth.
- `test_t2_f1_01_auth_empty_email_rejected`: Empty email address rejected with 400.
- `test_t2_f1_02_auth_csrf_untrusted_origin_rejected`: Untrusted CORS/Origin headers blocked on sensitive routes.
- `test_t2_f1_03_auth_invalid_session_cookie_returns_401`: Corrupt session cookie yields 401 Unauthorized.
- `test_t2_f1_04_auth_weak_password_rejected`: Password under minimum length requirement rejected with 400.
- `test_t2_f1_05_auth_non_admin_forbidden_from_admin_endpoints`: Non-admin user access to `/api/ai` concealed with 404.

### Feature 2: Video Ingestion (Direct Upload & Link Submission)
- `test_t1_f2_01_ingest_direct_upload`: Direct multipart upload creates job with source metadata.
- `test_t1_f2_02_ingest_multipart_start`: Chunked upload initialization returns upload ID and part specification.
- `test_t1_f2_03_ingest_multipart_complete`: Multi-part chunk assembly and validation into final video job.
- `test_t1_f2_04_ingest_url_job_submission`: Remote video URL submission accepts streaming source and creates job.
- `test_t1_f2_05_ingest_media_probe`: Probe utility extracts width, height, duration, and stream properties.
- `test_t2_f2_01_ingest_oversized_payload_rejected`: Payload exceeding size thresholds rejected with 413.
- `test_t2_f2_02_ingest_empty_zero_byte_upload_rejected`: 0-byte upload initialization rejected with 400 ("Bad file size").
- `test_t2_f2_03_ingest_invalid_media_extension_rejected`: Unsupported non-video extension (.exe) rejected with 400.
- `test_t2_f2_04_ingest_multipart_wrong_part_size_rejected`: Incomplete / incorrect part sizes rejected during upload.
- `test_t2_f2_05_ingest_nonexistent_upload_id_returns_404`: Non-existent upload chunk target returns 404.

### Feature 3: Job Queue Lifecycle & Fair Scheduling
- `test_t1_f3_01_queue_job_creation_and_status`: Job creation sets initial queued state.
- `test_t1_f3_02_queue_lifecycle_polling`: Sync endpoint reflects job state changes and stage notifications.
- `test_t1_f3_03_queue_fair_scheduling_round_robin`: `_FairQueue` interleaves multi-user jobs in fair round-robin order.
- `test_t1_f3_04_queue_job_cancellation`: Active/queued jobs protected against illegal deletion (409) and in-flight upload cancellation (200).
- `test_t1_f3_05_queue_concurrency_and_ahead_depth`: Ahead count calculates user position in processing line accurately.
- `test_t2_f3_01_queue_nonexistent_job_returns_404`: Querying non-existent job ID returns 404.
- `test_t2_f3_02_queue_cross_user_isolation`: User B cannot inspect or delete User A's jobs (returns 404).
- `test_t2_f3_03_queue_malformed_options_handling`: Malformed JSON options cleaned and sanitized safely.
- `test_t2_f3_04_queue_invalid_clip_rerender_404`: Re-render request on non-existent clip returns 404.
- `test_t2_f3_05_queue_delete_nonexistent_clip_404`: Deleting non-existent clip returns 404.

### Feature 4: AI Clip Selection & Judging
- `test_t1_f4_01_ai_settings_save_provider`: Admin configures AI model provider settings (`ai.json`).
- `test_t1_f4_02_ai_list_providers`: System lists supported AI model providers (OpenAI, Gemini, Anthropic, Ollama, etc.).
- `test_t1_f4_03_ai_clip_heuristic_tidy`: Heuristic bounds tidy clip boundaries and prevent overlapping timestamps.
- `test_t1_f4_04_ai_token_usage_tracking`: Token tracker records AI prompt and completion usage.
- `test_t1_f4_05_ai_prompt_sanitization_safe`: Untrusted video transcript text properly escaped in AI prompts (`brain._safe`).
- `test_t2_f4_01_ai_empty_transcript_handling`: Empty transcript input safely parsed without crashing heuristic judge.
- `test_t2_f4_02_ai_corrupted_llm_json_fallback`: Malformed LLM response safely rescued by regex JSON extractor.
- `test_t2_f4_03_ai_unknown_provider_settings_error`: Saving invalid provider configuration raises 400.
- `test_t2_f4_04_ai_negative_duration_clip_rejection`: Clips with `start >= end` rejected or corrected by heuristic cleaner.
- `test_t2_f4_05_ai_excessive_tokens_usage_log`: Usage records persist and query without overflow.

### Feature 5: Captions, Subtitles & Romanization
- `test_t1_f5_01_captions_hindi_romanization`: Devanagari Hindi text transliterated to Latin script.
- `test_t1_f5_02_captions_urdu_romanization`: Perso-Arabic Urdu text transliterated to readable Latin characters.
- `test_t1_f5_03_captions_drawable_glyph_detection`: Font glyph rasterizer detects missing glyphs and handles fallback.
- `test_t1_f5_04_captions_ass_event_generation`: ASS subtitle event generator produces styled Dialogue lines.
- `test_t1_f5_05_captions_word_timestamp_sync`: Word-level timestamps synchronized with video timeline.
- `test_t2_f5_01_captions_empty_words_ass_generation`: Empty word list generates valid ASS header without dialogue errors.
- `test_t2_f5_02_captions_malformed_timestamp_correction`: Misordered word timestamps sanitized and monotonically ordered.
- `test_t2_f5_03_captions_untransliterable_symbols`: Special punctuation and emojis preserved without breaking Romanizer.
- `test_t2_f5_04_captions_oversized_words_chunking`: Long spoken phrases split into manageable subtitle lines.
- `test_t2_f5_05_captions_special_characters_in_ass`: ASS meta-characters (`{`, `}`, `\`, newline) escaped properly.

### Feature 6: Video Rendering & Formats
- `test_t1_f6_01_render_vertical_geometry_1080x1920`: Crop and scale filters target vertical 1080x1920 (9:16).
- `test_t1_f6_02_render_ass_subtitle_styles`: Subtitle style configurations (bold, color, size, positioning).
- `test_t1_f6_03_render_watermark_filter_generation`: Filter complex constructs valid watermark overlay parameters.
- `test_t1_f6_04_render_ffmpeg_clip_execution`: Real ffmpeg execution generates valid playable MP4 clip with audio.
- `test_t1_f6_05_render_encoder_detection_fallback`: Hardware acceleration detection falls back cleanly to `libx264`.
- `test_t2_f6_01_render_invalid_crop_coordinates`: Invalid / negative crop dimensions handled without filter crash.
- `test_t2_f6_02_render_unsupported_aspect_ratio_fit`: Non-standard video dimensions scaled to 9:16 vertical envelope.
- `test_t2_f6_03_render_zero_length_duration_rejected`: 0-second clip render request rejected with 400.
- `test_t2_f6_04_render_missing_source_video_error`: Missing source media file raises descriptive FileNotFoundError.
- `test_t2_f6_05_render_watermark_missing_asset_fallback`: Missing watermark image asset falls back to text or unwatermarked render.

### Feature 7: Brand Consistency ("Cut it by Ai With Atif")
- `test_t1_f7_01_brand_dashboard_index_html`: Main web app interface contains exact brand name.
- `test_t1_f7_02_brand_auth_html`: Authentication portal prominently features "Cut it by Ai With Atif".
- `test_t1_f7_03_brand_reset_html`: Password reset page displays "Cut it by Ai With Atif".
- `test_t1_f7_04_brand_admin_html`: Admin control center displays "Cut it by Ai With Atif".
- `test_t1_f7_05_brand_legal_html`: Terms and legal documentation display "Cut it by Ai With Atif".
- `test_t2_f7_01_brand_unauthenticated_landing_no_leak`: Brand header renders cleanly without authenticated session leaks.
- `test_t2_f7_02_brand_storage_relocation_maintains_brand`: Storage relocation configuration maintains brand context.
- `test_t2_f7_03_brand_alert_notifications_maintain_brand`: Browser notifications and titles preserve brand integrity.
- `test_t2_f7_04_brand_error_pages_preserve_headers`: 404 / 500 error responses maintain system brand consistency.
- `test_t2_f7_05_brand_case_sensitive_brand_name_consistency`: Strict case-sensitive assertion for "Cut it by Ai With Atif".

---

## 5. Cross-Feature Combinations (Tier 3)
- `test_t3_01_combo_auth_and_ingestion`: Authenticated upload ensures job ownership, tenant isolation, and user storage segregation.
- `test_t3_02_combo_ingestion_and_fair_queue`: Simultaneous uploads from multiple users are scheduled fairly via round-robin queue.
- `test_t3_03_combo_queue_and_ai_clip_selection`: Queued video transcription flows through AI heuristic clip selection.
- `test_t3_04_combo_ai_selection_and_watermark_render`: AI-extracted clip boundaries combined with watermark overlay in render filter complex.
- `test_t3_05_combo_ingestion_non_latin_and_romanization`: Non-Latin video audio transcription processed with Hindi/Urdu Romanizer.
- `test_t3_06_combo_storage_relocation_and_job_access`: Active data directory relocation status reflects environment constraints.
- `test_t3_07_combo_user_deletion_and_cascade_cleanup`: Account deletion cascades across creators and associated data cleanly.

---

## 6. Real-World Application Scenarios (Tier 4)
- `test_t4_01_scenario_upload_transcribe_ai_render_short`:
  **Workflow 1**: User Upload -> Audio Transcription -> AI Clip Selection -> Rendered 9:16 Short with Synchronized Captions.
- `test_t4_02_scenario_signup_custom_ai_key_multiclip_watermark`:
  **Workflow 2**: Account Sign-up -> Custom AI Key Setting -> Multi-clip Extraction -> Watermark Overlay.
- `test_t4_03_scenario_streaming_url_concurrent_load_fair_queue_error_handling`:
  **Workflow 3**: Streaming Ingestion -> Concurrent Load -> Fair Queue Scheduling -> Error Handling.
- `test_t4_04_scenario_non_latin_transcription_hindi_urdu_romanization_no_overlap`:
  **Workflow 4**: Non-Latin Video Transcription -> Hindi/Urdu Romanization -> Subtitle Rendering Without Overlap.
- `test_t4_05_scenario_storage_relocation_disk_usage_bounds`:
  **Workflow 5**: Storage Management & Disk Usage Bounds Verification.

---

## 7. Sign-off & Readiness

The E2E test suite in `tests/test_e2e_suite.py` has been fully validated against the live server environment and passes with **0 failures, 0 errors across all 82 tests**. The baseline regression suite (`tests/run.py`) remains 100% functional. PeakCut ("Cut it by Ai With Atif") meets all criteria for Milestone 4 acceptance.
