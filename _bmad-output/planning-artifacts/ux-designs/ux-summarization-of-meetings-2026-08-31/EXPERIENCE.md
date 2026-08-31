---
name: Контекст
status: final
project: summarization-of-meetings
created: 2026-08-31
updated: 2026-09-01
sources:
  - ../../prds/prd-summarization-of-meetings-2026-08-31/prd.md
  - ../../prds/prd-summarization-of-meetings-2026-08-31/addendum.md
  - ../../prds/prd-summarization-of-meetings-2026-08-31/research-landscape.md
  - ../../architecture/architecture-summarization-of-meetings-2026-08-31/ARCHITECTURE-SPINE.md
---

# Контекст — Experience Spine

> Карта контракта: Foundation фиксирует границы; Information Architecture — поверхности; Component Patterns — поведение; State Patterns — состояния; Accessibility Floor — измеримый минимум; Key Flows и Requirement-to-flow mapping — пути и трассировку.

## Foundation

Локальное однопользовательское responsive web-приложение без авторизации, доступное через loopback в актуальных Chromium и Firefox. Первичная поверхность — desktop/laptop; узкие экраны поддерживают чтение и простые действия, но native mobile и offline-PWA не входят в MVP. Постоянные данные остаются на устройстве, а local/provider выбираются независимо для транскрибации и суммаризации.

`DESIGN.md` — единственный источник визуальной системы и обязательной политики реализации на Ant Design. `EXPERIENCE.md` наследует их и определяет только IA, поведение, состояния и пользовательские пути. Kebab-case IDs обозначают продуктовые композиции над готовыми компонентами Ant Design, а не независимую библиотеку компонентов.

Наследуются штатные Ant Design semantics, keyboard behavior, focus management, responsive primitives и component states. Политика разрешённых средств и исключений определена в `DESIGN.md §Implementation basis`; этот документ добавляет только продуктовые behavioral deltas.

Первая UI locale — русский; язык Саммари выбирается в Профиле обработки. Тон — короткий, нейтрально-деловой. Приложение — внутренний рабочий инструмент одного владельца, без growth-механик, ролей и shared workspaces.

Продукт хранит Встречи и Исходную запись бессрочно до явного удаления. Для каждой Встречи хранится текущее Саммари и сведения о последнем запуске, а не история версий. Прямой audio import добавлен решением Discovery; до обновления источника video baseline следует FR-1.

Номер внешней задачи — структурированное metadata-поле Встречи. Его exact/prefix lookup и filter выполняются локально отдельным запросом к структурированному индексу, вне FTS5. FTS5 остаётся только для title, текущих Сегментов и текущего Саммари по AD-9.

## Information Architecture

| Surface | Reached from | Purpose | Lands in flows |
|---|---|---|---|
| Библиотека | App open; nav «Встречи» | Все Встречи, status, metadata, filters, new import | 1, 2, 7, 8 |
| Поиск | Библиотека: `search-field` | Локальные lexical FTS5 hits по title/Расшифровке/Саммари и отдельный structured exact/prefix lookup/filter по task number; каждый hit показывает тип/context | 2, 3 |
| Импорт | Библиотека: «Новая встреча» | Один video/audio file, preflight, title/date/profile/language | 1 |
| Ход обработки | Успешный импорт; активная/ошибочная `meeting-row` | `prepare → transcribe → summarize`, progress, cancel, resume/retry | 1, 8 |
| Страница Встречи | `meeting-row`, search hit, processing completion | Player, metadata, Саммари, договорённости/evidence, Расшифровка, edit/copy/export/delete | 1, 2, 3, 5, 6, 7 |
| Участники | Main nav; metadata edit | Local mini-directory and meeting assignment; no speaker/access link | 5 |
| Профили обработки | Main nav; Import shortcut | Independent transcription/summarization configs, readiness, result settings | 1, 4 |
| Настройки и диагностика | Main nav; error details | Storage/models/resources, local app state, safe diagnostics | 4, 7, 8 |

Overlays do not become routes: `consent-dialog`, `confirm-dialog` and `export-menu`. Overlay depth is one; an open overlay must close before another opens.

