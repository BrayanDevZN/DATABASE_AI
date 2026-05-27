from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class WithToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class GenerateDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


class GetDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    dashboard_id: int = Field(gt=0)


class DeleteDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    dashboard_id: int = Field(gt=0)


class CreateDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    ai_suggestion: str | None = None
    file_name: str | None = None


class CreateChart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dashboard_id: int = Field(gt=0)
    chart_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    chart_data: dict[str, Any]
    chart_config: dict[str, Any] | None = None


class DashboardResponse(BaseModel):
    id: int
    user_id: int
    title: str
    prompt: str
    ai_suggestion: str | None = None
    file_name: str | None = None


class ChartResponse(BaseModel):
    id: int
    dashboard_id: int
    chart_type: str
    title: str
    chart_data: dict[str, Any]
    chart_config: dict[str, Any] | None = None


class DashboardWithChartsResponse(DashboardResponse):
    charts: list[ChartResponse] = []