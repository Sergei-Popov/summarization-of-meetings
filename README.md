# Meeting App

Воспроизводимый локальный каркас приложения для транскрибации и суммаризации встреч.
Baseline не загружает модели, не использует CDN, telemetry или внешние assets и публикует HTTP
только на loopback-интерфейсе хоста.

## Запуск

Нужны Docker Engine/Desktop и Docker Compose 5.4.0. Поддерживаются Linux, macOS и Windows.

```sh
cp .env.example .env
docker compose up --build --wait
```

После успешного preflight:

- UI: `http://127.0.0.1:8000/`
- health: `http://127.0.0.1:8000/api/v1/health`
- OpenAPI: `http://127.0.0.1:8000/api/v1/openapi.json`

Проверка из терминала:

```sh
curl --fail http://127.0.0.1:8000/api/v1/health
```

До завершения startup контейнер остаётся `unhealthy`. Preflight создаёт временную SQLite БД
на том же named volume, проверяет точную SQLite 3.53.4, реальную FTS5-таблицу и WAL, удаляет
probe и только после этого запускает Alembic для product DB. NFS, SMB/CIFS и SSHFS завершают
startup с безопасным кодом `storage.filesystem_unsupported`; автоматического fallback нет.

Остановка:

```sh
docker compose down
```

Данные остаются в named volume `meeting-app_meeting-data`. Для полного удаления локальных
данных явно выполните `docker compose down --volumes`; операция необратима.

## Каталоги

- `backend/src/meeting_app/modules` — domain/application/ports продуктовых модулей.
- `backend/src/meeting_app/platform` — технические адаптеры, включая SQLite preflight.
- `backend/src/meeting_app/entrypoints` — HTTP API `/api/v1`.
- `backend/src/meeting_app/bootstrap` — composition root и startup order.
- `backend/migrations` — Alembic migrations, выполняемые только после preflight.
- `frontend/src` — React/Ant Design UI; DTO генерируются из `openapi/openapi.json`.
- `deploy/release` — manifest, checksums, licenses и SPDX inventory.

## Резервная копия, восстановление и обновление

Для согласованной offline-копии остановите сервис и скопируйте основную БД через Compose. Этот
workflow не использует непереносимый mountpoint named volume и работает через Docker Desktop:

```sh
docker compose stop app
docker compose cp app:/var/lib/meeting-app/meeting-app.sqlite3 ./meeting-app-backup.sqlite3
```

Для восстановления оставьте существующий контейнер остановленным, скопируйте проверенный backup
обратно и восстановите владельца файла внутри named volume:

```sh
docker compose stop app
docker compose cp ./meeting-app-backup.sqlite3 app:/var/lib/meeting-app/meeting-app.sqlite3
docker compose run --rm --no-deps --user 0 --cap-add CHOWN --entrypoint chown app \
  10001:10001 /var/lib/meeting-app/meeting-app.sqlite3
docker compose up --wait
```

Startup повторно проверит volume до миграций. Перед обновлением сохраните backup, задайте
digest-ready reference в `MEETING_APP_IMAGE` (`registry/name@sha256:<digest>`), затем выполните
`docker compose pull` и `docker compose up --wait`. Откат требует совместимой БД или
восстановления backup.

## Локальные gates

Точные версии Python/Node и зависимости закреплены в `.python-version`, `uv.lock`,
`package.json` и `pnpm-lock.yaml`. Exact Python 3.13.15 backend/release gate выполняется внутри
pinned Docker base и не зависит от способности локального `uv` скачать этот interpreter:

```sh
docker build --target backend-verify --file deploy/app.Dockerfile .
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend test
pnpm --dir frontend build
test "$(docker compose version --short)" = "5.4.0"
docker compose config
```

Уже подготовленное host-окружение можно использовать как быстрый дополнительный путь для
pytest/Ruff/mypy и генерации inventory, но оно не считается доказательством exact Python;
канонический exact gate — Docker target `backend-verify` выше.

OpenAPI экспортируется без lifespan и сетевых вызовов:

```sh
uv run --project backend --frozen python backend/scripts/export_openapi.py
```

Проект распространяется по Apache License 2.0; см. `LICENSE`, `NOTICE` и release inventory.
