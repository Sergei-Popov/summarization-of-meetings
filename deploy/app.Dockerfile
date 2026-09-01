# syntax=docker/dockerfile:1.8

ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e
ARG NODE_IMAGE=node:24.20.0-bookworm-slim@sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e

FROM ${NODE_IMAGE} AS frontend-build
WORKDIR /build/frontend
RUN corepack enable && corepack prepare pnpm@11.1.3 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
COPY openapi/ /build/openapi/
RUN pnpm build

FROM ${PYTHON_IMAGE} AS sqlite-build
ARG SQLITE_VERSION=3.53.4
ARG SQLITE_AUTOCONF=3530400
ARG SQLITE_SHA256=0e9483900e92cd5de8fd48d16bf9200145a61f7fd5be542a5ac81d8a9516eb9c
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential ca-certificates curl \
    && curl --fail --show-error --location \
       "https://www.sqlite.org/2026/sqlite-autoconf-${SQLITE_AUTOCONF}.tar.gz" \
       --output /tmp/sqlite.tar.gz \
    && echo "${SQLITE_SHA256}  /tmp/sqlite.tar.gz" | sha256sum --check --strict \
    && mkdir /tmp/sqlite-src \
    && tar --extract --gzip --file /tmp/sqlite.tar.gz --directory /tmp/sqlite-src --strip-components=1 \
    && cd /tmp/sqlite-src \
    && CFLAGS="-O2 -DSQLITE_ENABLE_FTS5" ./configure --disable-static --disable-readline \
    && make --jobs="$(nproc)" \
    && make install \
    && test "$(/usr/local/bin/sqlite3 --version | cut -d' ' -f1)" = "${SQLITE_VERSION}"

FROM ${PYTHON_IMAGE} AS backend-build
WORKDIR /app/backend
RUN python -m pip install --no-cache-dir uv==0.11.21
COPY README.md /app/README.md
COPY backend/pyproject.toml backend/uv.lock backend/alembic.ini ./
COPY backend/src/ ./src/
COPY backend/migrations/ ./migrations/
RUN uv sync --frozen --no-dev

FROM ${PYTHON_IMAGE} AS backend-verify
ENV LD_LIBRARY_PATH="/usr/local/lib" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"
WORKDIR /workspace
COPY --from=sqlite-build /usr/local/lib/libsqlite3.so* /usr/local/lib/
RUN ldconfig \
    && python -m pip install --no-cache-dir uv==0.11.21 \
    && python -c "import sys; assert sys.version_info[:3] == (3, 13, 15)" \
    && python -c "import sqlite3; assert sqlite3.sqlite_version == '3.53.4'"
COPY README.md LICENSE NOTICE .env.example .gitignore .dockerignore compose.yaml ruff.toml .python-version ./
COPY .github/ ./.github/
COPY backend/pyproject.toml backend/uv.lock backend/alembic.ini ./backend/
COPY backend/migrations/ ./backend/migrations/
COPY backend/src/ ./backend/src/
COPY backend/scripts/ ./backend/scripts/
RUN uv sync --project backend --frozen
COPY backend/tests/ ./backend/tests/
COPY tests/release/ ./tests/release/
COPY deploy/ ./deploy/
COPY openapi/ ./openapi/
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY --from=frontend-build /build/frontend/src/api/generated/schema.ts ./frontend/src/api/generated/schema.ts
COPY _bmad-output/implementation-artifacts/spec-1-1-zapusk-lokalnogo-prilozheniya-iz-vosproizvodimogo-karkasa.md ./_bmad-output/implementation-artifacts/
RUN uv run --project backend --frozen pytest \
        -c backend/pyproject.toml backend/tests tests/release \
    && uv run --project backend --frozen ruff check --config ruff.toml . \
    && uv run --project backend --frozen mypy \
        --config-file backend/pyproject.toml backend/src

FROM ${PYTHON_IMAGE} AS runtime
LABEL org.opencontainers.image.title="Meeting App" \
      org.opencontainers.image.licenses="Apache-2.0"
ENV PATH="/app/backend/.venv/bin:${PATH}" \
    LD_LIBRARY_PATH="/usr/local/lib" \
    MEETING_APP_DATA_DIR="/var/lib/meeting-app" \
    MEETING_APP_STATIC_DIR="/app/backend/static" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"
WORKDIR /app/backend
COPY --from=sqlite-build /usr/local/lib/libsqlite3.so* /usr/local/lib/
COPY --from=sqlite-build /usr/local/bin/sqlite3 /usr/local/bin/sqlite3
COPY --from=backend-build /app/backend/.venv ./.venv
COPY --from=backend-build /app/backend/src ./src
COPY --from=backend-build /app/backend/migrations ./migrations
COPY --from=backend-build /app/backend/alembic.ini ./alembic.ini
COPY --from=frontend-build /build/frontend/dist ./static
RUN ldconfig \
    && groupadd --system --gid 10001 meeting-app \
    && useradd --system --uid 10001 --gid meeting-app --home-dir /nonexistent meeting-app \
    && mkdir --parents /var/lib/meeting-app \
    && chown meeting-app:meeting-app /var/lib/meeting-app \
    && sqlite3 ':memory:' "SELECT CASE sqlite_version() WHEN '3.53.4' THEN 1 ELSE load_extension('invalid') END;"
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "meeting_app.bootstrap.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
