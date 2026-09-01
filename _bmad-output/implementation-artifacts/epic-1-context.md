# Epic 1 Context: Безопасная настройка обработки

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Дать владельцу воспроизводимо запускаемое локальное приложение, где транскрибация и суммаризация независимо настраиваются для локального или внешнего выполнения, готовность движков проверяется заранее, а получатель и состав передаваемых данных понятны до внешнего запуска. Эпик создаёт основу обработки без скрытого fallback, постоянного хранения секретов и неявного сетевого доступа.

## Stories

- Story 1.1: Запуск локального приложения из воспроизводимого каркаса
- Story 1.2: Доступная адаптивная оболочка приложения
- Story 1.3: Создание независимого Профиля обработки
- Story 1.4: Настройка и проверка внешнего движка
- Story 1.5: Подготовка и проверка локальных движков
- Story 1.6: Просмотр границы данных и подтверждение передачи
- Story 1.7: Безопасная диагностика и самостоятельное обслуживание

## Requirements & Constraints

- Профиль независимо хранит две stage-конфигурации и поддерживает все четыре сочетания local/provider, язык Саммари и редактируемые инструкции с возвратом встроенных значений. Режим, движок и модель автоматически не заменяются.
- Provider probe использует display name, HTTPS endpoint, model ID и session secret и различает ready, limited compatibility, invalid credentials, unreachable service, incompatible API и missing model. Транскрибация без сегментов с таймкодами непригодна для evidence-required профиля.
- Секрет существует только в runtime; он запрещён в конфигурационных файлах, БД, заданиях, событиях, CLI, DTO, экспорте и логах. После restart показывается «Ожидается ключ»; диагностика не содержит секрет, полный пользовательский content или provider payload.
- Local readiness учитывает pinned revision/checksum, память и CPU/int8 baseline на 16 ГБ; ускоритель необязателен, одновременно резидентна одна тяжёлая модель. Кандидаты: Whisper large-v3-turbo CT2 и Qwen3-4B-GGUF Q4_K_M. После подготовки моделей local stage не создаёт content egress.
- До provider dispatch показываются stage, endpoint/provider, model и точный payload. Изменение stage, profile revision, endpoint origin, provider/model, категорий данных или snapshot digest инвалидирует consent proof; согласия этапов независимы, Cancel/Escape не создаёт dispatch. Local-to-provider fallback запрещён; auth/validation/missing-model не повторяются автоматически, ambiguous outcome требует явного attempt.
- Baseline работает через Docker Compose на Linux/macOS/Windows, слушает только loopback и не использует CDN, remote assets или telemetry. Clean-host запуск без моделей — до 20 минут; Chromium/Firefox, secret leakage и accessibility входят в release gates.

## Technical Decisions

- Архитектура — гексагональный модульный монолит. Seed: `backend/src/meeting_app/{modules,platform,entrypoints,bootstrap}`, `frontend/src/{app,features}`, `migrations`, `deploy`. Entry points → application → domain/ports; adapters реализуют ports, Профили принадлежат `profiles`.
- Стек pinned: Python 3.13.15, FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.1, SQLite 3.53.4 FTS5/WAL, React 19.2.7, Ant Design 6.6.2, TypeScript 6.0.3, Vite 8.2.2, Node.js 24.20.0 LTS, Compose 5.4.0. Release включает Apache-2.0, NOTICE, SBOM, revisions, checksums и licenses.
- REST API — `/api/v1`, OpenAPI — единственный источник client/DTO; IDs — UUIDv7, время — RFC 3339 UTC, ошибки — RFC 9457 с `code`, `stage`, `retryable`; Python/DB — `snake_case`, TypeScript/JSON — `camelCase`.
- `TranscriptionEngine` и `SummarizationEngine` — отдельные typed ports; `SecretProvider` — memory-only broker с single-use grants. Compose разделяет `app`, `local-worker`, stateless `provider-worker`, `model-fetch`; egress получают только два последних, provider-worker не монтирует постоянные данные. Модель публикуется `staging → ready` после checksum/license проверки.

## UX & Interaction Patterns

- UI использует только Ant Design 6 через `ConfigProvider → App → product routes`, русскую locale, системную тему и tokens. CSS, styled wrappers, internal selectors и visual `styles`/`classNames` запрещены; no-CSS feasibility проверяется до первого frontend feature merge.
- Симметричные `profile-stage-card` показывают mode, engine, model, readiness, data category и privacy boundary. Формы сохраняют допустимый ввод, имеют постоянные labels и связанные ошибки; несохранённые изменения требуют подтверждения выхода.
- `consent-dialog` точно называет получателя и payload, делает фон inert и возвращает фокус; confirm не фокусируется первым. `diagnostic-panel` показывает только безопасные metadata и следующее действие.
- Оболочка соответствует WCAG 2.2 AA, работает с клавиатуры и reduced motion, не кодирует статус только цветом и не имеет горизонтального scroll при 200% zoom/320 CSS px. Ниже 900 px навигация становится доступным overlay.

## Cross-Story Dependencies

- Stories 1.1–1.2 создают общий architecture/API/release/UI foundation.
- Story 1.3 задаёт Профиль для probe 1.4, readiness 1.5 и consent 1.6; проверки не меняют выбранный режим.
- Story 1.6 поставляет consent proof для provider execution в Story 2.7; dispatch без актуального proof и runtime-секрета запрещён.
- Story 1.7 объединяет health, profile, model-fetch и provider-probe states; diagnostic codes и redaction должны быть согласованы ранее.
