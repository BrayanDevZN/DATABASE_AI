from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class WithToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)


class GenerateDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


class GetDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    dashboard_id: int = Field(gt=0)


class DeleteDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    dashboard_id: int = Field(gt=0)


class CreateDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
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


class SaveChartSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    dashboard_id: int = Field(gt=0)

    # Agora pode salvar configuração de um gráfico específico.
    # Se vier None, mantém compatibilidade com configuração geral do dashboard.
    chart_id: int | None = Field(default=None, gt=0)

    chart_color: str = "#4f46e5"
    chart_background: str = "#f8fafc"

    x_axis_text_color: str = "#0f172a"
    y_axis_text_color: str = "#0f172a"

    grid_color: str = "#cbd5e1"
    grid_style: str = "3 3"

    bar_style: str = "rounded"


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
    chart_settings: dict[str, Any] | None = None


class ChartSettingsResponse(BaseModel):
    id: int | None = None
    dashboard_id: int | None = None
    chart_id: int | None = None

    chart_color: str = "#4f46e5"
    chart_background: str = "#f8fafc"

    x_axis_text_color: str = "#0f172a"
    y_axis_text_color: str = "#0f172a"

    grid_color: str = "#cbd5e1"
    grid_style: str = "3 3"

    bar_style: str = "rounded"


class DashboardWithChartsResponse(DashboardResponse):
    charts: list[ChartResponse] = Field(default_factory=list)
    chart_settings: ChartSettingsResponse | dict[str, Any] = Field(
        default_factory=dict
    )