# Reviewer Gate — rubric walker

Дата: 2026-08-31  
Артефакт: `ARCHITECTURE-SPINE.md`  
Источники: `prd.md`, `addendum.md`

## Вердикт

**Не проходит Finalize без исправлений.** Spine хорошо фиксирует модульные границы, локальность, staged processing, provenance и release budgets, но шесть high-находок оставляют несколько взаимно несовместимых реализаций формально соответствующими правилам. Главные риски — crash-consistency между SQLite и файловой системой, неполная state machine, неисполняемый security contract provider-контура и противоречие жизненного цикла локальных моделей заявленному лимиту памяти.

Сводка: **critical 0 · high 6 · medium 8 · low 2**.

## High

### H1 — Нет crash-consistent протокола для SQLite + filesystem

- **Где:** AD-2, AD-13; косвенно AD-10.
- **Почему это divergence:** `rename` и SQLite commit не образуют общую атомарную транзакцию. Одна реализация может сначала переименовать файл и оставить orphan при DB failure, другая — сначала commit-нуть ссылку и оставить missing artifact при rename/crash. Состояние `deleting` описано только названием, без порядка, идемпотентности и startup recovery. Это противоречит FR-1/2/4, NFR-4 и собственному `Prevents` AD-2/13.
- **Действие:** **autofix.** Зафиксировать фазовый протокол (`staging/publishing/ready`, `deleting`) с authoritative DB marker, детерминированным порядком fsync/rename/commit, idempotent startup reconciler и правилами orphan/missing cleanup. Полный delete должен перечислять DB rows, FTS rows, media/derived artifacts и transient attempt files; source-only delete — отдельная команда, не удаляющая text results.

### H2 — State machine не определяет конкурентные переходы и восстановление

- **Где:** AD-3, AD-7, AD-11.
- **Почему это divergence:** правило перечисляет happy-path stages, но не canonical job/attempt states, допустимые transitions, atomic claim/CAS, lease expiry, поведение после crash, terminal cancel и `waitingForSecret`. Не определено, что retry upstream-stage делает с downstream results: повтор transcription может оставить summary формально current. Два worker-а могут по-разному считать expired lease и публиковать разные outputs.
- **Действие:** **autofix.** Зафиксировать transition table/invariant: один active job enforced DB constraint; claim и publish через compare-and-swap по attempt/version; lease expiry возвращает attempt в recoverable state; late output от stale lease отвергается; retry upstream увеличивает transcript revision и invalidates downstream fingerprints/summary; terminal states и безопасные restart/cancel paths перечислены явно.

### H3 — Provider privacy/security boundary названа, но не исполнима одинаково

- **Где:** AD-5, AD-6, conventions.
- **Почему это divergence:** `authenticated internal RPC` не определяет service identity/transport, а `process environment` допускает ключ в container configuration, что конфликтует с «runtime only» и запретом env-file. Нет правила HTTPS для non-loopback endpoint, lifetime/zeroization provider payload/temp buffers и fingerprint-а согласия. Согласие на старую конфигурацию может считаться действующим после смены endpoint/model/data category. Это затрагивает главное продуктовые обещание FR-5/7, NFR-1 и SM-5.
- **Действие:** **discuss/autofix.** Выбрать один concrete broker/RPC flow и аутентификацию workload-а; запретить provider secret в container env/inspectable config; разрешить plain HTTP только loopback, для внешнего endpoint требовать TLS; consent key сделать hash от stage + provider identity + endpoint origin + model + data categories + profile revision и инвалидировать при изменении; provider-worker не должен durable-buffer-ить payload, а grant/result должны быть attempt-bound и rejected после revoke/lease loss.

### H4 — Capability manifest не превращён в gate полного пользовательского пути

- **Где:** AD-4, AD-7/8; Deferred «ASR chunk overlap/dedup».
- **Почему это divergence:** PRD запрещает использовать timestamp-less transcription там, где нужны evidence links, но spine только хранит capability manifest. Не сказано, кто и когда отклоняет несовместимый профиль. Также не закреплены семантические postconditions сегментов (stable unique ID, monotonic valid offsets, отсутствие недопустимого overlap/duplication) и summary evidence. Полное владение dedup алгоритмом adapter-ом не защищает domain contract.
- **Действие:** **autofix.** Application/profile validation обязан до save/run проверять required capabilities конкретного пути; end-to-end profile требует timestamped segments. Нормализатор adapter boundary валидирует IDs, offset range/order и evidence references; invalid output не публикуется как completed stage. Сам алгоритм chunking/dedup может остаться deferred, но его observable postconditions — нет.

### H5 — Топология `llama-server` противоречит последовательной загрузке моделей

