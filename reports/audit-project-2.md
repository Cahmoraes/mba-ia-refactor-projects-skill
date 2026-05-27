================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code
Audit date: 2026-05-27

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: `src/utils.js:1-7`
Evidence: `dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_1234567890abcdef", smtpUser: "no-reply@fullcycle.com.br"`
Impact: Senha do banco, chave do gateway de pagamento e usuário SMTP versionados em git; vazamento = comprometimento de todos os serviços dependentes.
Recommendation: Mover para `process.env` via `config/index.js` lendo de `.env`. (Playbook TX-01)

### [CRITICAL] Insecure Password Storage
File: `src/utils.js:17-22`
Evidence: `for(let i = 0; i < 10000; i++) { hash += Buffer.from(pwd).toString('base64').substring(0, 2); }`
Impact: "badCrypto" é apenas base64 truncado — qualquer atacante reverte trivialmente. Não há salt; senhas idênticas geram hashes idênticos.
Recommendation: Substituir por `bcrypt` ou `bcryptjs` com `hash(pwd, 10)`/`compare(...)`. (Playbook TX-03)

### [CRITICAL] God Class — AppManager
File: `src/AppManager.js:1-141`
Evidence: Single class instancia DB, define schema, faz seed e implementa 3 rotas (checkout, financial-report, delete user) com lógica inline.
Impact: Impossível testar partes em isolamento; qualquer mudança em rota toca DB + crypto + lógica de pagamento.
Recommendation: Quebrar em `infrastructure/database.js`, `models/`, `controllers/`, `routes/` por domínio. (Playbook TX-05)

