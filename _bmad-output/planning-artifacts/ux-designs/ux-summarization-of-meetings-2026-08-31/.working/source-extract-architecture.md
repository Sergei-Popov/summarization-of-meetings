# UX-релевантное извлечение из Architecture Spine

Источник: `_bmad-output/planning-artifacts/architecture/architecture-summarization-of-meetings-2026-08-31/ARCHITECTURE-SPINE.md`

Правило извлечения: ниже зафиксированы только архитектурные факты, которые UX должен отразить, объяснить или сознательно скрыть. Новые UX-решения не добавлены.

## Поверхности и форм-фактор

- MVP — локальное приложение с браузерным frontend, который обращается к UI/API только через loopback. Порт слушает `127.0.0.1`/`::1`; удалённая публикация интерфейса в LAN не входит в архитектуру. — Источник: **Design Paradigm**; **AD-5 — [ASSUMPTION] Топология и граница egress**; **Structural Seed**.
- Поддерживаемая release-матрица охватывает Linux, macOS и Windows на 16-ГБ CPU-машинах. Native packages не входят в MVP; архитектура описывает web UI, запускаемый через Docker Compose. — Источник: **AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate**; **Deferred**.
- Release gate проверяет Chromium и Firefox, клавиатурное управление, labels, non-color checks и one-screen happy path. — Источник: **AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate**.
- UI component library архитектурой не выбрана и отложена в code-owned решения. — Источник: **Deferred**.
- Пользовательские области возможностей, уже закреплённые архитектурой: импорт и библиотека встреч; профили обработки и privacy boundary; расшифровка и редактирование; фоновые задания; саммари и evidence; поиск и экспорт. — Источник: **Capability → Architecture Map**.

## Интеграции и границы подключения

- Обработка допускает четыре независимые комбинации: local/provider для транскрипции и local/provider для суммаризации. ASR и LLM имеют разные конфигурации и capabilities; сохранение профиля и запуск задания валидируют совместимость. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**.
- Автоматическая подмена выбранного движка запрещена. Ошибки адаптеров нормализуются, но fallback между local и provider не происходит скрыто. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**.
- Внешняя интеграция предусмотрена с OpenAI-compatible providers и выполняется только через отдельный stateless `provider-worker`; тот не имеет доступа к SQLite, meeting-data или локальным моделям. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Structural Seed**.
- Для любого non-loopback provider endpoint обязательны HTTPS и проверка certificate/hostname. Любое изменение stage, revision профиля, endpoint origin, provider/model, категорий данных или job snapshot инвалидирует ранее данное согласие на отправку. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**.
- Наружу разрешены только данные конкретного явно выбранного этапа: prepared audio и language/config для транскрипции либо текущие transcript chunks и instructions/config для суммаризации. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**.
- Локальные движки: ASR через faster-whisper и LLM через запускаемый по требованию llama-server. Модели скачивает отдельный одноразовый `model-fetch`; UI/app и local worker внешнего маршрута не имеют. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **AD-12 — [ASSUMPTION] Ресурсный и модельный baseline**; **Structural Seed**.
- Bundle не использует CDN, telemetry или remote assets; frontend CSP разрешает соединения только с `self`. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Consistency Conventions / Config**.

## Роли, права и область владения

- Remote exposure, authentication и multi-user data ownership явно находятся вне MVP. Архитектура не задаёт роли пользователей, матрицу разрешений или совместное владение встречами. — Источник: **Deferred**.
- Доменное состояние может меняться только через application commands; frontend и platform adapters не меняют его напрямую. — Источник: **Consistency Conventions / Mutation**.
- Полная ручная замена transcript требует явного подтверждения и проверки ожидаемой revision; постоянной остаётся только текущая версия. — Источник: **AD-7 — [ADOPTED] Provenance переживает редактирование**.

## Фоновая обработка, streaming и наблюдаемые состояния

