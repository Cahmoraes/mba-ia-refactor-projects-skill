# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## A) Análise Manual

### Projeto 1 — code-smells-project (Python/Flask, E-commerce API)

| # | Severidade | Arquivo:Linha | Problema |
|---|-----------|---------------|----------|
| 1 | CRITICAL | `app.py:7` | `SECRET_KEY = 'minha-chave-super-secreta-123'` hardcoded — qualquer leitura do source expõe a chave de sessão |
| 2 | CRITICAL | `app.py:8` | `DEBUG = True` hardcoded — expõe debugger interativo (execução de código arbitrário via browser) em produção |
| 3 | CRITICAL | `app.py:59-78` | Endpoint `/admin/query` executa SQL arbitrário sem autenticação — permite dump completo do banco e DROP TABLE |
| 4 | CRITICAL | `models.py:28-29` | Queries com concatenação de string: `f"WHERE nome = '{nome}'"` — SQL Injection direto |
| 5 | CRITICAL | `models.py:110` | Senhas armazenadas em texto plano: `cursor.execute("INSERT ... VALUES (?)", (senha,))` |
| 6 | HIGH | `models.py:1-350` | God file: lógica de negócio, queries, validação e formatação de 4 domínios num único arquivo de 350 LOC |
| 7 | HIGH | `app.py:1-80` | Business logic + routing no mesmo arquivo; controladores sem separação do modelo |
| 8 | MEDIUM | `models.py:220-260` | N+1: loop em pedidos + query por item dentro do loop (O(N) queries extras) |
| 9 | MEDIUM | `models.py:145-180` | Validação duplicada em create_produto e update_produto |
| 10 | LOW | `models.py:58` | Magic number `0.1` para desconto sem constante nomeada |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS checkout)

| # | Severidade | Arquivo:Linha | Problema |
|---|-----------|---------------|----------|
| 1 | CRITICAL | `src/utils.js:1-7` | Credenciais hardcoded: DB password, payment gateway key e SMTP credentials no código |
| 2 | CRITICAL | `src/utils.js:17-22` | Hashing inseguro: base64 de senha — trivialmente reversível, não é hash criptográfico |
| 3 | CRITICAL | `src/AppManager.js:1-78` | God class: routing + gerenciamento de DB + lógica de negócio em uma única classe de 78 LOC |
| 4 | CRITICAL | `src/AppManager.js:45` | Número do cartão de crédito logado em claro: `console.log('card:', card)` |
| 5 | CRITICAL | `src/AppManager.js:60-70` | DELETE /users sem cascade: orphan records de enrollments e payments no banco |
| 6 | HIGH | `src/AppManager.js:30-50` | Business logic dentro de route handler (checkout): validação, hash, DB, pagamento tudo inline |
| 7 | HIGH | `src/AppManager.js:10` | Tight coupling: `new sqlite3.Database(':memory:')` no construtor, impossível testar com DB diferente |
| 8 | MEDIUM | `src/AppManager.js:55-65` | N+1 em financial report: query por enrollment dentro de loop de courses |
| 9 | MEDIUM | `src/AppManager.js:20-30` | Callback hell 4-5 níveis — legibilidade e tratamento de erros comprometidos |
| 10 | LOW | `src/AppManager.js:15` | Naming pobre: `u`, `e`, `p`, `c_id` como campos de payload sem mapeamento documentado |

### Projeto 3 — task-manager-api (Python/Flask, Task Manager)

