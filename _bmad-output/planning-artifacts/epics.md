---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-summarization-of-meetings-2026-08-31/prd.md
  - _bmad-output/planning-artifacts/prds/prd-summarization-of-meetings-2026-08-31/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-summarization-of-meetings-2026-08-31/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-summarization-of-meetings-2026-08-31/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-summarization-of-meetings-2026-08-31/EXPERIENCE.md
---

# summarization-of-meetings - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for summarization-of-meetings, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Пользователь может создать Встречу, выбрав один аудио- или видеофайл и указав или отредактировав её название, дату, Профиль обработки и язык транскрибации; до создания сущностей файл должен пройти проверку доступности, читаемости, контейнера, аудиоданных, декодируемости и применимых лимитов.

FR2: Приложение сохраняет метаданные, Расшифровку, Саммари и состояние Задания обработки в локальной базе данных, а Исходную запись и производные медиафайлы — только в управляемом локальном хранилище.

FR3: Пользователь может просматривать локальную библиотеку Встреч со статусом, названием, датой, длительностью, Тегами, Участниками, номером Внешней задачи и временем последнего изменения и открывать Встречу, незавершённое Задание или сведения об ошибке.

FR4: Пользователь может удалить Исходную запись после успешной обработки, сохранив текст и метаданные, либо полностью удалить Встречу и все связанные материалы после явного подтверждения; частичное удаление не должно выдаваться за успешное.

FR5: Пользователь может независимо создать и проверить конфигурацию OpenAI-совместимого Движка транскрибации или суммаризации с отображаемым именем, адресом API, секретным ключом и идентификатором модели, получая категоризированные результаты проверки совместимости и ошибок.

FR6: Пользователь может выбрать установленный локальный Движок транскрибации и локальный Движок суммаризации, увидеть наличие моделей и требования к памяти и проверить их готовность до запуска; после подготовки моделей основной локальный путь работает без сети.

FR7: До запуска Задания приложение показывает локальный либо provider-режим каждого этапа, а для внешнего этапа — сервис и передаваемые данные; первое использование внешнего Профиля требует согласия, и автоматический local-to-provider fallback запрещён.

FR8: Пользователь может выбрать язык Саммари, отредактировать дополнительные инструкции, сохранить их в Профиле обработки и одним действием вернуть встроенные инструкции.

FR9: Приложение локально и потоково извлекает аудио из видео либо проверяет и при необходимости нормализует прямой аудиофайл для выбранного Движка транскрибации, не отправляя внешнему движку видеодорожку без необходимости.

FR10: Движок транскрибации создаёт Расшифровку из Сегментов с таймкодами, а Страница Встречи предоставляет доступный встроенный аудио- или видеоплеер, переход по таймкоду, фокус соответствующего Сегмента и явные состояния субтитров, ошибок и удалённого медиа без неявного автовоспроизведения.

FR11: Если Движок поддерживает определение спикеров, приложение сохраняет метки в Сегментах и позволяет переименовать метку во всей Расшифровке; обработка без диаризации допустима, а метки спикеров не связываются автоматически с Участниками.

FR12: Пользователь может редактировать текст Сегментов, объединять и разделять их без потери таймкодов, отменять несохранённые изменения, сохранять правки локально и тем самым помечать существующее Саммари как потенциально устаревшее.

FR13: Приложение показывает сохраняемое состояние этапов подготовки, транскрибации и суммаризации, прошедшее время и реальный процент, когда он доступен, либо честный индикатор активности без выдуманного значения.

FR14: После ошибки или перезапуска пользователь может продолжить с последнего сохранённого этапа либо повторить выбранный неуспешный этап без удаления успешно сохранённых результатов и без ненужного повтора предшествующих этапов.

FR15: Пользователь может отменить выполняемое Задание; приложение прекращает дальнейшие обращения к Движкам, явно фиксирует отмену и сохраняет уже опубликованные промежуточные результаты для нового запуска или удаления.

FR16: Движок суммаризации создаёт из Расшифровки структурированное Саммари с обзором, темами, решениями, задачами, ответственными и сроками только при наличии в источнике, Важными моментами и открытыми вопросами, не выдумывая отсутствующие значения.

FR17: Каждый элемент Саммари — решение, задача или Важный момент — содержит ссылку на подтверждающие Сегменты либо явный статус «подтверждение не найдено»; переход фокусирует актуальный Сегмент и позиционирует доступное медиа без автоматического запуска.

FR18: Пользователь может редактировать текущее Саммари и повторно создать его из текущей Расшифровки с выбранными инструкциями; замена вручную изменённого результата требует подтверждения, а история хранит только сведения о последнем запуске без секретов.

FR19: Пользователь может локально искать по названиям, текущим Расшифровкам и Саммари и фильтровать Встречи по дате, статусу, Тегам, Участникам и структурированному номеру Внешней задачи с exact/prefix-сопоставлением, сохраняя запрос и фильтры при переходах.

FR20: Пользователь может локально экспортировать полное Саммари с метаданными и таймкодами в Markdown, Расшифровку в TXT или VTT и структурированные данные Встречи в JSON без секретов и внутренних диагностических данных.

FR21: Пользователь может скопировать отдельный раздел Саммари, задачу, решение или Важный момент вместе с таймкодом в понятном вне приложения виде без сетевых обращений.

FR22: Пользователь может создавать и удалять Теги конкретной Встречи и изменять единый набор ручных и автоматически назначенных после успешной суммаризации Тегов; редактирование Тега не влияет на другие Встречи.

FR23: Пользователь может создавать, искать, редактировать и удалять записи локального Справочника участников и назначать Встрече нескольких Участников; удаление снимает связи после подтверждения и не меняет Расшифровку или метки спикеров.

FR24: Пользователь может вручную сохранить, изменить или удалить URL и структурированный номер одной существующей Внешней задачи, исправить извлечённый из URL номер и открыть явно обозначенный внешний переход без API-интеграции или синхронизации.

### NonFunctional Requirements

NFR1: Все постоянные данные приложения, включая Теги, Справочник участников и связь с Внешней задачей, хранятся на устройстве пользователя; библиотека, сохранение связи и поиск по номеру не требуют внешнего аккаунта или сетевого запроса.

NFR2: Библиотека до 1 000 Встреч и основные экраны открываются не более чем за 2 секунды на целевом устройстве; под локальной нагрузкой навигация, сохранение и запрос отмены отвечают не более чем за 1 секунду в p95, а безопасная остановка достигается не более чем за 10 секунд.

NFR3: Импорт поддерживаемого файла и подготовка аудио не помещают весь файл в оперативную память; прогресс или активность обновляются не реже одного раза в 5 секунд.

NFR4: Подтверждённые данные, метаданные и завершённые этапы сохраняются атомарно; аварийное завершение не теряет результат успешно завершённого этапа, а частичная ошибка удаления не маскируется под полное удаление.

NFR5: Локальный журнал содержит этапы, коды ошибок и технические метаданные, но по умолчанию не содержит секреты, полный текст Расшифровки или Саммари.

NFR6: Все основные действия, включая управление плеером и переходы по таймкодам, доступны с клавиатуры; поля и контролы имеют программные подписи, а статус обозначается не только цветом.

NFR7: Веб-интерфейс поддерживает актуальные Chromium и Firefox; основной самостоятельный запуск выполняется через Docker Compose на Linux, macOS и Windows, без нативных пакетов MVP.

NFR8: Публичный репозиторий содержит лицензию, пошаговый запуск, пример конфигурации без секретов, описание локальных каталогов и процедуры обновления, резервного копирования и восстановления всех материалов и метаданных.

NFR9: Код выпускается под Apache License 2.0 с явным патентным грантом.

NFR10: После однократной настройки Профиля пользователь выбирает одну Исходную запись и запускает Задание с одного экрана; необязательные технические параметры не блокируют запуск и не требуют повторного ввода.

### Additional Requirements

