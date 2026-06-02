from sqlalchemy import text
from connect.manager_database import main_database
import json

engine = main_database()


class RepositoryCharts:
    def __init__(self) -> None:
        self.db = engine

    def create_dashboard(
        self,
        user_id: int,
        title: str,
        prompt: str | None,
        ai_suggestion: str | None,
        file_name: str | None,
        data_source_id: int | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboards (
                        user_id,
                        title,
                        prompt,
                        ai_suggestion,
                        file_name,
                        data_source_id,
                        is_outdated
                    )
                    VALUES (
                        :user_id,
                        :title,
                        :prompt,
                        :ai_suggestion,
                        :file_name,
                        :data_source_id,
                        FALSE
                    )
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "title": title,
                    "prompt": prompt or "",
                    "ai_suggestion": ai_suggestion,
                    "file_name": file_name,
                    "data_source_id": data_source_id
                }
            )

            session.commit()
            dashboard = result.fetchone()

        return dict(dashboard._mapping) if dashboard else None

    def create_chart(
        self,
        dashboard_id: int,
        chart_type: str,
        title: str,
        chart_data: dict,
        chart_config: dict | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboard_charts (
                        dashboard_id,
                        chart_type,
                        title,
                        chart_data,
                        chart_config
                    )
                    VALUES (
                        :dashboard_id,
                        :chart_type,
                        :title,
                        CAST(:chart_data AS JSONB),
                        CAST(:chart_config AS JSONB)
                    )
                    RETURNING *
                """),
                {
                    "dashboard_id": dashboard_id,
                    "chart_type": chart_type,
                    "title": title,
                    "chart_data": json.dumps(chart_data, ensure_ascii=False),
                    "chart_config": json.dumps(chart_config or {}, ensure_ascii=False)
                }
            )

            session.commit()
            chart = result.fetchone()

        return dict(chart._mapping) if chart else None

    def select_dashboards_by_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                """),
                {"user_id": user_id}
            )

            dashboards = result.fetchall()

        return [dict(dashboard._mapping) for dashboard in dashboards]

    def select_dashboard(self, user_id: int, dashboard_id: int) -> dict | None:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE id = :dashboard_id
                    AND user_id = :user_id
                """),
                {
                    "dashboard_id": dashboard_id,
                    "user_id": user_id
                }
            )

            dashboard = result.fetchone()

        return dict(dashboard._mapping) if dashboard else None

    def select_charts_by_dashboard(self, dashboard_id: int) -> list[dict]:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboard_charts
                    WHERE dashboard_id = :dashboard_id
                    ORDER BY created_at ASC
                """),
                {"dashboard_id": dashboard_id}
            )

            charts = result.fetchall()

        return [dict(chart._mapping) for chart in charts]

    def delete_dashboard(self, user_id: int, dashboard_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM dashboards
                    WHERE id = :dashboard_id
                    AND user_id = :user_id
                """),
                {
                    "dashboard_id": dashboard_id,
                    "user_id": user_id
                }
            )

            session.commit()

        return result.rowcount > 0

    def delete_all_by_user(self, user_id: int) -> bool:
        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE FROM dashboards
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )

            session.commit()

        return result.rowcount >= 0

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
        pie_colors_json = json.dumps(
            pie_colors or [],
            ensure_ascii=False
        )

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    INSERT INTO dashboard_chart_settings (
                        dashboard_id,
                        chart_id,
                        chart_color,
                        chart_background,
                        x_axis_text_color,
                        y_axis_text_color,
                        grid_color,
                        grid_style,
                        bar_style,
                        pie_colors,
                        show_legend,
                        updated_at
                    )
                    VALUES (
                        :dashboard_id,
                        :chart_id,
                        :chart_color,
                        :chart_background,
                        :x_axis_text_color,
                        :y_axis_text_color,
                        :grid_color,
                        :grid_style,
                        :bar_style,
                        CAST(:pie_colors AS JSONB),
                        :show_legend,
                        NOW()
                    )
                    ON CONFLICT (chart_id)
                    DO UPDATE SET
                        chart_color = EXCLUDED.chart_color,
                        chart_background = EXCLUDED.chart_background,
                        x_axis_text_color = EXCLUDED.x_axis_text_color,
                        y_axis_text_color = EXCLUDED.y_axis_text_color,
                        grid_color = EXCLUDED.grid_color,
                        grid_style = EXCLUDED.grid_style,
                        bar_style = EXCLUDED.bar_style,
                        pie_colors = EXCLUDED.pie_colors,
                        show_legend = EXCLUDED.show_legend,
                        updated_at = NOW()
                    RETURNING *
                """),
                {
                    "dashboard_id": dashboard_id,
                    "chart_id": chart_id,
                    "chart_color": chart_color,
                    "chart_background": chart_background,
                    "x_axis_text_color": x_axis_text_color,
                    "y_axis_text_color": y_axis_text_color,
                    "grid_color": grid_color,
                    "grid_style": grid_style,
                    "bar_style": bar_style,
                    "pie_colors": pie_colors_json,
                    "show_legend": show_legend
                }
            )

            session.commit()
            settings = result.fetchone()

        return dict(settings._mapping) if settings else None

    def select_chart_settings(
        self,
        dashboard_id: int,
        chart_id: int | None = None
    ) -> dict | None:
        with self.db.connect() as session:
            if chart_id:
                result = session.execute(
                    text("""
                        SELECT *
                        FROM dashboard_chart_settings
                        WHERE dashboard_id = :dashboard_id
                        AND chart_id = :chart_id
                    """),
                    {
                        "dashboard_id": dashboard_id,
                        "chart_id": chart_id
                    }
                )
            else:
                result = session.execute(
                    text("""
                        SELECT *
                        FROM dashboard_chart_settings
                        WHERE dashboard_id = :dashboard_id
                        AND chart_id IS NULL
                    """),
                    {"dashboard_id": dashboard_id}
                )

            settings = result.fetchone()

        if not settings:
            return None

        settings_dict = dict(settings._mapping)

        if settings_dict.get("pie_colors") is None:
            settings_dict["pie_colors"] = []

        return settings_dict
    
    
    def select_dashboards_by_data_source(
        self,
        user_id: int,
        data_source_id: int
    ) -> list[dict]:

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE user_id = :user_id
                    AND data_source_id = :data_source_id
                    ORDER BY updated_at DESC
                """),
                {
                    "user_id": user_id,
                    "data_source_id": data_source_id
                }
            )

            dashboards = result.fetchall()

        return [
            dict(dashboard._mapping)
            for dashboard in dashboards
        ]
        
    def mark_dashboards_outdated(
        self,
        data_source_id: int
    ) -> bool:

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE dashboards
                    SET
                        is_outdated = TRUE,
                        updated_at = NOW()
                    WHERE data_source_id = :data_source_id
                """),
                {
                    "data_source_id": data_source_id
                }
            )

            session.commit()

        return result.rowcount > 0
    
    
    def delete_charts_by_dashboard(
        self,
        dashboard_id: int
    ) -> bool:

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    DELETE
                    FROM dashboard_charts
                    WHERE dashboard_id = :dashboard_id
                """),
                {
                    "dashboard_id": dashboard_id
                }
            )

            session.commit()

        return result.rowcount >= 0
    
    
    def update_dashboard_after_refresh(
        self,
        user_id: int,
        dashboard_id: int,
        ai_suggestion: str
    ) -> dict | None:

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    UPDATE dashboards
                    SET
                        ai_suggestion = :ai_suggestion,
                        is_outdated = FALSE,
                        updated_at = NOW()
                    WHERE id = :dashboard_id
                    AND user_id = :user_id
                    RETURNING *
                """),
                {
                    "user_id": user_id,
                    "dashboard_id": dashboard_id,
                    "ai_suggestion": ai_suggestion
                }
            )

            session.commit()

            dashboard = result.fetchone()

        if not dashboard:
            return None

        return dict(dashboard._mapping)
    
    def select_dashboard_by_id(
        self,
        dashboard_id: int
    ) -> dict | None:

        with self.db.connect() as session:
            result = session.execute(
                text("""
                    SELECT *
                    FROM dashboards
                    WHERE id = :dashboard_id
                """),
                {
                    "dashboard_id": dashboard_id
                }
            )

            dashboard = result.fetchone()

        if not dashboard:
            return None

        return dict(dashboard._mapping)