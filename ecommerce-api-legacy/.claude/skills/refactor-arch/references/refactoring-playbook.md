# Refactoring Playbook

Thirteen transformations mapped to the anti-patterns catalog. Each has detection → target shape → before/after. Apply them during Phase 3 to remediate Phase 2 findings.

---

## TX-01 — Extract secrets to environment

**Fixes:** AP-01 (Hardcoded Credentials)

**Target:** all secrets read from environment via a `config/settings.py` (Python) or `config/index.js` (Node). A `.env.example` documents the required variables.

### Python — before
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

### Python — after
```python
# config/settings.py
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")

settings = Settings()
```
```python
# app.py
from config.settings import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
```
```bash
# .env.example
SECRET_KEY=change-me
DEBUG=false
DB_PATH=loja.db
```

### Node — before
```javascript
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

### Node — after
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
    port: parseInt(process.env.PORT || '3000', 10),
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
};
```
```bash
# .env.example
PORT=3000
DB_PASS=
PAYMENT_GATEWAY_KEY=
SMTP_USER=
```

---

## TX-02 — Parameterize SQL queries

**Fixes:** AP-02 (SQL Injection)

**Target:** every SQL call uses placeholders (`?` for sqlite, `$1` for postgres, `%s` for mysql) and a parameter list. Never string-concatenate user input into SQL.

### Before
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES ('" + nome + "', '" + email + "', '" + senha + "')"
)
```

### After
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
    (nome, email, senha),
)
```

### Node — before
```javascript
db.run("SELECT * FROM users WHERE id = " + req.params.id);
```

### Node — after
```javascript
db.run("SELECT * FROM users WHERE id = ?", [req.params.id]);
```

For dynamic `WHERE` clauses, build placeholders + a parallel value list:
```python
clauses, values = [], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)")
    values.extend([f"%{termo}%", f"%{termo}%"])
if categoria:
    clauses.append("categoria = ?")
    values.append(categoria)

query = "SELECT * FROM produtos"
if clauses:
    query += " WHERE " + " AND ".join(clauses)
cursor.execute(query, values)
```

---

## TX-03 — Replace insecure password storage with a strong KDF

**Fixes:** AP-03 (Insecure Password Storage)

**Target:** passwords stored as `bcrypt` / `argon2` / `werkzeug.security.generate_password_hash` hashes with built-in salt. Verification uses the matching `check_password_hash`.

### Python — before
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

### Python — after
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd: str) -> None:
    self.password = generate_password_hash(pwd)

def check_password(self, pwd: str) -> bool:
    return check_password_hash(self.password, pwd)
```

### Node — before
```javascript
function badCrypto(pwd) {
    let hash = "";
    for (let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

### Node — after
```javascript
const bcrypt = require('bcryptjs');

async function hashPassword(pwd) {
    return bcrypt.hash(pwd, 10);
}

async function verifyPassword(pwd, hash) {
    return bcrypt.compare(pwd, hash);
}
```

Add `bcryptjs` / `bcrypt` to dependencies. Old plaintext or weak-hash data must be re-hashed on next login.

---

## TX-04 — Delete dangerous admin endpoints

**Fixes:** AP-04 (Arbitrary Code/SQL Execution Endpoint)

**Target:** endpoints that execute user-supplied SQL or code are removed entirely. If admin DB inspection is needed, build a proper read-only endpoint that returns specific data (not arbitrary queries).

### Before
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    cursor.execute(query)
    ...
```

### After
- Delete the route entirely.
- If a real admin need existed, replace with a typed endpoint:
```python
# views/admin_routes.py
@admin_bp.get("/admin/stats")
def admin_stats():
    return jsonify(admin_controller.collect_stats())
```

---

## TX-05 — Split God Class into Models + Controllers + Routes

**Fixes:** AP-05 (God Class / God Method)

**Target:** each domain entity has its own model file; each use-case family has its own controller; routes are thin handlers.

### Before (Node God class)
```javascript
class AppManager {
    constructor() { this.db = new sqlite3.Database(':memory:'); }
    initDb() { ... }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => { /* 50 lines of business + SQL */ });
        app.get('/api/admin/financial-report', ...);
        app.delete('/api/users/:id', ...);
    }
}
```

### After
```
src/
├── infrastructure/database.js          # createDatabase()
├── models/
│   ├── userModel.js                    # findByEmail, insert
│   ├── courseModel.js                  # findById
│   ├── enrollmentModel.js              # insert
│   └── paymentModel.js                 # insert
├── controllers/
│   ├── checkoutController.js           # processCheckout(payload)
│   └── reportController.js             # buildFinancialReport()
├── routes/
│   ├── checkoutRoutes.js               # POST /api/checkout → controller
│   ├── reportRoutes.js                 # GET /api/admin/financial-report
│   └── userRoutes.js                   # DELETE /api/users/:id
├── middlewares/errorHandler.js
└── app.js                              # wires everything
```

Each module is now ≤ 80 lines, focused on a single responsibility.

---

## TX-06 — Move business logic out of routes

**Fixes:** AP-07 (Business Logic in Routes)

**Target:** routes are thin: parse → delegate → respond. All branching, calculations, dispatches live in controllers.

### Before
```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data: return jsonify({...}), 400
    title = data.get('title')
    if not title: return jsonify({...}), 400
    if len(title) < 3: return jsonify({...}), 400
    if len(title) > 200: return jsonify({...}), 400
    # ... 40 more lines of validation + DB + notification
