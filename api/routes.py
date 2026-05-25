from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

import api.model.model_accounts as models
import api.model.model_conversation as conversation_models
import app.app_accounts.manager_accounts as manager
import app.app_conversations.manager_conversation as conversation_manager


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    
    return manager.User_Login().Env_codePass(data=data.model_dump()) 


@app.patch("/update_auth_pass", status_code=status.HTTP_200_OK)
def update_auth_pass(data: models.UpdateAuthPass):
    
    return manager.User_Login().updateAuth_Pass(data=data.model_dump()) 
    
    


@app.patch("/update_pass", status_code=status.HTTP_200_OK)
def update_pass(data: models.Pass):
    return manager.User_Login().update_Pass(data.model_dump())


@app.post("/check_pass", status_code=status.HTTP_200_OK)
def check_pass(data: models.Pass):
    return manager.User_Login().check_pass(data.model_dump())


@app.patch("/update_name", status_code=status.HTTP_200_OK)
def update_name(data: models.UpName):
    return manager.User_Login().update_name(data.model_dump())


@app.post("/valid_token", status_code=status.HTTP_200_OK)
def valid_token(data: models.ValidToken):
    return manager.User_Login().valid_token(data.model_dump())


@app.post("/conversation", status_code=status.HTTP_201_CREATED)
def create_conversation(data: conversation_models.CreateConversationWithToken):
    return conversation_manager.ManagerConversation().create(data.model_dump())


@app.post("/conversations", status_code=status.HTTP_200_OK)
def select_conversations(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().select_conversations(data.model_dump())


@app.post("/conversation/messages", status_code=status.HTTP_200_OK)
def select_by_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().select_by_conversation(data.model_dump())


@app.post("/conversation/user", status_code=status.HTTP_200_OK)
def select_by_user(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().select_by_user(data.model_dump())


@app.delete("/conversation", status_code=status.HTTP_200_OK)
def delete_conversation(data: conversation_models.GetConversation):
    return conversation_manager.ManagerConversation().delete_conversation(data.model_dump())


@app.post("/conversation/create", status_code=status.HTTP_201_CREATED)
def create_empty_conversation(data: conversation_models.WithToken):
    return conversation_manager.ManagerConversation().create_empty(data.model_dump())
#a