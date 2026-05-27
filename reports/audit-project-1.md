================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~785 lines of code
Audit date: 2026-05-27

## Summary
CRITICAL: 7 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: `app.py:7-8`
Evidence: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` and `app.config["DEBUG"] = True`
Impact: Chave de sessão e flag de debug versionadas em git; basta acesso ao repo para forjar sessões e ver stack traces em produção.
Recommendation: Mover para `config/settings.py` lendo de variáveis de ambiente. (Playbook TX-01)

### [CRITICAL] SQL Injection (string concatenation)
File: `models.py:28, 47-50, 58-61, 68, 92, 109-111, 127-129, 140, 148-151, 155-160, 163-166, 174, 188, 192, 220, 224, 280, 289-297`
Evidence: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
Impact: Todas as queries (~20) concatenam parâmetros direto na string SQL; qualquer endpoint público é vetor de injeção (`/login`, `/produtos/busca`, `/produtos/<id>`).
Recommendation: Substituir por queries parametrizadas com placeholder `?`. (Playbook TX-02)

### [CRITICAL] Plaintext Password Storage
File: `database.py:75-83`, `models.py:105-120, 122-131`
Evidence: `("Admin", "admin@loja.com", "admin123", "admin")` — senha gravada sem hash.
Impact: Vazamento do DB expõe todas as credenciais; senha do admin é "admin123" em claro.
Recommendation: Hash com `werkzeug.security.generate_password_hash` e verificação com `check_password_hash`. (Playbook TX-03)

### [CRITICAL] Arbitrary SQL Execution Endpoint
File: `app.py:59-78`
Evidence: `@app.route("/admin/query", methods=["POST"]) ... cursor.execute(query)` onde `query` vem do body.
Impact: Qualquer cliente pode executar SELECT/INSERT/UPDATE/DELETE/DROP arbitrário — RCE sobre o DB.
Recommendation: Deletar o endpoint inteiramente; substituir por endpoints tipados de métricas/admin. (Playbook TX-04)

### [CRITICAL] Unauthenticated DB Reset Endpoint
File: `app.py:47-57`
Evidence: `@app.route("/admin/reset-db", methods=["POST"]) ... DELETE FROM itens_pedido; DELETE FROM pedidos; ...`
Impact: Qualquer cliente apaga todos os dados sem autenticação. Denial of data.
Recommendation: Remover endpoint público; mover seed/reset para script CLI separado. (Playbook TX-04)

### [CRITICAL] God File — models.py
File: `models.py:1-315`
Evidence: Um único arquivo concentra acesso a dados de 4 domínios (produtos, usuários, pedidos, relatórios) + cálculo de descontos + manipulação de estoque.
Impact: Qualquer mudança ameaça funcionalidades não-relacionadas; impossível testar em isolamento; bloqueia trabalho paralelo.
Recommendation: Dividir em `models/produto_model.py`, `models/usuario_model.py`, `models/pedido_model.py`; mover regras de negócio para `controllers/`. (Playbook TX-05)

### [CRITICAL] Sensitive Data Leak in Response
File: `models.py:79-87`, `controllers.py:128-134`, `controllers.py:284-291`
Evidence: `get_todos_usuarios()` retorna `senha`; `/health` expõe `"secret_key": "minha-chave-super-secreta-123"`.
Impact: API entrega o hash/senha de todos os usuários em texto plano e o SECRET_KEY no health-check.
Recommendation: Remover `senha`/`secret_key` dos serializers; criar `_safe_dict()` que omite campos sensíveis. (Playbook TX-10)

### [HIGH] Business Logic in Controllers
File: `controllers.py:24-62, 64-96, 188-220, 237-256`
Evidence: Handler `criar_produto` mistura validação, persistência e respostas em 38 linhas; `criar_pedido` despacha notificações por `print` e formata HTTP.
Impact: Regras de negócio (validações, cálculo de pedido, notificações) ficam presas no `controllers.py` HTTP, impedindo reuso e testes unitários.
Recommendation: Extrair regras para `controllers/<dominio>_controller.py` e deixar rotas apenas com parse → delegate → respond. (Playbook TX-06)

### [HIGH] Tight Coupling / No Dependency Injection
File: `models.py:1-2, 4-5, ...`, `controllers.py:1-3`, `app.py:1-4`
Evidence: Todos os módulos importam `from database import get_db` e chamam direto — não há composition root.
Impact: Impossível injetar mock de DB em testes; mudar de SQLite para outro banco quebra arquivos espalhados.
Recommendation: Criar `infrastructure/database.py` com factory; injetar conexão via construção dos controllers. (Playbook TX-07)

### [HIGH] Global Mutable State
File: `database.py:4-10`
Evidence: `db_connection = None` (módulo-level); função `get_db()` mutaciona o global e retorna singleton com `check_same_thread=False`.
Impact: Conexão única compartilhada entre threads/requests sem locking; corrupção sob concorrência.
Recommendation: Encapsular em `Database` class instanciada pelo composition root; abrir conexão por request quando possível. (Playbook TX-08)

### [HIGH] Missing Centralized Error Handling
File: `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, ...` (todos os handlers)
Evidence: Cada handler tem `try/except Exception as e: return jsonify({"erro": str(e)}), 500` — vaza traceback e mensagens internas.
Impact: Respostas de erro inconsistentes; vazamento de detalhes internos (estrutura do DB, paths); duplicação massiva.
Recommendation: Centralizar em `middlewares/error_handler.py` com `@app.errorhandler` por tipo. Controllers podem lançar `AppError("...", 404)`. (Playbook TX-09)

### [MEDIUM] N+1 Queries in Report Endpoints
File: `models.py:171-201, 203-233`
Evidence: `get_pedidos_usuario` e `get_todos_pedidos` iteram pedidos e fazem 2 queries por pedido (itens + nome do produto) → ~2N+1 queries.
Impact: Endpoints `/pedidos` e `/pedidos/usuario/<id>` ficam O(N) em round-trips ao DB; já lentos com poucos dados.
Recommendation: Buscar itens com `IN (...)` e mapear em dicionário; juntar `produto.nome` via JOIN. (Playbook TX-14)

### [MEDIUM] Duplicated Validation Logic
File: `controllers.py:30-54` vs `controllers.py:73-89`
Evidence: Blocos idênticos de validação (`if "nome" not in dados`, `if preco < 0`, `if estoque < 0`, length checks) entre `criar_produto` e `atualizar_produto`.
Impact: Mudança em regra de validação precisa ser feita em 2+ lugares — fonte certa de drift de regras.
Recommendation: Extrair para `validators.validate_produto(payload, partial=False)`. (Playbook TX-15)

### [MEDIUM] Missing Input Validation
File: `controllers.py:146-165, 167-186`
Evidence: `criar_usuario` e `login` não validam formato de email nem força da senha; aceita qualquer string.
Impact: Aceita emails malformados e senhas vazias/triviais; valida apenas presença, não estrutura.
Recommendation: Validar email com regex/lib `email_validator`; aplicar regra de comprimento mínimo de senha. (Playbook TX-15)

### [LOW] Magic Numbers / Thresholds
File: `models.py:256-262`
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1; elif faturamento > 5000: ...`
Impact: Faixas de desconto sem nome — qualquer mudança requer reler/entender a função inteira.
Recommendation: Extrair `DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]` em constante de módulo. (Playbook TX-17)

### [LOW] Print Statements as Logging
File: `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 248-250, 257-258`, `app.py:56, 83-86`
Evidence: `print("Listando " + str(len(produtos)) + " produtos")` espalhado em controllers e startup.
Impact: Sem níveis (info vs error), sem estrutura, sem possibilidade de filtrar em produção.
Recommendation: Usar `logging.getLogger("app")` com formatter padronizado. (Playbook TX-19)

### [LOW] Broad Exception Swallowing
File: `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, ...`
Evidence: Cada handler captura `Exception` genericamente, retornando o `str(e)` ao cliente.
Impact: Erros específicos (ex: integridade do DB vs falha de rede) são tratados igual; clientes recebem mensagens internas.
Recommendation: Capturar exceções específicas próximas ao raise; deixar genéricas para o error handler centralizado. (Playbook TX-20)

================================
Total: 17 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