- **AR-1 — Начальный каркас:** готовый starter template архитектурой не указан. Первая реализационная история должна создать structural seed монорепозитория с `backend/src/meeting_app/{modules,platform,entrypoints,bootstrap}`, `frontend/src/{app,features}`, `migrations` и `deploy`, а также воспроизводимые команды сборки и проверок.
- **AR-2 — Архитектурная форма:** реализовать гексагональный модульный монолит с доменными модулями `meetings`, `profiles`, `processing`, `search_export`; entrypoints зависят от application, application — только от domain/ports, adapters реализуют ports, а межмодульные вызовы проходят через публичные application-команды и запросы.
- **AR-3 — Зафиксированный стек:** использовать Python 3.13.15, FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.1, SQLite 3.53.4 с FTS5/WAL, FFmpeg 9.0.1, React 19.2.7, Ant Design 6.6.2, TypeScript 6.0.3, Vite 8.2.2, Node.js 24.20.0 LTS и Docker Compose 5.4.0; версии runtime, images и моделей должны быть pinned.
- **AR-4 — Владение данными и артефактами:** SQLite является источником истины структурированного состояния, управляемая файловая область — media/artifacts/models; файлы публикуются через `pending → ready` с atomic rename и CAS, читаются только в `ready`, а startup reconciliation завершает intents и очищает pending/orphans.
- **AR-5 — Безопасное хранение и удаление media:** ввести lifecycle state/epoch, `MediaArtifact`, persisted leases и `DeleteIntent`; media-only и full delete должны блокировать новые операции, дождаться release/expiry readers/workers, атомарно сохранить либо удалить зависимые данные и оставаться восстанавливаемыми после сбоя.
- **AR-6 — Сохраняемая state machine:** `ProcessingJob` проходит `prepare → transcribe → summarize`, допускает не более одного активного job на Встречу, использует immutable snapshot, attempt/lease epochs, heartbeat/checkpoint CAS, revision/fingerprint guards и `superseded` для поздних результатов; recovery, retry и cancel следуют AD-3.
- **AR-7 — Контракты движков:** определить отдельные typed ports `TranscriptionEngine` и `SummarizationEngine`; Профиль хранит независимые конфигурации этапов и поддерживает все четыре local/provider-комбинации, проверяет capabilities и timestamped evidence и нормализует ошибки без скрытого fallback.
- **AR-8 — Сетевая топология и egress:** Compose разделяет `app`, `local-worker`, stateless `provider-worker` и одноразовый `model-fetch`; app/local-worker работают без внешнего маршрута, UI слушает только loopback, remote assets/CDN/telemetry запрещены, а provider-worker не монтирует SQLite, meeting data или models.
- **AR-9 — Провайдерский dispatch:** versioned RPC-контракт должен связывать dispatch, attempt/lease/lifecycle epochs, snapshot, consent proof и single-use grant; app ведёт `ProviderDispatch` ledger, ambiguous outcome становится `outcomeUnknown`, а автоматическая повторная отправка после `inFlight` запрещена.
- **AR-10 — Секреты только в runtime:** реализовать `SecretProvider` за memory-only broker с single-use attempt grants и ограниченным TTL; ключ запрещён в Compose/env-file, БД, jobs/events, CLI args, durable queue и logs, а restart переводит попытку в `waitingForSecret`.
- **AR-11 — Provenance и ревизии:** Transcript имеет возрастающую revision и валидируемые Segment IDs/таймкоды; EvidenceRef разрешается только в Segment той же revision; Summary хранит source revision, snapshot digest, generated time и manual/stale/unverified markers, а невалидный output не публикуется.
- **AR-12 — Структурированная суммаризация:** pipeline передаёт стабильные segment IDs, извлекает candidates по bounded chunks, сводит их вместе с evidence IDs и валидирует итог по доменной JSON Schema; Summary и auto-tags публикуются одной транзакцией, ручные Теги сохраняются.
- **AR-13 — Локальный поиск:** SQLite FTS5 индексирует title, текущие Segments и текущее Summary в транзакции публикации; номер задачи нормализуется backend-only через NFKC/trim/full casefold, хранится отдельным ключом и обслуживает только exact/prefix B-tree path с bounded pagination без fuzzy/contains/semantic fallback.
- **AR-14 — Миграции, backup и restore:** Alembic имеет один linear forward-only head; migration gate берёт maintenance lock, останавливает mutations/leases, создаёт и проверяет complete backup generation, после чего выполняет миграцию; restore проверяет новую generation до recoverable atomic pointer switch.
- **AR-15 — Единый API-контракт:** REST JSON API размещается под `/api/v1`, OpenAPI является единственным источником frontend client/DTO; IDs — UUIDv7, время — RFC 3339 UTC, offsets — integer milliseconds, ошибки — RFC 9457 со stable `code`, `stage`, `retryable`.
- **AR-16 — List/search API:** filters используют повторяемые значения OR внутри facet и AND между facets, bounded `limit` и opaque cursor, связанный с filter/sort digest; response возвращает canonical filter echo, typed match и `nextCursor`, а no-hit — пустую страницу `200` без переключения search path.
- **AR-17 — Media и SSE API:** playback endpoint скрывает filesystem path и реализует `GET`/`HEAD`, single byte ranges, 200/206/400/416, identity encoding, правильные headers и strong checksum ETag; SSE использует persisted monotonic revision, replaceable snapshots и `resync`, а клиент игнорирует stale revisions.
- **AR-18 — Ресурсный baseline:** `LocalResourceCoordinator` удерживает exclusive model-residency lease, одновременно резидентна одна тяжёлая модель; CPU/int8 — поддерживаемый baseline, accelerator optional; кандидаты — pinned Whisper large-v3-turbo CT2 и Qwen3-4B-GGUF Q4_K_M, их пригодность подтверждается release gates.
- **AR-19 — Атомарный intake:** единая команда принимает ровно один audio/video source, потоково пишет staging, проверяет его через `ffprobe` и создаёт Meeting/source artifact только после успеха; rejection очищает staging и не создаёт job.
- **AR-20 — Подготовленные и playback-артефакты:** `prepare` идемпотентно создаёт canonical PCM s16le mono 16 kHz prepared audio; исходник используется для playback только при browser-compatible container/codec, иначе создаётся WebM/Opus либо WebM/VP9+Opus; identities детерминированы и производные живут до явного удаления.
- **AR-21 — Frontend design system:** production UI использует только Ant Design 6 через единый `ConfigProvider → App → routes`, русскую locale, системные light/dark algorithms и tokens; CSS, CSS Modules, styled wrappers, internal selectors и visual `styles`/`classNames` запрещены, кроме native audio/video controls.
- **AR-22 — Операционные бюджеты:** API не выполняет compute, import/provider upload потоковые, list/search bounded и paginated; release benchmark под активным local job проверяет library/navigation ≤2 s на 1 000 Встреч, p95 UI/API ≤1 s, heartbeat/progress ≤5 s и cancel safe point ≤10 s.
- **AR-23 — Соглашения реализации:** Python/DB используют `snake_case`, TypeScript/JSON — `camelCase`, types/entities — `PascalCase`; данные — UTF-8/UTC, пути относительны managed root, mutations проходят application commands, adapters не меняют domain state, логи структурированы и исключают секреты/полные payloads.
- **AR-24 — Retry policy:** provider auto-retry допускается не более двух раз только при доказанном `not accepted` либо provider idempotency для timeout/network/rate/server failures; auth, validation и missing model не повторяются, ambiguous outcome требует явного нового attempt.
- **AR-25 — Release governance:** публичный release проходит Linux/macOS/Windows × 16-GB CPU, Chromium/Firefox media seek/playback, corpus quality/resource/performance gates, one-screen happy path, clean-host Compose install ≤20 минут без загрузки моделей и WCAG 2.2 AA outcomes.
- **AR-26 — Лицензии и supply chain:** корневой код — Apache-2.0; NOTICE, SBOM и release manifest фиксируют image/runtime/model/source revisions, checksums, licenses, FFmpeg flags/codecs и provenance; провал license/resource/quality gate требует заменить candidate за engine port.
- **AR-27 — Обязательные ранние проверки:** до первого frontend feature merge выполнить no-CSS Ant Design feasibility spike; до provider flow — threat/data-flow и secret-restart tests; до search completion — Unicode/pagination tests и benchmark на 1 000 Встреч; до первой migration — restore drill; до intake release — crash-injection и all-format playback/range tests.
- **AR-28 — Открытый release gate OQ-1:** поддерживаемые форматы и отдельные лимиты прямого аудио должны быть утверждены до реализации direct-audio intake и фиксации корпуса выпуска.
- **AR-29 — QA-протокол Саммари:** до оценки корпуса зафиксировать единицу сопоставления, правила неоднозначных эталонов, агрегацию precision/recall и проверку корректности evidence-ссылок без изменения порогов PRD.

### UX Design Requirements

UX-DR1: Production UI должен использовать Ant Design как единственную базовую UI-систему: `ConfigProvider → App → product routes`, русскую locale, светлую тему по умолчанию и системную тёмную тему; CSS, CSS Modules, styled wrappers, internal selectors и visual `styles`/`classNames` запрещены, кроме native `<video controls>`/`<audio controls>`.

UX-DR2: Реализовать полный набор заданных светлых/тёмных semantic color tokens и автоматическую проверку разрешённых foreground/background пар на WCAG 2.2 AA: 4.5:1 для обычного текста и 3:1 для крупного текста, компонентов и focus ring; status всегда дублируется текстом или значком.

UX-DR3: Реализовать typography tokens для page title, section title, body, body-sm, label, meta и mono через Ant Design Typography; использовать system-first sans stack и только локальный Inter bundle, не обрезать тексты договорённостей, ошибок, consent и delete confirmation.

UX-DR4: Реализовать 4-px spacing rhythm, заданные radius/content/sidebar/rail tokens, максимум контента 1200 px и минимальные цели: 24×24 либо WCAG spacing exception, а для icon-only/player/timecode/evidence/copy/destructive controls — 44×44 на всех ширинах.

UX-DR5: Реализовать маршрутизируемые поверхности «Библиотека», «Поиск», «Импорт», «Ход обработки», «Страница Встречи», «Участники», «Профили обработки», «Настройки и диагностика»; `consent-dialog`, `confirm-dialog` и `export-menu` остаются overlays, глубина overlay не превышает один.

UX-DR6: Страница Встречи должна сохранять единый DOM/focus/reading order: heading → summary → agreements → player → metadata → transcript; desktop может раскладывать те же узлы в две зоны, narrow reflow не меняет порядок и не скрывает header actions.

UX-DR7: Микрокопирайт должен быть коротким и нейтрально-деловым, называть сохранённое состояние, границу данных и безопасное действие; исключить восклицания, похвалу, антропоморфизм, AI-confidence theater, fake progress и неопределённые ошибки.

UX-DR8: `app-shell` должен предоставить первым фокусируемым элементом skip link «К основному содержимому», named navigation landmark, `aria-current="page"`, доступные имена rail-ссылок и маршрут к диагностике без account/avatar semantics.

UX-DR9: `mobile-nav-trigger` должен быть реальной кнопкой минимум 44×44 с именами открытия/закрытия, `aria-expanded`/`aria-controls`; nav overlay делает фон inert, переносит фокус внутрь, закрывается по Escape/outside action и возвращает фокус.

UX-DR10: `primary-button` должен быть единственным primary action в регионе; disabled state объясняет причину, а submit сохраняет footprint, меняет label, выставляет busy state и не отправляет повторную команду.

UX-DR11: `secondary-button` должен обслуживать безопасные и обратимые edit/cancel/retry actions; retry label явно называет повторяемый этап.

UX-DR12: `destructive-button` используется только внутри confirmation после списка последствий, визуально отделяется от безопасных действий и никогда не получает начальный фокус.

UX-DR13: `text-field` должен иметь постоянный label, `aria-describedby`, `aria-invalid`, связанную сводку ошибок/фокус первого невалидного поля и явные Save/Cancel для metadata/transcript/summary edits.

UX-DR14: `select-field` наследует label/error contract текстового поля; выбранный mode виден текстом, а смена provider/model до сохранения явно сообщает об инвалидации прежнего consent.

UX-DR15: `status-badge` должен отображать semantic icon и пользовательский label, сопоставленный durable backend state; raw codes показываются только в диагностике, цвет не является единственным носителем статуса.

UX-DR16: `meeting-row` реализуется как `<article>`/`<li>` с отдельной heading-link «Открыть встречу: [название]», метаданными/status и sibling retry/error actions; строка не становится единым interactive container, список имеет bounded pagination без infinite scroll.

UX-DR17: `search-field` выполняет debounced local FTS5 по title/current transcript/current summary, распознанный task number направляет в отдельный structured exact/prefix lookup, Enter открывает поверхность поиска; внешние запросы и semantic claims запрещены.

UX-DR18: `filter-bar` реализует date/status/tags/participants/task-number facets с AND между группами и OR внутри группы; collapsed popover управляет `aria-expanded`/`aria-controls`, Tab/Escape/outside-close/focus return, а multi-select объявляет count и предоставляет именованные 44×44 remove buttons.

UX-DR19: `import-dropzone` поддерживает drag/drop и labelled picker ровно одного файла; preflight до Meeting creation проверяет доступность/read permission, container, audio track, decodability и limits, а любой отказ сохраняет форму, не создаёт Meeting/job и предлагает повторный выбор.

UX-DR20: `stage-progress` показывает три фиксированных этапа, elapsed time и только реальный percent; обновление ≤5 секунд, completed stages сохраняются после failure/restart, `progressbar` несёт percent, а один стабильный polite/atomic status node объявляет только semantic transitions/resync/cancel/terminal outcomes.

UX-DR21: `notice-banner` обслуживает stale, unverified, high-load, waiting-secret, retryable и ambiguous состояния, показывает причину и ровно одно наиболее безопасное следующее действие с optional details link.

UX-DR22: `media-player` предпочитает native audio/video controls; fallback предоставляет именованные play/pause, seek с ARIA values, mute/volume, fullscreen для видео, elapsed/total и error state; VTT подключается как captions, transcript route доступен всегда, deleted media превращается в явное unavailable state.

UX-DR23: `summary-card` показывает текущие overview/themes/decisions/tasks/highlights/open questions, edit/copy и видимые manual/stale/unverified markers; version selector отсутствует, пустые разделы представлены как «Не обнаружено».

