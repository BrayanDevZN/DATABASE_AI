import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

from sqlalchemy import text

from core.config import data
from connect.manager_database import main_database


class CreateAccountCode:
    def __init__(self, email: str) -> None:
        self.email = email
        self.code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        self.engine = main_database()

        self.email_user = data().email_user()
        self.email_pass = data().key_email()

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
        self.save()
        self.send()

        return self.code