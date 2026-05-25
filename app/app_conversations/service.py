from auth.manager_auth import valid_jwt
from auth.jwt import JWT
from app.app_conversations.repository import RepositoryConversation


class ServiceConversation:
    def __init__(self) -> None:
        self.repo = RepositoryConversation()
        self.jwt = JWT()

    def _valid_token(self, token: str) -> dict:
        if not token:
            raise ValueError("token is required")

        auth = valid_jwt(token).validation()

        if not auth["is_valid"]:
            raise ValueError("invalid token")

        user_id = self.jwt.get_jwt("user_id", token)

        if user_id is None:
            raise ValueError("invalid token user_id")

        return {
            "token": token,
            "user_id": user_id,
            "admin": auth["admin"]
        }

    def create(self, data: dict, token: str) -> dict | None:
        user = self._valid_token(token)

        return self.repo.create(
            user_id=user["user_id"],
            conversation_id=data["conversation_id"],
            role=data["role"],
            content=data["content"]
        )

    def select_by_user(self, token: str) -> list[dict]:
        user = self._valid_token(token)

        return self.repo.select_by_user(
            user_id=user["user_id"]
        )

    def select_by_conversation(self, conversation_id: int, token: str) -> list[dict]:
        user = self._valid_token(token)

        return self.repo.select_by_conversation(
            user_id=user["user_id"],
            conversation_id=conversation_id
        )

    def select_conversations(self, token: str) -> list[dict]:
        user = self._valid_token(token)

        return self.repo.select_conversations(
            user_id=user["user_id"]
        )

    def delete_conversation(self, conversation_id: int, token: str) -> bool:
        user = self._valid_token(token)

        return self.repo.delete_conversation(
            user_id=user["user_id"],
            conversation_id=conversation_id
        )
        
    def create_empty(self, token: str) -> dict:
        user = self._valid_token(token)

        conversation_id = self.repo.create_empty(
            user_id=user["user_id"]
        )

        return {
            "conversation_id": conversation_id
        }