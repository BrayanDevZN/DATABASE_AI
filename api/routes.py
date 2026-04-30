from fastapi import FastAPI, status
import  api.model.model_accounts as models
import  app.app_accounts.manager_accounts as manager

app = FastAPI()

    
@app.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(data: models.CreateUser):
    return manager.create_User().create(data.model_dump())

@app.post("/env_code_create", status_code=status.HTTP_201_CREATED)
def env_create(data: models.ValidEmail):
    return manager.create_User().env_code(data.model_dump())

@app.post("/valid_user", status_code=status.HTTP_201_CREATED)
def valid_user(data: models.ValidEmail):
    return manager.create_User().env_code(data.model_dump())

@app.post("/login", status_code=status.HTTP_200_OK)
def login(data: models.Login):
    return manager.User_Login().login(data.model_dump())

@app.post("/Env_Pass", status_code=status.HTTP_201_CREATED)
def env_pass(data: models.Env_CodePass):
    return manager.User_Login().Env_codePass(data.model_dump())

@app.patch("/updateAuth_pass", status_code=status.HTTP_200_OK)
def env_AuthPass(data: models.UpdateAuthPass):
    return manager.User_Login().updateAuth_Pass(data.model_dump())

@app.patch("/update_pass", status_code=status.HTTP_200_OK)
def update_pass(data: models.Pass):
    return manager.User_Login().update_Pass(data.model_dump())

@app.post("/check_pass", status_code=status.HTTP_200_OK)
def check_pass(data: models.Pass):
    return manager.User_Login().check_pass(data.model_dump())

@app.patch("/update_name", status_code=status.HTTP_200_OK)
def up_name(data: models.UpName):
    return manager.User_Login().update_name(data.model_dump())

@app.get("/docs")
def docs_api():
    return {
        "create_user": {
            "method": "POST",
            "route": "/create_user",
            "description": "Cria um usuário depois de validar o código enviado por email.",
            "body": {
                "email": "str",
                "password": "str",
                "name": "str",
                "age": "int",
                "gender": "str",
                "code": "int"
            },
            "response": {
                "success": "retorna login/token",
                "error": None
            }
        },

        "env_code_create": {
            "method": "POST",
            "route": "/env_code_create",
            "description": "Envia código de criação de conta para o email.",
            "body": {
                "email": "str"
            },
            "response": {
                "success": "email",
                "error": None
            }
        },

        "valid_user": {
            "method": "POST",
            "route": "/valid_user",
            "description": "Verifica se o usuário já existe pelo email.",
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
            "description": "Faz login com email e senha.",
            "body": {
                "email": "str",
                "password": "str"
            },
            "response": {
                "success": "token/login",
                "error": False
            }
        },

        "env_pass": {
            "method": "POST",
            "route": "/env_pass",
            "description": "Envia código para alterar senha autenticada.",
            "body": {
                "token": "str"
            },
            "response": {
                "success": True,
                "error": False
            }
        },

        "update_auth_pass": {
            "method": "PATCH",
            "route": "/update_auth_pass",
            "description": "Atualiza senha usando token, código e nova senha.",
            "body": {
                "code": "int",
                "token": "str",
                "password": "str"
            },
            "response": {
                "status": "bool | equal"
            }
        },

        "check_pass": {
            "method": "POST",
            "route": "/check_pass",
            "description": "Confere senha atual e retorna token temporário para troca.",
            "body": {
                "token": "str",
                "password": "str"
            },
            "response": {
                "status": "bool",
                "change_token": "str | optional"
            }
        },

        "update_pass": {
            "method": "PATCH",
            "route": "/update_pass",
            "description": "Atualiza senha usando change_token gerado pelo check_pass.",
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

