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
        msg = EmailMessage()

        msg["Subject"] = "Código de criação de conta"
        msg["From"] = self.email_user
        msg["To"] = self.email

        msg.set_content(f"""
Olá,

Seu código para criar conta é:

{self.code}

Esse código expira em 8 minutos.

Se você não solicitou isso, ignore este e-mail.
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email_user, self.email_pass)
            smtp.send_message(msg)

    def execute(self) -> str:
        self.save()
        self.send()

        return self.code