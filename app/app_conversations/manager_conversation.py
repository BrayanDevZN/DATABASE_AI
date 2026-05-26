from app.app_conversations.service import ServiceConversation


class ManagerConversation:
    def __init__(self) -> None:
        self.service = ServiceConversation()

    def create(self, data: dict) -> dict | None:
        return self.service.create(
            data=data,
            token=data["token"]
        )

    def create_empty(self, data: dict) -> dict | None:
        return self.service.create_empty(
            token=data["token"],
            title=data["title"]
        )

    def select_by_conversation(self, data: dict) -> list[dict]:
        return self.service.select_by_conversation(
            conversation_id=data["conversation_id"],
            token=data["token"]
        )

    def select_conversations(self, data: dict) -> list[dict]:
        return self.service.select_conversations(
            token=data["token"]
        )