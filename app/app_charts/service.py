from app.app_charts.repository import RepositoryCharts


class ServiceCharts:
    def __init__(self) -> None:
        self.repo = RepositoryCharts()

    def create_dashboard(
        self,
        user_id: int,
        title: str,
        prompt: str | None,
        ai_suggestion: str | None,
        file_name: str | None,
        data_source_id: int | None = None
    ) -> dict | None:
        return self.repo.create_dashboard(
            user_id=user_id,
            title=title,
            prompt=prompt or "",
            ai_suggestion=ai_suggestion,
            file_name=file_name,
            data_source_id=data_source_id
        )

    def create_chart(
        self,
        dashboard_id: int,
        chart_type: str,
        title: str,
        chart_data: dict | list,
        chart_config: dict | None = None
    ) -> dict | None:
        return self.repo.create_chart(
            dashboard_id=dashboard_id,
            chart_type=chart_type,
            title=title,
            chart_data=chart_data,
            chart_config=chart_config or {}
        )

    def save_chart_settings(
        self,
        dashboard_id: int,
        chart_id: int | None,
        chart_color: str,
        chart_background: str,
        x_axis_text_color: str,
        y_axis_text_color: str,
        grid_color: str,
        grid_style: str,
        bar_style: str,
        pie_colors: list[str] | None = None,
        show_legend: bool = True
    ) -> dict | None:
        return self.repo.save_chart_settings(
            dashboard_id=dashboard_id,
            chart_id=chart_id,
            chart_color=chart_color,
            chart_background=chart_background,
            x_axis_text_color=x_axis_text_color,
            y_axis_text_color=y_axis_text_color,
            grid_color=grid_color,
            grid_style=grid_style,
            bar_style=bar_style,
            pie_colors=pie_colors,
            show_legend=show_legend
        )

    def select_dashboards_by_user(
        self,
        user_id: int
    ) -> list[dict]:
        return self.repo.select_dashboards_by_user(
            user_id=user_id
        )

    def select_dashboard_with_charts(
        self,
        user_id: int,
        dashboard_id: int
    ) -> dict | None:
        dashboard = self.repo.select_dashboard(
            user_id=user_id,
            dashboard_id=dashboard_id
        )

        if not dashboard:
            return None

        charts = self.repo.select_charts_by_dashboard(
            dashboard_id=dashboard_id
        )

        dashboard_settings = self.repo.select_chart_settings(
            dashboard_id=dashboard_id,
            chart_id=None
        )

        charts_with_settings = []

        for chart in charts:
            chart_settings = self.repo.select_chart_settings(
                dashboard_id=dashboard_id,
                chart_id=chart["id"]
            )

            chart["chart_settings"] = (
                chart_settings
                or dashboard_settings
                or {}
            )

            charts_with_settings.append(chart)

        dashboard["charts"] = charts_with_settings
        dashboard["chart_settings"] = dashboard_settings or {}

        return dashboard

    def select_dashboards_by_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> list[dict]:
        return self.repo.select_dashboards_by_data_source(
            user_id=user_id,
            data_source_id=data_source_id
        )

    def mark_dashboards_outdated_by_data_source(
        self,
        data_source_id: int
    ) -> bool:
        return self.repo.mark_dashboards_outdated(
            data_source_id=data_source_id
        )

    def replace_dashboard_charts(
        self,
        dashboard_id: int,
        charts: list[dict]
    ) -> list[dict]:
        if not charts:
            raise ValueError("Nenhum gráfico recebido para substituir.")

        self.repo.delete_charts_by_dashboard(
            dashboard_id=dashboard_id
        )

        created_charts = []

        for index, chart in enumerate(charts):
            chart_type = (
                chart.get("chart_type")
                or chart.get("type")
                or "bar"
            )

            title = chart.get("title") or f"Gráfico {index + 1}"

            chart_data = (
                chart.get("chart_data")
                or chart.get("data")
                or []
            )

            chart_config = chart.get("chart_config") or {
                "x": chart.get("x"),
                "y": chart.get("y"),
                "metric": chart.get("metric"),
                "group_by": chart.get("group_by"),
                "aggregation": chart.get("aggregation"),
                "operation": chart.get("operation"),
                "reason": chart.get("reason", ""),
            }

            created_chart = self.repo.create_chart(
                dashboard_id=dashboard_id,
                chart_type=chart_type,
                title=title,
                chart_data=chart_data,
                chart_config=chart_config
            )

            if created_chart:
                created_charts.append(created_chart)

        if not created_charts:
            raise ValueError("Erro ao criar novos gráficos do dashboard.")

        return created_charts

    def finish_dashboard_refresh(
        self,
        user_id: int,
        dashboard_id: int,
        ai_suggestion: str,
        charts: list[dict],
        prompt: str | None = None
    ) -> dict:
        dashboard = self.repo.select_dashboard(
            user_id=user_id,
            dashboard_id=dashboard_id
        )

        if not dashboard:
            raise ValueError("Dashboard não encontrado.")

        created_charts = self.replace_dashboard_charts(
            dashboard_id=dashboard_id,
            charts=charts
        )

        if hasattr(self.repo, "update_dashboard_after_refresh"):
            updated_dashboard = self.repo.update_dashboard_after_refresh(
                user_id=user_id,
                dashboard_id=dashboard_id,
                ai_suggestion=ai_suggestion,
                prompt=prompt
            )
        else:
            updated_dashboard = dashboard

        updated_dashboard["charts"] = created_charts
        updated_dashboard["ai_suggestion"] = ai_suggestion
        updated_dashboard["prompt"] = prompt if prompt is not None else dashboard.get("prompt", "")
        updated_dashboard["is_outdated"] = False

        return updated_dashboard

    def delete_dashboard(
        self,
        user_id: int,
        dashboard_id: int
    ) -> bool:
        return self.repo.delete_dashboard(
            user_id=user_id,
            dashboard_id=dashboard_id
        )

    def delete_all_by_user(
        self,
        user_id: int
    ) -> bool:
        return self.repo.delete_all_by_user(
            user_id=user_id
        )
