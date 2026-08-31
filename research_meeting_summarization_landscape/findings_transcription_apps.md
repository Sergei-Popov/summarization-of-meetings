# Смежные open-source/local-first инструменты транскрибации и суммаризации встреч

Проверено: 2026-08-31. Рассмотрены три наиболее релевантных и документированных проекта. Использованы только первичные источники: официальные репозитории, README, документация и GitHub Releases. Если возможность не заявлена в этих источниках, она отмечена как «не подтверждена», а не как безусловно отсутствующая.

## Краткое сравнение

| Инструмент | Форм-фактор и позиционирование | Импорт видео/аудио | ASR и diarization | LLM-суммаризация | OpenAI-compatible / local LLM | Подтверждённый пробел относительно целевого продукта |
|---|---|---|---|---|---|---|
| [Scriberr](https://github.com/rishikanthc/Scriberr) | Self-hosted web/PWA-приложение с локальным хранилищем записей и транскриптов | Аудио и видео; upload, drag-and-drop, folder watcher, recorder, API/CLI ingestion | Локальные Whisper, NVIDIA Parakeet и Canary; word-level timestamps; speaker diarization. В v1.2.0 также заявлена OpenAI transcription | Встроенные summary templates, генерация саммари и чат по транскрипту | Ollama и OpenAI API-compatible LLM; настраиваемый OpenAI base URL | Произвольный OpenAI-compatible **ASR** endpoint не заявлен; текущий README сообщает о временной паузе разработки |
| [Vibe](https://github.com/thewh1teagle/vibe) | Локальное кроссплатформенное desktop-приложение | Аудио/видео, несколько файлов, URL популярных видеосайтов, системный звук и микрофон | Whisper, Nemotron 3.5, Parakeet TDT v3; speaker diarization; VAD-backed stable timestamps | Многоязычные саммари через Claude API; локальный анализ и batch summaries через Ollama | Локальный Ollama подтверждён; OpenAI-compatible LLM endpoint не заявлен | Не self-hosted web UI; долговременная библиотека встреч/локальная БД и универсальная конфигурация провайдера не описаны |
| [noScribe](https://github.com/kaixxx/noScribe) | Privacy-first desktop GUI для интервью, качественных исследований и чувствительных записей; CLI/headless режим | Почти любые аудио/видео форматы; batch queue | Локальные Whisper V3 Turbo/faster-whisper и Pyannote; speaker detection; пользовательские CTranslate2-модели | В официальных возможностях не заявлена | Облачные или локальные LLM-провайдеры не заявлены; ASR строго локальный | Нет заявленной LLM-суммаризации и web-интерфейса; длительная обработка и обязательная ручная проверка транскрипта |

## 1. Scriberr

### Позиционирование и приватность

Scriberr — MIT-licensed self-hosted приложение, которое автор позиционирует как open-source и offline-first инструмент для приватной транскрибации. README прямо говорит, что аудио и видео транскрибируются локально и для этого доступны Whisper, NVIDIA Parakeet и Canary. Одновременно продукт поддерживает удалённые LLM, поэтому обещание «данные не уходят третьим сторонам» корректно применять к локальной транскрибации, но не автоматически ко всему pipeline при выборе облачного провайдера. Источник: [официальный README](https://github.com/rishikanthc/Scriberr#introduction).

### Поддерживаемый workflow

- Добавление аудио и видео, в том числе drag-and-drop; глобальный upload из интерфейса, folder watcher, API/CLI ingestion и встроенная запись аудио. Последний релиз также содержит исправление валидации MP4. Источники: [README](https://github.com/rishikanthc/Scriberr#introduction), [v1.2.0 release notes](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Очередь и видимый статус обработки, transcript reader с синхронизированным воспроизведением, переходом к позиции по тексту и подсветкой текущего фрагмента. Можно переименовывать говорящих, выделять важные места и добавлять заметки. Источники: [README и screenshots](https://github.com/rishikanthc/Scriberr#screenshots), [v1.2.0 release notes](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Speaker diarization, word-level timestamps и поддержка многодорожечных записей. Источники: [README](https://github.com/rishikanthc/Scriberr#introduction), [v1.2.0 release notes](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Суммаризация по шаблонам и чат по транскрипту. Можно подключить Ollama либо OpenAI API-compatible LLM; в v1.2.0 отдельно зафиксирован configurable OpenAI API Base URL. Источники: [README](https://github.com/rishikanthc/Scriberr#introduction), [v1.2.0 release notes](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Web UI запускается локально на `localhost:8080`, а PWA даёт desktop/mobile-подобный интерфейс. Данные приложения вынесены в persistent volume, содержащий `scriberr.db`, `uploads/` и `transcripts/`. Источник: [официальная установка и migration guide](https://github.com/rishikanthc/Scriberr#installation).

### Версия и подтверждённые ограничения

- Последний релиз — [v1.2.0 от 2025-12-17](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- В актуальном README автор сообщает, что разработка временно приостановлена, хотя проект не объявлен заброшенным. Это риск сопровождения для публичного продукта или источник требований к независимости форка. Источник: [Project status](https://github.com/rishikanthc/Scriberr#update-on-project-status).
- Релиз заявляет встроенную поддержку OpenAI transcription, но официальные материалы не подтверждают, что ASR можно направить на любой OpenAI-compatible base URL так же свободно, как LLM. Универсальная заменяемость **transcription provider** остаётся неподтверждённой.
- При переходе на v1.2.0 требуется разнести app data и model environment и пересоздать старое окружение WhisperX; это показывает, что обновление локального ML-runtime требует отдельного миграционного UX/документации. Источник: [migration guide](https://github.com/rishikanthc/Scriberr#migrating-from-v110).

## 2. Vibe

### Позиционирование и приватность

Vibe — MIT-licensed desktop-приложение для Windows, macOS и Linux с формулировкой «Transcribe audio and video right on your device». README заявляет полностью офлайн-транскрибацию без передачи данных наружу. Однако саммари через Claude API является внешним вызовом; для полностью локального анализа отдельно предусмотрен Ollama. Следовательно, интерфейс выбора режима должен ясно показывать границу локальности между ASR и LLM. Источник: [официальный README](https://github.com/thewh1teagle/vibe#features-).

### Поддерживаемый workflow

- Импорт аудио и видео, batch transcription нескольких файлов, получение медиа с YouTube/Vimeo/Facebook/Twitter и других сайтов, а также захват системного аудио или микрофона. Источник: [README](https://github.com/thewh1teagle/vibe#features-).
- Локальные модели Whisper, Nemotron 3.5 и Parakeet TDT v3; настройка моделей и расширенных model arguments; ускорение на GPU под основными ОС. Источник: [README](https://github.com/thewh1teagle/vibe#features-).
- Speaker diarization, realtime preview и отдельный VAD-backed режим стабильных timestamps, помеченный как более медленный. Источник: [README](https://github.com/thewh1teagle/vibe#features-).
- Быстрые многоязычные саммари через Claude API; локальный AI-анализ и пакетные саммари через Ollama. Поддержка общего OpenAI-compatible endpoint в официальном README не заявлена. Источник: [README](https://github.com/thewh1teagle/vibe#features-).
- Экспорт в SRT, VTT, TXT, HTML, PDF, JSON и DOCX, CLI и HTTP API со Swagger. Это делает Vibe удобным локальным engine/desktop tool, даже если целевой web workflow строится отдельно. Источник: [README](https://github.com/thewh1teagle/vibe#features-).

### Версия и подтверждённые ограничения

- Последний релиз — [v3.1.6 от 2026-08-28](https://github.com/thewh1teagle/vibe/releases/tag/v3.1.6), то есть проект активно выпускал обновления непосредственно перед датой проверки.
- Это desktop-приложение, а не self-hosted browser-based система. HTTP API подтверждён, но отдельный web UI для библиотеки встреч не заявлен.
- README не описывает локальную БД/долговременную коллекцию встреч, произвольные OpenAI-compatible LLM/ASR endpoints, summary templates для «решения / действия / риски» или просмотр исходного фрагмента из пункта саммари. Эти возможности следует считать неустановленными.
- Privacy claim требует уточнения по стадиям: локальная ASR остаётся офлайн, но выбор Claude API логически передаёт транскрипт внешнему сервису; Ollama сохраняет локальный режим. Это вывод из одновременно заявленных функций, а не отдельное обещание авторов.

## 3. noScribe

### Позиционирование и приватность

noScribe — GPL-3.0 desktop-приложение для создания и ручной проверки транскриптов интервью и других чувствительных записей. Официальный сайт подчёркивает: обработка полностью локальная, облака нет, продукт работает без сети. Основной фокус — достоверный редактируемый транскрипт для исследований, журналистики и других чувствительных сценариев, а не meeting intelligence. Источники: [официальный сайт](https://noscribe.de/en/), [privacy FAQ](https://noscribe.de/en/docs/faq/#can-i-trust-that-noscribe-does-not-send-audio-data-or-transcripts-to-the-outside).

### Поддерживаемый workflow

- Выбор почти любого аудио- или видеоформата; несколько файлов можно поставить в последовательную очередь. Выход: HTML, TXT или WebVTT. Источник: [usage guide](https://noscribe.de/en/docs/usage/).
- Два поставляемых локальных профиля Whisper V3 Turbo (`precise`/`fast`) на faster-whisper; разрешена установка собственных Faster-Whisper/CTranslate2 моделей. Источник: [advanced options](https://noscribe.de/en/docs/advanced-options/#use-special-transcription-models).
- Speaker detection на базе Pyannote с автоопределением или заданным числом говорящих; опциональные timestamps, паузы, disfluencies и экспериментальная разметка перекрывающейся речи. Источники: [официальный README](https://github.com/kaixxx/noScribe#what-is-noscribe), [usage guide](https://noscribe.de/en/docs/usage/).
- Очередь показывает статус и прогресс, позволяет отменить/перезапустить задачу и открыть даже неполный результат. Встроенный отдельный editor синхронизирует текст с аудио и поддерживает исправление и замену имён говорящих. Источник: [usage guide](https://noscribe.de/en/docs/usage/).
- С версии 0.7 есть CLI и `--no-gui`; [v0.7.2](https://github.com/kaixxx/noScribe/releases/tag/v0.7.2) отдельно заявляет true headless mode for servers. Это даёт строительный блок для автоматизации, но не готовое web-приложение.

### Версия и подтверждённые ограничения

- Последний релиз — [v0.7.2 от 2026-06-02](https://github.com/kaixxx/noScribe/releases/tag/v0.7.2).
- В официальном наборе возможностей и настройках отсутствует заявленная LLM-суммаризация, чат по транскрипту или конфигурация OpenAI-compatible/local LLM. Это не доказательство отсутствия любого экспериментального кода, но публично документированный workflow заканчивается проверкой и экспортом транскрипта.
- Официальный сайт оценивает обработку часа интервью примерно в 1–3 часа, на старых устройствах дольше, а установочный пакет с моделями — примерно в 3 ГБ. Источник: [How do I use noScribe?](https://noscribe.de/en/#how-do-i-use-noscribe).
- Авторы прямо требуют ручной проверки: возможны hallucinations, неправильное назначение говорящего, потеря содержания при одновременной речи, ошибки имён, повторяющиеся циклы текста и ухудшение пунктуации на длинных файлах. Источник: [Typical Issues with AI-Assisted Transcription](https://noscribe.de/en/docs/usage/#typical-issues-with-ai-assisted-transcription).
- Поддержка ОС ограничена: Windows 7/8 и Intel Mac больше не поддерживаются, для macOS требуется как минимум Sonoma; качество Linux-сборок зависит от дистрибутива. Источник: [FAQ](https://noscribe.de/en/docs/faq/).

## Сигналы для PRD

1. **Ближайший прямой comparable — Scriberr.** Он подтверждает спрос и жизнеспособность связки self-hosted web/PWA + локальные файлы/БД + video/audio upload + diarization + summary/chat + Ollama/OpenAI-compatible LLM. Отличительная точка целевого продукта должна быть сформулирована явно, а не сводиться к тому же набору функций.
2. **«Local-first» необходимо определять по каждой стадии.** ASR, diarization, LLM-суммаризация, хранение и telemetry могут иметь разные границы данных. Vibe и Scriberr показывают гибридный режим: локальная ASR сочетается с опциональным облачным LLM; noScribe показывает строгий offline baseline.
3. **Единая provider abstraction остаётся заметным пробелом.** Scriberr наиболее близок к OpenAI-compatible LLM и имеет OpenAI transcription, но произвольный OpenAI-compatible ASR endpoint публично не подтверждён. Vibe документирует только Claude API и Ollama; noScribe — только локальную ASR. Для PRD важно отдельно определить контракт провайдера транскрибации и контракт провайдера суммаризации.
4. **Проверка результата — часть основного workflow, а не исключение.** noScribe наиболее явно документирует ошибки ASR/diarization и необходимость сверки с аудио. Scriberr и Vibe демонстрируют нужный UX-паттерн: синхронизированный transcript reader, click-to-seek, timestamps и исправление speakers. Для саммари особенно важна прослеживаемость тезиса до фрагмента транскрипта/записи.
5. **Длинные локальные задачи требуют операционного UX.** Очередь, прогресс, cancel/retry, восстановление после перезапуска, выбор модели/устройства и понятное ожидание по времени повторяются в проектах. noScribe даёт количественный ориентир 1–3× real-time на CPU/старом железе; требования не должны предполагать мгновенную обработку.
6. **Суммаризация должна быть структурирована под рабочую встречу.** Существующие проекты подтверждают generic summary/chat, но в просмотренных первичных материалах не обнаружен хорошо специфицированный сквозной workflow «краткое содержание → решения → action items с ответственными/сроками → риски/open questions → ссылка на источник». Это потенциальный продуктовый фокус, который следует подтвердить у автора продукта, а не принимать без проверки.

## Источники

- Scriberr: [репозиторий и README](https://github.com/rishikanthc/Scriberr), [релиз v1.2.0](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Vibe: [репозиторий и README](https://github.com/thewh1teagle/vibe), [релиз v3.1.6](https://github.com/thewh1teagle/vibe/releases/tag/v3.1.6).
- noScribe: [официальный сайт](https://noscribe.de/en/), [usage guide](https://noscribe.de/en/docs/usage/), [advanced options](https://noscribe.de/en/docs/advanced-options/), [FAQ](https://noscribe.de/en/docs/faq/), [репозиторий](https://github.com/kaixxx/noScribe), [релиз v0.7.2](https://github.com/kaixxx/noScribe/releases/tag/v0.7.2).