Одобренный IA reference: [карта поверхностей и переходов](wireframes/information-architecture.excalidraw). Surface closure is complete: every surface is reached by at least one numbered journey, and every captured user need lands on a surface.

Одобренные композиционные референсы:

- [Библиотека и Поиск](mockups/library.html) — populated/paginated state, локальный поиск, фильтры, meeting rows и архивные metadata.
- [Страница Встречи](mockups/meeting-detail.html) — канонический reading order, плеер, сводка, договорённости, evidence focus, transcript и stale state.
- [Ход обработки](mockups/processing.html) — трёхэтапный progress, semantic status и восстановимая ошибка суммаризации.

Эти HTML-файлы — только визуальные референсы. Не копируйте их встроенные стили в рабочий интерфейс. При конфликте следуйте `DESIGN.md` и `EXPERIENCE.md`; реализуйте экраны средствами Ant Design, разрешёнными в `DESIGN.md §Implementation basis`.

### Страница Встречи: reading order

1. Page heading/title.
2. `summary-card`.
3. Complete list of `agreement-item`; important agreements are explicitly marked.
4. `media-player`, which stays available while `evidence-link` reveals and focuses the cited `transcript-segment`.
5. Metadata: date, duration, processing status, last modified, `tag-chip`, `participant-chip`, `task-link-card`, disk size and media retention.
6. Current Расшифровка and editing/regeneration controls.

Это также канонический порядок DOM, клавиатурной навигации и чтения с экрана: heading → summary → agreements → player → metadata → transcript. Desktop размещает те же узлы в двух зонах через Ant Design `Grid`/`Flex`, не меняя смысловой DOM-order. На узких ширинах зоны складываются в этом порядке. Header actions не исчезают при reflow: второстепенные действия, включая «Экспорт», переходят в доступный labelled `export-menu`. Пустые разделы Саммари остаются видимыми как «Не обнаружено», чтобы отсутствие отличалось от loading/error.

## Voice and Tone

Brand voice lives in `DESIGN.md.Brand & Style`; this section governs microcopy.

| Situation | Use | Avoid |
|---|---|---|
| Import ready | «Файл проверен. Можно начать анализ.» | «Магия начинается!» |
| Long stage | «Транскрибация выполняется · 24 мин» | «Почти готово» without evidence |
| No percent | «Суммаризация выполняется» | Fake 87% |
| Local boundary | «Этот этап выполняется локально. Содержание не покидает устройство.» | Blanket «100% private» |
| Provider consent | «Провайдеру Acme будет отправлена текущая Расшифровка для суммаризации.» | «Продолжая, вы соглашаетесь…» without payload |
| Retryable error | «Суммаризация не завершена. Расшифровка сохранена.» | «Что-то пошло не так» |
| Ambiguous provider result | «Не удалось подтвердить результат внешнего запроса. Новый запуск может повторить операцию.» | Silent retry |
| Stale summary | «Расшифровка изменена. Сводка требует обновления.» | Hiding old result |
| Regenerate summary | «Обновить краткую сводку» / «Создать краткую сводку заново» | Неоднозначное «Создать заново» |
| Unverified item | «Подтверждение не найдено» | «Вероятно верно» |
| Empty section | «Решения не обнаружены.» | Blank space |
| Delete | «Полностью удалить Встречу и 3 связанных материала?» | «Удалить объект?» |

No exclamation marks, praise, anthropomorphism or AI-confidence theater. Status text names what is saved and what action is safe.

## Component Patterns

Visual specs live in `DESIGN.md.Components`; token references below resolve there. Ant Design владеет базовой anatomy и interaction model; таблица ниже задаёт только product-specific composition и behavioral deltas. Canonical mapping к Ant Design зафиксирован в `DESIGN.md.Components`.

