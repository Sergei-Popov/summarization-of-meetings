---
name: Контекст
description: Спокойная, проверяемая визуальная система локального рабочего архива встреч.
status: final
project: summarization-of-meetings
created: 2026-08-31
updated: 2026-09-01
sources:
  - ../../prds/prd-summarization-of-meetings-2026-08-31/prd.md
  - ../../prds/prd-summarization-of-meetings-2026-08-31/addendum.md
  - ../../prds/prd-summarization-of-meetings-2026-08-31/research-landscape.md
  - ../../architecture/architecture-summarization-of-meetings-2026-08-31/ARCHITECTURE-SPINE.md
colors:
  surface-base: '#F5F7F6'
  surface-base-dark: '#101816'
  surface-raised: '#FFFFFF'
  surface-raised-dark: '#18221F'
  surface-subtle: '#EEF3F1'
  surface-subtle-dark: '#202D29'
  ink-primary: '#162C2A'
  ink-primary-dark: '#EAF3F1'
  ink-secondary: '#55706D'
  ink-secondary-dark: '#A6BBB6'
  ink-muted: '#596F6B'
  ink-muted-dark: '#819A94'
  border: '#D8E2DF'
  border-dark: '#334640'
  border-strong: '#B8CBC6'
  border-strong-dark: '#4D655F'
  control-border: '#708781'
  control-border-dark: '#66857C'
  accent: '#126E65'
  accent-dark: '#48B8A8'
  accent-hover: '#0D5B53'
  accent-hover-dark: '#5EC9BA'
  accent-soft: '#E8F4F1'
  accent-soft-dark: '#173B35'
  on-accent: '#FFFFFF'
  on-accent-dark: '#071B18'
  success: '#287A4B'
  success-dark: '#5AC486'
  success-soft: '#E9F6EE'
  success-soft-dark: '#153523'
  warning: '#A85D19'
  warning-dark: '#F0A65B'
  warning-soft: '#FFF4E7'
  warning-soft-dark: '#432A16'
  danger: '#B33A3A'
  danger-dark: '#F27474'
  danger-soft: '#FFF0F0'
  danger-soft-dark: '#402020'
  focus: '#0B6DF1'
  focus-dark: '#74A8FF'
  player-surface: '#273532'
  player-surface-dark: '#050907'
  player-control: '#FFFFFF'
  player-control-dark: '#FFFFFF'
  overlay: '#162C2A'
  overlay-dark: '#000000'
typography:
  page-title:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  section-title:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 18px
    fontWeight: '700'
    lineHeight: '1.35'
    letterSpacing: -0.01em
  body:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 15px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 12px
    fontWeight: '650'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  meta:
    fontFamily: 'Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 12px
    fontWeight: '450'
    lineHeight: '1.45'
  mono:
    fontFamily: 'SFMono-Regular, Consolas, Liberation Mono, monospace'
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.45'
rounded:
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px
  DEFAULT: 8px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 20px
  '6': 24px
  '8': 32px
  '10': 40px
  '12': 48px
  content-gutter: 24px
  content-gutter-compact: 16px
  sidebar-width: 216px
  rail-width: 64px
  content-max: 1200px
  control-min-height: 44px
  control-min-inline-size: 44px
  target-min: 24px