UX-DR24: `agreement-item` формирует полный упорядоченный список договорённостей; important state обозначается marker+label, responsible/due выводятся только при наличии в источнике, каждый элемент копируется отдельно и всегда показывает evidence state.

UX-DR25: `evidence-link` использует `href` на стабильный DOM ID Сегмента; activation атомарно seek-ит player, фокусирует `tabindex="-1"` target и делает одно polite announcement с item/timestamp/speaker/verification; playback начинается только отдельным явно названным действием, unresolved evidence не является ссылкой.

UX-DR26: `transcript-segment` имеет стабильный DOM ID, программный фокус и видимый non-color marker «Фрагмент подтверждения»; timestamp seek-ит player, split/merge сохраняет bounds, rename меняет только совпадающие speaker labels.

UX-DR27: `tag-chip` позволяет создавать/удалять ручные и редактировать auto-tags после успешного Саммари; origin виден только в edit mode, multi-select объявляет изменения/count и использует именованную 44×44 removal button.

UX-DR28: `participant-chip` использует тот же доступный combobox/listbox/count/removal contract, остаётся только архивным metadata и никогда не связывается со speaker labels, Segments, identity или access.

UX-DR29: `task-link-card` выводит task number главным уровнем, отмечает внешний переход, открывает URL в новой вкладке с notice, показывает extraction metadata в edit state, позволяет ручное исправление и использует structured exact/prefix path вне FTS5.

UX-DR30: `profile-stage-card` предоставляет симметричные отдельные карточки Transcription и Summarization с mode, engine, model, readiness, data category и privacy boundary; автоматический fallback отсутствует.

UX-DR31: `consent-dialog` реализует полный modal contract с `role="dialog"`, `aria-modal`, title/description IDs, inert background и focus return; называет stage/provider/endpoint/model/exact data categories, меняется при fingerprint change, а Cancel/Escape не выполняет dispatch.

UX-DR32: `confirm-dialog` наследует полный modal/focus contract, перечисляет последствия и сохранённые данные, не фокусирует destructive action первым и остаётся открытым при ошибке с явным перечнем оставшихся материалов; participant delete показывает число затронутых Встреч.

UX-DR33: `export-menu` имеет доступный trigger и labelled menu с Arrow/Tab/Escape/outside-close/focus return; строки явно называют format/content для Markdown, TXT/VTT и JSON, генерация локальна, secret/diagnostics исключены, результат имеет текстовый feedback.

UX-DR34: `empty-state` содержит один объясняющий текстовый блок и одно релевантное действие без mascot illustration; filtered-empty предлагает очистить фильтры, а не импортировать новую Встречу.

UX-DR35: `diagnostic-panel` показывает безопасные code/stage/retryable/model/profile/technical metadata; копирование диагностики исключает secret, full transcript, summary и provider payload.

UX-DR36: Для каждой поверхности реализовать перечисленные в UX-контракте loading, empty, populated, validating, active, failure, recovery, success и maintenance states; last safe view/form сохраняется при ошибках, partial cleanup не показывается как success, raw backend states не попадают в основной UI.

UX-DR37: Реализовать общие interaction primitives: Tab/Shift+Tab по canonical order, Enter для focused controls, Space для playback только внутри player, Escape закрывает верхний безопасный overlay/edit и никогда не отменяет processing job; запретить hover-only controls, autoplay, infinite scroll, modal stacks и drag-to-reorder.

UX-DR38: Search/filter state должен синхронизироваться с URL, Back восстанавливает архивный контекст; long operations переживают refresh/reconnect без duplicate job; unsaved navigation использует confirmation, а успешное сохранение объявляется стабильным status node без color-only toast.

UX-DR39: UI приватности и provenance должен перед каждым изменившимся provider dispatch точно называть stage, endpoint/provider/model и payload; после restart показывать «Ожидается ключ», stale/unverified сохранять видимыми, ambiguous provider outcome требовать явного нового attempt, а local-to-provider fallback запрещать.

UX-DR40: Responsive/accessibility contract должен пройти WCAG 2.2 AA, keyboard/focus и non-color status tests, 200% zoom и 320 CSS px reflow без горизонтального page scroll, `prefers-reduced-motion`, target sizes, эквивалентность audio/video controls и Chromium/Firefox parity на Linux/macOS/Windows; breakpoints: ≥1200 sidebar/two-zone/sticky player, 900–1199 rail/conditional zones, <900 overlay nav/single order, <600 collapsed filters/no wide tables.

### FR Coverage Map

FR1: Epic 2, Story 2.1 — Проверяемый импорт одной аудио- или видеозаписи.
FR2: Epic 2, Stories 2.1–2.2 — Локальное постоянное хранение Встречи и управляемых медиафайлов.
FR3: Epic 2, Story 2.2 — Библиотека Встреч с состояниями обработки и ошибками.
FR4: Epic 4, Stories 4.6–4.7 — Удаление медиа с сохранением текста либо полное удаление Встречи.
FR5: Epic 1, Story 1.4 — Создание и проверка конфигурации внешнего движка.
FR6: Epic 1, Story 1.5 — Выбор и проверка готовности локальных движков.
FR7: Epic 1, Story 1.6; execution support in Story 2.7 — Явная граница передачи данных и согласие без скрытого fallback.
FR8: Epic 1, Story 1.3 — Язык и инструкции Саммари в Профиле обработки.
FR9: Epic 2, Story 2.3 — Локальная потоковая подготовка аудио.
FR10: Epic 3, Stories 3.1–3.2; pipeline support in Story 2.5 — Расшифровка с таймкодами и встроенный media player.
FR11: Epic 3, Stories 3.2–3.3 — Опциональные редактируемые метки спикеров.
FR12: Epic 3, Story 3.3 — Редактирование Сегментов с сохранением временных границ.
FR13: Epic 2, Stories 2.4 and 2.8 — Честные сохраняемые этапы и прогресс обработки.
FR14: Epic 2, Story 2.8 — Восстановление и повтор выбранного этапа.
FR15: Epic 2, Story 2.9 — Безопасная отмена с сохранением опубликованных результатов.
FR16: Epic 3, Story 3.4; pipeline support in Story 2.6 — Структурированное Саммари без выдуманных значений.
FR17: Epic 3, Story 3.5 — Проверяемые evidence-ссылки либо явный статус их отсутствия.
FR18: Epic 3, Story 3.6 — Редактирование и повторное создание текущего Саммари.
FR19: Epic 4, Story 4.4 — Локальный текстовый поиск и structured exact/prefix task-number path.
FR20: Epic 4, Story 4.5 — Локальный экспорт Markdown, TXT/VTT и JSON.
FR21: Epic 3, Story 3.7 — Копирование отдельных проверяемых частей результата.
FR22: Epic 4, Story 4.1 — Ручные и автоматически назначенные Теги Встречи.
FR23: Epic 4, Story 4.2 — Локальный Справочник участников и назначения Встречам.
FR24: Epic 4, Story 4.3 — Локальная связь с существующей Внешней задачей без API-интеграции.

## Epic List

### Epic 1: Безопасная настройка обработки

Пользователь может самостоятельно запустить приложение, независимо настроить локальные или внешние Движки транскрибации и суммаризации, проверить их готовность и до каждого запуска понимать границы передачи данных.

**FRs covered:** FR5, FR6, FR7, FR8

**Implementation notes:** Эпик включает structural seed, воспроизводимый Compose-базис, Ant Design foundation, runtime-only secrets, независимые engine ports, Профили обработки, provider consent и безопасную диагностику.

### Epic 2: Надёжный импорт и обработка Встречи

Пользователь может импортировать одну аудио- или видеозапись, видеть её в локальной библиотеке и довести сохраняемое Задание через подготовку, транскрибацию и суммаризацию с честным прогрессом, отменой и восстановлением.

**FRs covered:** FR1, FR2, FR3, FR9, FR13, FR14, FR15

**Implementation notes:** Эпик включает атомарный streaming intake, managed storage, durable processing state machine, local/provider workers, progress/SSE, безопасный provider dispatch и локальный модельный baseline.

### Epic 3: Проверяемый и исправляемый результат

Пользователь может изучить Расшифровку и Саммари рядом с сохранённой записью, проверить выводы по evidence, исправить текст или метки спикеров, обновить Саммари и скопировать нужный результат.

**FRs covered:** FR10, FR11, FR12, FR16, FR17, FR18, FR21

**Implementation notes:** Эпик включает media playback/range, Transcript revisions, structured Summary, provenance, stale/manual/unverified states и канонический доступный reading order Страницы Встречи.

### Epic 4: Организованный и управляемый архив

Пользователь может дополнить Встречи Тегами, Участниками и связью с Внешней задачей, найти нужные материалы, экспортировать их и безопасно удалить медиа либо всю Встречу.

**FRs covered:** FR4, FR19, FR20, FR22, FR23, FR24

**Implementation notes:** Метаданные, поиск, экспорт и retention объединены, поскольку совместно изменяют Meeting DTO, библиотеку, `meetings` и `search_export`; эпик включает FTS5, отдельный structured task-number index, локальные экспорты и crash-safe delete intents.

## Epic 1: Безопасная настройка обработки

Пользователь может самостоятельно запустить приложение, независимо настроить локальные или внешние Движки транскрибации и суммаризации, проверить их готовность и до каждого запуска понимать границы передачи данных.

### Story 1.1: Запуск локального приложения из воспроизводимого каркаса

Как технически подготовленный владелец,
я хочу запустить приложение из публичного репозитория одной документированной Compose-командой,
чтобы получить безопасную локальную основу для последующей настройки обработки.

**Acceptance Criteria:**

**Given** чистый clone репозитория на поддерживаемой Linux, macOS или Windows-системе с Docker Compose
**When** владелец следует пошаговой инструкции и запускает baseline без загрузки моделей
**Then** приложение становится доступно через документированный URL не более чем за 20 минут, исключая время загрузки образов
**And** host binding ограничен `127.0.0.1`/`::1`, доступ по non-loopback адресу не является штатно доступным.

**Given** запущенный baseline
**When** клиент обращается к health endpoint под `/api/v1`
**Then** он получает стабильный versioned JSON-контракт с RFC 3339 UTC временем и RFC 9457 error shape для отказов
**And** OpenAPI публикуется как единственный источник будущего frontend client/DTO.

**Given** исходный код проекта
**When** выполняются build и architecture checks
**Then** присутствует structural seed `backend/src/meeting_app/{modules,platform,entrypoints,bootstrap}`, `frontend/src/{app,features}`, `migrations` и `deploy`
**And** automated dependency test запрещает импорт adapters/entrypoints в domain/application вопреки гексагональному направлению зависимостей.

**Given** startup локального хранилища
**When** SQLite не поддерживает требуемые version/FTS5/WAL options либо managed data path расположен на известной неподдерживаемой network filesystem
**Then** приложение завершается fail-fast с безопасным диагностическим кодом
**And** не создаёт частично инициализированную схему или готовый service state.