| Component ID | Use | Behavioral rules |
|---|---|---|
| `app-shell` | Global | First focusable control is «К основному содержимому» skip link. Persistent desktop nav is a named landmark; every rail link keeps an accessible name when visible text is hidden, and the active route has `aria-current="page"`. No accounts/avatar; local app/service status routes to diagnostics. |
| `mobile-nav-trigger` | Narrow/zoomed navigation | Real `<button>` named «Открыть навигацию»/«Закрыть навигацию» with `aria-expanded` and `aria-controls`. It opens the named nav overlay, makes background inert, moves focus into nav, closes on Escape/outside action, and returns focus to the trigger. |
| `primary-button` | Import, save, consent | One primary action per region; a disabled control explains why it is unavailable; submitting changes label and exposes busy state without duplicate command. |
| `secondary-button` | Edit, cancel, retry | Safe or reversible actions; retry label names the stage. |
| `destructive-button` | Inside delete confirmation | Fires only after consequences are listed; never default-focused. |
| `text-field` | Names, URL, task number, instructions | Persistent `<label>`; hint/error IDs join through `aria-describedby`; invalid controls set `aria-invalid="true"`. Failed submit focuses a linked error summary or first invalid field. Metadata, transcript and summary edits use explicit Save/Cancel. |
| `select-field` | Profile, language, stage mode/model | Inherits the mapped field/select behavior; persistent label and the same error contract as `text-field`. Changing provider/model invalidates prior consent and is stated before save. |
| `status-badge` | Library, processing, meeting, profile | Text + semantic icon; user-facing vocabulary maps to durable backend state, not raw codes. |
| `meeting-row` | Библиотека | `<article>`/`<li>` with heading-link «Открыть встречу: [название]», separate metadata/status description and sibling retry/error buttons. The row is not an interactive container; optional pointer delegation activates only the title link and never captures child controls. Paginated, never infinite scroll. |
| `search-field` | Библиотека/Поиск | Debounce local lexical FTS5 query over title/current transcript/current summary. A recognized task number uses separate local structured exact/prefix lookup outside FTS5; Enter opens search surface. No external request or semantic claim. |
| `filter-bar` | Библиотека | Date range, status, tags, participants and structured exact/prefix task-number filter; facets combine with AND, values within one facet with OR. A collapsed filter popover uses a button with `aria-expanded`/`aria-controls`, labelled region/dialog semantics, documented Tab/Escape/outside-close and focus return. Multi-select follows the inherited Ant Design combobox/listbox model plus announced selected count and specific chip-removal names; Escape closes suggestions without erasing typed text. |
| `import-dropzone` | Импорт | Drag/drop and labelled file picker; one file only. Availability/read permission, container, audio track, decodability and limits are checked before Meeting creation. Every rejection preserves form, creates no hidden Meeting/job and offers re-pick. |
| `stage-progress` | Ход обработки | Three fixed stages; exact percent only when supplied; updates at least every 5 s; completed stages remain visible after failure/restart. Percent stays on `progressbar`; one stable status live node announces only semantic transitions, cancel/resync and terminal results. |
| `notice-banner` | Cross-surface attention | Stale, unverified, high load, waiting secret, retryable/ambiguous errors; one safest next action, details link optional. |
| `media-player` | Страница Встречи | Prefer native `<video controls>`/`<audio controls>`. A custom player must expose named play/pause, seek slider (`aria-valuemin/max/now/valuetext`), mute/volume, fullscreen where applicable, elapsed/total and playback-error controls/status. Current VTT becomes `<track kind="captions">` when available; «Открыть расшифровку» always exists and the player states «Субтитры недоступны» when no track exists. Audio/video share the same logical controls; if media is deleted, text remains and the player becomes an explicit missing-media state. |
| `summary-card` | Страница Встречи | Current overview/themes/decisions/tasks/highlights/open questions; edit/copy; stale/manual/unverified markers; no version selector. |
| `agreement-item` | Страница Встречи | Complete ordered list; important label, responsible/due only if stated; copy independently; evidence state always present. |
| `evidence-link` | Summary/agreement/search | `href` targets the cited segment's stable DOM ID. Activation seeks, moves focus to the `tabindex="-1"` segment and issues one polite announcement: item, timestamp, speaker if present and verified state; playback starts only for a control explicitly named «Воспроизвести». Unresolved evidence is status text, never a false link. |
| `transcript-segment` | Страница Встречи | Stable DOM ID; evidence target accepts programmatic focus and shows visible «Фрагмент подтверждения» plus programmatic current state, not color alone. Timestamp seeks player; edit/split/merge preserves time bounds; speaker rename affects matching speaker labels only. |
| `tag-chip` | Library filters, meeting metadata | Owner can create/remove; auto-tags appear after successful Саммари and are editable; origin shown only in edit mode. In a multi-select, removal is a sibling 44×44 named button and selection/count changes are announced. |
| `participant-chip` | Directory, meeting metadata, filter | Multi-select metadata only; follows `filter-bar` combobox/listbox, announced-count and named 44×44 removal-button contract; never binds to speaker labels, transcript segments, identity or access. |
| `task-link-card` | Meeting metadata/search | Opens external URL in a new tab with external-destination notice. Extracts task number from URL, permits manual correction and uses structured exact/prefix lookup/filter outside FTS5; implementation is gated by the architecture follow-up in Foundation. |
| `profile-stage-card` | Профили/Импорт | Separate cards for transcription and summarization; mode/engine/model/readiness/data category; no automatic fallback. |
| `consent-dialog` | Before changed provider stage | `role="dialog"`, `aria-modal="true"`, title/description IDs, inert background, initial focus on title/safe action and focus return. Names stage, provider, endpoint, model and exact categories; consent is invalidated by relevant changes; Cancel/Escape performs no dispatch. |
| `confirm-dialog` | Delete media/meeting; replace manual summary; participant delete | Same complete dialog semantics; destructive action is never initial focus. Lists consequences and preserved data. Deleting a referenced participant detaches it from affected Meetings, never changes speaker labels and shows affected count. |
| `export-menu` | Meeting header/overflow | Trigger button has accessible name, `aria-expanded` and `aria-controls`; popup is a labelled menu with documented Arrow/Tab/Escape/outside-close and focus return. Markdown summary, TXT/VTT transcript and JSON meeting are generated locally; each item states contents; secrets/diagnostics are excluded. |
| `empty-state` | Library, search, participants | Explains why empty and provides one route; filtered empty offers clear filters, not import. |
| `diagnostic-panel` | Settings/error detail | Safe code, stage, retryable, model/profile identity and technical metadata; copy diagnostics excludes secret/full transcript/summary/provider payload. |

