# Сверка Architecture Spine с техническим приложением PRD

**Проверенные источники:** `ARCHITECTURE-SPINE.md`, `addendum.md`  
**Область:** только архитектурно значимые ограничения, предварительные решения и четыре вопроса архитектурной передачи.  
**Вердикт:** **частично согласовано; до реализации остаются четыре небезопасных разрыва и два неполных контракта.** Прямого отказа от обязательных требований нет, но некоторые правила сформулированы слабее, чем границы данных и поставки в addendum.

## Разрывы, требующие исправления

### R-1 — [HIGH][UNSAFE] Provider worker имеет слишком широкую границу доступа к данным

- **Источник:** обязательный локальный вход в виде Исходного видео; предварительное решение локально извлекать аудио и не отправлять видеодорожку; §7.1 разрешает внешнему этапу только необходимые данные.
- **Что попало в spine:** `prepare → transcribe → summarize` (AD-3), media adapter, processing egress только у `provider-worker` (AD-5).
- **Что не попало / чем опасно:** диаграмма даёт `provider-worker` доступ к общему `DATA`, где вместе показаны SQLite и meeting data volume. Правило не запрещает этому контейнеру читать Исходное видео, расшифровки или артефакты другого этапа. Наличие egress превращает широкое монтирование в реальную возможность отправить больше данных, чем разрешено.
- **Что должен зафиксировать spine:** `prepare` всегда выполняется локально и публикует отдельный подготовленный аудио-артефакт; provider adapter получает только stage-scoped read-only input и не монтирует корень данных Встреч. Для transcription разрешён подготовленный audio, для summarization — необходимый transcript/chunks; исходное video недоступно provider worker.

### R-2 — [HIGH][PARTIAL] Независимый выбор движков не закреплён как инвариант композиции Профиля

- **Источник:** обязательное независимое сочетание local/provider для транскрибации и суммаризации; предварительно для внешних движков нужны отдельные base URL, secret reference и model ID.
- **Что попало в spine:** разные ports `TranscriptionEngine` и `SummarizationEngine`, разные request/result/error (AD-4), engine фиксируется на попытке, секрет отделён через `secretRef` (AD-6).
- **Что не попало / чем опасно:** нет прямого правила, что `ProcessingProfile` содержит две независимые stage configurations и допускает все четыре сочетания local/local, local/provider, provider/local, provider/provider. `capability snapshot` не заменяет владение endpoint/model/secretRef каждого этапа. Две реализации могут несовместимо решить, что один profile обязан использовать общий режим или общего provider.
- **Что должен зафиксировать spine:** отдельная `TranscriptionStageConfig` и `SummarizationStageConfig`, каждая со своим engine kind, endpoint/base URL, model ID, capability snapshot и optional secretRef; job хранит неизменяемый snapshot обеих конфигураций.

### R-3 — [HIGH][UNSAFE] Контракт секретов для Compose описан намерением, а не реализуемой границей

- **Источник:** вопрос передачи №2 и §7.1: DB хранит только ссылку; без защищённого хранилища ключ живёт только при запуске/в сессии; требование действует и для контейнерного запуска.
- **Что попало в spine:** runtime-only credential broker, `secretRef`, session invalidation, `waitingForSecret`, stage-scoped выдача по «приватному каналу» (AD-6).
- **Что не попало / чем опасно:** не определены допустимые secret backends для host и Compose, идентичность вызывающего worker, протокол получения/отзыва, защита канала и запрет передачи значения через persisted Compose config, CLI arguments или durable queue. Термин «приватный канал» допускает несовместимые и небезопасные реализации. Неясно также, какой компонент владеет secretRef lifecycle и маскированием после проверки Профиля.
- **Что должен зафиксировать spine:** минимальный secret-provider port и один поддерживаемый Compose flow (например, runtime injection или memory session broker); ключ никогда не записывается в Compose YAML/env-file/DB/job/event; worker аутентифицируется и получает ключ по attempt-scoped opaque grant с TTL/revocation; transport и redaction rules называются явно. Если защищённый OS store не входит в MVP, это должно быть явным deferred, а не неявным вариантом.

### R-4 — [HIGH][UNSAFE] Local baseline выбран до обязательной cross-platform и license-проверки

- **Источник:** предварительное решение и вопрос передачи №1: один поддерживаемый local ASR и LLM путь выбирается после license/performance проверки на 16 ГБ; NFR-7 требует Compose на Linux, macOS и Windows; до публикации нужна проверка совместимости лицензий.
- **Что попало в spine:** faster-whisper + Whisper large-v3-turbo CT2 и llama.cpp + Qwen3-4B-GGUF Q4_K_M как `[ASSUMPTION]`; CPU/int8 baseline, release corpus и 16-GB gate (AD-12, Deferred).
- **Что не попало / чем опасно:** gate не требует прохождения Linux/macOS/Windows, проверки лицензии каждой модели, runtime и распространяемого артефакта, проверки способа загрузки/redistribution и воспроизводимого container build. Текущий Deferred допускает promotion после теста на одном 16-GB CPU host.
- **Что должен зафиксировать spine:** кандидаты не становятся supported baseline до матрицы Linux/macOS/Windows × 16-GB CPU, corpus quality/resource gates и license/redistribution review; release manifest/SBOM фиксирует модель, runtime, источник, checksum и лицензионные сведения. Провал любого gate оставляет замену за AD-4 ports.

### R-5 — [MEDIUM][VERIFICATION GAP] FTS5 выбран, но соответствие NFR-2 не доказано и не ограждено gate