**Given** проверка runtime и supply-chain baseline
**When** собираются образы и frontend bundle
**Then** версии основного стека pinned согласно AR-3, образы допускают digest pinning, а корень содержит Apache-2.0 license и пример конфигурации без секретов
**And** bundle не использует CDN, remote fonts/assets, telemetry или analytics и отдаёт CSP с соединениями только к `self`.

### Story 1.2: Доступная адаптивная оболочка приложения

Как владелец локального приложения,
я хочу последовательно перемещаться между основными разделами в светлой или тёмной теме,
чтобы настройка и дальнейшая работа оставались понятными на разных ширинах и при управлении с клавиатуры.

**Acceptance Criteria:**

**Given** frontend application root
**When** загружается любой продуктовый маршрут
**Then** используется единственная цепочка `ConfigProvider → App → product routes`, русская locale и документированные Ant Design tokens
**And** automated check не находит CSS, CSS Modules, styled wrappers, internal selectors либо visual `styles`/`classNames` customization.

**Given** wide desktop viewport
**When** пользователь проходит интерфейс клавишей Tab
**Then** первым доступен skip link «К основному содержимому», navigation имеет landmark и активный маршрут `aria-current="page"`
**And** доступны маршруты Библиотеки, Поиска, Импорта, Хода обработки, Встречи, Участников, Профилей и Диагностики с честными empty/not-yet-applicable states.

**Given** ширина менее 900 px либо zoom-triggered breakpoint
**When** пользователь открывает `mobile-nav-trigger`
**Then** кнопка имеет имя, `aria-expanded`, `aria-controls` и цель не менее 44×44, фон становится inert, фокус переходит в nav overlay
**And** Escape/outside action закрывает overlay и возвращает фокус, не теряя ни маршрут, ни действие.

**Given** системное переключение light/dark либо `prefers-reduced-motion: reduce`
**When** тема или motion preference меняется
**Then** semantic color, typography, spacing и radius tokens применяются без перезагрузки, contrast checks достигают WCAG 2.2 AA
**And** декоративная анимация, smooth scroll и indeterminate sweeps отключаются без потери функциональной информации.

**Given** 200% zoom и viewport 320 CSS px
**When** пользователь просматривает shell и базовые формы
**Then** отсутствует горизонтальный page scroll, controls не исчезают, status имеет text/icon кроме цвета
**And** icon-only и критические product controls сохраняют 44×44, остальные цели — не менее 24×24 либо документированное spacing exception.

**Given** базовые Button, Form, Input, Select, Alert, Empty и status compositions
**When** пользователь взаимодействует только клавиатурой
**Then** focus видим, labels постоянны, disabled actions объясняют причину, busy submit не дублирует команду
**And** Escape закрывает только верхний безопасный overlay или edit и никогда не отменяет processing job.

### Story 1.3: Создание независимого Профиля обработки

Как владелец приложения,
я хочу сохранить независимые настройки транскрибации и суммаризации вместе с параметрами результата,
чтобы один Профиль явно описывал весь выбранный способ обработки Встречи.

**Acceptance Criteria:**

**Given** пустая поверхность Профилей
**When** пользователь выбирает создание Профиля
**Then** отображаются две симметричные `profile-stage-card` для транскрибации и суммаризации с mode, engine, model, readiness и data category
**And** каждая стадия независимо допускает local или provider mode, включая все четыре комбинации.

**Given** форма нового Профиля
**When** пользователь задаёт имя, конфигурации обоих этапов, язык Саммари и дополнительные инструкции и сохраняет форму
**Then** приложение создаёт только необходимые сущности Профиля и stage configs через application command
**And** ответ `/api/v1` соответствует generated OpenAPI client, использует camelCase DTO и не содержит secret value.

**Given** сохранённый Профиль
**When** пользователь открывает его повторно
**Then** выбранные stage modes, engine/model identities, язык и инструкции восстановлены локально
**And** одним действием можно вернуть встроенные инструкции без изменения прочих полей.

**Given** невалидная или неполная форма
**When** пользователь пытается сохранить Профиль
**Then** постоянные labels, hints и errors связаны через `aria-describedby`, invalid fields имеют `aria-invalid="true"`, фокус переходит к error summary или первому ошибочному полю
**And** ранее введённые допустимые значения не теряются.

**Given** выбранный engine ещё не проверен или локальная модель не подготовлена
**When** Профиль сохраняется
**Then** UI честно фиксирует readiness «Не проверен» либо «Модель не подготовлена», не выдавая Профиль за готовый
**And** автоматическая замена режима, движка или модели не происходит.

**Given** несохранённые изменения Профиля
**When** пользователь пытается покинуть маршрут
**Then** доступный confirmation перечисляет несохранённые изменения и предлагает сохранить, продолжить редактирование либо выйти
**And** destructive action не получает начальный фокус.

### Story 1.4: Настройка и проверка внешнего движка

Как владелец приложения,
я хочу безопасно проверить OpenAI-совместимый движок для выбранного этапа,
чтобы до обработки понимать его доступность, совместимость и причину возможного отказа.

**Acceptance Criteria:**

**Given** provider stage в Профиле
**When** пользователь вводит display name, HTTPS endpoint, model ID и session secret и запускает проверку
**Then** typed `TranscriptionEngine` либо `SummarizationEngine` port выполняет stage-specific compatibility probe
**And** результат различает ready, limited compatibility, invalid credentials, unreachable service, incompatible API и missing model.

**Given** проверяется transcription engine
**When** ответ не предоставляет Сегменты с начальными и конечными таймкодами
**Then** движок помечается ограниченно совместимым и не может считаться готовым для evidence-required Профиля
**And** пользователь видит конкретное объяснение и безопасное следующее действие.

**Given** введённый session secret
**When** конфигурация сохраняется, логируется, экспортируется либо приложение перезапускается
**Then** открытое значение отсутствует в БД, Compose/env-file, CLI args, jobs/events, logs и DTO
**And** после restart состояние становится «Ожидается ключ», а ранее введённый ключ невозможно восстановить из интерфейса.

**Given** non-loopback provider origin
**When** выполняется probe
**Then** используется HTTPS с certificate/hostname validation
**And** auth, validation и missing-model failures не повторяются автоматически, а безопасно доказанные retryable failures не превышают двух попыток.

**Given** testing, auth/network/model error либо secret-missing state
**When** пользователь работает с формой только клавиатурой или при 320 CSS px
**Then** state обозначается текстом и значком, форма сохраняет введённые безопасные значения, primary action не дублируется
**And** полные provider payload, secret и meeting content не попадают в уведомления или диагностику.

### Story 1.5: Подготовка и проверка локальных движков

Как владелец приложения,
я хочу подготовить поддерживаемые локальные ASR- и LLM-модели и проверить ресурсы устройства,
чтобы выбранные этапы могли работать локально без передачи содержания Встречи.

**Acceptance Criteria:**

**Given** локальный stage выбран в Профиле
**When** пользователь открывает сведения о модели
**Then** UI показывает pinned model/revision/checksum, ориентировочные требования к памяти, readiness и CPU/int8 baseline
**And** accelerator обозначается как optional и не требуется для поддерживаемого пути.

**Given** модель отсутствует
**When** пользователь явно запускает подготовку
**Then** только одноразовый `model-fetch` получает egress, загружает модель во staging, проверяет checksum/license metadata и атомарно публикует состояние `ready`
**And** `app` и `local-worker` не получают внешний маршрут, а partial/corrupt download не считается готовой моделью.

**Given** целевое устройство с 16 ГБ памяти
**When** проверяются обе локальные стадии
**Then** доступны один поддерживаемый ASR candidate Whisper large-v3-turbo CT2 и один LLM candidate Qwen3-4B-GGUF Q4_K_M
**And** `LocalResourceCoordinator` сообщает, что одновременно может быть резидентна только одна тяжёлая модель.

**Given** ресурсов недостаточно либо manifest/checksum несовместим
**When** readiness check завершается
**Then** Профиль получает user-facing state «Несовместимые ресурсы» либо «Подготовка не завершена» и безопасное действие
**And** приложение не запускает модель, не меняет stage на provider и не скрывает причину.

**Given** модели успешно подготовлены
**When** сеть отключена и readiness проверяется повторно
**Then** обе локальные стадии остаются готовыми по локальному manifest и filesystem state
**And** UI формулирует обещание как отсутствие content egress после подготовки моделей, не как универсальную работу без сети.

### Story 1.6: Просмотр границы данных и подтверждение передачи

Как владелец приложения,
я хочу увидеть режим и точный состав данных каждого этапа и подтвердить изменившуюся внешнюю передачу,
чтобы осознанно контролировать приватность до provider dispatch.

**Acceptance Criteria:**

**Given** готовый Профиль с local и/или provider stages
**When** пользователь открывает проверку границ данных
**Then** каждая `profile-stage-card` явно показывает stage, mode, engine/provider, endpoint, model и data category
**And** local stage сообщает, что содержание не покидает устройство после подготовки моделей.

**Given** provider transcription stage без действующего согласия
**When** приложение готовит передачу
**Then** `consent-dialog` перечисляет prepared audio, language/config, stage, endpoint/provider и model
**And** ни один provider dispatch не может получить разрешение до явного подтверждения.

**Given** provider summarization stage без действующего согласия
**When** приложение готовит передачу
**Then** dialog перечисляет current transcript chunks, instructions/config и точную identity получателя
**And** согласие транскрибации не считается согласием на суммаризацию.

**Given** ранее принятое согласие
**When** меняется stage, profile revision, endpoint origin, provider/model, data categories либо snapshot digest
**Then** consent fingerprint инвалидируется и dialog снова переходит в review
**And** сохранённая proof содержит policy version и accepted time, но не secret или content payload.

**Given** открытый `consent-dialog`
**When** пользователь нажимает Cancel или Escape
**Then** dispatch не создаётся, фон остаётся защищённым от взаимодействия до закрытия и фокус возвращается к trigger
**And** destructive/confirm action не является начальной точкой фокуса.

**Given** ошибка local stage
**When** пользователь просматривает безопасные следующие действия
**Then** отсутствует автоматический либо предлагаемый как неявный local-to-provider fallback
**And** смена режима возможна только как явное редактирование Профиля с новой проверкой и новым consent.

### Story 1.7: Безопасная диагностика и самостоятельное обслуживание

Как технически подготовленный владелец,
я хочу видеть безопасную диагностику и документацию локальной установки,
чтобы самостоятельно понять состояние приложения и восстановить работоспособность без раскрытия содержимого Встреч.

**Acceptance Criteria:**

**Given** поверхность «Настройки и диагностика»
**When** приложение загружает локальное состояние
**Then** отображаются версии app/schema, storage/model/resource totals, service readiness и безопасные error codes
**And** предусмотрены loading, empty, ready, high-load, maintenance и migration-failure states с одним безопасным следующим действием.

**Given** engine, profile или service failure
**When** пользователь раскрывает `diagnostic-panel` и копирует сведения
**Then** copy содержит correlation/job/stage/error metadata, retryable flag и model/profile identity
**And** исключает secret, full transcript, summary, provider payload и filesystem path вне разрешённых managed identifiers.

**Given** локальное логирование
**When** обрабатываются configuration, model-fetch и provider-probe события
**Then** structured logs содержат stage, code и технические metadata
**And** automated redaction tests доказывают отсутствие secret и полного пользовательского content.

