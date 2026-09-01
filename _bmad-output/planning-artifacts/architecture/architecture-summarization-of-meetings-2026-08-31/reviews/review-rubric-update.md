# Reviewer Gate — Good-spine rubric, update

Дата: 2026-09-01

Артефакт: `ARCHITECTURE-SPINE.md`

Источники: финальные `prd.md`, `addendum.md`, `EXPERIENCE.md`, `DESIGN.md`

## Вердикт

**CHANGES REQUIRED.** Обновлённый spine правильно закрепляет Ant Design, прямой audio import/retention и отдельный `taskNumber` index + exact/prefix API, но ещё допускает четыре несовместимые реализации на load-bearing seams: воспроизведение принятого media, полный/конкурентный delete, durable at-most-once provider dispatch и повторная суммаризация с новым snapshot.

Сводка: **critical 0 · high 4 · medium 3 · low 2**. Детерминированный `lint_spine.py` — **PASS, 0 findings**.

## Critical

Критических находок нет: текущие правила не требуют невозможной атомарности между SQLite и filesystem, fencing lease присутствует, а provider ambiguity уже имеет безопасный терминальный исход `outcomeUnknown`.

## High

### H1 — HTTP Range не гарантирует воспроизведение каждого принятого audio/video

- **Где:** AD-2, AD-11, AD-13, AD-14; FR-1, FR-10, SM-3 и release corpus; финальные `media-player`/evidence flows.
- **Divergence:** AD-13 принимает файл по FFmpeg-decodability, а AD-11 отдаёт original `source` с MIME и byte ranges. FFmpeg-декодируемый MP4/MOV/MKV/WebM или прямой audio не обязан декодироваться одинаково в Chromium и Firefox. Одна реализация сочтёт успешный HTTP seek достаточным, другая создаст browser-compatible proxy; первая формально следует Rule, но провалит обязательный player journey. `preparedAudio` решает вход ASR и не решает сохранённое видео.
- **Действие:** **autofix.** Зафиксировать одно: либо import allowlist принимает только комбинации container/codec, доказанно воспроизводимые в обоих поддерживаемых браузерах, либо `prepare` публикует отдельный `playbackMedia` через AD-2 saga, сохраняя original `source`. Meeting DTO/player endpoint должен ссылаться на ready playable artifact; source/media-only deletion удаляет и proxy. Corpus gate обязан проверять seek/playback всех разрешённых комбинаций в Chromium и Firefox.

### H2 — Destructive lifecycle не покрывает полный delete и допускает гонку source-delete с новым job

- **Где:** AD-2, AD-3; FR-4, NFR-4; final UX Flow 7.
- **Divergence:** AD-2 описывает только удаление Исходной записи и разрешает его после *исторически* успешного job, но не запрещает удаление, когда новая `prepare`/`transcribe` attempt уже использует source/derived media. Полный delete Встречи вообще не имеет command-level правила: independently-built `meetings`, `processing`, `search_export` и filesystem adapters могут по-разному удалять Meeting rows, relations, FTS, jobs/attempts и artifacts, сообщая разные результаты после crash/ENOSPC.
- **Действие:** **autofix.** Добавить единый meeting-scoped destructive protocol: source-only delete требует опубликованных Transcript/Summary **и отсутствия активной lease/job, использующей media**; full delete ставит durable tombstone, блокирует mutations/new leases, отменяет/drain-ит active job, журналирует полный cascade (structured state, FTS, meeting relations, job artifacts, source/derived media) и только после reconciliation скрывает/удаляет Meeting. Partial failure остаётся видимым recoverable `deleting`, а не success.

### H3 — `stateless provider-worker` не может сам обеспечить заявленный durable `dispatchId` at-most-once

