# DataPilot Accounts, Data Sources and Dashboards API

API principal de persistencia do DataPilot. Este servico concentra autenticacao, usuarios, conversas, fontes de dados, dashboards, graficos, colaboracoes e notificacoes. Ele tambem faz a ponte entre dados cadastrados pelo usuario e a API de IA responsavel por gerar analises.

## Visao geral

O projeto `DATABASE` e o backend operacional da plataforma. Apesar do nome, ele nao e apenas banco de dados: e uma API FastAPI completa para gerenciar o estado do produto.

Principais responsabilidades:

- cadastro, login e validacao de usuarios;
- envio de codigos por e-mail para criacao e recuperacao de senha;
- gerenciamento de perfil, username e foto;
- persistencia de conversas e mensagens;
- criacao e atualizacao de fontes de dados;
- leitura de arquivos, APIs externas e bancos SQL;
- criacao, listagem, atualizacao e exclusao de dashboards;
- salvamento de graficos e configuracoes visuais;
- compartilhamento de dashboards com permissoes;
- notificacoes sobre convites e atualizacoes;
- sincronizacao automatica de fontes com dashboards vinculados.

## Tecnologias

| Tecnologia | Uso no projeto |
| --- | --- |
| Python | Linguagem principal |
| FastAPI | Framework HTTP da API |
| Uvicorn | Servidor ASGI |
| Pydantic | Validacao dos modelos de entrada |
| SQLAlchemy | Execucao de consultas SQL externas e suporte de persistencia |
| PostgreSQL / psycopg | Banco relacional em producao |
| Polars | Leitura e normalizacao de CSV, Excel, JSON e dados externos |
| python-jose | Criacao e leitura de JWT |
| passlib / bcrypt | Hash e verificacao de senhas |
| requests | Chamada para a API de IA e APIs externas |
| resend | Envio de e-mails transacionais |
| python-multipart | Upload de arquivos via FormData |
| Railway | Deploy da API |

## Arquitetura

```text
Cliente / Frontend
      |
      v
api/routes.py
      |
      +--> auth/
      |     +--> jwt.py
      |     +--> hash.py
      |     +--> auth_sender.py
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

O projeto segue uma separacao simples por dominio:

| Camada | Responsabilidade |
| --- | --- |
| `api/routes.py` | Define endpoints, CORS, leitura de arquivos e orquestracoes de alto nivel |
| `api/model/` | Contratos Pydantic por dominio |
| `auth/` | JWT, hash de senha e envio de codigos |
| `connect/` | Conexao e comandos de banco |
| `app/app_accounts/` | Regras de usuario, login, perfil e senha |
| `app/app_conversations/` | Conversas e mensagens |
| `app/app_data_sources/` | Fontes de dados |
| `app/app_charts/` | Dashboards, graficos e configuracoes |
| `app/app_collaborations/` | Compartilhamentos, convites e notificacoes |

## Estrutura de pastas

```text
DATABASE/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ api/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ routes.py
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ model/
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ model_accounts.py
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ model_charts.py
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ model_collaboration.py
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ model_conversation.py
Ã¢â€â€š       Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ model_data_source.py
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app_accounts/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app_charts/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app_collaborations/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app_conversations/
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ app_data_sources/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ auth/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ connect/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ core/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Procfile
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ requirements.txt
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ readme.md
```

## Variaveis de ambiente

As variaveis podem ser configuradas no ambiente local ou no provedor de deploy.

| Variavel | Obrigatoria | Descricao |
| --- | --- | --- |
| `DATABASE_URL` | Sim | URL de conexao com o banco principal da plataforma |
| `AI_URL` | Nao | URL da API de IA. Padrao: `https://web-production-40ead.up.railway.app` |
| `SECRET_KEY` ou equivalente JWT | Sim | Segredo usado para assinar tokens |
| `RESEND_API_KEY` | Sim para e-mail | Chave para envio de codigos por e-mail |
| `EMAIL_FROM` | Sim para e-mail | Remetente usado nos envios |
| `PORT` | Deploy | Porta definida pelo Railway/ambiente |