components:
  app-shell:
    background: '{colors.surface-base}'
    sidebar-background: '{colors.surface-subtle}'
    foreground: '{colors.ink-primary}'
    divider: '{colors.border}'
    sidebar-width: '{spacing.sidebar-width}'
    skip-link-background: '{colors.surface-raised}'
    skip-link-focus: '{colors.focus}'
  mobile-nav-trigger:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  primary-button:
    background: '{colors.accent}'
    foreground: '{colors.on-accent}'
    hover-background: '{colors.accent-hover}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  secondary-button:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  destructive-button:
    background: '{colors.danger}'
    foreground: '{colors.player-control}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  text-field:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  select-field:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  status-badge:
    background: '{colors.accent-soft}'
    foreground: '{colors.accent}'
    radius: '{rounded.full}'
  meeting-row:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  search-field:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    focus: '{colors.focus}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  filter-bar:
    background: '{colors.surface-subtle}'
    foreground: '{colors.ink-secondary}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  import-dropzone:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-secondary}'
    border: '{colors.control-border}'
    active-border: '{colors.accent}'
    radius: '{rounded.lg}'
  stage-progress:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    track: '{colors.border}'
    fill: '{colors.accent}'
    radius: '{rounded.lg}'
  notice-banner:
    background: '{colors.warning-soft}'
    foreground: '{colors.warning}'
    border: '{colors.warning}'
    radius: '{rounded.md}'
  media-player:
    background: '{colors.player-surface}'
    foreground: '{colors.player-control}'
    radius: '{rounded.lg}'
    control-min-height: '{spacing.control-min-height}'
    control-min-width: '{spacing.control-min-inline-size}'
  summary-card:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  agreement-item:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    divider: '{colors.border}'
    important-marker: '{colors.warning}'
  evidence-link:
    foreground: '{colors.accent}'
    unverified-foreground: '{colors.warning}'
    focus: '{colors.focus}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  transcript-segment:
    background: '{colors.surface-raised}'
    active-background: '{colors.accent-soft}'
    foreground: '{colors.ink-primary}'
    timestamp: '{colors.accent}'
    divider: '{colors.border}'
    timestamp-min-height: '{spacing.control-min-height}'
    timestamp-min-width: '{spacing.control-min-inline-size}'
  tag-chip:
    background: '{colors.surface-subtle}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    radius: '{rounded.full}'
    min-height: '{spacing.target-min}'
    min-width: '{spacing.target-min}'
  participant-chip:
    background: '{colors.accent-soft}'
    foreground: '{colors.ink-primary}'
    border: '{colors.control-border}'
    radius: '{rounded.full}'
    min-height: '{spacing.target-min}'
    min-width: '{spacing.target-min}'
  task-link-card:
    background: '{colors.surface-raised}'
    foreground: '{colors.accent}'
    border: '{colors.control-border}'
    radius: '{rounded.md}'
    min-height: '{spacing.control-min-height}'
    min-width: '{spacing.control-min-inline-size}'
  profile-stage-card:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  consent-dialog:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.warning}'
    radius: '{rounded.xl}'
    overlay: '{colors.overlay}'
  confirm-dialog:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border-strong}'
    radius: '{rounded.xl}'
    overlay: '{colors.overlay}'
  export-menu:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border}'
    radius: '{rounded.md}'
  empty-state:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-secondary}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  diagnostic-panel:
    background: '{colors.surface-subtle}'
    foreground: '{colors.ink-primary}'
    border: '{colors.border}'
    code-foreground: '{colors.ink-secondary}'
    radius: '{rounded.lg}'
---

## Brand & Style

Одобренное направление 01 «Спокойное рабочее пространство» и продуктовый label «Контекст» задают профессиональный content-first инструмент средней/высокой плотности, в котором сводка, договорённости и подтверждения выглядят как рабочие данные, а не как эффектная демонстрация AI. Визуальный характер внушает спокойное доверие к локальному архиву, но не создаёт ложное ощущение безошибочности результата.

### Implementation basis

Ant Design — обязательная базовая UI-система. Собирайте рабочий интерфейс из готовых компонентов Ant Design, composition primitives, функциональных props и theme/component tokens через `ConfigProvider`.

Не создавайте параллельную библиотеку базовых элементов и не добавляйте CSS, CSS Modules, styled wrappers или переопределения внутренних селекторов. Semantic DOM hooks используются только для семантики, доступности и тестирования; передача через них `styles` или `classNames` также считается пользовательской стилизацией. Если требование нельзя реализовать разрешёнными средствами, приостановите реализацию и оформите отдельное дизайн-решение.

Документированное исключение — browser-native `<video controls>` и `<audio controls>`. Для fallback-контролов используйте только перечисленные ниже компоненты Ant Design; исключение не разрешает собственные стили или отдельную библиотеку контролов.