- **Где:** AD-5 и convention `Errors and retry`; FR-7, NFR-4/5.
- **Divergence:** Rule требует, чтобы replay вернул cached result/`outcomeUnknown` и никогда повторно не вызвал provider, но provider-worker объявлен stateless, не монтирует SQLite и не имеет назначенного владельца durable dispatch ledger/cache. После restart одна compliant реализация забудет `dispatchId` и повторит вызов, другая пессимистично заблокирует все replay; обе могут считать себя соответствующими словам `at-most-once`.
- **Действие:** **autofix.** Назначить `app`/SQLite владельцем persisted `ProviderDispatch` ledger и result cache. До отправки envelope CAS переводит dispatch в `inFlight`; единственный claim допускает provider call. `completed` возвращает cached normalized result, любой crash/ambiguous `inFlight` после потери владельца становится `outcomeUnknown` и никогда автоматически не redispatch-ится. Stateless worker только исполняет уже claimed dispatch; retries остаются внутри одного claim и obey глобальный лимит.

### H4 — Retry и regenerate не различены, поэтому immutable snapshot конфликтует с FR-18

- **Где:** AD-3, AD-4, AD-7; FR-8, FR-14, FR-18; final UX Flow 6.
- **Divergence:** worker обязан читать immutable job snapshot, тогда как повторная суммаризация должна использовать текущую Transcript revision и выбранные сейчас language/instructions. AD-3 говорит лишь «Retry … создаёт новую попытку», не определяя, переиспользуется ли старый snapshot, мутируется ли он, либо создаётся новый job. Также «инвалидирует downstream» может означать немедленное удаление текущего manual/stale Summary до успешной замены, хотя UX сохраняет старый результат при failed regeneration.
- **Действие:** **autofix.** Развести команды: stage `retry` повторяет тот же immutable execution snapshot; `regenerateSummary` создаёт новый job/snapshot, привязанный к current Transcript revision и явно выбранным settings. Existing Summary остаётся опубликованным и помеченным stale/manual до atomic success новой summarization; accepted replacement manual Summary требует confirmation precondition. Только успешная публикация заменяет current Summary/auto-tags.

## Medium

### M1 — Participant directory и speaker labels не имеют архитектурного запрета на связывание

- **Где:** Capability Map FR-11/FR-23, AD-2, AD-7; финальные `participant-chip` и `transcript-segment` contracts.
- **Divergence:** PRD/UX прямо определяют Участника как локальные metadata, не identity/access и не speaker label. В Rules это не закреплено. Команда удаления Participant может каскадировать в speaker labels/Segments в одной реализации и только detach Meeting relations — в другой.
- **Действие:** **autofix.** Добавить invariant: Participant принадлежит локальному directory, assignment — только Meeting↔Participant relation; ни FK, ни автоматическая identity link к `Segment.speakerLabel` не допускается. Delete атомарно снимает meeting relations после preflight count и никогда не меняет Transcript/speaker labels; duplicate display names допустимы.

### M2 — `model-fetch` не наследует проверяемый publication protocol

- **Где:** AD-2, AD-5, AD-12, AD-14 и deployment diagram.
- **Divergence:** Stack/manifest фиксируют revisions и SHA-256, но Rule не требует, чтобы one-shot `model-fetch` проверил их до публикации. Models названы частью managed filesystem, однако AD-2 saga формально описана через `MediaArtifact`; один fetcher может открыть partial file для worker, другой — atomic verified model.
- **Действие:** **autofix.** Зафиксировать model registry contract: allowlisted immutable revision/file/size/hash/license из release manifest → same-filesystem staging → checksum/metadata verification → atomic `ready` publication; failure не меняет active model. `LocalResourceCoordinator` загружает только ready model matching job snapshot checksum.

### M3 — Общая filter algebra и URL/API round-trip остаются недоопределены

- **Где:** AD-9, AD-11; FR-19; final `search-field`, `filter-bar`, Flow 2.
- **Divergence:** taskNumber exact/prefix задан хорошо, но «сочетает с остальными facets через AND» не фиксирует repeatable/multi-value encoding и обязательный OR внутри одной facet; не определён canonical query echo/URL representation для date/status/tags/participants/page. Frontend и backend могут сгенерировать несовместимые DTO, а Back не восстановит тот же архивный запрос.
- **Действие:** **autofix.** В OpenAPI query contract закрепить все facets, repeatable array encoding, AND между groups/OR внутри group, pagination/sort и canonical echo. Frontend URL state должен быть lossless projection того же DTO; contract test покрывает open-hit → Back и exact/prefix no-match без fallback.

