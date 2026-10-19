# necktie

Technical assessment for doctor search in Python.

## Domain assumptions

Hong Kong–specific rules that shape the data model and API:

- **Hong Kong only.** Phone numbers are validated against the HK region, and only on create — reads return whatever is stored.
- **One row per clinic.** A doctor with multiple clinics is stored as one
  row per clinic (name clashes make deduplication unreliable), so there is no
  separate clinic table.
- **Public holidays are all-or-nothing.** HK clinics either open or close on
  public holidays as a whole, regardless of which weekday a holiday falls on —
  so `is_open_on_public_holidays` is a single flag, not per-day.
- **`place_id` is the Google Places ID** for a clinic, used for navigation.
- **Day of week follows ISO 8601** (1 = Monday, 7 = Sunday) in `operating_hours`.

## Framework and library choices

- **FastAPI** — typed JSON API: validation + OpenAPI docs come free from type
  annotations; async is first-class. Drawback: DI is implicit (resolved from
  signatures), and async forces care around blocking calls (we offload DB work
  via `run_in_threadpool`). Assumes read-heavy, JSON-only — a full-stack
  framework (Django) would be overhead.
- **SQLModel + SQLAlchemy** — ORM models double as Pydantic-typed tables, so the
  schema/ORM boundary stays typed. Drawback: type stubs fight mypy strict mode
  (we scope mypy overrides to repositories/mappers).
- **Pydantic** — the validation layer FastAPI builds on. We use its conventions:
  `Annotated[..., AfterValidator]`, built-in `Field` constraints over custom
  validators, per-domain input models. Kept to the schema layer (it's for
  untrusted boundary data, not internal domain objects).
- **Jetbase** — plain-SQL file-per-migration; no ORM autogeneration, so the
  schema is a readable spec. Drawback: a thin CLI with no startup hook (unlike
  Liquibase) — in production it runs as a deploy step.
- **Postgres + Redis** — Postgres for the relational model; Redis for the
  response cache and the lazily-loaded reference-data catalogs.

## Potential improvements

In rough priority order:

- **Async DB driver** — drop `run_in_threadpool` by using `sqlalchemy[asyncio]`.
- **Idempotency on create** — `POST /doctor[/batch]` are not idempotent; an
  `Idempotency-Key` header (claim in Redis, replay the stored response) would
  make retries safe.
- **PUT/PATCH** — no way to update a doctor yet.
- **Real Mandarin content** — `*_zh` is seeded as a copy of the Cantonese text.
- **Observability** — no logging/metrics/tracing; FastAPI's OpenTelemetry would
  be the addition.
- **Search** — filtering is exact-match; name search would need full-text
  indexes (e.g. Elasticsearch).

## Production considerations

- **Secrets** — `.env` is local-only; production uses a secrets manager.
- **Migrations as a deploy step** — run `jetbase upgrade` before rollout
  (initContainer / migration job), not in the app, so replicas don't race.
- **Cache invalidation** — catalogs + response cache share a TTL; seed changes
  take effect on expiry, so runtime reference-data edits need a cache clear.
- **Connection management** — per-process engine/Redis; pool sizing needs to be
  deliberate behind multiple ASGI workers.
- **Boundary validation** — schema constraints return 422, never a 500 from the
  DB; that contract should hold as the schema evolves.

## Project structure

```
├── pyproject.toml              # Package metadata and tool config
├── Dockerfile                  # App image (multi-stage, Alpine)
├── docker-compose.yml          # Infra only: Postgres + Redis
├── docker-compose.local.yml    # Adds the app service (merge with -f)
├── .github/workflows/ci.yaml   # CI pipeline
├── scripts/                    # local.sh, build.sh, verify.sh
├── src/
│   └── necktie/                # Package source
│       ├── main.py             # App entry point
│       ├── cache/              # Redis cache (lifespan, catalogs, client)
│       ├── db/                 # Engine/session
│       ├── mappers/            # ORM → schema serialization
│       ├── models/             # SQLModel ORM entities
│       ├── repositories/       # SQL data access
│       ├── routers/            # FastAPI endpoints + DI
│       ├── schemas/            # Pydantic API models
│       ├── services/           # Business logic
│       └── utils/              # Enums, validators, constants
├── jetbase/                    # SQL migrations
└── tests/                      # Test suite
```

## Run and build

There are three ways to run the app, depending on what you're doing.

### 1. Local development (deps in Docker, app on host)

Fastest for iterative coding — the app runs in your venv with `--reload`,
Postgres and Redis run in Docker:

```bash
# one-time setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# every session
docker compose up -d                                   # postgres + redis
(cd jetbase && ../.venv/bin/jetbase upgrade)           # apply migrations
.venv/bin/uvicorn necktie.main:app --reload            # app on :8000
```

Docs at http://localhost:8000/docs.

### 2. Full stack in Docker (test the real image)

Builds and runs the exact artifact CI produces:

```bash
./scripts/local.sh
# or explicitly:
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build -d
```

App on `http://localhost:${APP_PORT:-8000}`. Tear down with
`docker compose -f docker-compose.yml -f docker-compose.local.yml down`.

To run a pre-built GHCR image instead of building from source:

```bash
DOCKER_IMAGE=ghcr.io/gnumilanix/necktie:latest \
  docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

### 3. Tests and verification

```bash
# tests (needs deps running)
docker compose up -d
.venv/bin/pytest

# full local CI: lint + type-check + security scan + tests + Docker build
./scripts/verify.sh
```

### Scripts

| Script | What it does |
|---|---|
| `scripts/local.sh` | Build and run the full stack in Docker |
| `scripts/build.sh` | Build the Docker image (`necktie:local` or a tag arg) |
| `scripts/verify.sh` | Lint + mypy + bandit + pytest + Docker build |

## Lint and type-check

```bash
ruff check .
ruff format --check .
mypy src/
```

## API

Base URL: `/`. All read endpoints accept `?language=` (`en` | `yue` | `zh`, default `en`).

### `GET /district`

List all districts, ordered by `sort_order`, localized.

```
GET /district?language=yue
```

```json
[
  { "sort_order": 1, "id": 1, "name": "中西區" },
  { "sort_order": 2, "id": 2, "name": "東區" }
]
```

### `GET /category`

List all categories, ordered by id, localized.

```
GET /category?language=en
```

```json
[
  { "name_key": "anaesthesiology", "id": 1, "name": "Anaesthesiology" },
  { "name_key": "anatomical_pathology", "id": 2, "name": "Anatomical Pathology" }
]
```

### `GET /doctor`

List doctors, filterable and paginated, localized.

```
GET /doctor?language=zh&district=1&min_fee=100&max_fee=500&page=0&size=20
```

Query params: `language`, `district` (id), `category` (id), `min_fee`, `max_fee`,
`page` (0-based), `size` (10–100, default 20).

```json
[
  {
    "id": 1,
    "place_id": null,
    "phone_numbers": ["23456789"],
    "member_exclusive_fee": null,
    "consultation_fee": 300,
    "is_open_on_public_holidays": false,
    "category": { "id": 19, "name": "普通科" },
    "district": { "id": 1, "name": "中西區" },
    "name": "测试医生",
    "address": "测试街1号",
    "fee_detail": null,
    "operating_hours": []
  }
]
```

### `GET /doctor/{id}`

Get one doctor localized to `language`. Returns 404 if the id does not exist.

```
GET /doctor/2?language=yue
```

```json
{
  "id": 2,
  "place_id": null,
  "phone_numbers": ["23456789"],
  "member_exclusive_fee": null,
  "consultation_fee": 300,
  "is_open_on_public_holidays": false,
  "category": { "id": 19, "name": "普通科" },
  "district": { "id": 1, "name": "中西區" },
  "name": "測試醫生",
  "address": "測試街1號",
  "fee_detail": null,
  "operating_hours": []
}
```

### `POST /doctor`

Create one doctor. `name` and `address` require all three languages;
`fee_detail` is optional per language. Phone numbers are validated (HK region).

```
POST /doctor
Content-Type: application/json
```

```json
{
  "category_id": 19,
  "district_id": 1,
  "consultation_fee": 300,
  "phone_numbers": ["23456789"],
  "name": { "en": "Dr Test", "yue": "測試醫生", "zh": "测试医生" },
  "address": { "en": "1 Test St", "yue": "測試街1號", "zh": "测试街1号" },
  "fee_detail": { "en": "Mon–Fri" },
  "operating_hours": [
    { "day_of_week": 1, "open_time": "09:00", "close_time": "18:00" }
  ]
}
```

Returns 201 with the created doctor (localized, default language). 400 if
`category_id`/`district_id` is invalid; 422 if required fields are missing.

### `POST /doctor/batch`

Create many doctors in one transaction. Body is a JSON array of the same
`POST /doctor` payload. Returns 201 with the created list.

### Errors

| Status | When |
|---|---|
| 400 | Invalid `category_id` / `district_id` on create |
| 404 | `GET /doctor/{id}` with an unknown id |
| 422 | Validation failure (missing required field, bad phone number, unknown `language`) |