## State Patterns

User-facing processing vocabulary: «Проверка файла», «Подготовка аудио», «Транскрибация», «Суммаризация», «Ожидается ключ», «Требует действия», «Отменяется», «Отменено», «Завершено». Raw backend states remain in diagnostics only.

| Surface | Required states and treatment |
|---|---|
| Global / `app-shell` | Cold load: shape-matched placeholders; ready; local API unavailable: blocking explanation + restart/docs route; maintenance: read-only banner and mutations disabled; provider/network offline affects provider actions only, never hides local library. |
| Библиотека | Cold load; empty archive → `empty-state` + New meeting; populated/paginated; filtered empty → clear filters; active processing rows update in place; list error preserves last safe view + retry. |
| Поиск | Idle guidance; querying; bounded/paginated hits; no matches; FTS or structured task-number index repair/unavailable → name the affected local path; title/transcript/summary hit includes snippet, task-number exact/prefix hit is explicitly typed as structured metadata. |
| Импорт | Empty; drag focus; streaming/validating; unavailable/unreadable file, read-permission denied or file disappeared after pick; unsupported container; missing audio track; decoding failure; size/duration limit; valid/ready. Every preflight failure preserves title/date/profile/language, creates no Meeting/job and offers «Выбрать файл снова»; interrupted import cleans staging and returns to the same form. |
| Ход обработки | Each active stage; determinate/indeterminate; high load; reconnect/resync without duplicate job; waitingForSecret; retryable error; auth/validation/missing-model non-auto-retry; `outcomeUnknown`; cancelling up to 10 s; cancelled; complete. Saved upstream outputs remain visible. One stable `role="status" aria-live="polite" aria-atomic="true"` announces stage transitions, «Отмена запрошена», terminal cancel/result, `outcomeUnknown` in user-facing language and «Состояние восстановлено: …» once; actionable failure uses `role="alert"`, heartbeat is never live and focus does not jump. |
| Страница Встречи | Loading; processing with only published artifacts; complete; playback ready/error; media removed; transcript edit dirty/saving/error; summary stale/manual/unverified; empty section «Не обнаружено»; evidence focus; export busy/error/success; delete confirmation. |
| Участники | Empty; populated; search/no match; create/edit validation; duplicate-name allowed with distinguishing note; delete referenced/unreferenced; storage error retains form. |
| Профили обработки | Empty/no usable profile; local model missing/downloading/ready/incompatible resources; provider testing/valid/limited compatibility/auth/network/model error; session secret absent; unsaved changes; consent required/invalidated. |
| Настройки и диагностика | Loading storage/resource totals; ready; model fetch progress/error; high load; maintenance/migration failure with read-only explanation; diagnostics empty/populated/copy-success. |
| `consent-dialog` | Review; secret missing; submitting; dispatch accepted; changed snapshot invalidates and returns to review; error preserves choices. |
| `confirm-dialog` | Review consequences; submitting; success; failure retains overlay and reports what remains. |
| `export-menu` | Ready; generating; local file complete; write/permission failure with retry. |