**Given** provider/network offline
**When** пользователь открывает приложение
**Then** локальная оболочка, Профили и диагностические сведения остаются доступны, ограничиваются только provider actions
**And** недоступность local API показывает blocking explanation и документированный restart route.

**Given** публичная документация текущего baseline
**When** новый пользователь выполняет install/update/diagnostic procedures
**Then** описаны loopback boundary, конфигурация без секретов, локальные каталоги данных и моделей, maintenance/migration behavior и безопасное резервирование текущего состояния
**And** NOTICE/SBOM/release manifest фиксируют доступные runtime/image/model revisions, checksums и licenses без незавершённых утверждений о неподтверждённых моделях.

**Given** CI/release checks Epic 1
**When** проверяется Linux/macOS/Windows Compose baseline и Chromium/Firefox shell
**Then** запуск, theme/reflow/keyboard/contrast, отсутствие remote assets и secret leakage проходят автоматизированные gates
**And** любой провал блокирует выпуск foundation и сообщает конкретный нарушенный контракт.

## Epic 2: Надёжный импорт и обработка Встречи

Пользователь может импортировать одну аудио- или видеозапись, видеть её в локальной библиотеке и довести сохраняемое Задание через подготовку, транскрибацию и суммаризацию с честным прогрессом, отменой и восстановлением.

### Story 2.1: Атомарный импорт одной Исходной записи

Как владелец приложения,
я хочу проверить и импортировать одну существующую аудио- или видеозапись,
чтобы не создавать Встречу из недоступного, повреждённого или неподдерживаемого файла.

**Acceptance Criteria:**

**Given** поверхность Импорта
**When** пользователь выбирает файл через labelled picker или drag-and-drop
**Then** принимается ровно один source, а форма сохраняет название, дату, Профиль и язык транскрибации
**And** `import-dropzone` доступен с клавиатуры, сообщает validating state и не создаёт скрытую Встречу до завершения preflight.

**Given** утверждённый MVP media contract
**When** файл исследуется по содержимому через `ffprobe`
**Then** видео допускает MP4, MOV, MKV и WebM, прямое аудио — WAV, MP3, M4A/AAC, FLAC и OGG/Opus, при длительности до 3 часов и размере до 5 ГБ
**And** расширение файла само по себе не заменяет проверку container/codec, наличия audio track, decodability, доступности и read permission.

**Given** большой поддерживаемый файл
**When** intake копирует оригинальные bytes в staging и вычисляет checksum
**Then** данные обрабатываются потоково без помещения всего файла в RAM, а activity/progress обновляется не реже одного раза в 5 секунд
**And** interruption очищает staging и возвращает пользователя к заполненной форме.

**Given** файл исчез, недоступен, нечитаем, повреждён, не содержит аудио либо превышает лимит
**When** preflight завершается отказом
**Then** UI показывает конкретную категорию причины и действие «Выбрать файл снова»
**And** в SQLite и managed storage отсутствуют Meeting, source artifact и ProcessingJob этого импорта.

**Given** полностью успешный preflight
**When** intake command публикует импорт
**Then** одна транзакция создаёт Meeting и `MediaArtifact(role=source,pending)` с media kind, исходными metadata, size и checksum, затем idempotent rename и CAS переводят artifact в `ready`
**And** failure между транзакцией и публикацией восстанавливается startup reconciliation без дублирования Meeting или файла.

### Story 2.2: Постоянная библиотека Встреч

Как владелец приложения,
я хочу видеть все импортированные Встречи и их текущее состояние после перезапуска,
чтобы возвращаться к обработке без ручного доступа к базе или файлам.

**Acceptance Criteria:**

**Given** одна или несколько импортированных Встреч
**When** пользователь открывает Библиотеку
**Then** paginated `meeting-row` показывает название, дату, длительность, status, last modified и disk size, а доступные metadata — без интерактивности всей строки
**And** heading-link имеет имя «Открыть встречу: [название]», error/retry actions являются отдельными sibling controls.

**Given** перезапуск приложения
**When** Библиотека загружается вновь
**Then** ранее подтверждённые Meeting и ready source artifacts доступны без повторного импорта
**And** SQLite остаётся источником истины структурированного состояния, а API никогда не раскрывает абсолютный filesystem path.

**Given** пустой архив
**When** Библиотека загружена
**Then** `empty-state` объясняет отсутствие Встреч и предлагает ровно одно действие «Новая встреча»
**And** не использует mascot, growth-механику или ложный sample content.

**Given** до 1 000 Встреч и активная compute-нагрузка
**When** пользователь открывает или листает bounded library pages
**Then** первый экран и переходы укладываются в 2 секунды, API/UI p95 — в 1 секунду, без infinite scroll
**And** cursor pagination детерминирована, а compute не исполняется внутри API process.

**Given** временная ошибка list API
**When** обновление страницы не удаётся
**Then** последний безопасный список остаётся видимым с notice и retry
**And** refresh не создаёт новое Задание и не меняет durable state Встреч.

### Story 2.3: Идемпотентная подготовка аудио и playback-артефакта

Как владелец приложения,
я хочу автоматически подготовить выбранную запись для распознавания и воспроизведения,
чтобы движок получал только нужное аудио, а браузер мог открыть сохранённое медиа.

**Acceptance Criteria:**

**Given** ready video source
**When** выполняется stage `prepare`
**Then** FFmpeg потоково создаёт canonical `preparedAudio` как PCM s16le mono 16 kHz с profile `asr-audio-v1`
**And** ни локальному, ни внешнему transcription engine не передаётся видеодорожка.

**Given** ready direct-audio source
**When** выполняется `prepare`
**Then** UI сообщает проверку/нормализацию, а не извлечение дорожки из видео, и публикует тот же canonical prepared-audio contract
**And** весь source не загружается в RAM.

**Given** source container/codec из versioned Chromium+Firefox allowlist
**When** определяется playback representation
**Then** `playbackArtifactId` может безопасно ссылаться на source
**And** иначе stage создаёт `playback-v1`: audio WebM/Opus либо video WebM/VP9+Opus с проверенной seek/playback совместимостью.

**Given** повторный запуск `prepare` после crash или reconnect
**When** уже существует готовая производная с identity SHA-256 от canonical tuple meeting/source/checksum/role/profileVersion
**Then** artifact переиспользуется без повторного файла
**And** unique ownership не допускает cross-Meeting sharing или двух ready artifacts одной роли/version.

**Given** ошибка FFmpeg, публикации или нехватка места
**When** stage завершается неуспешно
**Then** source остаётся ready, partial derivative не виден reads, stage получает стабильный retryable/non-retryable code
**And** reconciliation очищает orphan/pending, не удаляя подтверждённую Исходную запись.

### Story 2.4: Запуск сохраняемого Задания обработки

Как владелец приложения,
я хочу запустить обработку импортированной записи с одного экрана,
чтобы получить устойчивый трёхэтапный процесс с неизменяемыми настройками запуска.

**Acceptance Criteria:**

**Given** успешно импортированная Встреча и готовый Профиль
**When** пользователь на одном экране подтверждает source, Профиль и язык и нажимает «Начать обработку»
**Then** application command создаёт один `ProcessingJob` со stages `prepare → transcribe → summarize`, immutable snapshot, lifecycle epoch и input fingerprint
**And** необязательные технические параметры не блокируют запуск и не требуют повторного ввода.

**Given** у Meeting уже есть active job
**When** приходит повторная команда из double-click, refresh или другого клиента
**Then** второй job не создаётся, API возвращает текущее durable state
**And** primary button сохраняет footprint, busy state и не отправляет duplicate command.

**Given** старт stage attempt
**When** worker получает lease
**Then** lease epoch увеличивается, heartbeat/checkpoint применяют CAS по attempt/lease/running, а snapshot остаётся неизменяемым
**And** job event/time/IDs используют UUIDv7, RFC 3339 UTC и integer millisecond offsets.

**Given** после старта меняются Профиль, язык или инструкции
**When** пользователь инициирует новый запуск
**Then** создаётся новый explicit job/snapshot, который может пометить still-valid upstream output как `reused`
**And** running attempt старого snapshot не публикует результат поверх нового состояния.

**Given** completion любого stage
**When** lifecycle/input/revision preconditions не совпадают с текущими
**Then** attempt становится `superseded` без authoritative publication
**And** пользовательский UI не выдаёт late result за актуальный.

### Story 2.5: Локальная транскрибация с таймкодами

Как владелец приложения,
я хочу выполнить транскрибацию подготовленного аудио локальной моделью,
чтобы получить сохраняемый результат без передачи содержания за пределы устройства.

**Acceptance Criteria:**

**Given** ready preparedAudio и local transcription stage
**When** worker получает exclusive model-residency lease
**Then** pinned faster-whisper/Whisper large-v3-turbo CT2 запускается с CPU int8 baseline и читает только preparedAudio
**And** во время stage не возникает content egress, CDN, telemetry или provider call.

**Given** русский, английский или auto-detect язык snapshot
**When** модель возвращает результат
**Then** adapter нормализует его в упорядоченные Segments с stable IDs, text, `startMs`, `endMs` и optional speaker label
**And** mixed speech сохраняется настолько, насколько поддерживается engine, без выдуманных labels.

**Given** candidate Transcript
**When** validator проверяет output
**Then** segment IDs уникальны, `0 ≤ startMs < endMs ≤ mediaDuration`, порядок стабилен и chunk duplicates отсутствуют
**And** невалидный либо partial result не становится текущей завершённой Расшифровкой.

**Given** валидный результат и актуальные job/lifecycle/input preconditions
**When** stage завершается
**Then** Transcript revision и Segments публикуются одной SQLite-транзакцией вместе со stage success
**And** crash после успешной транзакции не требует повторного распознавания.

**Given** недостаток памяти, ошибка модели либо cancel checkpoint
**When** adapter прекращает работу
**Then** stage получает нормализованный code, текущий ready source/preparedAudio сохраняется, model lease освобождается
**And** UI получает безопасное retry/cancel состояние без полного текста Расшифровки в логах.

### Story 2.6: Локальная суммаризация сохранённой Расшифровки

Как владелец приложения,
я хочу локально создать текущий структурированный результат из сохранённой Расшифровки,
чтобы Задание завершалось без внешней передачи и без потери связи с исходными Сегментами.

**Acceptance Criteria:**

**Given** успешная local transcription и local summarization stage
**When** coordinator начинает суммаризацию
**Then** ASR выгружен и освобождение памяти подтверждено до запуска pinned `llama-server` с Qwen3-4B-GGUF Q4_K_M
**And** одновременно резидентна только одна тяжёлая модель.

**Given** длинная текущая Расшифровка
**When** pipeline формирует запросы
**Then** Segments передаются bounded chunks со stable IDs, candidates сводятся только вместе с evidence IDs
**And** worker использует язык, instructions/template revision и model identity только из immutable job snapshot.

**Given** model output
**When** domain validator проверяет versioned JSON Schema
**Then** обязательные typed sections и evidence references валидны относительно source Transcript revision
**And** invalid output не завершает stage и не заменяет текущий результат.

