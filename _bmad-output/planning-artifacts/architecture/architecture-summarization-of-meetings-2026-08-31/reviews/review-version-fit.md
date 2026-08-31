# Final Reviewer Gate — Technology and Version Fit

**Review date:** 2026-08-31  
**Artifact:** `ARCHITECTURE-SPINE.md`  
**Verdict:** **NEEDS CORRECTION**  
**Decision-breaking findings:** Critical 0 / High 3 / Medium 1 / Low 0

All named versions are real releases. The Python and frontend sets are mutually compatible, and the two model families have acceptable upstream licenses for the intended Apache-2.0 project. The gate remains open because several pins are not reproducible as written and the runtime topology does not yet guarantee the resource and SQLite capabilities claimed by AD-12/AD-14.

## Findings

### VF-1 — High — Model pins are not reproducible as written, and the Whisper artifact is mislabeled as int8

**Evidence**

- The selected Whisper repository resolves at full revision `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`; its `model.bin` is 1,617,884,929 bytes with LFS SHA-256 `e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da`. The repository is marked MIT. Its own model card explicitly says the stored weights are **FP16**, converted with `--quantization float16`; int8 is a CTranslate2 runtime `compute_type`, not the downloaded artifact format. [Pinned model tree](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo/tree/0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf), [model card](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo/blob/0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf/README.md), [faster-whisper CPU int8 usage](https://github.com/SYSTRAN/faster-whisper/tree/v1.2.1#faster-whisper).
- The selected Qwen repository resolves at full revision `bc640142c66e1fdd12af0bd68f40445458f3869b`; the required file is `Qwen3-4B-Q4_K_M.gguf`, 2,497,280,256 bytes, LFS SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`. The repository includes Apache-2.0 terms and explicitly documents llama.cpp support. [Pinned model tree](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/bc640142c66e1fdd12af0bd68f40445458f3869b), [license](https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/bc640142c66e1fdd12af0bd68f40445458f3869b/LICENSE).
- The spine records Whisper with only a seven-character prefix plus `int8`, and Qwen as `bc640142…`. The latter is not a syntactically usable revision. Neither row names the exact artifact checksum that `model-fetch` must verify.

**Why it breaks a decision:** AD-12 and AD-14 promise an offline-capable, checksum-verifiable release manifest. A truncated revision with an ellipsis cannot be fetched deterministically, and calling the FP16 Whisper artifact `int8` makes resource/storage provenance ambiguous.

**Required correction:** replace both rows with full repository commits and exact artifact identities/checksums. Represent Whisper as `FP16 CT2 artifact; device=cpu; compute_type=int8`. For Qwen name `Qwen3-4B-Q4_K_M.gguf`. Make `model-fetch` verify size and SHA-256 before atomic publication. Pin the chat template, context size, `enable_thinking=false`/`reasoning_effort=none`, sampling parameters, and schema-constrained response mode in the release profile; llama.cpp v0.3.0 supports JSON-schema-constrained responses and disabling thinking through chat-template kwargs. [llama-server response format](https://github.com/ggml-org/llama.cpp/blob/v0.3.0/tools/server/README.md#post-v1chatcompletions-openai-compatible-chat-completions-api), [Qwen3 inference guidance](https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/bc640142c66e1fdd12af0bd68f40445458f3869b/README.md#best-practices).

### VF-2 — High — The declared `llama-server` topology does not guarantee AD-12's sequential model loading

**Evidence**

- AD-5 declares `llama-server` as a Compose service, while AD-12 says ASR and LLM are loaded sequentially to remain within the 16-GB baseline.
- A normal `llama-server -m model.gguf` process loads the model at server startup and remains ready with it loaded. llama.cpp v0.3.0 also offers router mode when launched without a model, with explicit loaded/unloaded/sleeping states, but the spine does not select that mode or define a stage-bound unload transition. [llama-server quick start](https://github.com/ggml-org/llama.cpp/blob/v0.3.0/tools/server/README.md#quick-start), [multiple-model router lifecycle](https://github.com/ggml-org/llama.cpp/blob/v0.3.0/tools/server/README.md#using-multiple-models).

**Why it breaks a decision:** under the most direct Compose implementation, Qwen remains resident while `local-worker` loads Whisper, contradicting the mechanism AD-12 relies on to keep memory bounded. The model sizes themselves fit 16 GB, but concurrent runtime/KV/decode allocations have not been bounded.

**Required correction:** choose one enforceable lifecycle: (a) start/stop or scale `llama-server` only around `summarize`, with readiness and confirmed process exit before ASR starts; (b) run v0.3.0 router mode and require the Qwen instance to reach `unloaded`/`sleeping` before `transcribe`; or (c) remove the separate service and supervise a stage-scoped llama process from the local worker. Record maximum context/KV/cache settings and prove peak RSS at AD-14's 16-GB CPU gate.

### VF-3 — High — `SQLite 3.53.4 + FTS5` is not actually pinned to Python's runtime library

**Evidence**

- Python's `sqlite3` module reports the version of the **runtime SQLite library**, not a version selected by SQLAlchemy. [Python 3.13 sqlite3 documentation](https://docs.python.org/3.13/library/sqlite3.html#sqlite3.sqlite_version).
- SQLite 3.53.4 is a real 2026-07-24 release. [Official release log](https://www.sqlite.org/releaselog/3_53_4.html).
- FTS5 inclusion depends on how SQLite is built: the canonical source-tree build needs `--enable-fts5`, or another build system needs `SQLITE_ENABLE_FTS5`; only the amalgamation configure default currently enables it. [Official FTS5 build documentation](https://www.sqlite.org/fts5.html#building_fts5_as_part_of_sqlite).
- WAL requires every process to share the same host and does not work on a network filesystem. A local Docker named volume satisfies that premise; an arbitrary NFS/SMB bind mount does not. [Official WAL constraints](https://www.sqlite.org/wal.html#overview).

**Why it breaks a decision:** pinning the Python image and SQLAlchemy does not make its linked SQLite become 3.53.4 or guarantee FTS5. AD-9 can fail at first migration or silently run on another SQLite revision, and user-selected network-backed data paths can invalidate AD-2/AD-3's cross-container locking assumptions.

**Required correction:** make the backend/runtime image build or install one known SQLite 3.53.4 artifact, linked to Python's `_sqlite3`, and pin that image by digest. Add a startup/release gate asserting `sqlite3.sqlite_version == 3.53.4`, `ENABLE_FTS5` in `PRAGMA compile_options`, successful `CREATE VIRTUAL TABLE ... USING fts5`, WAL activation, and locking from both `app` and `local-worker`. State that the database volume must be a local Docker volume/local filesystem; fail fast or document unsupported NFS/SMB placement.

### VF-4 — Medium — FFmpeg 9.0.1 names source, not a reproducible codec/runtime build

**Evidence**

- FFmpeg 9.0.1 is a real current source release, but the project itself distributes source and points users to third-party compiled packages. [Official download page](https://ffmpeg.org/download.html).
- AD-13 depends on `ffprobe`/FFmpeg behavior for four containers and audio-track/decodability checks. Compile flags determine codecs and licensing. FFmpeg's own compliance checklist requires, among other things, building without `--enable-gpl` and `--enable-nonfree` for the LGPL route, preserving the matching source and build configuration. [FFmpeg legal checklist](https://ffmpeg.org/legal.html#license-compliance-checklist).
- faster-whisper does not use the system FFmpeg binary for decoding; it uses PyAV, whose wheel bundles FFmpeg libraries. The release therefore contains two separately versioned FFmpeg surfaces unless the design intentionally avoids one. [faster-whisper requirements](https://github.com/SYSTRAN/faster-whisper/tree/v1.2.1#requirements).

**Why it matters:** `FFmpeg 9.0.1` alone cannot prove that the release image can probe/decode the PRD's MP4/MOV/MKV/WebM corpus or that redistributed binaries satisfy the selected license path.

**Required correction:** pin the source checksum, container build recipe/configure flags, enabled demuxers/decoders, and resulting binary/image digest; test `ffprobe -version` plus the four-container corpus. Include matching FFmpeg sources/notices/build flags in release compliance artifacts. Lock PyAV and its bundled FFmpeg libraries separately in the SBOM and corpus test.

## Version and compatibility matrix

| Named item | Reality/currentness at 2026-08-31 | Compatibility / fit verdict |
| --- | --- | --- |
| Python 3.13.15 | Real supported 3.13 patch; official source, macOS and Windows artifacts exist. [Python release](https://www.python.org/downloads/release/python-31315/) | Compatible with FastAPI, SQLAlchemy, Alembic and faster-whisper metadata. CTranslate2/PyAV/ONNX Runtime publish CPython 3.13 wheels for Linux x86_64/aarch64; preserve wheel/platform checks in the image build. |
| FastAPI 0.141.1 | Real, non-yanked, current PyPI release; declares Python >=3.10 and Python 3.13 support. [PyPI metadata](https://pypi.org/pypi/fastapi/0.141.1/json) | Fits REST/OpenAPI/SSE API role. Lock Starlette, Pydantic and Uvicorn transitives in the backend lockfile. |
| SQLAlchemy 2.0.52 | Real, non-yanked, current 2.0 release. [Release](https://github.com/sqlalchemy/sqlalchemy/releases/tag/rel_2_0_52) | Compatible with Python 3.13/Alembic 1.19.1; does not itself pin SQLite (VF-3). |
| Alembic 1.19.1 | Real, non-yanked, current release; requires Python >=3.10 and SQLAlchemy >=1.4.23. [Release](https://github.com/sqlalchemy/alembic/releases/tag/rel_1_19_1) | Compatible with the selected Python/SQLAlchemy pair and linear migration policy. |
| SQLite 3.53.4 + FTS5 + WAL | Real current release. | Feature fit is good, but the runtime link/compile flags are unresolved (VF-3). |
| FFmpeg 9.0.1 | Real current source release. | Functional fit is good; distributable build identity and codec/license surface are unresolved (VF-4). |
| React 19.2.7 | Real stable release. 19.2.8 is the latest patch as of review and contains an RSC decoding performance change; this Vite SPA does not use RSC. [19.2.7](https://github.com/react/react/releases/tag/v19.2.7), [19.2.8](https://github.com/react/react/releases/tag/v19.2.8) | Compatible. Updating to 19.2.8 is sensible but not architecture-breaking; pin matching `react-dom` and type packages in the lockfile. |
| TypeScript 6.0.3 | Real stable release; current upstream major is 7.0. [6.0.3 release](https://github.com/microsoft/TypeScript/releases/tag/v6.0.3), [official downloads](https://www.typescriptlang.org/download/) | Compatible with Node 24 and Vite 8. A deliberate one-major-back pin is acceptable if the frontend lockfile and CI typecheck own it. |
| Vite 8.2.2 | Real current release. [Release](https://github.com/vitejs/vite/releases/tag/v8.2.2) | Requires Node 20.19+ or 22.12+; Node 24.20.0 satisfies this. [Vite compatibility note](https://vite.dev/guide/#scaffolding-your-first-vite-project) |
| Node.js 24.20.0 LTS | Real latest v24 LTS (`Krypton`) at review time. [Node release table](https://nodejs.org/en/about/previous-releases) | Correct build-only baseline for Vite 8.2.2. Keep it out of runtime images. |
| Docker Compose 5.4.0 | Real signed release; 5.5.0 is newer. [5.4.0 release](https://github.com/docker/compose/releases/tag/v5.4.0) | Core required features fit. Treat this as tested/minimum host tooling rather than an image pin; validate the Compose file against 5.4.0 and current 5.5.x on all three host OSes. |
| faster-whisper 1.2.1 | Real current release; requires Python >=3.9 and CTranslate2 >=4,<5. [PyPI](https://pypi.org/project/faster-whisper/1.2.1/) | Compatible with Python 3.13 when Linux wheel platforms are fixed. Fit for timestamps and CPU int8; transitive native packages must be locked. |
| llama.cpp 0.3.0 | Real signed, latest stable semantic release. [Release](https://github.com/ggml-org/llama.cpp/releases/tag/v0.3.0) | Supports Qwen GGUF, OpenAI-style server calls, JSON-schema constrained output, and model router lifecycle. Build from the signed source tag/commit or pin the resulting image digest; release page supplies only a pointer to a nightly binary build, not a complete stable binary matrix. |
| Whisper large-v3-turbo CT2 `0a363e9` | Real verified revision; MIT metadata; source Whisper code/license is MIT. [model](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo/tree/0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf), [upstream license](https://github.com/openai/whisper/blob/main/LICENSE) | Format fits faster-whisper, but artifact is FP16 and int8 is runtime compute mode (VF-1). Quality/resource release gates remain necessary. |
| Qwen3-4B-GGUF `bc640142…`, Q4_K_M | Real verified Apache-2.0 model revision; exact Q4_K_M file exists and is documented for llama.cpp. | Model/runtime fit is sound and 2.5-GB weights are plausible for 16-GB CPU use, subject to context/KV/RSS corpus gate. The written truncated revision is not a valid reproducible pin (VF-1). |

## Gate close conditions

1. Replace the two model rows with full commit, filename, artifact SHA-256, size, license and runtime parameters.
2. Select and state an enforceable llama model load/unload lifecycle, then record peak RSS under the 16-GB corpus gate.
3. Bind Python's runtime SQLite to 3.53.4/FTS5 and add startup checks plus a local-filesystem requirement.
4. Pin the FFmpeg build recipe/configuration and both system-FFmpeg and PyAV-bundled library provenance.

Once those four corrections land, no remaining named-version incompatibility blocks this architecture.

## Recheck

**Verdict:** **PASS**  
**Remaining:** Critical 0 / High 0

- **VF-1 closed:** both candidates now carry full Hugging Face revisions, exact artifact filenames and verified SHA-256 values; Whisper correctly distinguishes the FP16 CT2 artifact from CPU `computeType=int8`.
- **VF-2 closed:** AD-12 assigns exclusive residency to `LocalResourceCoordinator`, requires confirmed ASR release, and runs pinned `llama-server` as a summary-stage child that is terminated afterward; the topology matches this lifecycle.
- **VF-3 closed:** the stack binds Python to SQLite 3.53.4 with FTS5/WAL startup assertions and rejects known network filesystems, preserving WAL's same-host/local-filesystem premise.
- **VF-4 closed:** AD-14 and the release convention require source/checksum/license provenance, image digests, FFmpeg build flags/codecs, and separate PyAV-bundled FFmpeg provenance in the release manifest/SBOM.

No critical or high version/fit blocker remains in the focused scope.