## Interaction Primitives

- Click/tap activates; Tab/Shift+Tab follows canonical DOM/reading order; Enter activates focused controls; Space controls playback only when focus is inside the player. Escape closes the top menu/filter/nav/dialog when safe or cancels the current edit, never the processing job.
- Evidence navigation follows the normative `evidence-link`, `transcript-segment` and `media-player` contracts in Component Patterns; the seek/focus/announcement transition is atomic from the user's perspective.
- On wide screens `media-player` remains sticky within its column during evidence review; it stops before page-level destructive/actions footer and never covers focused content.
- Navigation and overlays follow the exact ownership/focus contracts in Component Patterns for `app-shell`, `mobile-nav-trigger`, `filter-bar`, `consent-dialog`, `confirm-dialog` and `export-menu`. Modal stacks remain forbidden.
- Search and filters update the URL query so Back restores the archive view. Opening a search hit preserves query context.
- Long operations persist outside the page. Refresh/reconnect resyncs current durable state and never creates a second job.
- Edits follow the `text-field`/`select-field` Save, error and focus contracts; unsaved navigation gets `confirm-dialog`. A successful save is announced through the stable status node without a color-only toast.
- No hover-only controls, drag-to-reorder, infinite scroll, modal stacks, autoplay, push/email/system notifications, semantic archive chat or hidden engine fallback.

## Trust, Privacy & Provenance

- Before each provider dispatch, if the consent fingerprint has changed, `consent-dialog` states stage, endpoint/provider/model and exact data: prepared audio + language/config for transcription, or current transcript chunks + instructions/config for summarization.
- Provider secrets are session/attempt-only. After restart, «Ожидается ключ» routes to re-entry; no «remember key» promise.
- Local processing says «no content egress after models are prepared», not universal offline: model download and provider stages are separate.
- Editing Расшифровки makes current Саммари stale. Evidence that is broken or does not point to the current revision is unverified. Regeneration uses the current Расшифровка and does not rerun usable transcription.
- Auto retry never covers auth, validation or missing model. Ambiguous provider outcome requires an explicit new attempt. No local→provider fallback occurs automatically.
- Complete deletion lists media, transcript, summary, index and job-linked artifacts; media-only deletion preserves text and marks player unavailable.

## Accessibility Floor

WCAG 2.2 AA is the product floor for the responsive web surface; visual contrast is governed by `DESIGN.md`.

- Keyboard and focus: all actions are operable; visible focus uses `{colors.focus}` / `{colors.focus-dark}` and never disappears behind sticky content. Navigation semantics are owned by `app-shell` and `mobile-nav-trigger` in Component Patterns.
- Every target is at least `{spacing.target-min}` × `{spacing.target-min}` CSS px or satisfies the WCAG spacing exception. Icon-only, player, timecode/evidence, copy and destructive controls keep the product floor `{spacing.control-min-inline-size}` × `{spacing.control-min-height}` (44×44), including narrow layouts; destructive controls are spaced away from play/copy.
- Page headings receive focus on route navigation. Overlay and form semantics inherit the exact Component Patterns contracts for `mobile-nav-trigger`, `filter-bar`, `consent-dialog`, `confirm-dialog`, `export-menu`, `text-field` and `select-field`; destructive actions are never initially focused.
- Dynamic updates inherit `stage-progress`: semantic transitions, cancel, resync and terminal results are announced once through its persistent polite/atomic node; actionable errors use alert, percent/heartbeat churn stays silent and focus does not move.
- Media and evidence inherit `media-player`, `evidence-link` and `transcript-segment`. Test outcomes: equivalent audio/video controls, captions status and transcript route; stable focus target; one item/timestamp/speaker/verification announcement; visible non-color current marker.
- `prefers-reduced-motion: reduce` disables smooth scrolling, decorative animation, indeterminate sweeps and progress transitions; seek/focus updates remain immediate. No functional information depends on motion.
- At 200% zoom and 320 CSS px reflow, canonical DOM/focus/visual order stays heading → summary → agreements → player → metadata → transcript; no action disappears, secondary actions remain in a labelled overflow menu, and there is no horizontal page scroll. Status, provider mode and importance always include text.