**Given** валидный output и актуальные revision/lifecycle preconditions
**When** публикация завершается
**Then** current Summary, provenance metadata и stage success фиксируются атомарно без secret и raw checkpoints
**And** сохраняется только текущий результат и audit metadata attempts, а не полная история payloads.

**Given** локальная ошибка суммаризации
**When** stage получает failure
**Then** успешно сохранённая Расшифровка остаётся текущей и пригодной для отдельного retry
**And** приложение не повторяет транскрибацию и не переключается на provider автоматически.

### Story 2.7: Безопасное выполнение provider-этапа

Как владелец приложения,
я хочу выполнить явно подтверждённый этап у выбранного провайдера не более одного раза на попытку,
чтобы использовать внешний движок без скрытой повторной передачи или доступа к локальному архиву.

**Acceptance Criteria:**

**Given** provider stage с действующим consent proof и session secret
**When** app готовит versioned dispatch envelope
**Then** envelope связывает dispatchId, attempt/lease/lifecycle epochs, stage, input fingerprint, snapshot digest, consent proof и opaque grant
**And** allowlist содержит только prepared audio + language/config для transcription либо current transcript chunks + instructions/config для summarization.

**Given** stateless provider-worker
**When** он получает envelope
**Then** worker не имеет mounts к SQLite, meeting-data или models, а до egress возвращает authenticated ACK nonce, связанный с envelope
**And** app CAS-проверяет current attempt/epochs и фиксирует `ProviderDispatch=inFlight` до выдачи single-use commit token по той же session.

**Given** matching nonce и commit token
**When** provider-worker выполняет call
**Then** право используется ровно один раз, restart теряет право egress, а повтор того же inFlight dispatch автоматически запрещён
**And** результат проходит тот же domain validation и guarded publication, что и локальный stage.

**Given** timeout/network/rate/server failure с доказанным `not accepted` либо provider idempotency
**When** retry policy применяется
**Then** выполняется не более двух автоматических повторов
**And** auth, validation, missing model и ambiguous accepted outcome не повторяются автоматически.

**Given** результат внешнего вызова невозможно подтвердить
**When** dispatch остаётся с неоднозначным outcome
**Then** ledger фиксирует `outcomeUnknown`, UI объясняет риск повторной операции и требует явного нового attempt
**And** secret grant отзывается, payload и secret не попадают в durable queue или logs.

### Story 2.8: Наблюдение, восстановление и повтор этапа

Как владелец приложения,
я хочу видеть честный прогресс и восстановить длительное Задание после ошибки или перезапуска,
чтобы продолжить с первого незавершённого этапа без дублирования работы.

**Acceptance Criteria:**

**Given** активный ProcessingJob
**When** открыта поверхность Хода обработки
**Then** `stage-progress` показывает три фиксированных stage, elapsed time, completed states и реальный percent только при наличии данных
**And** при отсутствии percent отображается activity без выдуманного числового значения, heartbeat/progress сохраняется не реже раза в 5 секунд.

**Given** SSE connection
**When** job state меняется
**Then** events используют persisted monotonic revision и replaceable state snapshot, клиент игнорирует stale revisions
**And** один стабильный `role="status" aria-live="polite" aria-atomic="true"` объявляет только semantic transitions, resync и terminal results.

**Given** refresh, connection gap или restart приложения
**When** клиент восстанавливает наблюдение
**Then** cursor возвращает последующие revisions либо current `resync`, REST остаётся источником terminal state
**And** duplicate job/stage attempt не создаётся, завершённые этапы остаются завершёнными.

**Given** retryable failure на конкретном этапе
**When** пользователь выбирает явно названное действие «Повторить [этап]»
**Then** создаётся новая attempt только failed/cancelled stage с тем же snapshot, если upstream output остаётся valid
**And** успешные source, preparedAudio, Transcript или Summary не удаляются из-за ошибки последующего этапа.

**Given** auth/validation/missing-model, waitingForSecret либо `outcomeUnknown`
**When** failure отображается
**Then** `notice-banner` и optional diagnostic detail называют stage, сохранённые данные и одно безопасное действие
**And** actionable error использует alert, heartbeat не объявляется live и фокус самопроизвольно не перемещается.

### Story 2.9: Отмена обработки с сохранением опубликованных результатов

Как владелец приложения,
я хочу отменить выполняемое Задание и сохранить уже завершённые этапы,
чтобы остановить нагрузку и внешние обращения без потери пригодных результатов.

**Acceptance Criteria:**

**Given** running stage
**When** пользователь активирует явно названную кнопку отмены
**Then** UI/API подтверждает запрос не более чем за 1 секунду в p95, state становится «Отменяется», дальнейшие engine calls/dispatch grants запрещаются
**And** обработка достигает safe point не более чем за 10 секунд и фиксирует «Отменено».

**Given** cancel request
**When** worker проходит checkpoint
**Then** completion требует matching attempt/lease/lifecycle epochs, secret и provider grants отзываются, model/artifact leases освобождаются
**And** поздний result становится cancelled/superseded и не публикуется.

**Given** до отмены успешно опубликованы preparedAudio, Transcript или Summary
**When** job становится cancelled
**Then** эти результаты остаются доступны для явного нового запуска либо будущего удаления
**And** partial checkpoints/payloads не выдаются за completed output.

**Given** пользователь нажимает Escape вне специального confirmation
**When** фокус находится на странице обработки
**Then** processing job не отменяется
**And** отмена возможна только отдельным контролом с видимым status feedback и non-color semantics.

**Given** crash во время cancelling
**When** приложение запускается снова
**Then** recovery продолжает cancel/reconciliation до terminal durable state
**And** UI один раз объявляет восстановленное состояние, не создавая новую attempt автоматически.

## Epic 3: Проверяемый и исправляемый результат

Пользователь может изучить Расшифровку и Саммари рядом с сохранённой записью, проверить выводы по evidence, исправить текст или метки спикеров, обновить Саммари и скопировать нужный результат.

### Story 3.1: Доступная Страница Встречи и встроенный плеер

Как владелец приложения,
я хочу открыть завершённую или частично обработанную Встречу и воспроизвести сохранённую запись,
чтобы изучать опубликованные результаты рядом с исходным медиа.

**Acceptance Criteria:**

**Given** переход на Страницу Встречи
**When** route загружается
**Then** page heading получает фокус, а DOM/keyboard/screen-reader order фиксирован как heading → summary state → agreements state → player → metadata → transcript state
**And** отсутствующие ещё результаты имеют явное состояние, а не blank space или fake completed content.

**Given** ready `playbackArtifactId`
**When** browser запрашивает `/api/v1/meetings/{meetingId}/media/playback`
**Then** endpoint stream-ит stored representation без filesystem path, compression или transformation middleware
**And** `GET` без Range возвращает 200, один bounded/open/suffix range — 206, unsatisfiable — 416 с `bytes */N`, malformed/multi-range — 400, `HEAD` игнорирует Range и не возвращает body.

**Given** успешный playback response
**When** Chromium или Firefox открывает audio/video source
**Then** headers содержат identity encoding, правильные Content-Type/Length, `Accept-Ranges: bytes`, strong checksum ETag и inline disposition
**And** native `<audio controls>` или `<video controls>` предоставляет play/pause, position, volume, elapsed/total и fullscreen для видео без autoplay.

**Given** media отсутствует, удаляется либо playback завершился ошибкой
**When** Страница Встречи отображает player
**Then** controls не выглядят доступными, UI показывает явное missing/error state и оставляет текстовые результаты видимыми
**And** API возвращает стабильный `media_not_available`, не раскрывая внутреннее состояние файловой системы.

**Given** wide viewport, narrow viewport, 200% zoom или 320 CSS px
**When** пользователь просматривает Встречу
**Then** wide layout может использовать две зоны и sticky player, который не перекрывает focus/content и останавливается до destructive footer
**And** narrow layout сохраняет canonical order, отключает sticky, не создаёт горизонтальный page scroll и не скрывает actions.

### Story 3.2: Чтение Расшифровки с таймкодами и спикерами

Как владелец приложения,
я хочу читать текущую Расшифровку по Сегментам и переходить к их таймкодам,
чтобы быстро сопоставлять текст с сохранённой речью.

**Acceptance Criteria:**

**Given** опубликованная current Transcript revision
**When** Страница Встречи загружает Расшифровку
**Then** каждый `transcript-segment` имеет stable DOM ID, timestamp, text и optional speaker label в стабильном порядке
**And** partial/invalid output не отображается как завершённая Расшифровка.

**Given** пользователь активирует timestamp мышью или клавиатурой
**When** media доступно
**Then** player seek-ится к `startMs`, Сегмент получает programmatic focus и видимый non-color current marker
**And** воспроизведение не начинается, пока пользователь явно не активирует control с именем «Воспроизвести».

**Given** текущая Transcript допускает создание VTT
**When** captions artifact соответствует её revision
**Then** player подключает `<track kind="captions">`, а пользователь может включить субтитры
**And** при отсутствии актуального VTT показывает «Субтитры недоступны» и сохраняет действие «Открыть расшифровку».

**Given** engine вернул speaker labels
**When** Сегменты отображаются
**Then** label визуально и семантически отличается от participant identity/account state
**And** отсутствие diarization не блокирует чтение или successful Meeting state.

**Given** длинная Расшифровка
**When** пользователь проходит Segments клавиатурой либо screen reader
**Then** порядок остаётся предсказуемым, timestamp targets имеют 44×44, focus видим и не скрывается sticky content
**And** virtualisation, если применена, сохраняет адресуемость evidence target и не ломает browser find/focus contract.

### Story 3.3: Исправление Сегментов и меток спикеров

Как владелец приложения,
я хочу исправлять текст, границы Сегментов и повторяющиеся метки спикеров,
чтобы текущая Расшифровка соответствовала тому, что действительно сказано.

**Acceptance Criteria:**

**Given** current Transcript revision
**When** пользователь открывает редактирование Сегмента
**Then** форма предоставляет явные Save/Cancel, сохраняет исходные значения до успешной команды и помечает dirty state
**And** несохранённая навигация вызывает доступный confirmation, Escape отменяет только текущий edit, не processing job.

**Given** пользователь изменяет text
**When** save проходит с matching revision precondition
**Then** создаётся следующая current Transcript revision, segment ID и допустимые time bounds сохраняются
**And** существующее Summary становится visibly stale без автоматической regeneration.

**Given** пользователь разделяет Сегмент
**When** он выбирает точку внутри исходных границ
**Then** создаются два упорядоченных Сегмента с уникальными IDs и непротиворечивыми bounds внутри исходного интервала
**And** текст не теряется и validator отклоняет пустую или выходящую за границы часть.

**Given** пользователь объединяет соседние Сегменты
**When** command выполняется
**Then** новый Segment покрывает от начала первого до конца последнего, сохраняет порядок текста и валидный speaker state
**And** несоседние, перекрывающиеся либо относящиеся к другой revision Сегменты объединить нельзя.

**Given** пользователь переименовывает speaker label
**When** save подтверждён
**Then** обновляются все matching labels текущей Расшифровки одной командой
**And** participant records/assignments не создаются и не изменяются автоматически.

