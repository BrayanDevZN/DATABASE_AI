from app.app_conversations.service import ServiceConversation


class ManagerConversation:
    def __init__(self) -> None:
        self.service = ServiceConversation()

    def create(self, data: dict) -> dict | None:
        return self.service.create(data)

    def select_by_user(self, data: dict) -> list[dict]:
        return self.service.select_by_user(data)

    def select_by_conversation(self, data: dict) -> list[dict]:
        return self.service.select_by_conversation(data)

    def select_conversations(self, data: dict) -> list[dict]:
        return self.service.select_conversations(data)

    def delete_conversation(self, data: dict) -> bool:
        return self.service.delete_conversation(data)