```

### After
```python
# routes/task_routes.py
from controllers import task_controller

@task_bp.post('/tasks')
def create_task():
    payload = request.get_json()
    task, error = task_controller.create_task(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(task), 201
```
```python
# controllers/task_controller.py
def create_task(payload: dict) -> tuple[dict | None, str | None]:
    valid, error = validate_task_payload(payload)
    if error:
        return None, error
    task = task_model.create(valid)
    notification_service.notify_assigned(task)
    return task.to_dict(), None
```

---

## TX-07 — Introduce composition root with injected dependencies

**Fixes:** AP-08 (Tight Coupling)

**Target:** dependencies (DB connection, services) are constructed once in the entry point and passed into modules that need them.

### Before
```javascript
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');   // class instantiates its own DB
    }
}
```

### After
```javascript
// infrastructure/database.js
const sqlite3 = require('sqlite3');
function createDatabase() {
    const db = new sqlite3.Database(':memory:');
    return db;
}
module.exports = { createDatabase };
```
```javascript
// app.js
const { createDatabase } = require('./infrastructure/database');
const checkoutController = require('./controllers/checkoutController');

const db = createDatabase();
app.use('/api/checkout', require('./routes/checkoutRoutes')(checkoutController(db)));
```
```javascript
// controllers/checkoutController.js
module.exports = (db) => ({
    processCheckout: async (payload) => { /* uses db */ },
});
```

---

## TX-08 — Encapsulate state

**Fixes:** AP-09 (Global Mutable State)

**Target:** no module-level `let cache = {}` mutated by functions. Encapsulate in a class instance, a closure, or scope state to request lifecycle.

### Before
```javascript
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
module.exports = { globalCache, logAndCache };
```

### After
```javascript
// infrastructure/cache.js
class InMemoryCache {
    constructor() { this._store = new Map(); }
    set(key, value) { this._store.set(key, value); }
    get(key) { return this._store.get(key); }
}
module.exports = { InMemoryCache };
```
The single instance is created in the composition root and injected where needed.

---

## TX-09 — Add centralized error handler

**Fixes:** AP-10 (Missing Centralized Error Handling)

**Target:** all unhandled errors funnel through one place that formats them consistently and never leaks stack traces.

### Python (Flask)
```python
# middlewares/error_handler.py
from flask import jsonify

class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app_error(err):
        return jsonify({"error": str(err)}), err.status

    @app.errorhandler(404)
    def _not_found(_):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(Exception)
    def _generic(err):
        app.logger.exception("unhandled")
        return jsonify({"error": "Internal Server Error"}), 500
```

Controllers raise `AppError("Produto não encontrado", 404)` instead of returning a dict and a status code.

### Node (Express)
```javascript
// middlewares/errorHandler.js
class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
    }
}

function errorHandler(err, req, res, next) {
    if (err instanceof AppError) return res.status(err.status).json({ error: err.message });
    console.error(err);
    res.status(500).json({ error: 'Internal Server Error' });
}

module.exports = { AppError, errorHandler };
```
Register `app.use(errorHandler)` AFTER all routes.

---

## TX-10 — Strip sensitive fields from responses

**Fixes:** AP-06 (Sensitive Data Leak)

**Target:** serializers never emit `password`, `password_hash`, internal `token`, etc.

### Before
```python
def to_dict(self):
    return {
        'id': self.id, 'name': self.name, 'email': self.email,
        'password': self.password,   # leaks hash
        'role': self.role,
    }
