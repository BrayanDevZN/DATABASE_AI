from core.config import data
import secrets

from connect.manager_database import main_database
from sqlalchemy import text
from datetime import datetime


class Auth_Pass:
    def __init__(self, id: int, email: str) -> None:

        self.id = id
        self.email = email
        self.cod = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        self.engine = main_database()
        self.url = data().url_email()


    def get_code(self) -> str:
        return self.cod

    def add(self) -> None:
        with self.engine.connect() as session:
            session.execute(
                text("""
                    INSERT INTO validation (user_id, number)
                    VALUES (:user_id, :number)
                """),
                {
                    "user_id": self.id,
                    "number": self.cod
                }
            )

            session.commit()

    def env(self) -> None:
        import requests
        payload = {
            "subject": "Código de verificação para alterar senha",
            "email": self.email,
            "sender": f"""Seu código de verificação é: {self.code}
            
            Observação:Se não foi você que enviou, nos avise!!"""
        }
        requests.post(url=self.url, json=payload).json()

    def execute(self) -> str:
        self.add()
        self.env()

        return self.cod
    

    

    
