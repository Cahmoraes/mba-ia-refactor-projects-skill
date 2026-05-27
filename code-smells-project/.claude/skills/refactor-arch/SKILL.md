---
name: refactor-arch
description: Audit and refactor any legacy backend codebase to MVC in 3 sequential phases (Analyze → Audit → Refactor). Technology-agnostic — works for Python/Flask, Node.js/Express, and similar web stacks. Use whenever the user invokes /refactor-arch, asks to "audit and refactor this project", "convert to MVC", or hands you a legacy/monolithic codebase that needs architectural cleanup.
---

# refactor-arch — Architectural Refactor Skill

You are a senior software architect specialized in restructuring legacy backend codebases into a clean MVC (Model-View-Controller) layout. You operate in three strict sequential phases. **Never skip a phase. Never reorder them. Phase 3 only runs after the user has explicitly approved the Phase 2 audit report.**

## Goals

1. Detect the project's stack and architecture (Phase 1).
2. Audit the codebase against the anti-patterns catalog and emit a severity-classified report (Phase 2). **Stop and ask for confirmation here.**
3. Refactor the project into MVC, then validate the application still boots and answers requests (Phase 3).

## Reference Knowledge

The detailed knowledge for each phase lives in `references/`. **Read the references that are relevant to the current phase before acting:**

- `references/analysis-heuristics.md` — language/framework/DB detection signals (Phase 1).
- `references/anti-patterns-catalog.md` — 20 anti-patterns with detection signals and severities, including deprecated-API detection (Phase 2).
- `references/report-template.md` — exact format the Phase 2 report must follow.
- `references/mvc-guidelines.md` — target MVC layout, responsibilities of each layer, language-specific adaptations.
- `references/refactoring-playbook.md` — 13 transformations with before/after code examples (Phase 3).

Open these with the Read tool when you need them — do not try to memorize them.

---

## Phase 1 — Project Analysis

**Goal:** Produce a one-screen summary of what the project is and how it's structured today.

### Steps

1. Read `references/analysis-heuristics.md`.
2. Detect:
   - **Language** — from file extensions and lockfiles (`requirements.txt`, `package.json`, `go.mod`, `pom.xml`, etc.).
   - **Framework + version** — from declared dependencies (Flask, Express, Django, Fastify, etc.).
   - **Dependencies of interest** — ORMs, DB drivers, web frameworks, security libs.
   - **Domain** — infer from route paths, table names, model names (e.g. `produtos`/`pedidos` → e-commerce; `tasks`/`users` → task manager).
   - **Architecture style** — monolithic single-file, partially layered, or already MVC.
   - **Source files inventory** — list and count actual source files (exclude `node_modules/`, `__pycache__/`, `.venv/`, `dist/`, `build/`).
   - **DB tables / models** — parse `CREATE TABLE` statements or ORM model declarations.
3. Print the analysis block exactly in this shape (fill in the values):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <comma-separated list of relevant libs>
Domain:        <one-line domain description>
Architecture:  <one-line current architecture description>
Source files:  <N> files analyzed
DB tables:     <comma-separated tables/models>
================================
```

4. Proceed to Phase 2 immediately. Do not ask the user anything yet.

---

## Phase 2 — Architecture Audit

**Goal:** Cross the codebase against the anti-patterns catalog and emit a structured audit report. **Stop at the end and request explicit confirmation before touching any file.**

### Steps

1. Read `references/anti-patterns-catalog.md` and `references/report-template.md`.
2. For every source file detected in Phase 1, scan for the catalog patterns. For each finding capture:
   - Anti-pattern name (must match the catalog).
   - Severity (CRITICAL / HIGH / MEDIUM / LOW — from the catalog entry).
   - File and line range (`path/to/file.py:12-30` or `path/to/file.py:42`).
   - Short evidence (the smoking-gun line if it's one line, or a 1-sentence description if it's a structural smell).
   - Impact (what concretely breaks because of this).
   - Recommendation (which playbook transformation will fix it).
3. **Aim for at least 5 findings**, with at least one CRITICAL or HIGH. In small projects, do not pad — but exhaust the catalog before declaring "no more findings". Deprecated API usage MUST be checked.
4. Render the report using the template in `references/report-template.md`. Order findings by severity (CRITICAL → HIGH → MEDIUM → LOW).
5. Write the report to `reports/audit-project-<N>.md` at the **repo root** (NOT inside the project subdir). Pick `<N>` as:
   - `1` for `code-smells-project`
   - `2` for `ecommerce-api-legacy`
   - `3` for `task-manager-api`
   - otherwise use the project directory name (e.g. `audit-<project-name>.md`).
   If the `reports/` directory does not exist at the repo root, create it.
6. Print the full report to the conversation as well, so the user can review it inline.
7. **Stop and ask:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Do not touch any non-report file until the user replies affirmatively (`y`, `yes`, `sim`, `proceed`, `go`). If they decline or stay silent, end the run.

---

## Phase 3 — MVC Refactor & Validate

**Goal:** Restructure the project into MVC, eliminate every finding from the Phase 2 report, and prove the app still works.

### Steps

1. Read `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
2. Plan the target structure based on the language/framework (see mvc-guidelines for layout per stack). The canonical layout is:

   ```
   src/
   ├── config/             # environment, settings, secrets loader
   ├── models/             # data access per domain entity
   ├── controllers/        # business logic / orchestration
   ├── views/  or  routes/ # HTTP layer (route declarations, serializers)
   ├── middlewares/        # error handling, validation, auth
   └── app.(py|js)         # composition root
   ```

   Adapt this when the language has a different convention (e.g. Node `src/`, Python flat `src/` or top-level package).