## Low

### L1 — Final UX всё ещё помечает уже закрытый architecture follow-up как open

- **Где:** `EXPERIENCE.md §Open items`.
- **Проблема:** строка утверждает, что task-number field/index/API ещё не добавлены и «AD-9 remains unchanged», хотя AD-9/AD-11 теперь прямо их фиксируют. Это не дефект spine, но следующий builder видит противоречащие друг другу final sources.
- **Действие:** **source follow-up.** Отметить open item resolved/удалить при разрешённом обновлении UX source.

### L2 — NFR traceability агрегирована слишком широко

- **Где:** последняя строка Capability → Architecture Map.
- **Проблема:** `NFR-1–10 → AD-2–6, AD-10–16` не позволяет быстро проверить владельца locality, accessibility, install или performance gate и скрывает M2.
- **Действие:** **autofix optional.** Разбить на privacy/security, responsiveness/resources, reliability/diagnostics, accessibility и distribution/license/simplicity с точными AD ссылками.

## Rule enforceability

| Rules | Оценка | Комментарий |
| --- | --- | --- |
| AD-1 | Pass | Dependency direction проверяется import/dependency tests; публичные application seams названы. |
| AD-2–3 | Partial | Publication/fencing/atomic stage success сильны; H2 и H4 оставляют destructive/regeneration переходы неоднозначными. |
| AD-4 | Partial | Engine separation, capability gate и immutable snapshot enforceable; новый snapshot для regenerate не назначен (H4). |
| AD-5–6 | Fail/Pass | Egress, TLS, consent fingerprint и secret lifetime enforceable; durable at-most-once owner отсутствует (H3). |
| AD-7–8 | Pass | Revision/evidence validation и Summary/auto-tag atomic publication реально предотвращают заявленную divergence. |
| AD-9 | Pass | Нормализация, B-tree, equality/prefix semantics и forbidden fallbacks достаточно точны; API-wide filter algebra — M3, не дефект индекса. |
| AD-10 | Pass | Quiescent migration/backup generation и recoverable activation имеют владельца и проверяемый порядок. |
| AD-11 | Partial | OpenAPI/SSE/error/range contracts enforceable; playable codec/proxy boundary (H1) и full filter DTO (M3) отсутствуют. |
| AD-12 | Pass | Exclusive model residency и stage-scoped `llama-server` lifecycle enforceable; fetch publication — отдельный upstream gap M2. |
| AD-13 | Partial | Direct audio/video intake и no-partial-Meeting behavior enforceable; acceptance↔browser-playability postcondition отсутствует (H1). |
| AD-14–15 | Pass | Platform/accessibility/license/performance gates измеримы и привязаны к release. |
| AD-16 | Pass | Ant Design 6, one `ConfigProvider`/`App`, token-only customization, no custom CSS и native media exception точно наследуют final `DESIGN.md`. |

## Source coverage

| Область | Оценка | Комментарий |
| --- | --- | --- |
| FR-1–3 | Pass | Direct one-file audio/video streaming import, durable source retention, local paginated library/search owners определены. |
| FR-4 | Partial | Source-only success precondition есть; full delete и race с active job — H2. |
| FR-5–9 | Pass | Independent local/provider engines, consent/egress/secrets, result settings snapshot и prepared audio покрыты. |
| FR-10 | Partial | Segments/evidence/media endpoint есть; every-accepted-file playback не гарантирован — H1. |
| FR-11–12 | Partial | Speaker-capable segments/revisions/edit validation есть; Participant independence — M1. |
| FR-13–17 | Pass | Durable stages, CAS fencing, recovery/cancel, typed Summary и evidence validity закрыты. |
| FR-18 | Partial | Current-only/provenance/confirmation существуют; retry vs new-settings regeneration — H4. |
| FR-19 | Partial | FTS + exact/prefix taskNumber path закрыты; общий multi-facet URL/API contract — M3. |
| FR-20–22 | Pass | Local secret-free exports/copy, provenance markers и atomic auto-tags имеют владельцев. |
| FR-23 | Partial | CRUD capability mapped, но identity/delete boundary — M1. |
| FR-24 | Pass | Display + normalized taskNumber, exact/prefix index/API, local-only/no tracker integration согласованы. |
| Final UX | Partial | Ant Design policy, themes/accessibility, direct audio states, task-number UX and SSE resync land; player compatibility — H1, archive round-trip — M3. |

