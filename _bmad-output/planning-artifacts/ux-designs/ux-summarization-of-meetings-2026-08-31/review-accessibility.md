# Accessibility review — «Контекст»

## Overall verdict

**Условно не проходит Reviewer Gate до устранения High-находок.** Базовый контракт заметно сильнее обычного черновика: заявлены WCAG 2.2 AA, клавиатурный доступ, видимый focus, текстовые статусы, reduced motion, reflow, dialog focus management и осмысленные live-region события. Однако сейчас есть пять High-пробелов, способных заблокировать навигацию, распознавание контролов или ключевой сценарий проверки договорённости.

Сводка: **Critical 0 · High 5 · Medium 6 · Low 2**.

## Scope

Проверены контракты `DESIGN.md` и `EXPERIENCE.md`, канонический `.memlog.md`, подтверждённые PRD/addendum/research/architecture sources и референсы:

- `.working/design-directions-1.html`
- `.working/key-library.html`
- `.working/key-meeting-detail.html`
- `.working/key-processing.html`
- `.working/ia-2026-08-31.excalidraw`

Это review UX-контракта и иллюстративных материалов, не runtime-аудит. Поэтому каждая находка помечена как **Contract gap**, **Illustrative HTML gap** или обеими метками.

## Findings

### Critical

Нет.

### High

#### A11Y-H1 — Границы полей и outline-контролов не достигают 3:1

**Тип:** Contract gap.  
**Где:** `DESIGN.md:28-29`, `DESIGN.md:134-157`, `DESIGN.md:167-184`, `DESIGN.md:288`, `DESIGN.md:325-331`.

`{colors.border-strong}` (`#B8CBC6`) имеет контраст лишь **1.69:1** с `{colors.surface-raised}` и **1.57:1** с `{colors.surface-base}`. Тёмный `{colors.border-strong-dark}` (`#4D655F`) даёт **2.60:1** на raised, **2.87:1** на base и **2.28:1** на subtle. При этом именно этот border определяет границу `text-field`, `select-field`, `search-field`, фильтров и secondary controls; различие raised/base поверхностей само по себе также недостаточно. Это ниже 3:1 для визуальной информации, необходимой для распознавания UI-компонента (WCAG 1.4.11).

**Impact:** слабовидящий пользователь может не увидеть границы поля, области поиска или кнопки до фокуса; форма выглядит как обычный текст на фоне.

**Concrete contract fix:** ввести отдельную пару `colors.control-border` / `colors.control-border-dark` с контрастом ≥3:1 ко всем разрешённым соседним поверхностям и сослать на неё интерактивные компоненты. Рабочие кандидаты: light `#7A918C`, dark `#5F7B73`; перепроверить автоматически. Текущий low-contrast `border` можно оставить для декоративных разделителей, если он нигде не единственный носитель границы/состояния.

#### A11Y-H2 — Навигация становится безымянной или исчезает на rail, узкой ширине и при zoom

**Тип:** Contract gap + Illustrative HTML gap.  
**Где:** `EXPERIENCE.md:79`, `EXPERIENCE.md:149-151`, `EXPERIENCE.md:162-165`; `.working/key-library.html:20-21,29`; `.working/key-meeting-detail.html:6-7,9` selectors `.nav a`, `.nav span`, `.side`; `.working/key-processing.html:6-7,9` те же selectors.

На 64 px rail референсы скрывают `.nav span`. В library glyph одновременно `aria-hidden`, поэтому ссылка теряет accessible name; в detail/processing именем остаётся непонятный символ. Ниже 900 px `.side` скрыта полностью. Library рисует «☰» через `.top::before`, то есть это не фокусируемая кнопка; detail/processing не показывают даже такого псевдо-триггера. `EXPERIENCE.md` говорит «Nav overlay», но не задаёт триггер, имя, `aria-expanded`, focus order, Escape и focus return. При браузерном масштабировании эти breakpoints применяются так же, как на узком экране.

**Impact:** клавиатурный и screen-reader пользователь теряет основную навигацию; на 200% zoom часть пользователей не может перейти к Встречам, Участникам, Профилям или Настройкам.

**Concrete contract fix:** добавить `mobile-nav-trigger` как настоящий `<button>` с видимым текстом/доступным именем, `aria-expanded` и `aria-controls`; определить overlay/inert background, начальный focus, Escape и возврат focus. На rail сохранять accessible name через `aria-label` или visually-hidden текст, а текущую страницу обозначать `aria-current="page"`. Добавить первым фокусируемым элементом skip link «К основному содержимому». Ни одна ширина/zoom не должна оставаться без доступной навигации.

#### A11Y-H3 — Плеер в референсе не реализует обещанные клавиатурные и caption/transcript controls

