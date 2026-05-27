# MVC Architecture Guidelines

Target layout for Phase 3. Adapt to the host language but always keep these five layers separated.

## Layer responsibilities

### Models (`models/`)
- One module per domain entity (`produto_model.py`, `user_model.py`, …).
- Data access ONLY: read / write rows or documents, parameterized queries, ORM mappings.
- **NO** business rules, **NO** HTTP concerns, **NO** notifications.
- Functions return plain dicts / domain objects — never `flask.jsonify(...)` or `res.send(...)`.

### Views / Routes (`views/` or `routes/`)
- HTTP-only layer: route declarations, URL parameters, status codes, response serialization.
- Calls a controller and returns its result wrapped for HTTP.
- **NO** SQL, **NO** business calculations, **NO** direct model access for complex flows.
- One file per domain (`product_routes.py`, `order_routes.py`) keeps URLs organized.

### Controllers (`controllers/`)
- Orchestrate models + services to fulfill use-cases.
- Own business rules: validation, calculations, dispatch (notifications, audit).
- One controller per domain or per use-case family.
- Return plain Python/JS values — controllers don't know about HTTP.

### Middlewares (`middlewares/`)
- Cross-cutting concerns: error handling, request validation, authentication, rate-limiting, logging.
- One file per concern (`error_handler.py`, `auth_middleware.py`, `validation_middleware.py`).
- Registered at app construction time.

### Config (`config/`)
- Single source of truth for environment-derived configuration.
- Reads `os.environ` / `process.env`. Validates required vars at boot.
- Exposes a frozen `settings` / `config` object the rest of the app consumes.
- Never holds secrets as literals — only references env keys.

## Composition root (`app.py` / `app.js`)
- Constructs the framework instance.
- Loads config.
- Wires middlewares.
- Registers route modules.
- That's it. **No business logic, no SQL, no validation in the entry point.**

## Reference layout per stack

### Python / Flask

```
src/
├── config/
│   └── settings.py           # loads .env, exposes Settings
├── models/
│   ├── __init__.py
│   ├── produto_model.py
│   ├── usuario_model.py
│   └── pedido_model.py
├── controllers/
│   ├── __init__.py
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/                    # OR routes/
│   ├── __init__.py
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   └── pedido_routes.py
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py
├── database.py               # connection factory only
└── app.py                    # composition root
.env.example
requirements.txt
```

When the project is already a Flask app with files at the root (no `src/`), it is acceptable to keep the same convention and just add the new directories at the root instead of moving everything under `src/`. The structure rule is about **separation**, not about a specific top-level dir.

### Node.js / Express

```
src/
├── config/
│   └── index.js              # exports { port, db, paymentGateway, ... }
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   └── paymentModel.js
├── controllers/
│   ├── checkoutController.js
│   └── reportController.js
├── routes/
│   ├── checkoutRoutes.js
│   ├── adminRoutes.js
│   └── userRoutes.js
├── middlewares/
│   ├── errorHandler.js
│   └── validate.js
├── infrastructure/
│   └── database.js           # connection factory
├── utils/
│   └── crypto.js             # bcrypt helpers
└── app.js                    # composition root
.env.example
package.json
```

## Adaptation rules

### Already partially organized projects
If the project already has `models/` and `routes/`:
- **Keep them.** Do not move files around just to use new names.
- ADD the missing layers (`controllers/`, `middlewares/`, `config/`).
- Refactor each route handler to call its controller instead of doing the work inline.

### Tiny projects
For projects with one or two domains, controllers may be a single file (`controllers/checkout_controller.py`). The separation is more important than the file count.

### Naming consistency
- Stick to one language per project. If the project is in Portuguese, keep Portuguese (`produto_controller.py`); if in English, keep English (`product_controller.py`). Do not mix.
- File names: `snake_case` for Python, `camelCase` or `kebab-case` for Node — match the existing convention in the project.

## Anti-patterns the layout itself prevents

| Old pattern | Layered fix |
|---|---|
| Business logic in routes | Controllers absorb it |
| God class with everything | Each layer becomes its own file |
| Global DB connection imported everywhere | Config exposes `db`; routes get it via controllers |
| Inline secrets | `config/` reads env |
| Duplicate validation | Middleware or controller-shared validators |
| Inconsistent error responses | `middlewares/error_handler` standardizes them |
| Sensitive fields in responses | Model serializers / DTOs strip them |

## Validation criteria for the final layout

After Phase 3, the layout should pass this checklist:

- [ ] `config/` module exists; no string literal secrets anywhere in `models/`/`controllers/`/`routes/`.
- [ ] Models contain zero `flask.jsonify` / `res.json` / route-decorator usage.
- [ ] Routes contain zero raw SQL strings.
- [ ] Controllers contain zero `request.*` / `req.*` direct access (they receive parameters from routes).
- [ ] One centralized error handler in `middlewares/`.
- [ ] Entry point (`app.py`/`app.js`) ≤ 50 lines, only wiring.
- [ ] All env-derived values come from `config/`.
- [ ] `.env.example` documents every required env var.
