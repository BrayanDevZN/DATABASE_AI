from fastapi import FastAPI, status
import api.model.model_accounts as models
import app.app_accounts.manager_accounts as manager

app = FastAPI()


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(data: models.CreateUser):
    return manager.create_User().create(data.model_dump())


@app.post("/env_code_create", status_code=status.HTTP_201_CREATED)
def env_code_create(data: models.ValidEmail):
    return manager.create_User().env_code(data.model_dump())


@app.post("/valid_user", status_code=status.HTTP_200_OK)
def valid_user(data: models.ValidEmail):
    return manager.create_User().valid_user(data.model_dump())


@app.post("/login", status_code=status.HTTP_200_OK)
def login(data: models.Login):
    return manager.User_Login().login(data.model_dump())


@app.post("/env_pass", status_code=status.HTTP_200_OK)
def env_pass(data: models.Env_CodePass):
    return manager.User_Login().Env_codePass(data.model_dump()["token"])


@app.patch("/update_auth_pass", status_code=status.HTTP_200_OK)
def update_auth_pass(data: models.UpdateAuthPass):
    return manager.User_Login().updateAuth_Pass(data.model_dump())


@app.patch("/update_pass", status_code=status.HTTP_200_OK)
def update_pass(data: models.Pass):
    return manager.User_Login().update_Pass(data.model_dump())


@app.post("/check_pass", status_code=status.HTTP_200_OK)
def check_pass(data: models.Pass):
    return manager.User_Login().check_pass(data.model_dump())


@app.patch("/update_name", status_code=status.HTTP_200_OK)
def update_name(data: models.UpName):
    return manager.User_Login().update_name(data.model_dump())
@app.get("/docs_api")
def docs_api():
    return {
        "create_user": {
            "method": "POST",
            "route": "/create_user",
            "description": "Cria um usuário após validar código enviado por email.",
            "body": {
                "email": "str",
                "password": "str",
                "name": "str",
                "age": "int",
                "gender": "str",
                "code": "int"
            },
            "response": "token/login ou None"
        },

        "env_code_create": {
            "method": "POST",
            "route": "/env_code_create",
            "description": "Envia código de criação de conta para o email.",
            "body": {
                "email": "str"
            },
            "response": "email"
        },

        "valid_user": {
            "method": "POST",
            "route": "/valid_user",
            "description": "Verifica se o email já existe no sistema.",
            "body": {
                "email": "str"
            },
            "response": {
                "exists": "bool"
            }
        },

        "login": {
            "method": "POST",
            "route": "/login",
            "description": "Realiza login e retorna token.",
            "body": {
                "email": "str",
                "password": "str"
            },
            "response": "token"
        },

        "env_pass": {
            "method": "POST",
            "route": "/env_pass",
            "description": "Envia código para alteração de senha usando token.",
            "body": {
                "token": "str"
            },
            "response": "true/false"
        },

        "update_auth_pass": {
            "method": "PATCH",
            "route": "/update_auth_pass",
            "description": "Atualiza senha com código + token.",
            "body": {
                "code": "int",
                "token": "str",
                "password": "str"
            },
            "response": {
                "status": "true/false/equal"
            }
        },

        "check_pass": {
            "method": "POST",
            "route": "/check_pass",
            "description": "Valida senha atual e retorna token temporário para troca.",
            "body": {
                "token": "str",
                "password": "str"
            },
            "response": {
                "status": "bool",
                "change_token": "str (se válido)"
            }
        },

        "update_pass": {
            "method": "PATCH",
            "route": "/update_pass",
            "description": "Atualiza senha usando change_token.",
            "body": {
                "token": "str",
                "password": "str"
            },
            "response": {
                "status": "bool"
            }
        },

        "update_name": {
            "method": "PATCH",
            "route": "/update_name",
            "description": "Atualiza nome do usuário autenticado.",
            "body": {
                "token": "str",
                "name": "str"
            },
            "response": {
                "status": "bool"
            }
        }
    }