Светлая тема — исходная, тёмная следует системной настройке. Хром сдержанный, контент плотный, а бирюзовый акцент означает действие, выбранный объект или проверяемую связь. Предупреждения и ошибки заметны, но не окрашивают целые экраны. Игровые механики, «магическое» свечение AI, декоративные градиенты и celebratory-анимация исключены.

Одобренный визуальный референс: [три направления, вариант 01](mockups/design-directions.html). Он иллюстрирует характер и двухзонную страницу Встречи, но не является спецификацией. При конфликте с визуальным референсом `DESIGN.md` и `EXPERIENCE.md` имеют приоритет.

## Colors

Передайте токены этого спайна в отдельные светлую и тёмную конфигурации темы `ConfigProvider`.

- Surface-токены строят холст, карточки и вторичные области; ink-токены задают иерархию текста. Разрешённые пары определяет матрица ниже.
- `{colors.accent}` / `{colors.accent-dark}` отмечает действие, активный объект, таймкод или evidence-связь, но не «уверенность AI»; `{colors.player-surface}` удерживает медиа в нейтральной тёмной плоскости.
- Success означает завершение, warning — состояние, требующее внимания, danger — потерю данных или невосстановимое действие. Семантика всегда дублируется текстом/значком.

Цель — WCAG 2.2 AA: не менее 4.5:1 для обычного текста, 3:1 для крупного текста/компонентов и focus ring. `{colors.on-accent}` на `{colors.accent}` и dark-пара проверяются на 4.5:1. Все пары, включая warning/danger, проверяются автоматически перед реализацией.

### Foreground/background permission matrix

| Foreground | Permitted backgrounds | Constraint |
|---|---|---|
| `{colors.ink-primary}` / `-dark` | surface base, raised, subtle в соответствующей теме | Основной текст и labels. |
| `{colors.ink-secondary}` / `-dark` | surface base, raised, subtle в соответствующей теме | Вторичный текст; обычный размер. |
| `{colors.ink-muted}` / `-dark` | surface base, raised, subtle в соответствующей теме | Метаданные 12–13 px; новые значения сохраняют ≥4.5:1 на всех трёх поверхностях. |
| `{colors.accent}` / `-dark` | surface base, raised, subtle в соответствующей теме | Link/action text; не использовать на accent/semantic fills. |
| `{colors.on-accent}` / `-dark` | accent и accent-hover в соответствующей теме | Текст primary control. |
| `success`, `warning`, `danger` / `-dark` | Только соответствующая `*-soft` поверхность либо surface-пара, прошедшая автоматическую проверку | Семантика всегда продублирована текстом/значком. |
| `{colors.player-control}` / `-dark` | player-surface в соответствующей теме | Плеер и его controls. |
| `{colors.control-border}` / `-dark` | surface base, raised, subtle в соответствующей теме | ≥3:1; интерактивные outline boundaries. |
| `{colors.border}` / `-dark`, `border-strong` / `-dark` | Любая surface в соответствующей теме | Только декоративный divider/container edge; не обозначает control/state самостоятельно. |

## Typography

Интерфейс использует Ant Design `Typography` и единый theme `fontFamily` с локальным/system-first sans stack; Inter применяется только из локального bundle, внешние font CDN запрещены.

- `{typography.page-title}` — название страницы/Встречи; `{typography.section-title}` — содержательные секции.
- `{typography.body}` — сводка и длинный текст; `{typography.body-sm}` — пояснения/snippets.
- `{typography.label}` — поля и действия; `{typography.meta}` — дата, длительность, размер, модель, status.
- `{typography.mono}` — только безопасные diagnostic codes, таймкоды и технические IDs.

Текст не обрезается в договорённостях, ошибках, consent и delete-confirmation. В строках библиотеки допустимы две строки snippet.

## Layout & Spacing

