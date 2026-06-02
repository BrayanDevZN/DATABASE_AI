from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Permission = Literal["read", "edit", "full"]


class WithToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)


class SearchUsers(WithToken):
    query: str = Field(min_length=1, max_length=30)


class DashboardCollaborations(WithToken):
    dashboard_id: int = Field(gt=0)


class ShareDashboard(DashboardCollaborations):
    username: str = Field(min_length=1, max_length=30)
    permission: Permission


class UpdateCollaboration(WithToken):
    collaboration_id: int = Field(gt=0)
    permission: Permission


class DeleteCollaboration(WithToken):
    collaboration_id: int = Field(gt=0)


class RespondInvitation(DeleteCollaboration):
    response: Literal["accepted", "declined"]


class MarkNotificationRead(WithToken):
    notification_id: int = Field(gt=0)
