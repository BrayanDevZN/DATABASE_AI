import resend
from sqlalchemy import text
from core.config import data
from connect.manager_database import main_database
from typing import Literal
from pydantic import BaseModel, field_validator
import secrets

class Valid_Content(BaseModel):
    type:Literal["Create", "Update"]
    content:dict | str
    @field_validator("content")
    @classmethod
    def valid(cls, value, info):
        if info.data.get("type") == "Create":
            if not isinstance(value, str):
                raise TypeError(f"Expeted type {value} str.")
            
        if info.data.get("type") == "Update":
            if not isinstance(value, dict):
                raise TypeError(f"Expeted type {value} dict.")
            
            if not "id" in value.keys():
                raise KeyError(f"Expeted key 'id' in {value}")
            
            if not "email" in value.keys():
                raise KeyError(f"Expeted key 'email' in {value}")
            
            if len(value.keys()) > 2:
                raise KeyError("Max key exceded.")
            if len(value.keys()) < 2:
                raise KeyError(f"Expeted len({value}) == 2.")
            
        return value
            
            
            
    
class Sender_Auth:
    def __init__(self, type:str, content:dict)-> dict:
        valid = Valid_Content(type=type,content=content)
        self.type = valid.type
        self.content = valid.content
        self.code = str(''.join(str(secrets.randbelow(10)) for _ in range(6)))
        self.msg = self.payload()
        self.query = self.payload_db()
        self.engine = main_database()
        self.key = data().key_email()
        
    def payload(self) -> dict:
        return {
    "from": "DataPilot <no-reply@datapilotplataform.com>",
    "to": [self.content],
    "subject": "Código de verificação para criação de conta",
    "html": f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 32px;">
        <div style="max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <h2 style="color: #111827; margin-bottom: 16px;">Código de verificação</h2>

            <p style="color: #374151; font-size: 16px;">
                Use o código abaixo para finalizar a criação da sua conta:
            </p>

            <div style="text-align: center; margin: 32px 0;">
                <span style="display: inline-block; background-color: #f3f4f6; color: #111827; font-size: 32px; font-weight: bold; letter-spacing: 6px; padding: 16px 28px; border-radius: 10px;">
                    {self.code}
                </span>
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Se não foi você que solicitou este código, ignore este email ou entre em contato com o suporte.
            </p>
        </div>
    </div>
    """
} if self.type == "Create" else {
    "from": "DataPilot <no-reply@datapilotplataform.com>",
    "to": [self.content["email"]],
    "subject": "Código de verificação para alterar senha",
    "html": f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 32px;">
        <div style="max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <h2 style="color: #111827; margin-bottom: 16px;">Alteração de senha</h2>

            <p style="color: #374151; font-size: 16px;">
                Use o código abaixo para confirmar a alteração da sua senha:
            </p>

            <div style="text-align: center; margin: 32px 0;">
                <span style="display: inline-block; background-color: #f3f4f6; color: #111827; font-size: 32px; font-weight: bold; letter-spacing: 6px; padding: 16px 28px; border-radius: 10px;">
                    {self.code}
                </span>
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Se não foi você que solicitou este código, ignore este email ou entre em contato com o suporte.
            </p>
        </div>
    </div>
    """
}
        
    def payload_db(self) ->dict:
        return {"query":text("""
                    INSERT INTO validation_account (email, number, used, created_at)
                    VALUES (:email, :number, false, CURRENT_TIMESTAMP)
                """),
                             
                "params":{
                    "email": self.content,
                    "number": self.code
                }} if self.type == "Create" else {"query":text("""
                    INSERT INTO validation (user_id, number)
                    VALUES (:user_id, :number)
                """),
                "params":{
                    "user_id": self.content["id"],
                    "number": self.code
                }}
                
    def execute(self) -> None:
        with self.engine.connect() as session:
            session.execute(
                self.query["query"],
                self.query["params"]
            )
            
            session.commit()
            
    def env(self) -> None:
        resend.api_key = self.key

        params: resend.Emails.SendParams = self.msg

        email = resend.Emails.send(params)
        
    def __call__(self)-> None:
        self.env()
        self.execute()
        
        
        
                
    