**Тип:** Illustrative HTML gap; контракт требует уточнения anatomy.  
**Где:** `EXPERIENCE.md:92`, `EXPERIENCE.md:128-130`, `EXPERIENCE.md:153`; `DESIGN.md:196-199`, `DESIGN.md:334`; `.working/key-meeting-detail.html:5,9` selectors `.video`, `.play`, `.controls`, `.progress`; `.working/design-directions-1.html:136-193,607-610`.

Референс содержит только кнопку Play. Временная шкала — нефокусируемый `<span>`, fullscreen — скрытый от AT glyph, отсутствуют pause, seek, mute/volume, current/total announcement, captions state и явный переход к расшифровке. Это противоречит уже заявленному «keyboard play/pause/seek, captions/transcript access».

**Impact:** пользователь клавиатуры или screen reader не может проверить исходную запись — центральную trust-функцию продукта; без captions/transcript control часть видео недоступна пользователям с нарушениями слуха.

**Concrete contract fix:** закрепить anatomy `media-player`: предпочтительно нативные `<video controls>` / `<audio controls>`; при custom UI — именованные buttons, slider с `aria-valuemin/max/now/valuetext`, доступные mute/volume/fullscreen, elapsed/total и playback-error. Добавить `track kind="captions"` из текущей VTT-расшифровки, когда она существует, и отдельную кнопку/ссылку «Открыть расшифровку» с явным состоянием «Субтитры недоступны», когда track нет. Audio и video должны иметь одинаковый логический набор controls.

#### A11Y-H4 — Evidence links не ведут к конкретному сегменту и не создают объявляемый focus target

**Тип:** Illustrative HTML gap + частичный Contract gap.  
**Где:** `EXPERIENCE.md:47`, `EXPERIENCE.md:95-96`, `EXPERIENCE.md:129`, `EXPERIENCE.md:154`, `EXPERIENCE.md:203-208`; `.working/key-meeting-detail.html:9` selectors `.evidence`, `#evidence`, `.segment.active`, `.timestamp`.

Все четыре ссылки имеют одинаковый `href="#evidence"` и ведут только к контейнеру Расшифровки; timestamp links имеют `href="#"`. Конкретные сегменты не имеют уникальных IDs или программно фокусируемой цели. Активный сегмент отличается только фоном/левой границей и не имеет `aria-current` либо текстового маркера. Референс также не отражает объявление verified/unverified state.

**Impact:** пользователь не понимает, какой фрагмент подтверждает выбранную договорённость; screen reader не получает смену контекста, а клавиатурный focus остаётся на старой ссылке. Это ломает SM-3/FR-17 на уровне референса.

**Concrete contract fix:** каждому `transcript-segment` дать стабильный DOM id; verified action связывать с ним через `href`, `aria-describedby` и/или обработчик. После активации: seek → фокус на segment (`tabindex="-1"`) → одно polite announcement вида «Подтверждение к договорённости …, 26:41, Спикер 1, проверено»; play только для действия с текстом «Воспроизвести». Добавить видимый marker «Фрагмент подтверждения» и программное current state, не только цвет. Unresolved item остаётся текстом без ложной ссылки.

#### A11Y-H5 — Visual reordering расходится с DOM order, а действия теряются при reflow

**Тип:** Contract tension + Illustrative HTML gap.  
**Где:** `EXPERIENCE.md:43-51`, `EXPERIENCE.md:128`, `EXPERIENCE.md:156`, `EXPERIENCE.md:162-165`; `.working/key-meeting-detail.html:7-9` selectors `.right{display:contents}`, `.summary{order:1}`, `.agreements{order:2}`, `.left{order:3}`, `.top-actions .button:first-child{display:none}`.

На narrow layout визуально summary/agreement поставлены до player, но DOM и keyboard/screen-reader sequence по-прежнему начинают с `.left` (player/metadata). Это расходится с заявленным reading order. Ниже 560 px «Экспорт» просто скрыт, хотя Accessibility Floor обещает reflow без потери actions; desktop zoom способен попасть в тот же breakpoint.

**Impact:** зрячий пользователь и screen reader читают страницу в разной последовательности; при zoom действие экспорта исчезает вместо reflow, что затрудняет ориентацию и выполнение задачи.

**Concrete contract fix:** сделать канонический DOM order равным reading order: heading → summary → agreements → player → metadata → transcript; desktop placement решать grid areas без изменения смысловой последовательности. Не скрывать actions по width: переносить «Экспорт» в доступный labelled overflow menu. Добавить acceptance check на 200% zoom: DOM/focus/visual order согласованы, все действия достижимы, горизонтального page scroll нет.

### Medium

#### A11Y-M1 — Live-region contract недостаточно точен для progress, cancel и resync