## Responsive & Platform

| Width | Behavior |
|---|---|
| `≥1200px` | `{spacing.sidebar-width}` nav; meeting two-zone layout; player sticky; library rows expose full metadata. |
| `900–1199px` | `{spacing.rail-width}` nav with accessible names/`aria-current`; two zones only when each remains readable, otherwise canonical-order stack; filters may wrap. |
| `<900px` | `mobile-nav-trigger` and inert-background nav overlay; single canonical-order column; player not sticky; overlays become near-full-width. No route or action is lost at zoom-triggered breakpoints. |
| `<600px` | Reading and simple editing remain supported on this secondary surface; filter controls collapse into one labelled trigger with `aria-expanded`/`aria-controls`; no wide tables; agreement metadata stacks; timecode/copy/player/destructive targets remain 44×44. |

Chromium and Firefox parity on Linux/macOS/Windows. Native file picker wording may differ, but preflight/error taxonomy does not. Theme follows system; printing is not a primary export route.

## Inspiration & Anti-patterns

- **Scriberr:** lift video/audio upload, library and synced transcript/player; do not inherit unverified provider assumptions.
- **vts:** lift persistent stage progress, restart-safe recovery and timecode provenance; avoid knowledge-base/semantic scope.
- **TranscrIA:** lift preflight and explicit long-job states; reject heavy portal/admin complexity for one owner.
- **noScribe:** lift honest human-review posture and speaker/ASR caveats; retain web library and structured Саммари.
- **Reject:** blanket «local/private», AI result without evidence, fake progress, silent retries/fallback, automatic participant↔speaker binding, full version-history UI, gamification and decorative AI motion.

## Key Flows

### Flow 1 — UJ-1. Sergei обрабатывает запись завершившейся рабочей встречи.

1. Sergei opens Библиотека and chooses «Новая встреча».
2. In Импорт he selects one existing video or audio file, edits title/date, picks a Профиль обработки and transcription language.
3. `import-dropzone` streams and validates the file. If a provider stage is selected and consent is absent/invalid, `consent-dialog` names the stage and payload before dispatch.
4. Ход обработки shows preparation, transcription and summarization, real percent when available, elapsed time and durable completed stages.
5. Completion opens Страница Встречи with `summary-card`, complete `agreement-item` list and `media-player`.
6. **Climax:** Sergei sees, point by point, everything agreed—including stated responsible people, dates and deadlines—without replaying the whole recording.
7. He follows an `evidence-link`, verifies the source, optionally renames a speaker label, regenerates current Саммари and exports Markdown.

Failure: an external engine fails → the job and prior stages remain saved; stage/reason/safe action are shown; Sergei retries only the failed stage. `outcomeUnknown` requires explicit new attempt.

Preflight failure: the file is unavailable, unreadable, permission-denied or disappears after pick → the form is preserved, no Meeting/job exists, and Sergei selects the file again.

### Flow 2 — Sergei finds an archived decision three weeks later

1. Sergei opens Библиотека and enters a remembered task number from the external URL; alternatively he filters by date, tag or participant.
2. Поиск uses structured exact/prefix task-number lookup outside FTS5 and returns typed local hits; filters remain visible.
3. He opens the matching `meeting-row`/hit and lands at relevant meeting content.
4. He scans current summary and all agreements, then follows the external `task-link-card` if needed.
5. **Climax:** the old decision, deadline and linked external task are recovered from one page.

