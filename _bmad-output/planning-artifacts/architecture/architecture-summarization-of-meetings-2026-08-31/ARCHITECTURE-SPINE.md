---
name: summarization-of-meetings
type: architecture-spine
purpose: build-substrate
altitude: initiative
paradigm: hexagonal modular monolith with durable staged pipeline
scope: MVP локального приложения для суммаризации рабочих встреч
status: final
created: 2026-08-31
updated: 2026-08-31
binds:
  - FR-1..FR-21
  - NFR-1..NFR-10
  - SM-2..SM-6
sources:
  - ../../prds/prd-summarization-of-meetings-2026-08-31/prd.md
  - ../../prds/prd-summarization-of-meetings-2026-08-31/addendum.md
companions: []
---

# Architecture Spine — summarization-of-meetings

## Design Paradigm

**Гексагональный модульный монолит с сохраняемым staged pipeline.** Доменные модули: `meetings`, `profiles`, `processing`, `search_export`; интеграции находятся в `platform`; HTTP API и workers — сменные entrypoints одного application core.

```mermaid
flowchart LR
  UI[frontend] --> HTTP[HTTP entrypoint]
  HTTP --> APP[application]
  LOCAL[local worker] --> APP
  PROVIDER[provider worker] --> APP
  APP --> DOMAIN[domain]
  APP --> PORTS[ports]
  ADAPTERS[platform adapters] --> PORTS
  BOOT[composition root] --> HTTP
  BOOT --> LOCAL
  BOOT --> PROVIDER
  BOOT --> ADAPTERS
```

## Invariants & Rules

### AD-1 — [ASSUMPTION] Направление зависимостей

- **Binds:** all
- **Prevents:** циклы между возможностями и проникновение SQLite, файлов, HTTP и provider SDK в domain.
- **Rule:** entrypoints зависят от application; application — только от domain и ports; adapters реализуют ports; модули вызывают только публичные application-команды и запросы друг друга.

### AD-2 — [ADOPTED] Владение постоянными данными

- **Binds:** FR-1–4, FR-10–18, NFR-4
- **Prevents:** двух владельцев данных, битые ссылки и частично опубликованные результаты.
- **Rule:** SQLite — источник истины для структурированного состояния; управляемая файловая область — для media, artifacts и models. БД хранит относительный artifact ID, размер, checksum и `pending|ready|deleting`. Staging и final находятся на одном filesystem: DB фиксирует `pending`, idempotent rename публикует файл, CAS переводит его в `ready`; reads видят только `ready`. Startup reconciliation завершает либо очищает `pending`, `deleting` и orphans.

### AD-3 — [ADOPTED] Сохраняемая state machine обработки

- **Binds:** FR-13–15, NFR-2–5
- **Prevents:** дубли обработки, потерю прогресса и повтор уже успешных этапов.
- **Rule:** `ProcessingJob` проходит `prepare → transcribe → summarize`; у `Meeting` не более одного активного job. Каждая lease повышает `leaseEpoch`; heartbeat, checkpoint и completion делают CAS по `(attemptId, leaseEpoch, running)`. Stage становится `succeeded` только в одной SQLite-транзакции с authoritative output и FTS, когда file outputs уже `ready`; recovery возобновляет первый незавершённый stage. Retry инвалидирует downstream и создаёт новую попытку выбранного этапа; cancel проверяется в безопасных точках. Старые attempts хранят audit metadata, но не payload/checkpoints.

### AD-4 — [ADOPTED] Независимые контракты движков

- **Binds:** FR-5–10, FR-16–18
- **Prevents:** ложную взаимозаменяемость ASR и LLM и скрытый fallback.
- **Rule:** `TranscriptionEngine` и `SummarizationEngine` — отдельные typed ports. `ProcessingProfile` содержит независимые stage configs: `engineKind`, endpoint identity, model ID/revision/checksum, parameters, capability/adapter versions и optional `secretRef`; все четыре local/provider комбинации поддерживаются. Save profile и start job проверяют capabilities; evidence flow требует timestamped segments. Job snapshot также фиксирует languages и instructions/template revision, а worker читает только его; secret value исключён. Adapter нормализует ошибки; автоматическая замена запрещена.