Consulte os arquivos em `auth/`, `connect/` e `core/` para nomes finais usados na sua configuracao atual.

## Como executar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

O `Procfile` de producao usa:

```text
web: uvicorn api.routes:app --host 0.0.0.0 --port $PORT
```

## Autenticacao

A autenticacao usa JWT. Na maior parte das rotas, o token e enviado no body JSON ou no `FormData` com o campo `token`.

Exemplo:

```json
{
  "token": "JWT_DO_USUARIO"
}
```

O helper `get_user_id_from_token` extrai o `user_id` do token. Quando o token e invalido, a API retorna erro de permissao ou mensagem de token invalido.

## Rotas de usuarios e autenticacao

### `POST /env_code_create`

Envia codigo de verificacao para criacao de conta.

Body:

```json
{
  "email": "usuario@email.com"
}
```

### `POST /valid_user`

Verifica se um e-mail ja existe.

Body:

```json
{
  "email": "usuario@email.com"
}
```

### `POST /valid_username`

Verifica disponibilidade de username.

Body:

```json
{
  "username": "usuario123"
}
```

### `POST /create_user`

Cria uma conta e retorna dados de autenticacao.

Body:

```json
{
  "email": "usuario@email.com",
  "password": "senha_segura",
  "name": "Nome do Usuario",
  "username": "usuario123",
  "age": 25,
  "gender": "masculino",
  "code": 123456
}
```

### `POST /login`

Autentica o usuario.

Body:

```json
{
  "email": "usuario@email.com",
  "password": "senha_segura"
}
```

### `POST /valid_token`

Valida um JWT.

Body:

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /me`

Retorna dados do usuario autenticado.

Body:

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /check_pass`

Valida a senha atual antes de altera-la.

Body:

```json
{
  "token": "JWT_DO_USUARIO",
  "current_password": "senha_atual",
  "password": "nova_senha"
}
```

### `PATCH /update_pass`

Atualiza a senha em fluxo autenticado.

Body:

```json
{
  "token": "JWT_DO_USUARIO",
  "current_password": "senha_atual",
  "password": "nova_senha"
}
```

### `POST /env_pass`

Envia codigo para recuperacao de senha. Pode receber `email` ou `token`, dependendo do fluxo.

Body:

```json
{
  "email": "usuario@email.com"
}
```

ou:

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `PATCH /update_auth_pass`

Redefine senha com codigo.

Body:

```json
{
  "email": "usuario@email.com",
  "code": 123456,
  "password": "nova_senha"
}
```

ou:

```json
{
  "token": "JWT_DO_USUARIO",
  "code": 123456,
  "password": "nova_senha"
}
```

### `PATCH /update_name`

Atualiza nome do usuario.

```json
{
  "token": "JWT_DO_USUARIO",
  "name": "Novo Nome"
}
```

### `PATCH /update_username`

Atualiza username.

```json
{
  "token": "JWT_DO_USUARIO",
  "username": "novo_username"
}
```

### `PATCH /update_profile_image`

Atualiza imagem de perfil.

```json
{
  "token": "JWT_DO_USUARIO",
  "profile_image": "base64_ou_url"
}
```

### `DELETE /delete_user`

Remove a conta do usuario e dados relacionados.

```json
{
  "token": "JWT_DO_USUARIO",
  "password": "senha_atual"
}
```

## Rotas de conversas

### `POST /conversation/create`

Cria uma conversa vazia.

```json
{
  "token": "JWT_DO_USUARIO",
  "title": "Analise de vendas"
}
```

### `POST /conversation`

Salva uma mensagem.

```json
{
  "token": "JWT_DO_USUARIO",
  "conversation_id": 1,
  "role": "user",
  "content": "Analise meus dados"
}
```

`role` aceita `user` ou `assistant`.

### `POST /conversations`

