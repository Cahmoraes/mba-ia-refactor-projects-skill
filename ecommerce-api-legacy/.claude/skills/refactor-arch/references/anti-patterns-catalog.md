# Anti-Patterns Catalog

Twenty anti-patterns to look for in Phase 2, with detection signals, severity, and the playbook entry that fixes each one. Severity is fixed per anti-pattern — do not downgrade based on perceived "small project".

## CRITICAL

### AP-01 — Hardcoded Credentials / Secrets
**Detection signals:**
- String literals like `SECRET_KEY = "..."`, `password = "..."`, `apiKey = "..."`, `pk_live_...`, `sk_live_...`
- DB user/password as inline strings in code (`dbPass: "senha..."`)
- SMTP user/password assigned in code
- Lines containing `secret`, `password`, `token`, `key`, `apikey`, `api_key` immediately followed by `=` and a string literal (not env access)

**Why it matters:** secrets in source control leak to git history, CI logs, screenshots. Immediate compromise of dependent services.

**Fix → Playbook:** TX-01 Extract secrets to environment

---

### AP-02 — SQL Injection (string concatenation in queries)
**Detection signals:**
- `execute("SELECT ... WHERE x = " + var)` or f-strings inside SQL (`f"SELECT ... {x}"`)
- Any SQL string built with `+`, `%`, `.format()`, template literals (`` `SELECT ... ${x}` ``)
- `cursor.execute(query)` where `query` was assembled from user input

**Why it matters:** allows attackers to read/modify any data, escalate privileges, exfiltrate the DB.

**Fix → Playbook:** TX-02 Parameterize SQL / TX-13 Adopt an ORM

---

### AP-03 — Insecure Password Storage
**Detection signals:**
- Passwords stored as plaintext (`INSERT INTO users (..., pass) VALUES (..., '123')`)
- MD5/SHA1 of password (`hashlib.md5(pwd.encode()).hexdigest()`)
- Base64 "encryption" (`Buffer.from(pwd).toString('base64')`)
- Custom loop pseudo-hashing without salt (`for i in range(10000): hash += ...`)

**Why it matters:** any DB leak exposes all user accounts. MD5/SHA1 are broken; base64 is not crypto.

**Fix → Playbook:** TX-03 Replace with bcrypt / werkzeug.security / argon2

---

### AP-04 — Arbitrary Code/SQL Execution Endpoint
**Detection signals:**
- Endpoints like `/admin/query` that accept SQL from the body and execute it
- `eval(...)`, `exec(...)`, `Function(...)`, `child_process.exec(userInput)` in handlers
- Routes that read `request.body.sql` / `req.body.code` and run it

**Why it matters:** full remote-code or remote-database execution. Single-shot RCE.

**Fix → Playbook:** TX-04 Delete dangerous admin endpoints

---

### AP-05 — God Class / God Method
**Detection signals:**
- Single class with 5+ unrelated responsibilities (DB init + routing + business logic + crypto + email)
- File >400 lines covering multiple domain entities (e.g. `models.py` with products, users, orders, reports all in one)
- Class named `Manager`, `Helper`, `Util`, `App` that owns everything

**Why it matters:** impossible to test in isolation, every change risks breaking unrelated features, blocks parallel work.

**Fix → Playbook:** TX-05 Split into Models + Controllers + Services per domain

---

### AP-06 — Sensitive Data Leak in Response
**Detection signals:**
- `to_dict()` / serializer returning `password`, `password_hash`, `senha`, `secret`, `token` fields
- `JSON.stringify(user)` without omitting sensitive fields
- `SELECT * FROM users` followed by direct jsonify of rows including the password column

**Why it matters:** API exposes credential material to every client.

**Fix → Playbook:** TX-10 Remove sensitive fields from serialized output

---

## HIGH

### AP-07 — Business Logic in Routes / Controllers
**Detection signals:**
- Route handler functions >40 lines
- Validation, DB queries, business calculations, notification dispatch all in one handler
- Direct ORM calls inside an HTTP handler interleaved with response formatting

**Why it matters:** breaks MVC, makes business rules impossible to unit-test, duplicates logic across handlers.

**Fix → Playbook:** TX-06 Extract business logic to controller/service

---

### AP-08 — Tight Coupling / No Dependency Injection
**Detection signals:**
- Classes that instantiate their own DB connection (`this.db = new sqlite3.Database(':memory:')` inside `constructor`)
- Modules that import a singleton DB and call it directly
- No composition root — dependencies are imported wherever they're used

**Why it matters:** can't swap implementations for tests, mocks, or different envs.

**Fix → Playbook:** TX-07 Introduce composition root + injected deps

---

### AP-09 — Global Mutable State
**Detection signals:**
- Module-level `let globalCache = {}` / `db_connection = None` that gets reassigned
- Variables declared at top of module, mutated by functions, read by others
- Singleton pattern implemented with module-global variables

**Why it matters:** unpredictable behaviour under concurrency, leaks state between tests/requests.

**Fix → Playbook:** TX-08 Encapsulate state in modules/classes with lifecycle

---

### AP-10 — Missing Centralized Error Handling
**Detection signals:**
- Every handler wrapped in `try/except` that returns a 500 with the raw exception message
- Bare `except:` clauses (silent failure)
- No `@app.errorhandler` (Flask) / no Express error middleware (`(err, req, res, next) =>`)
- Exceptions leak internal stack traces to clients

**Why it matters:** information disclosure + inconsistent error responses across endpoints.

**Fix → Playbook:** TX-09 Add centralized error handler

---