### AD-5 — [ASSUMPTION] Топология и граница egress

- **Binds:** FR-6–7, SM-5, NFR-1, NFR-7–8
- **Prevents:** исходящий трафик локального этапа и случайную публикацию UI в LAN.
- **Rule:** Compose содержит `app`, `local-worker`, stateless `provider-worker` и одноразовый `model-fetch`. `app`/`local-worker` имеют только internal network; `provider-worker` подключён к ней и отдельной egress network, но не монтирует SQLite, meeting-data или models. Host port слушает только `127.0.0.1`/`::1`; bundle не использует CDN, telemetry или remote assets. Versioned generated RPC contract фиксирует TLS, workload auth, streaming и compatibility; любой non-loopback provider origin требует HTTPS с certificate/hostname validation. Envelope содержит `dispatchId`, attempt/lease epoch, stage, input fingerprint, snapshot digest, consent proof и opaque grant. `consentProof` связывает accepted time/policy version с digest от stage, profile revision, endpoint origin, provider/model, data categories и snapshot; любое изменение инвалидирует proof. Payload allowlist: prepared audio + language/config либо current transcript chunks + instructions/config. `dispatchId` at-most-once: replay возвращает cached result/`outcomeUnknown`, но не вызывает provider повторно.

### AD-6 — [ASSUMPTION] Секреты живут только в runtime

- **Binds:** FR-5, FR-7, NFR-1, NFR-5
- **Prevents:** сохранение ключей в DB, jobs, export или logs.
- **Rule:** `SecretProvider` port за memory-only broker разрешает `secretRef` только по single-use opaque attempt grant; TTL не длиннее stage lease, revoke происходит при completion, cancel и restart. Ключ вводится для текущей UI-session либо передаётся launcher-у через stdin и существует только в памяти app/provider attempt. Он запрещён в Compose YAML/env-file, DB, job/event, CLI args, durable queue и logs; restart переводит попытку в `waitingForSecret`. OS keychain — отдельное будущее решение.

### AD-7 — [ADOPTED] Provenance переживает редактирование

- **Binds:** FR-10–12, FR-16–18, FR-20–21, SM-3–4
- **Prevents:** непроверяемое саммари после изменения расшифровки.
- **Rule:** `Transcript` имеет возрастающую `revision`; validator требует unique IDs, `0 ≤ startMs < endMs ≤ mediaDuration`, стабильный порядок и отсутствие chunk duplicates. `EvidenceRef` обязан разрешаться в segment той же revision. `Summary` хранит source revision, job-snapshot digest, `generatedAt`, `manualEdit`; edit делает его `stale`, unresolved evidence — `unverified`. Невалидный output не завершает stage. Полная manual replacement требует подтверждения и revision precondition; постоянна только текущая версия.

### AD-8 — [ASSUMPTION] Структурированная суммаризация

- **Binds:** FR-16–18, SM-4
- **Prevents:** несовместимые свободные ответы моделей и потерю provenance на длинных встречах.
- **Rule:** pipeline передаёт модели сегменты со стабильными IDs, извлекает типизированные candidates по token-budget chunks, сводит только candidates вместе с evidence IDs и проверяет итог доменной JSON Schema. Только валидатор записывает `Summary`.

### AD-9 — [ASSUMPTION] Локальный полнотекстовый поиск

- **Binds:** FR-3, FR-19, NFR-1–2
- **Prevents:** внешний поиск, расходящиеся индексы и отдельную поисковую инфраструктуру.
- **Rule:** SQLite FTS5 индексирует title, текущие `Segment` и текущий `Summary` в транзакции их публикации. MVP использует lexical search без embeddings; hit содержит meeting, тип совпадения и локальный snippet. Результаты имеют bounded pagination; индекс детерминированно rebuild/repair-ится из authoritative tables и проходит release benchmark под compute load.