- Обработка — сохраняемая state machine со стадиями `prepare → transcribe → summarize`; у одной встречи может быть не более одного активного job. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**.
- После сбоя recovery продолжает с первого незавершённого stage и не повторяет уже успешно завершённые стадии. Старые attempts сохраняют только audit metadata, без payload и checkpoints. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**.
- Retry выбранного этапа инвалидирует downstream-результаты и создаёт новую попытку этого этапа. Cancel применяется в безопасных точках, а release contract ограничивает достижение safe point десятью секундами. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**; **AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts**.
- Фоновая вычислительная работа не выполняется API. Import и provider upload идут streaming; UI/API должны оставаться отзывчивыми при активном local job. — Источник: **AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts**.
- Наблюдение за job идёт через SSE: события содержат job, stage, state и optional progress. Cursor — сохраняемая монотонная revision; событие является заменяемым state snapshot, а не обязательным журналом дельт. — Источник: **AD-11 — [ASSUMPTION] Единый внешний контракт**; **Consistency Conventions / Events**.
- При reconnect клиент получает последующие revisions либо текущее состояние с `resync`, если есть gap/pruning; stale revisions должны игнорироваться. Terminal state всегда доступен через REST. — Источник: **AD-11 — [ASSUMPTION] Единый внешний контракт**.
- Release contract требует сохранять progress/heartbeat не реже чем раз в пять секунд. — Источник: **AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts**.
- Секрет действует только в текущей UI-session/attempt. После restart незавершённая provider-попытка переходит в `waitingForSecret`; revoke происходит при completion, cancel и restart. — Источник: **AD-6 — [ASSUMPTION] Секреты живут только в runtime**.
- Provider dispatch имеет at-most-once семантику: replay возвращает cached result или `outcomeUnknown`, но не вызывает provider повторно. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**.
- Файловые артефакты имеют внутренние состояния `pending|ready|deleting`, однако reads видят только `ready`; startup reconciliation завершает или очищает незавершённые состояния и orphans. — Источник: **AD-2 — [ADOPTED] Владение постоянными данными**.
- При обновлении maintenance lock запрещает mutations и новые leases, затем workers drain/cancel. При ошибке migration сервисы не запускаются. — Источник: **AD-10 — [ASSUMPTION] Обновление, backup и restore**.

## Ошибки, повтор и восстановление

- API-ошибки имеют единый формат RFC 9457 со stable `code`, `stage` и `retryable`; UX может отличать этап и допустимость повтора без разбора произвольного текста. — Источник: **AD-11 — [ASSUMPTION] Единый внешний контракт**; **Consistency Conventions / Errors and retry**.
- До двух автоматических provider retries разрешены только при доказанном `not accepted` или наличии provider idempotency. При неоднозначном исходе состояние — `outcomeUnknown`, а повтор требует явной новой попытки. Auth, validation и missing model автоматически не повторяются. — Источник: **Consistency Conventions / Errors and retry**.
- Невалидный transcript/summary output не завершает stage успешно. Evidence обязан разрешаться в segment той же transcript revision. — Источник: **AD-7 — [ADOPTED] Provenance переживает редактирование**; **AD-8 — [ASSUMPTION] Структурированная суммаризация**.
- Импорт stream-ит media во временную область и до создания Meeting проверяет container, audio track, decodability и продуктовые лимиты. При rejection staging очищается, частичная встреча и ProcessingJob не создаются. — Источник: **AD-13 — [ASSUMPTION] Импорт — одна атомарная команда**.
- Backup считается годным только после атомарного `complete` manifest с DB snapshot и точными artifacts/checksums. Restore сначала проверяет новую generation и только затем переключает её; rollback требует pinned совместимую версию приложения. — Источник: **AD-10 — [ASSUMPTION] Обновление, backup и restore**.
- Неизвестная config variable или model/profile ID вызывает fail-fast. SQLite startup отвергает неподдерживаемую версию/options и известные network filesystems. — Источник: **Consistency Conventions / Config**; **Stack**.

## Offline, сеть и доступность ресурсов

- Локальный этап архитектурно не имеет исходящего сетевого маршрута. Внешний трафик разрешён только provider-worker для явно выбранного provider stage и model-fetch для получения моделей. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Structural Seed**.
- Поэтому local processing после наличия нужных моделей не зависит от provider egress, но полный продукт нельзя считать безусловно offline на этапе загрузки моделей или при выборе provider engine. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Structural Seed**.
- Clean-host Compose install должен укладываться в 20 минут без учёта загрузки моделей. — Источник: **AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate**.
- На поддерживаемом baseline одновременно в памяти находится только одна heavy model. После transcription ASR выгружается и только затем запускается локальная LLM; CPU/int8 — baseline, accelerator — optional profile. — Источник: **AD-12 — [ASSUMPTION] Ресурсный и модельный baseline**.
- Library/navigation на 1000 встреч должны укладываться в 2 секунды, p95 UI/API response — в 1 секунду даже под активной local job; list/search ограничены и paginated. — Источник: **AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts**.

## Privacy и security

