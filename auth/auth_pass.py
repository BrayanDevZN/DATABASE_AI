from core.config import data
import secrets
import smtplib
from email.message import EmailMessage
from connect.manager_database import main_database
from sqlalchemy import text
from datetime import datetime


class Auth_Pass:
    def __init__(self, id: int, email: str) -> None:
        self.key = data().key_email()
        self.email_user = data().email_user()
        self.id = id
        self.email = email
        self.cod = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        self.engine = main_database()
        self.email_user = data().email_user()
        self.email_pass = data().key_email()

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
        import resend

        resend.api_key = self.email_pass  

        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": self.email,
            "subject": "Código de verificação",
            "html": f"""
            <p>Olá,</p>

            <p>Seu código para alterar senha é:</p>

            <h2>{self.cod}</h2>

            <p>Se você não solicitou isso, ignore este e-mail.</p>
            """
        })

    def execute(self) -> str:
        self.add()
        self.env()

        return self.cod
    

    

    
