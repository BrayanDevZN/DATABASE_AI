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
        msg = EmailMessage()

        msg["Subject"] = "Código de verificação"
        msg["From"] = self.email_user
        msg["To"] = self.email

        msg.set_content(f"""
Olá,

Seu código de verificação é:

{self.cod}

Se você não solicitou isso, ignore este e-mail.
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email_user, self.key)
            smtp.send_message(msg)

    def execute(self) -> str:
        self.add()
        self.env()

        return self.cod
    

    
    