- UI/API доступны только с локальной машины; remote exposure не поддерживается. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Deferred**.
- Значение provider secret существует только в памяти текущей UI-session/provider attempt. Запрещено сохранять его в Compose YAML/env-file, DB, job/event, CLI args, durable queue, export или logs. OS keychain в baseline отсутствует. — Источник: **AD-6 — [ASSUMPTION] Секреты живут только в runtime**; **Deferred**.
- Provider получает single-use opaque grant с TTL не длиннее lease этапа, а не постоянный доступ к секрету. — Источник: **AD-6 — [ASSUMPTION] Секреты живут только в runtime**.
- Отправка provider stage требует consent proof, связанного с временем принятия, версией policy, endpoint/provider/model, конкретными категориями отправляемых данных и snapshot. Изменение любой из этих составляющих требует нового consent proof. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**.
- Локальные structured logs могут содержать correlation/job/stage/error metadata, но не secrets, полный transcript, summary или provider payload. — Источник: **Consistency Conventions / Logging**.
- Export должен включать model identity и признаки `manual`, `stale`, `unverified`; secret value исключён из job snapshot и экспорта. — Источник: **Consistency Conventions / Data**; **AD-4 — [ADOPTED] Независимые контракты движков**; **AD-6 — [ASSUMPTION] Секреты живут только в runtime**.

## Accessibility и i18n

- Обязательный release baseline: Chromium/Firefox, keyboard, labels и передача смысла не только цветом. Более полный accessibility standard или WCAG target архитектура не задаёт. — Источник: **AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate**.
- Текстовые данные хранятся в UTF-8; абсолютное время — RFC 3339 UTC; offsets media — целые миллисекунды. — Источник: **Consistency Conventions / Data**.
- Языки входят в immutable job snapshot вместе с instructions/template revision; worker читает snapshot, а не последующие изменения профиля. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**.
- Evidence flow требует timestamped segments. Segment обязан иметь валидные границы `0 ≤ startMs < endMs ≤ mediaDuration`, стабильный порядок и unique IDs. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**; **AD-7 — [ADOPTED] Provenance переживает редактирование**.
- Архитектура не задаёт поддерживаемые UI-локали, язык интерфейса, форматы локального отображения даты/времени, RTL или правила pluralization. — Источник: **Architecture Spine в целом; соответствующие решения отсутствуют**.

## Данные и технические инварианты, заметные в UX

- SQLite — источник истины для структурированного состояния; media, artifacts и models лежат в управляемой файловой области. UI не должен опираться на произвольные внешние пути к артефактам. — Источник: **AD-2 — [ADOPTED] Владение постоянными данными**.
- Reads показывают только опубликованные `ready` artifacts; промежуточные `pending` и `deleting` не являются пользовательскими результатами. — Источник: **AD-2 — [ADOPTED] Владение постоянными данными**.
- Profile хранит раздельные настройки каждого stage: engine kind, endpoint identity, model ID/revision/checksum, parameters, capability/adapter versions и optional secret reference. Job фиксирует snapshot этих настроек на момент запуска. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**.
- Transcript имеет возрастающую `revision`. Summary хранит source revision, job-snapshot digest, generated time и `manualEdit`; изменение transcript делает summary `stale`, а неразрешимое evidence — `unverified`. — Источник: **AD-7 — [ADOPTED] Provenance переживает редактирование**.
- Постоянной является только текущая версия transcript; старые полные payload/checkpoints попыток не хранятся. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**; **AD-7 — [ADOPTED] Provenance переживает редактирование**.
- Structured summary создаётся только после проверки доменной JSON Schema; модель получает сегменты со стабильными IDs, а итоговые элементы сохраняют evidence IDs. — Источник: **AD-8 — [ASSUMPTION] Структурированная суммаризация**.
- MVP search — локальный lexical FTS5 без embeddings. Hit содержит meeting, тип совпадения и локальный snippet; выдача bounded и paginated. — Источник: **AD-9 — [ASSUMPTION] Локальный полнотекстовый поиск**.
- Клиентские IDs — lowercase UUIDv7; JSON использует `camelCase`. Эти значения являются контрактом API, но не обязаны показываться пользователю. — Источник: **AD-11 — [ASSUMPTION] Единый внешний контракт**; **Consistency Conventions / Naming**.
- Локальная ресурсная модель последовательно освобождает ASR перед запуском LLM; одновременное присутствие двух heavy models запрещено. Это технически ограничивает параллельность локальной обработки. — Источник: **AD-12 — [ASSUMPTION] Ресурсный и модельный baseline**.

## Неразрешённые вопросы

