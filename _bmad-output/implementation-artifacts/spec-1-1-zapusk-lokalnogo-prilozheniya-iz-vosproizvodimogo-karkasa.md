---
title: 'Story 1.1: Запуск локального приложения из воспроизводимого каркаса'
type: 'feature'
created: '2026-09-01'
status: 'done'
review_loop_iteration: 0
baseline_commit: '5369b556373753d2458909e6edc0bbd8e66680e0'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** В репозитории нет запускаемого приложения, воспроизводимых зависимостей, API-контракта, проверки хранилища и Compose-пути установки.

**Approach:** Создать рабочий monorepo seed: FastAPI health/problem-details API и SQLite preflight, React/Vite frontend, loopback-only Compose, документацию, лицензию и автоматические gates.

## Boundaries & Constraints

**Always:** Соблюдать `entrypoints → application → domain/ports`, точные pins, frozen `uv`/`pnpm` locks; выполнять preflight до product DB; публиковать API только на loopback; считать OpenAPI единственным источником frontend DTO; использовать RFC 3339 UTC/RFC 9457; собираться без моделей, CDN, telemetry и remote assets.

**Ask First:** Изменение pins, публичного интерфейса, Apache-2.0, границ модулей или ослабление gates.

**Never:** Сохранять секреты; создавать product DB до preflight; маскировать отсутствие FTS5/WAL или network filesystem; добавлять фиктивные workers/models, handwritten DTO или BMAD runtime dependencies.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Чистый запуск | Docker, локальный volume | Compose поднимает loopback app без моделей; health=`ready` | До startup health остаётся unhealthy |
| Контракт API | Health или неизвестный API route | Versioned JSON/OpenAPI, UTC, CSP | RFC 9457 + stable `code/stage/retryable` |
| Плохое хранилище | Неверная SQLite/FTS5/WAL или NFS/SMB/CIFS | Выход до schema/ready | Безопасный код; probe удалён |
| Frontend build | Production build | Только локальный bundle | Gate блокирует remote URL/telemetry |

</frozen-after-approval>

## Code Map

- `.gitignore`, `.dockerignore`, `.env.example` — сохранить BMAD ignores; исключить secrets/data/models/build; example только несекретный.
- `backend/pyproject.toml`, `backend/uv.lock`, `.python-version` — Python 3.13.15, exact runtime/tool pins и locks.
- `backend/src/meeting_app/bootstrap/app.py`, `entrypoints/http/**` — composition root, `/api/v1`, OpenAPI, RFC 9457 и CSP.
- `backend/src/meeting_app/platform/storage/sqlite_preflight.py` — same-volume file probe SQLite 3.53.4/FTS5/WAL и инъецируемый filesystem detector.
- `backend/src/meeting_app/{modules,platform,entrypoints,bootstrap}`, `migrations/` — реальный seed и Alembic basis.
- `frontend/{package.json,pnpm-lock.yaml,vite.config.ts,tsconfig*.json,src/app,src/features}` — pinned минимальный локальный bundle.
- `compose.yaml`, `deploy/app.Dockerfile` — multi-stage image, named volume, healthcheck, loopback bind; без моделей.
- `README.md`, `LICENSE`, `NOTICE`, `deploy/release/manifest.json` — запуск, каталоги, update/backup/restore основы, Apache-2.0 и inventory.
- `backend/tests/**`, `tests/release/**`, `.github/workflows/ci.yml` — gates для architecture/API/preflight/pins/assets/Compose.
- `_bmad-output/planning-artifacts/**` — read-only пользовательские артефакты; не изменять в этой истории.

## Tasks & Acceptance

**Execution:**
- [x] Root/deploy files из Code Map — создать безопасный Compose/build/release baseline и документацию без model download.
- [x] `backend/` и `migrations/` — создать installable hexagonal seed, FastAPI API и storage preflight до durable state.
- [x] `frontend/` — создать pinned минимальный build без handwritten DTO и внешних сетевых зависимостей.
- [x] `backend/tests/**`, `tests/release/**`, `.github/workflows/ci.yml` — закрепить все I/O edge cases и architecture/release contracts исполняемыми проверками.

**Acceptance Criteria:**
- Given чистый clone на Linux/macOS/Windows с Docker Compose, when выполняется документированная команда без моделей, then app становится доступным через loopback URL и non-loopback публикация отсутствует.
- Given запущенный baseline, when запрашиваются health, OpenAPI и ошибочный API route, then ответы соответствуют versioned JSON, RFC 3339 UTC и RFC 9457, а security headers разрешают соединения только к `self`.
- Given исходный код, when выполняются frozen build/test/architecture gates, then structural seed существует, запрещённые обратные импорты обнаруживаются, а frontend bundle не содержит remote assets/CDN/telemetry.
- Given несовместимая SQLite capability или filesystem, when начинается startup, then приложение fail-fast завершается до product DB/schema/ready-state и выдаёт безопасный стабильный код.
- Given release inventory, when проверяются pins и licensing, then утверждённые версии, Apache-2.0, NOTICE, безопасный example config и digest-ready image references подтверждены автоматически.