| # | Severidade | Arquivo:Linha | Problema |
|---|-----------|---------------|----------|
| 1 | CRITICAL | `app.py:13` | `SECRET_KEY = 'super-secret-key-123'` hardcoded |
| 2 | CRITICAL | `models/user.py:29` | MD5 para hash de senha: sem salt, rainbow-table trivial, md5 é hash genérico não KDF |
| 3 | CRITICAL | `models/user.py:16-25` | `to_dict()` inclui campo `password` — hash exposto em toda resposta de usuário |
| 4 | CRITICAL | `services/notification_service.py:9-10` | SMTP credentials hardcoded: `email_password = 'senha123'` |
| 5 | CRITICAL | `routes/user_routes.py:210` | Token fake: `'fake-jwt-token-' + str(user.id)` — qualquer caller forja autenticação |
| 6 | HIGH | `routes/task_routes.py:85-154` | Validação + queries + cálculos diretamente no handler — 70 LOC em uma única função de rota |
| 7 | HIGH | `services/notification_service.py` | NotificationService nunca importado nem usado — dead code que deveria estar integrado |
| 8 | MEDIUM | `routes/task_routes.py:41-56` | N+1: `User.query.get()` + `Category.query.get()` dentro do loop de tasks em GET /tasks |
| 9 | MEDIUM | `routes/report_routes.py:53-68` | N+1: `Task.query.filter_by(user_id=u.id).all()` por usuário em user_productivity loop |
| 10 | LOW | `app.py:34` | `debug=True` hardcoded — expõe debugger interativo em produção |

---

## B) Construção da Skill

### Estrutura do SKILL.md

O SKILL.md foi projetado como um **prompt orquestrador** com 3 fases sequenciais obrigatórias:

```
Phase 1 → ANÁLISE   (leitura, detecção de stack, resumo impresso)
Phase 2 → AUDITORIA  (cruzar código com catálogo, gerar relatório, pedir confirmação)
Phase 3 → REFATORAÇÃO (transformações, validação de boot + endpoints)
```

Decisão central: **Phase 2 Gate** — a skill para e aguarda `y/n` antes de qualquer escrita. Isso garante revisão humana dos findings antes de modificar código de produção.

### Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `analysis-heuristics.md` | Detecção de linguagem (extensões + lockfiles), framework, DB, classificação de arquitetura |
| `anti-patterns-catalog.md` | 20 anti-patterns (AP-01 a AP-20) com sinais de detecção e severity CRITICAL/HIGH/MEDIUM/LOW |
| `report-template.md` | Template exato do relatório com cabeçalho, formato de cada finding, tabela de summary |
| `mvc-guidelines.md` | Responsabilidades de cada camada, layouts de referência Python/Flask e Node.js/Express, regras para projetos já parcialmente organizados |
| `refactoring-playbook.md` | TX-01 a TX-20: padrões de transformação com exemplos before/after em código |

### Agnóstico de tecnologia

A skill não contém código Python ou Node.js no SKILL.md — apenas instruções de detecção heurística. Os arquivos de referência têm seções explícitas para cada stack. A skill decide qual layout aplicar na Phase 3 baseado no que detectou na Phase 1 (Python: `config/settings.py` + Blueprints; Node.js: `src/config/index.js` + Express Router + async/await).

### Anti-patterns selecionados

Critério de seleção: **impacto arquitetural + frequência real em projetos legados**. Os 20 anti-patterns cobrem:
- 6 CRITICAL (segurança, arquitetura fatal)
- 5 HIGH (SOLID violations, acoplamento)
- 6 MEDIUM (performance, duplicação, validação)
- 3 LOW (legibilidade, nomenclatura)

AP-16 (Deprecated APIs) foi incluído especificamente para cobrir `Task.query.get()` (SQLAlchemy 2.0 deprecated) e o Callback Hell do Node.js como padrão obsoleto.

### Desafios e soluções

| Desafio | Solução |
|---------|---------|
| Projetos com estrutura parcial (project 3) | `mvc-guidelines.md` tem seção "Partially Organized Projects": manter models/ e routes/ existentes, adicionar controllers/ e config/ faltantes |
| N+1 em Python/SQLAlchemy vs Node/raw-sqlite3 | Playbook com TX específicas: `joinedload()` para SQLAlchemy; JOIN SQL direto para raw sqlite3 |
| Callback hell → async/await | TX-13 no playbook com padrão `util.promisify` + wrapper Promise para sqlite3 |
| Cascade delete (Node.js sem ORM) | TX explícita: deletar payments → enrollments → user em sequência |

---

## C) Resultados