**Тип:** Contract gap + Illustrative HTML gap.  
**Где:** `EXPERIENCE.md:90`, `EXPERIENCE.md:109-124`, `EXPERIENCE.md:132`, `EXPERIENCE.md:152`; `.working/key-processing.html:9` selectors `.bar[role="progressbar"]`, `.badge`, `.stage-state`, `.actions`.

Контракт верно запрещает объявлять heartbeat, но не закрепляет стабильный live node, atomicity и поведение при `cancelling`, `cancelled`, reconnect/resync и `outcomeUnknown`. Mock имеет корректный `progressbar`, но текущий stage/status не live и cancel feedback не показан.

**Impact:** screen reader может не заметить завершение этапа, принятие отмены, восстановление после reconnect или ошибку; частые DOM-обновления при неудачной реализации, наоборот, создадут шум.

**Concrete contract fix:** один стабильный `role="status" aria-live="polite" aria-atomic="true"` для смысловых переходов; ошибки, требующие немедленного действия, — `role="alert"`. Percent остаётся на `progressbar`, heartbeat визуален и не live. После cancel кнопка становится «Отменяется…», busy/disabled; один раз объявляются `Отмена запрошена`, terminal result и `Состояние восстановлено: …`; focus не прыгает.

#### A11Y-M2 — Не закрыты семантика и keyboard model всех overlays/popovers

**Тип:** Contract gap.  
**Где:** `EXPERIENCE.md:39`, `EXPERIENCE.md:101-104`, `EXPERIENCE.md:122-124`, `EXPERIENCE.md:151`, `DESIGN.md:242-258`.

Focus trap/restore определены только в общих словах для consent/confirm. Не закреплены `role`, accessible name/description, inert background и initial focus; `export-menu`, filter popovers и mobile navigation не имеют keyboard model.

**Impact:** focus может уйти за dialog, меню может оказаться недоступным с клавиатуры, а после закрытия пользователь потеряет место.

**Concrete contract fix:** для dialogs задать `role="dialog"`, `aria-modal="true"`, title/description IDs, inert background, initial focus на title либо безопасное действие и обязательный return focus; destructive action никогда не initial. Для `export-menu`/filters: trigger button с `aria-expanded/controls`, документированный Tab/Arrow/Escape model, outside-close и возврат focus. Modal stack остаётся запрещён.

#### A11Y-M3 — Whole-card meeting links создают перегруженные имена и не совместимы с nested actions

**Тип:** Contract gap + Illustrative HTML gap.  
**Где:** `EXPERIENCE.md:86`; `.working/key-library.html:63,68,73` selector `a.meeting-row`.

Весь ряд — одна ссылка, accessible name которой включает title, snippet, tags, participants, status, date, size и glyph. При добавлении обещанного nested retry/error action внутри ссылки получится конфликт интерактивных элементов.

**Impact:** screen reader вынужден прослушивать длинное имя на каждой строке; retry может одновременно активировать navigation или породить невалидную семантику.

**Concrete contract fix:** `meeting-row` сделать `<article>`/`<li>` с heading-link «Открыть встречу …», отдельным metadata/status description и sibling retry/error buttons. Зафиксировать, что row не является интерактивным контейнером; pointer click может делегировать title link только без захвата кликов дочерних controls.

#### A11Y-M4 — `ink-muted` условно проваливает 4.5:1 на subtle surfaces

**Тип:** Contract gap.  
**Где:** `DESIGN.md:22-25`, `DESIGN.md:282-283`.

`#5E7471` на `#EEF3F1` даёт **4.45:1**, а dark `#78918B` на `#202D29` — **4.24:1**. Токен разрешён для metadata, но допустимый background не ограничен.

**Impact:** мелкие метаданные 12–13 px могут не пройти WCAG 1.4.3 в sidebar/filter/subtle cards.

**Concrete contract fix:** запретить `ink-muted` на subtle surfaces и использовать там `ink-secondary` (4.77:1 light, 7.08:1 dark), либо скорректировать muted pair до ≥4.5:1 на каждой разрешённой поверхности. Добавить матрицу «foreground token → permitted backgrounds».

#### A11Y-M5 — Form errors и custom multi-select filters не имеют программного контракта

**Тип:** Contract gap.  
**Где:** `EXPERIENCE.md:83-89`, `EXPERIENCE.md:97-102`, `DESIGN.md:325-331`.

Постоянные labels и inline validation заявлены, но не определены `aria-invalid`, связь hint/error, error summary/focus и keyboard semantics для tag/participant multi-select.

**Impact:** screen reader может не узнать причину отказа импорта/профиля или выбранные значения фильтра; custom listbox легко становится недоступным.