```

### After
```python
def to_dict(self) -> dict:
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'role': self.role,
        'active': self.active,
        'created_at': self.created_at.isoformat() if self.created_at else None,
    }
```
Add a separate `to_dict_with_secrets()` only if internal code legitimately needs the hash — never expose it through HTTP.

---

## TX-11 — Replace callback hell with async/await

**Fixes:** AP-13 (Callback Hell)

**Target:** asynchronous flows expressed with `async/await` and `Promise.all` instead of nested callbacks or pending counters.

### Before
```javascript
this.db.get("SELECT ...", [cid], (err, course) => {
    if (err) return res.status(500).send("Erro DB");
    this.db.get("SELECT ...", [e], (err, user) => {
        this.db.run("INSERT ...", [...], function(err) {
            ...
        });
    });
});
```

### After
```javascript
// infrastructure/database.js — promisify the few methods we need
const sqlite3 = require('sqlite3');
function createDatabase() {
    const db = new sqlite3.Database(':memory:');
    return {
        get: (sql, params=[]) => new Promise((res, rej) => db.get(sql, params, (e, r) => e ? rej(e) : res(r))),
        all: (sql, params=[]) => new Promise((res, rej) => db.all(sql, params, (e, r) => e ? rej(e) : res(r))),
        run: (sql, params=[]) => new Promise((res, rej) => db.run(sql, params, function(e) { e ? rej(e) : res(this); })),
    };
}
```
```javascript
// controllers/checkoutController.js
async function processCheckout(payload) {
    const course = await db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [payload.courseId]);
    if (!course) throw new AppError("Curso não encontrado", 404);

    let user = await db.get("SELECT id FROM users WHERE email = ?", [payload.email]);
    if (!user) {
        const hash = await hashPassword(payload.password);
        const inserted = await db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [payload.name, payload.email, hash]);
        user = { id: inserted.lastID };
    }
    // ... continues linearly
}
```

Use `Promise.all` for independent reads (e.g. the report endpoint).

---

## TX-12 — Wire up dead code or remove it

**Fixes:** AP-11 (Dead / Unintegrated Code)

**Target:** if a service exists for a real use-case (e.g. `NotificationService`), wire it from the controllers that should be triggering it. If it's truly unused, delete it.

### Before
`services/notification_service.py` exists with `send_email`, `notify_task_assigned`, `notify_task_overdue` — and is never imported.

### After
- Inject `NotificationService` in the composition root.
- Controllers call `notification_service.notify_task_assigned(user, task)` after `task_model.create(...)`.
- Remove SMTP credentials from the service constructor — read them from `config`.

---

## TX-13 — Adopt an ORM (or stay with parameterized queries cleanly)

**Fixes:** reinforces AP-02 mitigation; reduces boilerplate in models.

**Target:** if the project is medium-sized and on Flask, SQLAlchemy is appropriate. For tiny Node projects, `better-sqlite3` keeps things simple while remaining safe.

This is OPTIONAL — only adopt if the project doesn't already use an ORM. Don't tear out an existing ORM to introduce a new one.

---

## TX-14 — Replace N+1 with eager loading or batch queries

**Fixes:** AP-12 (N+1 Queries)

**Target:** one query for parents, one for all children (IN clause or JOIN). For ORMs, use `joinedload`/`select_related`.

### Before
```python
pedidos = Pedido.query.all()
for p in pedidos:
    p.itens = ItemPedido.query.filter_by(pedido_id=p.id).all()
```

### After (SQLAlchemy)
```python
from sqlalchemy.orm import joinedload
pedidos = Pedido.query.options(joinedload(Pedido.itens)).all()
```

### After (raw SQL, single round-trip)
```python
ids = [p["id"] for p in parents]
placeholders = ",".join("?" * len(ids))
itens = cursor.execute(
    f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})", ids,
).fetchall()
by_parent = {}
for it in itens:
    by_parent.setdefault(it["pedido_id"], []).append(it)
for p in parents:
    p["itens"] = by_parent.get(p["id"], [])