- **Где:** AD-12 и deployment diagram.
- **Почему это divergence:** отдельный постоянно запущенный `llama-server` обычно может держать LLM в памяти одновременно с in-process faster-whisper, тогда как AD-12 обещает строго последовательную загрузку на 16 GB. Spine не назначает владельца start/load/unload/readiness, поэтому две compliant реализации дадут разный peak RSS и одна нарушит baseline.
- **Действие:** **autofix.** Зафиксировать model lifecycle: ASR unload подтверждается до LLM load; `llama-server` запускается/загружает модель on-demand либо управляется supervisor-ом и выгружается после stage; worker начинает stage только после readiness и memory preflight. Release gate должен измерять peak RSS всего Compose topology, а не отдельного процесса.

### H6 — Upgrade/backup protocol не определяет безопасный исход ошибки

- **Где:** AD-10.
- **Почему это divergence:** maintenance mode и pre-upgrade backup полезны, но не определены atomic publication backup-а, проверка свободного места, поведение при migration failure и выбор authority после частично выполненной forward-only migration. «Restore до замены» не говорит, как приложение возвращается к совместимой версии schema/code.
- **Действие:** **autofix.** Migration gate до поднятия API/workers: exclusive lock, capacity preflight, consistent DB+artifact manifest snapshot, checksum, atomic mark `complete`; затем migration. При failure сервисы не стартуют, backup и совместимый image/version остаются указанным recovery path. Неполный backup никогда не предлагается для restore; совместимость manifest/schema/app version проверяется до swap.

## Medium

### M1 — Snapshot профиля не охватывает все настройки FR-8

- **Где:** AD-4/5.
- **Проблема:** перечислены engine, endpoint, model, capabilities и secretRef, но не закреплены summary language, additional instructions/default-instructions revision и transcription language. При retry разные компоненты могут читать live profile вместо immutable job snapshot.
- **Действие:** **autofix.** Добавить эти поля/версии в immutable stage snapshots; retry использует snapshot либо явную новую ревизию с новым fingerprint.

### M2 — SSE resume contract неоднозначен

- **Где:** AD-11.
- **Проблема:** `Last-Event-ID` требует определённого retention/replay, но сказано лишь «server state authoritative». После restart одна реализация replay-ит durable events, другая отправляет snapshot без protocol marker.
- **Действие:** **autofix.** Выбрать: durable bounded event log или canonical snapshot event при gap/restart; определить monotonic scope, gap response и terminal event semantics.

### M3 — NFR-6, NFR-10 и SM-6 заявлены в map, но не имеют gate

- **Где:** Capability Map, AD-14/15.
- **Проблема:** нет архитектурного/release требования для keyboard access, labels/non-color status, one-screen happy path и fresh-install ≤20 min. Map утверждает покрытие NFR-1–10, которого правила не дают.
- **Действие:** **autofix.** Добавить UI accessibility smoke/automated gate, UX happy-path acceptance и timed clean-host Compose install test на трёх ОС (загрузка моделей исключена).

### M4 — Model-fetch supply-chain path недостаточно зафиксирован

- **Где:** AD-5, AD-12/14.
- **Проблема:** release manifest фиксирует checksum/license, но runtime `model-fetch` может опубликовать неполную или неверную загрузку; stack показывает сокращённые revisions. Нет правила download staging → checksum/license/source verification → atomic publish.
- **Действие:** **autofix.** Model-fetch принимает только allowlisted full immutable revision + checksum из manifest, скачивает в staging, проверяет размер/hash/license metadata и атомарно публикует; failure не меняет active model.

### M5 — Операционный envelope неполон

- **Где:** AD-5, AD-10, AD-15.
- **Проблема:** отсутствуют readiness/health dependency order, graceful shutdown deadlines, restart policy, disk-low/disk-full behavior и права каталогов. Это определяет, стартует ли worker до migration, сохраняется ли heartbeat при shutdown и как 5-GB import не повреждает данные.
- **Действие:** **autofix.** Добавить deploy convention: migration-complete/readiness gates, bounded graceful shutdown с lease release/checkpoint, no restart loop on config/migration errors, capacity preflight and explicit ENOSPC error, data dirs least-privilege.

### M6 — Media playback contract не гарантирует переход по таймкоду

- **Где:** AD-11/13, Structural Seed.
- **Проблема:** FR-10 требует seek в сохранённом видео, но API/media adapter не обязан поддерживать HTTP byte ranges/content type; на файлах до 5 GB наивная выдача несовместима с NFR-2/3.
- **Действие:** **autofix.** Зафиксировать loopback media endpoint с validated artifact ID, Range/HEAD, streaming and no path traversal; отсутствие source file возвращает domain status, не broken URL.

### M7 — Search release benchmark и repair protocol не enforceable