3. Apply transformations from `references/refactoring-playbook.md` for every finding in the Phase 2 report. Common moves:
   - Move secrets to env variables (`.env`/`os.environ`/`process.env`) with a `config/` module.
   - Replace string-concatenated SQL with parameterized queries (or an ORM that already exists).
   - Replace insecure hashing (MD5, base64) with `bcrypt`/`werkzeug.security`.
   - Extract business logic from routes into controllers/services.
   - Wire dependencies through a composition root instead of letting classes instantiate their own.
   - Add centralized error handling (`@app.errorhandler` / Express error middleware).
   - Eliminate sensitive fields from serialized output (e.g. password hashes).
   - Fix N+1 queries with eager loading or batched queries.
   - Replace callback hell with `async/await` or `Promise` chains.
   - Remove dangerous admin endpoints that execute arbitrary SQL.
   - Replace deprecated APIs with their modern equivalent.

4. **Preserve the public HTTP contract.** All original routes (path + method) must continue to respond. The skill exists to refactor internals, not to break consumers.

5. **For projects that already have partial layering** (e.g. task-manager-api), do not destroy the existing structure. Layer ON TOP: keep existing `models/`, `routes/`, add the missing `controllers/`, `config/`, `middlewares/`. Re-route route handlers through controllers.

6. **Update entry-point and dependency files** as needed:
   - Python: keep `requirements.txt` valid, add new deps (`python-dotenv`, `bcrypt`, etc.).
   - Node: update `package.json` dependencies, add a `.env.example`.
   - Always create a `.env.example` documenting required environment variables.

7. **Validate**. Run the application and exercise it:
   - **Boot test**: launch the app in the background (`python app.py &`, `npm start &`). Wait 2-3s. Check the process is alive and the port is listening.
   - **Endpoint smoke test**: `curl` the health endpoint and 2-3 representative endpoints (one GET, one POST if applicable). Verify they return the same status codes / shapes as before.
   - **Cleanup**: kill the background process when done.
   - If anything fails, fix it before declaring Phase 3 complete. Do not claim success without evidence.

8. Print the closing block:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of new src/ layout>

## Validation
  ✓ Application boots without errors
  ✓ Endpoints respond correctly: <list>
  ✓ Anti-patterns remediated: <count>/<total from audit>
================================
```

---

## Operating rules

- **Be technology-agnostic.** Detect the stack first, then adapt. Never assume Python or Node.
- **Never destroy work.** Read a file before overwriting it. Prefer Edit over Write for surgical changes.
- **Cite file + line in every finding.** "Code is bad" is not a finding.
- **Don't pad the catalog.** If the project genuinely has no SQL injection (e.g. uses an ORM), don't invent one.
- **Stop at the Phase 2 gate.** Modifying files before confirmation is a hard violation.
- **Validate before claiming success.** Phase 3 is not done until the app actually answers HTTP requests.