Failure: no exact/prefix task-number hit → preserve query, offer clear filters and state that this field uses structured local matching; never fabricate semantic matches.

### Flow 3 — Sergei verifies an important agreement before acting

1. On Страница Встречи Sergei chooses an important `agreement-item`.
2. Its `evidence-link` focuses the cited current-revision `transcript-segment` and seeks `media-player` to the cited timestamp.
3. Sergei plays the fragment and compares wording, responsible person and deadline.
4. **Climax:** source audio/video and transcript confirm the agreement in under two minutes.

Failure: evidence cannot resolve → item remains visible as «Подтверждение не найдено», does not fake a link, and preserves this marker in copy/export.

### Flow 4 — Sergei configures a private or provider-assisted profile

1. Sergei opens Профили обработки and configures transcription and summarization independently in two `profile-stage-card` blocks.
2. For local mode he checks model readiness/memory; for provider mode he enters endpoint/model and session secret, then tests compatibility.
3. He selects summary language/instructions and saves the profile.
4. Before first or changed provider dispatch, `consent-dialog` names endpoint/model/data categories.
5. **Climax:** Sergei can state exactly which stage is local, which is external and what leaves the device.

Failure: auth/API/model/timestamp incompatibility is categorized with a safe action; no fallback changes mode. Missing local model routes to model preparation.

### Flow 5 — Sergei organizes a meeting for future recall

1. Sergei edits metadata on Страница Встречи.
2. He accepts, removes or creates `tag-chip` values; assigns one or more `participant-chip` entries from Участники.
3. He pastes an external task URL. `task-link-card` extracts a number; he corrects it manually if needed.
4. He saves changes and returns to Библиотека, where structured exact/prefix task-number lookup/filter and other filters reflect the saved metadata.
5. **Climax:** the meeting is now findable by date, tag, participant or external task number.

Failure: number extraction fails → preserve URL and request manual number. Participant metadata never changes speaker labels.

### Flow 6 — Sergei corrects the record and refreshes the result

1. Sergei edits/splits/merges `transcript-segment` entries or renames a recognized speaker label.
2. Save creates a new current transcript revision; `notice-banner` marks `summary-card` stale.
3. He reviews summary language/instructions and chooses «Обновить краткую сводку».
4. If current Саммари was manually edited, `confirm-dialog` names the replacement before proceeding.
5. **Climax:** the regenerated current Саммари and evidence resolve against the corrected transcript revision.

Failure: summarization fails → corrected transcript remains current and old summary stays visibly stale; retry does not rerun transcription.

### Flow 7 — Sergei exports or removes local materials

1. From Страница Встречи Sergei opens `export-menu`, chooses Markdown, TXT/VTT or JSON, and saves locally.
2. For space recovery he opens `confirm-dialog` and chooses media-only deletion or complete Meeting deletion.
3. The dialog lists exact materials and disk volume; complete delete requires explicit confirmation.
4. **Climax:** export is portable and secret-free, or the chosen materials disappear from library/managed storage as promised.

Failure: export write/delete fails → show what remains and preserve the Meeting; never report partial cleanup as complete.

### Flow 8 — Sergei recovers a long-running job after restart

1. Sergei reopens the app; active/failed `meeting-row` shows durable status.
2. Ход обработки resyncs current stage without duplicate work; completed stages remain complete.
3. If waiting for provider secret, he re-enters it; if retryable, he retries the named stage; if cancelled, he starts an explicit new attempt.
4. He opens `diagnostic-panel` only when details are needed and copies safe metadata.
5. **Climax:** processing continues from the first unfinished stage while saved outputs remain intact.

Failure: local service/migration is unavailable → mutations are blocked, the reason and recovery route are shown, and no unsafe retry is offered.

## Requirement-to-flow mapping