Базовый ритм — 4 px; рабочие интервалы — 8/12/16/24/32. Контент ограничен `{spacing.content-max}`.

На wide desktop `app-shell` собирается из Ant Design `Layout`, `Grid`, `Flex` и `Space`; sidebar имеет ширину `{spacing.sidebar-width}`. Страница Встречи имеет две зоны: слева плеер/метаданные, справа сводка/договорённости; Расшифровка занимает нижнюю ширину. На средней ширине sidebar становится rail `{spacing.rail-width}`, на узкой композиция — одноколоночной. Порядок, sticky-поведение, nav overlay и reflow определены в `EXPERIENCE.md.Information Architecture`, `Interaction Primitives` и `Responsive & Platform`.

Одобренные композиционные референсы: [библиотека](mockups/library.html), [страница Встречи](mockups/meeting-detail.html), [ход обработки](mockups/processing.html).

Каждая интерактивная цель имеет минимум `{spacing.target-min}` × `{spacing.target-min}` либо документированное WCAG spacing exception. Продуктовый floor для icon-only, player, timecode/evidence, copy и destructive controls — `{spacing.control-min-inline-size}` × `{spacing.control-min-height}` без уменьшения на узкой ширине. Табличная плотность допустима только без горизонтального скролла для основного действия.

## Elevation & Depth

Иерархия создаётся тоном, границами и расстоянием. Тени и границы задаются theme/component tokens Ant Design: карточки используют 1 px `{colors.border}` и малую тень в light, в dark — без тени; popover/dialog используют системную secondary shadow. Sticky player отделяется границей. Hover не является единственным признаком кликабельности.

## Shapes

`{rounded.md}` — поля/кнопки; `{rounded.lg}` — карточки/плеер; `{rounded.xl}` — dialogs; `{rounded.full}` — badges/chips. Эти значения подаются через Ant Design global/component radius tokens, а не через selector overrides. `agreement-item` остаётся линейным списком. Participant initials могут быть круглыми, но не должны выглядеть как account presence.

## Components

`EXPERIENCE.md.Component Patterns` задаёт поведение каждого ID; здесь зафиксированы только визуальные свойства и соответствие компонентам Ant Design. Product IDs — тонкие композиционные обёртки над Ant Design, а не новые базовые элементы управления.

| Product components | Ant Design basis |
|---|---|
| `app-shell`, `mobile-nav-trigger` | `Layout`, `Menu`, `Grid`, `Flex`, `Space`, `Button`, `Drawer` |
| `primary-button`, `secondary-button`, `destructive-button` | `Button` variants and danger state |
| `text-field`, `search-field`, `select-field`, `filter-bar` | `Form`, `Input`, `Input.Search`, `Select`, `DatePicker`, `Popover`, `Space` |
| `status-badge`, `tag-chip`, `participant-chip` | `Tag`, `Badge`, multi-value `Select` |
| `meeting-row`, `summary-card`, `agreement-item`, `task-link-card`, `profile-stage-card` | `List`, `Card`, `Typography`, `Descriptions`, `Space` |
| `import-dropzone`, `stage-progress`, `notice-banner` | `Upload.Dragger`, `Steps`, `Progress`, `Alert` |
| `evidence-link`, `transcript-segment` | `Button` link variant, `Anchor`, `List`, `Typography` |
| `consent-dialog`, `confirm-dialog`, `export-menu` | `Modal`, `Dropdown`, `Menu` |
| `empty-state`, `diagnostic-panel` | `Empty`, `Result`, `Descriptions`, `Collapse`, `Typography` |
| `media-player` | Browser-native `video`/`audio`; Ant Design `Space`, `Button`, `Slider` and `Typography` only for documented fallback controls |