### AD-10 — [ASSUMPTION] Обновление, backup и restore

- **Binds:** FR-2, FR-4, FR-14, NFR-4, NFR-8
- **Prevents:** несовместимую схему после обновления и backup без соответствующих media.
- **Rule:** Alembic имеет один linear forward-only head. До API/workers migration gate берёт persisted exclusive maintenance lock, запрещает mutations/new leases, drain/cancel-ит workers, проверяет место и создаёт backup во временной generation. Manifest перечисляет DB snapshot и точные artifacts/checksums и атомарно получает `complete`; только затем идёт migration. Ошибка не запускает services. Restore разворачивает и проверяет новую generation, затем одним recoverable atomic pointer switch активирует её; rollback запускает pinned совместимую версию приложения.

### AD-11 — [ASSUMPTION] Единый внешний контракт

- **Binds:** all UI/API capabilities, NFR-2, NFR-5–6
- **Prevents:** расхождение frontend/backend DTO и нестабильные форматы.
- **Rule:** REST JSON API живёт под `/api/v1`; OpenAPI — единственный источник frontend client/DTO. SSE cursor — persisted monotonic revision per job, event — replaceable state snapshot; reconnect отдаёт последующие revisions либо current `resync` при gap/pruning, клиент игнорирует stale revisions, terminal state доступен через REST. IDs — UUIDv7, время — RFC 3339 UTC, offsets — integer ms; ошибки — RFC 9457 со stable `code`, `stage`, `retryable`.

### AD-12 — [ASSUMPTION] Ресурсный и модельный baseline

- **Binds:** FR-6, FR-9–10, FR-16–17, NFR-2–3, SM-2–5
- **Prevents:** одновременную загрузку моделей сверх 16 ГБ и неповторяемое качество.
- **Rule:** `LocalResourceCoordinator` владеет exclusive model-residency lease. После transcription `local-worker` выгружает ASR, подтверждает освобождение памяти, запускает pinned `llama-server` как child; после summary завершает его. Одновременно resident одна heavy model; gate измеряет peak RSS всего Compose. CPU/int8 runtime — baseline, accelerator — optional profile. Начальные candidates: Whisper large-v3-turbo CT2 и Qwen3-4B-GGUF Q4_K_M.

### AD-13 — [ASSUMPTION] Импорт — одна атомарная команда

- **Binds:** FR-1, SM-2, NFR-2, NFR-4
- **Prevents:** job для невалидного media, частичный импорт и загрузку файла целиком в RAM.
- **Rule:** intake command stream-ит media в staging, затем `ffprobe` проверяет container, audio track, decodability и продуктовые лимиты. Только после успеха одна транзакция создаёт `Meeting`/`MediaArtifact`, а rename публикует файл; при rejection staging очищается, `ProcessingJob` не создаётся.

### AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate

- **Binds:** NFR-3, NFR-7–10, SM-2–5
- **Prevents:** выпуск непереносимого baseline и артефактов с неясными правами.
- **Rule:** release проходит Linux/macOS/Windows × 16-GB CPU, corpus quality/resource gates, Chromium/Firefox keyboard/labels/non-color checks, one-screen happy path и clean-host Compose install ≤20 min без model download. Корневой код — Apache-2.0; NOTICE, SBOM и manifest фиксируют image/runtime/model/source/checksum/license, FFmpeg build flags/codecs и PyAV-bundled FFmpeg provenance. Провал gate заменяет candidate за AD-4 port.

### AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts

- **Binds:** NFR-2–5, SM-2
- **Prevents:** формально корректное, но блокирующее UI приложение.
- **Rule:** API не исполняет compute; import/provider upload — streaming; list/search — bounded и paginated. Под активным local job release benchmarks требуют: library/navigation ≤2 s на 1000 meetings, p95 UI/API response ≤1 s, persisted progress/heartbeat ≤5 s, cancel safe point ≤10 s.