**Given** другой edit уже создал новую revision
**When** stale client пытается сохранить изменения
**Then** API возвращает стабильный conflict code и актуальную revision, не перезаписывает чужое изменение
**And** UI сохраняет локальный ввод и предлагает безопасно обновить данные.

### Story 3.4: Просмотр структурированного Саммари и договорённостей

Как владелец приложения,
я хочу видеть структурированное Саммари и полный список договорённостей,
чтобы быстро понять темы, решения, задачи и открытые вопросы Встречи.

**Acceptance Criteria:**

**Given** валидное current Summary
**When** Страница Встречи загружается
**Then** `summary-card` показывает обзор, основные темы, решения, задачи, Важные моменты и открытые вопросы
**And** пустой раздел остаётся видимым как «Не обнаружено», чтобы отличаться от loading/error.

**Given** задачи или решения в Summary
**When** формируется полный ordered `agreement-item` list
**Then** каждый элемент показывает текст, importance marker+label, responsible и due только если они выражены в Расшифровке
**And** приложение не требует и не подставляет выдуманное значение.

**Given** Summary metadata
**When** пользователь читает заголовок результата
**Then** видны model identity, generated time и manual/stale/unverified markers, каждый с текстом или значком кроме цвета
**And** version selector и полная история результатов отсутствуют.

**Given** model output с невалидной schema, evidence либо source revision
**When** guarded publication проверяет результат
**Then** старый current Summary не заменяется, stage не считается successful
**And** UI показывает сохранённое состояние и безопасное действие без raw payload.

**Given** light/dark theme, 200% zoom и 320 CSS px
**When** отображаются длинные договорённости
**Then** текст не обрезается, metadata stacks без wide table, important/status semantics не зависят от цвета
**And** visual hierarchy остаётся summary → agreements → evidence без декоративного AI theater.

### Story 3.5: Проверка элемента Саммари по evidence

Как владелец приложения,
я хочу перейти от решения, задачи или Важного момента к подтверждающему фрагменту,
чтобы проверить вывод по текущей Расшифровке и записи.

**Acceptance Criteria:**

**Given** Summary item с EvidenceRef текущей Transcript revision
**When** пользователь активирует `evidence-link`
**Then** `href` разрешается в stable DOM ID Сегмента, player seek-ится к timestamp, target с `tabindex="-1"` получает focus
**And** одно polite announcement называет item, timestamp, speaker при наличии и verified state.

**Given** focused evidence target
**When** transition завершён
**Then** Сегмент показывает видимый marker «Фрагмент подтверждения» и programmatic current state
**And** media playback не запускается без отдельного control «Воспроизвести».

**Given** EvidenceRef отсутствует, сломан либо относится не к current revision
**When** item отображается
**Then** присутствует status «Подтверждение не найдено»/unverified, а false link не создаётся
**And** весь Summary считается не полностью проверяемым, если хотя бы решение или задача не подтверждены.

**Given** media удалено, но current Segment существует
**When** пользователь активирует evidence
**Then** Transcript target всё равно раскрывается и фокусируется, player остаётся в явном unavailable state
**And** интерфейс не создаёт ложную ссылку воспроизведения.

**Given** release corpus и выбранное решение или задача
**When** технически подготовленный пользователь начинает поиск подтверждения
**Then** типовой путь позволяет открыть соответствующий Segment и нужный timestamp менее чем за 2 минуты
**And** benchmark проверяется клавиатурой и pointer input в Chromium и Firefox.

### Story 3.6: Редактирование и повторное создание Саммари

Как владелец приложения,
я хочу исправить текущее Саммари или создать его заново из исправленной Расшифровки,
чтобы сохранить один актуальный и проверяемый результат.

**Acceptance Criteria:**

**Given** current Summary
**When** пользователь редактирует допустимые разделы и сохраняет с matching revision precondition
**Then** текущий результат обновляется атомарно и получает `manualEdit=true`
**And** provenance и evidence status сохраняются либо становятся явно unverified, а старые версии не добавляются в UI.

**Given** вручную изменённое Summary
**When** пользователь выбирает «Создать краткую сводку заново»
**Then** `confirm-dialog` перечисляет заменяемый текущий результат и сохранённые Transcript/media данные, destructive action не фокусируется первым
**And** Cancel/Escape не запускает новое Задание.

**Given** пользователь подтверждает regeneration
**When** создаётся новый job snapshot
**Then** используется current Transcript revision, выбранный summarization engine, язык и инструкции; пригодная transcription помечается `reused` и не выполняется заново
**And** time/model/settings записываются без secret value.

**Given** успешная regeneration
**When** валидный Summary публикуется
**Then** он становится единственным current Summary, stale снимается, EvidenceRefs разрешаются только в source revision
**And** старый payload не хранится как пользовательская история версий.

**Given** regeneration завершилась ошибкой или outcomeUnknown
**When** пользователь возвращается к Странице Встречи
**Then** исправленная Transcript остаётся current, прежнее Summary остаётся видимым как stale, а failure называет безопасный retry
**And** транскрибация не запускается автоматически.

### Story 3.7: Локальное копирование частей результата

Как владелец приложения,
я хочу скопировать отдельный раздел, решение, задачу или Важный момент с контекстом,
чтобы использовать проверяемую часть результата вне приложения.

**Acceptance Criteria:**

**Given** `summary-card` либо `agreement-item`
**When** пользователь активирует именованную copy button
**Then** clipboard получает понятный вне приложения текст с типом элемента, содержанием, ответственным/сроком при наличии и timestamp/evidence status
**And** control имеет цель 44×44, доступное имя и текстовый success/error feedback.

**Given** подтверждённый item
**When** текст копируется
**Then** он содержит timestamp и различимый verification marker
**And** не включает internal IDs, secret, diagnostic metadata или абсолютный filesystem path.

**Given** unverified либо stale item
**When** пользователь копирует его
**Then** соответствующий marker «Подтверждение не найдено» или «Сводка требует обновления» сохраняется в тексте
**And** результат не выглядит проверенным или актуальным вне приложения.

**Given** copy action
**When** browser clipboard API недоступен или запрещён
**Then** UI сохраняет content, сообщает permission failure и предлагает доступный ручной способ выделения
**And** никакого сетевого запроса не выполняется.

### Story 3.8: Воспроизводимая оценка качества результата

Как владелец и сопровождающий проекта,
я хочу получить воспроизводимый отчёт о качестве Расшифровки, Саммари и evidence,
чтобы выпускать локальный baseline только при достижении утверждённых порогов.

**Acceptance Criteria:**

**Given** versioned release corpus
**When** формируется quality run
**Then** он содержит 10 поддерживаемых записей: 5 русских, 3 английских, 2 mixed, длительностью 5–180 минут, включая ≥4 записи с тремя и более спикерами и ≥2 с умеренным шумом/эхом
**And** отдельно включает повреждённый/неподдерживаемый audio и video source для preflight rejection.

**Given** corpus и gold data
**When** фиксируется протокол сопоставления
**Then** документированы единица решения/задачи, правила неоднозначных эталонов, micro/macro aggregation, WER normalization и правило корректной EvidenceRef
**And** versions/checksums corpus, gold Transcript/Summary, models, prompts и ProcessingProfile входят в отчёт.

**Given** восемь русско- и англоязычных поддерживаемых записей
**When** оценивается pinned local ASR
**Then** median WER не превышает 20% для чистой речи и 30% для умеренного шума
**And** mixed speech отчёт выделен отдельно и не блокирует MVP.

**Given** gold decisions/tasks/evidence
**When** оценивается pinned local summarization
**Then** precision ≥90%, recall ≥80% и корректные evidence links ≥90%
**And** каждый элемент без корректного подтверждения сохраняет статус «Подтверждение не найдено» и не засчитывается verified.

**Given** end-to-end local profile run
**When** обрабатываются 10 поддерживаемых и 2 rejected sources
**Then** не менее 9 из 10 поддерживаемых завершаются без потери данных/ручного вмешательства в БД, оба invalid sources отклоняются до job creation
**And** каждый supported source воспроизводится и seek-ится в Chromium/Firefox, а fully local processing не создаёт content egress.

**Given** любой недостигнутый quality/resource/license/accessibility gate
**When** release report завершается
**Then** выпуск блокируется с точным нарушенным threshold и evidence artifact
**And** model candidate заменяется за engine port без изменения domain/API contracts.

## Epic 4: Организованный и управляемый архив

Пользователь может дополнить Встречи Тегами, Участниками и связью с Внешней задачей, найти нужные материалы, экспортировать их и безопасно удалить медиа либо всю Встречу.

### Story 4.1: Управление ручными и автоматическими Тегами Встречи

Как владелец приложения,
я хочу изменять Теги конкретной Встречи и контролировать автоматически предложенные темы,
чтобы организовать архив без глобального изменения других Встреч.

**Acceptance Criteria:**

**Given** Страница Встречи
**When** пользователь создаёт, редактирует или удаляет `tag-chip`
**Then** одна application command атомарно изменяет только Tag set этой Meeting
**And** изменение не затрагивает другие Встречи и не удаляет их материалы.

**Given** успешная публикация нового Summary
**When** structured output содержит валидные `autoTags`
**Then** Summary и нормализованные/дедуплицированные auto tags публикуются одной транзакцией
**And** failed summarization не создаёт и не меняет auto tags.

**Given** существующие manual и auto tags
**When** новая успешная summarization публикуется
**Then** заменяются только предыдущие `origin=auto`, manual tags сохраняются
**And** edit auto tag сначала переводит его в manual, а explicit regeneration может снова предложить ранее удалённый auto tag.

**Given** обычный просмотр и edit mode
**When** Теги отображаются
**Then** origin виден только в edit mode и не меняет правила будущего поиска/фильтрации
**And** multi-select объявляет selected count, а remove controls имеют конкретные имена и размер 44×44.

**Given** storage/conflict failure
**When** save не проходит
**Then** UI сохраняет локальный набор, показывает стабильный code и безопасный retry
**And** stale client не перезаписывает более новую Tag set revision.

### Story 4.2: Локальный Справочник участников и назначения Встречам

Как владелец приложения,
я хочу вести локальный справочник людей и назначать нескольких Участников Встрече,
чтобы находить архив по фактическому составу встреч без создания аккаунтов и ролей.

**Acceptance Criteria:**

**Given** пустая поверхность Участников
**When** пользователь создаёт запись с именем и optional note
**Then** Participant сохраняется локально и появляется в directory
**And** одинаковые имена допустимы, если записи различаются заметкой; validation и error summary доступны с клавиатуры.

**Given** существующие Participant records
**When** пользователь ищет, редактирует или выбирает нескольких для Meeting
**Then** directory поддерживает populated/search/no-match states, а assignment меняет только metadata связи
**And** `participant-chip` объявляет count и предоставляет именованное 44×44 removal action.

**Given** назначенный Participant
**When** пользователь изменяет запись или назначение
**Then** speaker labels, Transcript Segments, identity и access state остаются неизменными
**And** UI визуально отличает Participant от speaker/account presence.