## Deferred safety

**Pass.** OQ-1 откладывает только конкретные direct-audio formats/limits с release condition, не сам audio intake/storage; diarization adapter, acceleration, chunking/dedup algorithm и prompt wording имеют достаточные domain postconditions. Remote exposure/auth/multi-user/semantic search действительно вне MVP. Fast-path assumptions имеют concrete revisit gates. Ни одна из high-находок не может быть безопасно перенесена в существующий Deferred без ослабления FR/NFR.

## Technology, codebase fit and altitude breadth

- **Named tech:** Pass на уровне rubric walker. Пины точные; модели имеют immutable revisions/checksums; Ant Design 6 совместим с React 19; SQLite runtime/options и network-filesystem guard названы. Детальная currentness/fit подтверждена соседним independent `review-version-fit.md`; M2 относится к runtime publication, а не к версии.
- **Brownfield/greenfield:** проект greenfield — product implementation code отсутствует; spine не противоречит существующим conventions. Vite/React/Ant Design и FastAPI/SQLAlchemy/Alembic образуют coherent cold-start seed; дальнейшая schema/tree остаётся code-owned корректно.
- **Parent spine:** не указан, inherited invariants отсутствуют.
- **Initiative-altitude dimensions:** paradigm/dependencies, module ownership, mutation/data consistency, API/events, privacy/security, compute/model lifecycle, frontend system, deployment/topology, migration/backup/restore, diagnostics, performance/accessibility/license release gates — все представлены. Целый operational/environmental dimension не пропущен; остаются точечные provider-dispatch и model-fetch lifecycle gaps H3/M2.

## Что уже хорошо

- Запрошенные обновления закреплены именно как invariants: `antd` 6 в Stack + AD-16, direct `audio|video` source contract в AD-2/13, `taskNumberNorm` B-tree и explicit exact/prefix API в AD-9/11.
- DB/filesystem saga, lease fencing, atomic stage publication, current-revision evidence и backup generation дают сильный consistency spine.
- Final UX accessibility floor перенесён в release gate без копирования визуального документа в архитектуру.

## Gate close conditions

1. Закрыть H1 playable-media postcondition.
2. Закрыть H2 полный/конкурентный destructive lifecycle.
3. Назначить durable owner для H3 `dispatchId` ledger.
4. Развести H4 retry и regeneration snapshot/publication semantics.

После этих четырёх исправлений high/critical blocker не останется; M1–M3 целесообразно исправить в тот же distill, поскольку это короткие cross-module/API rules.

---

## Final recheck — 2026-09-01, после gate fixes

### Итоговый вердикт

**PASS WITH MEDIUM FOLLOW-UPS — critical 0 · high 0 · medium 4 · low 2.** Все четыре прежние high-находки закрыты буквальными, enforceable Rules; новый deterministic lint также проходит с **0 findings**. Регрессий уровня critical/high не обнаружено.

### Проверка прежних High