- **Где:** AD-9, AD-15.
- **Проблема:** «проходит benchmark» не задаёт threshold для search, dataset/query mix и момент repair. Rebuild может блокировать UI или публиковать частичный индекс.
- **Действие:** **autofix/defer.** Привязать search/list gate к ≤2 s либо явно утвердить отдельный threshold; зафиксировать corpus 1000 meetings, concurrent compute и bounded page size. Rebuild строит shadow index и делает atomic swap либо помечает search unavailable до целостного completion.

### M8 — Fast-path assumptions не имеют индивидуальных revisit conditions

- **Где:** Deferred «Fast-path assumptions».
- **Проблема:** единая фраза «remain reviewable» не указывает владельца/триггер/срок для AD-1, 5, 6, 8–12. Особенно AD-6/10 нельзя безопасно отложить за implementation seam.
- **Действие:** **autofix.** Для каждого оставшегося assumption добавить concrete gate: dependency tests before first module, security threat review before provider-profile implementation, schema fixture before summarization, benchmark before search, restore drill before migrations, contract test before frontend, model corpus/16-GB gate before local feature-complete.

## Low

### L1 — Capability Map чрезмерно агрегирует NFR

- **Где:** последняя строка Capability Map.
- **Проблема:** `NFR-1–10 → AD-2–6, AD-10–15` скрывает фактические пробелы и делает traceability непроверяемой.
- **Действие:** **autofix.** Разбить минимум на privacy, performance, reliability, accessibility, distribution/license и simplicity с точными AD/gate ссылками.

### L2 — Версионирование domain/export schemas не названо

- **Где:** AD-8, AD-11, FR-20 mapping.
- **Проблема:** API version указан, но JSON export и structured summary schema могут эволюционировать без discriminator/version; импорт/restore/consumer tooling станет неоднозначным.
- **Действие:** **defer с условием.** Добавить `schemaVersion` в JSON export и summary payload до первого публичного release; detailed schema может остаться code-owned.

## Checklist coverage

| Rubric item | Оценка | Комментарий |
| --- | --- | --- |
| Реальные divergence points зафиксированы | Partial | Основные seams выбраны удачно; H1–H6 остаются архитектурными, а не code-level деталями. |
| Rule каждого AD enforceable и соответствует Prevents | Fail | AD-3/5/6/10/12/13 допускают несовместимые реализации; AD-9 benchmark без pass criterion. |
| Deferred не допускает divergence | Fail | Dedup semantic postconditions и общий список assumptions отложены слишком широко. |
| Named tech verified-current | Partial | Версии и official links присутствуют; отдельный version-fit reviewer должен подтвердить актуальность. Полные model digests нужны в release manifest (M4). |
| Brownfield ratification | N/A | Greenfield; конфликтующего product code не найдено во входном контексте. |
| Покрытие PRD capabilities | Partial | FR-5 evidence-capability gate, FR-8 snapshot, NFR-6/10, SM-6 и media seek не закрыты. |
| Inherited parent spine | N/A | Parent spine не указан. |
| Все altitude dimensions decided/deferred/open | Partial | Модули, данные и deployment topology заданы; failure recovery, operational lifecycle и security transport требуют решения. |

## Что уже хорошо

- Hexagonal dependency direction и capability ownership дают ясный structural seed.
- Независимые ASR/LLM ports и запрет fallback правильно защищают privacy promise.
- Stage-scoped provider payload и отсутствие provider-worker доступа к DB/data volume — сильная граница.
- Provenance/revision/stale/unverified модель хорошо связывает transcript edits с evidence.
- Точные NFR budgets в AD-15 и cross-platform/license gates в AD-14 полезны как release contracts.

## Recheck

**FAIL — critical 0 · high 1.** H1, H2, H4, H5 и H6 закрыты; исправления не ввели нового blocker. H3 закрыта частично: generated RPC фиксирует TLS/workload auth для внутреннего канала и runtime-only secret flow, но внешний provider transport и граница действия consent всё ещё допускают несовместимые небезопасные реализации.

- **Оставшийся high:** AD-5/6 должны требовать TLS для любого non-loopback provider endpoint и canonicalize его origin. `consentProof` обязан быть привязан к `stage + profileRevision + endpointOrigin + provider/model identity + data categories + snapshotDigest` и становиться недействительным при изменении любого поля; иначе допустимы plaintext provider call или повторное использование согласия для изменённой передачи.

### Final recheck

**PASS — critical 0 · high 0.** AD-5 теперь требует HTTPS с certificate/hostname validation для non-loopback provider origin и привязывает `consentProof` к accepted time/policy, stage, profile revision, endpoint origin, provider/model, data categories и snapshot digest с invalidation при изменении; последняя high-находка закрыта.
