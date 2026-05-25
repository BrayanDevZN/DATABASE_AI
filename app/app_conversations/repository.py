from sqlalchemy import text
from connect.manager_database import main_database

engine = main_database()


class RepositoryConversation:
    def __init__(self) -> None:
        self.db = engine

    def create(
        self,
        user_id: int,
        conversation_id: int,
        role: str,
        content: str
    ) -> dict | None:
        with self.db.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO conversations (user_id, conversation_id, role, content)
                    VALUES (:user_id, :conversation_id, :role, :content)
                    RETURNING id, user_id, conversation_id, role, content, created_at
                """),
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content
                }
            )

            data = result.mappings().first()
            return dict(data) if data else None

    def select_by_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, user_id, conversation_id, role, content, created_at
                    FROM conversations
                    WHERE user_id = :user_id
                    ORDER BY created_at ASC
                    LIMIT 20
                """),
                {"user_id": user_id}
            )

            return [dict(row) for row in result.mappings().all()]

    def select_by_conversation(
        self,
        user_id: int,
        conversation_id: int
    ) -> list[dict]:
        with self.db.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, user_id, conversation_id, role, content, created_at
                    FROM conversations
                    WHERE user_id = :user_id
                    AND conversation_id = :conversation_id
                    ORDER BY created_at ASC
                """),
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }
            )

            return [dict(row) for row in result.mappings().all()]

    def select_conversations(self, user_id: int) -> list[dict]:
        with self.db.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        conversation_id,
                        MIN(created_at) AS created_at,
                        MAX(created_at) AS updated_at,
                        COUNT(*) AS total_messages
                    FROM conversations
                    WHERE user_id = :user_id
                    GROUP BY conversation_id
                    ORDER BY updated_at DESC
                """),
                {"user_id": user_id}
            )

            return [dict(row) for row in result.mappings().all()]

    def delete_conversation(
        self,
        user_id: int,
        conversation_id: int
    ) -> bool:
        with self.db.begin() as conn:
            result = conn.execute(
                text("""
                    DELETE FROM conversations
                    WHERE user_id = :user_id
                    AND conversation_id = :conversation_id
                """),
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }
            )

            return result.rowcount > 0
        
    def create_empty(self, user_id: int) -> int:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT COALESCE(MAX(conversation_id), 0) + 1 AS next_id
                    FROM conversations
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            conversation_id = result.fetchone()._mapping["next_id"]

            session.execute(
                text("""
                    INSERT INTO conversations (user_id, conversation_id, role, content)
                    VALUES (:user_id, :conversation_id, :role, :content)
                """),
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": "Nova conversa criada."
                }
            )

            session.commit()

            return conversation_id