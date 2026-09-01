# Reconciliation: обновлённый Architecture Spine ↔ финальный PRD и addendum

**Вердикт:** **PASS WITH CORRECTIONS** — spine согласован с актуальными FR-1…FR-24 и закрыл прежние load-bearing разрывы по прямому audio import/storage, локальности, `taskNumber` index и exact/prefix API. Перед передачей builder'ам стоит исправить два оставшихся межмодульных инварианта; противоречий обязательным ограничениям PRD/addendum не найдено.

**Сверены:**

- `prd.md`, `status: final`, `updated: 2026-09-01`;
- `addendum.md`;
- `ARCHITECTURE-SPINE.md`, `status: final`, `updated: 2026-09-01`.

## Findings

### R-1 — High: удаление Исходной записи не ограничено успешной обработкой

**Источник:** FR-4 разрешает удалить только Исходную запись **после успешной обработки**, сохранив Расшифровку, Саммари и метаданные; полное удаление Встречи доступно отдельно.

**Состояние spine:** AD-2 хорошо фиксирует бессрочное хранение `source` без TTL, явное удаление source вместе с derived media, сохранение текста/метаданных и восстановление после частичного удаления. Однако его Rule не содержит precondition успешной обработки, а Capability Map для FR-1–4 не связывает retention/delete с state machine AD-3.

**Риск расхождения:** independently-built meetings API может разрешить `delete source` у новой, выполняющейся или неуспешной Встречи. Это необратимо уничтожит единственный вход до появления пригодного результата, хотя реализация формально будет следовать AD-2.

**Correction:** добавить к AD-2 или AD-3 command precondition: source-only deletion разрешена лишь при успешно сохранённых пригодных текстовых результатах и отсутствии активного stage, использующего source/derived media; иначе API возвращает стабильную domain error. Полное подтверждённое удаление Встречи остаётся отдельной командой.

### R-2 — Medium: автотеги FR-22 не имеют атомарного владельца в успешной суммаризации

**Источник:** FR-22 требует создавать тематические автотеги только после успешного создания Саммари; при незавершённой или ошибочной суммаризации они не создаются. Ручные и автоматические теги составляют один редактируемый meeting-owned набор, а происхождение видно при редактировании.

**Состояние spine:** AD-3 атомарно публикует authoritative stage output, AD-8 валидирует `Summary`, AD-2 владеет structured state. Но FR-22–24 в Capability Map отнесены только к `meetings`/`search_export` и AD-2/9/11: `processing`, AD-3 и AD-8 отсутствуют, а Rule не говорит, входят ли автотеги в транзакцию успешной публикации Саммари или являются отдельным best-effort side effect.

**Риск расхождения:** processing и meetings могут независимо выбрать несовместимые моменты записи — теги появятся после failed summary, не появятся после successful summary либо останутся частично опубликованными после crash.

**Correction:** закрепить, что валидированные auto-tag candidates публикуются в одном command/stage-success boundary с текущим `Summary` (либо идемпотентной обязательной postcondition до `summarize=succeeded`), с `origin=automatic`; failed/cancelled stage не мутирует tags. В Capability Map добавить `processing`, AD-3 и AD-8 к FR-22.

## Проверка обязательных обновлений

| Область | Вердикт | Покрытие в spine |
| --- | --- | --- |
| FR-1…FR-24 и source bindings | **Согласовано** | Frontmatter ссылается на финальные PRD/addendum и оба final UX source; `binds` охватывает FR-1..24 и NFR-1..10, Capability Map покрывает все диапазоны без пропусков. Исключение SM-1 допустимо: это post-release product outcome, а не архитектурный инвариант. |
| Прямой audio import | **Согласовано** | AD-13 принимает ровно один `audio- or video-source`, stream-ит его, одинаково валидирует через `ffprobe`, не создаёт Meeting/job при rejection и создаёт отдельный `preparedAudio`; для audio UI не обязан имитировать video extraction. Форматы/лимиты корректно оставлены в OQ-1 с release gate. |
| Audio/video storage и retention | **Согласовано, кроме R-1** | AD-2 хранит оригинальные bytes, `mediaKind=audio|video`, checksum/size/state в managed local storage без TTL; удаление source сохраняет текст и переводит media в недоступное состояние по product/UX contract. Не хватает только precondition успешной обработки. |
| `taskNumber` data/index | **Согласовано** | AD-9 задаёт display value и единый write/query `taskNumberNorm` (`NFKC → trim → casefold`), отдельный non-unique partial B-tree `(task_number_norm, id)`, equality и prefix range под `BINARY`, rebuild/repair и запрет fuzzy/contains/FTS/semantic fallback. Это прямо отвечает вопросу addendum §Architecture. |
| `taskNumber` exact/prefix API | **Согласовано** | AD-11 фиксирует `GET /api/v1/meetings?taskNumber=…&taskNumberMatch=exact|prefix`, AND с другими facets, `matchedField`/`matchKind`, pagination и `200` empty page с echo query без fallback path; AD-9 запрещает пустой normalized query. |
| External task boundary | **Согласовано** | Сингулярные `taskNumber`/URL остаются локальными meeting metadata; ни index, ни API не требуют tracker API. Внешняя интеграция и синхронизация остаются вне MVP. |
| Addendum constraints | **Согласовано** | Независимые ASR/LLM configs, запрет hidden fallback, stage-scoped provider payload, runtime-only secrets, loopback Compose, managed DB/filesystem ownership, evidence links, durable pipeline, cross-platform/license/release gates и backup/restore имеют явных владельцев. Предварительное указание addendum «хранить API-ключи» корректно уточнено более сильным финальным PRD: DB хранит только `secretRef`, значение — runtime-only. |

## Итог

После R-1 и R-2 дополнительных PRD/addendum-коррекций spine не требуется. Детальные audio formats/limits остаются единственным явным product gate OQ-1; protocol quality evaluation OQ-2 остаётся QA/test-design gate и не требует нового AD.
