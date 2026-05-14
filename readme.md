<div align="center">

# 👤 Accounts & Conversations API

**API de autenticação, gerenciamento de usuários e histórico de conversas**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io)

</div>

---

## 📋 Índice

- [Sobre](#-sobre)
- [URL Base](#-url-base)
- [Autenticação](#-autenticação)
- [Rotas — Usuários](#-rotas--usuários)
- [Rotas — Conversas](#-rotas--conversas)
- [Fluxos completos](#-fluxos-completos)
- [Códigos de resposta](#-códigos-de-resposta)

---

## 📖 Sobre

API responsável por toda a camada de **identidade e histórico** da plataforma. Ela oferece:

- Cadastro de usuários com validação de e-mail por código
- Login com retorno de JWT
- Recuperação e atualização de senha
- Validação de tokens JWT
- Criação e consulta de conversas e mensagens

---

## 🌐 URL Base

```
https://web-production-81b91.up.railway.app
```

Todos os endpoints abaixo são relativos a essa URL.

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Token)**. O token é retornado no login e deve ser incluído no body das rotas que exigem autenticação, no campo `token`.

> Não há header `Authorization` — o token vai **sempre no body** da requisição.

---

## 👤 Rotas — Usuários

### 1. Enviar código de verificação

Envia um código por e-mail para validar o endereço antes do cadastro.

```
POST /env_code_create
```

**Body:**
```json
{
  "email": "usuario@email.com"
}
```

**Resposta:** `201 Created`
```json
"usuario@email.com"
```

---

### 2. Verificar se e-mail já existe

Checa se um e-mail já está cadastrado na base.

```
POST /valid_user
```

**Body:**
```json
{
  "email": "usuario@email.com"
}
```

**Resposta:** `200 OK`
```json
{ "exists": true }
// ou
{ "exists": false }
```

---

### 3. Criar usuário

Cadastra um novo usuário. Requer o código de verificação enviado por e-mail.

```
POST /create_user
```

**Body:**
```json
{
  "email": "usuario@email.com",
  "password": "senha123",
  "name": "João Silva",
  "age": 28,
  "gender": "masculino",
  "code": 123456
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `email` | string | E-mail do usuário |
| `password` | string | Senha |
| `name` | string | Nome completo |
| `age` | int | Idade |
| `gender` | string | Gênero |
| `code` | int | Código recebido por e-mail |

**Resposta:** `201 Created` — mesmo formato do login (com token JWT) ou `null` se o código for inválido/expirado.

```json
{
  "exists": true,
  "status": true,
  "token": "eyJ...",
  "name": "João Silva",
  "gender": "masculino",
  "age": 28
}
```

---

### 4. Login

Autentica o usuário e retorna um JWT.

```
POST /login
```

**Body:**
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```

**Resposta:** `200 OK`

| Cenário | `exists` | `status` | `token` |
|---|---|---|---|
| Usuário não encontrado | `false` | `false` | `null` |
| Senha incorreta | `true` | `false` | `null` |
| Login bem-sucedido | `true` | `true` | `"eyJ..."` |

```json
{
  "exists": true,
  "status": true,
  "token": "eyJ...",
  "name": "João Silva",
  "gender": "masculino",
  "age": 28
}
```

---

### 5. Validar token JWT

Verifica se um token ainda é válido e se o usuário é administrador.

```
POST /valid_token
```

**Body:**
```json
{
  "token": "eyJ..."
}
```

**Resposta:** `200 OK`
```json
{
  "admin": false,
  "is_valid": true,
  "token": "eyJ..."
}
```

---

### 6. Verificar senha atual

Valida a senha atual do usuário. Retorna um `change_token` temporário para autorizar a troca de senha.

```
POST /check_pass
```

**Body:**
```json
{
  "token": "eyJ...",
  "password": "senha_atual"
}
```

**Resposta:** `200 OK`
```json
{
  "status": true,
  "change_token": "eyJ..."
}
// ou
{ "status": false }
```

---

### 7. Atualizar senha (fluxo autenticado)

Troca a senha usando o `change_token` retornado por `/check_pass`.

```
PATCH /update_pass
```

**Body:**
```json
{
  "token": "change_token_aqui",
  "password": "nova_senha"
}
```

**Resposta:** `200 OK`
```json
{ "status": true }
// ou
{ "status": false }
```

---

### 8. Enviar código para recuperação de senha

Envia um código por e-mail para redefinição de senha (usuário esqueceu a senha). Requer token JWT válido.

```
POST /env_pass
```

**Body:**
```json
{
  "token": "eyJ..."
}
```

**Resposta:** `200 OK`
```json
true
// ou
false
```

---

### 9. Redefinir senha com código (recuperação)

Redefine a senha usando o código recebido por e-mail. Não aceita a mesma senha atual.

```
PATCH /update_auth_pass
```

**Body:**
```json
{
  "token": "eyJ...",
  "code": 123456,
  "password": "nova_senha"
}
```

**Resposta:** `200 OK`

| Cenário | `status` |
|---|---|
| Sucesso | `true` |
| Token/código inválido ou expirado | `false` |
| Nova senha igual à atual | `"equal"` |

---

### 10. Atualizar nome

Atualiza o nome do usuário autenticado.

```
PATCH /update_name
```

**Body:**
```json
{
  "token": "eyJ...",
  "name": "Novo Nome"
}
```

**Resposta:** `200 OK`
```json
{ "status": true }
// ou
{ "status": false }
```

---

## 💬 Rotas — Conversas

### 11. Criar mensagem em uma conversa

Salva uma mensagem (do usuário ou do assistente) em uma conversa.

```
POST /conversation
```

**Body:**
```json
{
  "token": "eyJ...",
  "conversation_id": 1,
  "role": "user",
  "content": "Qual produto vende mais?"
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `token` | string | JWT do usuário |
| `conversation_id` | int | ID da conversa (deve ser `> 0`) |
| `role` | string | `"user"` ou `"assistant"` |
| `content` | string | Conteúdo da mensagem (não pode ser vazio) |

**Resposta:** `201 Created`

---

### 12. Listar todas as conversas do usuário

Retorna um resumo de todas as conversas do usuário autenticado.

```
POST /conversations
```

**Body:**
```json
{
  "token": "eyJ..."
}
```

**Resposta:** `200 OK`
```json
{
  "conversations": [
    {
      "conversation_id": 1,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T11:00:00",
      "total_messages": 8
    }
  ]
}
```

---

### 13. Buscar mensagens de uma conversa

Retorna todas as mensagens de uma conversa específica.

```
POST /conversation/messages
```

**Body:**
```json
{
  "token": "eyJ...",
  "conversation_id": 1
}
```

**Resposta:** `200 OK`
```json
{
  "messages": [
    {
      "id": 42,
      "user_id": 7,
      "conversation_id": 1,
      "role": "user",
      "content": "Qual produto vende mais?",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 43,
      "user_id": 7,
      "conversation_id": 1,
      "role": "assistant",
      "content": "O produto Teclado lidera as vendas...",
      "created_at": "2024-01-15T10:30:05"
    }
  ]
}
```

---

### 14. Buscar conversas por usuário

Retorna dados agrupados por usuário autenticado.

```
POST /conversation/user
```

**Body:**
```json
{
  "token": "eyJ..."
}
```

**Resposta:** `200 OK` — lista de conversas do usuário.

---

### 15. Deletar uma conversa

Remove uma conversa e todas as suas mensagens.

```
DELETE /conversation
```

**Body:**
```json
{
  "token": "eyJ...",
  "conversation_id": 1
}
```

**Resposta:** `200 OK`
```json
true
// ou
false
```

---

## 🔄 Fluxos completos

### Fluxo de cadastro

```
1. POST /env_code_create     → envia código para o e-mail
2. POST /create_user         → cria conta com o código recebido
                             → retorna JWT automaticamente
```

### Fluxo de login

```
1. POST /login               → retorna JWT se credenciais válidas
```

### Fluxo de troca de senha (usuário logado)

```
1. POST /check_pass          → valida senha atual → retorna change_token
2. PATCH /update_pass        → usa change_token para salvar nova senha
```

### Fluxo de recuperação de senha (esqueci a senha)

```
1. POST /env_pass            → envia código para o e-mail (requer JWT válido)
2. PATCH /update_auth_pass   → usa código + JWT para definir nova senha
```

### Fluxo de conversa

```
1. POST /conversation        → salva mensagem do usuário (role: "user")
2. [IA processa a resposta]
3. POST /conversation        → salva resposta da IA (role: "assistant")
4. POST /conversation/messages → recupera histórico completo
```

---

## 📊 Códigos de resposta

| Código | Significado |
|---|---|
| `200 OK` | Requisição bem-sucedida |
| `201 Created` | Recurso criado com sucesso |
| `422 Unprocessable Entity` | Body inválido ou campos faltando |

---

<div align="center">

Feito com ☕ e **FastAPI** · [Voltar ao topo](#-accounts--conversations-api)

</div>