| Source requirement (exact name) | Flow(s) | Experience delivery |
|---|---|---|
| **UJ-1. Sergei обрабатывает запись завершившейся рабочей встречи.** | 1 | `Импорт`; `stage-progress`; `evidence-link`; `export-menu`. |
| **FR-1: Импорт Исходного видео** | 1 | `Импорт`; `import-dropzone`; State Patterns: Импорт. |
| **FR-2: Локальное хранение Встреч** | 1, 2, 7, 8 | Foundation; `Библиотека`; `confirm-dialog`. |
| **FR-3: Библиотека Встреч** | 1, 2, 8 | `Библиотека`; `meeting-row`; `search-field`; `filter-bar`. |
| **FR-4: Управление сроком хранения** | 7 | `confirm-dialog`; Flow 7. |
| **FR-5: Профиль внешнего провайдера** | 4 | `profile-stage-card`; `consent-dialog`; Flow 4. |
| **FR-6: Локальный Профиль обработки** | 4 | Foundation; `profile-stage-card`; Flow 4. |
| **FR-7: Явная граница передачи данных** | 1, 4 | `consent-dialog`; Trust, Privacy & Provenance. |
| **FR-8: Настройки результата** | 4, 6 | `profile-stage-card`; Flows 4, 6. |
| **FR-9: Подготовка аудио** | 1 | `stage-progress`; State Patterns: Ход обработки. |
| **FR-10: Расшифровка с таймкодами** | 1, 3, 6 | `transcript-segment`; `media-player`; Flow 3. |
| **FR-11: Спикеры** | 1, 6 | `transcript-segment`; `participant-chip`; Flows 1, 6. |
| **FR-12: Редактирование Расшифровки** | 6 | `transcript-segment`; `text-field`; Flow 6. |
| **FR-13: Этапы и прогресс** | 1, 8 | `stage-progress`; State Patterns: Ход обработки. |
| **FR-14: Восстановление и повтор** | 1, 6, 8 | State Patterns: Ход обработки; Flow 8. |
| **FR-15: Отмена обработки** | 1, 8 | State Patterns: Ход обработки; Flows 1, 8. |
| **FR-16: Структурированное Саммари** | 1, 2, 6 | `summary-card`; State Patterns: Страница Встречи. |
| **FR-17: Ссылки на подтверждения** | 1, 3, 6 | `evidence-link`; `transcript-segment`; `media-player`. |
| **FR-18: Редактирование и повторная суммаризация** | 1, 6 | `summary-card`; `confirm-dialog`; Flow 6. |
| **FR-19: Поиск по содержимому** | 2, 3 | `Поиск`; `search-field`; `evidence-link`. |
| **FR-20: Экспорт результатов** | 1, 7 | `export-menu`; Flow 7. |
| **FR-21: Копирование частей результата** | 3, 7 | `summary-card`; `agreement-item`; `evidence-link`. |
| **NFR-1 — Локальность данных** | 1, 2, 4; Foundation; Trust, Privacy & Provenance | Foundation; Trust, Privacy & Provenance; Flows 2, 4. |
| **NFR-2 — Отзывчивость интерфейса** | 1, 2, 8; Foundation; State Patterns | State Patterns; Responsive & Platform; Flow 8. |
| **NFR-3 — Большие файлы** | 1; State Patterns | `import-dropzone`; `stage-progress`; State Patterns: Импорт. |
| **NFR-4 — Надёжность** | 1, 7, 8; State Patterns | State Patterns: Ход обработки; Flows 7, 8. |
| **NFR-5 — Диагностика** | 4, 8; Trust, Privacy & Provenance | `diagnostic-panel`; Trust, Privacy & Provenance. |
| **NFR-6 — Доступность** | 1–8; Accessibility Floor | Accessibility Floor; Component Patterns; Interaction Primitives. |
| **NFR-7 — Поддерживаемая среда** | Responsive & Platform | Responsive & Platform; UX-exclusion: deployment documentation. |
| **NFR-8 — Воспроизводимая установка** | UX-exclusion | UX-exclusion: architecture/release documentation. |
| **NFR-9 — Открытый исходный код** | UX-exclusion | UX-exclusion: release governance. |
| **NFR-10 — Простота основного пути** | 1; Information Architecture | `Импорт`; Flow 1. |

## Open items

- `[OPEN · nonblocking]` Supported direct audio formats and audio size/duration limits. Video baseline remains the source contract until PRD update.
- `[OPEN · architecture follow-up]` `[NOTE FOR ARCHITECTURE]` Add task-number storage field, non-FTS structured index and exact/prefix lookup/filter API before implementing the approved archive UX; AD-9 remains unchanged and does not already cover this field.