## Spec Change Log

## Design Notes

Probe использует временный файл на целевом volume, реальный FTS5 DDL и `journal_mode=wal`, затем очищается. Инъецируемый filesystem detector позволяет тестировать denylist без NFS mount. OpenAPI экспортируется без lifespan.

## Verification

**Commands:**
- `docker build --target backend-verify --file deploy/app.Dockerfile .` — pinned Python 3.13.15/SQLite 3.53.4 stage устанавливает frozen dev closure и выполняет pytest с `backend/pyproject.toml`, Ruff с `ruff.toml`, strict mypy с `backend/pyproject.toml`, release/inventory и generated-bundle gates; локальная загрузка interpreter через `uv` не требуется.
- `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend test && pnpm --dir frontend build` — frontend воспроизводимо собирается без remote assets.
- `test "$(docker compose version --short)" = "5.4.0" && docker compose config && docker compose up --build --wait && curl --fail http://127.0.0.1:8000/api/v1/health && curl --fail http://127.0.0.1:8000/` — exact Compose baseline собирается и health/UI доступны на loopback; после smoke выполняется `docker compose down --volumes --remove-orphans`.

## Suggested Review Order

**Startup и граница хранения**

- Composition root допускает ready-state только после безопасной инициализации.
  [`app.py:54`](../../backend/src/meeting_app/bootstrap/app.py#L54)

- Same-volume probe закрывает SQLite, FTS5, WAL и filesystem edge cases.
  [`sqlite_preflight.py:184`](../../backend/src/meeting_app/platform/storage/sqlite_preflight.py#L184)

- Staging и atomic replace не публикуют частично мигрированную базу.
  [`database.py:54`](../../backend/src/meeting_app/platform/storage/database.py#L54)

- Preflight всегда предшествует durable database initialization.
  [`storage.py:15`](../../backend/src/meeting_app/bootstrap/storage.py#L15)

**API и пользовательский baseline**

- Versioned router задаёт health и типизированный problem media contract.
  [`router.py:8`](../../backend/src/meeting_app/entrypoints/http/router.py#L8)

- Единые handlers сохраняют RFC 9457 для ожидаемых и неожиданных ошибок.
  [`problems.py:39`](../../backend/src/meeting_app/entrypoints/http/problems.py#L39)

- Security middleware ограничивает browser network boundary значением `self`.
  [`security.py:9`](../../backend/src/meeting_app/entrypoints/http/security.py#L9)

- Generated DTO, timeout и runtime validation защищают frontend health path.
  [`client.ts:56`](../../frontend/src/api/client.ts#L56)

- Health surface показывает ready/error и следует системной теме.
  [`HealthPanel.tsx:11`](../../frontend/src/features/health/HealthPanel.tsx#L11)

**Воспроизводимость и поставка**

- Compose публикует единственный app только на IPv4 loopback.
  [`compose.yaml:3`](../../compose.yaml#L3)

- Pinned backend verification отделяет exact runtime от host toolchain.
  [`app.Dockerfile:42`](../../deploy/app.Dockerfile#L42)

- Runtime image объединяет проверенный backend, SQLite и локальный frontend bundle.
  [`app.Dockerfile:73`](../../deploy/app.Dockerfile#L73)

- Inventory выводится детерминированно из обоих lock-файлов.
  [`generate_inventory.py:212`](../../deploy/release/generate_inventory.py#L212)

- Трёхплатформенные gates и exact Compose smoke закреплены в CI.
  [`ci.yml:10`](../../.github/workflows/ci.yml#L10)

- Документация проводит пользователя через запуск и переносимый backup/restore.
  [`README.md:7`](../../README.md#L7)

**Доказательства**

- HTTP suite проверяет RFC 9457, OpenAPI, static serving и startup wiring.
  [`test_http_contract.py:29`](../../backend/tests/test_http_contract.py#L29)

- Storage suite проверяет fail-closed detection и non-masking cleanup.
  [`test_sqlite_preflight.py:21`](../../backend/tests/test_sqlite_preflight.py#L21)

- Architecture suite ловит абсолютные, относительные и package-alias нарушения.
  [`test_architecture.py:68`](../../backend/tests/test_architecture.py#L68)

- Release suite блокирует stale inventory и remote production assets.
  [`test_release_contracts.py:20`](../../tests/release/test_release_contracts.py#L20)