Lista conversas do usuario.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /conversation/messages`

Lista mensagens de uma conversa.

```json
{
  "token": "JWT_DO_USUARIO",
  "conversation_id": 1
}
```

### `POST /conversation/user`

Lista conversas agrupadas por usuario autenticado.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `DELETE /conversation`

Remove uma conversa.

```json
{
  "token": "JWT_DO_USUARIO",
  "conversation_id": 1
}
```

## Rotas de fontes de dados

As fontes podem ser de tres tipos:

| Tipo | Campo `source_type` | Entrada |
| --- | --- | --- |
| Arquivo | `file` | CSV, XLS, XLSX ou JSON |
| API externa | `web` | `api_url` ou `api_payload` |
| Banco SQL | `database` | `database_url` + query `SELECT` |

### `POST /data-source/create`

Cria uma fonte de dados.

Content-Type: `multipart/form-data`

Campos:

| Campo | Obrigatorio | Descricao |
| --- | --- | --- |
| `token` | Sim | JWT do usuario |
| `name` | Sim | Nome da fonte |
| `source_type` | Nao | `file`, `web` ou `database`. Padrao: `file` |
| `file` | Para `file` | Arquivo CSV/XLS/XLSX/JSON |
| `api_url` | Para `web` | URL de API externa |
| `api_payload` | Opcional | JSON ja carregado pelo frontend |
| `database_url` | Para `database` | String de conexao |
| `query` | Para `database` | Consulta SQL somente `SELECT` |
| `refresh_interval_days` | Nao | Intervalo de sincronizacao automatica |

### `POST /data-sources`

Lista fontes do usuario, fontes compartilhadas e sincroniza fontes vencidas.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /data-source`

Retorna uma fonte especifica.

```json
{
  "token": "JWT_DO_USUARIO",
  "data_source_id": 1
}
```

### `POST /data-source/linked-dashboards`

Lista dashboards vinculados a uma fonte.

```json
{
  "token": "JWT_DO_USUARIO",
  "data_source_id": 1
}
```

### `PATCH /data-source/update`

Atualiza dados de uma fonte. Tambem pode marcar dashboards vinculados como desatualizados.

Content-Type: `multipart/form-data`

Campos principais:

- `token`
- `data_source_id`
- `refresh_dashboards`
- `source_type`
- `file`
- `api_url`
- `api_payload`
- `database_url`
- `query`
- `refresh_interval_days`

### `PATCH /data-source/rename`

Renomeia uma fonte.

```json
{
  "token": "JWT_DO_USUARIO",
  "data_source_id": 1,
  "name": "Novo nome"
}
```

### `DELETE /data-source`

Remove uma fonte.

```json
{
  "token": "JWT_DO_USUARIO",
  "data_source_id": 1
}
```

## Rotas de dashboards e graficos

### `POST /dashboards`

Lista dashboards do usuario, dashboards compartilhados e convites.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /dashboard`

Busca um dashboard com seus graficos.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1
}
```

### `POST /dashboard/create`

Cria um dashboard persistido. Normalmente e chamado pela API de IA apos gerar analise.

```json
{
  "token": "JWT_DO_USUARIO",
  "title": "Dashboard Comercial",
  "prompt": "Analise vendas mensais",
  "ai_suggestion": "Resumo gerado pela IA",
  "file_name": "vendas.xlsx",
  "data_source_id": 1
}
```

### `POST /dashboard/chart/create`

Cria um grafico dentro de um dashboard.

```json
{
  "dashboard_id": 1,
  "chart_type": "bar",
  "title": "Receita por categoria",
  "chart_data": {
    "data": []
  },
  "chart_config": {}
}
```

### `POST /dashboard/refresh/finish`

Salva resultado de uma atualizacao gerada pela IA.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1,
  "prompt": "Novo prompt",
  "ai_suggestion": "Nova analise",
  "charts": []
}
```

### `POST /dashboard/chart/settings`

Salva configuracoes visuais de dashboard ou grafico.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1,
  "chart_id": 10,
  "chart_color": "#4f46e5",
  "chart_background": "#f8fafc",
  "x_axis_text_color": "#0f172a",
  "y_axis_text_color": "#0f172a",
  "grid_color": "#cbd5e1",
  "grid_style": "3 3",
  "bar_style": "rounded",
  "show_legend": true,
  "pie_colors": ["#4f46e5", "#06b6d4"]
}
```