### Summary de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project | 7 | 4 | 3 | 3 | 17 |
| ecommerce-api-legacy | 5 | 4 | 4 | 3 | 16 |
| task-manager-api | 5 | 3 | 4 | 4 | 16 |

### Comparação Antes/Depois

#### Projeto 1 — code-smells-project

**Antes:**
```
code-smells-project/
├── app.py          (routing + config + admin SQL endpoint)
├── models.py       (God file: 4 domínios, SQL injection, texto plano)
├── database.py     (conexão global)
└── controllers.py  (lógica duplicada)
```

**Depois:**
```
code-smells-project/
├── app.py                    (composition root, create_app())
├── config/settings.py        (env-based, sem hardcoded)
├── infrastructure/database.py (Database class, execute(q, params))
├── models/{produto,usuario,pedido}_model.py
├── controllers/{produto,usuario,pedido,relatorio,health}_controller.py
├── routes/{produto,usuario,pedido,relatorio,health}_routes.py
├── middlewares/{error_handler,validators}.py
└── .env.example
```

#### Projeto 2 — ecommerce-api-legacy

**Antes:**
```
src/
├── AppManager.js  (God class: routing + DB + business logic)
└── utils.js       (hardcoded credentials + insecure hash)
```

**Depois:**
```
src/
├── app.js                    (bootstrap() composition root)
├── config/index.js           (env-based settings)
├── infrastructure/database.js (Promise-wrapped sqlite3)
├── utils/{crypto,logger}.js  (bcrypt hash, structured logger)
├── middlewares/{errorHandler,validate}.js
├── models/{user,course,enrollment,payment,auditLog}Model.js
├── controllers/{checkout,report,user}Controller.js
└── routes/{checkout,report,user}Routes.js
```

#### Projeto 3 — task-manager-api

**Antes:**
```
task-manager-api/
├── app.py           (hardcoded SECRET_KEY, debug=True)
├── models/user.py   (MD5 hash, password in to_dict)
├── routes/          (fat handlers, N+1 queries, bare except)
├── services/notification_service.py  (hardcoded SMTP, never used)
└── (sem config/, controllers/, middlewares/)
```

**Depois:**
```
task-manager-api/
├── app.py                    (create_app() factory, env-based config)
├── config/settings.py        (todos os settings via env)
├── controllers/{task,user,report}_controller.py
├── middlewares/error_handler.py
├── models/user.py            (werkzeug hash, to_public() sem password)
├── services/notification_service.py  (SMTP via config, integrado)
├── routes/                   (thin handlers, ~10 LOC cada)
└── .env.example
```

### Checklist de Validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python 3)
- [x] Framework detectado corretamente (Flask)
- [x] Domínio da aplicação descrito corretamente (E-commerce: produtos, pedidos, usuários)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] 17 findings identificados (mínimo 5 ✓)
- [x] API deprecated não aplicável (Flask 3.1.1 sem APIs obsoletas detectadas)
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura MVC com config/, models/, controllers/, routes/, middlewares/
- [x] SECRET_KEY e DEBUG lidos de variáveis de ambiente
- [x] Models isolam acesso a dados (queries parametrizadas)
- [x] Routes são thin handlers
- [x] Controllers concentram lógica de negócio
- [x] Error handler centralizado (AppError + handlers 404/405/500)
- [x] Entry point claro (create_app() em app.py)
- [x] Aplicação inicia sem erros (`python app.py` → boot OK)
- [x] Endpoints respondem: /health, /produtos, /usuarios (sem password), /login, /pedidos, /relatorios/vendas

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Node.js)
- [x] Framework detectado corretamente (Express)
- [x] Domínio da aplicação descrito corretamente (LMS checkout: cursos, matrículas, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade (3 src files)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] 16 findings identificados
- [x] AP-16 (Callback hell + deprecated sqlite3 API) incluído
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura MVC completa
- [x] Credenciais removidas de utils.js, lidas de process.env
- [x] bcryptjs substitui base64 hash
- [x] AppManager.js eliminado, responsabilidades separadas
- [x] Cascade delete implementado (payments → enrollments → user)
- [x] Error handler centralizado (AppError + errorHandler middleware)
- [x] bootstrap() async em app.js
- [x] Aplicação inicia sem erros
- [x] Endpoints respondem: /health, POST /api/checkout (payload moderno + legado), GET /api/admin/financial-report, DELETE /api/users/:id

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python 3)
- [x] Framework detectado corretamente (Flask + SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (Task Manager: tasks, users, categories, reports)
- [x] Número de arquivos analisados condiz com a realidade (~12 arquivos)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] 16 findings identificados
- [x] AP-16 (Task.query.get() deprecated SQLAlchemy 2.0) incluído
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] controllers/ e config/ adicionados ao projeto parcialmente organizado
- [x] SECRET_KEY e DEBUG lidos de variáveis de ambiente
- [x] werkzeug substitui MD5 em models/user.py
- [x] to_public() exclui password das respostas
- [x] NotificationService integrado ao task_controller (wired via DI no create_app)
- [x] N+1 eliminado com joinedload(Task.user, Task.category)
- [x] Task.query.get() substituído por db.session.get(Task, id)
- [x] Error handler centralizado (AppError + register_error_handlers)
- [x] create_app() factory em app.py
- [x] Aplicação inicia sem erros
- [x] Endpoints respondem: /health, GET /tasks (com user_name/category_name), POST /tasks, GET /users (sem password), POST /login, GET /reports/summary