```

---

## TX-15 — Extract validation to schemas / middleware

**Fixes:** AP-14 (Duplicated Validation) + AP-15 (Missing Input Validation)

**Target:** one definition per payload type; create and update share the rules.

### Before (duplicated in create + update)
```python
if not title: return jsonify({"error": "..."}), 400
if len(title) < 3: return jsonify({"error": "..."}), 400
if len(title) > 200: return jsonify({"error": "..."}), 400
```

### After
```python
# middlewares/validators.py
TASK_STATUSES = {"pending", "in_progress", "done", "cancelled"}

def validate_task_payload(data: dict, partial: bool = False) -> tuple[dict | None, str | None]:
    if not data:
        return None, "Dados inválidos"
    if not partial or "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return None, "Título é obrigatório"
        if not (3 <= len(title) <= 200):
            return None, "Título deve ter entre 3 e 200 caracteres"
    if "status" in data and data["status"] not in TASK_STATUSES:
        return None, "Status inválido"
    if "priority" in data and not (1 <= data["priority"] <= 5):
        return None, "Prioridade deve ser entre 1 e 5"
    return data, None
```
Routes call the validator once; create and update both reuse it (with `partial=True` on update).

---

## TX-16 — Replace deprecated APIs

**Fixes:** AP-16 (Deprecated APIs)

**Target:** modernize calls per the catalog mapping.

### Examples
```python
# before
from datetime import datetime
now = datetime.utcnow()
# after
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```
```javascript
// before
const buf = new Buffer(value);
// after
const buf = Buffer.from(value);
```
```javascript
// before
const sqlite3 = require('sqlite3').verbose();
// after  (verbose() is fine in dev but should be conditional in prod)
const sqlite3 = require('sqlite3');
```

When in doubt, the catalog entry for AP-16 lists the modern equivalent.

---

## TX-17 — Replace magic numbers with named constants

**Fixes:** AP-17

**Target:** thresholds and status strings get a name.

### Before
```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

### After
```python
# controllers/sales_controller.py
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]

def compute_discount(revenue: float) -> float:
    for threshold, rate in DISCOUNT_TIERS:
        if revenue > threshold:
            return revenue * rate
    return 0.0
```

---

## TX-18 — Rename to intention-revealing names

**Fixes:** AP-18 (Poor Naming)

**Target:** local vars, parameters, payload keys all read as English/Portuguese words.

### Before
```javascript
let u = req.body.usr;
let e = req.body.eml;
let cc = req.body.card;
```

### After
```javascript
const { name, email, password, courseId, creditCard } = req.body;
```

When the public payload uses bad names (`usr`, `eml`), keep backwards compatibility by mapping at the route boundary:
```javascript
const payload = {
    name: req.body.usr ?? req.body.name,
    email: req.body.eml ?? req.body.email,
    ...
};
```

---

## TX-19 — Replace print/console.log with a logger

**Fixes:** AP-19 (Inconsistent Logging)

### Python
```python
# infrastructure/logger.py
import logging, os
logger = logging.getLogger("app")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
logger.addHandler(handler)
```
Replace `print("Task criada: " + str(task.id))` with `logger.info("task created", extra={"task_id": task.id})`.

### Node
Use `pino` or the built-in `console` with structured payloads:
```javascript
console.log(JSON.stringify({ level: "info", event: "checkout", enrollmentId }));
```

---

## TX-20 — Catch specific exceptions, log, re-raise

**Fixes:** AP-20 (Bare Except / Silent Failures)

### Before
```python
try:
    ...
except:
    return jsonify({"error": "Erro interno"}), 500
```

### After
```python
try:
    ...
except sqlalchemy.exc.IntegrityError:
    raise AppError("Conflito de integridade", 409)
except Exception:
    logger.exception("tasks.create.failed")
    raise   # let centralized handler return 500
```
Bare except is acceptable ONLY at the outermost edge (the centralized error handler).

---

## Phase 3 validation routine

After applying transformations:

1. **Static check** — re-grep the codebase for the catalog signals; nothing should match anymore.
2. **Boot check** — start the app in the background; confirm process alive and port open.
3. **Smoke endpoints** — `curl` 2–3 known endpoints (the health check, a list endpoint, a create endpoint with a sample payload). Compare status codes / response shape against the pre-refactor behavior.
4. **Cleanup** — kill the background process.
5. **Report** — print the closing block from SKILL.md (`PHASE 3: REFACTORING COMPLETE`).
