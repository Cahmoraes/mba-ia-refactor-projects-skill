# Audit Report — task-manager-api (Project 3)

**Generated:** 2026-05-27  
**Skill version:** refactor-arch v1.0  
**Phase:** 2 — Audit

---

## Project Overview

| Item | Value |
|------|-------|
| Language | Python 3 |
| Framework | Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 |
| Domain | Task Manager (tasks, users, categories, reports, notifications) |
| Architecture | Partial MVC — has models/, routes/, services/, utils/ but business logic in routes; no controllers/ or config/ layers |
| Source files | 12 files, ~1158 LOC |
| DB | SQLite via SQLAlchemy ORM (tasks.db) |

---

## Findings

### [CRITICAL] AP-01 — Hardcoded SECRET_KEY

- **File:** `app.py:13`
- **Evidence:** `app.config['SECRET_KEY'] = 'super-secret-key-123'`
- **Impact:** Any attacker who reads the source can forge session cookies, bypass CSRF protection, or sign tokens. The value is committed to VCS and shared across all environments.
- **Recommendation:** Read from `os.environ['SECRET_KEY']`; fail fast if absent. Add to `.env.example` with a placeholder.

---

### [CRITICAL] AP-03 — Insecure Password Hashing (MD5)

- **File:** `models/user.py:29,32`
- **Evidence:** `self.password = hashlib.md5(pwd.encode()).hexdigest()`
- **Impact:** MD5 is a general-purpose hash, not a password KDF. No salt, trivially reversible via rainbow tables. Full database dump → all passwords cracked in minutes.
- **Recommendation:** Replace with `werkzeug.security.generate_password_hash` (bcrypt/scrypt) and `check_password_hash`. Remove `hashlib` import.

---

### [CRITICAL] AP-06 — Password Hash Exposed in API Responses

- **File:** `models/user.py:16-25`, `routes/user_routes.py:85-86`, `routes/user_routes.py:207-210`
- **Evidence:** `to_dict()` includes `'password': self.password`; called on user creation response and login response.
- **Impact:** Every GET /users/:id, POST /users, and POST /login returns the password hash to the caller. Violates data minimization; hash can be cracked offline.
- **Recommendation:** Remove `password` from `to_dict()`. Add separate `to_public()` method for API responses.

---

### [CRITICAL] AP-01 — Hardcoded SMTP Credentials

- **File:** `services/notification_service.py:9-10`
- **Evidence:** `self.email_user = 'taskmanager@gmail.com'` / `self.email_password = 'senha123'`
- **Impact:** Real email credentials committed to VCS. Account will be compromised on first public repo push.
- **Recommendation:** Read `SMTP_USER` and `SMTP_PASSWORD` from environment variables via config.

---

### [CRITICAL] AP-05 — Fake JWT Authentication Token

- **File:** `routes/user_routes.py:210`
- **Evidence:** `'token': 'fake-jwt-token-' + str(user.id)`
- **Impact:** Not a real token; trivially forgeable by any caller who knows any user ID. Any route that trusts this token is bypassed. No authentication actually occurs.
- **Recommendation:** Use `PyJWT` or similar to generate a signed token from `SECRET_KEY` with expiry. Or remove token field entirely until real auth is implemented.

---

### [HIGH] AP-07 — Business Logic Directly in Route Handlers

- **File:** `routes/task_routes.py:85-154`, `routes/user_routes.py:42-90`, `routes/report_routes.py:12-101`
- **Evidence:** Input validation, DB queries, overdue calculations, user productivity aggregation — all inline in route functions. Longest handler is 70 LOC.
- **Impact:** Untestable without HTTP context; violates SRP; duplication inevitable.
- **Recommendation:** Extract logic to `controllers/` layer. Routes become thin: parse request → call controller → return JSON.

---

### [HIGH] AP-11 — Dead Code: NotificationService Not Integrated

- **File:** `services/notification_service.py` (entire file)
- **Evidence:** `grep -r "NotificationService\|notification_service" routes/ app.py` → 0 results. Class exists, never instantiated, never imported.
- **Impact:** Notification behavior described in README is silently absent. Feature debt masquerading as implemented code.
- **Recommendation:** Wire into task creation: import, instantiate in composition root, inject into task controller, call `notify_task_assigned` when `user_id` set.

---

### [HIGH] AP-10 — No Centralized Error Handler