## Consistency Conventions

| Concern | Convention |
| --- | --- |
| Naming | Python/DB — `snake_case`; TypeScript/JSON — `camelCase`; types/entities — `PascalCase`; IDs — lowercase UUIDv7. |
| Data | UTF-8; UTC RFC 3339; media time — integer ms; file paths relative to managed root; exports include model, manual/stale/unverified markers. |
| Mutation | UI вызывает application commands; один transaction boundary на command или stage checkpoint; adapters не меняют domain state напрямую. |
| Errors and retry | RFC 9457 + stable code. До двух автоматических provider retries разрешены только при доказанном `not accepted` либо provider idempotency; ambiguous outcome → `outcomeUnknown` и явный новый attempt. Auth, validation и missing model не повторяются. |
| Events | SSE events подчиняются cursor/resync contract AD-11 и несут job, stage, state и optional progress. |
| Logging | Structured local logs: correlation/job/stage/error metadata; без secrets, полного transcript, summary и provider payloads. |
| Config | Несекретные значения: environment → checked-in defaults. Секреты подчиняются AD-6. Неизвестная переменная или model/profile ID вызывает fail-fast. Frontend CSP разрешает соединения только с `self`; remote assets запрещены. |
| Release | Images pin-ятся digest; SBOM, NOTICE, checksums, model/runtime revisions и лицензии входят в release manifest; gates подчиняются AD-14–15. |

## Stack