| Component ID | Visual contract |
|---|---|
| `app-shell` | Sidebar — subtle, рабочая область — base; skip link, rail focus и active item используют контрастные surface/focus/accent-состояния. |
| `mobile-nav-trigger` | Outline-кнопка минимум 44×44: menu icon, текстовый label и видимый focus ring. |
| `primary-button` | Accent fill и максимальный акцент в группе; loading сохраняет footprint и видимый label. |
| `secondary-button` | Raised surface, `{colors.control-border}` и меньший акцент, чем у primary. |
| `destructive-button` | Danger fill; визуально отделён от безопасных действий. |
| `text-field` | Постоянный label, `{colors.control-border}`, 3 px focus ring; error занимает строку под полем. |
| `select-field` | Геометрия `text-field` с chevron; выбранный mode виден текстом. |
| `status-badge` | Semantic icon + label на soft surface; цвет не единственный носитель состояния. |
| `meeting-row` | Название, дата, длительность, status, modified, disk size, metadata; title — до двух строк. |
| `search-field` | Широкое поле с `{colors.control-border}`, постоянным label и ненавязчивой подсказкой shortcut. |
| `filter-bar` | Subtle container; вложенные controls имеют `{colors.control-border}`, активные фильтры — neutral chips. |
| `import-dropzone` | `{colors.control-border}` + icon + picker label; drag-active — accent, error — локальная danger-индикация без сплошной заливки. |
| `stage-progress` | Три этапа с track/fill, status и elapsed; indeterminate-вариант не показывает числовой percent. |
| `notice-banner` | Warning-soft panel: заголовок, причина и визуально вторичное безопасное действие. |
| `media-player` | Нейтральная dark surface; controls не меньше 44×44; audio variant использует metadata/waveform без декора. |
| `summary-card` | Overview — первый визуальный уровень; manual/stale/unverified markers примыкают к заголовку. |
| `agreement-item` | Линейная anatomy: importance, текст, responsible/due и evidence; важность отмечена marker + label. |
| `evidence-link` | Accent timestamp/play label минимум 44×44; unverified-вариант — warning + текстовый marker. |
| `transcript-segment` | Timestamp target минимум 44×44, speaker и текст; активный фрагмент — accent-soft + текстовый marker. |
| `tag-chip` | Neutral pill; automatic origin имеет отдельный edit-state marker. |
| `participant-chip` | Initials + name; визуально отличается от speaker label и account presence. |
| `task-link-card` | Task number — первый уровень, внешний переход — glyph; edit-state показывает URL/extraction metadata. |
| `profile-stage-card` | Симметричные Transcription/Summarization cards: mode, engine, model, readiness и boundary. |
| `consent-dialog` | Warning border; stage/provider/model/data сгруппированы над primary/secondary actions. |
| `confirm-dialog` | Consequence list над actions; destructive и safe actions визуально разделены. |
| `export-menu` | В каждой строке видны format и content; завершение имеет текстовый feedback. |
| `empty-state` | Один текстовый блок и одно действие; без mascot illustration. |
| `diagnostic-panel` | Subtle surface, metadata labels и mono code с ровной технической иерархией. |

## Do's and Don'ts

| Do | Don't |
|---|---|
| Сводка → договорённости → evidence как явная иерархия | Смешивать summary, transcript и job log в одну панель |
| Teal для действий и проверяемых переходов | Окрашивать teal всё «сгенерированное AI» |
| Status текстом/значком в обеих темах | Передавать ready/error/local/provider только цветом |
| Participants и speaker labels визуально различны | Подразумевать автоматическую связь участников с репликами |
| Явные stale/manual/unverified markers | Выдавать старое или неподтверждённое за актуальное |
| Local/system fonts and assets | CDN, remote font/icons/telemetry assets |
| Ant Design components, composition primitives and `ConfigProvider` tokens | Reimplementing available controls or styling Ant Design through internal class selectors |
| Функциональные props; semantic DOM hooks только для accessibility и tests | CSS, CSS Modules, styled wrappers, `styles`/`classNames` customization |
| Destructive red внутри confirmation | Удаление как обычная primary-кнопка |

Поведенческие правила, включая доступность плеера, честный progress и границы destructive actions, определены в `EXPERIENCE.md.Component Patterns`, `State Patterns` и `Interaction Primitives`.