**Concrete contract fix:** предпочесть native inputs/selects. Для ошибок — label + `aria-describedby` на hint/error, `aria-invalid="true"`, текстовая причина и после failed submit focus на error summary/первое invalid поле. Для multi-select определить combobox/listbox semantics, announced selected count, удаление chip отдельной именованной кнопкой и Escape без потери введённого текста.

#### A11Y-M6 — Target-size contract задаёт только высоту и расходится с timestamp mock

**Тип:** Contract gap + Illustrative HTML gap.  
**Где:** `DESIGN.md:104-119`, `DESIGN.md:210-214`, `EXPERIENCE.md:150`; `.working/key-meeting-detail.html:8` selector `.timestamp{min-height:32px}`.

Обещан control-min-height 44 px, но inline-size/spacing exceptions не формализованы. Narrow mock уменьшает интерактивный timestamp до 32 px по высоте, несмотря на собственный UX floor.

**Impact:** точные timecode/copy/delete controls могут стать трудными для пользователей с нарушениями моторики, особенно на touch secondary surface.

**Concrete contract fix:** закрепить минимум WCAG 2.2 AA **24×24 CSS px** для каждого target либо документированное spacing exception; для icon-only, player, timestamp, copy и destructive controls сохранить продуктовый floor **44×44 px**. Добавить `control-min-inline-size` и не уменьшать timestamp на narrow layout.

### Low

#### A11Y-L1 — Approved direction включает smooth scroll без reduced-motion override

**Тип:** Illustrative HTML gap.  
**Где:** `.working/design-directions-1.html:16`; `EXPERIENCE.md:155`.

`html { scroll-behavior: smooth; }` не отключается через `prefers-reduced-motion`, хотя spine это явно требует.

**Concrete contract fix:** в каждом promoted HTML reference добавить `@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; } }`; функциональные seek/focus transitions остаются мгновенными.

#### A11Y-L2 — Кнопка «Создать заново» теряет объект вне визуального контекста

**Тип:** Illustrative HTML gap / microcopy.  
**Где:** `.working/key-meeting-detail.html:9` selector `.notice .button`; `.working/design-directions-1.html:631`; `EXPERIENCE.md:53-71`.

Screen reader button list покажет неоднозначное «Создать заново». Остальная русская microcopy в целом ясная и stage-specific.

**Concrete contract fix:** использовать «Обновить краткую сводку» или «Создать краткую сводку заново»; в production copy не выводить внутренние английские `stale/manual/unverified/provider/local/retry` без русской пользовательской формулировки.

## Strengths

- `EXPERIENCE.md:145-156` уже задаёт редкий для черновика полноценный accessibility floor: keyboard, focus visibility, dialog restore, meaningful live announcements, media access, reduced motion и 200% reflow.
- Evidence behavior запрещает autoplay без явной надписи и запрещает ложную ссылку при unresolved state (`EXPERIENCE.md:95`, `EXPERIENCE.md:129`).
- Состояния не полагаются только на цвет: status/icon/label, important label, stale/unverified text и честный determinate/indeterminate progress закреплены в обоих spines.
- Error/recovery microcopy называет этап, сохранённые результаты и безопасное следующее действие; `key-processing.html` хорошо демонстрирует это для out-of-memory failure.
- Primary text contrast, semantic soft states и focus colors в целом сильные: on-accent/accent 6.10:1, success/soft 4.75:1, warning/soft 4.56:1, danger/soft 5.30:1; light focus к основным поверхностям 4.19–4.70:1, dark focus 5.98–7.55:1.
- В `key-library.html` search имеет программный label/help, active page использует `aria-current`, status текстовый, pagination bounded; в `key-processing.html` determinate bar имеет корректные `role` и `aria-value*`.
- Dialog destructive action не должен получать initial focus; Escape не отменяет job; focus не должен скрываться sticky player — хорошие защитные инварианты.

## Mechanical notes

- Контраст рассчитан по sRGB relative luminance для всех frontmatter color pairs, реально используемых как text/state/focus/control boundary. `border` может быть low-contrast только как декоративный divider; findings относятся к случаям, где border нужен для распознавания control/state.
- HTML-файлы статичны и без JavaScript. Поэтому отсутствие runtime behavior не считалось дефектом само по себе; High отмечен только там, где DOM/CSS референса противоречит spine или может закрепить недоступную структуру при handoff.
- `ia-2026-08-31.excalidraw` принят как информационная карта, не production UI. В ней не найдено отдельного accessibility-противоречия, но её modal/nav узлы наследуют исправления A11Y-H2 и A11Y-M2.
- Нужны release acceptance checks минимум в Chromium + Firefox: keyboard-only; NVDA/Firefox или JAWS/Chrome на Windows; VoiceOver/Chrome либо Safari на macOS как дополнительная проверка; 200% zoom на 1024/1280 widths; 320 CSS px reflow; light/dark contrast; `prefers-reduced-motion`.
