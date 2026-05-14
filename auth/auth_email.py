import secrets


from sqlalchemy import text

from core.config import data
from connect.manager_database import main_database


class Auth_Create:
    def __init__(self, email: str) -> None:
        self.email = email
        self.code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        self.engine = main_database()
        
        

        
        self.url = data().url_email()

    def get_code(self) -> str:
        return self.code

    def save(self) -> None:
        with self.engine.connect() as session:
            session.execute(
                text("""
                    INSERT INTO validation_account (email, number, used, created_at)
                    VALUES (:email, :number, false, CURRENT_TIMESTAMP)
                """),
                {
                    "email": self.email,
                    "number": self.code
                }
            )

            session.commit()

    def send(self) -> None:
        import requests
        payload = {
            "subject": "Código de verificação para criação de conta",
            "email": self.email,
            "sender": f"""Seu código de verificação é: {self.code}
            
            Observação:Se não foi você que enviou, nos avise!!"""
        }
        requests.post(url=self.url, json=payload).json()
    def execute(self) -> str:
        self.save()
        self.send()

        return self.code