| Finding | Recheck | Почему закрыто |
| --- | --- | --- |
| H1 — playable media | **Closed** | AD-2 вводит отдельный `playbackArtifactId`; AD-13 разрешает source только по browser codec allowlist, иначе публикует `playback-v1` WebM/Opus или WebM/VP9+Opus; player читает только этот slot. AD-11 фиксирует endpoint/Range/ETag contract, AD-14 проверяет каждый supported corpus source в Chromium и Firefox на трёх ОС. |
| H2 — destructive lifecycle | **Closed at high severity** | AD-2 теперь различает media-only/full delete, требует successful job + no active job для media-only, CAS-повышает `lifecycleEpoch`, фиксирует `DeleteIntent`, запрещает mutations/leases/grants, revoke/cancel-ит attempts, ждёт bounded leases и очищает files → authoritative rows/indexes с startup reconciliation. Late completion дополнительно fenced в AD-3. |
| H3 — durable provider at-most-once | **Closed** | AD-5 назначает `app`/SQLite единственным владельцем `ProviderDispatch` ledger, отделяет no-egress ACK от persisted `inFlight` и one-shot commit, запрещает повторную отправку того же `dispatchId`, возвращает cached result/`outcomeUnknown`; explicit retry получает новый attempt/dispatch ID. Stateless worker больше не обязан помнить replay после restart. |
| H4 — retry vs regenerate | **Closed** | AD-3 теперь явно оставляет retry на неизменяемом snapshot failed/cancelled stage, а изменённые profile/language/instructions и explicit regeneration создают новый job/snapshot с controlled reuse upstream outputs. Completion CAS проверяет expected Transcript/Summary/Tag revisions и публикует replacement только при success; AD-7 сохраняет confirmation/revision precondition для manual replacement. |

### Regression scan

Новые правила не ослабили crash consistency, privacy boundary, exact/prefix semantics, provenance или Ant Design policy. В частности, BLOB upper bound `p + 0xFF` в AD-9 корректен для canonical UTF-8 keys, потому что valid UTF-8 не содержит byte `FF`, а ordering/pagination явно закреплены.

Остаётся одна новая **medium**-неоднозначность, не открывающая data-loss path, но влияющая на FR-4 UX recovery:

#### RM1 — Failed `DeleteIntent` скрыт из ordinary reads без назначенного recovery view

- **Где:** AD-2, AD-11; FR-4 и final UX Flow 7.
- **Наблюдение:** `deleting` справедливо скрыт из обычной библиотеки, но Rule не говорит, где после timeout/permanent filesystem error пользователь увидит оставшиеся материалы и безопасное recovery action, как требует PRD. Startup reconciliation может завершить transient failure, но не гарантирует исход permission/I/O failure.
- **Действие:** **medium autofix или API-owned detail.** Delete command/status endpoint должен возвращать persisted intent, remaining artifacts и retryable/error state; failed intent остаётся доступен через recovery/diagnostics surface до completion. Timeout ожидания lease не переходит к file delete: intent остаётся pending/retryable.

### Remaining medium/low tail

- **Medium 4:** прежние M1 (Participant ≠ speaker identity), M2 (verified atomic `model-fetch` publication), M3 (полный multi-facet API/URL round-trip) и RM1 (failed-delete recovery visibility).
- **Low 2:** прежние L1 (stale resolved architecture note в final UX) и L2 (агрегированная NFR traceability).

### Final checklist verdict

| Rubric item | Recheck |
| --- | --- |
| Реальные initiative-level divergence points | **Pass at blocker tier**; medium tail перечислен явно. |
| Enforceability Rules / stated Prevents | **Pass at critical/high tier**; AD-2 delete observability имеет только medium follow-up RM1. |
| Deferred safety | **Pass**; ни один обязательный инвариант не спрятан в Deferred. |
| Named technology current/fit | **Pass**; новые codec/Range/Ant Design details согласованы с pinned stack и release gates. |
| Greenfield fit | **Pass**; product code по-прежнему отсутствует, новые rules усиливают cold-start convergence и не противоречат brownfield reality. |
| FR-1..FR-24 + final UX coverage | **Pass at blocker tier**; H1/H2/H4 закрыли прежние FR-4/10/18 gaps, taskNumber/API и Ant Design остаются согласованы. |
| Initiative altitude incl. operations | **Pass**; lifecycle epochs, dispatch ledger, model/resource topology, migration/backup/restore, release/observability envelopes присутствуют. |

**Gate conclusion:** spine можно передавать дальше без unresolved critical/high. Medium follow-ups стоит закрыть до соответствующих implementation seams; они не требуют пересмотра парадигмы или stack.
