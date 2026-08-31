# Ландшафт open-source/local-first приложений для транскрибации и суммаризации встреч

**Дата проверки:** 2026-08-31  
**Контекст:** локальное однопользовательское web-приложение, в которое загружается видеозапись встречи; транскрибация и суммаризация могут выполняться локально либо через настраиваемого OpenAI-compatible провайдера; данные хранятся локально; репозиторий публичный.

## Метод и оговорки

Исследование основано только на первичных источниках: официальных репозиториях, README/документации, release notes и метаданных GitHub. Это desk research, а не установка и сравнительный прогон на одинаковых записях. Поэтому заявления о приватности, скорости и качестве ниже являются заявлениями авторов; неподтверждённые возможности помечены как «не документировано», а не как доказанно отсутствующие.

## Краткий вывод

Рынок разделён на три типа продуктов:

1. **Desktop meeting assistants** захватывают встречу в реальном времени и дают transcript/summary, но часто не имеют upload-first web workflow или документированной локальной БД.
2. **Self-hosted transcription portals** ближе всего к целевому сценарию: video/audio upload, очередь, история, diarization, локальные модели и LLM-постобработка. Их цена — сложная установка и управление ML-моделями.
3. **Offline transcription utilities** сильнее в достоверности транскрипта, синхронном playback/editing и экспорте, но часто не имеют meeting-specific summary workflow или настраиваемых внешних провайдеров.

Наиболее близкий прямой comparable — **Scriberr**: self-hosted web/PWA, video/audio upload, SQLite и локальные файлы, diarization, summary/chat, Ollama и OpenAI-compatible LLM. Однако произвольный OpenAI-compatible **ASR** endpoint у него не подтверждён, а разработка временно приостановлена. **zabt.ai**, **vts** и **TranscrIA** показывают более полные web-pipeline и operational UX, но являются молодыми либо существенно более тяжёлыми системами. **Meetily**, **Vibe**, **noScribe** и **Amurex** полезны как смежные ориентиры для live capture, offline transcription и human review.

Главный незакрытый рыночный стык: единый простой локальный web-продукт, где **транскрибация и суммаризация имеют независимые, явно настроенные local/OpenAI-compatible контракты**, а интерфейс честно показывает, какие данные и на каком шаге могут покинуть устройство.

## Сравнение проектов