| Name | Version |
| --- | --- |
| [Python](https://www.python.org/downloads/release/python-31315/) | 3.13.15 |
| [FastAPI](https://github.com/fastapi/fastapi/releases/tag/0.141.1) | 0.141.1 |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/releases/tag/rel_2_0_52) | 2.0.52 |
| [Alembic](https://github.com/sqlalchemy/alembic/releases/tag/rel_1_19_1) | 1.19.1 |
| [SQLite](https://www.sqlite.org/releaselog/3_53_4.html) | Python linked to 3.53.4 + FTS5 + WAL; startup asserts version/options; known network filesystems rejected |
| [FFmpeg](https://ffmpeg.org/download.html) | 9.0.1 |
| [React](https://react.dev/versions) | 19.2.7 |
| [TypeScript](https://github.com/microsoft/TypeScript/releases/tag/v6.0.3) | 6.0.3 |
| [Vite](https://github.com/vitejs/vite/releases/tag/v8.2.2) | 8.2.2 |
| [Node.js](https://nodejs.org/en/download) | 24.20.0 LTS; build only |
| [Docker Compose](https://docs.docker.com/desktop/release-notes/) | 5.4.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper/releases/tag/v1.2.1) | 1.2.1 |
| [llama.cpp](https://github.com/ggml-org/llama.cpp/releases/tag/v0.3.0) | 0.3.0 |
| [Whisper large-v3-turbo CT2](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo) | `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf/model.bin`; SHA-256 `e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da`; FP16 artifact, CPU `computeType=int8` |
| [Qwen3-4B-GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF) | `bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q4_K_M.gguf`; SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` |

## Structural Seed

```text
summarization-of-meetings/
  backend/src/meeting_app/
    modules/                 # meetings, profiles, processing, search_export
    platform/                # sqlite, filesystem, engines, media, HTTP
    entrypoints/             # API, local worker, provider worker, maintenance CLI
    bootstrap/               # composition roots only
  frontend/src/features/     # UI slices consuming the generated API client
  migrations/                # one linear Alembic history
  deploy/                    # Compose, images, model/release manifests
```

```mermaid
flowchart LR
  BROWSER[Browser] -->|loopback| APP[app: UI + API + credential broker]
  APP --> DATA[(SQLite + meeting data volume)]
  LOCAL[local-worker] --> DATA
  APP -->|stage envelope / result RPC| PROVIDER[provider-worker]
  LOCAL --> ASR[faster-whisper in-process]
  LOCAL --> LLM[llama-server child; on demand]
  PROVIDER -->|explicit stage only| EXTERNAL[OpenAI-compatible providers]
  APP -. attempt grant / runtime secret .-> PROVIDER
  FETCH[model-fetch] --> REGISTRY[model registry]
  FETCH --> MODELS[(model cache)]
  LOCAL --> MODELS

  subgraph NO_EGRESS[internal network — no external route]
    APP
    LOCAL
    LLM
    DATA
    MODELS
  end
```

```mermaid
erDiagram
  MEETING ||--o{ MEDIA_ARTIFACT : owns
  MEETING ||--o| TRANSCRIPT : owns
  TRANSCRIPT ||--|{ SEGMENT : contains
  MEETING ||--o| SUMMARY : owns
  SUMMARY ||--|{ SUMMARY_ITEM : contains
  SUMMARY_ITEM ||--o{ EVIDENCE_REF : cites
  EVIDENCE_REF }o--|| SEGMENT : resolves_to
  MEETING ||--o{ PROCESSING_JOB : processes
  PROCESSING_JOB ||--|{ STAGE_ATTEMPT : checkpoints
  PROCESSING_PROFILE ||--o{ PROCESSING_JOB : snapshots
  PROCESSING_PROFILE ||--|| TRANSCRIPTION_STAGE_CONFIG : contains
  PROCESSING_PROFILE ||--|| SUMMARIZATION_STAGE_CONFIG : contains
  PROCESSING_PROFILE ||--o{ SECRET_REF : references
```

## Capability → Architecture Map

| Capability / Area | Lives in | Governed by |
| --- | --- | --- |
| FR-1–4 — import, library, retention | `meetings`, filesystem/media adapters | AD-2, AD-10, AD-13 |
| FR-5–8 — profiles and privacy boundary | `profiles`, engine adapters, credential broker | AD-4–6 |
| FR-9–12 — transcription and editing | `processing`, `meetings`, media/ASR adapters | AD-2–4, AD-7, AD-12 |
| FR-13–15 — durable jobs | `processing`, worker entrypoints | AD-3, AD-5 |
| FR-16–18 — summary and evidence | `meetings`, `processing`, LLM adapters | AD-4, AD-7–8, AD-12 |
| FR-19–21 — search and export | `search_export` | AD-7, AD-9, conventions |
| NFR-1–10 — operations and delivery | `platform`, `entrypoints`, `deploy` | AD-2–6, AD-10–15 |

## Deferred

- **Promotion of local model candidates:** выполнить AD-14 gates до `local processing` feature complete; заменить candidate за AD-4 port при любом провале.
- **Automatic diarization:** keep speaker labels in the domain contract, but choose a local diarization adapter only after ASR baseline and license/resource tests pass.
- **GPU/Metal/DirectML tuning:** CPU remains the supported baseline; add accelerator profiles only after per-OS measurements, without changing domain or provider contracts.
- **ASR chunk overlap/dedup algorithm:** owned wholly by the transcription adapter; fix it when corpus tests expose the required accuracy/performance trade-off.
- **UI component library, detailed schema, SQL indexes outside FTS5, prompt wording:** code-owned unless a cross-module incompatibility appears.
- **Remote exposure, authentication, multi-user data ownership, native packages, semantic search and plugin catalog:** outside MVP; require a higher-altitude architecture update.
- **OS keychain integration:** runtime broker по AD-6 остаётся baseline; выбрать portable keychain adapter только отдельным решением после проверки трёх ОС.
- **Fast-path assumption revisit gates:** AD-1 — dependency test до первого module merge; AD-5/6 — threat/data-flow и secret-restart tests до provider flow; AD-8 — schema/corpus fixtures до summarization; AD-9 — 1000-meeting benchmark under load до search complete; AD-10 — restore drill до первой migration; AD-11 — OpenAPI/SSE reconnect tests до frontend integration; AD-12 — corpus/peak-RSS до local processing complete; AD-13 — crash injection до intake release; AD-14/15 — OS/license/SBOM/performance gates до первого public release.