### `DELETE /dashboard`

Remove dashboard.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1
}
```

## Rotas de colaboracao

Permissoes aceitas:

| Permissao | Significado |
| --- | --- |
| `read` | Apenas visualizar |
| `edit` | Editar configuracoes e conteudo permitido |
| `full` | Acesso amplo, incluindo atualizacoes vinculadas |

### `POST /users/search`

Busca usuarios por username/nome para compartilhar.

```json
{
  "token": "JWT_DO_USUARIO",
  "query": "ana"
}
```

### `POST /collaborations`

Retorna visao geral de dashboards, compartilhados e convites.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `POST /dashboard/collaborations`

Lista colaboradores de um dashboard.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1
}
```

### `POST /dashboard/collaboration/share`

Compartilha dashboard com outro usuario.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1,
  "username": "colega",
  "permission": "edit"
}
```

### `PATCH /dashboard/collaboration`

Atualiza permissao de colaborador.

```json
{
  "token": "JWT_DO_USUARIO",
  "collaboration_id": 1,
  "permission": "full"
}
```

### `DELETE /dashboard/collaboration`

Remove colaboracao.

```json
{
  "token": "JWT_DO_USUARIO",
  "collaboration_id": 1
}
```

### `POST /dashboard/collaboration/respond`

Aceita ou recusa convite.

```json
{
  "token": "JWT_DO_USUARIO",
  "collaboration_id": 1,
  "response": "accepted"
}
```

`response` aceita `accepted` ou `declined`.

### `POST /dashboard/access`

Lista pessoas com acesso ao dashboard.

```json
{
  "token": "JWT_DO_USUARIO",
  "dashboard_id": 1
}
```

## Rotas de notificacoes

### `POST /notifications`

Lista notificacoes do usuario.

```json
{
  "token": "JWT_DO_USUARIO"
}
```

### `PATCH /notification/read`

Marca notificacao como lida.

```json
{
  "token": "JWT_DO_USUARIO",
  "notification_id": 1
}
```

## Fontes de dados e sincronizacao automatica

Quando `/data-sources` e chamado, a API verifica fontes com `refresh_interval_days` vencido. Para cada fonte vencida:

1. recarrega os dados pela configuracao original;
2. atualiza a fonte no banco;
3. busca dashboards vinculados;
4. chama a API de IA para recalcular dashboards;
5. salva os dashboards atualizados quando possivel;
6. cria notificacoes em caso de sucesso ou falha.

## Integracao com a API de IA

A variavel `AI_URL` define para onde a API envia pedidos de reanalise. O fluxo de refresh usa:

```text
DATABASE /data-sources
  -> detecta fonte vencida
  -> POST {AI_URL}/dashboard/refresh/analyze
  -> salva resultado via ManagerCharts
```

## Codigos de resposta

| Codigo | Uso |
| --- | --- |
| `200 OK` | Consulta, atualizacao ou exclusao bem-sucedida |
| `201 Created` | Criacao de usuario, conversa, fonte, dashboard, grafico ou colaboracao |
| `400 Bad Request` | Erro de validacao de regra de negocio |
| `422 Unprocessable Entity` | Body/FormData fora do schema esperado |
| `500 Internal Server Error` | Erro inesperado |

## Observacoes de seguranca

- Para fontes `database`, apenas consultas iniciadas com `SELECT` sao aceitas.
- Tokens sao resolvidos no backend para impedir acesso a dados de outro usuario.
- Colaboracoes passam por verificacao de permissao antes de listar fontes e dashboards.
- Senhas devem ser armazenadas apenas com hash.
- Strings de conexao de banco externo devem ser tratadas como segredo.

## Status da pasta de migrations

A pasta `migrations/` foi removida deste reposititorio conforme decisao do projeto. Caso o time volte a usar versionamento formal de schema, recomenda-se recriar uma estrutura controlada com Alembic ou ferramenta equivalente.
