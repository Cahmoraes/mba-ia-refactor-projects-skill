# Phase 1 — Analysis Heuristics

Heuristics for detecting language, framework, database, and architecture in any backend project. Use these signals in order: file inventory → lockfile → entry point → routes/models.

## 1. Language detection

| Signal | Language |
|---|---|
| `*.py` files + (`requirements.txt` OR `pyproject.toml` OR `Pipfile`) | Python |
| `*.js` / `*.mjs` / `*.cjs` + `package.json` | Node.js (CommonJS or ESM — see `"type"` field) |
| `*.ts` + `tsconfig.json` | TypeScript |
| `*.go` + `go.mod` | Go |
| `*.java` + (`pom.xml` OR `build.gradle`) | Java |
| `*.rb` + (`Gemfile` OR `*.gemspec`) | Ruby |
| `*.php` + `composer.json` | PHP |
| `*.rs` + `Cargo.toml` | Rust |
| `*.cs` + `*.csproj` | C# / .NET |

When multiple match, count source files in each — the dominant language wins. Ignore generated dirs (`node_modules/`, `__pycache__/`, `.venv/`, `dist/`, `target/`, `build/`).

## 2. Framework detection (web/backend)

### Python

| Dependency in lockfile | Framework |
|---|---|
| `flask` | Flask |
| `django` | Django |
| `fastapi` | FastAPI |
| `tornado` | Tornado |
| `bottle` | Bottle |
| `aiohttp` | aiohttp |

Confirm by scanning entry points for `from flask import`, `from django...`, `from fastapi import FastAPI`, etc.

### Node.js

| Dependency | Framework |
|---|---|
| `express` | Express |
| `fastify` | Fastify |
| `koa` | Koa |
| `hapi` | Hapi |
| `nestjs` | NestJS |
| `next` | Next.js |

Confirm with `const express = require('express')` or `import express from 'express'`.

### Other ecosystems

| Signal | Framework |
|---|---|
| `gin-gonic/gin`, `gorilla/mux`, `chi`, `echo`, `fiber` | Go web frameworks |
| `spring-boot-starter-web` | Spring Boot |
| `Rails` in `Gemfile.lock` | Rails |
| `Sinatra` in `Gemfile.lock` | Sinatra |

## 3. Version detection

- **Python**: read pinned version in `requirements.txt` (`flask==3.0.0`) or `pyproject.toml`.
- **Node**: read `dependencies.express` in `package.json` (strip `^`/`~`).
- **Java**: parse `<version>` in `pom.xml`.

Always include the version in the Phase 1 summary when available.

## 4. Database / persistence detection

Look for:

- **SQLite**: `sqlite3` import, `:memory:`, `*.db` files.
- **PostgreSQL**: `psycopg2`, `pg`, `node-postgres`, env vars like `DATABASE_URL=postgres://...`.
- **MySQL**: `pymysql`, `mysql2`, `mysql-connector`.
- **MongoDB**: `pymongo`, `mongoose`.
- **Redis**: `redis`, `ioredis`.
- **ORMs**: `sqlalchemy`, `prisma`, `typeorm`, `sequelize`, `peewee`, `gorm`.

For DB tables, parse:
- `CREATE TABLE <name>` in SQL strings.
- ORM model classes (`class Foo(db.Model)` for SQLAlchemy, `model Foo {` for Prisma).

List 4-8 most relevant tables/models in the Phase 1 summary.

## 5. Architecture classification

Classify with one short sentence. Common patterns:

| Signal | Classification |
|---|---|
| 1-3 source files, all logic in entry point | Monolithic single-file |
| Routes, models, controllers all in one file | Monolithic flat |
| Has `models/` and `routes/` but no `controllers/` or `services/` | Partially layered |
| Has `models/`, `controllers/`, `routes/`, `services/`, `config/` | Layered / MVC-ish |
| Has `domain/`, `application/`, `infrastructure/` | DDD / Hexagonal |
| Single God class doing routing + DB + business logic | God class anti-pattern |

The phrase to use in Phase 1 should mention the file count and the level of separation:

> "Monolítica — tudo em 4 arquivos, sem separação de camadas"
>
> "Parcialmente organizada — models e routes separados, mas regras de negócio dentro das routes"
>
> "God class — toda lógica em src/AppManager.js"

## 6. Domain inference

Read route paths and table names to infer the domain in one short sentence:

- `/products`, `/orders`, `/users` + `produtos`, `pedidos`, `usuarios` → "E-commerce API"
- `/tasks`, `/users`, `/categories` → "Task Manager API"
- `/courses`, `/enrollments`, `/payments` → "LMS / online course platform"
- `/posts`, `/comments`, `/likes` → "Social network / blog"

Always include 2-4 main entities to anchor the description: "E-commerce API (produtos, pedidos, usuários)".

## 7. File inventory rules

When counting "source files analyzed", **include**:
- Application code (`*.py`, `*.js`, `*.ts`, etc.)
- Configuration that holds logic (entry points, `app.py`, `index.js`)

**Exclude**:
- `node_modules/`, `__pycache__/`, `.venv/`, `venv/`, `dist/`, `build/`, `target/`
- Tests directories (`tests/`, `__tests__/`) — count them separately if relevant
- Migration auto-generated files
- Lock files (`package-lock.json`, `poetry.lock`)
- The skill itself (`.claude/`)

When in doubt: count only files in which a developer writes business logic.