- **File:** `app.py` (entire file), `routes/task_routes.py:62,237`, `routes/user_routes.py:130,149`
- **Evidence:** Bare `except:` clauses silently swallow exceptions. No `@app.errorhandler` registered. 404/405 return Flask default HTML responses.
- **Impact:** Errors invisible in logs; inconsistent response format (HTML vs JSON); debugging impossible.
- **Recommendation:** Register `AppError` class + `@app.errorhandler` for 404, 405, 500. Replace all bare `except:` with `except Exception as e:` and log `str(e)`.

---

### [MEDIUM] AP-12 — N+1 Queries in GET /tasks

- **File:** `routes/task_routes.py:41-56`
- **Evidence:**
  ```python
  for t in tasks:  # 1 query (Task.query.all())
      user = User.query.get(t.user_id)   # +1 query per task
      cat = Category.query.get(t.category_id)  # +1 query per task
  ```
- **Impact:** 100 tasks = 201 queries. Degrades linearly. Visible latency spike under load.
- **Recommendation:** Use SQLAlchemy eager loading: `Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()`. Access `t.user.name` directly — no extra queries.

---

### [MEDIUM] AP-12 — N+1 Queries in User Productivity Report

- **File:** `routes/report_routes.py:53-68`
- **Evidence:**
  ```python
  for u in users:  # 1 query (User.query.all())
      user_tasks = Task.query.filter_by(user_id=u.id).all()  # +1 query per user
  ```
- **Impact:** 50 users = 51 queries just for productivity section.
- **Recommendation:** Single query: `Task.query.all()` then group by `user_id` in a dict.

---

### [MEDIUM] AP-14 — Duplicated Overdue Logic

- **File:** `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/user_routes.py:171-181`, `routes/report_routes.py:33-43`
- **Evidence:** Same 9-line overdue detection block copied 4+ times across files.
- **Impact:** Bug in logic must be fixed in 4+ places. Already diverged: some copies check `status != 'done'`, others also check `!= 'cancelled'`.
- **Recommendation:** Extract to `utils/helpers.py::is_overdue(task)`.

---

### [MEDIUM] AP-16 — Deprecated SQLAlchemy API

- **File:** `routes/task_routes.py:67,157,225,241`, `routes/user_routes.py:29,94,105,136,155`, `routes/report_routes.py:104,157`
- **Evidence:** `Task.query.get(task_id)` — `Query.get()` deprecated in SQLAlchemy 2.0, removed in 2.1.
- **Impact:** Will break on SQLAlchemy 2.1+ upgrade. Already raises `LegacyAPIWarning` in 2.0.
- **Recommendation:** Replace with `db.session.get(Task, task_id)` everywhere.

---

### [LOW] AP-17 — Hardcoded debug=True

- **File:** `app.py:34`
- **Evidence:** `app.run(debug=True, host='0.0.0.0', port=5000)`
- **Impact:** Debug mode in production exposes interactive debugger (arbitrary code execution via browser). Also exposes tracebacks in HTTP responses.
- **Recommendation:** `debug=settings.DEBUG` where `DEBUG` defaults to `False` and reads from `os.environ`.

---

### [LOW] AP-18 — Unused Imports

- **File:** `routes/task_routes.py:7`, `routes/user_routes.py:6`, `requirements.txt`
- **Evidence:** `import json, os, sys, time` (task_routes — none used); `import hashlib` (user_routes — MD5 logic, removable after fix); `marshmallow==3.20.1` (requirements — never imported anywhere).
- **Impact:** Dead imports inflate module load time; mislead readers; lint failures.
- **Recommendation:** Remove unused imports and `marshmallow` from requirements.txt.

---

### [LOW] AP-20 — Bare except Clauses

- **File:** `routes/task_routes.py:62,237`, `routes/user_routes.py:130,149`, `routes/report_routes.py:187,206,220`
- **Evidence:** `except:` with no exception type, no logging.
- **Impact:** Catches `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`. Swallows all errors silently. Impossible to debug failures.
- **Recommendation:** Use `except Exception as e:` and log `str(e)`. Let errors propagate to centralized handler.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 5 |
| HIGH | 3 |
| MEDIUM | 4 |
| LOW | 4 |
| **TOTAL** | **16** |

---

## Phase 2 Gate: Proceed to Refactoring

All findings documented. Ready for Phase 3.

**Priority refactoring order:**
1. Fix CRITICAL security issues (SECRET_KEY, MD5, password exposure, SMTP creds, fake JWT)
2. Add `config/settings.py`, `middlewares/error_handler.py`
3. Add `controllers/` layer — extract business logic from routes
4. Fix N+1 queries with joinedload
5. Wire NotificationService
6. Replace deprecated `Query.get()` with `db.session.get()`
7. Update routes to thin handlers
8. Add `.env.example`, update `requirements.txt`
