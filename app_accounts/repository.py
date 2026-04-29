from sqlalchemy import text
from connect.manager_database import main_database

engine = main_database()


class RepositoryAccount:
    def __init__(self) -> None:
        self.db = engine

    def create(
        self,
        name: str,
        email: str,
        password: str,
        role: str,
        status: bool,
        gender:str,
        age:int
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO users (name, email, password, role, status, age, gender)
                    VALUES (:name, :email, :password, :role, :status, :age, :gender)
                    RETURNING user_id, name, email, password, role, status, created_at, age, gender
                """),
                {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "status": status,
                    "age": age,
                    "gender":gender
                }
            )

            session.commit()
            user = result.fetchone()

        return dict(user._mapping) if user else None

    def select(self, user_id: int) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT user_id, name,gender, age, email, password, role, status, created_at
                    FROM users
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            user = result.fetchone()

        return dict(user._mapping) if user else None

    def select_by_email(self, email: str) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT user_id, name,gender, age, email, password, role, status, created_at
                    FROM users
                    WHERE email = :email
                """),
                {"email": email}
            )

            user = result.fetchone()

        return dict(user._mapping) if user else None

    def select_all(self) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT user_id, name,gender, age, email, password, role, status, created_at
                    FROM users
                    ORDER BY user_id
                """)
            )

            users = result.fetchall()

        return [dict(user._mapping) for user in users]

    def update(
        self,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role: str | None = None,
        status: bool | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE users
                    SET
                        name = COALESCE(:name, name),
                        email = COALESCE(:email, email),
                        password = COALESCE(:password, password),
                        role = COALESCE(:role, role),
                        status = COALESCE(:status, status)
                    WHERE user_id = :user_id
                    RETURNING user_id, name, email, password, role, status, created_at
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "status": status
                }
            )

            session.commit()
            user = result.fetchone()

        return dict(user._mapping) if user else None

    def delete(self, user_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM users
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            session.commit()

        return result.rowcount > 0