### AP-11 — Dead / Unintegrated Code
**Detection signals:**
- Service classes/files declared but never imported anywhere
- Helper functions that are never called
- Commented-out import paths

**Why it matters:** misleads readers, suggests features that don't exist, increases surface for bugs.

**Fix → Playbook:** TX-12 Wire it up or remove it

---

## MEDIUM

### AP-12 — N+1 Queries
**Detection signals:**
- `cursor.execute(...)` / `Model.query.get(id)` / `db.get(...)` inside a `for`/`forEach`/`.map` loop
- Building a "report" by iterating parent rows and querying child rows one-by-one

**Why it matters:** linear blow-up of DB round-trips; report endpoints get slow at small data sizes already.

**Fix → Playbook:** TX-14 Replace N+1 with JOIN / IN-clause / eager loading

---

### AP-13 — Callback Hell / Async Anti-Patterns
**Detection signals:**
- 3+ nested callbacks in a single handler (`db.get(..., (err, row) => { db.get(..., (err, row) => { db.run(..., (err) => { ... }) }) })`)
- Manual pending counters (`let coursesPending = ...; coursesPending--`) to "await" parallel async ops
- Mixing sync, callback and Promise styles in the same function

**Why it matters:** unmaintainable, error-prone (forgotten error paths), blocks `async/await` adoption.

**Fix → Playbook:** TX-11 Convert to async/await + Promise.all

---

### AP-14 — Duplicated Validation Logic
**Detection signals:**
- Same validation block (`if not title: ...`, `if len(x) < 3: ...`) repeated in create + update handlers
- Same `if priority < 1 or priority > 5` in 3+ files
- Same email regex repeated in user creation and user update

**Why it matters:** rules drift over time as one copy gets updated and another doesn't.

**Fix → Playbook:** TX-15 Extract validation to schemas / middleware

---

### AP-15 — Missing Input Validation
**Detection signals:**
- Endpoints that read `request.get_json()` and pass values straight to DB without type/length/format checks
- No regex on email, no length check on password, no range check on numeric ranks

**Why it matters:** crashes on bad input + opens attack surface (long-string DoS, type confusion).

**Fix → Playbook:** TX-15 Extract validation to schemas / middleware

---

### AP-16 — Deprecated / Obsolete API Usage
**Detection signals (examples — not exhaustive):**

| Stack | Deprecated | Modern equivalent |
|---|---|---|
| Node sqlite3 | `require('sqlite3').verbose()` — `verbose()` is deprecated; SDK callback API is legacy | use `better-sqlite3` or `sqlite` (promise wrapper); avoid `.verbose()` in production |
| Node | `new Buffer(x)` | `Buffer.from(x)` |
| Node Express | `body-parser` as separate dep | `express.json()` / `express.urlencoded()` built-in |
| Python | `datetime.utcnow()` (deprecated 3.12+) | `datetime.now(datetime.UTC)` |
| Python Flask | `flask_script` | Flask CLI (`flask run`) |
| Python | `hashlib.md5(...)` / `hashlib.sha1(...)` for passwords | `bcrypt`, `argon2`, `werkzeug.security.generate_password_hash` |
| Python | `pkg_resources` | `importlib.resources` / `importlib.metadata` |
| Node | callback-based `fs` | `fs/promises` + `async/await` |

If a project uses any of the deprecated APIs above, file a finding.

**Why it matters:** deprecated APIs are removed in future versions; many were deprecated specifically because they have correctness or security issues.

**Fix → Playbook:** TX-16 Migrate to modern API

---

## LOW

### AP-17 — Magic Numbers / Strings
**Detection signals:**
- Numeric literals embedded in logic without name (`if faturamento > 10000:`, `priority >= 1 and priority <= 5`)
- Status string literals repeated everywhere (`'pendente'`, `'approved'`) instead of an enum/constants module

**Why it matters:** unclear intent, makes changing thresholds risky.

**Fix → Playbook:** TX-17 Replace with named constants / enums

---

### AP-18 — Poor Naming
**Detection signals:**
- Single-letter variables for non-trivial values (`u`, `e`, `p`, `cc`, `cid`) when they hold user/email/password/credit-card
- Inconsistent language mixing (Portuguese + English for same domain)
- `data1`, `data2`, `temp`, `result` as final names

**Why it matters:** readers must trace every variable to learn what it holds.

**Fix → Playbook:** TX-18 Rename to intention-revealing names

---

### AP-19 — Inconsistent Logging (print/console.log everywhere)
**Detection signals:**
- `print(...)` / `console.log(...)` scattered in handlers and models
- No log level (everything is the same severity)
- No structured logging (key=value or JSON)

**Why it matters:** noisy logs in production; can't filter; sensitive data may be printed (passwords, tokens).

**Fix → Playbook:** TX-19 Use a logger with levels

---

### AP-20 — Bare Except / Silent Failures
**Detection signals:**
- `except:` with no exception type (Python)
- `try { ... } catch (e) { }` empty catch (Node)
- `except Exception: pass`

**Why it matters:** hides bugs, makes debugging nearly impossible.

**Fix → Playbook:** TX-20 Catch specific exceptions + log

---

## Severity rules

- **CRITICAL** → security failure or architecture-blocking. Must be remediated before Phase 3 closes.
- **HIGH** → strong MVC/SOLID violation. Remediate during Phase 3.
- **MEDIUM** → standardization / moderate performance. Remediate during Phase 3.
- **LOW** → readability / hygiene. Fix where convenient.

When a single line participates in multiple anti-patterns (e.g. a line is both a `bare except` and a duplicated validation block), file it under the highest severity that applies.