**Given** удаление Participant, связанного с Встречами
**When** открывается `confirm-dialog`
**Then** dialog показывает точное число затронутых Встреч, последствия detach и сохранение Расшифровок
**And** destructive action не имеет initial focus, Cancel/Escape не меняет данные.

**Given** пользователь подтверждает удаление
**When** command фиксируется
**Then** Participant и все его Meeting assignments удаляются атомарно
**And** Tags, speaker labels, Segments, Summaries и media не изменяются; failure сохраняет форму и перечисляет оставшееся состояние.

### Story 4.3: Связь Встречи с существующей Внешней задачей

Как владелец приложения,
я хочу сохранить URL и номер одной существующей Внешней задачи,
чтобы вернуться из локального архива к связанному рабочему контексту без API-интеграции.

**Acceptance Criteria:**

**Given** metadata edit Страницы Встречи
**When** пользователь вставляет task URL
**Then** приложение пытается извлечь display number, показывает результат и позволяет исправить его вручную до сохранения
**And** failure extraction сохраняет URL и предлагает ввести номер, не теряя связь.

**Given** display task number
**When** metadata сохраняется
**Then** backend сохраняет исходное `taskNumber` и отдельно вычисляет backend-only normal form через Unicode NFKC, trim Unicode White_Space и full casefold в UTF-8 BLOB
**And** пустые/control-only normalized значения отклоняются, client не вычисляет нормализацию.

**Given** сохранённая связь
**When** `task-link-card` отображается
**Then** номер является первым визуальным уровнем, внешний glyph/notice явно обозначает переход, edit state показывает URL/extraction metadata
**And** URL открывается в новой вкладке только по явному действию.

**Given** создание, чтение или редактирование связи
**When** операция завершается
**Then** приложение не обращается к task-tracker API, не создаёт задачу, не получает атрибуты и не синхронизирует статус
**And** отсутствие сети не мешает локально сохранить или показать связь.

**Given** пользователь удаляет URL и/или номер
**When** save подтверждён
**Then** поля и derived normalized value очищаются согласованно одной command
**And** Meeting, Transcript, Summary и прочие metadata остаются неизменными.

### Story 4.4: Локальный поиск и фильтрация архива

Как владелец приложения,
я хочу искать по содержимому и фильтровать Встречи по локальным метаданным,
чтобы быстро восстановить старое решение, участника или номер задачи без внешнего сервиса.

**Acceptance Criteria:**

**Given** публикация или изменение title/current Transcript/current Summary
**When** command фиксируется
**Then** SQLite FTS5 обновляется в той же транзакции из authoritative tables
**And** stale versions, secret и удалённые records отсутствуют в поисковом индексе.

**Given** task-number metadata
**When** пользователь выбирает exact или prefix lookup/filter
**Then** non-unique partial B-tree по `(task_number_norm,id)` обслуживает BLOB bounds `key=:p` либо `key>=:p AND key<:p+0xFF`
**And** fuzzy, contains, FTS и semantic fallback для task number запрещены.

**Given** search text и filters date/status/tags/participants/taskNumber
**When** выполняется `/api/v1/meetings` query
**Then** repeated values образуют OR внутри facet, facets и date range — AND, taskNumber принимается только с `taskNumberMatch=exact|prefix`
**And** bounded limit/opaque cursor связан с filter/sort digest и не может быть переиспользован с другим запросом.

**Given** results page
**When** matches найдены
**Then** каждый hit показывает Meeting, typed matched field/context/snippet и match kind, response возвращает canonical filter echo и nextCursor
**And** URL использует те же query names/repetition, поэтому opening hit и Back восстанавливают поиск и filters.

**Given** совпадений нет
**When** query завершается
**Then** API возвращает 200 с пустой page и filter echo, UI сохраняет запрос и предлагает очистить filters
**And** task-number no-hit явно объясняет structured local exact/prefix path и не создаёт semantic result.

**Given** 1 000 Встреч и активная local compute-нагрузка
**When** выполняются FTS, structured lookup, pagination и index rebuild/repair
**Then** library/navigation budget ≤2 s и UI/API p95 ≤1 s подтверждены benchmark
**And** repair детерминированно восстанавливает оба индекса из authoritative tables, называя affected local path при недоступности.

### Story 4.5: Локальный экспорт результатов Встречи

Как владелец приложения,
я хочу экспортировать Саммари, Расшифровку или структурированные данные в переносимом формате,
чтобы использовать архив в других локальных инструментах.

**Acceptance Criteria:**

**Given** Страница Встречи
**When** пользователь открывает `export-menu`
**Then** trigger имеет accessible name, `aria-expanded`/`aria-controls`, menu поддерживает Arrow/Tab/Escape/outside-close и focus return
**And** каждая строка явно называет format и включаемое содержимое.

**Given** выбор Markdown
**When** export формируется
**Then** файл содержит полное current Summary, Meeting metadata, решения/задачи/highlights, timestamps и evidence status
**And** включает model identity и manual/stale/unverified markers.

**Given** выбор TXT или VTT
**When** export формируется
**Then** TXT содержит текущий ordered Transcript, VTT — валидные cues из current revision с timestamps и speaker labels при наличии
**And** stale captions artifact не используется.

**Given** выбор JSON
**When** export формируется
**Then** versioned schema содержит Meeting, current Transcript/Summary provenance, Tags, Participant assignments, task number и URL
**And** IDs/time/offsets соответствуют UUIDv7, RFC 3339 UTC и integer ms contracts.

**Given** любой export
**When** генерация выполняется
**Then** файл создаётся локально и исключает secret, internal diagnostics, provider payload и абсолютные filesystem paths
**And** success имеет текстовый feedback, write/permission failure сохраняет menu state и предлагает retry.

### Story 4.6: Удаление медиа с сохранением текста

Как владелец приложения,
я хочу освободить место, удалив Исходную запись и производные media после успешной обработки,
чтобы сохранить Расшифровку, Саммари и metadata без недействующих controls.

**Acceptance Criteria:**

**Given** Meeting с successful job и без active job
**When** пользователь выбирает media-only delete
**Then** `confirm-dialog` перечисляет source/prepared/playback artifacts, общий disk volume и сохраняемые Transcript/Summary/Tags/Participants/task link
**And** destructive action отделён, не имеет initial focus, Cancel/Escape ничего не удаляет.

**Given** пользователь подтверждает media-only delete
**When** command проходит CAS
**Then** Meeting переходит в `mediaDeleting`, lifecycle epoch увеличивается, создаётся persisted `DeleteIntent(scope=media)`
**And** новые mutations/artifact grants/leases/renewals запрещаются, active streams закрываются на safe boundary.

**Given** persisted artifact leases
**When** deletion intent исполняется
**Then** система ждёт release/expiry, каждый reader/worker проверяет lifecycle epoch перед chunk, после чего unlink выполняется идемпотентно
**And** crash/restart продолжает intent, не сообщает преждевременный success.

**Given** все media artifacts удалены
**When** финальная транзакция завершается
**Then** source/prepared/playback slots и artifact rows очищаются, Meeting возвращается в `active`, text/metadata/FTS сохраняются
**And** player показывает «Запись недоступна», evidence продолжает фокусировать Transcript без false playback link.

**Given** active job, незавершённый lease либо частичная filesystem error
**When** удалить media безопасно нельзя
**Then** UI не сообщает успех, показывает persisted intent/remaining artifacts и действие retry/wait
**And** Meeting остаётся в согласованном восстанавливаемом состоянии.

### Story 4.7: Полное crash-safe удаление Встречи

Как владелец приложения,
я хочу полностью удалить Встречу и все связанные материалы после явного подтверждения,
чтобы она не оставалась ни в библиотеке, ни в управляемом хранилище.

**Acceptance Criteria:**

**Given** существующая Meeting
**When** пользователь выбирает полное удаление
**Then** confirmation перечисляет media, Transcript, Summary, Tags, Participant links, task link, FTS/index data и job-linked artifacts
**And** показывает последствия/объём, safe action получает initial focus, destructive action требует явного выбора.

**Given** подтверждённый full delete
**When** command проходит lifecycle CAS
**Then** Meeting становится `deleting`, lifecycle epoch увеличивается, создаётся `DeleteIntent(scope=meeting)`, обычные reads скрывают Meeting
**And** новые mutations, jobs, streams, leases и grants запрещены.

**Given** readers/workers и dependent artifacts
**When** intent исполняется
**Then** streams закрываются, renew запрещён, система ждёт release/expiry и идемпотентно удаляет managed files
**And** late stage completion не может опубликовать данные после нового lifecycle epoch.

**Given** filesystem cleanup успешно завершён
**When** финальная SQLite-транзакция фиксируется
**Then** удаляются Meeting, dependent rows, FTS/structured index entries и tombstone по правилам reconciliation
**And** библиотека, search и direct route больше не отображают Встречу.

**Given** crash или частичная ошибка на любом шаге
**When** приложение перезапускается либо пользователь открывает состояние удаления
**Then** startup reconciliation продолжает persisted intent, UI показывает remaining materials и retry
**And** partial cleanup никогда не маскируется под complete success и не возвращает Meeting к обычным mutations самопроизвольно.

### Story 4.8: Резервное копирование, обновление и восстановление архива

Как технически подготовленный владелец,
я хочу создать согласованную резервную копию и безопасно обновить или восстановить локальный архив,
чтобы не потерять записи, результаты и metadata при изменении версии приложения.

**Acceptance Criteria:**

**Given** запрос update/backup
**When** maintenance gate начинается
**Then** берётся persisted exclusive lock, новые mutations/leases запрещаются, workers drain/cancel-ятся, UI переходит в read-only maintenance state
**And** пользователь видит причину и не получает небезопасное retry действие.

**Given** достаточно места
**When** создаётся backup generation
**Then** manifest перечисляет согласованный SQLite snapshot и точные ready artifacts с checksums, включая media, results, Tags, Participants и task links
**And** generation получает `complete` только после проверки каждого элемента; incomplete backup не используется для migration/restore.

**Given** complete pre-migration backup
**When** Alembic выполняет update
**Then** применяется один linear forward-only head до запуска API/workers
**And** failure не запускает services на смешанной schema и сохраняет проверенный backup/recovery instructions.

**Given** выбранная complete backup generation
**When** владелец выполняет restore
**Then** система разворачивает данные в новую generation, проверяет schema/artifact checksums и только затем делает recoverable atomic pointer switch
**And** failure до switch оставляет текущую generation активной, rollback запускает pinned совместимую app version.

**Given** публичная документация выпуска
**When** новый пользователь выполняет backup/update/restore drill на Linux, macOS или Windows
**Then** описаны локальные каталоги, expected downtime, проверка объёма/manifest, восстановление media и всех metadata
**And** fault-injection test подтверждает recovery после interruption на создании manifest, migration и pointer switch.

**Given** release candidate полного MVP
**When** формируется release manifest
**Then** images/runtime/models/sources/checksums/licenses, FFmpeg flags/codecs, PyAV provenance, NOTICE и SBOM зафиксированы
**And** install ≤20 минут без model download, restore drill, performance, quality, accessibility и three-OS/browser gates обязательны до публичного выпуска.