### [CRITICAL] Sensitive Data Leak in Logs
File: `src/AppManager.js:45`
Evidence: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`
Impact: Logs gravam número de cartão de crédito e chave do gateway — violação PCI-DSS, log retention propaga.
Recommendation: Nunca logar PAN; logar apenas últimos 4 dígitos. Remover gateway key dos logs. (Playbook TX-19)

### [CRITICAL] Orphan Records on User Delete
File: `src/AppManager.js:131-137`
Evidence: `app.delete('/api/users/:id', ... DELETE FROM users WHERE id = ?', [id], (err) => { res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."); })`
Impact: O próprio handler admite deixar registros órfãos em `enrollments` e `payments`; histórico financeiro fica corrompido. Sem FK constraints reais.
Recommendation: Implementar exclusão transacional cascata ou soft-delete; adicionar FOREIGN KEY com ON DELETE. (Controller transacional via Playbook TX-06)

### [HIGH] Business Logic in Routes
File: `src/AppManager.js:28-78` (checkout), `src/AppManager.js:80-129` (financial-report)
Evidence: Handler `/api/checkout` mistura validação, busca de curso, criação de usuário, hash, mock de pagamento, criação de matrícula, pagamento, audit log, cache em 50 linhas.
Impact: Regras de negócio (lógica de pagamento, criação de matrícula) ficam presas no handler HTTP; impossível reusar em outro fluxo (ex: importação batch).
Recommendation: Extrair `checkoutController.processCheckout(payload)` e `reportController.buildFinancialReport()`. (Playbook TX-06)

### [HIGH] Tight Coupling / No Dependency Injection
File: `src/AppManager.js:7`, `src/app.js:8-10`
Evidence: `this.db = new sqlite3.Database(':memory:')` dentro do construtor; AppManager é instanciado em app.js sem injeção.
Impact: Não dá para trocar para um sqlite em arquivo ou testar com DB fake.
Recommendation: `infrastructure/database.js` exporta `createDatabase()`; composição em `app.js` injeta nos controllers. (Playbook TX-07)

### [HIGH] Global Mutable State
File: `src/utils.js:9-15, 25`
Evidence: `let globalCache = {};` e `let totalRevenue = 0;` exportados como módulo-globais e mutados por `logAndCache`.
Impact: Estado compartilhado entre requests; risco de race conditions em produção; também há `totalRevenue` exportado mas nunca lido (dead).
Recommendation: Encapsular em classe `InMemoryCache` com instância via composition root. (Playbook TX-08)

### [HIGH] Missing Centralized Error Handling
File: `src/AppManager.js:28-137` (callbacks no checkout, financial-report, delete user)
Evidence: Cada caminho tem `res.status(500).send("Erro DB")` ad-hoc; nenhum `app.use((err, req, res, next) => ...)` registrado.
Impact: Mensagens de erro inconsistentes; falhas inesperadas viram unhandled rejections.
Recommendation: Middleware único `errorHandler` registrado por último; controllers lançam `AppError`. (Playbook TX-09)

### [MEDIUM] N+1 Queries in Financial Report
File: `src/AppManager.js:80-129`
Evidence: `courses.forEach(c => db.all("SELECT * FROM enrollments WHERE course_id = ?" ... enrollments.forEach(enr => db.get(SELECT user ...) ... db.get(SELECT payment ...)))`
Impact: 1 + N + 2·M consultas para N cursos com M matrículas cada; explode com volume.
Recommendation: Single SQL com `JOIN courses + enrollments + users + payments`, agregação em memória. (Playbook TX-14)

### [MEDIUM] Callback Hell
File: `src/AppManager.js:37-78` (checkout), `src/AppManager.js:80-129` (report)
Evidence: 4-5 níveis de callbacks aninhados + contador manual `coursesPending--, enrPending--` para "esperar" paralelo.
Impact: Caminhos de erro frequentemente esquecidos; impossível usar `async/await`; código contraintuitivo.
Recommendation: Promisificar `db.get/all/run` e migrar para `async/await` + `Promise.all`. (Playbook TX-11)

### [MEDIUM] Missing Input Validation
File: `src/AppManager.js:29-35`
Evidence: Apenas `if (!u || !e || !cid || !cc) return 400` — não valida formato de email, comprimento de senha, formato de cartão (16 dígitos numéricos).
Impact: Aceita emails malformados; "mock de pagamento" só verifica se o cartão começa com "4" — vulnerável a DoS de input.
Recommendation: Schema validator (`zod`/`joi`) ou middleware `validate(checkoutSchema)`. (Playbook TX-15)

### [MEDIUM] Deprecated API Usage
File: `src/AppManager.js:1`, `src/utils.js:17-22`
Evidence: `require('sqlite3').verbose()` (verbose mode desencorajado em prod, callback-based API legacy); padrão de "hash custom" com `Buffer.from(...).toString('base64')` é prática deprecada para senhas.
Impact: Driver legacy não devolve Promise; mantém o codebase preso ao estilo callback-hell.
Recommendation: Trocar para `better-sqlite3` (sync, simples) OU manter `sqlite3` mas promisificar; substituir `badCrypto` por `bcryptjs`. (Playbook TX-16)

### [LOW] Poor Naming
File: `src/AppManager.js:29-33`
Evidence: `let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;`
Impact: Leitor precisa rastrear cada variável para identificar usuário/email/senha/curso/cartão; payload public usa `usr`/`eml`/`pwd`.
Recommendation: Renomear localmente e suportar tanto `usr` quanto `name` no payload por retrocompatibilidade. (Playbook TX-18)

### [LOW] Inconsistent Logging via console.log
File: `src/utils.js:13`, `src/AppManager.js:45`, `src/app.js:13`
Evidence: `console.log(\`[LOG] Salvando no cache: ${key}\`)` espalhado, sem níveis, sem estrutura.
Impact: Logs não filtráveis; mistura `info` + `error` + dados sensíveis (vide finding de PCI).
Recommendation: Logger estruturado (`pino` ou JSON via `console`) com níveis. (Playbook TX-19)

### [LOW] Dead Code
File: `src/utils.js:10, 25`
Evidence: `let totalRevenue = 0` exportado mas nunca incrementado/lido; `logAndCache` escreve em `globalCache` que ninguém lê.
Impact: Código morto confunde leitor e sugere features que não existem.
Recommendation: Remover `totalRevenue`; substituir cache por feature real ou remover. (Playbook TX-12)

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