| Проект | Позиционирование и актуальность | Ввод и транскрибация | Суммаризация / модели | Хранение и заметный UX | Явный пробел относительно целевого сценария |
|---|---|---|---|---|---|
| [Meetily](https://github.com/Zackriya-Solutions/meetily) | MIT, privacy-first desktop meeting assistant; [v0.4.0, 2026-06-05](https://github.com/Zackriya-Solutions/meetily/releases/tag/v0.4.0) | Live capture; локальные Whisper/Parakeet; beta-import существующего **аудио** и re-transcribe | Ollama, Claude, Groq, OpenRouter, OpenAI и custom OpenAI-compatible endpoint | Локальные записи/транскрипты, realtime transcript, history, model manager | Video import не документирован; diarization и часть exports/templates противоречиво отнесены к PRO/coming soon |
| [Scriberr](https://github.com/rishikanthc/Scriberr) | MIT, self-hosted web/PWA; [v1.2.0, 2025-12-17](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0); README сообщает о временной паузе разработки | Video/audio upload, drag-and-drop, folder watcher, recorder/API/CLI; локальные Whisper, Parakeet, Canary; diarization и word timestamps | Summary templates и chat; Ollama и OpenAI-compatible LLM; OpenAI transcription заявлен отдельно | SQLite + uploads/transcripts; queue/status, synced transcript player, seek, speaker rename, notes/highlights | Произвольный OpenAI-compatible ASR base URL не подтверждён; ML-runtime требует отдельной миграции/инициализации |
| [Vibe](https://github.com/thewh1teagle/vibe) | MIT, локальное desktop-приложение; [v3.1.6, 2026-08-28](https://github.com/thewh1teagle/vibe/releases/tag/v3.1.6) | Audio/video, batch, web URLs, mic/system audio; Whisper, Nemotron 3.5, Parakeet TDT v3; diarization | Claude API или локальный Ollama | Realtime preview, SRT/VTT/TXT/HTML/PDF/JSON/DOCX, CLI и HTTP API | Не web-library; долговременная БД и общий OpenAI-compatible provider не документированы; cloud summary размывает offline claim |
| [noScribe](https://github.com/kaixxx/noScribe) | GPL-3.0, strict-offline desktop transcription для чувствительных записей; [v0.7.2, 2026-06-02](https://github.com/kaixxx/noScribe/releases/tag/v0.7.2) | Почти любые audio/video; local faster-whisper/Whisper V3 Turbo, Pyannote, batch и headless CLI | LLM-суммаризация и LLM-провайдеры не заявлены | Progress/cancel/restart, открытие частичного результата, synced editor, speaker correction, HTML/TXT/WebVTT | Нет web UI, summary и provider abstraction; авторы прямо требуют ручной проверки ошибок ASR/diarization |
| [zabt.ai](https://github.com/afeef/zabt-ai) | AGPL-3.0, self-hosted meeting intelligence; на дату проверки тегированных релизов нет | Audio/video upload, faster-whisper, pyannote diarization, timestamps; CPU/GPU worker | Любой OpenAI-compatible LLM: Ollama, vLLM, LM Studio, OpenRouter, OpenAI; summary templates | Postgres, Redis/Celery, MinIO/S3, Next.js UI; transcript editor, PDF, notifications | Молодой проект; сложный стек; pyannote требует HF token/acceptance; quick start включает Supabase auth; CPU медленный |
| [vts](https://github.com/gorynychzmey/vts) | MIT, self-hosted video/audio knowledge base; автор называет его working personal project; [build-1.7.85, 2026-08-31](https://github.com/gorynychzmey/vts/releases/tag/build-1.7.85) | File/URL/mobile share, Whisper, optional diarization и persistent speaker registry | Локальные llama.cpp/Ollama; возможен OpenAI-compatible proxy; custom prompts/presets | Postgres + pgvector, library, SSE progress, restart-safe worker, search, notifications, ссылки на timecode | Внутренний API не формально версионирован; production auth завязан на Google OAuth; generic provider picker в UI не заявлен |
| [TranscrIA](https://github.com/Martossien/transcria) | Apache-2.0, production-oriented self-hosted meeting portal; [v0.4.5, 2026-08-26](https://github.com/Martossien/transcria/releases/tag/v0.4.5) | Upload → audio preflight → interchangeable local/remote STT; Whisper/faster-whisper, Voxtral, Parakeet, MOSS, Kroko и др.; remote OpenAI-compatible serving; pyannote/Sortformer | Локальный OpenAI-compatible LLM через Ollama/llama.cpp/vLLM; structured summaries, correction/review, editable prompts | PostgreSQL production / SQLite dev; persistent queue, transcript editor, versioning, quality reports, DOCX/SRT/ZIP, backup/retention | Значительно тяжелее solo-MVP; reference setup ориентирован на Linux/NVIDIA; default upload limit 1 GB; часть языков beta; меньше 8 GB VRAM — без LLM summary |
| [Amurex](https://github.com/thepersonalaicompany/amurex) | AGPL-3.0 browser meeting copilot; [v1.0.27, 2025-03-21](https://github.com/thepersonalaicompany/amurex/releases/tag/v1.0.27); последний push — 2025-05-27 | Live transcript в Google Meet/MS Teams; готовый video upload и конкретный ASR backend не документированы | Live suggestions, summary, takeaways, late-join recap, follow-up email; provider contract в главном README не описан | Extension + self-hosted backend/web endpoints | Не upload-first и не offline; главный репозиторий не подтверждает local/OpenAI-compatible models; пример self-host config включает analytics=true |

## Подробные наблюдения

### 1. Граница «локальности» должна быть видна по стадиям

У большинства проектов локальная ASR сочетается с необязательным облачным LLM. [Vibe](https://github.com/thewh1teagle/vibe#features-) одновременно заявляет полностью offline transcription и саммари через Claude API; [Meetily](https://github.com/Zackriya-Solutions/meetily#features) и [Scriberr](https://github.com/rishikanthc/Scriberr#introduction) предлагают и local Ollama, и внешних провайдеров. Следовательно, общий ярлык «local/private» недостаточен: отдельно существуют исходное медиа, извлечённое аудио, транскрипт, summary prompt, API key, telemetry и model downloads.

### 2. OpenAI-compatible LLM и OpenAI-compatible ASR — разные контракты

Поддержка custom base URL почти везде относится к chat/completions для саммари. [Scriberr](https://github.com/rishikanthc/Scriberr) отдельно заявляет OpenAI transcription, но не подтверждает одинаково свободный custom ASR base URL. [TranscrIA](https://github.com/Martossien/transcria#how-it-works), напротив, документирует заменяемые STT backends и remote OpenAI-compatible serving, но его решение рассчитано на тяжёлый портал. Для PRD это две независимые области требований: провайдер транскрибации и провайдер анализа/суммаризации.

### 3. Длинная обработка формирует отдельный UX

Self-hosted проекты показывают повторяющийся workflow: upload → persistent job → очередь/прогресс → промежуточные стадии → retry/restart → результат. [vts](https://github.com/gorynychzmey/vts) делает worker restart-safe и показывает SSE progress; [TranscrIA](https://github.com/Martossien/transcria#what-it-does) сохраняет checkpoint/queue state; [noScribe](https://noscribe.de/en/docs/usage/) позволяет отменить, повторить и открыть частичный результат. На локальном CPU час записи может обрабатываться дольше часа, поэтому «приложение отвечает» и «задача завершена» — разные состояния.

### 4. Проверяемость результата важнее чистой генерации

Сильный повторяющийся паттерн — transcript рядом с проигрывателем, timestamps, click-to-seek, переименование спикеров и ручное исправление. Это есть у [Scriberr](https://github.com/rishikanthc/Scriberr#screenshots), [noScribe](https://noscribe.de/en/docs/usage/), [zabt.ai](https://github.com/afeef/zabt-ai#features), [vts](https://github.com/gorynychzmey/vts) и [TranscrIA](https://github.com/Martossien/transcria#what-it-does). vts дополнительно связывает найденный passage с точной секундой записи. Это ответ рынка на ожидаемые ошибки ASR, diarization и LLM, а не второстепенный editor feature.

### 5. Speaker diarization почти всегда требует human-in-the-loop

Pyannote широко используется, но часто требует отдельный Hugging Face token и принятие gated model terms. Автоматические speaker labels не равны реальным именам; проекты добавляют rename/reassign, аудиофрагменты для проверки и persistent voice registry. [noScribe](https://noscribe.de/en/docs/usage/#typical-issues-with-ai-assisted-transcription) отдельно предупреждает об ошибках назначения говорящих и потере содержания при overlap.

### 6. Локальные модели создают lifecycle внутри продукта

На практике требуются выбор ASR/LLM-моделей, скачивание нескольких гигабайт, контроль свободного диска, CPU/GPU fallback, VRAM admission и понятное первое включение. [zabt.ai](https://github.com/afeef/zabt-ai#hardware-requirements) оценивает Whisper large-v3 в 10–12 GB VRAM плюс 2–4 GB для diarization; [TranscrIA](https://github.com/Martossien/transcria#known-limitations) документирует аппаратные пороги и деградацию без LLM; [Scriberr](https://github.com/rishikanthc/Scriberr#migrating-from-v110) показывает, что обновление model runtime может требовать миграции persistent volumes.

### 7. «История встреч» бывает файловой, библиотечной и knowledge-base

Vibe/noScribe в первую очередь производят и редактируют файлы. Scriberr хранит `scriberr.db`, uploads и transcripts. zabt.ai разделяет Postgres и object storage. vts превращает архив в полнотекстовую/семантическую базу с provenance. Для PRD нельзя считать «локальная БД» достаточным ответом: отдельно нужны правила хранения исходного видео, производного аудио, transcript versions, summaries, task logs и индексов.

### 8. Публичная open-source поставка усиливает требования к установке и безопасности

Comparables варьируются от desktop installer до многоконтейнерного Docker-стека. Документированные проблемы включают unsigned binaries, default credentials/example secrets, secure cookies/HTTPS, внешнюю auth-зависимость, gated models и лицензионные различия MIT/GPL/AGPL. Даже для single-user localhost продукта публичный репозиторий делает first-run, secrets storage, network binding, upgrade/migration и backup частью качества продукта.

## Повторяющиеся UX/workflow-паттерны

- Drag-and-drop/file picker, иногда folder watcher и batch upload.
- Карточка задачи с очередью, стадией, процентом/оценкой времени, cancel/retry и восстановлением после restart.
- Transcript reader, синхронизированный с аудио/видео, с переходом по timestamp.
- Diarization с временными `Speaker 1/2`, rename/reassign и проверкой по аудиофрагменту.
- Отдельные результаты: transcript, краткое summary, key points, decisions и action items; иногда chat по transcript.
- Custom prompts/templates и повторная генерация без повторной транскрибации.
- Экспорт Markdown/TXT/SRT/VTT/PDF/DOCX/JSON и копирование отдельных блоков.
- Library/history, поиск и явное удаление; у более развитых систем — versioning и source provenance.
- Settings/model manager с test connection, model selection, download/progress и hardware diagnostics.

## Явные пробелы ландшафта

1. **Единый provider UX для двух AI-стадий.** Настраиваемый OpenAI-compatible LLM распространён; столь же ясный contract для remote/local transcription встречается редко.
2. **Простой solo-local web package.** Наиболее полные web-порталы тянут Postgres/Redis/object storage/auth/GPU orchestration; простые desktop tools не дают браузерную библиотеку.
3. **Честная privacy-модель гибридного режима.** Маркетинговое «offline/local» часто соседствует с Claude/OpenAI/OpenRouter или внешней auth/telemetry.
4. **Проверяемое meeting summary.** Generic summary/chat распространены, но сквозная связь «решение/action item → speaker/timecode → исходный фрагмент» документирована редко.
5. **Video-first поддержка в meeting assistants.** Live capture и audio import распространены; готовый video upload чаще встречается в transcription-first продуктах.
6. **Предсказуемая работа на обычном CPU.** Local AI возможен, но latency, размер моделей и качество малых LLM часто делают его существенно менее бесшовным, чем обещает позиционирование.
7. **Сопровождение публичного hobby-проекта.** Несколько ближайших аналогов не имеют стабильных релизов, временно paused или прямо называются personal/hobby projects.

## Вопросы и риски, которые нужно закрыть в PRD

1. **Два provider contracts:** какие именно OpenAI-compatible endpoints поддерживаются для ASR и для LLM; можно ли настроить разные base URL/key/model; какие capability/connection tests обязательны?
2. **Privacy boundary:** что остаётся локально в каждом режиме, что отправляется провайдеру, какой экран предупреждает об этом и хранятся ли API keys безопасно?
3. **Форматы и пределы input:** какие video/audio containers/codecs, максимальный размер/длительность, batch upload, повреждённые файлы и extraction failure входят в MVP?
4. **Долгие задания:** нужны ли очередь, progress by stage, cancel/retry, resume after restart и повторный запуск только одной стадии без потери предыдущего результата?
5. **Аппаратный baseline:** на каких OS/CPU/GPU/RAM/disk должна работать локальная ASR и локальная LLM; допустимое время обработки часа видео; кто управляет загрузкой/обновлением моделей?
6. **Diarization и проверка:** обязательны ли speaker separation, ручное rename/reassign, mixed/overlapping speech и связь transcript/summary с timestamp исходной записи?
7. **Локальное хранение:** что хранится и как долго — исходное видео, извлечённое аудио, transcript, versions, summaries, task logs, model cache; нужны ли backup/export и каскадное удаление?
8. **Публичная поставка и безопасность:** Docker или installer, localhost-only default, нужна ли auth, как защищаются secrets, как выполняются migrations/upgrades и какая open-source license подходит проекту?

## Источники

- Meetily: [README](https://github.com/Zackriya-Solutions/meetily), [v0.4.0](https://github.com/Zackriya-Solutions/meetily/releases/tag/v0.4.0).
- Scriberr: [README](https://github.com/rishikanthc/Scriberr), [v1.2.0](https://github.com/rishikanthc/Scriberr/releases/tag/v1.2.0).
- Vibe: [README](https://github.com/thewh1teagle/vibe), [v3.1.6](https://github.com/thewh1teagle/vibe/releases/tag/v3.1.6).
- noScribe: [официальный сайт](https://noscribe.de/en/), [usage guide](https://noscribe.de/en/docs/usage/), [FAQ/privacy](https://noscribe.de/en/docs/faq/), [репозиторий](https://github.com/kaixxx/noScribe), [v0.7.2](https://github.com/kaixxx/noScribe/releases/tag/v0.7.2).
- zabt.ai: [README и self-host docs](https://github.com/afeef/zabt-ai).
- vts: [README](https://github.com/gorynychzmey/vts), [build-1.7.85](https://github.com/gorynychzmey/vts/releases/tag/build-1.7.85).
- TranscrIA: [README/docs](https://github.com/Martossien/transcria), [v0.4.5](https://github.com/Martossien/transcria/releases/tag/v0.4.5).
- Amurex: [README](https://github.com/thepersonalaicompany/amurex), [v1.0.27](https://github.com/thepersonalaicompany/amurex/releases/tag/v1.0.27), [официальная Chrome Web Store listing](https://chromewebstore.google.com/detail/amurex-early-preview/dckidmhhpnfhachdpobgfbjnhfnmddmc).

## Ограничения исследования

- Не проводилось hands-on тестирование установки, качества русского/mixed-language ASR, diarization и summary accuracy.
- Не проверялись security posture, telemetry на уровне сетевого трафика и полнота удаления данных.
- README может опережать или отставать от Community/Pro-кода; особенно это заметно у Meetily.
- GitHub activity и версии отражают состояние на дату проверки и могут измениться.
