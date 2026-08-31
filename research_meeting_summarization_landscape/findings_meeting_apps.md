# Open-source помощники для встреч

Проверено: 2026-08-31. Использованы только официальные репозитории, README, документация, релизы и GitHub API репозиториев. Возможность, которую первичный источник не описывает, отмечена как неподтверждённая.

## Meetily

- [Репозиторий](https://github.com/Zackriya-Solutions/meetily), MIT; последний релиз — [v0.4.0 от 2026-06-05](https://github.com/Zackriya-Solutions/meetily/releases/tag/v0.4.0).
- Desktop-first помощник для macOS и Windows (Linux — сборка из исходников): захват встречи, локальная realtime-транскрибация Whisper или Parakeet, локальное хранение записи и транскрипта.
- Для саммари README перечисляет Ollama, Claude, Groq, OpenRouter, OpenAI и произвольный OpenAI-compatible endpoint.
- UX-паттерны: onboarding/model manager, realtime transcript, history, импорт существующего аудио и повторная транскрибация другой моделью/языком.
- Ограничения относительно исследуемого сценария: импорт видео не заявлен; README Community Edition противоречиво описывает diarization (она присутствует в заголовке, но speaker identification одновременно отнесён к PRO/coming soon); custom summary templates и advanced exports перечислены как PRO. Это требует проверки конкретной редакции, а не переноса рекламного заголовка в требования.

## zabt.ai

- [Репозиторий](https://github.com/afeef/zabt-ai), AGPL-3.0; на дату проверки тегированных релизов нет, последний push по GitHub API — 2026-08-12.
- Self-hosted web-система: audio/video upload, faster-whisper, pyannote diarization, timestamped speaker transcript, редактирование, шаблоны саммари и PDF export.
- LLM-слой принимает любой OpenAI-compatible endpoint; README прямо перечисляет OpenRouter, Ollama, vLLM, LM Studio и OpenAI.
- Локальный стек включает Next.js/FastAPI, Postgres, Redis/Celery и MinIO/S3; web UI показывает библиотеку и результаты. Поддержаны CPU-only и GPU worker, но CPU описан как медленный.
- Риски/границы: для diarization нужен Hugging Face token и принятие условий gated pyannote-моделей; quick start требует Supabase-параметры для auth; default large-v3 оценивается в 10–12 GB VRAM плюс 2–4 GB для diarization. Система молода и не имеет стабильного релиза.

## vts

- [Репозиторий](https://github.com/gorynychzmey/vts), MIT; последний опубликованный build — [build-1.7.85 от 2026-08-31](https://github.com/gorynychzmey/vts/releases/tag/build-1.7.85).
- Self-hosted web/PWA для загрузки видео или аудио, URL и mobile share; pipeline скачивает/сегментирует, транскрибирует Whisper, опционально диаризует, суммаризирует локальным LLM и индексирует в Postgres + pgvector.
- LLM запускается через llama.cpp или Ollama; документация также описывает OpenAI-compatible proxy (например LiteLLM). Это не позиционируется как универсальный облачный provider picker в UI.
- UX-паттерны: SSE-прогресс, restart-safe worker, library записей, custom prompts, presets, уведомления, полнотекстовый/семантический поиск, переход к точной секунде и speaker/timecode provenance.
- Ограничения: автор прямо называет проект личным и говорит, что внутренний API не формально версионирован; production auth использует Google OAuth, хотя локальный dev mode может работать без него; публичная зрелость/поддержка пока ограничены.

## Amurex

- [Репозиторий](https://github.com/thepersonalaicompany/amurex), AGPL-3.0; последний релиз — [v1.0.27 от 2025-03-21](https://github.com/thepersonalaicompany/amurex/releases/tag/v1.0.27), последний push по GitHub API — 2025-05-27.
- Browser extension/coprocessor для Google Meet и Microsoft Teams: live transcript, подсказки в ходе звонка, summary/key takeaways, late-join recap и follow-up email.
- Self-hosting предусмотрен через отдельные backend/web endpoints. Пример конфигурации включает переключатель analytics, включённый по умолчанию.
- Главный README не описывает загрузку готового видео, конкретный ASR backend, OpenAI-compatible provider contract или полностью offline режим. Поэтому Amurex полезен как контрастный live-meeting workflow, но не как прямой аналог upload-first локального приложения.

## Сигналы

1. Meeting-first проекты чаще оптимизированы под live capture, тогда как надёжный video upload чаще встречается в transcription-first инструментах.
2. OpenAI-compatible почти всегда документирован для LLM-саммари; заменяемый OpenAI-compatible ASR endpoint остаётся редкостью.
3. Повторяются progress/queue, transcript-player synchronization, speaker correction, custom prompts/templates, history/library и source timecodes.
4. «Local/private» требует стадийного определения: локальная запись и ASR не гарантируют локальность саммари при выборе облачного LLM, а auth/telemetry/model downloads могут создавать отдельные внешние связи.
5. Model lifecycle, gated downloads, VRAM/RAM/disk и безопасное восстановление долгой задачи оказываются частью продуктового опыта, а не только технической реализации.
