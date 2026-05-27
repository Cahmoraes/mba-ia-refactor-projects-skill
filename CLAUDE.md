# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Challenge Overview

This is a challenge project for the MBA Full Cycle IA course. The goal is to create a reusable AI Skill (for Claude Code, Gemini CLI, or Codex) that can automatically analyze, audit, and refactor legacy codebases to follow the MVC pattern.

The skill should work in three phases:
1. **Detect** — identify language, framework, and current architecture
2. **Audit** — classify anti-patterns by severity (CRITICAL → LOW)
3. **Refactor** — restructure to MVC and validate the app still works

## Repository Structure

Three intentionally broken projects serve as test targets:

- `code-smells-project/` — Python/Flask e-commerce API (~780 LOC), monolithic, 4 files, SQL injection vulnerabilities
- `ecommerce-api-legacy/` — Node.js/Express LMS (~180 LOC), God class (`AppManager.js`), hardcoded credentials
- `task-manager-api/` — Python/Flask task manager (~1158 LOC), partially structured but config/security issues

The skill itself should be created at `.claude/skills/refactor-arch/` (or equivalent path).

## Running the Projects

### code-smells-project (Python/Flask)
```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
# Serves on http://localhost:5000
# DB: loja.db (auto-created)
```

### ecommerce-api-legacy (Node.js/Express)
```bash
cd ecommerce-api-legacy
npm install
npm start
# Serves on http://localhost:3000
# DB: in-memory SQLite
```

### task-manager-api (Python/Flask)
```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py   # must run before first start
python app.py
# Serves on http://localhost:5000
# DB: tasks.db (auto-created)
```

## Known Anti-Patterns per Project

### Severity Scale
- **CRITICAL**: Security vulnerabilities, unauthorized data exposure, architecture failures
- **HIGH**: God classes, tight coupling, SOLID violations
- **MEDIUM**: Code duplication, N+1 queries, missing validation
- **LOW**: Magic numbers, naming conventions, clarity issues

### code-smells-project
- `app.py:7` — Hardcoded `SECRET_KEY`
- `app.py:8` — `DEBUG=True` hardcoded
- `app.py:59-78` — `/admin/query` endpoint executes arbitrary SQL
- `models.py:28-29` — SQL injection via string concatenation

### ecommerce-api-legacy
- `utils.js:1-7` — Hardcoded DB password, payment gateway key, SMTP credentials
- `utils.js:17-22` — Insecure password hashing (base64, not cryptographic)
- `AppManager.js:1-78` — God class: routing + DB management + business logic in one class

### task-manager-api
- `app.py:13` — Hardcoded `SECRET_KEY`
- Routes contain business logic that belongs in a service layer
- `notification_service.py` exists but is not properly integrated

## Deliverables

The challenge requires:
1. A reusable skill file with knowledge references about MVC, anti-patterns, and refactoring
2. Audit reports for all three projects
3. Refactored versions of the three projects following MVC
4. Validation that refactored apps still function correctly
5. Updated README documenting the results
