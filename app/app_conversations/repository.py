from sqlalchemy import text
from connect.manager_database import main_database


class RepositoryConversation:
    def __init__(self) -> None:
        self.db = main_database()
        
    def create_empty(self, user_id: int, title: str) -> int:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO conversations (user_id, title)
                    VALUES (:user_id, :title)
                    RETURNING id
                """),
                {
                    "user_id": user_id,
                    "title": title
                }
            )

            session.commit()

            return result.fetchone()[0]


    def create(
        self,
        user_id: int,
        conversation_id: int,
        role: str,
        content: str
    ) -> dict:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO messages (conversation_id, role, content)
                    VALUES (:conversation_id, :role, :content)
                    RETURNING id, conversation_id, role, content, created_at
                """),
                {
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content,
                }
            )

            session.execute(
                text("""
                    UPDATE conversations
                    SET updated_at = NOW()
                    WHERE id = :conversation_id
                    AND user_id = :user_id
                """),
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                }
            )

            session.commit()

            row = result.fetchone()
            return dict(row._mapping)

    def select_conversations(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT
                        c.id AS conversation_id,
                        c.title,
                        c.created_at,
                        c.updated_at,
                        COUNT(m.id) AS total_messages
                    FROM conversations c
                    LEFT JOIN messages m
                        ON m.conversation_id = c.id
                    WHERE c.user_id = :user_id
                    GROUP BY c.id, c.title, c.created_at, c.updated_at
                    ORDER BY c.updated_at DESC
                """),
                {"user_id": user_id}
            )

            return [dict(row._mapping) for row in result.fetchall()]

    def select_by_conversation(
        self,
        user_id: int,
        conversation_id: int
    ) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT
                        m.id,
                        c.user_id,
                        m.conversation_id,
                        m.role,
                        m.content,
                        m.created_at
                    FROM messages m
                    INNER JOIN conversations c
                        ON c.id = m.conversation_id
                    WHERE c.user_id = :user_id
                    AND c.id = :conversation_id
                    ORDER BY m.created_at ASC
                """),
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                }
            )

            return [dict(row._mapping) for row in result.fetchall()]

    def select_by_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT
                        m.id,
                        c.user_id,
                        m.conversation_id,
                        m.role,
                        m.content,
                        m.created_at
                    FROM messages m
                    INNER JOIN conversations c
                        ON c.id = m.conversation_id
                    WHERE c.user_id = :user_id
                    ORDER BY m.created_at ASC
                """),
                {"user_id": user_id}
            )

            return [dict(row._mapping) for row in result.fetchall()]

    def delete_conversation(self, user_id: int, conversation_id: int) -> bool:
        with self.db.connect() as session:
            session.execute(text(
                
                
            ))
            result = session.execute(
                text("""
                    DELETE FROM conversations
                    WHERE id = :conversation_id
                    AND user_id = :user_id
                """),
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                }
            )
            
            

            session.commit()
            return result.rowcount > 0
        
    def delete_all_by_user(self, user_id: int) -> bool:
        with self.db.connect() as session:
            session.execute(
                text("""
                    DELETE FROM messages
                    WHERE conversation_id IN (
                        SELECT id
                        FROM conversations
                        WHERE user_id = :user_id
                    )
                """),
                {"user_id": user_id}
            )

            result = session.execute(
                text("""
                    DELETE FROM conversations
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            session.commit()

        return result.rowcount >= 0
            