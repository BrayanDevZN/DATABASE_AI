from app.app_charts.service import ServiceCharts


class ManagerCharts:
    def __init__(self) -> None:
        self.service = ServiceCharts()

    def create_dashboard(
        self,
        user_id: int,
        title: str,
        prompt: str,
        ai_suggestion: str | None,
        file_name: str | None
    ) -> dict | None:
        return self.service.create_dashboard(
            user_id=user_id,
            title=title,
            prompt=prompt,
            ai_suggestion=ai_suggestion,
            file_name=file_name
        )

    def create_chart(
        self,
        dashboard_id: int,
        chart_type: str,
        title: str,
        chart_data: dict,
        chart_config: dict | None = None
    ) -> dict | None:
        return self.service.create_chart(
            dashboard_id=dashboard_id,
            chart_type=chart_type,
            title=title,
            chart_data=chart_data,
            chart_config=chart_config
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
        bar_style: str
    ) -> dict | None:
        return self.service.save_chart_settings(
            dashboard_id=dashboard_id,
            chart_id=chart_id,
            chart_color=chart_color,
            chart_background=chart_background,
            x_axis_text_color=x_axis_text_color,
            y_axis_text_color=y_axis_text_color,
            grid_color=grid_color,
            grid_style=grid_style,
            bar_style=bar_style
        )

    def select_dashboards_by_user(self, user_id: int) -> list[dict]:
        return self.service.select_dashboards_by_user(
            user_id=user_id
        )

    def select_dashboard_with_charts(
        self,
        user_id: int,
        dashboard_id: int
    ) -> dict | None:
        return self.service.select_dashboard_with_charts(
            user_id=user_id,
            dashboard_id=dashboard_id
        )

    def delete_dashboard(
        self,
        user_id: int,
        dashboard_id: int
    ) -> bool:
        return self.service.delete_dashboard(
            user_id=user_id,
            dashboard_id=dashboard_id
        )

    def delete_all_by_user(self, user_id: int) -> bool:
        return self.service.delete_all_by_user(
            user_id=user_id
        )