### Logs de Boot

**Projeto 1:**
```
$ python app.py
 * Running on http://127.0.0.1:5000
$ curl http://localhost:5000/health
{"db_stats":{"categorias":0,"pedidos":0,"produtos":10,"usuarios":3},"status":"ok"}
```

**Projeto 2:**
```
$ npm start
{"level":"info","event":"server.start","port":3000}
$ curl http://localhost:3000/health
{"status":"ok"}
```

**Projeto 3:**
```
$ python seed.py
Seed concluído com sucesso!
  3 usuários / 4 categorias / 10 tasks
$ python app.py
 * Running on http://127.0.0.1:5000
$ curl http://localhost:5000/health
{"status":"ok","timestamp":"2026-05-27 12:06:06.762382"}
```

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (`claude --version`)
- Python 3.10+ e `pip` (Projetos 1 e 3)
- Node.js 18+ e `npm` (Projeto 2)

### Executar a Skill

```bash
# Projeto 1 — code-smells-project
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api
cd ../task-manager-api
claude "/refactor-arch"
```

### Executar os Projetos Refatorados

#### Projeto 1 — code-smells-project
```bash
cd code-smells-project
cp .env.example .env        # edite com SECRET_KEY real
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

#### Projeto 2 — ecommerce-api-legacy
```bash
cd ecommerce-api-legacy
cp .env.example .env        # edite PAYMENT_GATEWAY_KEY e SMTP_USER
npm install
npm start
# → http://localhost:3000
```

#### Projeto 3 — task-manager-api
```bash
cd task-manager-api
cp .env.example .env        # edite SECRET_KEY e opcionalmente SMTP_*
pip install -r requirements.txt
python seed.py              # popula o banco (obrigatório antes do 1º start)
python app.py
# → http://localhost:5000
```

### Validar que a Refatoração Funcionou

```bash
# Projeto 1
curl http://localhost:5000/health           # deve retornar {"status":"ok",...}
curl http://localhost:5000/produtos         # deve listar produtos (sem SQL injection)
curl http://localhost:5000/usuarios         # NÃO deve conter campo "senha" ou "senha_hash"

# Projeto 2
curl http://localhost:3000/health
curl -X POST http://localhost:3000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test","email":"t@t.com","password":"abc","courseId":1,"card":"4111222233334444"}'
# deve retornar {"enrollment_id":...}

# Projeto 3
curl http://localhost:5000/health
curl http://localhost:5000/tasks            # deve incluir "user_name" e "overdue" (via joinedload)
curl http://localhost:5000/users            # NÃO deve conter campo "password"
curl http://localhost:5000/reports/summary  # deve conter user_productivity sem N+1
```

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.