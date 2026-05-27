# Audit Report Template

The Phase 2 report MUST follow this exact template. Findings are ordered by severity (CRITICAL → HIGH → MEDIUM → LOW). Each finding includes file + line range, evidence, impact, and a recommendation that references a playbook transformation (TX-NN).

The report is both printed to the conversation AND saved to `reports/audit-project-<N>.md` at the repo root.

---

## Template

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project-directory-name>
Stack:   <language> + <framework version>
Files:   <N> analyzed | ~<LOC> lines of code
Audit date: <YYYY-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <anti-pattern name (matches catalog AP-NN)>
File: `<path/to/file.ext>:<start>-<end>` (or `:<line>` for single-line)
Evidence: `<smoking-gun code snippet, max 1 line>` (or 1-sentence structural description)
Impact: <one short sentence about what concretely breaks>
Recommendation: <action> (Playbook TX-NN)

### [CRITICAL] <next>
...

### [HIGH] <name>
...

### [MEDIUM] <name>
...

### [LOW] <name>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
````

## Rules for filling in the template

1. **Project name** = the immediate parent directory name of the codebase being audited (NOT the repo root).
2. **Stack** = `<Language> + <Framework> <version>` (e.g. `Python + Flask 3.1.1`).
3. **Files** = count of source files analyzed in Phase 1.
4. **LOC** = approximate, can be rounded to the nearest 50 or 100.
5. **Summary** counters are the totals per severity — they must match what's in `## Findings`.
6. **Each finding header** is `### [<SEVERITY>] <Title>`. The title should be short and match the catalog anti-pattern name when possible.
7. **File reference**:
   - Single-line: `models.py:28`
   - Range: `models.py:28-29`
   - Whole file / class: `models.py:1-315`
   - Multiple files for the same finding: list all, comma-separated.
8. **Evidence** ≤ 100 characters. Prefer the smoking-gun line itself.
9. **Impact** ≤ 1 short sentence.
10. **Recommendation** ≤ 1 line + the playbook transformation ID.
11. **Order**: severity DESC, then file path ASC, then line ASC.
12. **Confirmation gate** is part of the report — print it verbatim.

## Filled example (excerpt)

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~800 lines of code
Audit date: 2026-05-27

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials
File: `app.py:7-8`
Evidence: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Impact: Secret material lives in git history; compromise of repo = compromise of sessions.
Recommendation: Load from env via `config/settings.py`. (Playbook TX-01)

### [CRITICAL] SQL Injection
File: `models.py:28, 47-49, 109-111, 280, 289-297`
Evidence: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
Impact: Any client can read/modify the entire DB via crafted parameters.
Recommendation: Use parameterized queries `?` placeholders + bind params. (Playbook TX-02)
```