- Какой UI system/component library использовать: решение явно отложено. — Источник: **Deferred**.
- Как именно выглядят prompt wording и пользовательское управление инструкциями/шаблонами: архитектура фиксирует revision в snapshot, но wording оставляет code-owned. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**; **Deferred**.
- Будет ли automatic diarization и какой локальный adapter использовать: speaker labels оставлены в domain contract, выбор отложен до resource/license tests. — Источник: **Deferred**.
- Какие accelerator profiles появятся на macOS/Windows/Linux: CPU остаётся baseline, GPU/Metal/DirectML tuning отложен. — Источник: **Deferred**.
- Появится ли безопасное сохранение ключей через OS keychain: baseline требует повторного runtime-ввода, portable adapter ещё не выбран. — Источник: **AD-6 — [ASSUMPTION] Секреты живут только в runtime**; **Deferred**.
- Каким будет UX update/backup/restore и отображение maintenance/failure: архитектура задаёт состояния и запреты, но не пользовательские поверхности. — Источник: **AD-10 — [ASSUMPTION] Обновление, backup и restore**.
- Каковы конкретные продуктовые лимиты media при импорте: проверка лимитов обязательна, сами значения в spine отсутствуют. — Источник: **AD-13 — [ASSUMPTION] Импорт — одна атомарная команда**.
- Каковы поддерживаемые UI-языки и правила локализации: архитектура фиксирует encoding/time representation и processing languages, но не UI i18n. — Источник: **Consistency Conventions / Data**; **AD-4 — [ADOPTED] Независимые контракты движков**.
- Каков полный accessibility floor сверх keyboard/labels/non-color checks: конкретный стандарт не назван. — Источник: **AD-14 — [ASSUMPTION] Воспроизводимый open-source release gate**.
- Remote exposure, auth, multi-user ownership, native packages, semantic search и plugin catalog не являются открытыми деталями MVP: они исключены из scope и требуют architecture update более высокого уровня. — Источник: **Deferred**.
- Большая часть UX-значимых архитектурных решений помечена `[ASSUMPTION]` и имеет обязательные revisit gates до интеграции/релиза: threat/data-flow, secret restart, SSE reconnect, restore drill, crash injection, resource/performance, OS/license/SBOM. До прохождения gate их нельзя считать подтверждёнными реализацией. — Источник: **Deferred / Fast-path assumption revisit gates**.

## Возможные противоречия или жёсткие границы для UX

- UX постоянного «запомнить API key» противоречит memory-only baseline: после restart provider attempt становится `waitingForSecret`. — Источник: **AD-6 — [ASSUMPTION] Секреты живут только в runtime**; **Deferred**.
- Обещание автоматического fallback между local и provider либо между моделями противоречит запрету автоматической подмены движка. — Источник: **AD-4 — [ADOPTED] Независимые контракты движков**.
- Обещание мгновенной отмены противоречит safe-point cancellation: архитектурный budget допускает до 10 секунд. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**; **AD-15 — [ASSUMPTION] Операционные бюджеты — release contracts**.
- Silent retry после неоднозначного provider outcome противоречит at-most-once dispatch: `outcomeUnknown` требует явной новой попытки. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Consistency Conventions / Errors and retry**.
- Представление отредактированного transcript и старого summary как согласованных противоречит provenance: summary обязан стать `stale`, а broken evidence — `unverified`. — Источник: **AD-7 — [ADOPTED] Provenance переживает редактирование**.
- UX истории всех полных версий transcript/job payloads противоречит retention-инварианту: постоянна только текущая версия, старые attempts содержат лишь audit metadata. — Источник: **AD-3 — [ADOPTED] Сохраняемая state machine обработки**; **AD-7 — [ADOPTED] Provenance переживает редактирование**.
- Показ частично созданной встречи или промежуточного artifact как доступного результата противоречит atomic import и `ready`-only reads. — Источник: **AD-2 — [ADOPTED] Владение постоянными данными**; **AD-13 — [ASSUMPTION] Импорт — одна атомарная команда**.
- UX параллельной загрузки нескольких heavy local models противоречит exclusive model-residency lease и 16-ГБ baseline. — Источник: **AD-12 — [ASSUMPTION] Ресурсный и модельный baseline**.
- Формулировка «полностью offline» без оговорок конфликтует с model-fetch и выбранными provider stages, хотя сама local processing изолирована от egress. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**; **Structural Seed**.
- Удалённый доступ, accounts/roles, совместная библиотека и нативное приложение выходят за архитектурный scope MVP. — Источник: **Deferred**.
- Semantic/meaning-based search противоречит текущему MVP-контракту lexical FTS5 без embeddings. — Источник: **AD-9 — [ASSUMPTION] Локальный полнотекстовый поиск**; **Deferred**.
- Согласие на provider processing нельзя трактовать как бессрочное: любое изменение связанных параметров делает consent proof недействительным. — Источник: **AD-5 — [ASSUMPTION] Топология и граница egress**.
