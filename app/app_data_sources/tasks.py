import os

import requests

from app.app_charts.manager_charts import ManagerCharts
from app.app_collaborations.manager_collaborations import ManagerCollaborations
from core.celery_app import celery_app


AI_URL = os.getenv("AI_URL", "https://web-production-40ead.up.railway.app")


def _analyze_dashboard_refresh_with_ai(token: str, dashboard: dict) -> dict:
    response = requests.post(
        f"{AI_URL}/dashboard/refresh/analyze",
        data={
            "token": token,
            "title": dashboard.get("title") or "Dashboard",
            "prompt": dashboard.get("prompt") or "",
            "data_source_id": str(dashboard["data_source_id"]),
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


@celery_app.task(name="data_sources.refresh_linked_dashboards")
def refresh_linked_dashboards_task(token: str, user_id: int, source: dict, dashboards: list[dict]) -> list[dict]:
    refreshed_dashboards = []
    chart_manager = ManagerCharts()
    collaborations = ManagerCollaborations()

    for dashboard in dashboards:
        try:
            analysis = _analyze_dashboard_refresh_with_ai(
                token=token,
                dashboard=dashboard,
            )
            charts = (
                analysis.get("charts")
                or analysis.get("dashboard", {}).get("charts")
                or []
            )
            ai_suggestion = (
                analysis.get("ai_suggestion")
                or analysis.get("dashboard", {}).get("ai_suggestion")
                or analysis.get("answer")
                or ""
            )

            if not charts:
                raise ValueError("A IA nao retornou graficos para o dashboard.")

            refreshed_dashboard = chart_manager.finish_dashboard_refresh(
                user_id=user_id,
                dashboard_id=dashboard["id"],
                ai_suggestion=ai_suggestion,
                charts=charts,
                prompt=dashboard.get("prompt"),
            )

            collaborations.notify_dashboard_refreshed(
                owner_user_id=user_id,
                dashboard_id=dashboard["id"],
                dashboard_title=dashboard.get("title") or "Dashboard",
                source_name=source.get("name") or "Fonte de dados",
            )
            refreshed_dashboards.append(refreshed_dashboard)
        except Exception as error:
            chart_manager.mark_dashboards_outdated_by_data_source(
                data_source_id=source["id"],
            )
            collaborations.create_notification(
                user_id=user_id,
                dashboard_id=dashboard.get("id"),
                message=(
                    f'Nao foi possivel atualizar automaticamente o dashboard '
                    f'"{dashboard.get("title", "Dashboard")}" da fonte '
                    f'"{source.get("name", "Fonte de dados")}". Atualize manualmente.'
                ),
                notification_type="dashboard_auto_refresh_failed",
            )
            refreshed_dashboards.append({
                "dashboard": dashboard,
                "error": str(error),
            })

    return refreshed_dashboards
