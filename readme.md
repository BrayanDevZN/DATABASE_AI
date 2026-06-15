# DataPilot Database API

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Polars](https://img.shields.io/badge/Polars-DataFrames-CD792C?style=for-the-badge&logo=polars&logoColor=white)](https://pola.rs/)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Railway](https://img.shields.io/badge/Railway-Deploy-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app/)

API principal de persistencia e operacao do DataPilot. Este servico centraliza contas, autenticacao, conversas, fontes de dados, dashboards, graficos, colaboracoes, convites, notificacoes e sincronizacao com a API de IA.

Apesar do nome `DATABASE`, este repositorio nao e apenas uma camada de banco. Ele e o backend operacional do SaaS: recebe comandos do frontend, valida identidade, salva entidades do produto, controla permissoes e mantem a ponte entre dados cadastrados pelo usuario e dashboards gerados pelo agente de IA.

## Indice

- [Visao geral](#visao-geral)
- [Como a plataforma funciona](#como-a-plataforma-funciona)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Dominios da API](#dominios-da-api)
- [Fluxos principais](#fluxos-principais)
- [Autenticacao](#autenticacao)
- [Rotas](#rotas)
- [Fontes de dados](#fontes-de-dados)
- [Dashboards e graficos](#dashboards-e-graficos)
- [Colaboracao e permissoes](#colaboracao-e-permissoes)
- [Variaveis de ambiente](#variaveis-de-ambiente)
- [Como executar](#como-executar)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Seguranca e confiabilidade](#seguranca-e-confiabilidade)
- [Resumo tecnico para recrutadores](#resumo-tecnico-para-recrutadores)

## Visao geral

O DataPilot e um SaaS de Business Intelligence com IA. A API `DATABASE` e responsavel por manter o estado do produto: usuarios, sessoes, fontes, dashboards, graficos, convites e notificacoes.

Responsabilidades principais:

- criar contas com validacao por codigo de e-mail;
- autenticar usuarios e emitir JWT;
- validar token e recuperar dados do usuario autenticado;
- atualizar nome, username, foto de perfil e senha;
- excluir conta e dados relacionados;
- persistir conversas e mensagens usadas pelo chat da IA;
- cadastrar fontes por arquivo, API externa ou banco SQL;
- normalizar dados tabulares usando Polars;
- salvar dashboards e graficos gerados pelo AI Agent;
- atualizar dashboards quando uma fonte vinculada muda;
- compartilhar dashboards entre usuarios com niveis de permissao;
- gerenciar convites, notificacoes e pessoas com acesso;
- chamar a API de IA para refresh automatico de dashboards.

## Como a plataforma funciona

```text
Frontend React
    |
    | Login, fontes, dashboards, colaboracoes
    v
DataPilot Database API
    |
    +--> PostgreSQL
    |       - usuarios
    |       - validacoes
    |       - conversas
    |       - fontes
    |       - dashboards
    |       - graficos
    |       - colaboracoes
    |       - notificacoes
    |
    +--> AI Agent API
            - refresh de dashboard
            - recalculo de analises
```

Fluxo de valor:

```text
Usuario cria conta
    -> cadastra fonte de dados
    -> frontend pede dashboard para a IA
    -> AI Agent gera analise e graficos
    -> Database API salva dashboard e charts
    -> usuario customiza, compartilha e atualiza
```

## Arquitetura

```text
api/routes.py
    |
    +--> api/model/
    |       +--> model_accounts.py
    |       +--> model_conversation.py
    |       +--> model_data_source.py
    |       +--> model_charts.py
    |       +--> model_collaboration.py
    |
    +--> auth/
    |       +--> jwt.py
    |       +--> hash.py
    |       +--> manager_auth.py
    |       +--> auth_sender.py
    |
    +--> app/app_accounts/
    +--> app/app_conversations/
    +--> app/app_data_sources/
    +--> app/app_charts/
    +--> app/app_collaborations/
    |
    +--> connect/
            +--> database.py
            +--> manager_database.py
```

### Padrao interno

| Camada | Responsabilidade |
| --- | --- |
| `api/routes.py` | Define endpoints, CORS, leitura de arquivos, validacao de token e orquestracoes de alto nivel. |
| `api/model/` | Schemas Pydantic dos payloads de entrada. |
| `auth/` | JWT, hash de senha, validacao de login e envio de codigos por e-mail. |
| `connect/` | Conexao com PostgreSQL. |
| `app/app_accounts/` | Regras de usuario, perfil, senha e exclusao de conta. |
| `app/app_conversations/` | Conversas e mensagens do chat. |
| `app/app_data_sources/` | CRUD de fontes de dados. |
| `app/app_charts/` | Dashboards, graficos, configuracoes e refresh. |
| `app/app_collaborations/` | Compartilhamento, permissoes, convites e notificacoes. |

## Tecnologias

| Tecnologia | Uso no projeto |
| --- | --- |
| Python | Linguagem principal da API. |
| FastAPI | Framework HTTP, rotas, FormData, upload e middlewares. |
| Uvicorn | Servidor ASGI usado em desenvolvimento e deploy. |
| Pydantic | Validacao dos contratos de entrada. |
| PostgreSQL | Banco relacional principal. |
| SQLAlchemy | Execucao de queries e conexoes com bancos externos. |
| psycopg / psycopg2 | Drivers PostgreSQL. |
| Polars | Leitura, limpeza e normalizacao de CSV, Excel, JSON e dados externos. |
| python-jose | Criacao e decodificacao de JWT. |
| bcrypt | Hash e verificacao de senhas. |
| Resend | Envio de codigos transacionais por e-mail. |
| Requests | Chamada para API de IA e APIs externas. |
| python-multipart | Recebimento de uploads via FormData. |
| Railway | Deploy e execucao em producao. |

## Dominios da API

| Dominio | O que resolve |
| --- | --- |
| Accounts | Cadastro, login, perfil, senha, token e exclusao de conta. |
| Conversations | Conversas e mensagens usadas pelo chat de IA. |
| Data Sources | Fontes de dados por arquivo, API externa ou banco SQL. |
| Dashboards | Criacao, listagem, leitura, exclusao, refresh e configuracoes de graficos. |
| Collaborations | Compartilhamento de dashboards e fontes com permissoes. |
| Notifications | Convites, atualizacoes automaticas e avisos para usuarios. |
| AI Integration | Recalculo automatico de dashboards vinculados a fontes sincronizadas. |

## Fluxos principais

### 1. Criacao de conta

```text
POST /env_code_create
    -> gera codigo de 6 digitos
    -> envia e-mail via Resend
    -> salva em validation_account

POST /create_user
    -> valida codigo
    -> cria usuario com senha em bcrypt
    -> retorna token de login
```

### 2. Login

```text
POST /login
    -> busca usuario por e-mail
    -> compara senha com hash
    -> gera JWT com user_id, email, role e status
```

### 3. Criacao de fonte

```text
POST /data-source/create
    -> valida JWT
    -> recebe arquivo, API externa ou banco SQL
    -> normaliza dados com Polars
    -> salva file_data, row_count e column_count
```

### 4. Geracao de dashboard

```text
AI Agent gera analise
    -> POST /dashboard/create
    -> POST /dashboard/chart/create
    -> frontend abre dashboard salvo
```

### 5. Atualizacao de fonte com dashboards vinculados

```text
PATCH /data-source/update
    -> atualiza a fonte
    -> identifica dashboards vinculados
    -> pode marcar dashboards como desatualizados
    -> frontend ou rotina de sync chama refresh
```

### 6. Sincronizacao automatica

```text
POST /data-sources
    -> detecta fontes vencidas por refresh_interval_days
    -> recarrega dados da fonte
    -> busca dashboards vinculados
    -> chama AI_URL /dashboard/refresh/analyze
    -> salva refresh com ManagerCharts
    -> cria notificacoes de sucesso ou falha
```

## Autenticacao

A API usa JWT assinado com `SECRET`. O token e enviado no body JSON ou em `multipart/form-data`, dependendo da rota.

Exemplo:

```json
{
  "token": "JWT_DO_USUARIO"
}
```

O helper `get_user_id_from_token`:

- decodifica o JWT;
- extrai `user_id`;
- confirma que o usuario ainda existe;
- retorna `401` quando a sessao esta invalida ou expirada.

## Rotas

### Accounts e autenticacao

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/env_code_create` | Envia codigo de verificacao para criacao de conta. |
| `POST` | `/valid_user` | Verifica se um e-mail ja esta cadastrado. |
| `POST` | `/valid_username` | Verifica disponibilidade de username. |
| `POST` | `/create_user` | Cria usuario validando codigo enviado por e-mail. |
| `POST` | `/login` | Autentica usuario e retorna token. |
| `POST` | `/valid_token` | Valida JWT. |
| `POST` | `/me` | Retorna dados do usuario autenticado. |
| `POST` | `/env_pass` | Envia codigo de recuperacao/troca de senha. |
| `POST` | `/check_pass` | Confirma senha atual antes de alterar. |
| `PATCH` | `/update_auth_pass` | Redefine senha com codigo. |
| `PATCH` | `/update_pass` | Atualiza senha no fluxo autenticado. |
| `PATCH` | `/update_name` | Atualiza nome. |
| `PATCH` | `/update_username` | Atualiza username. |
| `PATCH` | `/update_profile_image` | Atualiza foto de perfil. |
| `DELETE` | `/delete_user` | Exclui conta e dados relacionados. |

Exemplo de login:

```json
{
  "email": "usuario@email.com",
  "password": "senha_segura"
}
```

Exemplo de resposta:

```json
{
  "exists": true,
  "status": true,
  "token": "JWT",
  "name": "Nome",
  "username": "usuario",
  "profile_image": null,
  "gender": "masculino",
  "age": 25
}
```

### Conversations

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/conversation/create` | Cria conversa vazia com titulo. |
| `POST` | `/conversation` | Salva mensagem de usuario ou assistente. |
| `POST` | `/conversations` | Lista conversas do usuario. |
| `POST` | `/conversation/messages` | Lista mensagens de uma conversa. |
| `POST` | `/conversation/user` | Lista conversas agrupadas por usuario autenticado. |
| `DELETE` | `/conversation` | Remove conversa. |

Exemplo:

```json
{
  "token": "JWT_DO_USUARIO",
  "conversation_id": 1,
  "role": "user",
  "content": "Analise meus dados"
}
```

### Data Sources

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/data-source/create` | Cria fonte por arquivo, API externa ou banco SQL. |
| `POST` | `/data-sources` | Lista fontes proprias e compartilhadas, alem de sincronizar fontes vencidas. |
| `POST` | `/data-source` | Retorna fonte especifica. |
| `POST` | `/data-source/linked-dashboards` | Lista dashboards vinculados a uma fonte. |
| `PATCH` | `/data-source/update` | Atualiza os dados ou conexao da fonte. |
| `PATCH` | `/data-source/rename` | Renomeia fonte. |
| `DELETE` | `/data-source` | Remove fonte. |

### Dashboards e charts

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/dashboards` | Lista dashboards proprios, compartilhados e convites. |
| `POST` | `/dashboard` | Busca dashboard com graficos. |
| `POST` | `/dashboard/create` | Cria dashboard persistido. |
| `POST` | `/dashboard/chart/create` | Cria grafico dentro de um dashboard. |
| `POST` | `/dashboard/refresh/finish` | Salva resultado de refresh gerado pela IA. |
| `POST` | `/dashboard/chart/settings` | Salva configuracoes visuais de graficos. |
| `DELETE` | `/dashboard` | Exclui dashboard. |

### Collaborations

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/users/search` | Busca usuarios por nome ou username. |
| `POST` | `/collaborations` | Retorna visao geral de dashboards, compartilhados e convites. |
| `POST` | `/dashboard/collaborations` | Lista colaboradores de um dashboard. |
| `POST` | `/dashboard/collaboration/share` | Envia convite de compartilhamento. |
| `PATCH` | `/dashboard/collaboration` | Atualiza permissao de colaborador. |
| `DELETE` | `/dashboard/collaboration` | Remove colaboracao. |
| `POST` | `/dashboard/collaboration/respond` | Aceita ou recusa convite. |
| `POST` | `/dashboard/access` | Lista pessoas com acesso ao dashboard. |

### Notifications

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/notifications` | Lista notificacoes do usuario. |
| `PATCH` | `/notification/read` | Marca notificacao como lida. |

## Fontes de dados

A API aceita tres tipos de fonte.

| `source_type` | Entrada | Tratamento |
| --- | --- | --- |
| `file` | CSV, XLS, XLSX ou JSON | Leitura com Polars, limpeza de nulos e conversao para lista de registros. |
| `web` | URL de API ou payload JSON | Requisicao HTTP ou payload enviado pelo frontend, normalizado como tabela. |
| `database` | Connection string + query `SELECT` | Execucao via SQLAlchemy e conversao para registros. |

Campos de `multipart/form-data`:

| Campo | Obrigatorio | Descricao |
| --- | --- | --- |
| `token` | Sim | JWT do usuario. |
| `name` | Sim na criacao | Nome visivel da fonte. |
| `source_type` | Nao | `file`, `web` ou `database`. Padrao: `file`. |
| `file` | Para `file` | Arquivo CSV, XLS, XLSX ou JSON. |
| `api_url` | Para `web` | URL da API externa. |
| `api_payload` | Opcional | JSON ja carregado pelo frontend. |
| `database_url` | Para `database` | String de conexao. |
| `query` | Para `database` | Query SQL somente `SELECT`. |
| `refresh_interval_days` | Opcional | Intervalo de sincronizacao automatica. |
| `refresh_dashboards` | Update | Marca dashboards vinculados para atualizacao. |

## Dashboards e graficos

O dashboard e salvo em duas etapas:

1. `/dashboard/create` cria a entidade principal.
2. `/dashboard/chart/create` persiste cada grafico com dados e configuracao.

Configuracoes suportadas em `/dashboard/chart/settings`:

- `chart_color`;
- `chart_background`;
- `x_axis_text_color`;
- `y_axis_text_color`;
- `grid_color`;
- `grid_style`;
- `bar_style`;
- `show_legend`;
- `pie_colors`.

Refresh:

```text
AI Agent
    -> POST /dashboard/refresh/analyze
Database API
    -> POST /dashboard/refresh/finish
    -> substitui graficos
    -> salva nova analise
    -> atualiza prompt quando enviado
```

## Colaboracao e permissoes

Permissoes aceitas:

| Permissao | Significado |
| --- | --- |
| `read` | Pode visualizar dashboard. |
| `edit` | Pode editar configuracoes permitidas. |
| `full` | Pode atualizar analises e acessar recursos mais amplos. |

O backend verifica acesso antes de listar fontes, dashboards e colaboradores. Fontes compartilhadas tambem sao resolvidas a partir dos dashboards aos quais o usuario possui acesso.

## Variaveis de ambiente

As variaveis sao carregadas por `core/config.py`, que le `core/.env`.

| Variavel | Obrigatoria | Descricao |
| --- | --- | --- |
| `DB_NAME` | Sim | Nome do banco PostgreSQL. |
| `DB_USER` | Sim | Usuario do banco. |
| `DB_PORT` | Sim | Porta do banco. |
| `DB_HOST` | Sim | Host do banco. |
| `DB_PASSWORD` | Sim | Senha do banco. |
| `SECRET` | Sim | Chave usada para assinar JWT. |
| `KEY_EMAIL` | Sim para e-mail | Chave da Resend. |
| `EMAIL_USER` | Opcional | E-mail/remetente configurado. |
| `URL_EMAIL` | Opcional | URL relacionada ao fluxo de e-mail. |
| `AI_URL` | Nao | URL da API de IA. Padrao: `https://web-production-40ead.up.railway.app`. |
| `PORT` | Deploy | Porta usada pelo provedor de deploy. |

Exemplo:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PORT=5432
DB_HOST=localhost
DB_PASSWORD=senha
SECRET=uma_chave_segura
KEY_EMAIL=re_...
AI_URL=http://localhost:8001
```

## Como executar

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

Documentacao local:

```text
http://localhost:8000/docs
```

Producao:

```text
web: uvicorn api.routes:app --host 0.0.0.0 --port $PORT
```

## Estrutura de pastas

```text
DATABASE/
|-- api/
|   |-- routes.py
|   `-- model/
|       |-- model_accounts.py
|       |-- model_charts.py
|       |-- model_collaboration.py
|       |-- model_conversation.py
|       `-- model_data_source.py
|-- app/
|   |-- app_accounts/
|   |-- app_charts/
|   |-- app_collaborations/
|   |-- app_conversations/
|   `-- app_data_sources/
|-- auth/
|   |-- auth_sender.py
|   |-- dependences.py
|   |-- hash.py
|   |-- jwt.py
|   `-- manager_auth.py
|-- connect/
|   |-- database.py
|   `-- manager_database.py
|-- core/
|   `-- config.py
|-- Procfile
|-- requirements.txt
`-- readme.md
```

## Seguranca e confiabilidade

- Senhas sao armazenadas com hash bcrypt.
- JWT centraliza identidade e permissao basica.
- Rotas sensiveis resolvem `user_id` a partir do token, nao do frontend.
- Recuperacao e criacao de conta usam codigos temporarios.
- Fontes de banco aceitam apenas queries iniciadas com `SELECT`.
- Dados tabulares sao normalizados para JSON seguro antes da resposta.
- Valores `NaN`, infinitos e datas sao convertidos para formatos seguros.
- Dashboards vinculados podem ser marcados como desatualizados quando a fonte muda.
- Falhas de refresh automatico geram notificacoes para o usuario.

## Observacoes de manutencao

- A pasta `migrations/` foi removida deste repositorio.
- Se o time retomar versionamento formal de schema, recomenda-se usar Alembic ou ferramenta equivalente.
- O CORS esta configurado com `allow_origins=["*"]`; em producao, uma evolucao natural e restringir para os dominios oficiais do frontend.
- O arquivo `requirements.txt` contem dependencias alem do nucleo da API; uma melhoria futura seria separar dependencias de runtime e desenvolvimento.

## Resumo tecnico para recrutadores

Este projeto demonstra um backend FastAPI com responsabilidades reais de produto: autenticacao, persistencia relacional, upload e normalizacao de dados, colaboracao, notificacoes, integracao entre microservicos e suporte a dashboards gerados por IA.

O ponto forte da arquitetura esta na separacao por dominio e na orquestracao entre dados do usuario, graficos persistidos e analises recalculadas pelo AI Agent. A API resolve problemas comuns de SaaS em producao: sessao expirada, permissao por recurso, dados compartilhados, refresh assincrono, tratamento de uploads, validacao de payloads e sincronizacao entre servicos.