- **Источник:** вопрос передачи №4: локальная реализация поиска должна обеспечить NFR-2 без внешнего сервиса.
- **Что попало в spine:** SQLite FTS5, транзакционное индексирование, lexical-only поиск, локальный snippet (AD-9).
- **Что не попало / чем опасно:** нет release gate на корпусе до 1 000 Встреч, лимита/пагинации запроса, стратегии rebuild/repair и измерения при параллельной локальной обработке. Сам выбор FTS5 отвечает границе приватности, но ещё не отвечает измеримой части NFR-2.
- **Что должен зафиксировать spine:** benchmark/release gate для library/search на целевом объёме и во время compute-heavy job; bounded paginated query; детерминированный rebuild FTS из авторитетных таблиц. Конкретные SQL indexes могут оставаться code-owned.

### R-6 — [MEDIUM][MISSING] Open-source/license supply-chain constraint исчез из spine

- **Источник:** локальное однопользовательское приложение распространяется как исходный код; Apache License 2.0; перед публикацией проверяются модели и зависимости.
- **Что попало в spine:** Compose/release manifest и конкретный stack; frontmatter формально bind'ит NFR-1..10.
- **Что не попало / чем опасно:** ни одно AD/convention/deferred не делает Apache-2.0 release и compatibility review обязательным. Выбранные модели, binaries и container layers могут сделать заявленный способ распространения юридически или технически невоспроизводимым.
- **Что должен зафиксировать spine:** release gate с root Apache-2.0 license, dependency/model notices, SBOM, source/model attribution и compatibility/redistribution check до публикации образов и model manifest.

## Обязательные ограничения addendum

| Ограничение | Статус | Архитектурное покрытие |
| --- | --- | --- |
| Вход — видео рабочей встречи | **Частично** | `Meeting`/`MediaArtifact` и media adapter есть, но входной video contract и обязательная локальная подготовка audio не закреплены; см. R-1. |
| ASR и LLM независимо выбираются local/provider | **Частично** | Раздельные ports есть (AD-4), но композиция Profile не закреплена; см. R-2. |
| Локальное single-user приложение, исходный код для самостоятельной установки | **Частично** | Loopback и отсутствие multi-user/auth согласованы (AD-5, Deferred); open-source/license delivery rule отсутствует; см. R-6. |
| Структурированные данные в SQLite, крупные media в managed filesystem | **Попало** | AD-2 прямо фиксирует владельцев, relative artifact ID, checksum и atomic publish. |
| Автоматический fallback local → provider запрещён | **Попало** | AD-4 прямо запрещает автоматическую замену engine. |
| Summary содержит evidence на transcript segments и timecodes | **Попало** | AD-7 и AD-8 фиксируют stable segment IDs, `startMs`/`endMs`, validation и stale/unverified semantics. |

## Предварительные решения addendum

| Предварительное решение | Статус | Архитектурное покрытие |
| --- | --- | --- |
| Docker Compose, UI только loopback | **Попало как `[ASSUMPTION]`** | AD-5 называет topology и binds `127.0.0.1`/`::1`. |
| Раздельные base URL, API key и model ID внешних ASR/LLM | **Частично** | Раздельные ports и `secretRef` есть, владение двумя stage configs не определено; R-2/R-3. Хранение открытого API key справедливо отклонено в пользу §7.1 PRD. |
| Аудио извлекается локально, video не отправляется без необходимости | **Небезопасно** | `prepare` есть, но provider worker видит общий `DATA`; R-1. |
| Один поддерживаемый local ASR и LLM путь после 16-GB/license validation | **Частично / небезопасно** | Кандидаты и runtime названы, но promotion gate неполон; R-4. |
| Durable multi-stage job и retry отдельного этапа | **Попало** | AD-3 задаёт state machine, lease/heartbeat, fingerprints, checkpoints, retry/cancel. |
| Diarization необязательна; полученные speaker labels сохраняются и редактируются | **Попало / корректно deferred** | Domain contract сохраняет labels, adapter выбора diarization deferred; capability map покрывает FR-9–12. Успех pipeline от diarization не зависит. |
| Source video сохраняется по умолчанию; size виден; можно удалить, сохранив text | **В основном попало** | AD-2 хранит size и filesystem artifact, model отделяет media от transcript/summary. Политика default retention остаётся продуктовым правилом; при реализации нужно сохранить nullable media lifecycle. |
| Apache-2.0 и license compatibility до публикации | **Не попало** | См. R-6. |

## Четыре вопроса архитектурной передачи

| № | Решение в spine | Вердикт |
| --- | --- | --- |
| 1. Local models/runtimes на трёх ОС | AD-12 выбирает faster-whisper/Whisper и llama.cpp/Qwen как кандидатов | **Частичный ответ, небезопасен для handoff:** нет трёх-ОС и license/redistribution gate; R-4. |
| 2. Защита секретов во всех launch variants, включая containers | AD-6 выбирает `secretRef` + runtime memory broker | **Частичный ответ, небезопасен для реализации:** «приватный канал» и Compose flow не определены; R-3. |
| 3. Миграции, backup и restore с видео | AD-10: linear Alembic, pre-upgrade backup, maintenance snapshot, media manifest/checksums, verified restore | **Попало достаточно:** единица согласованности DB+media и порядок restore названы. Низкоуровневый формат остаётся code-owned. |
| 4. Локальный поиск с NFR-2 | AD-9 выбирает transactional SQLite FTS5 | **Архитектура выбрана, verification gap остаётся:** нет performance/rebuild gate; R-5. |

## Итоговый приоритет

Перед передачей builder'ам нужно закрыть R-1–R-4. R-5 можно оставить `[ASSUMPTION]` только с явным release gate и revisit condition. R-6 должен стать обязательным release invariant до фиксации распространяемого stack/model manifest. AD-2, AD-3, AD-4 (запрет fallback), AD-7/8 и AD-10 согласованы с addendum и не требуют пересмотра по результатам этой сверки.
